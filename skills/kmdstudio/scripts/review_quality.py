"""Verify a bounded review record and its local brief and DOCX references."""

import argparse
import sys
import xml.etree.ElementTree as ET
from zipfile import BadZipFile

from guard import (
    DOCX_LIMIT,
    JSON_LIMIT,
    PACKAGE,
    bounded_read,
    confined,
    parse_json,
    parse_xml,
    read_json,
    sha256,
    workspace,
)
from ooxml import q
from review_docx import check_content, read_archive, text_paragraphs
from spec import validate_shape

MANDATORY = {"fidelity", "structure", "security", "editability"}


def read_reference(root, reference, suffix, limit):
    data = bounded_read(confined(root, reference["path"], suffix), limit)
    if sha256(data) != reference["sha256"]:
        raise ValueError("stage file differs from its recorded digest")
    return data


def check_findings(record, briefs):
    stages = record["stages"]
    seen = set()
    for finding in record["findings"]:
        identity, start, status = (finding[key] for key in ("id", "observed", "status"))
        if identity in seen or start >= len(stages) or not {"page", "block"} & finding.keys():
            raise ValueError("finding requires a unique ID and a location in a retained stage")
        seen.add(identity)
        if "block" in finding and finding["block"] not in {block["id"] for block in briefs[start]["blocks"]}:
            raise ValueError("finding refers to an unknown content block")
        if "page" in finding and finding["page"] > stages[start].get("page_count", 100):
            raise ValueError("finding refers to an unknown rendered page")
        end = finding.get("resolved")
        if status == "resolved":
            if end is None or not start < end < len(stages) or "result" not in finding:
                raise ValueError("resolved findings require a subsequent stage and an observed result")
            if finding["method"] in {"render", "human"} and any(
                    stages[index]["render"] != "inspected" for index in (start, end)):
                raise ValueError("visually resolved findings require inspected before and after stages")
        elif end is not None or (status == "accepted" and (
                finding["category"] != "art-direction" or finding["severity"] != "observation"
                or "result" not in finding)):
            raise ValueError("acceptance applies only to documented artistic observations")
        if status == "open" and (finding["category"] in MANDATORY or finding["severity"] == "blocker"):
            if record["outcome"] != "blocked":
                raise ValueError("unresolved mandatory findings block delivery")
        elif status == "open" and finding["severity"] == "major" and record["outcome"] == "pass":
            raise ValueError("an unresolved major finding prevents a passing result")


def verify_record(record, root):
    schema = read_json(confined(PACKAGE, "schemas/quality.schema.json", ".json", package=True))
    validate_shape(record, schema, schema["$defs"])
    briefs, seen_docx = [], set()
    initial = None
    for stage in record["stages"]:
        inspected = stage["render"] == "inspected"
        if inspected != ("renderer" in stage) or inspected != ("page_count" in stage):
            raise ValueError("render inspection requires an application and page count")
        brief = parse_json(read_reference(root, stage["brief"], ".json", JSON_LIMIT))
        digest = stage["docx"]["sha256"]
        if digest in seen_docx:
            raise ValueError("a correction must retain a distinct DOCX result")
        seen_docx.add(digest)
        parts = read_archive(read_reference(root, stage["docx"], ".docx", DOCX_LIMIT))
        document = parse_xml(parts["word/document.xml"])
        check_content(document, brief)
        briefs.append(brief)
        if record["scope"] == "layout-only":
            signature = (text_paragraphs(document, arrows=True),
                         [node.get("descr") for node in document.iter(q("wp:docPr"))],
                         {key: sha256(data) for key, data in parts.items() if key.startswith("word/media/")})
            if initial is not None and signature != initial:
                raise ValueError("layout-only correction changed native text, descriptions or images")
            initial = signature
    check_findings(record, briefs)
    if record["outcome"] == "pass" and record["stages"][-1]["render"] != "inspected":
        raise ValueError("a passing quality record requires a final inspected render")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--record", required=True, help="relative JSON quality record")
    args = parser.parse_args()
    try:
        root = workspace(args.root)
        record = read_json(confined(root, args.record, ".json"))
        verify_record(record, root)
    except (ValueError, OSError, KeyError, IndexError, TypeError, ET.ParseError, BadZipFile) as exc:
        print(f"BLOCKED: invalid quality record: {exc}", file=sys.stderr)
        return 2
    print(f"Quality record verified ({len(record['stages']) - 1} correction cycles, "
          f"{len(record['findings'])} findings). Recorded outcome: {record['outcome']}.")
    return 2 if record["outcome"] == "blocked" else 0


if __name__ == "__main__":
    sys.exit(main())
