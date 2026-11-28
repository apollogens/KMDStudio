# Typography evidence

Use the smallest verified family set that gives distinct display, heading, body, caption, metadata and code roles. Record each requested family and weight, the concrete face available to the renderer, the generator's choice and the font observed in rendered text. A regular and bold family pairing is usually easier to verify than variable weight instances across applications.

Ask the authorized host for an installed font inventory or an exact-family glyph check. Check the scripts in the brief, digits and decimal marks, and exact technical or code symbols. Record missing glyphs rather than assuming the whole alphabet or symbols are available. A family declared by the operator may still be substituted by Word or Writer. When possible, inspect actual glyphs on pages and the fonts reported by the application's diagnostic output. Never infer renderer availability from OOXML alone.

With no confirmed open family, choose an available installed face independently for each role or let the generator resolve its documented aliases. Inter, Manrope, Golos Text, Onest and IBM Plex Sans fall back to Arial. Literata falls back to Georgia and JetBrains Mono to Consolas. Use `--available-font FAMILY` on creative and hybrid runs after checking the applicable renderer, actual regular and bold, and script coverage. Repeat the flag for multiple confirmed optional families and use the same options when regenerating. The CLI reports generator substitutions. Structured defaults retain their existing behavior.

For a custom face, request operator approval for the source, exact version and environment. Document license conditions, glyph coverage, resolved weight and renderer evidence. Font acquisition and preparation take place outside DOCX generation. The core passes family names and weights only and does not embed files. Retain a portable alternative when the target system differs.

## Design decisions

| Card and occasion | Decision and supported controls | Avoid | Verify |
| --- | --- | --- | --- |
| D04 Typographic contrast, when the document needs a distinct voice | Choose one pronounced change between `display_font`, `display_pt`, `display_weight` and the body roles. Use `display_tracking_twips` for a short checked title and `metadata_tracking_twips` for brief labels. Adjust `body_line_percent`, available width and `spacing.paragraph_pt` together. Keep code in `monospace_font`. | Using display scale for prose, stretching long labels or assuming a named family yields a real weight. | Read at actual size. Check title wraps, body line measure, both scripts, and the renderer's effective faces. |
| D14 Constraint-aware fallback, when a face is absent or layout wraps badly | Use the generator's fallback or a checked installed family. Restore hierarchy with size and spacing. Use ordinary serial blocks if a width-sensitive region fails. | Embedding an unreviewed font, rasterizing the page or forcing alignment with spaces. | Record requested, resolved and effective families. Verify natural reading order, exact text, editability and the revised rendered page. |

For a new optional family, have the operator obtain only the reviewed revision and preserve its license and digest. Check real regular and bold instances, needed glyphs and embedding flags with the host inventory. Render representative Latin, Cyrillic and code samples in the target viewer. Enable the family only after it passes. Keep renderer substitutions visible in the review record.
