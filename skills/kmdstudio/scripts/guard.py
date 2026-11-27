"""Filesystem and parser boundaries for the local document workflow."""

import hashlib
import json
import os
import re
import stat
import struct
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
JSON_LIMIT = 192 * 1024
ICON_LIMIT = 128 * 1024
DOCX_LIMIT = 4 * 1024 * 1024
XML_LIMIT = 2 * 1024 * 1024
XML_DEPTH = 32
XML_NODES = 120_000
DEVICE = re.compile(r"(?:CON|PRN|AUX|NUL|CONIN\$|CONOUT\$|(?:COM|LPT)[0-9¹²³])", re.I)
INVALID = re.compile(r'[<>:"|?*~\x00-\x1f\x7f]')
PRIVATE = {".git", ".agents", ".codex", ".aws", ".venv", ".ssh"}


def relative_parts(raw):
    parts = raw.replace("\\", "/").split("/")
    if len(raw) > 240 or len(parts) > 12:
        raise ValueError("path exceeds the supported limits")
    for part in parts:
        if (not part or part != part.strip() or part.endswith(".")
                or INVALID.search(part) or DEVICE.fullmatch(part.split(".")[0].rstrip())):
            raise ValueError("unsafe path component")
    return parts


def plain_path(path, *, directory=False):
    info = path.lstat()
    attributes = getattr(info, "st_file_attributes", 0)
    if stat.S_ISLNK(info.st_mode) or attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
        raise ValueError("links, junctions and other reparse points are unsupported")
    if directory:
        if not stat.S_ISDIR(info.st_mode):
            raise ValueError("expected an existing directory")
    elif not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError("expected a regular file without additional hard links")
    return info


def workspace(raw):
    path = Path(raw)
    if not path.is_absolute() or path.anchor.startswith(("//", "\\\\")):
        raise ValueError("root must be an absolute local directory")
    if os.name == "nt":
        from ctypes import WinDLL, c_uint, c_wchar_p

        if not re.fullmatch(r"[A-Za-z]:\\", path.anchor):
            raise ValueError("root must use a local Windows drive path")
        drive_type = WinDLL("kernel32").GetDriveTypeW
        drive_type.argtypes = [c_wchar_p]
        drive_type.restype = c_uint
        if drive_type(path.anchor) not in {2, 3, 6}:
            raise ValueError("root must be on a local disk")
    if len(path.parts) < 2:
        raise ValueError("root must be narrower than the filesystem root")
    relative_parts(raw.replace("\\", "/")[len(path.anchor):].removesuffix("/"))
    check_directory_chain(path, reject_reserved=True)
    resolved = path.resolve(strict=True)
    if resolved.anchor.startswith(("//", "\\\\")):
        raise ValueError("root resolves to a nonlocal directory")
    return resolved


def check_directory_chain(path, *, reject_reserved=False):
    for path_part in (*reversed(path.parents), path):
        if path_part != Path(path.anchor):
            relative_parts(path_part.name)
            if reject_reserved and path_part.name.casefold() in PRIVATE:
                raise ValueError("root contains a reserved directory")
        info = plain_path(path_part, directory=True)
    return info


def confined(root, raw, suffix, *, new=False, package=False):
    parts = relative_parts(raw)
    if not package and any(part.casefold() in PRIVATE for part in parts):
        raise ValueError("reserved path component")
    candidate = root.joinpath(*parts)
    if candidate.suffix.lower() != suffix:
        raise ValueError(f"expected a {suffix} file")
    parent = root
    plain_path(parent, directory=True)
    for component in parts[:-1]:
        parent /= component
        plain_path(parent, directory=True)
    if new:
        try:
            candidate.lstat()
        except FileNotFoundError:
            pass
        else:
            raise FileExistsError("output already exists")
        checked = parent.resolve(strict=True) / candidate.name
    else:
        plain_path(candidate)
        checked = candidate.resolve(strict=True)
    if not checked.is_relative_to(root):
        raise ValueError("path escapes its authorized root")
    return checked


def bounded_read(path, limit):
    before = plain_path(path)
    if before.st_size > limit:
        raise ValueError("file exceeds size limit")
    with path.open("rb") as stream:
        opened = os.fstat(stream.fileno())
        if (not os.path.samestat(before, opened) or not stat.S_ISREG(opened.st_mode)
                or opened.st_nlink != 1 or opened.st_size > limit):
            raise ValueError("input changed while opening")
        data = stream.read(limit + 1)
        after = os.fstat(stream.fileno())
        if (opened.st_size != after.st_size or opened.st_mtime_ns != after.st_mtime_ns
                or after.st_nlink != 1 or not os.path.samestat(after, plain_path(path))):
            raise ValueError("input changed while reading")
    if len(data) > limit:
        raise ValueError("file exceeds size limit")
    return data


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON property")
        result[key] = value
    return result


def _integer(raw):
    if len(raw) > 8:
        raise ValueError("JSON integer exceeds the supported range")
    return int(raw)


def _unsupported_number(_):
    raise ValueError("JSON supports finite integers only")


def read_json(path):
    return parse_json(bounded_read(path, JSON_LIMIT))


def parse_json(data):
    data = data.decode("utf-8")
    depth = 0
    quoted = escaped = False
    for char in data:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            if depth > 16:
                raise ValueError("JSON exceeds parser nesting limit")
        elif char in "]}":
            depth -= 1
    try:
        return json.loads(data, object_pairs_hook=_unique_pairs, parse_int=_integer,
                          parse_float=_unsupported_number, parse_constant=_unsupported_number)
    except RecursionError as exc:
        raise ValueError("JSON exceeds parser nesting limit") from exc


class BoundedTree(ET.TreeBuilder):
    def __init__(self):
        super().__init__()
        self.depth = self.nodes = 0

    def start(self, tag, attrs):
        self.depth += 1
        self.nodes += 1
        if self.depth > XML_DEPTH or self.nodes > XML_NODES:
            raise ValueError("XML tree exceeds limits")
        return super().start(tag, attrs)

    def end(self, tag):
        self.depth -= 1
        return super().end(tag)


def parse_xml(data):
    if len(data) > XML_LIMIT:
        raise ValueError("XML part exceeds size limit")
    source = data.decode("utf-8")
    if "<!" in source or "<?" in source or "\x00" in source or source.startswith("\ufeff"):
        raise ValueError("XML declarations, DTDs and processing instructions are unsupported")
    return ET.fromstring(source, parser=ET.XMLParser(target=BoundedTree()))


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def check_png(data, *, max_edge=512):
    if (len(data) < 45 or data[:16] != b"\x89PNG\r\n\x1a\n\x00\x00\x00\x0dIHDR"
            or data[-12:] != b"\x00\x00\x00\x00IEND\xaeB\x60\x82"):
        raise ValueError("expected a reviewed PNG")
    width, height = struct.unpack(">II", data[16:24])
    if not (1 <= width <= max_edge and 1 <= height <= max_edge):
        raise ValueError("PNG dimensions exceed limits")
    return width, height


def verified_assets():
    base = PACKAGE / "assets"
    manifest = read_json(confined(PACKAGE, "assets/manifest.json", ".json", package=True))
    if not isinstance(manifest, dict) or not 1 <= len(manifest) <= 12:
        raise ValueError("invalid asset manifest")
    result = {}
    keys = {"path", "source", "version", "license", "license_path", "license_sha256",
            "sha256", "verification"}
    for asset_id, entry in manifest.items():
        if (not re.fullmatch(r"[a-z][a-z0-9-]{1,40}", asset_id)
                or not isinstance(entry, dict) or entry.keys() != keys
                or any(not isinstance(value, str) for value in entry.values())
                or entry["verification"] != "reviewed-source-and-local-derivative"
                or not entry["source"].startswith("https://github.com/lucide-icons/lucide/blob/")
                or not entry["version"] or entry["license"] not in {"ISC", "MIT"}
                or not entry["path"].startswith("icons/")
                or not entry["license_path"].startswith("licenses/")):
            raise ValueError("invalid asset provenance")
        icon = bounded_read(confined(base, entry["path"], ".png", package=True), ICON_LIMIT)
        notice = bounded_read(confined(base, entry["license_path"], ".txt", package=True), 8192)
        if sha256(icon) != entry["sha256"] or sha256(notice) != entry["license_sha256"]:
            raise ValueError("asset or notice integrity check failed")
        check_png(icon)
        result[asset_id] = icon
    return result


def publish_new(path, data):
    """Publish only complete data and fail atomically if the destination exists."""
    parent = check_directory_chain(path.parent)
    descriptor, staged = tempfile.mkstemp(prefix=".kmd-", suffix=".tmp", dir=path.parent)
    staged = Path(staged)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
            file_info = os.fstat(stream.fileno())
        if (not os.path.samestat(parent, check_directory_chain(path.parent))
                or not os.path.samestat(file_info, plain_path(staged))):
            raise ValueError("output directory or staging file changed before publication")
        os.link(staged, path)
    finally:
        staged.unlink(missing_ok=True)
