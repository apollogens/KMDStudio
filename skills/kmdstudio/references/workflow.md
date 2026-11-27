# Brief and local workflow

The optional `mode` is `structured`, `creative`, or `hybrid`. An absent mode preserves the existing structured workflow. Resolve `auto` in host planning before generation. Use the [creative direction guide](creative.md) for creative and hybrid controls and font declarations.

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
- Use `layout.columns` for ordered ranges of at least two flowing blocks. Each range uses inclusive `from` and `through` IDs. Leave a full-width block between ranges. Keep any leading heading and its following text together within the range. See [Planning](planning.md) for width and reading order.
- A cover can include one `illustration` with `asset`, `alt`, `caption` and `width_mm`. Use a short cover lead. A figure can use `side_text` for one short paragraph before the inline image in a 60:40 composition. The usual manifest or packaged asset rules apply to both.
- `paragraph.role` can be `lead`, `note`, or `emphasis`. `callout.tone` can be `definition`, `info`, `success`, `warning`, or `takeaway`. Meaning should be explicit in the text. For a printable checklist, use `list` with `ordered: false` and `checklist: true`.
- Use `table.column_weights` for proportional column sizes. `presentation: "comparison"` requires two columns. Follow [Illustrations](illustrations.md) for figure width, alignment, captions, and alternative text. Diagrams remain editable sequences with short labels and text. Code accepts `python` or `text` and preserves indentation and tabs.
- Use `keep_lines: true` on a paragraph of up to 640 characters that needs to stay intact. Use `keep_rows: true` on a short table with at most three data rows and 900 total cell characters. Leave wide prose, code and dense tables free to flow across pages.

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
