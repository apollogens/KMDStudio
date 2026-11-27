"""Export a freshly verified brief with an operator-selected LibreOffice renderer."""

import io
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import BadZipFile

from generate import build_document, cli_paths, parser
from guard import bounded_read, confined, plain_path, publish_new, workspace

PDF_LIMIT = 12 * 1024 * 1024
XREF_LIMIT = 1 * 1024 * 1024
OBJECT_LIMIT = 5000
GRAPH_LIMIT = 25000
PAGE_LIMIT = 100
BLOCKED_KEYS = {
    "/AA", "/AF", "/Annots", "/Collection", "/EF", "/EmbeddedFiles", "/JavaScript",
    "/JS", "/Launch", "/RichMedia", "/XFA", "/AcroForm", "/URI", "/FFilter", "/FDecodeParms",
}
BLOCKED_TYPES = {
    "/Action", "/EmbeddedFile", "/Filespec", "/FileAttachment", "/RichMedia",
    "/Movie", "/Sound", "/Screen", "/3D", "/Rendition",
}
ACTION_TYPES = {
    "/GoTo", "/GoToR", "/GoToE", "/GoToDp", "/Launch", "/Thread", "/URI", "/Sound",
    "/Movie", "/Hide", "/Named", "/SubmitForm", "/ResetForm", "/ImportData",
    "/JavaScript", "/SetOCGState", "/Rendition", "/Trans", "/GoTo3DView",
}


def check_xref(data):
    end = re.search(rb"\nstartxref\s+([0-9]{1,8})\s+%%EOF\s*\Z", data[-128:])
    if not end:
        raise ValueError("invalid PDF cross-reference pointer")
    offset = int(end[1])
    if not 0 < offset < len(data) or len(data) - offset > XREF_LIMIT:
        raise ValueError("PDF cross-reference table exceeds limits")
    xref, separator, trailer = data[offset:].partition(b"trailer")
    lines = xref.splitlines()
    if not separator or lines[:1] != [b"xref"]:
        raise ValueError("expected a classic PDF cross-reference table")
    # Validate before PdfReader can follow offsets declared in the trailer.
    entry = (rb"(?:/Size\s+\d{1,5}|/(?:Root|Info)\s+\d{1,5}\s+\d{1,5}\s+R"
             rb"|/ID\s*\[\s*<[0-9A-Fa-f]{1,128}>\s*<[0-9A-Fa-f]{1,128}>\s*\]"
             rb"|/DocChecksum\s+/[0-9A-Fa-f]{1,128})")
    if len(trailer) > 2048 or not re.fullmatch(
        rb"\s*<<(?:\s*" + entry + rb"){2,5}\s*>>\s*startxref\s+\d{1,8}\s+%%EOF\s*", trailer,
    ):
        raise ValueError("PDF trailer is outside the static export profile")
    keys = re.findall(rb"/(Size|Root|Info|ID|DocChecksum)(?=\s|\[)", trailer)
    if len(keys) != len(set(keys)) or not {b"Size", b"Root"} <= set(keys):
        raise ValueError("PDF trailer requires unique size and root entries")
    cursor = 1
    table = {}
    while cursor < len(lines):
        line = re.fullmatch(rb"([0-9]{1,8}) ([0-9]{1,5})", lines[cursor])
        if not line:
            raise ValueError("invalid PDF cross-reference subsection")
        first, count = map(int, line.groups())
        cursor += 1
        if not 0 < count <= OBJECT_LIMIT or first + count > OBJECT_LIMIT:
            raise ValueError("PDF cross-reference table exceeds limits")
        for identity in range(first, first + count):
            if cursor >= len(lines) or identity in table:
                raise ValueError("truncated or duplicate PDF cross-reference entry")
            entry = re.fullmatch(rb"([0-9]{10}) ([0-9]{5}) ([nf]) *", lines[cursor])
            cursor += 1
            if not entry:
                raise ValueError("invalid PDF cross-reference entry")
            position, generation = map(int, entry.groups()[:2])
            table[identity] = None
            if entry[3] == b"n":
                marker = f"{identity} {generation} obj".encode("ascii")
                if (identity == 0 or not 0 < position < offset
                        or not data.startswith(marker, position)
                        or data[position + len(marker):position + len(marker) + 1]
                        not in (b" ", b"\t", b"\n", b"\r", b"<", b"[", b"(", b"/")):
                    raise ValueError("PDF cross-reference entry does not match its object")
                table[identity] = (generation, position)
    return {key: entry for key, entry in table.items() if entry is not None}


def check_pdf(data):
    try:
        return _check_pdf(data)
    except RecursionError as exc:
        raise ValueError("PDF parser nesting exceeds limits") from exc


def _check_pdf(data):
    from pypdf import PdfReader
    from pypdf.generic import (
        ArrayObject,
        DictionaryObject,
        FloatObject,
        IndirectObject,
        NameObject,
        NullObject,
        NumberObject,
        StreamObject,
    )

    if (len(data) > PDF_LIMIT or not data.startswith(b"%PDF-")
            or not data.rstrip().endswith(b"%%EOF")):
        raise ValueError("invalid PDF header, end marker or size")
    xref = check_xref(data)
    reader = PdfReader(io.BytesIO(data), strict=True, root_object_recovery_limit=0)
    if (reader.is_encrypted or reader.xref_objStm
            or reader.trailer.keys() & {"/Prev", "/XRefStm"}):
        raise ValueError("encrypted, hybrid and incremental PDFs are unsupported")
    if any(reader.xref.get(generation, {}).get(obj) != offset
           for obj, (generation, offset) in xref.items()):
        raise ValueError("parsed PDF cross-reference table differs from the source")
    root = reader.trailer.get("/Root")
    pending = [(reader.trailer, 0)]
    pending.extend((IndirectObject(obj, generation, reader), 0)
                   for obj, (generation, _) in xref.items())
    visited = set()
    view = None
    nodes = 0
    while pending:
        current, depth = pending.pop()
        nodes += 1
        if nodes + len(pending) > GRAPH_LIMIT or depth > 32:
            raise ValueError("PDF object graph exceeds limits")
        if isinstance(current, IndirectObject):
            identity = (current.idnum, current.generation)
            if identity in visited:
                continue
            visited.add(identity)
            if xref.get(current.idnum, (None,))[0] != current.generation:
                raise ValueError("PDF reference is outside the cross-reference table")
            resolved = current.get_object()
            if resolved is None or isinstance(resolved, NullObject):
                raise ValueError("unresolved PDF reference")
            pending.append((resolved, 0))
            continue
        elif isinstance(current, DictionaryObject):
            obj_type = current.get("/Type")
            if (current.keys() & BLOCKED_KEYS
                    or any(key in current and not isinstance(current.raw_get(key), NameObject)
                           for key in ("/Type", "/Subtype", "/S"))
                    or str(obj_type) in BLOCKED_TYPES
                    or str(current.get("/Subtype")) in BLOCKED_TYPES
                    or str(current.get("/S")) in ACTION_TYPES
                    or ("/A" in current and obj_type != "/StructElem")
                    or (isinstance(current, StreamObject) and current.keys() & {"/F", "/Ref"})):
                raise ValueError("PDF contains prohibited active content")
            if "/OpenAction" in current:
                if not isinstance(root, IndirectObject) or current is not root.get_object():
                    raise ValueError("PDF contains a misplaced open action")
                view = current.raw_get("/OpenAction")
            children = current.values()
        elif isinstance(current, ArrayObject):
            children = current
        else:
            continue
        if nodes + len(pending) + len(current) > GRAPH_LIMIT:
            raise ValueError("PDF object graph exceeds limits")
        pending.extend((child, depth + 1) for child in children)

    catalog = root.get_object() if isinstance(root, IndirectObject) else None
    if not isinstance(catalog, DictionaryObject) or catalog.get("/Type") != "/Catalog":
        raise ValueError("invalid PDF catalog")
    page_ids = set()
    tree_ids = set()

    def page_count(ref, parent=None, depth=0):
        if not isinstance(ref, IndirectObject) or depth > 16:
            raise ValueError("invalid or excessively deep PDF page tree")
        identity = (ref.idnum, ref.generation)
        if identity in tree_ids or len(tree_ids) >= PAGE_LIMIT * 2:
            raise ValueError("repeated PDF page tree node or tree exceeds limits")
        tree_ids.add(identity)
        node = ref.get_object()
        if not isinstance(node, DictionaryObject) or node.get("/Parent") != parent:
            raise ValueError("invalid PDF page parent")
        if node.get("/Type") == "/Page" and parent is not None and "/Kids" not in node:
            page_ids.add(identity)
            if len(page_ids) > PAGE_LIMIT:
                raise ValueError("PDF page count is out of bounds")
            return 1
        kids, count = node.get("/Kids"), node.get("/Count")
        if (node.get("/Type") != "/Pages" or not isinstance(kids, ArrayObject)
                or not 1 <= len(kids) <= PAGE_LIMIT or not isinstance(count, NumberObject)
                or not 1 <= count <= PAGE_LIMIT):
            raise ValueError("invalid PDF page tree node")
        if sum(page_count(child, ref, depth + 1) for child in kids) != count:
            raise ValueError("PDF page count differs from the page tree")
        return count

    page_count(catalog.get("/Pages"))
    if view is not None:
        # Writer emits a static initial view with a destination in the actual page tree.
        arities = {"/XYZ": 5, "/Fit": 2, "/FitH": 3, "/FitV": 3, "/FitR": 6}
        if (not isinstance(view, ArrayObject) or not 2 <= len(view) <= 6
                or not isinstance(view[0], IndirectObject)
                or (view[0].idnum, view[0].generation) not in page_ids
                or not isinstance(view[1], NameObject) or arities.get(view[1]) != len(view)
                or any(not isinstance(arg, (NumberObject, FloatObject, NullObject)) for arg in view[2:])):
            raise ValueError("PDF contains a prohibited open action")
    return reader


def renderer_path(raw):
    path = Path(raw)
    name = "soffice.com" if os.name == "nt" else "soffice"
    if path.name.lower() != name:
        raise ValueError("provide the absolute path to the trusted LibreOffice binary")
    parent = workspace(str(path.parent))
    return confined(parent, path.name, path.suffix.lower(), package=True)


def render(office, workspace_dir, document):
    with tempfile.TemporaryDirectory(prefix=".kmd-render-", dir=workspace_dir) as temp:
        scratch = Path(temp)
        docx = scratch / "document.docx"
        docx.write_bytes(document)
        system = {key: os.environ[key] for key in ("SystemRoot", "WINDIR") if key in os.environ}
        paths = (str(Path(system["SystemRoot"]) / "System32") if "SystemRoot" in system
                 else os.defpath)
        environment = dict(system, PATH=paths, HOME=temp, USERPROFILE=temp, APPDATA=temp,
                           LOCALAPPDATA=temp, TEMP=temp, TMP=temp, TMPDIR=temp)
        options = '{"UseTaggedPDF":{"type":"boolean","value":"true"}}'
        subprocess.run(
            [str(office), "-env:UserInstallation=" + (scratch / "profile").as_uri(),
             "--headless", "--nologo", "--nodefault", "--norestore",
             "--convert-to", "pdf:writer_pdf_Export:" + options, "--outdir", temp, str(docx)],
            cwd=scratch, env=environment, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, shell=False, timeout=60, check=True,
        )
        return bounded_read(scratch / "document.pdf", PDF_LIMIT)


def main():
    args = parser(__doc__)
    args.add_argument("--renderer", required=True, help="absolute operator-approved soffice path")
    options = args.parse_args()
    try:
        import pypdf
        if pypdf.__version__ != "7.2.0":
            raise ValueError("the pinned PDF validator is required")
        brief, output, illustrations = cli_paths(options, ".pdf")
        spec, document = build_document(brief, illustrations=illustrations)
        if "pdf" not in spec["formats"]:
            raise ValueError("the brief does not request PDF")
        renderer = renderer_path(options.renderer)
        plain_path(renderer)
        result = render(renderer, output.parent, document)
        pdf = check_pdf(result)
        publish_new(output, result)
    except (ImportError, ValueError, OSError, ET.ParseError, BadZipFile,
            subprocess.SubprocessError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    except pypdf.errors.PyPdfError:
        print("BLOCKED: the renderer produced an invalid PDF.", file=sys.stderr)
        return 2
    print(f"PASS: PDF structure verified ({len(pdf.pages)} pages). Visual review is separate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
