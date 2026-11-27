# Verification for KMDStudio 0.7.0rc1

28 November 2026, Europe/Moscow. Engine baseline `8b35f97d5226349697f023a0f8c87ad9ca7bf535`. Research synchronized fast-forward through `b59054ba596f087c9e6d2db4802d50ac6bae9218`. The [acceptance plan](PLAN-v0.7.0.md) freezes the comparison and synthetic content. The previous package, artifacts, KDL and component library are the comparison baseline. The [research atlas](DESIGN-RESEARCH-v0.7.0.md#candidate-verification-of-sources) records which references were consulted.

## Design and rendered results

| Case | Observed result |
| --- | --- |
| A. Structured | All seven structured fixtures reproduce identical whole DOCX files on Python 3.15.2 against the pinned 0.6.0rc1 and 0.5.0rc1 archives. The previous 0.2.0 part comparison and 0.3.0rc1 networking pair pass in the same bundle run. |
| B. Same-source report | The evidence edition brings title, context, measure and table onto its first page. A separate trial page gives the smaller supporting visual from the baseline more room. The baseline report's large cover and second-page action proximity remain useful for slower reading. Source and both images match exactly. |
| C. Exhibition publication | Six A4 pages use art-led entrance, asymmetric orientation, close view, index, same-scale comparison and a closing exercise. On page 5 the shapes and captions let the reader compare a central gap and a returning strip at one scale. The quieter index and closing use generous space. The initial cover split in Writer. Reducing its display size and vertical intervals restored a single cover. |
| D. Educational hybrid | The two-page Russian lesson leads from an objective to a native diagram and an editable trace. The exact Python listing, guided practice, independent task and feedback share page 2. The trace independently yields 13, 15 and 11. The independent practice yields 9, 15 and 21. |
| E. Quiet booking | One page links a large serif entry, 29% date rail, readable terms, right-aligned fees and the reply deadline. The editable values reconcile to GBP 155.00. |
| F. Alternative concept | The place edition gives its 165 mm cover illustration a dedicated page and puts findings and actions below a panel entry on page 2. The evidence edition uses a 92 mm inset cover figure, a continued opening and a 62% action image region. They vary focus, spacing and alignment while retaining identical native text order, alternative text and artwork. |
| G. External holdout | Procedure prepared. No owner-supplied case or independently judged agent comparison was run. |

The candidate uses 15 decision cards, five composition sketches and four compact counterexamples. They map to supported selectors, type roles, measures, images, charts and semantic blocks. Three JSON fragments are validated through the normal generator. The five final and three retained initial editions are editable DOCX. Three correction records capture the Writer total-row spill, label alignment and split cover. The two report review sheets label rows A and B. In the baseline comparison A is the evidence edition. In the concepts comparison A is the place edition. The [review images](../artifacts/v0.7.0rc1/review) contain all 13 final pages. The [benchmark guide](../examples/benchmarks/design-knowledge) gives decisions, source and reproduction. These authored visual observations establish differences in the artifacts. Independent design acceptance is pending.

## Typography, Word and accessible structure

Writer 26.8.3.1 diagnostic text runs show the font and size used for actual text. Ghostscript 10.03.1 rasterized those pages at 120 dpi. The Windows exact-family inventory found no regular or bold face for Manrope, Onest, Golos Text, Inter, Unbounded, Literata, IBM Plex Sans or JetBrains Mono. The [previous font evidence](FONTS-v0.6.0.md) records pinned upstream license metadata and the host glyph and embedding probe. The [qualification procedure](../skills/kmdstudio/references/typography.md#design-decisions) applies to later optional font preparation. This candidate contains no font files.

| Document | Observed type roles in Writer |
| --- | --- |
| Report, evidence | Arial Black 50 pt title and metric, Cambria Bold 28 pt heading, Calibri 12 pt body and Calibri Bold 9 pt metadata. |
| Report, place | Georgia 44 pt display, Calibri Bold 24 pt headings and Calibri 11 pt body. |
| Exhibition | Georgia 54 pt display, Cambria Bold 32 pt headings, Cambria 13 pt prose and Calibri 10 pt captions. |
| Lesson | Calibri Bold 58 pt Cyrillic title, Cambria Bold 30 pt headings, Calibri 13 pt prose and Consolas 11 pt listing. The CLI reports `JetBrains Mono -> Consolas`. |
| Booking | Cambria 52 pt regular title, Calibri Bold 23 pt headings and Calibri 13 pt prose. |

Open XML SDK 2.8.1.0 reported zero errors on all eight stages. Word 16.0.20625 opened the five final DOCX files read-only, repaginated to 2, 2, 6, 2 and 1 pages respectively, and reported no document protection. The native heading levels are 1, 1, 1 and 2 for the lesson. The modern option produced mode 15. Word Accessibility Assistant opened on the lesson copy and showed “Looks good! No issues found.” The four other final documents used mode 12. Keyboard navigation, actual screen-reader announcements and a multi-document accessibility assessment remain open.

## Execution and boundaries

| Gate | Evidence |
| --- | --- |
| Tests and clean bundle | Python 3.15.2 ran 56 tests with the optional validators present. System Python completed the same suite with five optional skips. Ruff, `pip check`, and OSV passed with the existing locked versions. The clean archive reproduced eight new stages and ran all historical comparisons. |
| Source, data and assets | Native text, figures, tabs, code, digits and relationships pass the generator and independent package comparison. The route values 96, 78 and 66 sum to 240. Their Writer strokes measure 186, 151 and 128 px from one origin in both editions at 120 dpi. The site and distance columns also reconcile. The total row carries no data bar. The art manifest pins three original normalized PNGs. |
| Compatibility security | Independent parser checks require the exact Word compatibility setting, its internal relationship and content type. Negative coverage rejects misspecified options, unexpected trees, attributes and values. The structured build path remains byte-identical. |
| Package | 33 canonical files, 208,444 expanded bytes, 74,542 ZIP bytes. Relative to v0.6.0rc1 this is +2 files, +16,705 expanded bytes and +7,534 ZIP bytes. Main instructions are 2,071 UTF-8 bytes, a change of +6. No dependency or lock file changed. The research atlas, source art and rendered studies are outside the portable skill. |
| Timings | Clean-package final benchmark CLI generation took 170–224 ms per document in the recorded run. The three quality records retain five transitions, including two report reinterpretations and three targeted layout fixes. CLI timings measure deterministic generation. |
| Hosted CI | The same four Linux and Windows, Python 3.11 and 3.15 jobs check the candidate archive and existing locks. See the [draft PR checks](https://github.com/apollogens/KMDStudio/pull/1/checks) and [branch runs](https://github.com/apollogens/KMDStudio/actions/workflows/verify.yml?query=branch%3Adev%2Fvisual-intelligence). |
| Agent A/B/C | **NOT RUN.** The runner now pins the 0.6.0rc1 archive for the comparison. Earlier fixture-access smoke failure remains the host blocker. No unchanged nested probe was repeated. Agent duration, token usage and autonomous selection quality remain unmeasured. |
| PDF and security review | Production PDF remains blocked on this host pending descendant sandbox qualification. The rendered sheets use local diagnostic exports. The independent release security review and stable redistribution approval remain open. |

## Reproduce

```powershell
python -E -s -B -m unittest discover -s tests -v
.venv/Scripts/python.exe -E -s -B -m unittest discover -s tests -v
.venv/Scripts/ruff.exe check skills tests tools evals examples/benchmarks/design-knowledge
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe -E -s -B tools/audit_dependencies.py
python -E -s -B tools/verify_bundle.py --archive artifacts/v0.7.0rc1/kmdstudio-0.7.0rc1.zip
```

The portable archive SHA-256 is `e0dec2dba3c4cfd0db41fea8395bded6289a0aa6866ea86241073c2fcb1f8092`. The [record files](../examples/benchmarks/design-knowledge/records) retain the brief and DOCX digests for the comparison and correction stages. See [current capability and maturity](PROJECT_STATUS.md) and the [next milestone](ROADMAP.md).
