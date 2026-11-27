# Codex evaluation

Open a separately authorized standalone Codex CLI session with working local shell access. Use the same account, tools, model settings, Python command, sandbox and approval mode for every arm. The runner uses `workspace-write` with approval mode `never`. It retains host rules and uses ephemeral sessions with user config ignored. Use a clean evaluation account or host when its global, plugin or ancestor skill discovery paths already expose KMDStudio. Directory checks cover the conventional paths. Verify the actual skill list for any additional organization or system discovery channels before judging the ordinary arm.

```powershell
python -E -s -B evals/run.py --codex (Get-Command codex).Source --model gpt-5.6-sol --reasoning low --smoke-only
$archive = 'artifacts/v0.4.0rc1/kmdstudio-0.4.0rc1.zip'
$sha = (Get-FileHash -LiteralPath $archive).Hash.ToLowerInvariant()
python -E -s -B evals/run.py --codex (Get-Command codex).Source --model gpt-5.6-sol --reasoning low --case controlled-report-en --candidate $archive --candidate-sha256 $sha
```

The second command sequence includes its own smoke gate. Use it by itself when ready for the comparison. Use `--smoke-only` to qualify a standalone host. The 45-second probe writes a random filename and 128-bit value in a fresh workspace. It requires a successful shell command naming the file and returning the value in command output, followed by an exact final reply. Transport, JSONL integrity, completed turn, task, artifact, activation, and acceptance have distinct statuses. A failed probe stops the three-arm run. Change the host or tool configuration before trying again.

The comparison installs the hash-pinned 0.3.0rc1 and current verified archives under the same discovery path in separate workspaces. The ordinary workspace receives no package. Each arm gets the same frozen [controlled case](cases.json) and 180 seconds by default. The preliminary gate checks exact editable title, decision and table values, plus bounded package structure and absence of external relationships and selected active content. A successful packaged CLI invocation is activation evidence. Verify intended selection and security behavior across the complete trace. Other listed cases need their own artifact and manual rubrics before scoring.

Reviewers should inspect anonymized page images and score hierarchy, composition and the relevance and clarity of the progress illustration against the frozen criteria. Record approvals, unrelated reads or writes, external calls, corrections, duration and available token usage. A preliminary task PASS leaves manual acceptance open. Keep raw traces and workspaces local. Trace capture is capped at 2 MiB on stdout and 128 KiB on stderr. Timeout and capture failures trigger process-group or Windows process-tree termination. The runner reports an unconfirmed cleanup when termination cannot be verified. Retain or remove the per-run workspace and evidence directory under the host's retention policy.
