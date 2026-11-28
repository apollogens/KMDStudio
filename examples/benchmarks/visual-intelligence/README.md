# Visual intelligence benchmarks

These synthetic sources and required block IDs were fixed before the first generation. The algorithm guide's final changes are limited to KDL design tokens. Its listing and acceptance criteria are identical to the first render.

| Fixture | Acceptance evidence |
| --- | --- |
| [Reading the Surface](reading-the-surface.json) | The approved illustration appears at 146 mm wide with an editable caption, exact alternative text, and observation prompts on one page. |
| [Find the First Match](binary-search-boundaries.json) | The editable 40-line listing retains every character, with a longest line of 92 characters. Its three-step trace and exercise remain native Word text. |
| [Dispatch Readiness](dispatch-readiness.json) | Two native five-column tables contain 32 rows with repeating header definitions. The counts reconcile to 1,725 planned and 1,699 actual, with five batches under review. |

## Generate the documents

From the repository root with Python 3.11+ on PATH, using new output names.

```powershell
$fixture = 'examples/benchmarks/visual-intelligence'
$generator = 'skills/kmdstudio/scripts/generate.py'
$manifest = "$fixture/assets/study-vessel.json"
$approvedHash = '88404121fb734716791c3b328036b4a954fada5e7e6880eda91fce828d7057cf'
python -E -s -S -B $generator --root (Get-Location).Path --spec "$fixture/reading-the-surface.json" --output artifacts/gallery-local.docx --asset-manifest $manifest --asset-manifest-sha256 $approvedHash
python -E -s -S -B $generator --root (Get-Location).Path --spec "$fixture/binary-search-boundaries.json" --output artifacts/algorithm-local.docx
python -E -s -S -B $generator --root (Get-Location).Path --spec "$fixture/dispatch-readiness.json" --output artifacts/dispatch-local.docx
```

The [candidate evidence](../../../docs/VERIFICATION-v0.3.0rc1.md) includes review reproduction and checksums. The [deliverables](../../../artifacts/v0.3.0rc1) include DOCX and print-scale previews.

## Illustration provenance

The built-in OpenAI ImageGen tool produced a 1536 × 1024 PNG. It depicts an original fictional vessel. The raw image was imported from the approved local workspace with `--id local-study-vessel --origin host-generated`. The preserved [receipt](assets/study-vessel.json) records the input and normalized SHA-256 values. The [normalized PNG](assets/study-vessel.png) is 864 × 576, uses 664,776 bytes, and contains only image header, pixel and end chunks. This file and the pinned receipt are sufficient to reproduce the DOCX. The source image was retained locally for auditing.

ImageGen prompt

> Photorealistic natural editorial museum study photograph for a synthetic guide titled 'Reading the Surface'. One small visibly handmade, unglazed terracotta study vessel on a warm pale limestone tabletop. Three-quarter close-up with the complete rim and foot visible and generous breathing room, a few subtle concentric throwing ridges and quiet variations in clay tone. Diffused daylight from camera left, softly defined shadow to the right, museum conservation studio atmosphere, neutral ivory backdrop, restrained amber and warm grey palette. Horizontal composition 3:2, subject centered, legible at small print size. No people, tools, labels, labels on objects, letters, overlays, watermarks, borders or invented archaeological marks. An invented object rather than a reproduction of any existing art.
