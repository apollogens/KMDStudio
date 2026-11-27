# KMDStudio project status

27 November 2026, Europe/Moscow

## Executive summary

KMDStudio is an original Agent Skill for designed, editable A4 documents. Its dependency-free core turns a bounded brief into native Word paragraphs, headings, lists, tables, code, diagrams and figures. The 0.4.0rc1 candidate adds an illustrated cover, continuous two-column prose, asymmetric text and figure placement, and explicit short-content flow controls. A Russian networking workbook demonstrates how an authorized visual reference affects a real document.

The candidate is usable for the verified local DOCX workflow. Both comparison files preserve 42 required source blocks, pass Microsoft Open XML SDK validation and open into nine pages in Word. A randomized local-tool smoke completed a model turn without reading its fixture. Comparative agent effectiveness, independent human preference, and assistive-technology behavior are unverified. [Candidate evidence](VERIFICATION-v0.4.0rc1.md)

## Development history

| Milestone | Delivered | Evidence |
| --- | --- | --- |
| 0.1.0 | Portable skill, bounded brief, editable Word, native structures and initial PDF validation. | [Verification](VERIFICATION-v0.1.0.md) |
| 0.2.0 | Six KDL profiles, semantic tokens, expanded native composition, three benchmarks and tighter DOCX and PDF validation. | [Verification](VERIFICATION.md) |
| 0.3.0rc1 | Approved raster import and host-generated illustration workflow, six packaged benchmarks, Word and Writer checks, four-job Windows and Ubuntu CI. | [Verification](VERIFICATION-v0.3.0rc1.md) |
| 0.4.0rc1 | Bounded native columns, two figure compositions, reference planning and a same-source Word comparison with hardened evaluation gates. | [Verification](VERIFICATION-v0.4.0rc1.md) |

The iteration reused the six KDL profiles, package verification, the optional raster decoder, native components, and pinned CI. The three-image limit remains adequate for the benchmark, which uses two illustrations. Broad design-system research, additional profiles, graph frameworks and repeated Windows PDF qualification were deferred. [Delta plan](PLAN-v0.4.0.md) · [Architecture](ARCHITECTURE.md)

## Global capability matrix

Current statuses apply to the observed scope. Application checks refer to Word 16.0 build 16.0.20625. [Verification record](VERIFICATION-v0.4.0rc1.md)

| Capability | Current | Implementation and remaining scope |
| --- | --- | --- |
| ACT-01 Skill activation | NOT RUN | The runner can record packaged CLI invocation. Controlled activation awaits a shell-enabled model run. |
| CNT-01 Source analysis | PARTIAL | Required IDs and exact text are verified after authoring. Autonomous source extraction awaits evaluation. |
| DIR-01 Art direction | PARTIAL | The host planning record selects KDL and composition. Autonomous choices await a controlled run. |
| REF-01 Reference interpretation | PASS | The original board's grid, hierarchy and palette are reflected in the inspected workbook. Generalization to unseen references is unverified. |
| TYP-01 Typography | PASS | Six profiles and validated overrides. Cyrillic, Latin and monospaced listings inspected in Word. |
| CLR-01 Color system | PASS | Semantic foreground contrasts and reference-driven palette checked. Viewer print behavior can vary. |
| LAY-01 Composition | PASS | Word shows continuous columns, an illustrated cover and a 60:40 figure row. Exact pagination remains application-dependent. |
| CMP-01 Native components | PASS | New options extend the ten existing block types. Short rows and paragraphs can stay together. Separate numbered lists restart at one. |
| ART-01 Image generation workflow | PASS | The previous authorized host-generated gallery is retained. The new benchmark uses two original project illustrations. |
| ART-02 Raster import | PASS | The reviewed PNG/JPEG path and three-asset manifest bound pass regression. Native decoder containment remains a host responsibility. |
| ICO-01 Packaged icons | PASS | Two verified icon derivatives and pinned notices. |
| DIA-01 Technical diagrams | PARTIAL | Editable ordered diagrams cover the workshop request path. Richer graph structures remain outside the implemented scope. |
| DOC-01 Editable DOCX | PASS | Eight clean-package CLI runs and independent SDK validation of both final networking files. |
| PDF-01 Qualified PDF delivery | BLOCKED | Static PDF validation tests pass. The renderer and descendants require a qualified host. |
| PPT-01 PPTX | NOT IMPLEMENTED | Deferred. |
| TXT-01 Fidelity | PASS | Both files preserve 42 required IDs, native text order, code, captions, alt text and table values. |
| SEC-01 Output checks | PASS | Path, ZIP, XML, image, section and row profile checks pass. Independent release security review remains open. |
| VIS-01 Visual verification | PASS | All 18 final Word pages inspected. Blinded human review is available through anonymized previews. |
| ACC-01 Accessibility | PARTIAL | Native structures and explicit figure descriptions verified. Layout row announcements, keyboard order and screen-reader use remain open. |
| EVA-01 Agent evaluation | FAIL | The randomized shell probe recorded no file access. Controlled A/B/C is **NOT RUN**. |
| PLT-01 Platform compatibility | PARTIAL | The established hosted Windows/Ubuntu jobs cover Python 3.11 and 3.15. The new Word-specific observations come from Windows. |
| PKG-01 Portable skill | PASS | 26 canonical members and fresh extraction under site-disabled Python. |
| CI-01 Hosted verification | PASS | The established four job names are retained. Candidate runs are tracked on the [branch workflow](https://github.com/apollogens/KMDStudio/actions/workflows/verify.yml?query=branch%3Adev%2Fvisual-intelligence). |
| PUB-01 Distribution | PARTIAL | Review takes place in the [existing draft PR](https://github.com/apollogens/KMDStudio/pull/1). Owner license approval and stable release remain open. |

## Product and evidence

The 0.3.0rc1 comparison places the cover artwork on page 2 and splits the first diagram and the final journal. The candidate keeps the diagram on page 2, moves the art to the cover, and brings text and exchange art onto page 5 together. It groups the short cache comparison on page 7, puts the listing and journal on page 8, and keeps each final exercise with its check on page 9. The preview pair is available for human assessment without version labels. [Editable files and previews](../artifacts/v0.4.0rc1)

| Metric | Observed value |
| --- | --- |
| Local tests | 41 pass with existing optional validators installed. Standard-library environment registers 36 pass and 5 optional skips. |
| Runtime dependencies | Zero for DOCX. Optional Pillow 13.0.0 and pypdf 7.2.0 pins are unchanged. pip and OSV checks passed. |
| Bundle | 26 members, 142,907 expanded bytes and 51,148 archived bytes. Archive growth is 5,681 bytes versus 0.3.0rc1. |
| Workbook | 21,796 bytes for the candidate and 21,534 for the baseline. One clean-package run measured 189 ms and 227 ms respectively, including CLI startup. |
| Independent checks | Two final files with zero Open XML SDK validation errors, nine pages each in Word. |
| Shell probe | 18.93 seconds, 96,893 input tokens including 94,976 cached, and 486 output tokens including 81 reasoning tokens. Zero shell commands and zero MCP calls. No comparative efficiency measure. |

## Security and release gates

The writer gates bounded JSON, ZIP, XML and normalized PNGs. It checks native section geometry, relationship reuse, reading order, captions, asset identity and exclusive publication. The verified manifest establishes integrity. The operator establishes source provenance and rights. Residual risks include shared-directory races, app and decoder defects, untrusted source instructions and compromised trusted inputs. Reference text, pixels and metadata supply no operational authority. Diagnostic Word QA and the production PDF boundary are separate. [Security policy](../SECURITY.md) · [Threat model](threatmodel.md)

The next milestone is one controlled standalone evaluation after real shell access is demonstrated. Run the three package arms with the frozen rubric, then seek blinded design feedback and verify Word keyboard and screen-reader behavior. Stable distribution still requires independent security review, supported-path acceptance and an owner-approved redistribution license. [Roadmap](ROADMAP.md) · [Evaluation procedure](../evals/README.md)
