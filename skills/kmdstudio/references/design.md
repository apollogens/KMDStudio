# KMDStudio Design Language

Choose a direction for the reader and medium, then use the fewest overrides needed. Each profile uses the same editable components.

| Profile | Use when | Verify on the page |
| --- | --- | --- |
| `soft-education` | Learners need a friendly introduction with short explanations. | The green palette, serif titles, and highlighted definitions support a clear sequence. |
| `technical-modern` | Code and process diagrams do most of the explaining. | Navy headings, teal cues, and a separate code background remain legible in print. |
| `bold-editorial` | A guide or feature needs expressive typography and generous spacing. | The cover rule and serif titles establish hierarchy while multi-line paragraphs stay readable. |
| `business-premium` | A decision and its supporting evidence need quick scanning. | The muted palette, compact spacing, and aligned data put evidence and decision in reading order. |
| `creative-playful` | Younger or creative readers benefit from larger type and warmer cues. | Violet and warm accents support clearly labeled actions. |
| `swiss-minimal` | Structure and typography should carry the hierarchy. | Neutral colors and whitespace mark section boundaries and align related material. |

## Composition

| When | Action | Verify |
| --- | --- | --- |
| The title needs a dedicated opening | Use a cover with a clear label, short lead, and an optional relevant packaged mark. | The title dominates and the next page begins with content. |
| A new chapter changes the reader's task | Use a chapter heading and one lead paragraph. For theory, follow with plain text and a definition only where needed. | Heading levels appear in the outline and adjacent text stays with its heading. |
| A worked example explains behavior | Put the question first, then a captioned code block and a short result trace. | Copy the code and confirm indentation, glyphs, and example results. |
| Readers need to follow stages | Use a short diagram or native numbered steps and explain the sequence in words. | Labels, arrow direction, and reading order agree. |
| Readers must compare two alternatives | Use a comparison table with meaningful column headers and comparable entries. | Headers repeat and the longer column can wrap without hiding data. |
| Readers must apply or recall a concept | Give an exercise, ordered instructions, and a visible outcome. Use a checklist for checks and a takeaway for the conclusion. | The task can be completed from the document, including in grayscale. |

## Token decisions

| When | Action | Verify |
| --- | --- | --- |
| A default profile needs adjustment | Override semantic colors, type roles, spacing, or composition through `design.tokens`. Use compact, balanced, or spacious density to set starting intervals. | Inspect the actual A4 render and ensure the design does not crowd the content. |
| Foreground and background change together | Keep at least 4.5:1 for text, syntax, semantic cues, and panel text. Supply labels for color-coded meaning. | Resolve the brief through the CLI and check print legibility. This ratio checks color pairs only. |
| Latin and Cyrillic share a page | Use installed faces with both scripts. Arial and Georgia are practical starting faces and Consolas or Courier New works for code. | Inspect both scripts and code at reading scale. Font substitution and pagination are renderer-dependent. |
| An illustration supports understanding | Use a diagram, a table, or a reviewed packaged PNG. Give informative images a caption and relevant alternative text. | Compare the visual and its text equivalent with the source. |

The [schema](../schemas/document.schema.json) defines override keys and bounds. [Profile defaults](../scripts/design.py) are resolved by the generator. No fonts or illustration imports are required to use the profiles. The canvas background can depend on the viewer's rendering or print settings. KDL checks text colors on white as well as the chosen canvas color.

## Information and learning

| Card and occasion | Decision and supported controls | Avoid | Verify |
| --- | --- | --- | --- |
| D08 Evidence-first data, when readers need evidence | Use `table` for exact lookup and `column_alignments` for comparable numbers. Use `table.bars` for a same-unit nonnegative integer magnitude comparison on a common zero baseline. Show trend, distributions or part-to-whole with ordered rows, units and a plain-language interpretation when an editable table is sufficient. Use `diagram` for a short process and a keyed table or prose for relationships. An exact specialized plot needs separately approved deterministic artwork and a native text equivalent. | Bars on totals, mixed units or trend data. The native diagram expresses ordered stages, with no arbitrary graph layout. | Recalculate totals and scale independently. Check ordering, units, bar proportions and labels. Confirm that the table or accompanying text communicates the result without color. |
| D09 Learning sequence, when teaching a procedure or concept | Use an objective in a `paragraph`, a worked example next to a `diagram` or `table`, then a guided `exercise` and independent practice followed by feedback. Put the learner's first task before the listing. | Art unrelated to the lesson or a worked example and its interpretation on disconnected pages. | Trace the example against the source and perform the exercise using the stated feedback. Check that the visual sits near the step it explains. |
| D10 Technical quiet zone, when editorial pages include exact material | Use native `code`, `table`, ordered `list` or `diagram` outside continuous columns. Keep formulas as exact native text where that representation is adequate. Set `monospace_font`, align comparable numeric columns and explain each dependency in reading order. | Rasterizing exact content or styling code as display. Equation layout and rich technical graphs have no specialized editable primitive. | Compare copied content character by character, including indents and operators. Check header semantics, glyphs, line wrapping and result values. |
