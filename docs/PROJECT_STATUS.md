# KMDStudio project status

28 November 2026, Europe/Moscow

KMDStudio 0.7.0rc1 is a development candidate for structured, creative and hybrid editable A4 documents. Fifteen on-demand design decisions and five composition studies guide the host from a reader's task to native Word controls. Five authored documents demonstrate the workflow, including two editions of one source. The seven established structured briefs match both archived comparison versions byte for byte. [Candidate verification](VERIFICATION-v0.7.0rc1.md)

## Milestones

| Version | Delivered | Evidence |
| --- | --- | --- |
| 0.1.0 | Portable skill, bounded brief, editable Word and initial PDF verification. | [Verification](VERIFICATION-v0.1.0.md) |
| 0.2.0 | Six KDL profiles, semantic controls, native components and stronger gates. | [Verification](VERIFICATION.md) |
| 0.3.0rc1 | Reviewed raster import, host-generated imagery and Windows/Ubuntu CI. | [Verification](VERIFICATION-v0.3.0rc1.md) |
| 0.4.0rc1 | Native continuous columns, paired figures, illustrated covers and a same-source networking comparison. | [Verification](VERIFICATION-v0.4.0rc1.md) |
| 0.5.0rc1 | Mode selection, editable editorial composition and five benchmark DOCX files with anonymous previews. | [Acceptance plan](PLAN-v0.5.0.md) · [Verification](VERIFICATION-v0.5.0rc1.md) |
| 0.6.0rc1 | Bounded quality records, observed typography, report and lesson refinements, native data bars and anonymous before-and-after evidence. | [Acceptance plan](PLAN-v0.6.0.md) · [Verification](VERIFICATION-v0.6.0rc1.md) |
| 0.7.0rc1 | Selective design knowledge, contrasted report concepts, six-page exhibition guide, native technical lesson, quiet booking and an explicit modern Word mode. | [Acceptance plan](PLAN-v0.7.0.md) · [Verification](VERIFICATION-v0.7.0rc1.md) |

## Global capability matrix

Statuses apply to the observed candidate scope. PASS records a verified path. PARTIAL marks a demonstrated path with open scope.

| Capability | Current | Evidence and scope |
| --- | --- | --- |
| ACT-01 Skill activation | NOT RUN | Explicit local CLI works from a fresh skill extraction. Controlled model-based activation still awaits a shell-enabled host. |
| CNT-01 Source analysis | PARTIAL | Frozen content, required IDs and exact text are verified after authorship. Autonomous extraction is unmeasured. |
| DIR-01 Art direction | PARTIAL | Fifteen cards inform the five authored outputs and two same-source report concepts. Independent preference and autonomous choices remain unmeasured. |
| REF-01 Reference interpretation | PASS | Host-authored choices derived from the supplied imagery appear in new synthetic documents. Autonomous interpretation of unseen imagery is unmeasured. |
| TYP-01 Typography | PASS | Writer renders Arial Black, Georgia, Cambria, Calibri and Consolas in actual output. The Cyrillic lesson exercises the documented code-font fallback. Optional open families still need renderer qualification. |
| CLR-01 Color system | PASS | Semantic foreground contrasts, warm or dark panels and legible captions in the inspected examples. Print and background rendering depend on the viewer. |
| LAY-01 Composition | PASS | Existing native components express a dense evidence page, art-led opening, varied exhibition sequence and quiet asymmetric booking. Word and Writer agree on the five final page counts. |
| CMP-01 Native components | PASS | Twelve block types share one generator. Existing editable components retain their output. |
| ART-01 Image generation workflow | PASS | Three original illustrations prepared via authorized host-native ImageGen. Native exact data, code and diagrams stay separate from generated art. |
| ART-02 Raster import | PASS | Existing asset hashes, bounds and normalized PNG verification remain in effect. Native decoder containment is a host responsibility. |
| ICO-01 Packaged icons | PASS | The two existing verified derivatives and notices are retained. |
| DIA-01 Technical diagrams and information graphics | PARTIAL | Editable ordered steps and quantitatively checked table bars work. More complex graph structures remain open. |
| DOC-01 Editable DOCX | PASS | The clean-package CLI reproduces all eight new stages. Open XML SDK accepts each. Word repaginates the five final editable documents. |
| PDF-01 Qualified PDF delivery | BLOCKED | Static validator tests pass. Production export requires a qualified host for the renderer and descendants. |
| PPT-01 PPTX | NOT IMPLEMENTED | Deferred. |
| TXT-01 Fidelity | PASS | Both report concepts preserve source reading order, descriptions and image bytes. The Russian lesson preserves the exact editable listing and verified results. |
| SEC-01 Output checks | PASS | Existing path, ZIP, XML, field, relationship, image and section checks pass. The optional settings part accepts one fixed compatibility entry and is independently checked. Independent release security review remains open. |
| VIS-01 Visual verification | PARTIAL | Five Writer sheets include two anonymous comparisons and previews of all 13 final pages. Independent human acceptance remains open. |
| QA-01 Correction traceability | PASS | Three new bounded correction records retain the initial and final versions, locations and native fidelity. The four earlier records still pass. |
| ACC-01 Accessibility | PARTIAL | Word Accessibility Assistant completed the mode 15 lesson check and reported no issues. Keyboard and screen-reader testing remain open. |
| EVA-01 Agent evaluation | NOT RUN | The matched runner is pinned to the 0.6.0rc1 baseline. The earlier local-tool gate failed and no changed standalone host was established. |
| PLT-01 Platform compatibility | PARTIAL | Word and Writer examined on Windows. Hosted checks cover Python 3.11 and 3.15 on Ubuntu and Windows. |
| PKG-01 Portable skill | PASS | 33 canonical files and fresh extraction under site-disabled Python. The main instructions are 2,071 UTF-8 bytes. |
| CI-01 Hosted verification | TRACKED | Four preserved job names cover the committed archive. See [commit-specific checks](https://github.com/apollogens/KMDStudio/pull/1/checks). |
| PUB-01 Distribution | PARTIAL | The [development draft](https://github.com/apollogens/KMDStudio/pull/1) is the review surface. Owner license approval and stable release remain open. |

Existing lock files, raster bounds, source illustrations, benchmarks and evaluation gates were reused. Independent owner acceptance, assistive-technology testing, qualified production PDF and a stable release remain open. See the [architecture](ARCHITECTURE.md), [security policy](../SECURITY.md) and [roadmap](ROADMAP.md).
