"""Build and verify an editable DOCX from a bounded JSON brief."""

import argparse
import sys
import xml.etree.ElementTree as ET
from zipfile import BadZipFile

from guard import confined, publish_new, read_json, verified_assets, workspace
from layout import WordLayout
from raster import verified_rasters
from review_docx import check_docx
from spec import validate_spec


def build_document(brief, *, illustrations=None):
    assets = verified_assets()
    if illustrations:
        assets.update(illustrations)
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
    args.add_argument("--asset-manifest", help="relative reviewed illustration manifest")
    args.add_argument("--asset-manifest-sha256", help="trusted SHA-256 of that manifest")
    return args


def cli_paths(args, suffix):
    root = workspace(args.root)
    if (args.asset_manifest is None) != (args.asset_manifest_sha256 is None):
        raise ValueError("both illustration manifest options are required together")
    brief = confined(root, args.spec, ".json")
    output = confined(root, args.output, suffix, new=True)
    illustrations = (None if args.asset_manifest is None else
                     verified_rasters(root, args.asset_manifest, args.asset_manifest_sha256))
    return brief, output, illustrations


def main():
    args = parser(__doc__).parse_args()
    try:
        brief, output, illustrations = cli_paths(args, ".docx")
        spec, document = build_document(brief, illustrations=illustrations)
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
