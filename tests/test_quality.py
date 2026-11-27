import copy
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from test_kmdstudio import BENCHMARKS, ROOT, rewrite_package

# isort: split
from generate import build_document
from guard import parse_xml, read_json, sha256, verified_assets
from ooxml import q
from raster import verified_rasters
from review_docx import check_docx, read_archive
from review_quality import verify_record
from spec import validate_spec

QUALITY = BENCHMARKS / "quality"


class DataBarTests(unittest.TestCase):
    def setUp(self):
        self.spec, self.content = build_document(QUALITY / "objects-under-glass.json")
        self.assets = verified_assets()

    def test_editable_values_and_zero_based_widths(self):
        document = check_docx(self.content, self.assets, spec=self.spec)
        _, table = list(document.iter(q("w:tbl")))
        rows = table.findall(q("w:tr"))
        cells = [row.findall(q("w:tc"))[-1] for row in rows]
        self.assertEqual([next(cell.iter(q("w:t"))).text for cell in cells],
                         ["Hours", "8", "6", "4", "0", "0"])
        width = int(cells[1][0][0].get(q("w:w"))) - 160
        inset = [int(cell[2].find(f"{q('w:pPr')}/{q('w:ind')}").get(q("w:right")))
                 for cell in cells[1:4]]
        self.assertEqual([width - value for value in inset], [width, width * 3 // 4, width // 2])
        self.assertFalse(any(len(cell) > 2 for cell in [cells[0], *cells[4:]]))

    def test_invalid_series_and_wrong_proportion(self):
        table = self.spec["blocks"][2]
        invalid = (table["bars"] | {"column": 4}, table["bars"] | {"through": 6})
        for bars in invalid:
            broken = copy.deepcopy(self.spec)
            broken["blocks"][2]["bars"] = bars
            with self.assertRaisesRegex(ValueError, "table bounds"):
                validate_spec(broken, self.assets)
        table["rows"][0][2] = "1.5"
        with self.assertRaisesRegex(ValueError, "nonnegative integers"):
            validate_spec(self.spec, self.assets)
        table["rows"][0][2] = "8"
        part = "word/document.xml"
        doc = parse_xml(read_archive(self.content)[part])
        last_column = list(doc.iter(q("w:tbl")))[1].findall(q("w:tr"))[1].findall(q("w:tc"))[-1]
        next(last_column[2].iter(q("w:ind"))).set(q("w:right"), "12")
        with self.assertRaisesRegex(ValueError, "bar proportions"):
            check_docx(rewrite_package(self.content, {part: ET.tostring(doc)}), self.assets, spec=self.spec)

    def test_running_cover_and_original_art(self):
        manifest = BENCHMARKS / "creative/assets/manifest.json"
        assets = verified_rasters(ROOT, manifest.relative_to(ROOT).as_posix(), sha256(manifest.read_bytes()))
        brief, content = build_document(QUALITY / "relational-databases-refined.json", illustrations=assets)
        self.assertEqual(brief["blocks"][0]["flow"], "continue")
        doc = check_docx(content, self.assets | assets, spec=brief)
        self.assertFalse(any(node.get(q("w:type")) == "page" for node in doc.iter(q("w:br"))))
        original = read_archive((ROOT / "artifacts/v0.5.0rc1/relational-databases.docx").read_bytes())
        self.assertEqual(read_archive(content)["word/media/image1.png"], original["word/media/image1.png"])

    def test_unplanned_heading_break_is_rejected(self):
        brief, content = build_document(QUALITY / "saturday-handover-refined.json")
        part = "word/document.xml"
        document = parse_xml(read_archive(content)[part])
        heading = next(p for p in document.iter(q("w:p")) if any(
            node.get(q("w:name")) == "kmd_sequence" for node in p.findall(q("w:bookmarkStart"))))
        ET.SubElement(heading[0], q("w:pageBreakBefore"))
        with self.assertRaisesRegex(ValueError, "heading page break"):
            check_docx(rewrite_package(content, {part: ET.tostring(document)}), self.assets, spec=brief)


class QualityRecordTests(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name).resolve()
        self.record = {
            "version": 1, "scope": "layout-only", "outcome": "pass",
            "stages": [self.stage("saturday-handover-initial", 2), self.stage("saturday-handover-refined", 1)],
            "findings": [{"id": "stranded-schedule", "block": "sequence", "page": 2,
                          "category": "visual", "severity": "major", "evidence": "Schedule is isolated.",
                          "correction": "Remove the explicit page break.", "method": "render",
                          "status": "resolved", "observed": 0, "resolved": 1, "result": "Together on page 1."}],
        }

    def stage(self, name, pages, spec=None):
        source = self.root / (name + ".json")
        source.write_bytes((QUALITY / (name + ".json")).read_bytes() if spec is None else
                           json.dumps(spec).encode("utf-8"))
        _, content = build_document(source)
        result = source.with_suffix(".docx")
        result.write_bytes(content)
        return {"brief": {"path": source.name, "sha256": sha256(source.read_bytes())},
                "docx": {"path": result.name, "sha256": sha256(content)}, "render": "inspected",
                "renderer": "Writer", "page_count": pages, "change": name}

    def test_provenance_and_visible_resolution(self):
        verify_record(self.record, self.root)
        for change, message in (
            (lambda r: r["stages"][0]["brief"].update(sha256="0" * 64), "digest"),
            (lambda r: r["findings"][0].update(block="wrong"), "unknown content block"),
            (lambda r: r["findings"][0].update(resolved=2), "subsequent stage"),
            (lambda r: r["stages"][0].update(render="pending"), "render inspection"),
            (lambda r: r["stages"].extend(r["stages"] * 2), "array size"),
        ):
            record = copy.deepcopy(self.record)
            change(record)
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                verify_record(record, self.root)

    def test_layout_revision_cannot_change_native_text(self):
        spec = read_json(QUALITY / "saturday-handover-refined.json")
        spec["blocks"][2]["rows"][0][0] = "09:00"
        self.record["stages"][1] = self.stage("silent-data-edit", 1, spec)
        with self.assertRaisesRegex(ValueError, "changed native text"):
            verify_record(self.record, self.root)

    def test_mandatory_finding_blocks_delivery(self):
        finding = self.record["findings"][0]
        finding.update(category="security", status="open")
        del finding["resolved"]
        with self.assertRaisesRegex(ValueError, "block delivery"):
            verify_record(self.record, self.root)
        self.record["outcome"] = "blocked"
        verify_record(self.record, self.root)
