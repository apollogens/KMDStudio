# Codex evaluation

Use a standalone, authorized Codex CLI session with local workspace tools and the same discoverable Python interpreter for all configurations. Configure model access through the normal host. The runner uses fresh workspaces outside the repository. It checks the ordinary configuration for existing KMDStudio discovery entries. The second configuration installs the hash-verified 0.2.0 ZIP at the discovery path. The third installs the current reviewed source. Model, reasoning, case, fixture, sandbox, approval mode, and timeout are shared. Prompts and fixtures are synthetic and may be sent to the model host.

```powershell
python -E -s -B evals/run.py --codex (Get-Command codex).Source --model gpt-5.6-sol --reasoning low --smoke-only
python -E -s -B evals/run.py --codex (Get-Command codex).Source --model gpt-5.6-sol --reasoning low --case controlled-report-en --timeout 180
```

The smoke gives the model 45 seconds to read a one-line fixture and return the exact value. Only a completed turn with trace evidence of a terminal command and the expected reply unlocks the comparison. The controlled one-page report allows up to 180 seconds per variant for tool use, editable artifact generation, and inspection. The runner makes a single attempt per variant and stops expanding cases after an incomplete comparison. It keeps raw traces under the ignored `.tools` directory and prints the local paths to retained workspaces.

Score each expected outcome in [cases.json](cases.json) as PASS, FAIL, or NOT OBSERVABLE. Check explicit, implicit and negative activation through trace evidence. Record actual tool calls, source matches, native Word structures, unrelated writes or transfers, artifact validity, corrections, elapsed time, and available token usage. Use blinded rendered comparisons for visual judgment. Evaluate matched outcomes before generalizing. The [candidate verification record](../docs/VERIFICATION-v0.3.0rc1.md) documents the unfinished local pilot. [OpenAI skill evaluation guidance](https://developers.openai.com/blog/eval-skills) and [Codex workflow iteration](https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex)
