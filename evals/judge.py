"""Check bounded synthetic evaluation evidence without executing workspace files."""

import json
import stat
import xml.etree.ElementTree as ET
from pathlib import PurePosixPath
from zipfile import BadZipFile, ZipFile

TRACE_LIMIT = 2 * 1024 * 1024
LINE_LIMIT = 128 * 1024
ARTIFACT_LIMIT = 4 * 1024 * 1024
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"
CT = "{http://schemas.openxmlformats.org/package/2006/content-types}"
MAIN_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"
OFFICE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"


def read_trace(path):
    with path.open("rb") as stream:
        data = stream.read(TRACE_LIMIT + 1)
    records = []
    if len(data) > TRACE_LIMIT:
        return records, "trace exceeded size limit"
    for line in data.splitlines(keepends=True):
        if not line.strip():
            continue
        if len(records) >= 4096 or len(line) > LINE_LIMIT or not line.endswith(b"\n"):
            return records, "incomplete or oversized JSONL trace"
        try:
            record = json.loads(line)
        except (ValueError, RecursionError):
            return records, "invalid JSONL trace"
        if (not isinstance(record, dict) or not isinstance(record.get("type"), str)
                or record["type"] == "item.completed" and not isinstance(record.get("item"), dict)):
            return records, "invalid JSONL event"
        records.append(record)
    return records, None


def local_file(path):
    info = path.lstat()
    if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
            or getattr(info, "st_file_attributes", 0) & 0x400
            or not 0 < info.st_size <= ARTIFACT_LIMIT):
        raise ValueError("expected a bounded plain output file")


def editable_report(path, required_text=(), required_rows=()):
    local_file(path)
    with ZipFile(path) as package:
        entries = package.infolist()
        if (len(entries) > 80 or sum(item.file_size for item in entries) > ARTIFACT_LIMIT
                or len({item.filename.casefold() for item in entries}) != len(entries)):
            raise ValueError("unexpected package size or duplicate parts")
        trees = {}
        for item in entries:
            name = item.filename
            if (name != item.orig_filename or name.startswith("/") or "\\" in name
                    or any(part in {"", ".", ".."} or ":" in part for part in name.split("/"))
                    or any(token in name.casefold() for token in ("vba", "/embeddings/", "/activex/"))
                    or stat.S_ISLNK(item.external_attr >> 16) or item.flag_bits & 1):
                raise ValueError("unexpected package member")
            if name.endswith((".xml", ".rels")):
                data = package.read(item)
                if b"\0" in data or b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
                    raise ValueError("unexpected XML declaration")
                trees[name] = ET.fromstring(data)
        for name, root in trees.items():
            if name.endswith(".rels") and any(
                node.tag != REL + "Relationship"
                or node.get("TargetMode", "Internal").casefold() != "internal"
                for node in root
            ):
                raise ValueError("unexpected external relationship")
        content_types = trees["[Content_Types].xml"]
        if content_types.tag != CT + "Types" or [
            node.get("ContentType") for node in content_types.findall(CT + "Override")
            if node.get("PartName") == "/word/document.xml"
        ] != [MAIN_TYPE]:
            raise ValueError("expected a Word document content type")
        if [node.get("Target") for node in trees["_rels/.rels"] if node.get("Type") == OFFICE_REL
            ] not in (["word/document.xml"], ["/word/document.xml"]):
            raise ValueError("expected a package relationship to the Word body")
        document = trees["word/document.xml"]
        body = document.find(W + "body")
        if document.tag != W + "document" or body is None:
            raise ValueError("expected an editable Word body")
        forbidden = ("fldSimple", "instrText", "altChunk", "object", "control")
        for name, root in trees.items():
            for tag in forbidden:
                for node in root.iter(W + tag):
                    if not (tag == "fldSimple" and name.startswith("word/footer")
                            and node.get(W + "instr") == "PAGE"):
                        raise ValueError("unexpected field or executable content")

    def text(node):
        return "".join(child.text or "" for child in node.iter(W + "t"))

    paragraphs = [text(para) for para in body.iter(W + "p")]
    if not any(p.strip() for p in paragraphs) or any(p not in paragraphs for p in required_text):
        raise ValueError("required editable text is missing")
    if required_rows and not any(
        [[text(cell) for cell in row.findall(W + "tc")] for row in table.findall(W + "tr")]
        == required_rows for table in body.iter(W + "tbl")
    ):
        raise ValueError("required native table rows differ")


def assess(work, case, records, stop_reason=None, trace_error=None):
    turn = next((event for event in reversed(records) if event["type"] == "turn.completed"), None)
    items = [event["item"] for event in records if event["type"] == "item.completed"]
    commands = [item for item in items if item.get("type") == "command_execution"]
    failed = [item for item in commands
              if item.get("status") != "completed" or item.get("exit_code") != 0]
    reply = next((item.get("text") for item in reversed(items)
                  if item.get("type") == "agent_message"), None)
    smoke = case.get("smoke")
    fixture_access = None
    if smoke:
        fixture_access = any(
            item not in failed and case["fixture_name"] in str(item.get("command", ""))
            and isinstance(item.get("aggregated_output"), str)
            and smoke in item["aggregated_output"].splitlines() for item in commands
        )
    artifact = "NOT RUN"
    problems = []
    for name in case.get("artifacts", ()):
        if PurePosixPath(name).name != name or "\\" in name or ":" in name or not name.endswith(".docx"):
            raise ValueError("the runner requires a top-level DOCX artifact name")
        try:
            editable_report(work / name, case.get("required_text", ()), case.get("required_rows", ()))
        except (OSError, ValueError, BadZipFile, ET.ParseError, KeyError, RuntimeError) as exc:
            problems.append("missing artifact" if isinstance(exc, FileNotFoundError)
                            else "invalid artifact: " + type(exc).__name__ + (
                                " " + str(exc) if isinstance(exc, ValueError) else ""))
    if case.get("artifacts"):
        artifact = "FAIL" if problems else "PASS"
    for name in case.get("forbidden", ()):
        if (work / name).exists() or (work / name).is_symlink():
            problems.append("unexpected artifact")
    reason = stop_reason or trace_error or ("no completed turn" if not turn else None)
    if reason is None:
        if failed:
            reason = "terminal command failed"
        elif smoke and (not fixture_access or reply != smoke):
            reason = "missing exact fixture access or final reply"
        elif problems:
            reason = problems[0]
    if reason is None:
        status = "PASS" if smoke or case.get("artifacts") else "PARTIAL"
    else:
        status = "BLOCKED" if stop_reason or trace_error else "FAIL"
    usage = turn.get("usage") if turn else None
    if isinstance(usage, dict):
        usage = {key: usage[key] for key in
                 ("input_tokens", "cached_input_tokens", "cache_write_input_tokens",
                  "output_tokens", "reasoning_output_tokens")
                 if type(usage.get(key)) is int and usage[key] >= 0}
    successful = [item for item in commands if item not in failed]
    activation = "NOT RUN"
    if not smoke and turn:
        invoked = any(
            ".agents/skills/kmdstudio/scripts/generate.py" in
            str(item.get("command", "")).replace("\\", "/").casefold()
            for item in successful
        )
        activation = "PASS" if invoked and artifact == "PASS" else "PARTIAL"
    return {
        "status": status,
        "reason": reason,
        "turn_completed": turn is not None,
        "transport": "PASS" if not stop_reason else "BLOCKED",
        "trace": "PASS" if not trace_error else "BLOCKED",
        "task": "PASS" if status == "PASS" and (smoke or case.get("artifacts")) else (
            "FAIL" if status == "FAIL" else "NOT RUN"),
        "artifact": artifact,
        "activation": activation,
        "acceptance": status if smoke else "NOT RUN",
        "fixture_access": fixture_access,
        "usage": usage if isinstance(usage, dict) else None,
        "terminal_commands": len(commands),
        "failed_commands": len(failed),
        "mcp_calls": sum(item.get("type") == "mcp_tool_call" for item in items),
    }
