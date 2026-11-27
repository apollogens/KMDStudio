"""Rasterize the two reviewed Lucide paths without loading SVG or other inputs."""

import hashlib
import json
import struct
import zlib
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "skills/kmdstudio/assets"
UPSTREAM = "https://github.com/lucide-icons/lucide/blob/0.468.0/icons/"
PATHS = {
    # code-xml.svg uses three relative line paths.
    "code-xml": ([((18, 16), (22, 12), (18, 8)), ((6, 8), (2, 12), (6, 16)),
                  ((14.5, 4), (9.5, 20))], (16, 96, 72), "ISC"),
    # arrow-right.svg uses one horizontal line and one relative line path.
    "arrow-right": ([((5, 12), (19, 12)), ((12, 5), (19, 12), (12, 19))],
                    (45, 75, 114), "MIT"),
}


def chunk(kind, content):
    payload = kind + content
    return struct.pack(">I", len(content)) + payload + struct.pack(">I", zlib.crc32(payload))


def hits(x, y, start, end):
    x1, y1 = start
    dx, dy = end[0] - x1, end[1] - y1
    fraction = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    return (x - x1 - dx * fraction)**2 + (y - y1 - dy * fraction)**2 <= 1


def png(paths, rgb):
    edges = [edge for path in paths for edge in zip(path, path[1:])]
    size, samples = 144, (0.25, 0.75)
    rows = bytearray()
    for y in range(size):
        rows.append(0)
        for x in range(size):
            coverage = sum(any(hits((x + subx) / 6, (y + suby) / 6, a, b) for a, b in edges)
                           for subx in samples for suby in samples)
            rows.extend((*rgb, round(255 * coverage / 4)))
    header = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
            + chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b""))


def main():
    manifest = {}
    for name, (paths, rgb, license_id) in PATHS.items():
        notice = "licenses/feather.txt" if license_id == "MIT" else "licenses/lucide.txt"
        notice_hash = hashlib.sha256((ASSETS / notice).read_bytes()).hexdigest()
        data = png(paths, rgb)
        path = f"icons/{name}.png"
        (ASSETS / path).write_bytes(data)
        manifest[name] = {
            "path": path, "source": UPSTREAM + name + ".svg", "version": "0.468.0",
            "license": license_id, "license_path": notice, "license_sha256": notice_hash,
            "sha256": hashlib.sha256(data).hexdigest(),
            "verification": "reviewed-source-and-local-derivative",
        }
    (ASSETS / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n",
                                         encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
