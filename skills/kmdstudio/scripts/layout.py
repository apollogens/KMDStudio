"""Editable Word components for the bounded document brief."""

import io
import keyword
import re
import tokenize
import xml.etree.ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from guard import check_png
from ooxml import MAIN_RELS, ROOT_RELS, R, content_types, element, relationships, val, w
from raster import RASTER_EDGE

SYNTAX_ROLES = {
    tokenize.STRING: "syntax_string", tokenize.NUMBER: "syntax_number",
    tokenize.COMMENT: "syntax_comment", tokenize.OP: "syntax_operator",
}
CALLOUT_COLORS = {
    "definition": "accent", "info": "info", "success": "success", "warning": "warning",
    "takeaway": "primary",
}
PARAGRAPH_STYLES = {"lead": "Lead", "note": "Note", "emphasis": "Emphasis"}


def twips(mm):
    return round(mm * 1440 / 25.4)


def run(paragraph, text, *, bold=False, color=None):
    item = w("r", paragraph)
    if bold or color:
        props = w("rPr", item)
        if bold:
            w("b", props)
        if color:
            val("color", props, color)
    for piece in re.split(r"([\n\t])", text):
        if piece == "\n":
            w("br", item)
        elif piece == "\t":
            w("tab", item)
        elif piece:
            element("w:t", item, piece, xml_space="preserve")
    return item


def paragraph(parent, style="Normal", text=None, *, new_page=False, number=None,
              keep=False, align=None, before=None, rule=None):
    node = w("p", parent)
    props = w("pPr", node)
    val("pStyle", props, style)
    if keep:
        w("keepNext", props)
    if new_page:
        w("pageBreakBefore", props)
    if number is not None:
        num = w("numPr", props)
        val("ilvl", num, 0)
        val("numId", num, number)
    if rule:
        w("bottom", w("pBdr", props), val="single", sz=12, space=5, color=rule)
    if before is not None:
        w("spacing", props, before=before * 20)
    if align:
        val("jc", props, align)
    if text is not None:
        run(node, text)
    return node


def highlighted(text):
    offsets = [0]
    for line in text.split("\n"):
        offsets.append(offsets[-1] + len(line) + 1)
    cursor = 0
    try:
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            role = SYNTAX_ROLES.get(token.type)
            if token.type == tokenize.NAME and keyword.iskeyword(token.string):
                role = "syntax_keyword"
            if role:
                start = offsets[token.start[0] - 1] + token.start[1]
                end = offsets[token.end[0] - 1] + token.end[1]
                if cursor < start:
                    yield text[cursor:start], None
                yield text[start:end], role
                cursor = end
    except (tokenize.TokenError, IndentationError):
        pass
    if cursor < len(text):
        yield text[cursor:], None


class WordLayout:
    def __init__(self, spec, assets, design):
        self.spec = spec
        self.assets = assets
        self.design = design
        self.colors = design["colors"]
        self.type = design["typography"]
        self.spacing = design["spacing"]
        self.margin = twips(self.spacing["margin_mm"])
        self.width = twips(210) - 2 * self.margin
        self.media = {}
        self.images = 0
        self.numberings = []
        self.document = w("document")
        if self.colors["background"] != "FFFFFF":
            w("background", self.document, color=self.colors["background"])
        self.body = w("body", self.document)

    def style(self, root, identity, label, *, size, font, color, before=0, after=0,
              bold=False, keep=False, fill=None, outline=None, line=None,
              inset=None, rule=None):
        style = w("style", root, type="paragraph", styleId=identity,
                  **({"default": 1} if identity == "Normal" else {}))
        val("name", style, label)
        if identity != "Normal":
            val("next", style, "Normal")
        if identity in {"Title", "Subtitle", "Normal", "Heading1", "Heading2"}:
            w("qFormat", style)
        props = w("pPr", style)
        if keep:
            w("keepNext", props)
            w("keepLines", props)
        w("widowControl", props)
        if rule is not None or fill:
            borders = w("pBdr", props)
            if rule is not None:
                edge, color_role = rule
                w(edge, borders, val="single", sz=12, space=9 if fill else 6,
                  color=self.colors[color_role])
            else:
                w("left", borders, val="single", sz=4, space=9, color=fill)
        if fill:
            w("shd", props, val="clear", color="auto", fill=fill)
        w("spacing", props, before=round(before * 20), after=round(after * 20),
          line=round((line or self.type["body_line_percent"]) * 2.4), lineRule="auto")
        if inset:
            w("ind", props, left=inset, right=inset)
        if outline is not None:
            val("outlineLvl", props, outline)
        text_style = w("rPr", style)
        w("rFonts", text_style, ascii=font, hAnsi=font, eastAsia=font, cs=font)
        if bold:
            w("b", text_style)
        val("color", text_style, color)
        val("sz", text_style, size * 2)
        val("szCs", text_style, size * 2)
        val("lang", text_style, self.spec["language"])

    def styles(self):
        root = w("styles")
        defaults = w("docDefaults", root)
        default_text = w("rPr", w("rPrDefault", defaults))
        val("lang", default_text, self.spec["language"])
        gap, para = self.spacing["component_pt"], self.spacing["paragraph_pt"]
        tint = self.colors["surface"]

        def role(identity, label, family, color, **formatting):
            font = {"display": "heading", "subheading": "body", "code": "monospace"}.get(
                family, family,
            )
            settings = {
                "size": self.type[family + "_pt"], "font": self.type[font + "_font"],
                "color": self.colors[color], "bold": self.type[family + "_weight"] == "bold",
            }
            self.style(root, identity, label, **(settings | formatting))

        role("Normal", "Normal", "body", "text", after=para)
        role("Title", "Title", "display", "primary", after=gap, keep=True,
             line=self.type["display_line_percent"])
        role("Subtitle", "Subtitle", "subheading", "secondary", bold=False, after=gap * 2)
        role("Heading1", "heading 1", "heading", "primary", before=gap + 5, after=para,
             keep=True, outline=0, line=self.type["heading_line_percent"])
        role("Heading2", "heading 2", "subheading", "accent", before=gap, after=para // 2,
             keep=True, outline=1, line=self.type["heading_line_percent"])

        cover = self.design["composition"]["cover"]
        label_rule = ("bottom", "accent") if cover in {"panel", "rule"} else None
        panel = {"fill": self.colors["primary"], "inset": 320} if cover == "panel" else {}
        cover_text = "on_primary" if panel else "primary"
        role("CoverLabel", "Cover label", "caption", "accent", before=gap * 4, after=gap * 2,
             bold=True, keep=True, rule=label_rule)
        role("CoverTitle", "Cover title", "display", cover_text, before=gap, after=gap,
             keep=True, line=self.type["display_line_percent"], **panel)
        role("CoverSubtitle", "Cover subtitle", "subheading", cover_text, bold=False,
             after=gap, keep=True, line=140, **panel)
        role("CoverLead", "Cover introduction", "body", "text", before=gap * 2,
             after=gap, size=self.type["body_pt"] + 2)
        role("CoverMark", "Cover illustration", "caption", "accent", after=gap, keep=True)

        role("Caption", "Caption", "caption", "muted", after=para)
        role("Lead", "Lead paragraph", "body", "secondary", after=gap,
             size=self.type["body_pt"] + 2)
        role("Note", "Note", "caption", "muted", after=para)
        role("Emphasis", "Emphasis paragraph", "body", "primary", bold=True, after=para)
        role("ListParagraph", "List Paragraph", "body", "text", after=para // 2 + 1)
        for tone, color in CALLOUT_COLORS.items():
            style = "Callout" + tone.title()
            label = tone.capitalize() + " callout"
            panel = {"fill": tint, "inset": 230, "rule": ("left", color)}
            role(style + "Title", label + " title", "body", color, before=gap, after=2,
                 bold=True, keep=True, **panel)
            role(style + "Text", label + " text", "body", "text", after=gap, **panel)
        role("Code", "Code", "code", "code_text", before=2, after=gap,
             fill=self.colors["code_background"], line=self.type["code_line_percent"], inset=240)
        role("TableText", "Table text", "body", "text", after=0)
        role("TableHeader", "Table header", "body", "primary", bold=True, after=0)
        rule = ("left", "border")
        role("DiagramTitle", "Diagram step", "body", "accent", bold=True, keep=True, after=2,
             rule=rule, inset=230)
        role("DiagramText", "Diagram explanation", "body", "text", after=para // 2,
             rule=rule, inset=230)
        role("DiagramArrow", "Diagram arrow", "body", "accent", bold=True, before=1, after=2,
             keep=True, line=110)
        role("RunningText", "Running text", "caption", "muted")
        return root

    def add_list(self, items, kind):
        number = len(self.numberings) + 1
        self.numberings.append(kind)
        first = None
        for text in items:
            current = paragraph(self.body, "ListParagraph", text, number=number)
            if first is None:
                first = current
        return first

    def numbering(self):
        root = w("numbering")
        lists = (("bullet", "•"), ("decimal", "%1."), ("bullet", "□"))
        for index, (formatting, marker) in enumerate(lists):
            abstract = w("abstractNum", root, abstractNumId=index)
            val("multiLevelType", abstract, "singleLevel")
            level = w("lvl", abstract, ilvl=0)
            val("start", level, 1)
            val("numFmt", level, formatting)
            val("lvlText", level, marker)
            val("lvlJc", level, "left")
            props = w("pPr", level)
            w("tab", w("tabs", props), val="num", pos=400)
            w("ind", props, left=400, hanging=250)
        for index, kind in enumerate(self.numberings, 1):
            val("abstractNumId", w("num", root, numId=index), kind)
        return root

    def picture(self, parent, asset, description, mm):
        if asset not in self.media:
            self.media[asset] = len(self.media) + 1
        self.images += 1
        width, height = check_png(self.assets[asset], max_edge=RASTER_EDGE)
        cx, cy = mm * 36000, round(mm * 36000 * height / width)
        inline = element("wp:inline", w("drawing", w("r", parent)),
                         distT=0, distB=0, distL=0, distR=0)
        element("wp:extent", inline, cx=cx, cy=cy)
        element("wp:docPr", inline, id=self.images, name=asset, descr=description)
        frame = element("wp:cNvGraphicFramePr", inline)
        element("a:graphicFrameLocks", frame, noChangeAspect=1)
        graphic = element("a:graphic", inline)
        graphic_data = element("a:graphicData", graphic,
                               uri="http://schemas.openxmlformats.org/drawingml/2006/picture")
        picture = element("pic:pic", graphic_data)
        props = element("pic:nvPicPr", picture)
        element("pic:cNvPr", props, id=0, name=asset)
        element("pic:cNvPicPr", props)
        fill = element("pic:blipFill", picture)
        element("a:blip", fill, r_embed=f"rIdImage{self.media[asset]}")
        element("a:fillRect", element("a:stretch", fill))
        shape = element("pic:spPr", picture)
        transform = element("a:xfrm", shape)
        element("a:off", transform, x=0, y=0)
        element("a:ext", transform, cx=cx, cy=cy)
        element("a:avLst", element("a:prstGeom", shape, prst="rect"))

    def add_table(self, block):
        caption = block.get("caption")
        first = paragraph(self.body, "Caption", caption, keep=True) if caption else None
        table = w("tbl", self.body)
        props = w("tblPr", table)
        w("tblW", props, w=self.width, type="dxa")
        borders = w("tblBorders", props)
        comparison = block.get("presentation") == "comparison"
        edges = ("bottom", "insideH", "insideV") if comparison else ("bottom", "insideH")
        for edge in edges:
            w(edge, borders, val="single", sz=5, color=self.colors["border"])
        w("tblLayout", props, type="fixed")
        margins = w("tblCellMar", props)
        for edge in ("top", "left", "bottom", "right"):
            w(edge, margins, w=self.spacing["cell_pt"] * 20, type="dxa")
        grid = w("tblGrid", table)
        weights = block.get("column_weights", [1] * len(block["headers"]))
        widths = [self.width * weight // sum(weights) for weight in weights]
        widths[-1] += self.width - sum(widths)
        for width in widths:
            w("gridCol", grid, w=width)
        for index, row in enumerate([block["headers"], *block["rows"]]):
            line = w("tr", table)
            row_props = w("trPr", line)
            w("cantSplit", row_props)
            if index == 0:
                w("tblHeader", row_props)
            for text, width in zip(row, widths, strict=True):
                cell = w("tc", line)
                cell_props = w("tcPr", cell)
                w("tcW", cell_props, w=width, type="dxa")
                if index == 0:
                    w("shd", cell_props, val="clear", color="auto", fill=self.colors["surface"])
                style = "TableText" if index else "TableHeader"
                item = paragraph(cell, style, text, keep=index == 0)
                if first is None:
                    first = item
        return first

    def add_block(self, block, *, after_table=False):
        match block["kind"]:
            case "cover":
                label = paragraph(self.body, "CoverLabel", block["label"])
                if "icon" in block:
                    image = paragraph(self.body, "CoverMark")
                    self.picture(image, block["icon"], "", 27)
                self.title(cover=True)
                paragraph(self.body, "CoverLead", block["lead"])
                if "caption" in block:
                    paragraph(self.body, "Caption", block["caption"])
                if len(self.spec["blocks"]) > 1:
                    w("br", w("r", w("p", self.body)), type="page")
                return label
            case "heading":
                chapter = block.get("chapter", False)
                new_page = block.get("new_page", False)
                ruled = chapter or (block["level"] == 1 and self.design["composition"]["heading_rule"])
                before = self.spacing["component_pt"] * 2 if chapter else None
                return paragraph(
                    self.body, f"Heading{block['level']}", block["text"],
                    new_page=new_page, before=0 if new_page else before,
                    rule=self.colors["accent"] if ruled else None,
                )
            case "paragraph":
                before = self.spacing["component_pt"] if after_table else None
                style = PARAGRAPH_STYLES.get(block.get("role"), "Normal")
                return paragraph(self.body, style, block["text"], before=before)
            case "list":
                kind = 2 if block.get("checklist") else int(block["ordered"])
                return self.add_list(block["items"], kind)
            case "callout":
                style = "Callout" + block.get("tone", "definition").title()
                title = paragraph(self.body, style + "Title", block["title"])
                paragraph(self.body, style + "Text", block["text"])
                return title
            case "code":
                if "caption" in block:
                    first = paragraph(self.body, "Caption", block["caption"], keep=True)
                code = paragraph(self.body, "Code")
                if block["language"] == "python":
                    for text, role in highlighted(block["text"]):
                        run(code, text, color=self.colors[role] if role else None)
                else:
                    run(code, block["text"])
                return first if "caption" in block else code
            case "table":
                return self.add_table(block)
            case "diagram":
                caption = paragraph(self.body, "Caption", block["caption"], keep=True)
                for index, step in enumerate(block["steps"]):
                    if index:
                        paragraph(self.body, "DiagramArrow", "↓", align="center")
                    paragraph(self.body, "DiagramTitle", step["label"])
                    paragraph(self.body, "DiagramText", step["detail"])
                return caption
            case "figure":
                alignment = block.get("align", "center")
                plot = paragraph(self.body, "Normal", keep=True, align=alignment)
                self.picture(plot, block["asset"], block["alt"], block["width_mm"])
                paragraph(self.body, "Caption", block["caption"], align=alignment)
                return plot
            case "exercise":
                title = paragraph(self.body, "Heading2", block["title"])
                paragraph(self.body, "Normal", block["intro"], keep=True)
                self.add_list(block["steps"], 1)
                if "check" in block:
                    paragraph(self.body, "CalloutSuccessText", block["check"])
                return title
        raise ValueError("block has no layout component")

    def title(self, *, cover=False):
        paragraph(self.body, "CoverTitle" if cover else "Title", self.spec["title"])
        if "subtitle" in self.spec:
            paragraph(self.body, "CoverSubtitle" if cover else "Subtitle", self.spec["subtitle"])

    def build(self):
        if self.spec["blocks"][0]["kind"] != "cover":
            self.title()
        previous_kind = None
        for index, block in enumerate(self.spec["blocks"], 1):
            first = self.add_block(block, after_table=previous_kind == "table")
            start = w("bookmarkStart", id=index, name="kmd_" + block["id"].replace("-", "_"))
            first.insert(1, start)
            w("bookmarkEnd", first, id=index)
            previous_kind = block["kind"]
        section = w("sectPr", self.body)
        relationships_list = list(MAIN_RELS)
        design = self.spec["design"]
        header = design.get("header")
        if header:
            element("w:headerReference", section, w_type="default", r_id="rIdHeader")
            relationships_list.append(("rIdHeader", R + "/header", "header1.xml"))
        element("w:footerReference", section, w_type="default", r_id="rIdFooter")
        w("pgSz", section, w=twips(210), h=twips(297))
        w("pgMar", section, top=self.margin, right=self.margin, bottom=self.margin,
          left=self.margin, header=twips(9), footer=twips(9), gutter=0)
        footer = w("ftr")
        footer_p = paragraph(footer, "RunningText", align="right")
        if "footer" in design:
            run(footer_p, design["footer"] + "  ·  ")
        run(w("fldSimple", footer_p, instr="PAGE"), "1")
        core = element("cp:coreProperties")
        element("dc:title", core, self.spec["title"])
        element("dc:description", core, self.spec["purpose"])
        element("dc:language", core, self.spec["language"])
        images = {}
        for asset, index in self.media.items():
            name = f"media/image{index}.png"
            relationships_list.append((f"rIdImage{index}", R + "/image", name))
            images["word/" + name] = self.assets[asset]
        parts = {
            "[Content_Types].xml": content_types(bool(header), bool(images)),
            "_rels/.rels": relationships(ROOT_RELS),
            "word/_rels/document.xml.rels": relationships(relationships_list),
            "word/document.xml": self.document,
            "word/styles.xml": self.styles(),
            "word/numbering.xml": self.numbering(),
            "word/footer1.xml": footer,
            "docProps/core.xml": core,
        }
        if header:
            parts["word/header1.xml"] = w("hdr")
            paragraph(parts["word/header1.xml"], "RunningText", header)
        result = io.BytesIO()
        with ZipFile(result, "w", compression=ZIP_DEFLATED) as package:
            contents = {name: ET.tostring(node, encoding="utf-8") for name, node in parts.items()}
            for name, data in (contents | images).items():
                entry = ZipInfo(name)
                entry.create_system = 0
                package.writestr(entry, data, compress_type=ZIP_DEFLATED)
        return result.getvalue()
