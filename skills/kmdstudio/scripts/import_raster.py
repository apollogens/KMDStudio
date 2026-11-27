"""Normalize an explicitly authorized local PNG or JPEG and print a review receipt."""

import argparse
import io
import json
import sys
import warnings
from pathlib import PurePath

from guard import bounded_read, confined, publish_new, sha256, workspace
from raster import ORIGINS, RASTER_EDGE, RASTER_LIMIT, check_provenance, normalized_dimensions

SOURCE_LIMIT = 8 * 1024 * 1024
SOURCE_PIXELS = 8_000_000
PILLOW_VERSION = "13.0.0"
FORMATS = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG"}


def normalize(data, image_format):
    import PIL
    from PIL import Image, ImageOps

    if PIL.__version__ != PILLOW_VERSION:
        raise ValueError("the pinned optional raster decoder is required")
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(io.BytesIO(data), formats=(image_format,)) as source:
            width, height = source.size
            if (max(width, height) > 4096 or width * height > SOURCE_PIXELS
                    or getattr(source, "is_animated", False)):
                raise ValueError("source image exceeds dimensions, pixels or frame limit")
            source.verify()
        with Image.open(io.BytesIO(data), formats=(image_format,)) as source:
            oriented = ImageOps.exif_transpose(source)
            rgba = oriented.mode in {"RGBA", "LA", "PA"} or "transparency" in oriented.info
            converted = oriented.convert("RGBA" if rgba else "RGB")
            converted.thumbnail((RASTER_EDGE, RASTER_EDGE), Image.Resampling.LANCZOS)
            # A fresh pixel buffer carries no source EXIF, XMP, ICC profiles or other metadata.
            clean = Image.new(converted.mode, converted.size)
            clean.paste(converted)
    while True:
        result = io.BytesIO()
        clean.save(result, format="PNG")
        if result.tell() <= RASTER_LIMIT:
            return result.getvalue()
        edge = max(clean.size) * 3 // 4
        clean.thumbnail((edge, edge), Image.Resampling.LANCZOS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="absolute, approved local workspace")
    parser.add_argument("--input", required=True, help="relative PNG, JPG or JPEG input")
    parser.add_argument("--output", required=True, help="new relative PNG output")
    parser.add_argument("--id", required=True, help="local- figure asset ID")
    parser.add_argument("--origin", required=True, choices=sorted(ORIGINS))
    parser.add_argument("--credit", required=True, help="short source and rights note")
    args = parser.parse_args()
    try:
        from PIL.Image import DecompressionBombError, DecompressionBombWarning
    except ImportError:
        print("BLOCKED: install the pinned optional raster decoder.", file=sys.stderr)
        return 2
    try:
        check_provenance(args.id, args.origin, args.credit)
        root = workspace(args.root)
        suffix = PurePath(args.input).suffix.lower()
        if suffix not in FORMATS:
            raise ValueError("only local PNG and JPEG input is supported")
        source = confined(root, args.input, suffix)
        destination = confined(root, args.output, ".png", new=True)
        original = bounded_read(source, SOURCE_LIMIT)
        png = normalize(original, FORMATS[suffix])
        normalized_dimensions(png)
        receipt = {args.id: {
            "path": destination.relative_to(root).as_posix(),
            "origin": args.origin,
            "credit": args.credit,
            "source_sha256": sha256(original),
            "sha256": sha256(png),
        }}
        publish_new(destination, png)
    except (ValueError, OSError, SyntaxError, RuntimeError, DecompressionBombError,
            DecompressionBombWarning) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
