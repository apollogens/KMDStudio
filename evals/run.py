"""Run synthetic paired Codex cases and preserve raw evidence for scoring."""

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]


def run_case(executable, root, case, variant):
    work = root / case["id"] / variant
    work.mkdir(parents=True)
    if "fixture" in case:
        (work / "reference.txt").write_text(case["fixture"], encoding="utf-8")
    if variant == "enabled":
        folder = work / ".agents" / "skills" / "kmdstudio"
        shutil.copytree(PROJECT / "skills/kmdstudio", folder,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    args = [
        str(executable), "exec", "--ephemeral", "--skip-git-repo-check", "--sandbox",
        "workspace-write", "--json", case["prompt"],
    ]
    stdout = work.parent / f"{variant}.jsonl"
    stderr = work.parent / f"{variant}.stderr"
    with stdout.open("wb") as events, stderr.open("wb") as errors:
        try:
            result = subprocess.run(args, cwd=work, stdin=subprocess.DEVNULL,
                                    stdout=events, stderr=errors, timeout=150, shell=False,
                                    check=False)
        except subprocess.TimeoutExpired:
            return "NOT RUN: timeout"
    if result.returncode != 0:
        return f"NOT RUN: Codex exited {result.returncode}"
    records = stdout.read_text(encoding="utf-8").splitlines()
    if not any(json.loads(line).get("type") == "turn.completed" for line in records if line.strip()):
        return "NOT RUN: no completed turn"
    return "COMPLETED: evaluate artifacts and trace against rubric"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex", required=True, type=Path)
    parser.add_argument("--case", action="append", help="run only these case IDs")
    args = parser.parse_args()
    executable = args.codex.resolve(strict=True)
    cases = json.loads((PROJECT / "evals/cases.json").read_text(encoding="utf-8"))
    if args.case and set(args.case) - {case["id"] for case in cases}:
        parser.error("unknown case ID")
    storage = PROJECT / ".tools"
    storage.mkdir(exist_ok=True)
    report = Path(tempfile.mkdtemp(prefix="eval-", dir=storage))
    statuses = {}
    for case in cases:
        if args.case and case["id"] not in args.case:
            continue
        statuses[case["id"]] = {}
        for variant in ("baseline", "enabled"):
            outcome = run_case(executable, report, case, variant)
            print(case["id"], variant, outcome, flush=True)
            statuses[case["id"]][variant] = outcome
        if all(status.startswith("NOT RUN") for status in statuses[case["id"]].values()):
            break
    (report / "status.json").write_text(json.dumps(statuses, indent=2) + "\n", encoding="utf-8")
    print(report)
    return 0 if any(status.startswith("COMPLETED") for pair in statuses.values()
                    for status in pair.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
