"""Validate operator-approved, normalized illustration assets without Pillow."""

import re
import struct
import zlib

from guard import bounded_read, confined, parse_json, sha256

RASTER_LIMIT = 768 * 1024
RASTER_EDGE = 1600
RASTER_COUNT = 3
RASTER_MANIFEST_LIMIT = 8192
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
ASSET_ID = re.compile(r"local-[a-z][a-z0-9-]{0,25}")
DIGEST = re.compile(r"[0-9a-f]{64}")
ORIGINS = {"authorized-local", "host-generated"}


def normalized_dimensions(data):
    """Accept only bounded, static RGB(A) pixels and no auxiliary chunks."""
    if not 45 <= len(data) <= RASTER_LIMIT or not data.startswith(PNG_SIGNATURE):
        raise ValueError("invalid normalized PNG size or signature")
    offset = len(PNG_SIGNATURE)
    pixels = bytearray()
    width = height = channels = 0
    while offset + 12 <= len(data):
        length, name = struct.unpack_from(">I4s", data, offset)
        end = offset + 8 + length
        if end + 4 > len(data):
            raise ValueError("truncated normalized PNG chunk")
        payload = data[offset + 8:end]
        crc, = struct.unpack_from(">I", data, end)
        if crc != zlib.crc32(payload, zlib.crc32(name)):
            raise ValueError("invalid normalized PNG checksum")
        if name == b"IHDR" and offset == 8 and length == 13:
            width, height, depth, color, compression, filtering, interlace = struct.unpack(
                ">IIBBBBB", payload)
            if (not (1 <= width <= RASTER_EDGE and 1 <= height <= RASTER_EDGE)
                    or depth != 8 or color not in (2, 6) or compression or filtering or interlace):
                raise ValueError("unsupported normalized PNG dimensions or format")
            channels = 3 if color == 2 else 4
        elif name == b"IDAT" and channels and length:
            pixels.extend(payload)
        elif name == b"IEND" and not length and pixels and end + 4 == len(data):
            break
        else:
            raise ValueError("unexpected normalized PNG chunk")
        offset = end + 4
    else:
        raise ValueError("incomplete normalized PNG")
    stride = width * channels + 1
    expected = stride * height
    decoder = zlib.decompressobj()
    try:
        rows = decoder.decompress(pixels, expected + 1)
    except zlib.error as exc:
        raise ValueError("invalid normalized PNG pixel stream") from exc
    if (len(rows) != expected or not decoder.eof or decoder.unused_data
            or any(value > 4 for value in rows[::stride])):
        raise ValueError("invalid normalized PNG scanlines")
    return width, height


def check_provenance(asset_id, origin, credit):
    if not isinstance(asset_id, str) or not ASSET_ID.fullmatch(asset_id):
        raise ValueError("expected a local- illustration ID")
    if not isinstance(origin, str) or origin not in ORIGINS:
        raise ValueError("invalid illustration origin")
    if (not isinstance(credit, str) or not 1 <= len(credit) <= 160
            or not credit.strip() or not credit.isprintable()):
        raise ValueError("illustration credit must be printable text")


def verified_rasters(root, relative_manifest, digest):
    manifest_path = confined(root, relative_manifest, ".json")
    data = bounded_read(manifest_path, RASTER_MANIFEST_LIMIT)
    if not DIGEST.fullmatch(digest) or sha256(data) != digest:
        raise ValueError("illustration manifest integrity check failed")
    manifest = parse_json(data)
    if not isinstance(manifest, dict) or not 1 <= len(manifest) <= RASTER_COUNT:
        raise ValueError("expected one to three reviewed illustrations")
    keys = {"path", "origin", "credit", "source_sha256", "sha256"}
    assets = {}
    for asset_id, entry in manifest.items():
        if (not isinstance(entry, dict) or entry.keys() != keys
                or any(not isinstance(value, str) for value in entry.values())
                or not DIGEST.fullmatch(entry["source_sha256"])
                or not DIGEST.fullmatch(entry["sha256"])):
            raise ValueError("invalid illustration manifest entry")
        check_provenance(asset_id, entry["origin"], entry["credit"])
        png = bounded_read(confined(root, entry["path"], ".png"), RASTER_LIMIT)
        if sha256(png) != entry["sha256"]:
            raise ValueError("illustration integrity check failed")
        normalized_dimensions(png)
        assets[asset_id] = png
    return assets
