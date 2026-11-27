"""Build or inspect the portable skill and exercise its CLI from an isolated directory."""

import argparse
import copy
import hashlib
import json
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import tomllib
import xml.etree.ElementTree as ET
from decimal import Decimal
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
SKILL_PARENT = ROOT / "skills"
SKILL = SKILL_PARENT / "kmdstudio"
BENCHMARKS = Path("examples/benchmarks")
VISUAL = BENCHMARKS / "visual-intelligence"
MANIFEST = VISUAL / "assets/study-vessel.json"
MANIFEST_SHA256 = "88404121fb734716791c3b328036b4a954fada5e7e6880eda91fce828d7057cf"
PREVIOUS = ROOT / "artifacts/v0.2.0/kmdstudio-0.2.0.zip"
PREVIOUS_HASH = "c42e8fd52f4ecafd7a040f1c09126f786628685f2cc80b14cb95fe37a450eb8b"
REFERENCE_BASELINE = ROOT / "artifacts/v0.3.0rc1/kmdstudio-0.3.0rc1.zip"
REFERENCE_BASELINE_HASH = "56415c7c743ae3b572365a1c802a88da60cc867f7b6989a80cc8d075cc5c90ef"
STRUCTURED_BASELINE = ROOT / "artifacts/v0.5.0rc1/kmdstudio-0.5.0rc1.zip"
STRUCTURED_BASELINE_HASH = "53ca34e50ca90ee401a8a856220abb5a0c317a21f31582d9348c68691f4455b9"
NETWORK = BENCHMARKS / "networking"
NETWORK_MANIFEST = NETWORK / "assets/manifest.json"
NETWORK_MANIFEST_HASH = "e5a5a91d55b33946e0be0965f910577dc21495315a727edd9d5d9399a15ee920"
CREATIVE = BENCHMARKS / "creative"
CREATIVE_MANIFEST = CREATIVE / "assets/manifest.json"
CREATIVE_MANIFEST_HASH = "754b9b648552f01659071528a43abffcbdfe775b6b48f6c164fd6fec853fee6f"
QUALITY = BENCHMARKS / "quality"
QUALITY_ARTIFACTS = Path("artifacts/v0.6.0rc1")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def skill_files():
    result = {}
    for path in sorted(SKILL.rglob("*")):
        relative = path.relative_to(SKILL_PARENT)
        if "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        info = path.lstat()
        require(not path.is_symlink() and not getattr(info, "st_file_attributes", 0) & 0x400,
                f"linked skill member {relative}")
        if stat.S_ISDIR(info.st_mode):
            continue
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, f"unsafe skill file {relative}")
        result[relative.as_posix()] = path.read_bytes()
    return result


def build_bundle(destination, files):
    with ZipFile(destination, "x") as package:
        for name, data in files.items():
            entry = ZipInfo(name)
            entry.create_system = 0
            package.writestr(entry, data, compress_type=ZIP_DEFLATED)


def unpack(archive, files, directory):
    with ZipFile(archive) as package:
        names = package.namelist()
        require(len(names) == len(files) and set(names) == files.keys(),
                "skill archive paths differ from canonical files")
        require(all(entry.file_size == len(files[entry.filename]) for entry in package.infolist()),
                "skill archive expanded sizes differ from canonical files")
        require(package.testzip() is None, "skill archive CRC mismatch")
        for name in names:
            content = package.read(name)
            require(content == files[name], f"skill archive bytes differ for {name}")
            target = directory / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)


def parts(docx):
    with ZipFile(docx) as package:
        require(len(package.namelist()) == len(set(package.namelist())),
                "OOXML archive has duplicate entries")
        require(package.testzip() is None, "OOXML archive CRC mismatch")
        return {name: package.read(name) for name in package.namelist()}


def native_text(node):
    pieces = []
    for item in node.iter():
        if item.tag == W + "t":
            pieces.append(item.text or "")
        elif item.tag == W + "tab":
            pieces.append("\t")
        elif item.tag == W + "br":
            pieces.append("\n")
    return "".join(pieces)


def verify_output(path, fixture, brief, directory):
    docx = parts(path)
    for name, data in docx.items():
        require("vba" not in name.casefold() and "embeddings/" not in name,
                f"unexpected executable or embedded object in {name}")
        if name.endswith(".rels"):
            require(all("TargetMode" not in rel.attrib for rel in ET.fromstring(data)),
                    f"external relationship in {name}")
    document = ET.fromstring(docx["word/document.xml"])
    paragraphs = [native_text(p) for p in document.iter(W + "p")]
    bookmarks = {node.get(W + "name") for node in document.iter(W + "bookmarkStart")}
    require(brief["title"] in paragraphs, "main title is missing or noneditable")
    for block_id in brief["acceptance"]["required_ids"]:
        require("kmd_" + block_id.replace("-", "_") in bookmarks,
                f"missing required block {block_id}")
    for block in brief["blocks"]:
        if block["kind"] == "code":
            require(block["text"] in paragraphs, "editable code differs from the source")
    if fixture.stem == "dispatch-readiness":
        tables = list(document.iter(W + "tbl"))
        require(len(tables) == 2, "expected two native tables")
        rows = []
        expected = [block for block in brief["blocks"] if block["kind"] == "table"]
        for table, block in zip(tables, expected):
            header, *body = table.findall(W + "tr")
            require(header.find(f"{W}trPr/{W}tblHeader") is not None, "missing repeating header")
            require([native_text(cell) for cell in header.findall(W + "tc")] == block["headers"],
                    "table headers differ from the source")
            cells = [[native_text(cell) for cell in row.findall(W + "tc")] for row in body]
            require(cells == block["rows"], "editable ledger rows differ from the source")
            rows.extend(cells)
        require(len(rows) == 32 and sum(int(row[2]) for row in rows) == 1725
                and sum(int(row[3]) for row in rows) == 1699
                and sum(row[4] == "Review" for row in rows) == 5, "ledger totals differ")
    if fixture.stem == "reading-the-surface":
        figure = next(block for block in brief["blocks"] if block["kind"] == "figure")
        asset = json.loads((directory / MANIFEST).read_bytes())[figure["asset"]]
        pictures = list(document.iter(WP + "docPr"))
        require(len(pictures) == 1 and pictures[0].get("descr") == figure["alt"],
                "Word drawing lacks the exact description")
        require(figure["caption"] in paragraphs, "caption is missing or noneditable")
        require(hashlib.sha256(docx["word/media/image1.png"]).hexdigest() == asset["sha256"],
                "embedded photo does not match the reviewed asset")


def compare_structured(directory, fixture, output, *manifest_args):
    historical = directory / "structured-baseline" / output.name
    subprocess.run(
        [sys.executable, "-E", "-s", "-S", "-B",
         str(historical.parent / "kmdstudio/scripts/generate.py"), "--root", str(directory),
         "--spec", fixture.as_posix(), "--output", historical.relative_to(directory).as_posix(),
         *manifest_args], cwd=directory.parent, check=True, capture_output=True, timeout=30,
    )
    require(output.read_bytes() == historical.read_bytes(), f"0.5.0rc1 regression in {fixture}")


def verify_cli(directory):
    shutil.copytree(ROOT / BENCHMARKS, directory / BENCHMARKS)
    require(hashlib.sha256(PREVIOUS.read_bytes()).hexdigest() == PREVIOUS_HASH,
            "baseline skill archive differs from the recorded hash")
    baseline = directory / "previous"
    with ZipFile(PREVIOUS) as previous:
        previous.extractall(baseline)
    require(hashlib.sha256(STRUCTURED_BASELINE.read_bytes()).hexdigest() == STRUCTURED_BASELINE_HASH,
            "0.5.0rc1 archive differs from its recorded hash")
    with ZipFile(STRUCTURED_BASELINE) as reference:
        reference.extractall(directory / "structured-baseline")
    fixtures = [
        path.relative_to(directory) for path in sorted((directory / BENCHMARKS).glob("*.json"))
    ]
    fixtures.extend(path.relative_to(directory) for path in sorted((directory / VISUAL).glob("*.json")))
    require(len(fixtures) == 6, "expected three regression and three candidate benchmarks")
    manifest_args = ["--asset-manifest", MANIFEST.as_posix(),
                     "--asset-manifest-sha256", MANIFEST_SHA256]
    python = [sys.executable, "-E", "-s", "-S", "-B"]
    for index, fixture in enumerate(fixtures):
        output = directory / (fixture.stem + ".docx")
        brief_args = ["--root", str(directory), "--spec", fixture.as_posix()]
        args = [*python, str(directory / "kmdstudio/scripts/generate.py"), *brief_args,
                "--output", output.name]
        if fixture.stem == "reading-the-surface":
            failed = subprocess.run(args, cwd=directory.parent, capture_output=True,
                                    check=False, timeout=30)
            require(failed.returncode == 2 and not output.exists(),
                    "unapproved illustration was accepted")
            args.extend(manifest_args)
        started = time.perf_counter()
        result = subprocess.run(args, cwd=directory if index % 2 else directory.parent,
                                capture_output=True, check=False, timeout=30)
        require(result.returncode == 0,
                f"CLI failed for {fixture}: {result.stderr.decode('utf-8', errors='replace')}")
        elapsed = time.perf_counter() - started
        verify_output(output, fixture, json.loads((directory / fixture).read_bytes()), directory)
        if fixture.parent == BENCHMARKS:
            historical = baseline / output.name
            subprocess.run(
                [*python, str(baseline / "kmdstudio/scripts/generate.py"), *brief_args,
                 "--output", historical.relative_to(directory).as_posix()],
                cwd=directory.parent, check=True, capture_output=True, timeout=30,
            )
            require(parts(output) == parts(historical), "existing benchmark changed")
        compare_structured(directory, fixture, output,
                           *(manifest_args if fixture.stem == "reading-the-surface" else []))
        print(f"{output.name} {output.stat().st_size} bytes {elapsed * 1000:.0f} ms, 0.5.0rc1 exact PASS")


def compatible_brief(source):
    """Keep the source in order using features in the 0.3.0rc1 package."""
    brief = copy.deepcopy(source)
    del brief["layout"]
    blocks = []
    for block in brief["blocks"]:
        block.pop("keep_lines", None)
        block.pop("keep_rows", None)
        if "side_text" in block:
            blocks.append({"id": block["id"] + "-copy", "kind": "paragraph",
                           "text": block.pop("side_text")})
        image = block.pop("illustration", None)
        blocks.append(block)
        if image:
            blocks.append({"id": "cover-art", "kind": "figure", **image})
    brief["blocks"] = blocks
    return brief


def verify_networking(directory, destination=None):
    fixture = NETWORK / "networking.json"
    source = json.loads((directory / fixture).read_bytes())
    reference = json.loads((directory / NETWORK / "reference-analysis.json").read_bytes())
    application = reference["application"]
    require(all(source["design"]["tokens"][key] == application[key] for key in
                ("colors", "typography", "spacing", "composition"))
            and source["layout"] == application["layout"], "reference mapping diverges from the brief")
    images = [source["blocks"][0]["illustration"],
              next(block for block in source["blocks"] if "side_text" in block)]
    require([image["asset"] for image in images] == list(application["image_slots"].values()),
            "reference image slots diverge from the brief")
    require(hashlib.sha256(REFERENCE_BASELINE.read_bytes()).hexdigest() == REFERENCE_BASELINE_HASH,
            "0.3.0rc1 archive differs from its recorded hash")
    baseline = directory / "baseline-v030"
    with ZipFile(REFERENCE_BASELINE) as package:
        package.extractall(baseline)
    compatible = fixture.with_name("baseline-brief.json")
    (directory / compatible).write_bytes(json.dumps(compatible_brief(source)).encode())
    selected = []
    for name, skill, brief_path in (
        ("networking", directory, fixture),
        ("networking-v0.3.0rc1", baseline, compatible),
    ):
        output = directory / f"{name}.docx"
        start = time.perf_counter()
        subprocess.run(
            [sys.executable, "-E", "-s", "-S", "-B", str(skill / "kmdstudio/scripts/generate.py"),
             "--root", str(directory), "--spec", brief_path.as_posix(), "--output", output.name,
             "--asset-manifest", NETWORK_MANIFEST.as_posix(),
             "--asset-manifest-sha256", NETWORK_MANIFEST_HASH],
            cwd=directory.parent, check=True, capture_output=True, timeout=30,
        )
        duration = (time.perf_counter() - start) * 1000
        verify_output(output, fixture, source, directory)
        package = parts(output)
        document = ET.fromstring(package["word/document.xml"])
        style_tree = ET.fromstring(package["word/styles.xml"])
        styles = {style.get(W + "styleId"): style for style in style_tree.findall(W + "style")}
        for style, tag, value in (
            ("CoverTitle", "color", application["colors"]["primary"]),
            ("Heading2", "color", application["colors"]["accent"]),
            ("Normal", "sz", str(application["typography"]["body_pt"] * 2)),
        ):
            run_style = styles[style].find(f"{W}rPr/{W}{tag}")
            require(run_style.get(W + "val") == value, "reference KDL style was not materialized")
        props = list(document.iter(WP + "docPr"))
        require([prop.get("descr") for prop in props] == [image["alt"] for image in images],
                "networking alternative text differs from the brief")
        manifest = json.loads((directory / NETWORK_MANIFEST).read_bytes())
        for index, image in enumerate(images, 1):
            require(hashlib.sha256(package[f"word/media/image{index}.png"]).hexdigest()
                    == manifest[image["asset"]]["sha256"], "networking artwork differs")
        tables = list(document.iter(W + "tbl"))
        data = [list(table.iter(W + "tr")) for table in tables]
        data = [rows for rows in data if len(rows) > 1]
        table_briefs = [block for block in source["blocks"] if block["kind"] == "table"]
        require(len(data) == len(table_briefs), "networking data table count differs")
        for rows, block in zip(data, table_briefs, strict=True):
            require(rows[0].find(f"{W}trPr/{W}tblHeader") is not None and
                    [[native_text(cell) for cell in row.findall(W + "tc")] for row in rows]
                    == [block["headers"], *block["rows"]], "networking data table differs")
        selected.append((output, document, tables))
        print(f"{output.name} {output.stat().st_size} bytes {duration:.0f} ms PASS")

    (_, candidate, tables), (_, previous, previous_tables) = selected
    for document, counts in ((candidate, (3, 1)), (previous, (1, 0))):
        require((len(list(document.iter(W + "sectPr"))), len(list(document.iter(W + "cols"))))
                == counts, "networking section profile differs")
    require(len(tables) == len(previous_tables) + 1, "missing text-and-figure row")
    require([value for p in candidate.iter(W + "p") if (value := native_text(p)) and value != "\n"] ==
            [value for p in previous.iter(W + "p") if (value := native_text(p)) and value != "\n"],
            "candidate and comparison differ in native text order")
    if destination is not None:
        for output, _, _ in selected:
            with (destination / output.name).open("xb") as target:
                target.write(output.read_bytes())
    compare_structured(directory, fixture, selected[0][0], "--asset-manifest",
                       NETWORK_MANIFEST.as_posix(), "--asset-manifest-sha256", NETWORK_MANIFEST_HASH)
    print("networking.docx 0.5.0rc1 exact PASS")


def verify_creative(directory, destination=None):
    fixtures = sorted((directory / CREATIVE).glob("*.json"))
    require(len(fixtures) == 5, "expected five editorial comparison artifacts")
    manifest = json.loads((directory / CREATIVE_MANIFEST).read_bytes())
    documents = {}
    for path in fixtures:
        fixture = path.relative_to(directory)
        brief = json.loads(path.read_bytes())
        output = directory / (fixture.stem + ".docx")
        subprocess.run(
            [sys.executable, "-E", "-s", "-S", "-B", str(directory / "kmdstudio/scripts/generate.py"),
             "--root", str(directory), "--spec", fixture.as_posix(), "--output", output.name,
             "--asset-manifest", CREATIVE_MANIFEST.as_posix(), "--asset-manifest-sha256",
             CREATIVE_MANIFEST_HASH], cwd=directory.parent, check=True, capture_output=True, timeout=30,
        )
        verify_output(output, fixture, brief, directory)
        package = parts(output)
        document = ET.fromstring(package["word/document.xml"])
        drawings = list(document.iter(WP + "docPr"))
        artwork = ([brief["blocks"][0]["illustration"]] if "illustration" in brief["blocks"][0]
                   else []) + [block for block in brief["blocks"] if block["kind"] == "figure"]
        require([drawing.get("descr") for drawing in drawings] == [image["alt"] for image in artwork],
                "editorial alternative text differs")
        for index, asset in enumerate(artwork, 1):
            require(hashlib.sha256(package[f"word/media/image{index}.png"]).hexdigest()
                    == manifest[asset["asset"]]["sha256"], "editorial image differs")
        data_rows = [table.findall(W + "tr") for table in document.iter(W + "tbl")]
        data_rows = [rows for rows in data_rows if len(rows) > 1]
        table_briefs = [block for block in brief["blocks"] if block["kind"] == "table"]
        values = []
        for rows, block in zip(data_rows, table_briefs, strict=True):
            require(rows[0].find(f"{W}trPr/{W}tblHeader") is not None, "missing repeating header")
            result = [[native_text(cell) for cell in row.findall(W + "tc")] for row in rows]
            require(result == [block["headers"], *block["rows"]], "editorial table content differs")
            values.append(result)
        documents[fixture.stem] = document, package, values
        if destination is not None:
            with (destination / output.name).open("xb") as target:
                target.write(output.read_bytes())
        print(f"{output.name} {output.stat().st_size} bytes PASS")

    editorial, editorial_parts, routes = documents["cooler-route-editorial"]
    structured, structured_parts, _ = documents["cooler-route-structured"]
    texts = [[text for para in doc.iter(W + "p") if (text := native_text(para)) not in {"", "\n"}]
             for doc in (editorial, structured)]
    require(texts[0] == texts[1] and all(editorial_parts[name] == structured_parts[name]
                                        for name in editorial_parts if name.startswith("word/media/")),
            "same-content editions diverged")
    require(len(list(editorial.iter(W + "tbl"))) == 3 and len(list(structured.iter(W + "tbl"))) == 1
            and editorial_parts["word/styles.xml"] != structured_parts["word/styles.xml"],
            "same-content layout or typography did not change")
    for column in (1, 2, 3):
        require(sum(Decimal(row[column]) for row in routes[0][1:-1]) == Decimal(routes[0][-1][column]),
                "walking report totals differ")
    fees = documents["fieldwork-agreement"][2][0]
    require(sum(Decimal(row[1].replace(",", "")) for row in fees[1:-1])
            == Decimal(fees[-1][1].replace(",", "")) == Decimal("1800.00"), "incorrect synthetic fee total")
    authors, books, results = documents["relational-databases"][2]
    require([[author[1], book[1]] for book in books[1:] for author in authors[1:] if author[0] == book[2]]
            == results[1:], "relational lesson result differs from its source rows")
    require(documents["night-relay"][2][0][3] == ["00:28", "Both", "Silent pause for four seconds."],
            "timed silence differs from the performance score")
    print("same content, route/fee totals, lesson joins and score cue PASS")


def verify_quality(directory, destination=None):
    for folder in (Path("artifacts/v0.5.0rc1"), QUALITY_ARTIFACTS):
        (directory / folder).mkdir(parents=True, exist_ok=True)
        for path in (ROOT / folder).glob("*.docx"):
            shutil.copyfile(path, directory / folder / path.name)
    fixtures = sorted((directory / QUALITY).glob("*.json"))
    fixtures += sorted((directory / QUALITY / "intermediate").glob("*.json"))
    require(len(fixtures) == 7, "expected seven retained quality benchmark stages")
    python = [sys.executable, "-E", "-s", "-S", "-B"]
    scripts = directory / "kmdstudio/scripts"
    for fixture in fixtures:
        output = directory / (fixture.stem + ".docx")
        subprocess.run(
            [*python, str(scripts / "generate.py"), "--root", str(directory),
             "--spec", fixture.relative_to(directory).as_posix(), "--output", output.name,
             "--asset-manifest", CREATIVE_MANIFEST.as_posix(), "--asset-manifest-sha256",
             CREATIVE_MANIFEST_HASH], cwd=directory.parent, check=True, capture_output=True, timeout=30,
        )
        verify_output(output, fixture, json.loads(fixture.read_bytes()), directory)
        require(parts(output) == parts(directory / QUALITY_ARTIFACTS / output.name),
                f"regenerated quality benchmark differs from retained OOXML: {output.name}")
        if destination is not None:
            with (destination / output.name).open("xb") as target:
                target.write(output.read_bytes())
        print(f"{output.name} {output.stat().st_size} bytes, retained OOXML PASS")
    records = sorted((directory / QUALITY / "records").glob("*.json"))
    require(len(records) == 4, "expected four bounded correction records")
    for path in records:
        subprocess.run([*python, str(scripts / "review_quality.py"), "--root", str(directory),
                        "--record", path.relative_to(directory).as_posix()],
                       cwd=directory.parent, check=True, capture_output=True, timeout=30)
    print("four correction records and retained source text, alt text, and image bytes PASS")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--build", type=Path, help="write a new portable skill archive")
    modes.add_argument("--archive", type=Path, help="verify an existing candidate archive")
    parser.add_argument("--networking-output", type=Path,
                        help="also save the verified networking pair in an existing directory")
    parser.add_argument("--creative-output", type=Path,
                        help="also save the five creative benchmark DOCX files in an existing directory")
    parser.add_argument("--quality-output", type=Path,
                        help="also save the seven quality benchmark stages in an existing directory")
    args = parser.parse_args()
    version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    files = skill_files()
    with tempfile.TemporaryDirectory(prefix="kmdstudio-bundle-") as tmp:
        directory = Path(tmp).resolve(strict=True)
        archive = args.archive or args.build or directory / f"kmdstudio-{version}.zip"
        if args.archive is None:
            build_bundle(archive, files)
        unpack(archive, files, directory)
        verify_cli(directory)
        verify_networking(directory, args.networking_output)
        verify_creative(directory, args.creative_output)
        verify_quality(directory, args.quality_output)
        print(f"{len(files)} canonical skill files, {archive.stat().st_size} archive bytes")


if __name__ == "__main__":
    main()
