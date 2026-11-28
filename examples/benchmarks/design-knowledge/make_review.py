"""Assemble diagnostic Writer page PNGs into anonymized benchmark sheets."""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

SHEETS = {
    "report-baseline": (("A", "cooler-route-evidence"), ("B", "cooler-route-refined")),
    "report-concepts": (("A", "cooler-route-place"), ("B", "cooler-route-evidence")),
    "publication": (("", "edge-of-the-water"),),
    "lesson": (("", "rolling-window"),),
    "booking": (("", "reading-room-booking"),),
}
TILE_WIDTH, TILE_HEIGHT = 436, 614
MAX_COLUMNS = 3


def make_sheet(rows, source):
    tiles = []
    for label, name in rows:
        paths = sorted((source / name).glob("page-*.png"))
        if not paths:
            raise FileNotFoundError(f"no rendered pages for {name}")
        entries = [(f"{label}  /  {index}" if label else str(index), path)
                   for index, path in enumerate(paths, 1)]
        tiles.extend(entries[offset:offset + MAX_COLUMNS]
                     for offset in range(0, len(entries), MAX_COLUMNS))
    canvas = Image.new("RGB", (max(map(len, tiles)) * TILE_WIDTH, len(tiles) * TILE_HEIGHT), "#deddd8")
    draw = ImageDraw.Draw(canvas)
    for row, entries in enumerate(tiles):
        for column, (caption, path) in enumerate(entries):
            x, y = column * TILE_WIDTH + 12, row * TILE_HEIGHT + 12
            with Image.open(path) as page:
                thumb = ImageOps.contain(page.convert("RGB"), (TILE_WIDTH - 24, TILE_HEIGHT - 41))
            canvas.paste(thumb, (x + (TILE_WIDTH - 24 - thumb.width) // 2, y))
            draw.text((x + 3, y + TILE_HEIGHT - 36), caption, fill="#242424", font_size=15)
    return canvas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pages", type=Path, help="per-document folders of numbered page PNGs")
    parser.add_argument("output", type=Path, help="existing directory for review sheets")
    args = parser.parse_args()
    for name, rows in SHEETS.items():
        with (args.output / f"{name}.png").open("xb") as target:
            make_sheet(rows, args.pages).save(target, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
