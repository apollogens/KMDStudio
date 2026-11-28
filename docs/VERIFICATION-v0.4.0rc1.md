# Verification for KMDStudio 0.4.0rc1

27 November 2026, Europe/Moscow. The reviewed baseline was `56fbb801badde85b3548cfa70b028e05fd28f154`. The [delta plan](PLAN-v0.4.0.md) scoped this pass to new composition, a reference-driven benchmark and the evaluation gate. Existing KDL profiles, raster import, original technical diagrams, dense tables and the restricted PDF path were reused. Historical evidence remains in the [0.3.0rc1 record](VERIFICATION-v0.3.0rc1.md).

## Artifact acceptance

| Check | Status and evidence |
| --- | --- |
| Packaged CLI and compatibility | **PASS**. The 26-member ZIP matches the canonical skill byte for byte. A clean workspace generates the six established examples with Python site packages disabled. The three 0.2.0 regression briefs match every OOXML part from their shipped package on the same interpreter. The verifier also generates the new workbook from the candidate and the hash-pinned 0.3.0rc1 archive. |
| Content and editability | **PASS**. The workbook preserves all 42 required IDs, all native text in the same reading order, exact 3-, 5- and 19-line listings, every table cell, two image payloads and exact alternative text in both files. The [source and acceptance criteria](../examples/benchmarks/networking) were authored before generation. The final reading sequence puts the journal before the exercises that use it. |
| Reference to output | **PASS** for the original synthetic board and a reviewed host interpretation. The [reference record](../examples/benchmarks/networking/reference-analysis.json) maps its palette, hierarchy, density and grid to KDL and native region choices. The archive verifier checks the applied KDL roles, section counts and approved image bytes. Word shows the full-width artwork, paired columns and 60:40 text-and-figure row. The reference was not embedded in the workbook. Autonomous interpretation of unseen references is **NOT RUN**. |
| Independent Word structure | **PASS**. Microsoft Open XML SDK 2.8.1.0 returned zero errors on both final files. Word 16.0 build 16.0.20625 opened and repaginated both. The candidate reported native sections with 1, 2 and 1 columns, four tables including one layout row, two inline figures and five separate numbered lists starting at 1. The baseline reported one column, three tables and two inline figures. |
| Visual verification | **PASS** for this pair in Word. All 18 final A4 pages were inspected. [Anonymized page sets](../artifacts/v0.4.0rc1/review) use the same renderer, fonts and 120 dpi rasterization. Human preference review is **NOT RUN**. |
| Tests, lint and dependencies | **PASS**. System Python 3.15.2 ran 41 tests with 5 optional dependency skips. The project interpreter passed 41 of 41. Ruff, pip consistency, and OSV lookup passed for the existing pins. No dependency or lock file changed. |
| Accessibility | **PARTIAL**. Native heading, column, paragraph, code, list and header markup and two informative image descriptions were verified. Layout-table announcements, keyboard use, tag generation, and screen-reader reading order require separate testing. |
| Production PDF | **BLOCKED** on this host. The unchanged exporter requires verified file and network containment for the renderer and descendants. The diagnostic Word preview is local QA evidence. The tagged preview attempt stalled. The paired page images use an untagged internal preview. |

## Observed layout differences

Set A uses 0.3.0rc1 and set B uses 0.4.0rc1. Both have nine pages. A puts the cover art on page 2 and splits the first diagram across pages 2 and 3. B puts the art on the cover and keeps the four-step diagram on page 2. On page 3 B keeps IP addressing and routing in balanced native columns and returns to a wide paragraph for ports. On page 5 the client-server explanation and inset can be read together in B. In A the same prose and art occupy serial blocks across pages 5 and 6.

The first Word draft continued numbering between independent lists, split the short DNS/HTTP comparison, and cut the lab lead at a page boundary. Explicit list starts and the bounded row and paragraph keep controls corrected those defects. A tighter spacing trial stranded the conclusion on a separate page. The accepted flow restores the original type spacing and places the journal before the diagnostic exercises. B keeps the comparison on page 7, the full listing and journal on page 8 and both final tasks with their checks on page 9. A splits the journal across its last two pages and starts the final tasks at 8 and 12. B leaves some spare space at the end of the HTTP explanation to carry the whole comparison forward. Page boundaries depend on the application and fonts.

## Agent evaluation

**FAIL** for the local-tool smoke. Codex CLI 0.171.0-alpha.13.2 emitted a completed turn in 18.93 seconds with zero terminal commands and zero MCP calls. No fixture access occurred. Actual usage was 96,893 input, including 94,976 cached, and 486 output, including 81 reasoning tokens. The controlled A/B/C and agent effectiveness remain **NOT RUN**.

The historical 313,651-input-token run used a one-line fixture and no shell calls. Its 52,077-byte trace contained a 51,061-byte completed MCP resource event. That result can add context after tool use. The current trace was 766 bytes and had no MCP event, yet its input was still mostly cached. The user configuration has plugin and MCP entries, and the nested process inherits IDE session context. Both pilots used `--ignore-user-config`. The traces expose usage and events without a provider prompt breakdown, so the relative contribution of inherited instructions, tool schemas, discovery and nested routing is unresolved. The runner now caps capture, verifies random fixture access and exact replies, checks artifacts and records timeout cleanup separately. Synthetic tests cover these gates. Follow the [standalone procedure](../evals/README.md) on a separately authorized shell-enabled host.

## Reproduction and checksums

```powershell
python -E -s -B -m unittest discover -s tests -v
ruff check skills tests tools evals examples/benchmarks/networking
python -m pip check
python -E -s -B tools/audit_dependencies.py
python -E -s -B tools/verify_bundle.py --archive artifacts/v0.4.0rc1/kmdstudio-0.4.0rc1.zip
```

Use `--networking-output` with an existing empty directory to retain the regenerated pair. For the independent Word check, use [review_word.ps1](../tools/review_word.ps1) on an authorized Windows host with a trusted installed SDK assembly. Its optional preview directory is for synthetic local QA. Rasterize those intermediates with Ghostscript 10.03.1 using `-dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -r120`. The tagged preview stall and script execution policy were kept separate from qualified PDF delivery. [Candidate CI history](https://github.com/apollogens/KMDStudio/actions/workflows/verify.yml?query=branch%3Adev%2Fvisual-intelligence)

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| [Candidate DOCX](../artifacts/v0.4.0rc1/networking.docx) | 21,796 | `57c537552a8b3e4d965dbd429382a71280230f6aafc5a31e118b2db4292b3fe2` |
| [Baseline DOCX](../artifacts/v0.4.0rc1/networking-v0.3.0rc1.docx) | 21,534 | `9b3790c8ab19f6b54d17c94365fd0e311501eb662dceb6529da97719c016d695` |
| [Candidate skill ZIP](../artifacts/v0.4.0rc1/kmdstudio-0.4.0rc1.zip) | 51,148 | `e175887e65b74f0c53b4688694ccd041893b8b3fc13a237d3e6113dd291e32d4` |

One local clean-package run measured 189 ms for the candidate workbook and 227 ms for the baseline workbook, including interpreter startup and verification. A single run establishes reproducibility on that host. The prior ZIP was 45,467 bytes and 123,291 expanded bytes. The new ZIP adds 5,681 compressed bytes and 19,616 expanded bytes, primarily from layout and verification.
