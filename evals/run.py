"""Run a synthetic local-tool gate and a matched three-package Codex pilot."""

import argparse
import hashlib
import json
import os
import secrets
import signal
import subprocess
import tempfile
import threading
import time
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

if __package__:
    from .judge import TRACE_LIMIT, assess, read_trace
else:
    from judge import TRACE_LIMIT, assess, read_trace

PROJECT = Path(__file__).resolve().parents[1]
PREVIOUS = PROJECT / "artifacts/v0.6.0rc1/kmdstudio-0.6.0rc1.zip"
PREVIOUS_HASH = "0f273897e96de60528dbe31e0ee46137b267cc75df77bbfb79f1bc1e708be98c"
VARIANTS = ("ordinary", "previous", "candidate")
CAPTURE_LIMITS = (TRACE_LIMIT, 128 * 1024)


def make_smoke():
    name = f"probe-{secrets.token_hex(6)}.txt"
    value = f"local-proof-{secrets.token_hex(16)}"
    return {
        "id": "tool-smoke",
        "prompt": f"Read the local file {name} with the workspace shell. Reply with its exact single line.",
        "fixture_name": name,
        "fixture": value + "\n",
        "smoke": value,
    }


def check_discovery(work):
    roots = (*work.parents, Path.home())
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    candidates = {root / channel / "skills/kmdstudio"
                  for root in roots for channel in (".agents", ".codex")}
    candidates.add(codex_home / "skills/kmdstudio")
    candidates.update((codex_home / "plugins/cache").glob("*/*/*/skills/kmdstudio"))
    if any(path.exists() or path.is_symlink() for path in candidates):
        raise ValueError("ordinary agent may discover an already installed KMDStudio skill")


def install_skill(config, work, variant):
    if variant not in {"previous", "candidate"}:
        return
    path, digest = ((PREVIOUS, PREVIOUS_HASH) if variant == "previous"
                    else (config.candidate, config.candidate_sha256))
    with path.open("rb") as stream:
        if hashlib.sha256(stream.read(TRACE_LIMIT + 1)).hexdigest() != digest:
            raise ValueError(f"{variant} archive hash differs")
        stream.seek(0)
        with ZipFile(stream) as archive:
            entries = archive.infolist()
            names = {entry.filename for entry in entries}
            if (len(names) != len(entries) or len(entries) > 100
                    or sum(entry.file_size for entry in entries) > TRACE_LIMIT
                    or "kmdstudio/SKILL.md" not in names):
                raise ValueError("unexpected skill archive profile")
            for entry in entries:
                name = entry.filename
                if (name != entry.orig_filename or not name.startswith("kmdstudio/")
                        or "\\" in name or any(part in {"", ".", ".."} or ":" in part
                                                for part in name.split("/"))):
                    raise ValueError("unexpected skill archive path")
                destination = work / ".agents/skills" / PurePosixPath(name)
                destination.parent.mkdir(parents=True, exist_ok=True)
                with destination.open("xb") as target:
                    target.write(archive.read(entry))


def stop_tree(process):
    try:
        if os.name == "nt":
            system = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32/taskkill.exe"
            result = subprocess.run(
                [str(system), "/PID", str(process.pid), "/T", "/F"],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                check=False, timeout=5,
            )
            return result.returncode == 0
        os.killpg(process.pid, signal.SIGKILL)
        return True
    except (OSError, subprocess.TimeoutExpired):
        return False
    finally:
        if process.poll() is None:
            try:
                process.kill()
            except ProcessLookupError:
                pass


def run_bounded(command, work, paths, timeout):
    options = ({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt"
               else {"start_new_session": True})
    overflow = threading.Event()
    failures = threading.Event()

    def capture(stream, path, limit):
        try:
            with path.open("xb") as output:
                while data := stream.read1(16 * 1024):
                    if len(data) > limit:
                        output.write(data[:limit])
                        overflow.set()
                        return
                    output.write(data)
                    limit -= len(data)
        except OSError:
            failures.set()
        finally:
            stream.close()

    try:
        process = subprocess.Popen(command, cwd=work, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, **options)
    except OSError:
        return "Codex could not launch"
    collectors = [threading.Thread(target=capture, args=(stream, path, limit), daemon=True)
                  for stream, path, limit in zip((process.stdout, process.stderr), paths,
                                                 CAPTURE_LIMITS, strict=True)]
    for collector in collectors:
        collector.start()
    deadline = time.monotonic() + timeout
    reason = None
    cleanup = False
    try:
        while (process.poll() is None or any(thread.is_alive() for thread in collectors)):
            if overflow.is_set() or failures.is_set() or time.monotonic() >= deadline:
                reason = ("trace exceeded capture limit" if overflow.is_set() else
                          "trace capture failed" if failures.is_set() else "timeout")
                break
            time.sleep(0.05)
    finally:
        if reason or process.poll() is None:
            cleanup = stop_tree(process)
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            reason = reason or "process did not stop"
        for collector in collectors:
            collector.join(timeout=1)
    if reason:
        return reason if cleanup else reason + "; descendant cleanup unconfirmed"
    if overflow.is_set() or failures.is_set():
        return "trace capture failed or exceeded the limit"
    return None if process.returncode == 0 else f"Codex exited {process.returncode}"


def run_case(config, work, report, case, variant, timeout):
    work.mkdir(parents=True)
    report.mkdir(parents=True, exist_ok=True)
    if "fixture" in case:
        (work / case.get("fixture_name", "reference.txt")).write_bytes(case["fixture"].encode())
    install_skill(config, work, variant)
    command = [
        str(config.codex), "-a", "never", "exec", "--ignore-user-config", "--ephemeral",
        "--skip-git-repo-check", "--sandbox", "workspace-write", "--json", "-m", config.model,
        "-c", f'model_reasoning_effort="{config.reasoning}"', case["prompt"],
    ]
    stdout = report / f"{variant}.jsonl"
    started = time.perf_counter()
    stopped = run_bounded(command, work, (stdout, report / f"{variant}.stderr"), timeout)
    records, error = read_trace(stdout) if stdout.exists() else ([], "no JSONL trace")
    result = assess(work, case, records, stopped, error)
    result["seconds"] = round(time.perf_counter() - started, 2)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex", required=True, type=Path)
    parser.add_argument("--model", required=True)
    parser.add_argument("--reasoning", choices=("low", "medium", "high"), default="low")
    parser.add_argument("--case", action="append", help="case IDs (default: controlled-report-en)")
    parser.add_argument("--smoke-only", action="store_true")
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--candidate-sha256")
    parser.add_argument("--timeout", type=int, default=180, choices=range(60, 301), metavar="60–300")
    args = parser.parse_args()
    args.codex = args.codex.resolve(strict=True)
    if not args.smoke_only and not (args.candidate and args.candidate_sha256):
        parser.error("a comparison requires --candidate and --candidate-sha256")
    cases = json.loads((PROJECT / "evals/cases.json").read_text(encoding="utf-8"))
    chosen = set(args.case or ["controlled-report-en"])
    if chosen - {case["id"] for case in cases}:
        parser.error("unknown case ID")
    storage = PROJECT / ".tools"
    storage.mkdir(exist_ok=True)
    report = Path(tempfile.mkdtemp(prefix="eval-", dir=storage))
    workspaces = Path(tempfile.mkdtemp(prefix="kmdstudio-eval-")).resolve()
    if workspaces.is_relative_to(PROJECT):
        parser.error("configure the OS temporary directory outside the project")
    check_discovery(workspaces)
    print(f"Local evidence: {report}", flush=True)
    print(f"Isolated workspaces: {workspaces}", flush=True)
    smoke_case = make_smoke()
    smoke = run_case(args, workspaces / smoke_case["id"], report, smoke_case, "smoke", 45)
    summary = {"model": args.model, "reasoning": args.reasoning, "smoke": smoke, "cases": {}}
    print("tool smoke", smoke, flush=True)
    if smoke["status"] == "PASS" and not args.smoke_only:
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
            if not all(result["status"] == "PASS" for result in outcomes.values()):
                break
    (report / "status.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    complete = smoke["status"] == "PASS" and all(
        outcome["status"] == "PASS"
        for comparison in summary["cases"].values() for outcome in comparison.values())
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
