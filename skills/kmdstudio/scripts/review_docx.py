"""Check the exact package profile emitted by KMDStudio."""

import io
import re
import stat
import xml.etree.ElementTree as ET
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from design import EDITORIAL_MODES, resolve_design
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
    tracking = set(root.findall(f"{q('w:style')}/{q('w:rPr')}/{q('w:spacing')}"))
    for spacing in root.iter(q("w:spacing")):
        if spacing in tracking or q("w:val") in spacing.attrib:
            value = spacing.get(q("w:val"), "")
            if (name != "word/styles.xml" or spacing not in tracking or len(spacing)
                    or len(spacing.attrib) != 1 or not re.fullmatch(r"-?[0-9]{1,2}", value)
                    or not -24 <= int(value) <= 30):
                raise ValueError("unexpected character spacing")
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

    editorial = any(style.get(q("w:styleId")) == "MetadataLabel"
                    for style in trees["word/styles.xml"].findall(q("w:style")))
    if editorial and any(a.tag == b.tag == q("w:tbl") for a, b in zip(body, body[1:])):
        raise ValueError("adjacent editorial tables require a separating paragraph")
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
            for index, row in enumerate(rows):
                for cell in row.findall(q("w:tc")):
                    tags = [node.tag for node in cell]
                    if tags == [q("w:tcPr"), q("w:p")]:
                        continue
                    if (not editorial or index == 0
                            or tags != [q("w:tcPr"), q("w:p"), q("w:p")]):
                        raise ValueError("unexpected data table cell structure")
                    data_bar(cell[2])
        else:
            check_paired_table(table, rows[0], sections[1], editorial)

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


def paragraph_value(node, property_name):
    prop = node.find(f"{q('w:pPr')}/{q('w:' + property_name)}")
    return None if prop is None else prop.get(q("w:val"))


def data_bar(node):
    props = node.find(q("w:pPr"))
    if node.attrib or len(node) != 1 or props is None or props.attrib:
        raise ValueError("invalid data bar structure")
    keep = props.find(q("w:keepNext"))
    remaining = props[:] if keep is None else props[1:]
    if ((keep is not None and (props[0] is not keep or keep.attrib or len(keep)))
            or [child.tag for child in remaining] != [q("w:" + name) for name in ("pBdr", "spacing", "ind")]):
        raise ValueError("invalid data bar structure")
    border, spacing, indent = remaining
    color = border[0].get(q("w:color"), "") if len(border) == 1 else ""
    right = indent.get(q("w:right"), "")
    expected = {q("w:" + k): v for k, v in {"val": "single", "sz": "28", "space": "0", "color": color}.items()}
    if (not re.fullmatch(r"[0-9A-F]{6}", color) or border.attrib
            or border[0].tag != q("w:bottom") or border[0].attrib != expected
            or len(border[0]) or len(spacing) or len(indent)
            or spacing.attrib != {q("w:before"): "0", q("w:after"): "0",
                                  q("w:line"): "120", q("w:lineRule"): "exact"}
            or not re.fullmatch(r"[0-9]{1,5}", right) or int(right) >= 11906
            or indent.attrib != {q("w:left"): "0", q("w:right"): right}):
        raise ValueError("invalid data bar geometry")
    return int(right), color


def check_bar_grid(table, block, design):
    spacing = design["spacing"]
    width = 11906 - 2 * round(spacing["margin_mm"] * 1440 / 25.4)
    weights = block.get("column_weights", [1] * len(block["headers"]))
    widths = [width * weight // sum(weights) for weight in weights[:-1]]
    widths.append(width - sum(widths))
    columns = table.find(q("w:tblGrid"))
    props = table.find(q("w:tblPr"))
    margins = props.find(q("w:tblCellMar")) if props is not None else None
    expected_margin = {q("w:w"): str(spacing["cell_pt"] * 20), q("w:type"): "dxa"}
    if (columns is None or [node.attrib for node in columns] != [{q("w:w"): str(n)} for n in widths]
            or margins is None or any(node.attrib != expected_margin for node in margins)
            or [node.tag for node in margins] != [q("w:" + edge) for edge in ("top", "left", "bottom", "right")]):
        raise ValueError("data bar grid or margins differ from the brief")
    return widths


def check_paired_table(table, row, margins, editorial):
    if ([node.tag for node in table] != [q("w:tblPr"), q("w:tblGrid"), q("w:tr")]
            or [node.tag for node in row] != [q("w:trPr"), q("w:tc"), q("w:tc")]):
        raise ValueError("invalid text-and-figure row")
    props, left, right = row
    if ([node.tag for node in props] != [q("w:cantSplit")] or props[0].attrib or len(props[0])
            or any(len(cell) < 2 or cell[0].tag != q("w:tcPr") or any(
                node.tag != q("w:p") for node in cell[1:]) for cell in (left, right))):
        raise ValueError("invalid text-and-figure or metadata row reading order")
    drawings = list(table.iter(q("w:drawing")))
    if drawings:
        if (len(left) != 2 or len(right) != 3 or len(drawings) != 1
                or drawings != list(right[1].iter(q("w:drawing"))) or not text_paragraphs(left)):
            raise ValueError("invalid text-and-figure reading order")
        percentages = range(30, 66) if editorial else (40,)
    else:
        count = len(left) - 1
        if (not editorial or count not in {2, 4, 6, 8} or len(right) != 2
                or [paragraph_value(p, "pStyle") for p in left[1:]]
                != ["MetadataLabel", "MetadataValue"] * (count // 2)
                or paragraph_value(right[1], "pStyle") != "Normal"
                or len(text_paragraphs(table)) != count + 1):
            raise ValueError("invalid metadata sidebar reading order")
        percentages = range(60, 76)
    props, grid, _ = table
    widths = [col.get(q("w:w"), "") for col in grid]
    margin = margins.get(q("w:left"), "")
    tags = [q("w:" + tag) for tag in ("tblW", "tblLayout", "tblCellMar")]
    if (len(widths) != 2 or not all(re.fullmatch("[1-9][0-9]{0,4}", n) for n in [*widths, margin])
            or [col.tag for col in grid] != [q("w:gridCol")] * 2
            or any(len(col) or len(col.attrib) != 1 for col in grid)
            or [node.tag for node in props] != tags):
        raise ValueError("invalid text-and-figure geometry")
    width = 11906 - 2 * int(margin)
    right_width = int(widths[1])
    if (sum(map(int, widths)) != width or right_width not in {width * p // 100 for p in percentages}
            or props[0].attrib != {q("w:w"): str(width), q("w:type"): "dxa"}):
        raise ValueError("invalid text-and-figure proportions")
    cell_margins = props[-1]
    if ([node.tag for node in cell_margins] != [q("w:" + tag) for tag in ("top", "left", "bottom", "right")]
            or any(node.attrib != cell_margins[0].attrib or len(node) for node in cell_margins)
            or cell_margins[0].get(q("w:w")) not in {str(pt * 20) for pt in range(4, 10)}
            or cell_margins[0].get(q("w:type")) != "dxa" or len(cell_margins[0].attrib) != 2):
        raise ValueError("invalid paired row cell margins")
    for index, (cell, expected) in enumerate(zip((left, right), widths, strict=True)):
        shaded = not drawings and index == 0
        tags = [q("w:tcW")] + ([q("w:shd")] if shaded else [])
        if ([node.tag for node in cell[0]] != tags
                or cell[0][0].attrib != {q("w:w"): expected, q("w:type"): "dxa"}):
            raise ValueError("invalid text-and-figure cell width")
        if shaded:
            shading = cell[0][1]
            if (len(shading) or len(shading.attrib) != 3 or shading.get(q("w:val")) != "clear"
                    or shading.get(q("w:color")) != "auto"
                    or not re.fullmatch(r"[0-9A-F]{6}", shading.get(q("w:fill"), ""))):
                raise ValueError("invalid metadata sidebar shading")
    if drawings:
        extent = next(drawings[0].iter(q("wp:extent")), None)
        padding = 2 * int(cell_margins[0].get(q("w:w")))
        if (extent is None or not re.fullmatch(r"[1-9][0-9]{0,6}", extent.get("cx", ""))
                or int(extent.get("cx")) > (right_width - padding) * 635):
            raise ValueError("paired figure exceeds its cell width")


def check_pair_width(table, right_percent, design):
    margin = round(design["spacing"]["margin_mm"] * 1440 / 25.4)
    width = (11906 - 2 * margin) * right_percent // 100
    columns = table.find(q("w:tblGrid"))
    padding = table.find(f"{q('w:tblPr')}/{q('w:tblCellMar')}/{q('w:left')}")
    if (columns[1].get(q("w:w")) != str(width)
            or padding.get(q("w:w")) != str(design["spacing"]["cell_pt"] * 20)):
        raise ValueError("paired row geometry differs from the brief")


def check_word_settings(data):
    root = parse_xml(data)
    nodes = list(root.iter())
    if ([node.tag for node in nodes] != [q("w:settings"), q("w:compat"), q("w:compatSetting")]
            or len(root) != 1 or len(root[0]) != 1
            or any(node.text or node.tail for node in nodes)
            or root.attrib or root[0].attrib
            or nodes[-1].attrib != {q("w:name"): "compatibilityMode",
                                    q("w:uri"): "http://schemas.microsoft.com/office/word",
                                    q("w:val"): "15"}):
        raise ValueError("unexpected Word settings")


def check_docx(data, assets, *, spec=None, available_fonts=()):
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
    settings_path = "word/settings.xml"
    has_settings = settings_path in parts
    if spec is not None and has_settings != (spec.get("word_compatibility") == "modern"):
        raise ValueError("Word compatibility differs from the brief")
    if has_settings:
        check_word_settings(parts[settings_path])
        rels.append(("rIdSettings", R + "/settings", "settings.xml"))
    image_ids = set()
    for index, name in enumerate(image_parts, 1):
        if name != f"word/media/image{index}.png" or parts[name] not in assets.values():
            raise ValueError("image is outside the verified library")
        identity = f"rIdImage{index}"
        rels.append((identity, R + "/image", f"media/image{index}.png"))
        image_ids.add(identity)
    metadata = {
        "[Content_Types].xml": content_types(has_header, bool(image_parts), modern=has_settings),
        "_rels/.rels": relationships(ROOT_RELS),
        "word/_rels/document.xml.rels": relationships(rels),
    }
    expected_parts = set(roots) | set(metadata) | set(image_parts)
    if has_settings:
        expected_parts.add(settings_path)
    if set(parts) != expected_parts:
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
        mode = spec.get("mode", "structured")
        design = resolve_design(spec["design"], mode, available_fonts)
        margin = str(round(design["spacing"]["margin_mm"] * 1440 / 25.4))
        expected_margins = {q("w:" + edge): margin for edge in ("top", "right", "bottom", "left")}
        expected_margins.update({q("w:header"): "510", q("w:footer"): "510", q("w:gutter"): "0"})
        if endpoints != expected_endpoints or margins != expected_margins:
            raise ValueError("section layout differs from the brief")
        check_metadata(trees, parts, assets, spec, design)
        if mode in EDITORIAL_MODES:
            check_editorial_styles(trees["word/styles.xml"], design, spec["blocks"])
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
                image_first = block.get("image_position") == "before-title"
                expected.append(block["label"])
                if image_first:
                    expected.append(block["illustration"]["caption"])
                expected.extend([*headline, block["lead"]])
                if "caption" in block:
                    expected.append(block["caption"])
                if "illustration" in block and not image_first:
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
            case "sidebar":
                for item in block["items"]:
                    expected.extend([item["label"], item["value"]])
                expected.append(block["text"])
            case "highlight":
                expected.extend([block["value"], block["label"]])
            case "exercise":
                expected.extend([block["title"], block["intro"], *block["steps"]])
                if "check" in block:
                    expected.append(block["check"])
    bookmarks = [node.get(q("w:name")) for node in document.iter(q("w:bookmarkStart"))]
    expected_names = ["kmd_" + block["id"].replace("-", "_") for block in spec["blocks"]]
    if text_paragraphs(document, arrows=True) != expected or bookmarks != expected_names:
        raise ValueError("editable content or block identifiers differ from the brief")


def check_editorial_styles(root, design, blocks):
    typography = design["typography"]
    colors = design["colors"]
    styles = {style.get(q("w:styleId")): style for style in root.findall(q("w:style"))}
    roles = {
        "Title": ("display", "primary", None),
        "CoverTitle": ("display", "primary", None),
        "Heading1": ("heading", "primary", None),
        "PanelHeading": ("heading", "on_primary", "primary"),
        "Caption": ("caption", "muted", None),
        "MetadataLabel": ("metadata", "accent", None),
        "HighlightInk": ("display", "on_primary", "primary"),
        "HighlightLight": ("display", "primary", "surface"),
        "HighlightInkLabel": ("metadata", "on_primary", "primary"),
        "HighlightLightLabel": ("metadata", "primary", "surface"),
    }
    if design["composition"]["cover"] == "panel":
        roles["CoverTitle"] = ("display", "on_primary", "primary")
    if any(block["kind"] == "highlight" and block.get("tone") == "plain" for block in blocks):
        roles["HighlightPlain"] = ("display", "primary", None)
        roles["HighlightPlainLabel"] = ("metadata", "muted", None)
    for name, (role, color, fill) in roles.items():
        style = styles.get(name)
        if style is None:
            raise ValueError("missing editorial style")
        run = style.find(q("w:rPr"))
        para = style.find(q("w:pPr"))
        if run is None or para is None:
            raise ValueError("incomplete editorial style")
        size = typography[role + "_pt"]
        if name in {"HighlightInk", "HighlightLight", "HighlightPlain"}:
            size = min(54, size)
        font = typography[role + "_font"]
        spacing = typography.get(role + "_tracking_twips")
        tracking = run.find(q("w:spacing"))
        expected_tracking = None if spacing is None else {q("w:val"): str(spacing)}
        shade = para.find(q("w:shd"))
        expected_shade = None if fill is None else {
            q("w:fill"): colors[fill], q("w:val"): "clear", q("w:color"): "auto",
        }
        line = typography.get(role + "_line_percent", typography["body_line_percent"])
        font_node = run.find(q("w:rFonts"))
        line_node = para.find(q("w:spacing"))
        if name == "PanelHeading" or (fill is not None and name.startswith("Highlight")):
            borders = para.find(q("w:pBdr"))
            border = {q("w:val"): "single", q("w:sz"): "4", q("w:space"): "6",
                      q("w:color"): colors[fill]}
            if (borders is None or [node.tag for node in borders]
                    != [q("w:" + edge) for edge in ("top", "left", "bottom", "right")]
                    or any(node.attrib != border or len(node) for node in borders)):
                raise ValueError(f"editorial panel padding differs for {name}")
        if (font_node is None or font_node.attrib != {q("w:" + key): font for key in
                                                     ("ascii", "hAnsi", "eastAsia", "cs")}
                or (run.find(q("w:b")) is not None) != (typography[role + "_weight"] == "bold")
                or run.find(f"{q('w:color')}[@{q('w:val')}='{colors[color]}']") is None
                or run.find(f"{q('w:sz')}[@{q('w:val')}='{size * 2}']") is None
                or (None if tracking is None else tracking.attrib) != expected_tracking
                or paragraph_value(style, "jc") != typography.get(role + "_align")
                or line_node is None or line_node.get(q("w:line")) != str(round(line * 2.4))
                or (None if shade is None else shade.attrib) != expected_shade):
            raise ValueError(f"editorial style {name} differs from the brief")
    if paragraph_value(styles["PanelHeading"], "outlineLvl") != "0":
        raise ValueError("section panel must retain its heading level")


def check_metadata(trees, parts, assets, spec, effective_design):
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
    page_breaks = [node for node in body.iter(q("w:br")) if node.get(q("w:type")) == "page"]
    expected_break = cover["kind"] == "cover" and cover.get("flow") != "continue" and len(spec["blocks"]) > 1
    if len(page_breaks) != int(expected_break):
        raise ValueError("cover flow differs from the brief")
    named_paragraphs = {bookmark.get(q("w:name")): para for para in body.iter(q("w:p"))
                        for bookmark in para.findall(q("w:bookmarkStart"))}
    keep_lines = f"{q('w:pPr')}/{q('w:keepLines')}"
    keep_next = f"{q('w:pPr')}/{q('w:keepNext')}"
    for block in spec["blocks"]:
        para = named_paragraphs["kmd_" + block["id"].replace("-", "_")]
        if block["kind"] == "paragraph":
            if (para.find(keep_lines) is not None) != block.get("keep_lines", False):
                raise ValueError("paragraph flow differs from the brief")
        if block["kind"] == "heading":
            expected_style = "PanelHeading" if "treatment" in block else f"Heading{block['level']}"
            if paragraph_value(para, "pStyle") != expected_style:
                raise ValueError("heading treatment differs from the brief")
            page_before = para.find(f"{q('w:pPr')}/{q('w:pageBreakBefore')}")
            if (page_before is not None) != block.get("new_page", False) or (
                    page_before is not None and (page_before.attrib or len(page_before))):
                raise ValueError("heading page break differs from the brief")
    data_tables = [node for node in body.findall(q("w:tbl")) if len(node.findall(q("w:tr"))) > 1]
    for table, block in zip(data_tables, (b for b in spec["blocks"] if b["kind"] == "table"),
                            strict=True):
        rows = table.findall(q("w:tr"))
        bars = block.get("bars")
        maximum = max(int(row[bars["column"] - 1]) for row in block["rows"][:bars["through"]]) if bars else 0
        if bars:
            widths = check_bar_grid(table, block, effective_design)
        for index, row in enumerate(rows):
            cells = row.findall(q("w:tc"))
            primary = [cell[1] for cell in cells]
            expected_keep = index == 0 or (block.get("keep_rows") and index < len(rows) - 1)
            if any((para.find(keep_next) is not None) != bool(expected_keep)
                   for para in row.iter(q("w:p"))):
                raise ValueError("table flow differs from the brief")
            if "column_alignments" in block:
                alignments = [paragraph_value(para, "jc") for para in primary]
                if alignments != block["column_alignments"]:
                    raise ValueError("table column alignment differs from the brief")
            for column, cell in enumerate(cells, 1):
                expected = None
                if bars and column == bars["column"] and 1 <= index <= bars["through"]:
                    cell_width = cell[0].find(q("w:tcW"))
                    width = widths[column - 1]
                    if (cell_width is None or cell_width.attrib != {q("w:w"): str(width), q("w:type"): "dxa"}
                            or not 0 < width < 11906):
                        raise ValueError("invalid data bar cell width")
                    usable = width - effective_design["spacing"]["cell_pt"] * 40
                    value = int(block["rows"][index - 1][column - 1])
                    length = usable * value // maximum
                    if length > 0:
                        expected = usable - length, effective_design["colors"]["accent"]
                actual = data_bar(cell[2]) if len(cell) == 3 else None
                if actual != expected:
                    raise ValueError("data bar proportions differ from the brief")
    slots = {}
    sidebars = {"kmd_" + block["id"].replace("-", "_"): block for block in spec["blocks"]
                if block["kind"] == "sidebar"}
    highlights = {"kmd_" + block["id"].replace("-", "_"): block for block in spec["blocks"]
                  if block["kind"] == "highlight"}
    observed_sidebars = set()
    for index, node in enumerate(body):
        if node.tag == q("w:tbl"):
            row = node.findall(q("w:tr"))
            if len(row) == 1:
                text, picture_cell = row[0][1:]
                bookmark = text[1].find(q("w:bookmarkStart"))
                name = bookmark.get(q("w:name")) if bookmark is not None else None
                if name in sidebars:
                    check_pair_width(node, 100 - sidebars[name]["sidebar_percent"], effective_design)
                    fill = text.find(f"{q('w:tcPr')}/{q('w:shd')}")
                    if fill is None or fill.get(q("w:fill")) != effective_design["colors"]["surface"]:
                        raise ValueError("sidebar surface differs from the brief")
                    observed_sidebars.add(name)
                    continue
                if name not in figures or "side_text" not in figures[name]:
                    raise ValueError("unexpected text-and-figure composition")
                check_pair_width(node, figures[name].get("image_percent", 40), effective_design)
                slots[name] = tuple(picture_cell[1:])
        elif node.tag == q("w:p"):
            bookmark = node.find(q("w:bookmarkStart"))
            name = bookmark.get(q("w:name")) if bookmark is not None else None
            if name in highlights:
                style = "Highlight" + highlights[name].get("tone", "light").title()
                if (paragraph_value(node, "pStyle") != style
                        or paragraph_value(body[index + 1], "pStyle") != style + "Label"):
                    raise ValueError("highlight treatment differs from the brief")
            if name in figures:
                if "side_text" in figures[name]:
                    raise ValueError("missing text-and-figure composition")
                slots[name] = (node, body[index + 1])
    if slots.keys() != figures.keys():
        raise ValueError("missing figure slot")
    if observed_sidebars != sidebars.keys():
        raise ValueError("missing metadata sidebar")
    if "illustration" in cover:
        index = 1 if cover.get("image_position") == "before-title" else 3 + ("subtitle" in spec)
        figures["cover"] = cover["illustration"]
        if len(body[index:index + 2]) != 2:
            raise ValueError("missing illustrated cover slot")
        slots["cover"] = body[index:index + 2]
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
