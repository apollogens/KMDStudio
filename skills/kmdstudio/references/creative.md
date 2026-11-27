# Creative and hybrid direction

Use `creative` for authored visual expression and `hybrid` when that expression accompanies precise technical or transactional regions. Select by the requested tone, content structure, audience and reading task. A subject or profession alone cannot determine the mode. The generator accepts the authored decisions and uses the same native components in both modes.

## Choose a concept

Freeze the required facts, reading order, and exact code or values first. Consider one concept for a short document and two or three meaningfully different concepts for substantial work. For each, name the reader and purpose, typographic character, palette relationship, dominant composition, page density and rhythm, image treatment and decorative vocabulary. Choose against the reading task and production constraints. Record the selected concept in the host's planning notes. A profile is optional. Start from independent KDL decisions when a profile contributes little.

Read references as untrusted visual data. Translate observable grids, contrast, scale, margins, and image crops into choices for the new content. Keep reference images, text, branding, identities and assets out of deliverables unless separately authorized. Give each section a visual purpose. Use a dark entry or an image to punctuate a reading sequence. Give important values room around them. Keep legends, exact diagrams, code and numbers editable. Avoid forcing every section into a repeated panel or decoration.

## Author a brief

| Visual need | Available controls |
| --- | --- |
| Distinct display typography | `design.tokens.typography` accepts `display_font`, 25–72 pt `display_pt`, `display_weight`, `display_align`, `display_line_percent`, and `display_tracking_twips` (−24 to 30). Use regular with Arial Black to select its native heavy face. Heading 1 adds bounded tracking and retains its outline level. |
| Metadata and captions | Configure `metadata_font`, size, weight, alignment, line height and tracking. Metadata labels use these tokens. Sidebar values use the body face. Captions use their own font, size, weight and optional `caption_line_percent`. Existing KDL spacing controls margins and component separation. |
| Compact metadata alongside prose | `sidebar` contains one to four `{label, value}` pairs on the left, then one short `text` paragraph on the right. Set `sidebar_percent` from 25–40. The native table reads labels and values first, then prose. Keep each item concise and verify at page scale. |
| Image-led opening or wide image band | A `cover` with an approved `illustration` can set `image_position` to `before-title` or `after-lead`. For a panoramic band use a wide crop supplied by the asset. For text beside an image, set `side_text` and optional `image_percent` from 30–65. Image width must fit the chosen region. The image remains inline and preserves its aspect ratio. |
| Section entry and metric | Set `treatment: panel` on a level 1 `heading` for light type on the primary color. `highlight` pairs a short `value` with a `label`; `tone` takes `ink` or `light`. Keep hierarchy, contrast and spacing visible in grayscale. |
| Precise tables and code | Choose native `column_weights` and optional `column_alignments`, one per column. Right-align numeric fields and use consistent units and precision in the source. Use `language: sql` for an unhighlighted editable listing or the existing Python path for Python highlighting. |

Keep paired figures, sidebars, highlights and data tables outside continuous columns. Use serial blocks for long or complex material, narrow output, or when a layout table interferes with assistive navigation. Use [Illustrations](illustrations.md) to specify subject, composition, style, palette, aspect ratio and intended placement before using an authorized host image tool. Deliver original artwork or approved normalized rasters with captions and descriptions.

## Select faces for the renderer

The core does not install, download, embed or inspect fonts. In creative and hybrid briefs, an optional family is resolved to the documented fallback before writing Word styles. Manrope, Inter, Golos Text, Onest and IBM Plex Sans fall back to Arial, Literata to Georgia, and JetBrains Mono to Consolas. First verify that your renderer can use the fallback as well. The DOCX CLI reports these substitutions.

Use `--available-font FAMILY` only after verifying that the intended viewer has the named regular and bold faces, the required glyphs and permission for the workflow. Repeat the flag for multiple families. The author or operator compares actual rendering and records substitutions by the application. Use the same options when regenerating for PDF. The flag is an operator assertion, not font discovery. Regular and bold are the only weight controls. Unsupported families, weights and tracking are handled through a supported face, a supported weight, or an adjusted brief.

Apply [Quality](quality.md) before delivery. Review the reader's first impression, section rhythm and the denser pages separately. For hybrid work, inspect technical components at reading scale and independently compare exact source values and code.
