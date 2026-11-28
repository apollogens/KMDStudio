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

NETWORK = BENCHMARKS / "networking"


class CompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        manifest = NETWORK / "assets/manifest.json"
        art = verified_rasters(ROOT, manifest.relative_to(ROOT).as_posix(),
                               sha256(manifest.read_bytes()))
        cls.spec, cls.output = build_document(NETWORK / "networking.json", illustrations=art)
        cls.assets = verified_assets() | art
        cls.parts = read_archive(cls.output)

    def test_native_columns_figures_and_continuous_reading_order(self):
        doc = check_docx(self.output, self.assets, spec=self.spec)
        body = doc.find(q("w:body"))
        sections = list(doc.iter(q("w:sectPr")))
        self.assertEqual([section.find(q("w:cols")) is not None for section in sections],
                         [False, True, False])
        self.assertEqual([section.find(q("w:type")).get(q("w:val")) for section in sections],
                         ["continuous"] * 3)
        captions = [block["caption"] for block in self.spec["blocks"] if block["kind"] == "figure"]
        self.assertEqual(len(captions), 1)
        table = body.find(q("w:tbl"))
        figure = next(block for block in self.spec["blocks"] if block["kind"] == "figure")
        self.assertEqual(text_paragraphs(table), [figure["side_text"], figure["caption"]])
        self.assertEqual(len(list(table.iter(q("w:tblHeader")))), 0)
        first_heading = next(node for node in body if node.find(q("w:bookmarkStart")) is not None
                             and node.find(q("w:bookmarkStart")).get(q("w:name")) == "kmd_overview")
        before_heading = list(body)[:list(body).index(first_heading)]
        self.assertEqual(sum(1 for node in before_heading for _ in node.iter(q("w:drawing"))), 1)
        self.assertIn(next(block["text"] for block in self.spec["blocks"]
                           if block["id"] == "offline-code"), text_paragraphs(doc))

    def test_invalid_placement_and_fit_options(self):
        for key, change in (
            ("unknown boundary", lambda d: d["layout"]["columns"][0].update({"from": "missing"})),
            ("reversed range", lambda d: d["layout"]["columns"][0].update({"from": "roles"})),
            ("wide component in columns",
             lambda d: d["layout"]["columns"][0].update({"through": "exchange"})),
            ("split heading",
             lambda d: d["layout"]["columns"][0].update({"from": "address"})),
            ("oversize inset",
             lambda d: next(b for b in d["blocks"] if b["id"] == "exchange").update(width_mm=75)),
            ("ambiguous cover", lambda d: d["blocks"][0].update(icon="arrow-right")),
            ("oversize kept table",
             lambda d: next(b for b in d["blocks"] if b["id"] == "protocol-table").update(keep_rows=True)),
        ):
            spec = copy.deepcopy(self.spec)
            change(spec)
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_spec(spec, self.assets)

    def test_layout_mutations_rejected(self):
        part = "word/document.xml"
        for source, replacement, message in (
            (b'w:num="2"', b'w:num="3"', "two-column geometry"),
            (b'w:val="continuous"', b'w:val="nextPage"', "continuous section"),
            (b"<w:cantSplit />", b"", "text-and-figure"),
            (b'w:w="3764"', b'w:w="3765"', "text-and-figure"),
            (b"<w:keepLines />", b"", "paragraph flow"),
        ):
            modified = self.parts[part].replace(source, replacement, 1)
            self.assertNotEqual(modified, self.parts[part])
            damaged = rewrite_package(self.output, {part: modified})
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                check_docx(damaged, self.assets, spec=self.spec)

    def test_numbering_instances_restart_in_word(self):
        part = "word/numbering.xml"
        numbering = parse_xml(self.parts[part])
        starts = list(numbering.iter(q("w:startOverride")))
        self.assertEqual([node.get(q("w:val")) for node in starts], ["1"] * 5)
        starts[0].set(q("w:val"), "3")
        damaged = rewrite_package(self.output, {part: ET.tostring(numbering)})
        with self.assertRaisesRegex(ValueError, "restart"):
            check_docx(damaged, self.assets, spec=self.spec)

    def test_multiple_regions_and_final_columns_keep_the_running_parts(self):
        spec = copy.deepcopy(self.spec)
        spec["design"]["header"] = "Running header"
        spec["blocks"] = [{"id": name, "kind": "paragraph", "text": name}
                          for name in ("alpha", "beta", "wide", "gamma", "delta")]
        spec["acceptance"]["required_ids"] = [block["id"] for block in spec["blocks"]]
        spec["layout"]["columns"] = [{"from": "alpha", "through": "beta"},
                                      {"from": "gamma", "through": "delta"}]
        design = validate_spec(spec, self.assets)
        doc = check_docx(WordLayout(spec, self.assets, design).build(), self.assets, spec=spec)
        sections = list(doc.iter(q("w:sectPr")))
        self.assertEqual([section.find(q("w:cols")) is not None for section in sections],
                         [False, True, False, True])
        self.assertEqual(len(list(doc.iter(q("w:headerReference")))), 4)
        self.assertEqual(text_paragraphs(doc)[-5:], spec["acceptance"]["required_ids"])
