import json
import re
import unittest
import xml.etree.ElementTree as ET

from test_kmdstudio import BUSINESS, SKILL, rewrite_package

# isort: split
from generate import build_document
from guard import verified_assets
from layout import WordLayout
from ooxml import q
from review_docx import check_docx, read_archive
from spec import validate_spec


class DesignKnowledgeTests(unittest.TestCase):
    def test_card_routes_are_local_and_creative_material_is_on_demand(self):
        references = SKILL / "references"
        entry = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("For creative or hybrid work", entry)
        for name in ("composition.md", "design-examples.md", "DESIGN-RESEARCH-v0.7.0.md"):
            self.assertNotIn(name, entry)
            self.assertNotIn(name, (references / "design.md").read_text(encoding="utf-8"))

        direction = (references / "creative.md").read_text(encoding="utf-8")
        links = re.findall(r"\]\(([^)#]+)(?:#([^)]+))?\)", direction)
        targets = {path: (references / path).read_text(encoding="utf-8") for path, _ in links}
        for path, anchor in links:
            if anchor:
                headings = re.findall(r"^## (.+)$", targets[path], re.M)
                self.assertIn(anchor, {heading.lower().replace(" ", "-") for heading in headings})
        cards = [card for text in targets.values() for card in re.findall(r"^\| (D\d{2})\b", text, re.M)]
        self.assertCountEqual(cards, [f"D{number:02d}" for number in range(1, 16)])

    def test_example_fragments_generate_editable_documents(self):
        spec, _ = build_document(BUSINESS)
        assets = verified_assets()
        examples = (SKILL / "references/design-examples.md").read_text(encoding="utf-8")
        fragments = [json.loads(payload) for payload in re.findall(r"```json\n(.+?)\n```", examples, re.S)]
        self.assertEqual({block["kind"] for block in fragments}, {"table", "sidebar", "diagram"})
        for block in fragments:
            with self.subTest(block=block["id"]):
                brief = spec | {"mode": "hybrid", "design": {"profile": "swiss-minimal"},
                                "blocks": [block], "acceptance": {
                                    "required_ids": [block["id"]], "criteria": ["Native content."]}}
                design = validate_spec(brief, assets)
                check_docx(WordLayout(brief, assets, design).build(), assets, spec=brief)


class WordCompatibilityTests(unittest.TestCase):
    def test_modern_mode_is_explicit_and_only_adds_the_bounded_settings(self):
        classic_spec, classic = build_document(BUSINESS)
        assets = verified_assets()
        spec = classic_spec | {"word_compatibility": "modern"}
        modern = WordLayout(spec, assets, validate_spec(spec, assets)).build()
        legacy_parts, modern_parts = read_archive(classic), read_archive(modern)
        part = "word/settings.xml"
        self.assertEqual(set(modern_parts) - set(legacy_parts), {part})
        self.assertEqual({name for name in legacy_parts if legacy_parts[name] != modern_parts[name]},
                         {"[Content_Types].xml", "word/_rels/document.xml.rels"})
        check_docx(modern, assets, spec=spec)
        with self.assertRaisesRegex(ValueError, "compatibility differs"):
            check_docx(classic, assets, spec=spec)
        with self.assertRaisesRegex(ValueError, "compatibility differs"):
            check_docx(modern, assets, spec=classic_spec)
        with self.assertRaises(ValueError):
            validate_spec(spec | {"word_compatibility": "12"}, assets)

        for tag, key, value in (("w:compatSetting", "w:val", "14"),
                                 ("w:compatSetting", "w:uri", "https://example.com"),
                                 ("w:settings", "w:default", "1")):
            with self.subTest(tag=tag, key=key):
                root = ET.fromstring(modern_parts[part])
                next(root.iter(q(tag))).set(q(key), value)
                with self.assertRaisesRegex(ValueError, "unexpected Word settings"):
                    check_docx(rewrite_package(modern, {part: ET.tostring(root)}), assets)
        root = ET.fromstring(modern_parts[part])
        ET.SubElement(root, q("w:updateFields"), {q("w:val"): "true"})
        with self.assertRaisesRegex(ValueError, "unexpected Word settings"):
            check_docx(rewrite_package(modern, {part: ET.tostring(root)}), assets)
