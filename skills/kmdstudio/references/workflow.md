# Brief and local workflow

The [JSON Schema](../schemas/document.schema.json) describes the authoring shape. The Python validator enforces the same structural subset and checks cross-field invariants. A generator run uses a trusted project directory and distinct relative paths under it. Create the output parent first. The generator refuses overwrites.

```powershell
python -E -s -B skills/kmdstudio/scripts/generate.py --root (Get-Location).Path --spec examples/python-oop-lecture.json --output artifacts/draft.docx
python -E -s -B skills/kmdstudio/scripts/render_pdf.py --root (Get-Location).Path --spec examples/python-oop-lecture.json --output artifacts/draft.pdf --renderer 'C:/trusted/LibreOffice/program/soffice.com'
```

The PDF command requires [the pinned optional package](../requirements-pdf.lock) and host containment. It builds and verifies its input again in an isolated temporary working directory. For ordinary generation, invoke only the format commands the user requested. A visual review and a user-facing publication decision remain separate from either command's structural result.

## Brief fields

- `purpose`, `audience`, `language`, `title`, and optional `subtitle` describe the assignment. A language such as `ru-RU` also sets the Word proofing language.
- `design.profile` selects a KDL visual direction. Optional `density`, `tokens`, `header`, and `footer` refine it. Tokens override the resolved profile and density values. Use the schema for bounds and [Design](design.md) for selection rules.
- `formats` lists DOCX, PDF, or both in lowercase. `acceptance.required_ids` binds source commitments to `blocks`. Give each block a different lowercase ID. Use acceptance criteria for the page count, content, readability, and audience needs that a reviewer can observe.
- Blocks appear in reading order. A cover comes first and separates itself from subsequent content. Use level 1 and 2 headings in order. Set `chapter: true` on a level-1 heading for a ruled introduction. Set `new_page: true` only for an intentional page boundary after content.
- `paragraph.role` can be `lead`, `note`, or `emphasis`. `callout.tone` can be `definition`, `info`, `success`, `warning`, or `takeaway`. Meaning should be explicit in the text. For a printable checklist, use `list` with `ordered: false` and `checklist: true`.
- Use `table.column_weights` for proportional column sizes. `presentation: "comparison"` requires two columns. A figure uses a manifest asset ID, meaningful alternative text, and a caption. Diagrams remain editable sequences with short labels and text. Code accepts `python` or `text` and preserves indentation and tabs.

```json
{
  "profile": "technical-modern",
  "density": "balanced",
  "tokens": {"typography": {"code_pt": 11}, "spacing": {"margin_mm": 23}},
  "footer": "Python workshop"
}
```

Existing `version: 1` briefs with `design.direction`, `palette`, `typography`, and `spacing` remain accepted. Those values retain their color, font, and spacing roles. Shared component refinements can change pagination. To adopt KDL, replace the design object with a profile and add only the overrides required for the document. Keep all content, IDs, and acceptance criteria.

Treat accepted source text as ready for typesetting. For corrections, save a new version of the brief and generate to a new filename. Verify the newly generated artifact before choosing a delivery file.
