import importlib.util
import json
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

from generate import build_document
from guard import read_json, sha256
from raster import PNG_SIGNATURE, normalized_dimensions, verified_rasters
from review_docx import check_docx, read_archive
from test_kmdstudio import BENCHMARKS, ROOT, SKILL, rewrite_package

VISUAL = BENCHMARKS / "visual-intelligence"


def png_chunk(kind, content):
    return struct.pack(">I", len(content)) + kind + content + struct.pack(
        ">I", zlib.crc32(kind + content))


def single_pixel(rows, extra=b""):
    header = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    return (PNG_SIGNATURE + png_chunk(b"IHDR", header) + extra
            + png_chunk(b"IDAT", zlib.compress(rows)) + png_chunk(b"IEND", b""))


class RasterGateTests(unittest.TestCase):
    def setUp(self):
        area = tempfile.TemporaryDirectory()
        self.addCleanup(area.cleanup)
        self.root = Path(area.name).resolve(strict=True)

    def test_normalized_profile_checks_pixels_crc_and_auxiliary_chunks(self):
        pixel = b"\0\x92\x44\x20"
        self.assertEqual(normalized_dimensions(single_pixel(pixel)), (1, 1))
        for wrong in (
            single_pixel(pixel * 1024),
            single_pixel(b"\x05" + pixel[1:]),
            single_pixel(pixel, png_chunk(b"tEXt", b"Author\0Example")),
            single_pixel(pixel)[:-1] + b"\0",
            single_pixel(pixel) + b"trailing",
        ):
            with self.subTest(length=len(wrong)), self.assertRaises(ValueError):
                normalized_dimensions(wrong)

    def test_explicit_manifest_and_asset_integrity(self):
        png = self.root / "figure.png"
        png.write_bytes(single_pixel(b"\0\x12\x34\x56"))
        manifest = self.root / "manifest.json"
        entry = {"path": png.name, "origin": "authorized-local", "credit": "Synthetic pixel",
                 "source_sha256": sha256(png.read_bytes()), "sha256": sha256(png.read_bytes())}

        def store():
            manifest.write_text(json.dumps({"local-figure": entry}), encoding="utf-8")
            return sha256(manifest.read_bytes())

        digest = store()
        self.assertEqual(verified_rasters(self.root, manifest.name, digest),
                         {"local-figure": png.read_bytes()})
        manifest.write_bytes(manifest.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "manifest integrity"):
            verified_rasters(self.root, manifest.name, digest)
        png.write_bytes(single_pixel(b"\0\x12\x34\x57"))
        with self.assertRaisesRegex(ValueError, "illustration integrity"):
            verified_rasters(self.root, manifest.name, store())
        entry["path"] = "../figure.png"
        with self.assertRaises(ValueError):
            verified_rasters(self.root, manifest.name, store())

    def test_figure_alignment_geometry_and_required_caption(self):
        manifest = VISUAL / "assets/study-vessel.json"
        assets = verified_rasters(ROOT, manifest.relative_to(ROOT).as_posix(),
                                  sha256(manifest.read_bytes()))
        spec, output = build_document(VISUAL / "reading-the-surface.json", illustrations=assets)
        body = read_archive(output)["word/document.xml"]
        for old, new, message in (
            (b'w:val="left"', b'w:val="center"', "alignment"),
            (b'<wp:extent cx="5256000"', b'<wp:extent cx="5256001"', "dimensions"),
            (b"<w:keepNext />", b"", "caption"),
        ):
            changed = body.replace(old, new)
            self.assertNotEqual(body, changed)
            damaged = rewrite_package(output, {"word/document.xml": changed})
            with self.assertRaisesRegex(ValueError, message):
                check_docx(damaged, assets, spec=spec)

        spec["blocks"][1]["width_mm"] = 165
        spec["design"]["tokens"]["spacing"] = {"margin_mm": 26}
        brief = self.root / "too-wide.json"
        brief.write_text(json.dumps(spec), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "available width"):
            build_document(brief, illustrations=assets)

    def test_manifest_keeps_three_asset_limit(self):
        manifest = self.root / "too-many.json"
        manifest.write_text(json.dumps({f"local-image-{n}": {} for n in range(4)}),
                            encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "one to three"):
            verified_rasters(self.root, manifest.name, sha256(manifest.read_bytes()))


@unittest.skipUnless(importlib.util.find_spec("PIL"), "optional raster decoder unavailable")
class RasterImportTests(unittest.TestCase):
    def setUp(self):
        area = tempfile.TemporaryDirectory()
        self.addCleanup(area.cleanup)
        self.root = Path(area.name).resolve(strict=True)

    def run_import(self, name, output="normalized.png"):
        return subprocess.run(
            [sys.executable, "-E", "-s", "-B", str(SKILL / "scripts/import_raster.py"),
             "--root", str(self.root), "--input", name, "--output", output, "--id",
             "local-example", "--origin", "authorized-local", "--credit", "Synthetic fixture"],
            capture_output=True, check=False, timeout=15,
        )

    def test_png_metadata_removed_and_existing_output_preserved(self):
        from PIL import Image, PngImagePlugin

        source = self.root / "source.png"
        comment = PngImagePlugin.PngInfo()
        comment.add_text("Comment", "This metadata must not survive the import.")
        Image.new("RGBA", (12, 8), (31, 33, 37, 120)).save(source, pnginfo=comment)
        result = self.run_import(source.name)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = self.root / "normalized.png"
        original = output.read_bytes()
        self.assertEqual(normalized_dimensions(original), (12, 8))
        with Image.open(output) as image:
            self.assertEqual(image.getpixel((0, 0)), (31, 33, 37, 120))
            self.assertFalse(image.info)
        manifest = self.root / "manifest.json"
        manifest.write_bytes(result.stdout)
        self.assertEqual(read_json(manifest)["local-example"]["source_sha256"],
                         sha256(source.read_bytes()))
        self.assertEqual(self.run_import(source.name).returncode, 2)
        self.assertEqual(output.read_bytes(), original)

    def test_jpeg_orientation_and_malformed_or_oversized_inputs(self):
        from PIL import Image

        source = self.root / "source.jpg"
        frame = Image.new("RGB", (14, 7), "tan")
        exif = Image.Exif()
        exif[274] = 6
        frame.save(source, exif=exif)
        result = self.run_import(source.name, "oriented.png")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(normalized_dimensions((self.root / "oriented.png").read_bytes()), (7, 14))

        Image.new("RGB", (4097, 1)).save(self.root / "too-wide.png")
        frame.save(self.root / "motion.png", save_all=True,
                   append_images=[Image.new("RGB", frame.size, "navy")])
        (self.root / "wrong.png").write_bytes(source.read_bytes())
        (self.root / "cut.jpg").write_bytes(source.read_bytes()[:40])
        for name in ("too-wide.png", "motion.png", "wrong.png", "cut.jpg", "../source.jpg"):
            with self.subTest(name=name):
                self.assertEqual(self.run_import(name).returncode, 2)
                self.assertFalse((self.root / "normalized.png").exists())
        self.assertFalse(list(self.root.glob(".kmd-*.tmp")))
