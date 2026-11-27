# Verification for KMDStudio 0.6.0rc1

28 November 2026, Europe/Moscow. Baseline `b34c3fc074c04ba018e3d66a37606ba78e9726ed`. The [acceptance plan](PLAN-v0.6.0.md) used the existing source, DOCX, Writer previews and observed defects. The mode contract, KDL profiles, asset workflow, DOCX and PDF boundaries, and evaluation infrastructure were reused.

## Benchmarks and correction results

| Case | Retained evidence | Observed result |
| --- | --- | --- |
| A. Structured | Seven unchanged benchmark briefs generated on both packages | Each whole DOCX matches byte for byte against the pinned 0.5.0rc1 archive on the same interpreter. Earlier 0.2.0 part regression and the 0.3.0rc1 networking pair still pass. |
| B. Creative report | [Initial](../artifacts/v0.5.0rc1/cooler-route-editorial.docx) · [Refined](../artifacts/v0.6.0rc1/cooler-route-refined.docx) · [Record](../examples/benchmarks/quality/records/report.json) | The dedicated cover retains a deliberate interval. Findings and actions now share page 2 after removing a forced break and balancing the illustration and caption. Unshaded entry type and metric replace stacked rectangles. The three route bars clarify comparison, while all values, native text order and both assets match the original. |
| C. Hybrid lesson | [Initial](../artifacts/v0.5.0rc1/relational-databases.docx) · [Trial](../artifacts/v0.6.0rc1/relational-databases-trial.docx) · [Refined](../artifacts/v0.6.0rc1/relational-databases-refined.docx) · [Record](../examples/benchmarks/quality/records/lesson.json) | The first trial joined the pictured opening with the lesson but separated the source tables. A one-line Cyrillic title and adjusted spacing bring both tables onto page 1. The existing deterministic relationship diagram, exact SQL, result and exercise follow on page 2. The original illustration, text and descriptions are preserved. |
| D. Unseen catalogue | [Initial](../artifacts/v0.6.0rc1/objects-under-glass-initial.docx) · [Refined](../artifacts/v0.6.0rc1/objects-under-glass.docx) · [Record](../examples/benchmarks/quality/records/catalogue.json) | The synthetic exhibit combines dates, locations and planned hours in the shared Word components. Compact intervals keep the schedule note near the 18-hour total. The editable source reads 8, 6, 4, 0 and 0 hours with the corresponding three bars. It demonstrates authored generalization to an inventory and rotation schedule. |
| E. Intentional pagination defect | [Initial](../artifacts/v0.6.0rc1/saturday-handover-initial.docx) · [Refined](../artifacts/v0.6.0rc1/saturday-handover-refined.docx) · [Record](../examples/benchmarks/quality/records/handover.json) | The initially isolated lead and schedule fill only the upper portion of two pages. Removing the explicit heading break brings them onto one page in Writer and Word. All three times, actions and owners remain exact and the briefs differ in one setting. Both stages pass mandatory output validation. |

The four [anonymous comparison sheets](../artifacts/v0.6.0rc1/review) label rows A and B. Sheet B shows baseline then revision. C shows revision then baseline. D shows initial then revision. E shows revision then intentionally flawed initial. Twelve new pages were inspected at 120 dpi, including retained trial stages. The six earlier report and lesson pages were rechecked for the comparison. Previews use LibreOffice Writer 26.8.3.1 and Ghostscript 10.03.1. Local visual judgments are preliminary. Independent owner preference and professional acceptance remain open.

## Evidence and limits

| Gate | Status and evidence |
| --- | --- |
| Mandatory content and editing | **PASS**. The record verifier compares exact native reading order, text, code, tables, figure descriptions and image payloads across all layout-only revisions. The clean package recreates the retained OOXML parts from seven briefs and verifies four correction records. |
| Information graphics | **PASS**. The generator emits native bounded paragraph borders within numeric table cells. A separate parser validates placement, proportions, kept rows, cell bounds and exact text. Benchmarks compare 96, 78 and 66 on one scale, and 8, 6 and 4 on another. Targeted Writer pixel measurements of 186, 151 and 128 px, and 181, 136 and 91 px, agree with the ratios within one pixel. Zeros and the report total are represented by editable text. Editing a number in Word requires regeneration to recompute the stroke. |
| Word and SDK | **PASS**. Open XML SDK 2.8.1.0 returned zero errors on all seven new DOCX stages. Word 16.0 build 16.0.20625 opened and repaginated every stage read-only. It reports two pages for the report and lesson revisions, one for the catalogue and final handover. |
| Accessibility | **PARTIAL**. Word verifies the lesson's three repeating data headers, outline levels 1, 1 and 2, alternative text and the ordered exercise beginning at 1. Programmatic Go To Heading navigated all three headings in that order. In the actual Word UI, Accessibility Assistant opened, showed Compatibility Mode and requested format conversion to enable checks. The original remained intact. Checker results, keyboard traversal and screen-reader behavior remain open. The serial layout alternative uses native paragraphs in reading order. |
| Fonts | **PASS** for the observed host and candidate roles. WPF checked installed faces and sample glyphs. Writer's diagnostic text runs confirm Cambria, Calibri and Consolas, including the Cyrillic display change. Open candidates were researched as metadata and license evidence. [Font results and limitations](FONTS-v0.6.0.md) |
| Unit and dependency gates | **PASS**. Python 3.15.2 ran 53 tests with the optional tools present. System Python recorded 48 passes and five optional skips. Ruff, `pip check` and OSV passed for existing versions. Dependency and lock files remain unchanged. |
| Package and instruction budget | **PASS**. The checked-in ZIP has 31 canonical files, 191,739 expanded bytes and 67,008 archive bytes. Relative to 0.5.0rc1 this is +4 files, +21,526 expanded bytes and +7,979 archived bytes. `SKILL.md` stays at 2,065 UTF-8 bytes. Detailed review and font guidance is on demand. No candidate agent token telemetry is available. |
| Hosted verification | The existing four job names and platform matrix run the checked-in ZIP. See the [candidate checks](https://github.com/apollogens/KMDStudio/pull/1/checks) and [branch runs](https://github.com/apollogens/KMDStudio/actions/workflows/verify.yml?query=branch%3Adev%2Fvisual-intelligence). |
| PDF and agent evaluation | Production PDF remains **BLOCKED** on this host pending renderer and descendant qualification. Writer PDFs were local diagnostic intermediates. Autonomous activation and A/B/C remain **NOT RUN**. No new standalone shell-enabled agent host was established. Earlier failed nested experiments were not repeated. |

## Reproduce

```powershell
python -E -s -B -m unittest discover -s tests -v
.venv/Scripts/ruff.exe check skills tests tools evals
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe -E -s -B tools/audit_dependencies.py
python -E -s -B tools/verify_bundle.py --archive artifacts/v0.6.0rc1/kmdstudio-0.6.0rc1.zip
python -E -s -B skills/kmdstudio/scripts/review_quality.py --root (Get-Location).Path --record examples/benchmarks/quality/records/lesson.json
```

See the [normal generation command](../examples/benchmarks/quality/README.md). The archived CLI runs from a fresh extraction with Python site initialization disabled. For independent application checks use [review_word.ps1](../tools/review_word.ps1) with `-AccessibilityDetails` and the local SDK assembly. Render synthetic QA material in Writer under a fresh profile, then rasterize with Ghostscript `-dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -r120`. Do not use a diagnostic PDF as qualified output.

## Checksums

| Final artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `kmdstudio-0.6.0rc1.zip` | 67,008 | `0f273897e96de60528dbe31e0ee46137b267cc75df77bbfb79f1bc1e708be98c` |
| `cooler-route-refined.docx` | 1,168,094 | `4ea8dd400f0c0ab25fd1eb796006d5b65ef499e34bc678ae01e94f6a457571c3` |
| `relational-databases-refined.docx` | 521,678 | `7f93ce6b21ae426e18b125e312dbe25a3b97d82909caebb2cc7fab24c8c84212` |
| `objects-under-glass.docx` | 4,994 | `413be11229ddcd0cb601ba59984292ebe2a0e39db7ac8cd823a2857e59aa69d4` |
| `saturday-handover-refined.docx` | 4,576 | `a37bd2371c03c425ba8283bd8042a2179f70e61c92cd5283f9e9643e6627bc79` |

The [correction records](../examples/benchmarks/quality/records) include digests of every initial and intermediate brief and DOCX.
