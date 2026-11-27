"""Build or inspect the portable skill and exercise its CLI from an isolated directory."""

import argparse
import hashlib
import json
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
SKILL_PARENT = ROOT / "skills"
SKILL = SKILL_PARENT / "kmdstudio"
BENCHMARKS = Path("examples/benchmarks")
VISUAL = BENCHMARKS / "visual-intelligence"
MANIFEST = VISUAL / "assets/study-vessel.json"
MANIFEST_SHA256 = "88404121fb734716791c3b328036b4a954fada5e7e6880eda91fce828d7057cf"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def skill_files():
    result = {}
    for path in sorted(SKILL.rglob("*")):
        relative = path.relative_to(SKILL_PARENT)
        if "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        info = path.lstat()
        require(not path.is_symlink() and not getattr(info, "st_file_attributes", 0) & 0x400,
                f"linked skill member {relative}")
        if stat.S_ISDIR(info.st_mode):
            continue
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, f"unsafe skill file {relative}")
        result[relative.as_posix()] = path.read_bytes()
    return result


def build_bundle(destination, files):
    with ZipFile(destination, "x") as package:
        for name, data in files.items():
            entry = ZipInfo(name)
            entry.create_system = 0
            package.writestr(entry, data, compress_type=ZIP_DEFLATED)


def unpack(archive, files, directory):
    with ZipFile(archive) as package:
        names = package.namelist()
        require(len(names) == len(files) and set(names) == files.keys(),
                "skill archive paths differ from canonical files")
        require(all(entry.file_size == len(files[entry.filename]) for entry in package.infolist()),
                "skill archive expanded sizes differ from canonical files")
        require(package.testzip() is None, "skill archive CRC mismatch")
        for name in names:
            content = package.read(name)
            require(content == files[name], f"skill archive bytes differ for {name}")
            target = directory / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)


def parts(docx):
    with ZipFile(docx) as package:
        require(len(package.namelist()) == len(set(package.namelist())),
                "OOXML archive has duplicate entries")
        require(package.testzip() is None, "OOXML archive CRC mismatch")
        return {name: package.read(name) for name in package.namelist()}


def native_text(node):
    pieces = []
    for item in node.iter():
        if item.tag == W + "t":
            pieces.append(item.text or "")
        elif item.tag == W + "tab":
            pieces.append("\t")
        elif item.tag == W + "br":
            pieces.append("\n")
    return "".join(pieces)


def verify_output(path, fixture, brief, directory):
    docx = parts(path)
    for name, data in docx.items():
        require("vba" not in name.casefold() and "embeddings/" not in name,
                f"unexpected executable or embedded object in {name}")
        if name.endswith(".rels"):
            require(all("TargetMode" not in rel.attrib for rel in ET.fromstring(data)),
                    f"external relationship in {name}")
    document = ET.fromstring(docx["word/document.xml"])
    paragraphs = [native_text(p) for p in document.iter(W + "p")]
    bookmarks = {node.get(W + "name") for node in document.iter(W + "bookmarkStart")}
    require(brief["title"] in paragraphs, "main title is missing or noneditable")
    for block_id in brief["acceptance"]["required_ids"]:
        require("kmd_" + block_id.replace("-", "_") in bookmarks,
                f"missing required block {block_id}")
    for block in brief["blocks"]:
        if block["kind"] == "code":
            require(block["text"] in paragraphs, "editable code differs from the source")
    if fixture.stem == "dispatch-readiness":
        tables = list(document.iter(W + "tbl"))
        require(len(tables) == 2, "expected two native tables")
        rows = []
        expected = [block for block in brief["blocks"] if block["kind"] == "table"]
        for table, block in zip(tables, expected):
            header, *body = table.findall(W + "tr")
            require(header.find(f"{W}trPr/{W}tblHeader") is not None, "missing repeating header")
            require([native_text(cell) for cell in header.findall(W + "tc")] == block["headers"],
                    "table headers differ from the source")
            cells = [[native_text(cell) for cell in row.findall(W + "tc")] for row in body]
            require(cells == block["rows"], "editable ledger rows differ from the source")
            rows.extend(cells)
        require(len(rows) == 32 and sum(int(row[2]) for row in rows) == 1725
                and sum(int(row[3]) for row in rows) == 1699
                and sum(row[4] == "Review" for row in rows) == 5, "ledger totals differ")
    if fixture.stem == "reading-the-surface":
        figure = next(block for block in brief["blocks"] if block["kind"] == "figure")
        asset = json.loads((directory / MANIFEST).read_bytes())[figure["asset"]]
        pictures = list(document.iter(WP + "docPr"))
        require(len(pictures) == 1 and pictures[0].get("descr") == figure["alt"],
                "Word drawing lacks the exact description")
        require(figure["caption"] in paragraphs, "caption is missing or noneditable")
        require(hashlib.sha256(docx["word/media/image1.png"]).hexdigest() == asset["sha256"],
                "embedded photo does not match the reviewed asset")


def verify_cli(directory):
    shutil.copytree(ROOT / BENCHMARKS, directory / BENCHMARKS)
    fixtures = [
        path.relative_to(directory) for path in sorted((directory / BENCHMARKS).glob("*.json"))
    ]
    fixtures.extend(path.relative_to(directory) for path in sorted((directory / VISUAL).glob("*.json")))
    require(len(fixtures) == 6, "expected three regression and three candidate benchmarks")
    manifest_args = ["--asset-manifest", MANIFEST.as_posix(),
                     "--asset-manifest-sha256", MANIFEST_SHA256]
    for index, fixture in enumerate(fixtures):
        output = directory / (fixture.stem + ".docx")
        args = [sys.executable, "-E", "-s", "-S", "-B",
                str(directory / "kmdstudio/scripts/generate.py"), "--root", str(directory),
                "--spec", fixture.as_posix(), "--output", output.name]
        if fixture.stem == "reading-the-surface":
            failed = subprocess.run(args, cwd=directory.parent, capture_output=True,
                                    check=False, timeout=30)
            require(failed.returncode == 2 and not output.exists(),
                    "unapproved illustration was accepted")
            args.extend(manifest_args)
        started = time.perf_counter()
        subprocess.run(args, cwd=directory if index % 2 else directory.parent,
                       capture_output=True, check=True, timeout=30)
        elapsed = time.perf_counter() - started
        verify_output(output, fixture, json.loads((directory / fixture).read_bytes()), directory)
        historical = ROOT / "artifacts/v0.2.0" / output.name
        if fixture.parent == BENCHMARKS:
            require(parts(output) == parts(historical), "existing benchmark changed")
        print(f"{output.name} {output.stat().st_size} bytes {elapsed * 1000:.0f} ms PASS")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--build", type=Path, help="write a new portable skill archive")
    modes.add_argument("--archive", type=Path, help="verify an existing candidate archive")
    args = parser.parse_args()
    version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    files = skill_files()
    with tempfile.TemporaryDirectory(prefix="kmdstudio-bundle-") as tmp:
        directory = Path(tmp)
        archive = args.archive or args.build or directory / f"kmdstudio-{version}.zip"
        if args.archive is None:
            build_bundle(archive, files)
        unpack(archive, files, directory)
        verify_cli(directory)
        print(f"{len(files)} canonical skill files, {archive.stat().st_size} archive bytes")


if __name__ == "__main__":
    main()
