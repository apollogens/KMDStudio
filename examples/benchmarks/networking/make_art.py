"""Draw original workbook illustrations and a reference board using the optional Pillow lock."""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
INK = "#18334B"
TEAL = "#12635D"
RUST = "#953F29"
PALE = "#FCF8ED"
TINT = "#F3EDE0"
GRID = "#D9CEBB"
WHITE = "#FFFFFF"


def routes():
    im = Image.new("RGB", (1320, 720), PALE)
    draw = ImageDraw.Draw(im)
    draw.rounded_rectangle((20, 20, 1300, 700), 36, fill=INK)
    for x in range(58, 1280, 48):
        for y in range(56, 685, 48):
            draw.ellipse((x - 1, y - 1, x + 1, y + 1), fill="#72908F")
    for path in (
        [(125, 550), (310, 550), (310, 158), (602, 158)],
        [(145, 272), (467, 272), (467, 535), (890, 535), (890, 365), (1185, 365)],
        [(602, 158), (952, 158), (952, 618), (1155, 618)],
        [(467, 535), (467, 405), (718, 405), (718, 244), (1180, 244)],
    ):
        draw.line(path, fill="#5C8589", width=5, joint="curve")
        for x, y in (path[0], path[-1]):
            draw.ellipse((x - 11, y - 11, x + 11, y + 11), fill=INK, outline="#93C6BB", width=4)
    path = [(140, 405), (405, 405), (405, 200), (742, 200), (742, 507), (1165, 507)]
    draw.line(path, fill="#F3B38E", width=9, joint="curve")
    for index, (x, y) in enumerate(path):
        radius = 26 if index in (0, len(path) - 1) else 15
        draw.ellipse((x - radius, y - radius, x + radius, y + radius),
                     fill="#FCDBC6", outline="#F3B38E", width=5)
    return im


def exchange():
    im = Image.new("RGB", (930, 650), PALE)
    draw = ImageDraw.Draw(im)
    draw.rounded_rectangle((12, 12, 918, 638), 30, fill=TINT, outline=GRID, width=4)
    draw.rounded_rectangle((78, 188, 277, 363), 22, fill=INK)
    draw.rounded_rectangle((96, 208, 259, 338), 7, fill=WHITE)
    draw.line((165, 363, 148, 408, 207, 408), fill=INK, width=11)
    for y in (190, 266, 342):
        draw.rounded_rectangle((664, y, 855, y + 55), 11, fill=INK)
        draw.ellipse((815, y + 19, 831, y + 35), fill="#9BCCBD")
    draw.line((308, 256, 622, 256), fill=RUST, width=8)
    draw.polygon(((622, 237), (650, 256), (622, 275)), fill=RUST)
    draw.line((628, 340, 315, 340), fill=TEAL, width=8)
    draw.polygon(((315, 320), (286, 340), (315, 360)), fill=TEAL)
    return im


def reference_board():
    im = Image.new("RGB", (810, 1050), PALE)
    draw = ImageDraw.Draw(im)
    draw.rectangle((54, 54, 758, 998), fill=WHITE, outline=GRID, width=2)
    draw.rectangle((96, 106, 242, 115), fill=RUST)
    for y, end in ((151, 659), (190, 538)):
        draw.rectangle((96, y, end, y + 24), fill=INK)
    draw.rounded_rectangle((96, 245, 716, 477), 16, fill=INK)
    draw.line((140, 413, 280, 413, 280, 321, 491, 321, 491, 382, 670, 382),
              fill="#F3B38E", width=5, joint="curve")
    for x, y in ((140, 413), (280, 321), (491, 382), (670, 382)):
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill="#F3B38E")

    def copy(x, y, width):
        draw.rectangle((x, y, x + width * 2 // 3, y + 10), fill=TEAL)
        for offset in (29, 46, 63, 80, 97):
            end = width if offset != 97 else width * 3 // 5
            draw.rectangle((x, y + offset, x + end, y + offset + 4), fill=INK)

    copy(96, 542, 620)
    copy(96, 691, 282)
    copy(432, 691, 282)
    copy(96, 837, 340)
    draw.rounded_rectangle((467, 827, 716, 946), 12, fill=TINT)
    draw.line((500, 876, 681, 876), fill=RUST, width=5)
    draw.line((681, 897, 500, 897), fill=TEAL, width=5)
    return im


def main():
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    manifest = {}
    for name, drawing in (("routes", routes()), ("exchange", exchange())):
        image = assets / f"{name}.png"
        drawing.save(image)
        digest = hashlib.sha256(image.read_bytes()).hexdigest()
        manifest[f"local-{name}"] = {
            "path": image.relative_to(ROOT.parents[2]).as_posix(),
            "origin": "authorized-local",
            "credit": "Original KMDStudio synthetic benchmark illustration",
            "source_sha256": digest,
            "sha256": digest,
        }
    (assets / "manifest.json").write_bytes((json.dumps(manifest, indent=2) + "\n").encode())
    reference_board().save(ROOT / "reference-board.png")


if __name__ == "__main__":
    main()
