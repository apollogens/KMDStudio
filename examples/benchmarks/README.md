# Benchmark briefs

The 0.3.0rc1 candidate keeps these three regression fixtures and adds [an illustrated gallery guide, an algorithms guide, and a dispatch audit](visual-intelligence).

Generate the 0.2.0 versions from the project root with an available Python 3.11+ interpreter.

```powershell
foreach ($name in @('python-oop-lecture', 'workshop-status', 'read-the-street')) {
    python -E -s -B skills/kmdstudio/scripts/generate.py --root (Get-Location).Path --spec "examples/benchmarks/$name.json" --output "artifacts/$name-local.docx"
    if ($LASTEXITCODE) { exit $LASTEXITCODE }
}
```

The [original lecture](../python-oop-lecture.json) and [original workshop report](../workshop-status.json) supply the same text and page breaks. Their 0.1.0 outputs remain in [artifacts](../../artifacts). The current briefs change presentation and retain the original content, IDs, and criteria.

For the 0.1.0 editorial comparator, remove `chapter`, `role`, `tone`, `presentation`, and `checklist` from the relevant blocks of `read-the-street.json`. Keep the existing headings, text, rows, steps, and page breaks. Replace its design object with the following, then run the generator extracted from the [0.1.0 skill archive](../../artifacts/kmdstudio-0.1.0.zip).

```json
{
  "direction": "editorial",
  "palette": {"ink": "3F2541", "muted": "655366", "accent": "8B2D4E", "tint": "F7EDF1"},
  "typography": {"title_font": "Georgia", "body_font": "Arial", "code_font": "Consolas", "title_pt": 43, "body_pt": 11},
  "spacing": {"margin_mm": 24, "paragraph_pt": 9, "line_percent": 130},
  "footer": "Read the Street"
}
```

The new comparator is [read-the-street.docx](../../artifacts/v0.1.0/read-the-street.docx). Compare its content and page previews with the [0.2.0 artifacts](../../artifacts/v0.2.0). Use the [PDF safety contract](../../skills/kmdstudio/references/security.md) before repeating conversion.
