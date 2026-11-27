"""Check the exact package profile emitted by KMDStudio."""

import io
import re
import stat
import xml.etree.ElementTree as ET
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from guard import DOCX_LIMIT, ICON_LIMIT, XML_LIMIT, parse_xml, relative_parts
from ooxml import MAIN_RELS, ROOT_RELS, R, content_types, q, relationships

ROOTS = {
    "word/document.xml": "w:document",
    "word/styles.xml": "w:styles",
    "word/numbering.xml": "w:numbering",
    "word/footer1.xml": "w:ftr",
    "docProps/core.xml": "cp:coreProperties",
}
WORD_TAGS = """
document background body p pPr pStyle r rPr t tab br b color keepNext keepLines pageBreakBefore
widowControl pBdr left shd spacing ind outlineLvl jc numPr ilvl numId bookmarkStart
bookmarkEnd sectPr pgSz pgMar hdr ftr headerReference footerReference fldSimple styles
style name basedOn next qFormat rFonts sz szCs lang docDefaults rPrDefault
numbering abstractNum multiLevelType
lvl start numFmt lvlText lvlJc tabs num abstractNumId drawing tbl tblPr tblW tblBorders
bottom insideH insideV tblLayout tblCellMar top right tblGrid gridCol tr trPr cantSplit tblHeader
tc tcPr tcW
"""
DRAWING_TAGS = {
    "wp": "inline extent docPr cNvGraphicFramePr",
    "a": ("graphicFrameLocks graphic graphicData blip stretch fillRect "
          "xfrm off ext prstGeom avLst"),
    "pic": "pic nvPicPr cNvPr cNvPicPr blipFill spPr",
}
ALLOWED_TAGS = {q("w:" + name) for name in WORD_TAGS.split()}
for prefix, names in DRAWING_TAGS.items():
    ALLOWED_TAGS.update(q(prefix + ":" + name) for name in names.split())
ALLOWED_TAGS.update(map(q, ("cp:coreProperties", "dc:title", "dc:description", "dc:language")))
ALLOWED_ATTRS = {q("w:" + key) for key in """
    val type default styleId before after line lineRule left right fill color sz space
    ascii hAnsi eastAsia cs abstractNumId ilvl pos numId id name w h top bottom header
    footer gutter hanging instr
""".split()}
ALLOWED_ATTRS.update("""
    distT distB distL distR cx cy id name descr noChangeAspect uri x y prst
""".split())
ALLOWED_ATTRS.add(q("xml:space"))


def read_archive(data):
    if len(data) > DOCX_LIMIT:
        raise ValueError("DOCX exceeds size limit")
    parts = {}
    with ZipFile(io.BytesIO(data)) as archive:
        entries = archive.infolist()
        if not 8 <= len(entries) <= 21 or archive.comment:
            raise ValueError("DOCX archive profile is invalid")
        if sum(entry.file_size for entry in entries) > DOCX_LIMIT:
            raise ValueError("DOCX expanded size exceeds limit")
        names = set()
        for entry in entries:
            name = entry.orig_filename
            relative_parts(name)
            limit = ICON_LIMIT if name.endswith(".png") else XML_LIMIT
            if (name != entry.filename or "\\" in name or name.casefold() in names
                    or entry.flag_bits & 1 or entry.compress_type not in {ZIP_STORED, ZIP_DEFLATED}
                    or entry.file_size > limit or entry.file_size > 200 * max(entry.compress_size, 1)
                    or entry.extra or entry.comment or stat.S_ISLNK(entry.external_attr >> 16)):
                raise ValueError("unsafe DOCX archive entry")
            names.add(name.casefold())
            with archive.open(entry) as stream:
                content = stream.read(limit + 1)
            if len(content) != entry.file_size:
                raise ValueError("DOCX archive size mismatch")
            parts[name] = content
    return parts


def check_tree(name, root, images):
    fields = 0
    for node in root.iter():
        if node.tag not in ALLOWED_TAGS:
            raise ValueError("unexpected XML element in DOCX")
        for key, value in node.attrib.items():
            if key == q("w:instr"):
                if node.tag != q("w:fldSimple") or name != "word/footer1.xml" or value != "PAGE":
                    raise ValueError("unexpected document field")
                fields += 1
            elif key == q("r:embed"):
                if (node.tag != q("a:blip") or name != "word/document.xml"
                        or value not in images):
                    raise ValueError("unexpected image reference")
            elif key == q("r:id"):
                reference = {"w:headerReference": "rIdHeader", "w:footerReference": "rIdFooter"}
                if name != "word/document.xml" or not any(
                    node.tag == q(tag) and value == rid for tag, rid in reference.items()
                ):
                    raise ValueError("unexpected relationship reference")
            elif key not in ALLOWED_ATTRS:
                raise ValueError("unexpected XML attribute in DOCX")
        if node.tag == q("w:fldSimple") and q("w:instr") not in node.attrib:
            raise ValueError("field instruction is missing")
        if node.tag == q("w:br") and node.get(q("w:type")) not in {None, "page"}:
            raise ValueError("unexpected document break")
        if node.tag == q("w:t") and (len(node) or node.get(q("xml:space")) != "preserve"):
            raise ValueError("editable text must preserve whitespace")
    if name == "word/footer1.xml" and fields != 1:
        raise ValueError("expected exactly one footer PAGE field")


def _records(root):
    if root.attrib or (root.text or "").strip():
        raise ValueError("unexpected package metadata content")
    if any(len(child) or child.text or (child.tail or "").strip() for child in root):
        raise ValueError("unexpected nested package metadata")
    return sorted((node.tag, sorted(node.attrib.items())) for node in root)


def check_structure(trees, images, has_header):
    document = trees["word/document.xml"]
    children = [node.tag for node in document]
    if children not in ([q("w:body")], [q("w:background"), q("w:body")]):
        raise ValueError("expected exactly one document body")
    body = document[-1]
    sections = list(document.iter(q("w:sectPr")))
    if not len(body) or sections != [body[-1]]:
        raise ValueError("expected one final page section")
    for tag, expected in (("headerReference", int(has_header)), ("footerReference", 1)):
        references = list(document.iter(q("w:" + tag)))
        if (len(references) != expected or any(node not in body[-1] for node in references)
                or any(node.get(q("w:type")) != "default" or q("r:id") not in node.attrib
                       for node in references)):
            raise ValueError("invalid section relationship reference")

    drawings = list(document.iter(q("w:drawing")))
    picture_ids = []
    for index, drawing in enumerate(drawings, 1):
        props = drawing.findall(f"{q('wp:inline')}/{q('wp:docPr')}")
        blips = list(drawing.iter(q("a:blip")))
        if (len(props) != 1 or props[0].get("id") != str(index) or "descr" not in props[0].attrib
                or len(blips) != 1 or q("r:embed") not in blips[0].attrib):
            raise ValueError("invalid image structure")
        picture_ids.append(blips[0].get(q("r:embed")))
    if set(picture_ids) != images or len(picture_ids) != len(list(document.iter(q("a:blip")))):
        raise ValueError("unused or misplaced image reference")

    bookmarks = []
    for para in body.iter(q("w:p")):
        starts, ends = para.findall(q("w:bookmarkStart")), para.findall(q("w:bookmarkEnd"))
        if starts or ends:
            identity = str(len(bookmarks) + 1)
            if (len(starts) != 1 or len(ends) != 1 or len(para) < 4
                    or para[1] is not starts[0] or para[-1] is not ends[0]
                    or starts[0].get(q("w:id")) != identity or ends[0].get(q("w:id")) != identity
                    or not re.fullmatch(r"kmd_[a-z][a-z0-9_]{0,31}",
                                       starts[0].get(q("w:name"), ""))):
                raise ValueError("invalid block bookmark")
            bookmarks.append(starts[0].get(q("w:name")))
    if (not bookmarks or len(bookmarks) != len(set(bookmarks))
            or any(len(list(document.iter(q(tag)))) != len(bookmarks)
                   for tag in ("w:bookmarkStart", "w:bookmarkEnd"))):
        raise ValueError("invalid or misplaced block bookmark")

    for table in body.iter(q("w:tbl")):
        rows = table.findall(q("w:tr"))
        columns = len(table.findall(f"{q('w:tblGrid')}/{q('w:gridCol')}"))
        layout = table.find(f"{q('w:tblPr')}/{q('w:tblLayout')}")
        header_path = f"{q('w:trPr')}/{q('w:tblHeader')}"
        if (not 2 <= columns <= 5 or len(rows) < 2
                or layout is None or layout.attrib != {q("w:type"): "fixed"}
                or [row for row in rows if row.find(header_path) is not None] != rows[:1]
                or any(len(row.findall(q("w:tc"))) != columns for row in rows)):
            raise ValueError("invalid editable table structure")

    numbering = trees["word/numbering.xml"]
    ids = [node.get(q("w:numId")) for node in numbering.findall(q("w:num"))]
    numbers = {node.get(q("w:val")) for node in document.iter(q("w:numId"))}
    if ids != [str(index) for index in range(1, len(ids) + 1)] or numbers != set(ids):
        raise ValueError("invalid list numbering references")

    footer = trees["word/footer1.xml"]
    if len(footer.findall(f"{q('w:p')}/{q('w:fldSimple')}")) != 1:
        raise ValueError("invalid footer field placement")


def check_docx(data, assets, *, spec=None):
    parts = read_archive(data)
    image_parts = sorted(
        (name for name in parts if re.fullmatch(r"word/media/image[1-9][0-9]?\.png", name)),
        key=lambda name: int(name.split("image")[-1][:-4]),
    )
    roots = dict(ROOTS)
    rels = list(MAIN_RELS)
    has_header = "word/header1.xml" in parts
    if has_header:
        roots["word/header1.xml"] = "w:hdr"
        rels.append(("rIdHeader", R + "/header", "header1.xml"))
    image_ids = set()
    for index, name in enumerate(image_parts, 1):
        if name != f"word/media/image{index}.png" or parts[name] not in assets.values():
            raise ValueError("image is outside the verified library")
        identity = f"rIdImage{index}"
        rels.append((identity, R + "/image", f"media/image{index}.png"))
        image_ids.add(identity)
    metadata = {
        "[Content_Types].xml": content_types(has_header, bool(image_parts)),
        "_rels/.rels": relationships(ROOT_RELS),
        "word/_rels/document.xml.rels": relationships(rels),
    }
    if set(parts) != set(roots) | set(metadata) | set(image_parts):
        raise ValueError("unexpected or missing DOCX part")
    for name, generated in metadata.items():
        root = parse_xml(parts[name])
        expected = parse_xml(ET.tostring(generated, encoding="utf-8"))
        if root.tag != expected.tag or _records(root) != _records(expected):
            raise ValueError("unexpected content types or relationships")
    trees = {}
    for name, tag in roots.items():
        root = parse_xml(parts[name])
        if root.tag != q(tag):
            raise ValueError("unexpected root in DOCX XML part")
        check_tree(name, root, image_ids)
        trees[name] = root
    check_structure(trees, image_ids, has_header)
    if spec is not None:
        check_content(trees["word/document.xml"], spec)
        check_metadata(trees, parts, assets, spec)
    return trees["word/document.xml"]


def text_paragraphs(document, *, arrows=False):
    result = []
    for para in document.iter(q("w:p")):
        style = para.find(f"{q('w:pPr')}/{q('w:pStyle')}")
        if not arrows and style is not None and style.get(q("w:val")) == "DiagramArrow":
            continue
        pieces = []
        for node in para.iter():
            if node.tag == q("w:t"):
                pieces.append(node.text or "")
            elif node.tag == q("w:tab"):
                pieces.append("\t")
            elif node.tag == q("w:br") and q("w:type") not in node.attrib:
                pieces.append("\n")
        if pieces:
            result.append("".join(pieces))
    return result


def check_content(document, spec):
    headline = [spec["title"]]
    if "subtitle" in spec:
        headline.append(spec["subtitle"])
    expected = [] if spec["blocks"][0]["kind"] == "cover" else list(headline)
    for block in spec["blocks"]:
        match block["kind"]:
            case "cover":
                expected.extend([block["label"], *headline, block["lead"]])
                if "caption" in block:
                    expected.append(block["caption"])
            case "heading" | "paragraph":
                expected.append(block["text"])
            case "list":
                expected.extend(block["items"])
            case "callout":
                expected.extend([block["title"], block["text"]])
            case "code" | "table":
                if "caption" in block:
                    expected.append(block["caption"])
                if block["kind"] == "code":
                    expected.append(block["text"])
                else:
                    expected.extend(block["headers"])
                    for row in block["rows"]:
                        expected.extend(row)
            case "diagram":
                expected.append(block["caption"])
                for index, step in enumerate(block["steps"]):
                    if index:
                        expected.append("↓")
                    expected.extend([step["label"], step["detail"]])
            case "figure":
                expected.append(block["caption"])
            case "exercise":
                expected.extend([block["title"], block["intro"], *block["steps"]])
                if "check" in block:
                    expected.append(block["check"])
    bookmarks = [node.get(q("w:name")) for node in document.iter(q("w:bookmarkStart"))]
    expected_names = ["kmd_" + block["id"].replace("-", "_") for block in spec["blocks"]]
    if text_paragraphs(document, arrows=True) != expected or bookmarks != expected_names:
        raise ValueError("editable content or block identifiers differ from the brief")


def check_metadata(trees, parts, assets, spec):
    design = spec["design"]
    header = trees.get("word/header1.xml")
    expected_header = [design["header"]] if "header" in design else []
    expected_footer = design["footer"] + "  ·  1" if "footer" in design else "1"
    core = trees["docProps/core.xml"]
    expected_core = [(q("dc:" + key), spec[field]) for key, field in
                     (("title", "title"), ("description", "purpose"), ("language", "language"))]
    if (bool(expected_header) != (header is not None)
            or (header is not None and text_paragraphs(header) != expected_header)
            or text_paragraphs(trees["word/footer1.xml"]) != [expected_footer]
            or [(node.tag, node.text) for node in core] != expected_core):
        raise ValueError("running text or document metadata differ from the brief")

    expected_images = [(block["asset"], block["alt"]) for block in spec["blocks"]
                       if block["kind"] == "figure"]
    cover = spec["blocks"][0]
    if cover["kind"] == "cover" and "icon" in cover:
        expected_images.insert(0, (cover["icon"], ""))
    actual_images = []
    for drawing in trees["word/document.xml"].iter(q("w:drawing")):
        properties = next(drawing.iter(q("wp:docPr")))
        identity = next(drawing.iter(q("a:blip"))).get(q("r:embed"))
        name = properties.get("name")
        if parts[f"word/media/image{identity.removeprefix('rIdImage')}.png"] != assets.get(name):
            raise ValueError("embedded image differs from the named asset")
        actual_images.append((name, properties.get("descr")))
    if actual_images != expected_images:
        raise ValueError("figure or alternative text differs from the brief")
