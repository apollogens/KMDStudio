"""Validate the bundled schema subset and document-wide layout invariants."""

import re
import unicodedata

from design import resolve_design
from guard import PACKAGE, check_png, confined, read_json
from raster import RASTER_EDGE

COLUMN_GAP_MM = 8


def validate_shape(value, rule, definitions, path="$"):
    if "$ref" in rule:
        name = rule["$ref"].removeprefix("#/$defs/")
        return validate_shape(value, definitions[name], definitions, path)
    if "if" in rule:
        # The design formats are disjoint by presence of the profile key.
        branch = ("then" if isinstance(value, dict) and
                  set(rule["if"]["required"]) <= value.keys() else "else")
        return validate_shape(value, rule[branch], definitions, path)
    if "oneOf" in rule:
        # Every current union is a block type with a distinct kind.
        kind = value.get("kind") if isinstance(value, dict) else None
        if isinstance(kind, str) and {"$ref": "#/$defs/" + kind} in rule["oneOf"]:
            return validate_shape(value, definitions[kind], definitions, path)
        raise ValueError(f"{path}: unknown block kind")
    if "const" in rule:
        constant = rule["const"]
        if type(value) is not type(constant) or value != constant:
            raise ValueError(f"{path}: unexpected constant")
    if "enum" in rule and value not in rule["enum"]:
        raise ValueError(f"{path}: unsupported value")
    match rule.get("type"):
        case "object":
            fields = rule["properties"]
            if (not isinstance(value, dict) or value.keys() - fields.keys()
                    or set(rule.get("required", ())) - value.keys()):
                raise ValueError(f"{path}: required or unexpected properties")
            for key, item in value.items():
                validate_shape(item, fields[key], definitions, f"{path}.{key}")
        case "array":
            if not isinstance(value, list) or not rule["minItems"] <= len(value) <= rule["maxItems"]:
                raise ValueError(f"{path}: array size or type is invalid")
            for index, item in enumerate(value):
                validate_shape(item, rule["items"], definitions, f"{path}[{index}]")
            if rule.get("uniqueItems") and len(value) != len(set(value)):
                raise ValueError(f"{path}: values must be unique")
        case "string":
            if (not isinstance(value, str) or not rule["minLength"] <= len(value) <= rule["maxLength"]
                    or not value.strip() or not re.fullmatch(rule.get("pattern", r"[\s\S]*"), value)):
                raise ValueError(f"{path}: invalid text")
            check_text(value, path)
        case "integer":
            if type(value) is not int or not rule["minimum"] <= value <= rule["maximum"]:
                raise ValueError(f"{path}: integer is out of bounds")
        case "boolean":
            if type(value) is not bool:
                raise ValueError(f"{path}: expected a boolean")


def check_text(value, path):
    for char in value:
        code = ord(char)
        unsafe = (unicodedata.category(char) in {"Cc", "Cs"} and char not in "\n\t"
                  or 0x202A <= code <= 0x202E or 0x2066 <= code <= 0x2069
                  or 0xFDD0 <= code <= 0xFDEF or code & 0xFFFF in {0xFFFE, 0xFFFF})
        if unsafe:
            raise ValueError(f"{path}: unsupported control or Unicode code point")


def column_ranges(spec):
    """Return zero-based inclusive ranges with one full-width block between ranges."""
    blocks = spec["blocks"]
    index_by_id = {block["id"]: index for index, block in enumerate(blocks)}
    result = []
    previous_end = -2
    for region in spec.get("layout", {}).get("columns", []):
        start = index_by_id.get(region["from"], -1)
        end = index_by_id.get(region["through"], -1)
        if not (previous_end + 1 < start < end < len(blocks)):
            raise ValueError("column ranges must be known, ordered, disjoint and at least two blocks")
        if ((start and blocks[start - 1]["kind"] == "heading")
                or blocks[end]["kind"] == "heading"):
            raise ValueError("keep each column-region heading with its following text")
        for block in blocks[start:end + 1]:
            if (block["kind"] not in {"heading", "paragraph", "list", "callout"}
                    or block.get("new_page")):
                raise ValueError("column ranges support flowing prose, headings, lists and callouts")
        result.append((start, end))
        previous_end = end
    return result


def check_figure(figure, assets, design, *, cover=False):
    asset = figure["asset"]
    if asset not in assets:
        raise ValueError("asset is outside the verified PNG library")
    width, height = check_png(assets[asset], max_edge=RASTER_EDGE)
    spacing = design["spacing"]
    available = 210 - 2 * spacing["margin_mm"]
    max_height = 110 if cover else 155
    if "side_text" in figure:
        available = available * 2 / 5 - (spacing["cell_pt"] + 1) * 25.4 / 36
        max_height = 82
        if "\n" in figure["side_text"] or "\t" in figure["side_text"]:
            raise ValueError("figure side text must be one short paragraph")
    if figure["width_mm"] > available or figure["width_mm"] * height > max_height * width:
        raise ValueError(f"figure exceeds the available width or {max_height} mm height")


def validate_spec(spec, assets):
    """Check the brief and return the effective design used by the layout engine."""
    schema = read_json(confined(PACKAGE, "schemas/document.schema.json", ".json", package=True))
    validate_shape(spec, schema, schema["$defs"])
    all_ids = {block["id"] for block in spec["blocks"]}
    required = spec["acceptance"]["required_ids"]
    if len(all_ids) != len(spec["blocks"]) or len(required) != len(set(required)):
        raise ValueError("content identifiers and acceptance identifiers must be unique")
    if missing := sorted(set(required) - all_ids):
        raise ValueError("required content is missing: " + ", ".join(missing))
    level = 0
    design = resolve_design(spec["design"])
    column_ranges(spec)
    for index, block in enumerate(spec["blocks"]):
        kind = block["kind"]
        if kind == "cover" and index != 0:
            raise ValueError("a cover can appear only as the first block")
        if kind == "heading":
            if block["level"] > level + 1:
                raise ValueError("heading levels must begin at 1 and cannot skip a level")
            level = block["level"]
            if block.get("new_page") and index == 1 and spec["blocks"][0]["kind"] == "cover":
                raise ValueError("the cover already ends with a page break")
            if block.get("chapter") and level != 1:
                raise ValueError("a chapter introduction requires a level 1 heading")
        if kind == "list" and block.get("checklist") and block["ordered"]:
            raise ValueError("choose either a checklist or numbered steps")
        if kind == "paragraph" and block.get("keep_lines") and len(block["text"]) > 640:
            raise ValueError("keep_lines requires a paragraph of up to 640 characters")
        if kind == "table":
            columns = len(block["headers"])
            if any(len(row) != columns for row in block["rows"]):
                raise ValueError("table rows must have the same width as their headers")
            if weights := block.get("column_weights"):
                if len(weights) != columns or min(weights) * 10 < sum(weights):
                    raise ValueError("table weights must give each column at least 10% of the width")
            if block.get("presentation") == "comparison" and columns != 2:
                raise ValueError("a side-by-side comparison requires two columns")
            if block.get("keep_rows") and (len(block["rows"]) > 3 or
                    sum(len(cell) for row in [block["headers"], *block["rows"]]
                        for cell in row) > 900):
                raise ValueError("keep_rows is for short tables with up to three data rows")
        if kind == "code" and (len(block["text"].split("\n")) > 48
                or any(len(line.expandtabs(4)) > 100 for line in block["text"].split("\n"))):
            raise ValueError("code must fit within 48 lines of at most 100 columns")
        asset = block.get("icon") or block.get("asset")
        if asset and asset not in assets:
            raise ValueError("asset is outside the verified PNG library")
        if kind == "cover" and asset and asset.startswith("local-"):
            raise ValueError("cover marks require a bundled icon")
        if kind == "cover" and "illustration" in block:
            if "icon" in block or "caption" in block or len(block["lead"]) > 640:
                raise ValueError("an illustrated cover requires one illustration and a short lead")
            check_figure(block["illustration"], assets, design, cover=True)
        if kind == "figure":
            check_figure(block, assets, design)
    return design
