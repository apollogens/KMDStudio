# Paired Codex evaluation

The runner gives each synthetic case a fresh workspace. The enabled workspace contains the reviewed skill at the Codex discovery path. Baseline contains the same prompt and fixture. Use the same Codex version, model, host policy, and discoverable Python interpreter for both runs. Configure model access through the normal Codex host before running. This can use the hosted model and sends the synthetic prompt and fixture to that host.

```powershell
& '.venv/Scripts/python.exe' -E -s -B evals/run.py --codex (Get-Command codex).Source
```

Use `--case <id>` for a pilot. The runner writes isolated workspaces and traces under `.tools`. Review trace evidence, files produced, and visual quality where supported. For each expected outcome in [cases.json](cases.json), score PASS, FAIL, or NOT OBSERVABLE with a brief artifact or trace reference. Compare matched outcomes by case across configurations. A completed process is not evidence of skill activation, correctness, or quality. An unavailable evaluator or failed authorization is NOT RUN for the affected cases.
