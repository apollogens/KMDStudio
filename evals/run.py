"""Run bounded synthetic Codex cases with ordinary, previous and candidate workspaces."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from zipfile import ZipFile

PROJECT = Path(__file__).resolve().parents[1]
PREVIOUS = PROJECT / "artifacts/v0.2.0/kmdstudio-0.2.0.zip"
PREVIOUS_HASH = "c42e8fd52f4ecafd7a040f1c09126f786628685f2cc80b14cb95fe37a450eb8b"
VARIANTS = ("ordinary", "previous", "candidate")
SMOKE = {
    "id": "tool-smoke",
    "prompt": "Read reference.txt with a workspace tool. Reply with its exact single line.",
    "fixture": "KMDSTUDIO-TOOL-SMOKE-47",
}


def check_discovery(work):
    roots = (*work.parents, Path.home())
    candidates = {root / channel / "skills/kmdstudio"
                  for root in roots for channel in (".agents", ".codex")}
    if codex_directory := os.environ.get("CODEX_HOME"):
        candidates.add(Path(codex_directory) / "skills/kmdstudio")
    if any(path.exists() or path.is_symlink() for path in candidates):
        raise ValueError("ordinary agent may discover an already installed KMDStudio skill")


def install_skill(work, variant):
    if variant == "candidate":
        shutil.copytree(PROJECT / "skills/kmdstudio", work / ".agents/skills/kmdstudio",
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    elif variant == "previous":
        if hashlib.sha256(PREVIOUS.read_bytes()).hexdigest() != PREVIOUS_HASH:
            raise ValueError("previous skill archive hash differs from verification record")
        with ZipFile(PREVIOUS) as archive:
            archive.extractall(work / ".agents/skills")


def run_case(config, work, report, case, variant, timeout):
    work.mkdir(parents=True)
    report.mkdir(parents=True, exist_ok=True)
    if "fixture" in case:
        (work / "reference.txt").write_text(case["fixture"], encoding="utf-8")
    install_skill(work, variant)
    command = [
        str(config.codex), "-a", "never", "exec", "--ignore-user-config", "--ephemeral",
        "--skip-git-repo-check", "--sandbox", "workspace-write", "--json", "-m", config.model,
        "-c", f'model_reasoning_effort="{config.reasoning}"', case["prompt"],
    ]
    stdout = report / f"{variant}.jsonl"
    stderr = report / f"{variant}.stderr"
    started = time.perf_counter()
    with stdout.open("wb") as events, stderr.open("wb") as errors:
        try:
            result = subprocess.run(command, cwd=work, stdin=subprocess.DEVNULL,
                                    stdout=events, stderr=errors, timeout=timeout, check=False)
            stopped = None if result.returncode == 0 else f"Codex exited {result.returncode}"
        except subprocess.TimeoutExpired:
            stopped = "timeout"
    elapsed = round(time.perf_counter() - started, 2)
    records = []
    for line in stdout.read_bytes().splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except (UnicodeDecodeError, json.JSONDecodeError):
            stopped = stopped or "incomplete JSONL trace"
            break
    completed = next((event for event in reversed(records)
                      if event.get("type") == "turn.completed"), None)
    items = [event["item"] for event in records if event.get("type") == "item.completed"]
    summary = {
        "status": "COMPLETED" if completed and not stopped else "NOT RUN",
        "reason": stopped or (None if completed else "no completed turn"),
        "turn_completed": completed is not None,
        "seconds": elapsed,
        "usage": completed.get("usage") if completed else None,
        "terminal_commands": sum(item.get("type") == "command_execution" for item in items),
        "failed_commands": sum(item.get("type") == "command_execution"
                               and item.get("status") == "failed" for item in items),
        "mcp_calls": sum(item.get("type") == "mcp_tool_call" for item in items),
    }
    if case == SMOKE:
        reply = any(item.get("type") == "agent_message" and item.get("text") == SMOKE["fixture"]
                    for item in items)
        if not summary["terminal_commands"] or not reply:
            summary.update(status="NOT RUN", reason=stopped or "missing smoke tool or reply evidence")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex", required=True, type=Path)
    parser.add_argument("--model", required=True)
    parser.add_argument("--reasoning", choices=("low", "medium", "high"), default="low")
    parser.add_argument("--case", action="append", help="case IDs (default: controlled-report-en)")
    parser.add_argument("--smoke-only", action="store_true")
    parser.add_argument("--timeout", type=int, default=180, choices=range(60, 301),
                        metavar="60–300")
    args = parser.parse_args()
    args.codex = args.codex.resolve(strict=True)
    cases = json.loads((PROJECT / "evals/cases.json").read_text(encoding="utf-8"))
    chosen = set(args.case or ["controlled-report-en"])
    if chosen - {case["id"] for case in cases}:
        parser.error("unknown case ID")
    storage = PROJECT / ".tools"
    storage.mkdir(exist_ok=True)
    report = Path(tempfile.mkdtemp(prefix="eval-", dir=storage))
    workspaces = Path(tempfile.mkdtemp(prefix="kmdstudio-eval-"))
    if workspaces.is_relative_to(PROJECT):
        parser.error("configure the OS temporary directory outside the project")
    check_discovery(workspaces)
    print(f"Local evidence: {report}", flush=True)
    print(f"Isolated workspaces: {workspaces}", flush=True)
    smoke = run_case(args, workspaces / SMOKE["id"], report, SMOKE, "smoke", 45)
    summary = {"model": args.model, "reasoning": args.reasoning, "smoke": smoke, "cases": {}}
    print("tool smoke", smoke, flush=True)
    if smoke["status"] == "COMPLETED" and not args.smoke_only:
        for case in cases:
            if case["id"] not in chosen:
                continue
            outcomes = {}
            for variant in VARIANTS:
                outcome = run_case(args, workspaces / case["id"] / variant, report / case["id"],
                                   case, variant, args.timeout)
                print(case["id"], variant, outcome, flush=True)
                outcomes[variant] = outcome
            summary["cases"][case["id"]] = outcomes
            if not all(result["status"] == "COMPLETED" for result in outcomes.values()):
                break
    (report / "status.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    complete = smoke["status"] == "COMPLETED" and all(
        outcome["status"] == "COMPLETED"
        for comparison in summary["cases"].values() for outcome in comparison.values())
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
