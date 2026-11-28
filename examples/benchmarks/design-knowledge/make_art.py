"""Draw the three original Shoreline Room study prints before raster normalization."""

import argparse
import random
from pathlib import Path

from PIL import Image, ImageDraw

INK = "#153d42"
DEEP = "#0e3037"
WATER = "#2f5b5c"
MIST = "#8daba0"
PAPER = "#e7d6ab"
SAND = "#b49165"
RUST = "#bd7454"
WIDTH, HEIGHT = 1440, 864

STUDIES = {
    "low-bank": (
        (WATER, ((0, 643), (372, 605), (676, 689), (1100, 600), (1440, 624), (1440, 864), (0, 864))),
        (MIST, ((0, 361), (625, 361), (863, 461), (1008, 461), (1008, 516), (1440, 516), (1440, 553), (0, 491))),
        (SAND, ((0, 250), (1220, 250), (1220, 312), (1320, 312), (1320, 368), (1440, 368), (1440, 449), (0, 393))),
        (PAPER, ((0, 0), (1440, 0), (1440, 346), (1310, 346), (1310, 293), (1193, 293), (1193, 235), (0, 362))),
        (RUST, ((0, 118), (510, 110), (727, 138), (406, 164), (0, 158))),
    ),
    "slack-water": (
        (WATER, ((0, 353), (430, 304), (789, 364), (1440, 586), (1440, 746), (0, 651))),
        (MIST, ((0, 528), (466, 450), (759, 446), (1154, 570), (1440, 746), (1440, 864), (0, 864))),
        (PAPER, ((0, 650), (446, 523), (754, 459), (1125, 582), (1440, 767), (1440, 864), (0, 864))),
        (PAPER, ((0, 0), (1440, 0), (1440, 253), (1080, 287), (674, 405), (401, 379), (0, 341))),
        (SAND, ((0, 288), (426, 335), (674, 376), (1095, 246), (1440, 217), (1440, 253), (1080, 287), (674, 405), (401, 379), (0, 341))),
    ),
    "return-mark": (
        (WATER, ((0, 223), (334, 148), (702, 249), (1114, 184), (1440, 56), (1440, 378), (0, 448))),
        (MIST, ((0, 517), (509, 477), (837, 456), (1138, 414), (1440, 441), (1440, 859), (0, 864))),
        (SAND, ((0, 647), (449, 576), (781, 585), (1011, 561), (1035, 632), (814, 691), (597, 677), (1440, 739), (1440, 864), (0, 864))),
        (PAPER, ((0, 671), (425, 606), (778, 617), (980, 592), (998, 626), (811, 678), (580, 669), (454, 721), (1107, 789), (1440, 763), (1440, 864), (0, 864))),
        (RUST, ((1060, 763), (1205, 772), (1440, 738), (1440, 761), (1107, 789))),
    ),
}


def draw_study(layers, seed):
    image = Image.new("RGB", (WIDTH, HEIGHT), INK)
    draw = ImageDraw.Draw(image)
    for color, points in layers:
        draw.polygon(points, fill=color)
    if seed == 1:
        for offset in range(0, 90, 15):
            draw.line([(0, 524 + offset), (500, 496 + offset), (840, 551 + offset),
                       (1440, 566 + offset)], fill=DEEP, width=2)
    else:
        for offset in range(0, 55, 11):
            draw.line([(0, 55 + offset), (510, 105 + offset), (930, 74 + offset),
                       (1440, 120 + offset)], fill=DEEP if seed == 3 else SAND, width=2)
    randomizer = random.Random(seed)
    for _ in range(19_000):
        x = randomizer.randrange(WIDTH)
        y = randomizer.randrange(HEIGHT)
        shift = randomizer.choice((-14, -7, 8, 14))
        color = tuple(max(0, min(255, channel + shift)) for channel in image.getpixel((x, y)))
        draw.line([(x, y), (x + randomizer.randrange(4), y)], fill=color)
    return image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="existing directory for the source PNGs")
    output = parser.parse_args().output
    for seed, (name, layers) in enumerate(STUDIES.items(), 1):
        with (output / f"{name}.png").open("xb") as stream:
            draw_study(layers, seed).save(stream, format="PNG")


if __name__ == "__main__":
    main()
