# KMDStudio project status

28 November 2026, Europe/Moscow

KMDStudio 0.6.0rc1 is a development candidate for structured, creative and hybrid editable A4 documents. All modes share one dependency-free Word generator, schema, KDL, component library, asset pipeline and security profile. Refinements include traceable corrections, an optional continuing cover, unshaded display metrics, proportional bars in editable data tables, and verified host typography. The seven established briefs match the archived 0.5.0rc1 output byte for byte. [Candidate verification](VERIFICATION-v0.6.0rc1.md)

## Milestones

| Version | Delivered | Evidence |
| --- | --- | --- |
| 0.1.0 | Portable skill, bounded brief, editable Word and initial PDF verification. | [Verification](VERIFICATION-v0.1.0.md) |
| 0.2.0 | Six KDL profiles, semantic controls, native components and stronger gates. | [Verification](VERIFICATION.md) |
| 0.3.0rc1 | Reviewed raster import, host-generated imagery and Windows/Ubuntu CI. | [Verification](VERIFICATION-v0.3.0rc1.md) |
| 0.4.0rc1 | Native continuous columns, paired figures, illustrated covers and a same-source networking comparison. | [Verification](VERIFICATION-v0.4.0rc1.md) |
| 0.5.0rc1 | Mode selection, editable editorial composition and five benchmark DOCX files with anonymous previews. | [Acceptance plan](PLAN-v0.5.0.md) · [Verification](VERIFICATION-v0.5.0rc1.md) |
| 0.6.0rc1 | Bounded quality records, observed typography, report and lesson refinements, native data bars and anonymous before-and-after evidence. | [Acceptance plan](PLAN-v0.6.0.md) · [Verification](VERIFICATION-v0.6.0rc1.md) |

## Global capability matrix

Statuses apply to the observed candidate scope. PASS records a verified path. PARTIAL marks a demonstrated path with open scope.

| Capability | Current | Evidence and scope |
| --- | --- | --- |
| ACT-01 Skill activation | NOT RUN | Explicit local CLI works from a fresh skill extraction. Controlled model-based activation still awaits a shell-enabled host. |
| CNT-01 Source analysis | PARTIAL | Frozen content, required IDs and exact text are verified after authorship. Autonomous extraction is unmeasured. |
| DIR-01 Art direction | PARTIAL | Three authored strategies share the engine. Before-and-after evidence shows improved grouping and hierarchy in the report and lesson. Independent preference and automatic choices remain unmeasured. |
| REF-01 Reference interpretation | PASS | Host-authored choices derived from the supplied imagery appear in new synthetic documents. Autonomous interpretation of unseen imagery is unmeasured. |
| TYP-01 Typography | PASS | Exact-family Windows probe, glyph samples and Writer type-run evidence for Cambria, Calibri and Consolas. Optional open families need separate renderer qualification. |
| CLR-01 Color system | PASS | Semantic foreground contrasts, warm or dark panels and legible captions in the inspected examples. Print and background rendering depend on the viewer. |
| LAY-01 Composition | PASS | Continuing cover, unshaded display metrics and natural page flow add to the existing components. Word and Writer agree on page counts for all revised stages. |
| CMP-01 Native components | PASS | Twelve block types share one generator. Existing editable components retain their output. |
| ART-01 Image generation workflow | PASS | Three original illustrations prepared via authorized host-native ImageGen. Native exact data, code and diagrams stay separate from generated art. |
| ART-02 Raster import | PASS | Existing asset hashes, bounds and normalized PNG verification remain in effect. Native decoder containment is a host responsibility. |
| ICO-01 Packaged icons | PASS | The two existing verified derivatives and notices are retained. |
| DIA-01 Technical diagrams and information graphics | PARTIAL | Editable ordered steps and quantitatively checked table bars work. More complex graph structures remain open. |
| DOC-01 Editable DOCX | PASS | Twenty clean-package CLI generations covering historical and new briefs. Seven new stages pass the SDK and open in Word. |
| PDF-01 Qualified PDF delivery | BLOCKED | Static validator tests pass. Production export requires a qualified host for the renderer and descendants. |
| PPT-01 PPTX | NOT IMPLEMENTED | Deferred. |
| TXT-01 Fidelity | PASS | All four layout-only correction records preserve actual text order, artwork and descriptions. SQL and tabular values remain editable. |
| SEC-01 Output checks | PASS | Existing path, ZIP, XML, field, relationship, image and section checks pass. New row and style mutations are rejected. Independent release security review remains open. |
| VIS-01 Visual verification | PARTIAL | Four anonymous comparison sheets and 12 new full-resolution checks document observed defects and corrections. Independent human acceptance remains open. |
| QA-01 Correction traceability | PASS | Four bounded records verify immutable source and output references, correction stage, location and exact layout-only preservation. |
| ACC-01 Accessibility | PARTIAL | Word structure and heading navigation verified. Word Accessibility Assistant requests modern format conversion. Keyboard and screen-reader use remain open. |
| EVA-01 Agent evaluation | NOT RUN | Previous randomized local-tool smoke failed fixture access. No repeated probe or token-efficiency comparison for this candidate. |
| PLT-01 Platform compatibility | PARTIAL | Word and Writer examined on Windows. Hosted checks cover Python 3.11 and 3.15 on Ubuntu and Windows. |
| PKG-01 Portable skill | PASS | 31 canonical files and fresh extraction under site-disabled Python. The main instructions retain their byte length. |
| CI-01 Hosted verification | TRACKED | Four preserved job names cover the committed archive. See [commit-specific checks](https://github.com/apollogens/KMDStudio/pull/1/checks). |
| PUB-01 Distribution | PARTIAL | The [development draft](https://github.com/apollogens/KMDStudio/pull/1) is the review surface. Owner license approval and stable release remain open. |

Existing lock files, raster bounds, source illustrations, benchmarks and evaluation gates were reused. Modern Word accessibility assessment, independent owner acceptance, qualified production PDF and a stable release remain open. See the [architecture](ARCHITECTURE.md), [security policy](../SECURITY.md) and [roadmap](ROADMAP.md).
