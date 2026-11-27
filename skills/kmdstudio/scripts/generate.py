"""Build and verify an editable DOCX from a bounded JSON brief."""

import argparse
import sys
import xml.etree.ElementTree as ET
from zipfile import BadZipFile

from guard import confined, publish_new, read_json, verified_assets, workspace
from layout import WordLayout
from review_docx import check_docx
from spec import validate_spec


def build_document(brief):
    assets = verified_assets()
    spec = read_json(brief)
    design = validate_spec(spec, assets)
    result = WordLayout(spec, assets, design).build()
    check_docx(result, assets, spec=spec)
    return spec, result


def parser(description):
    args = argparse.ArgumentParser(description=description)
    args.add_argument("--root", required=True, help="absolute, approved local workspace")
    args.add_argument("--spec", required=True, help="relative UTF-8 JSON brief")
    args.add_argument("--output", required=True, help="new relative output file")
    return args


def cli_paths(args, suffix):
    root = workspace(args.root)
    return confined(root, args.spec, ".json"), confined(root, args.output, suffix, new=True)


def main():
    args = parser(__doc__).parse_args()
    try:
        brief, output = cli_paths(args, ".docx")
        spec, document = build_document(brief)
        if "docx" not in spec["formats"]:
            raise ValueError("the brief does not request DOCX")
        publish_new(output, document)
    except (ValueError, OSError, ET.ParseError, BadZipFile) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    print("PASS: DOCX structure and editable content verified. Visual review is separate.")
    if "pdf" in spec["formats"]:
        print("PDF export uses the separate render_pdf.py command.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
