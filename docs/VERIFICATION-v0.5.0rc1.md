# Verification for KMDStudio 0.5.0rc1

27 November 2026, Europe/Moscow. The reviewed baseline was `9d6f347f4d14adf276eacbe402fb842a6fbf4c59`. The [acceptance plan](PLAN-v0.5.0.md) and [synthetic source facts](../examples/benchmarks/creative/source.md) were recorded before generation. The development branch and its [draft PR](https://github.com/apollogens/KMDStudio/pull/1) carry the candidate.

## Acceptance and reproduction

| Check | Evidence |
| --- | --- |
| Structured regression | **PASS**. The six legacy bench briefs and networking brief produce seven byte-identical DOCX files against the pinned 0.4.0rc1 archive on the same interpreter. The existing three 0.2.0 part comparisons and networking 0.3.0rc1 comparison also pass. An explicit `structured` legacy brief matches the output from its omitted-mode version. |
| Clean package | **PASS**. 27 canonical skill files, 170,213 expanded bytes and 59,029 archived bytes. Fresh extraction, Python `-E -s -S -B`, and the normal CLI reproduced eight established outputs including the historical networking comparison and five new outputs. Three new rasters live with the fixtures. |
| Content and editability | **PASS**. The two report editions preserve all native body text in the same paragraph order and identical image bytes and alt text. The independent package harness checks native table cells, exact SQL and repeating header flags. It reconciles 240 observations, 18 sites, 2.4 km, the EUR 1,800.00 agreement total and the three expected join results. The performance score holds the four-second silent cue at 00:28 in the native table. |
| Word and XML SDK | **PASS**. Microsoft Open XML SDK 2.8.1.0 returned zero errors for each final DOCX. Word 16.0 build 16.0.20625 opened all five files read-only and repaginated into 3, 3, 1, 3 and 1 pages for review sets A–E. The report editions have one versus three native tables, the lesson has three native tables, one inline image and one ordered exercise beginning at 1. |
| Visual review | **Preliminary PASS**. All 11 final pages were inspected in LibreOffice Writer 26.8.3.1, rasterized by Ghostscript 10.03.1 at 120 dpi. Word fixed-format automation stalled, so the visual evidence uses Writer. Successful Word opening and pagination are reported separately. Human design acceptance remains open. |
| Tests and dependencies | **PASS**. Python 3.15.2 standard-library run recorded 41 passes and five optional skips. All 46 tests pass with the existing pinned optional tools. Ruff, `pip check` and OSV checks for Pillow 13.0.0, pypdf 7.2.0 and Ruff 0.17.6 passed. The first OSV attempt encountered a transient TLS EOF and the rerun passed. No dependency pin changed. |
| CI | Existing Windows and Ubuntu jobs for Python 3.11 and 3.15 exercise the checked-in candidate ZIP and all benchmarks. Commit-specific outcomes appear on the [draft PR checks](https://github.com/apollogens/KMDStudio/pull/1/checks) and the [branch workflow history](https://github.com/apollogens/KMDStudio/actions/workflows/verify.yml?query=branch%3Adev%2Fvisual-intelligence). |
| Accessibility and production PDF | **PARTIAL** for accessible DOCX markup and **BLOCKED** for production PDF on this host. Native headings, sequential metadata, source text, lists, repeating headers and descriptions were verified. Word keyboard traversal and screen-reader behavior in layout rows remain unmeasured. Writer PDFs were intermediate QA material from synthetic inputs. The production exporter still requires a qualified filesystem and network boundary for the renderer and descendants. |
| Agent evaluation | **NOT RUN** for acquisition of source facts, implicit activation, creative effectiveness and controlled comparison. The previous local-tool probe remains **FAIL** for fixture access. This candidate's deterministic package experiments test the implementation. |

```powershell
python -E -s -B -m unittest discover -s tests -v
.venv/Scripts/python.exe -E -s -B -m unittest discover -s tests -v
.venv/Scripts/ruff.exe check skills tests tools evals
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe -E -s -B tools/audit_dependencies.py
python -E -s -B tools/verify_bundle.py --archive artifacts/v0.5.0rc1/kmdstudio-0.5.0rc1.zip
```

Use `--creative-output` with an existing empty directory to keep the verified DOCX files. See the [direct CLI command and artwork provenance](../examples/benchmarks/creative) and the [Word and SDK review script](../tools/review_word.ps1). The preview path used the local extracted Writer binary with a fresh user profile, then Ghostscript with `-dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -r120`.

## Visual observations and corrections

- [A](../artifacts/v0.5.0rc1/review/A) is the structured report. Its 40 pt Arial heading, standard section rules and serial process notes retain predictable reading. The initial image-only third page was replaced with a complete action page and a wider standalone illustration.
- [B](../artifacts/v0.5.0rc1/review/B) is the same-content editorial report. Its 62 pt Georgia display, dark chapter entry, warm 54 pt display value, right-aligned ledger and separate 30:70 metadata and 39:61 figure rows establish a different hierarchy. An explicit paragraph boundary corrected Word joining the two neighboring tables. Differentiated fills separate the title band from the metric. The caption wraps beneath the inset image.
- [C](../artifacts/v0.5.0rc1/review/C) is the minimalist agreement. The authentic Arial Black 50 pt title, smaller metadata region and right-aligned amount column retain one-page reading. The display line height was tightened after the first review. Amounts remain editable.
- [D](../artifacts/v0.5.0rc1/review/D) is the hybrid SQL lesson. A wide conceptual cover image precedes a Cyrillic display title. The two source tables, two-step diagram, Consolas SQL, result grid and separate numbered exercise remain editable. The second pass separated table captions from preceding rules with extra vertical space.
- [E](../artifacts/v0.5.0rc1/review/E) is a timed performance score. A 71 pt right-aligned Georgia title and a large opening cue contrast with a compact score. The second pass aligned the cue label with the time and gave the dark panel padding. The cue timings and silence remain in the table.

## Font evidence

The Windows font files for Arial regular/bold, Arial Black, Georgia regular/bold and Consolas regular/bold cover sampled Latin and Russian Cyrillic, including `Ё/ё`. Windows reports editable embedding for those files. The candidate embeds no fonts in DOCX. Font names and weights were checked against text runs in the diagnostic Writer render. It used Georgia regular for both creative English titles, Arial Black for agreement display, Georgia Bold at 58 pt for the Russian display, Arial regular and bold for body and headings, and Consolas at 10 pt for SQL. The CLI explicitly substituted Georgia for the unavailable requested Literata. Microsoft documents separate license rules for font file redistribution and embedding. [Microsoft font FAQ](https://learn.microsoft.com/en-us/typography/fonts/font-faq)

Inter and IBM Plex Sans are open alternatives with documented Latin and Cyrillic coverage and regular/bold faces. Literata offers an OFL variable family with Latin and Cyrillic coverage and regular/bold instances. OFL allows document embedding under its terms. These alternatives were reviewed from publisher information. The candidate does not qualify their Word or Writer rendering, distribute files, install them or test embedding. Manrope, Golos Text, Onest and JetBrains Mono keep explicit fallback entries and have no candidate renderer qualification. [Inter distribution](https://github.com/rsms/inter) · [IBM Plex](https://github.com/IBM/plex) · [Literata](https://github.com/googlefonts/literata) · [OFL FAQ](https://openfontlicense.org/ofl-faq/)

## Artifact checksums

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| [A cooler route, structured](../artifacts/v0.5.0rc1/cooler-route-structured.docx) | 1,167,702 | `29ab30d99639ff1e298ada4d12c24a7b5459254a04fe78149d09af0bb7acde49` |
| [A cooler route, editorial](../artifacts/v0.5.0rc1/cooler-route-editorial.docx) | 1,168,003 | `d95075e07d84cd4528c86b2a1f8202ff68632ac93516952e6a56538c91860b01` |
| [Fieldwork agreement](../artifacts/v0.5.0rc1/fieldwork-agreement.docx) | 4,908 | `07c151bb80e4e270efbda1062df3aea6c109f6d5205f60847b30fc5d172397ac` |
| [Как данные связаны](../artifacts/v0.5.0rc1/relational-databases.docx) | 521,701 | `46ef113ce07fad88e9f16ba888a430fcf2700a66b0b641a1d0f1fb7ea3b3ae3b` |
| [Night relay](../artifacts/v0.5.0rc1/night-relay.docx) | 4,717 | `58b5a1a3ad5c715da25d356c821106c7f81efb706d98df69043889b914b61ba5` |
| [Portable skill](../artifacts/v0.5.0rc1/kmdstudio-0.5.0rc1.zip) | 59,029 | `53ca34e50ca90ee401a8a856220abb5a0c317a21f31582d9348c68691f4455b9` |
