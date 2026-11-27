"""Check the exact package profile emitted by KMDStudio."""

import io
import re
import stat
import xml.etree.ElementTree as ET
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from design import resolve_design
from guard import DOCX_LIMIT, XML_LIMIT, check_png, parse_xml, relative_parts
from ooxml import MAIN_RELS, ROOT_RELS, R, content_types, q, relationships
from raster import RASTER_EDGE, RASTER_LIMIT
from spec import COLUMN_GAP_MM, column_ranges

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
bookmarkEnd sectPr type cols pgSz pgMar hdr ftr headerReference footerReference fldSimple styles
style name basedOn next qFormat rFonts sz szCs lang docDefaults rPrDefault
numbering abstractNum multiLevelType
lvl start numFmt lvlText lvlJc tabs num abstractNumId lvlOverride startOverride drawing tbl tblPr tblW tblBorders
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
    footer gutter hanging instr num equalWidth
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
            limit = RASTER_LIMIT if name.endswith(".png") else XML_LIMIT
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


def section_signature(document, body, has_header):
    sections = []
    endpoints = []
    blocks = 0
    for position, node in enumerate(body):
        if node.tag == q("w:sectPr") and node is body[-1]:
            sections.append(node)
        else:
            blocks += sum(1 for _ in node.iter(q("w:bookmarkStart")))
            section = node.find(f"{q('w:pPr')}/{q('w:sectPr')}")
            if section is not None:
                props = node[0]
                spacing = {q("w:" + key): value for key, value in
                           {"before": "0", "after": "0", "line": "20", "lineRule": "exact"}.items()}
                if (node.tag != q("w:p") or len(node) != 1 or props.tag != q("w:pPr")
                        or [child.tag for child in props] != [q("w:spacing"), q("w:sectPr")]
                        or props[0].attrib != spacing or position + 1 >= len(body)
                        or next(body[position + 1].iter(q("w:bookmarkStart")), None) is None):
                    raise ValueError("invalid continuous section boundary")
                sections.append(section)
                endpoints.append(blocks)
    if (not sections or sections[-1] is not body[-1]
            or sections != list(document.iter(q("w:sectPr")))
            or len(sections) > 13 or endpoints != sorted(set(endpoints))):
        raise ValueError("invalid section placement")
    references = (["headerReference"] if has_header else []) + ["footerReference"]
    reference_tags = {q("w:" + tag) for tag in references}
    expected_references = []
    column_nodes = []
    margins = []
    for index, section in enumerate(sections):
        columns = index % 2 == 1
        children = references + (["type"] if len(sections) > 1 else [])
        children += ["pgSz", "pgMar"] + (["cols"] if columns else [])
        if (section.attrib or [child.tag for child in section] != [q("w:" + tag) for tag in children]
                or any(len(child) for child in section)):
            raise ValueError("invalid section properties")
        expected_references.extend(section[:len(references)])
        for reference in section[:len(references)]:
            if (reference.get(q("w:type")) != "default" or len(reference.attrib) != 2
                    or q("r:id") not in reference.attrib):
                raise ValueError("invalid section relationship reference")
        if len(sections) > 1 and section[len(references)].attrib != {q("w:val"): "continuous"}:
            raise ValueError("expected a continuous section")
        page = section.find(q("w:pgSz"))
        if page.attrib != {q("w:w"): "11906", q("w:h"): "16838"}:
            raise ValueError("invalid A4 section geometry")
        margins.append(section.find(q("w:pgMar")).attrib)
        if columns:
            cols = section[-1]
            gap = str(round(COLUMN_GAP_MM * 1440 / 25.4))
            if cols.attrib != {q("w:num"): "2", q("w:space"): gap, q("w:equalWidth"): "1"}:
                raise ValueError("invalid two-column geometry")
            column_nodes.append(cols)
    if ([node for node in document.iter() if node.tag in reference_tags] != expected_references
            or list(document.iter(q("w:cols"))) != column_nodes
            or list(document.iter(q("w:type"))) != [
                section.find(q("w:type")) for section in sections if len(sections) > 1]
            or any(margin != margins[0] for margin in margins)):
        raise ValueError("inconsistent or misplaced section properties")
    return endpoints, margins[0]


def check_structure(trees, images, has_header):
    document = trees["word/document.xml"]
    children = [node.tag for node in document]
    if children not in ([q("w:body")], [q("w:background"), q("w:body")]):
        raise ValueError("expected exactly one document body")
    body = document[-1]
    sections = section_signature(document, body, has_header)

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
        if (table not in body or not 2 <= columns <= 5 or not rows
                or layout is None or layout.attrib != {q("w:type"): "fixed"}
                or any(len(row.findall(q("w:tc"))) != columns for row in rows)):
            raise ValueError("invalid editable table structure")
        if len(rows) > 1:
            if [row for row in rows if row.find(header_path) is not None] != rows[:1]:
                raise ValueError("invalid repeating header in data table")
        else:
            check_figure_table(table, rows[0], sections[1])

    numbering = trees["word/numbering.xml"]
    instances = numbering.findall(q("w:num"))
    ids = [node.get(q("w:numId")) for node in instances]
    numbers = {node.get(q("w:val")) for node in document.iter(q("w:numId"))}
    if ids != [str(index) for index in range(1, len(ids) + 1)] or numbers != set(ids):
        raise ValueError("invalid list numbering references")
    kinds = [node[0].get(q("w:val")) if len(node) and node[0].tag == q("w:abstractNumId")
             else None for node in instances]
    multiple_ordered = kinds.count("1") > 1
    for node, kind in zip(instances, kinds, strict=True):
        restart = kind == "1" and multiple_ordered
        if kind not in {"0", "1", "2"} or len(node) != 1 + restart:
            raise ValueError("invalid list numbering instance")
        if restart:
            override = node[1]
            if (override.tag != q("w:lvlOverride") or override.attrib != {q("w:ilvl"): "0"}
                    or len(override) != 1 or override[0].tag != q("w:startOverride")
                    or override[0].attrib != {q("w:val"): "1"} or len(override[0])):
                raise ValueError("ordered list must restart at one")

    footer = trees["word/footer1.xml"]
    if len(footer.findall(f"{q('w:p')}/{q('w:fldSimple')}")) != 1:
        raise ValueError("invalid footer field placement")
    return sections


def check_figure_table(table, row, margins):
    if ([node.tag for node in table] != [q("w:tblPr"), q("w:tblGrid"), q("w:tr")]
            or [node.tag for node in row] != [q("w:trPr"), q("w:tc"), q("w:tc")]):
        raise ValueError("invalid text-and-figure row")
    props, left, right = row
    if ([node.tag for node in props] != [q("w:cantSplit")] or props[0].attrib or len(props[0])
            or [node.tag for node in left] != [q("w:tcPr"), q("w:p")]
            or [node.tag for node in right] != [q("w:tcPr"), q("w:p"), q("w:p")]
            or not text_paragraphs(left)
            or list(table.iter(q("w:drawing"))) != list(right[1].iter(q("w:drawing")))
            or len(list(right[1].iter(q("w:drawing")))) != 1):
        raise ValueError("invalid text-and-figure reading order")
    props, grid, _ = table
    widths = [col.get(q("w:w"), "") for col in grid]
    margin = margins.get(q("w:left"), "")
    tags = [q("w:" + tag) for tag in ("tblW", "tblLayout", "tblCellMar")]
    if (len(widths) != 2 or not all(re.fullmatch("[1-9][0-9]{0,4}", n) for n in [*widths, margin])
            or [col.tag for col in grid] != [q("w:gridCol")] * 2
            or [node.tag for node in props] != tags):
        raise ValueError("invalid text-and-figure geometry")
    width = 11906 - 2 * int(margin)
    if ([int(n) for n in widths] != [width - width * 2 // 5, width * 2 // 5]
            or props[0].attrib != {q("w:w"): str(width), q("w:type"): "dxa"}):
        raise ValueError("invalid text-and-figure proportions")
    for cell, expected in zip((left, right), widths, strict=True):
        if (len(cell[0]) != 1 or cell[0][0].tag != q("w:tcW")
                or cell[0][0].attrib != {q("w:w"): expected, q("w:type"): "dxa"}):
            raise ValueError("invalid text-and-figure cell width")


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
    endpoints, margins = check_structure(trees, image_ids, has_header)
    if spec is not None:
        check_content(trees["word/document.xml"], spec)
        expected_endpoints = [i for start, end in column_ranges(spec) for i in (start, end + 1)
                              if i < len(spec["blocks"])]
        margin = str(round(resolve_design(spec["design"])["spacing"]["margin_mm"] * 1440 / 25.4))
        expected_margins = {q("w:" + edge): margin for edge in ("top", "right", "bottom", "left")}
        expected_margins.update({q("w:header"): "510", q("w:footer"): "510", q("w:gutter"): "0"})
        if endpoints != expected_endpoints or margins != expected_margins:
            raise ValueError("section layout differs from the brief")
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
                if "illustration" in block:
                    expected.append(block["illustration"]["caption"])
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
                if "side_text" in block:
                    expected.append(block["side_text"])
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

    expected_images = [(block["asset"], block["alt"], block["width_mm"]) for block in spec["blocks"]
                       if block["kind"] == "figure"]
    cover = spec["blocks"][0]
    if cover["kind"] == "cover" and "icon" in cover:
        expected_images.insert(0, (cover["icon"], "", 27))
    if cover["kind"] == "cover" and "illustration" in cover:
        image = cover["illustration"]
        expected_images.insert(0, (image["asset"], image["alt"], image["width_mm"]))
    actual_images = []
    for drawing in trees["word/document.xml"].iter(q("w:drawing")):
        properties = next(drawing.iter(q("wp:docPr")))
        identity = next(drawing.iter(q("a:blip"))).get(q("r:embed"))
        name = properties.get("name")
        if parts[f"word/media/image{identity.removeprefix('rIdImage')}.png"] != assets.get(name):
            raise ValueError("embedded image differs from the named asset")
        extent = next(drawing.iter(q("wp:extent")), None)
        transform = next(drawing.iter(q("a:ext")), None)
        if extent is None or transform is None or extent.attrib != transform.attrib:
            raise ValueError("invalid drawing dimensions")
        actual_images.append((name, properties.get("descr"), extent.attrib))
    expected = []
    for asset, alt, size_mm in expected_images:
        width, height = check_png(assets[asset], max_edge=RASTER_EDGE)
        expected.append((asset, alt, {"cx": str(size_mm * 36000),
                                     "cy": str(round(size_mm * 36000 * height / width))}))
    if actual_images != expected:
        raise ValueError("figure or alternative text differs from the brief")

    figures = {"kmd_" + block["id"].replace("-", "_"): block
               for block in spec["blocks"] if block["kind"] == "figure"}
    document = trees["word/document.xml"]
    body = document.find(q("w:body"))
    named_paragraphs = {bookmark.get(q("w:name")): para for para in body.iter(q("w:p"))
                        for bookmark in para.findall(q("w:bookmarkStart"))}
    keep_lines = f"{q('w:pPr')}/{q('w:keepLines')}"
    keep_next = f"{q('w:pPr')}/{q('w:keepNext')}"
    for block in spec["blocks"]:
        if block["kind"] == "paragraph":
            para = named_paragraphs["kmd_" + block["id"].replace("-", "_")]
            if (para.find(keep_lines) is not None) != block.get("keep_lines", False):
                raise ValueError("paragraph flow differs from the brief")
    data_tables = [node for node in body.findall(q("w:tbl")) if len(node.findall(q("w:tr"))) > 1]
    for table, block in zip(data_tables, (b for b in spec["blocks"] if b["kind"] == "table"),
                            strict=True):
        rows = table.findall(q("w:tr"))
        for index, row in enumerate(rows):
            expected_keep = index == 0 or (block.get("keep_rows") and index < len(rows) - 1)
            if any((para.find(keep_next) is not None) != bool(expected_keep)
                   for para in row.iter(q("w:p"))):
                raise ValueError("table flow differs from the brief")
    slots = {}
    for index, node in enumerate(body):
        if node.tag == q("w:tbl"):
            row = node.findall(q("w:tr"))
            if len(row) == 1:
                text, picture_cell = row[0][1:]
                bookmark = text[1].find(q("w:bookmarkStart"))
                name = bookmark.get(q("w:name")) if bookmark is not None else None
                if name not in figures or "side_text" not in figures[name]:
                    raise ValueError("unexpected text-and-figure composition")
                slots[name] = tuple(picture_cell[1:])
        elif node.tag == q("w:p"):
            bookmark = node.find(q("w:bookmarkStart"))
            if bookmark is not None and bookmark.get(q("w:name")) in figures:
                name = bookmark.get(q("w:name"))
                if "side_text" in figures[name]:
                    raise ValueError("missing text-and-figure composition")
                slots[name] = (node, body[index + 1])
    if slots.keys() != figures.keys():
        raise ValueError("missing figure slot")
    if "illustration" in cover:
        index = 4 if "subtitle" in spec else 3
        figures["cover"] = cover["illustration"]
        slots["cover"] = (body[index], body[index + 1])
    for name, (picture, caption) in slots.items():
        figure = figures[name]
        align = figure.get("align", "center")
        for paragraph in (picture, caption):
            alignment = paragraph.find(f"{q('w:pPr')}/{q('w:jc')}")
            if alignment is None or alignment.get(q("w:val")) != align:
                raise ValueError("figure or caption alignment differs from the brief")
        if (picture.tag != q("w:p") or caption.tag != q("w:p") or text_paragraphs(picture)
                or len(list(picture.iter(q("w:drawing")))) != 1
                or picture.find(keep_next) is None or picture.find(keep_next).attrib
                or text_paragraphs(caption) != [figure["caption"]]):
            raise ValueError("figure must stay with its editable caption")
