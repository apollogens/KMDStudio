import copy
import unittest
import xml.etree.ElementTree as ET

from test_kmdstudio import BENCHMARKS, ROOT, rewrite_package

# isort: split
from generate import build_document
from guard import parse_xml, sha256, verified_assets
from layout import WordLayout
from ooxml import q
from raster import verified_rasters
from review_docx import check_docx, read_archive, text_paragraphs
from spec import validate_spec

CREATIVE = BENCHMARKS / "creative"


class CreativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        manifest = CREATIVE / "assets/manifest.json"
        cls.art = verified_rasters(ROOT, manifest.relative_to(ROOT).as_posix(),
                                   sha256(manifest.read_bytes()))
        cls.assets = verified_assets() | cls.art
        cls.spec, cls.output = build_document(CREATIVE / "cooler-route-editorial.json",
                                              illustrations=cls.art)
        cls.parts = read_archive(cls.output)

    def test_modes_and_explicit_structured_compatibility(self):
        spec, previous = build_document(ROOT / "examples/workshop-status.json")
        spec["mode"] = "structured"
        self.assertEqual(WordLayout(spec, self.assets, validate_spec(spec, self.assets)).build(),
                         previous)
        for mode, message in (("auto", "resolve auto"), ("unknown", "unsupported value"),
                              ("creative", "require KDL"), ("hybrid", "require KDL")):
            spec["mode"] = mode
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, message):
                validate_spec(spec, self.assets)
        for mode in ("creative", "hybrid"):
            design = validate_spec(self.spec | {"mode": mode}, self.assets)
            self.assertEqual(design["typography"]["display_pt"], 62)

    def test_font_fallback_and_declared_face(self):
        brief = CREATIVE / "relational-databases.json"
        spec, fallback = build_document(brief, illustrations=self.art)
        _, declared = build_document(brief, illustrations=self.art, available_fonts=["Literata"])
        self.assertEqual(validate_spec(spec, self.assets)["typography"]["display_font"], "Georgia")
        for contents, font in ((fallback, "Georgia"), (declared, "Literata")):
            styles = parse_xml(read_archive(contents)["word/styles.xml"])
            cover = next(s for s in styles if s.get(q("w:styleId")) == "CoverTitle")
            self.assertEqual(cover.find(f"{q('w:rPr')}/{q('w:rFonts')}").get(q("w:ascii")), font)
        with self.assertRaisesRegex(ValueError, "editorial style"):
            check_docx(declared, self.assets, spec=spec)

    def test_native_layout_and_exact_hybrid_content(self):
        doc = check_docx(self.output, self.assets, spec=self.spec)
        body = doc.find(q("w:body"))
        data, sidebar, figure = body.findall(q("w:tbl"))
        self.assertEqual([node.get(q("w:val")) for node in data.iter(q("w:jc"))][:4],
                         ["left", "right", "right", "right"])
        for table, percent in ((sidebar, 70), (figure, 61)):
            left, right = [int(col.get(q("w:w"))) for col in table.find(q("w:tblGrid"))]
            self.assertEqual(right, (left + right) * percent // 100)
        self.assertEqual(body[list(body).index(sidebar) + 1].tag, q("w:p"))
        self.assertIn("Free seating", text_paragraphs(sidebar))

        lesson, contents = build_document(CREATIVE / "relational-databases.json",
                                          illustrations=self.art)
        native = check_docx(contents, self.assets, spec=lesson)
        text = text_paragraphs(native)
        self.assertLess(text.index(lesson["blocks"][0]["illustration"]["caption"]),
                        text.index(lesson["title"]))
        self.assertIn(next(b["text"] for b in lesson["blocks"] if b["kind"] == "code"), text)
        self.assertEqual(len(list(native.iter(q("w:tblHeader")))), 3)

    def test_invalid_editorial_briefs(self):
        for mutation in (
            lambda s: s.update(mode="structured"),
            lambda s: s["design"]["tokens"]["typography"].update(display_pt=73),
            lambda s: s["design"]["tokens"]["typography"].update(display_tracking_twips=-25),
            lambda s: s["design"]["tokens"]["typography"].update(display_font="Arial Black",
                                                                  display_weight="bold"),
            lambda s: s["blocks"][1].update(level=2),
            lambda s: s["blocks"][4].update(column_alignments=["left", "right"]),
            lambda s: s["blocks"][-2].update(sidebar_percent=41),
            lambda s: s["blocks"][-2]["items"][0].update(value="two\nlines"),
            lambda s: s["blocks"][-1].update(image_percent=30),
            lambda s: s["blocks"][-1].pop("side_text"),
            lambda s: s.update(layout={"columns": [{"from": "scope", "through": "shade-study"}]}),
        ):
            spec = copy.deepcopy(self.spec)
            mutation(spec)
            with self.subTest(spec=spec), self.assertRaises(ValueError):
                validate_spec(spec, self.assets)

    def test_output_mutations_are_rejected(self):
        def changed_alignment(document):
            table = next(document.iter(q("w:tbl")))
            next(table.iter(q("w:jc"))).set(q("w:val"), "right")

        def removes_separator(document):
            body = document.find(q("w:body"))
            sidebar = body.findall(q("w:tbl"))[1]
            body.remove(body[list(body).index(sidebar) + 1])

        def moves_tracking(document):
            node = next(document.iter(q("w:jc")))
            node.tag = q("w:spacing")
            node.set(q("w:val"), "12")

        part = "word/document.xml"
        for mutation, message in ((changed_alignment, "column alignment"),
                                  (removes_separator, "separating paragraph"),
                                  (moves_tracking, "character spacing")):
            document = parse_xml(self.parts[part])
            mutation(document)
            contents = rewrite_package(self.output, {part: ET.tostring(document)})
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                check_docx(contents, self.assets, spec=self.spec)
