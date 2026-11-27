# Architecture

KMDStudio is a skill folder plus an offline document generator. The host agent performs intake, editorial analysis, clarification, and art direction. The structured brief carries design decisions and editable content. It has no authority over execution or filesystem policy.

```text
Authorized sources -> Host analysis and art direction -> Bounded JSON brief
                              |
Authorized PNG or JPEG -> Optional decoder -> Reviewed PNG and pinned manifest
                                                         |
Bundled icons --------> Verified asset IDs --------------+
                              |
      Brief and assets -> Native Word layout and OPC writer
                              |
                  Package, content and metadata verification
                              |
                           Editable DOCX
                              |
        Optional isolated LibreOffice -> Static PDF validator
```

| Responsibility | Implementation |
| --- | --- |
| Entry points and operator paths | `generate.py`, `render_pdf.py`, and `guard.py` |
| Design data and semantics | `document.schema.json` defines one brief. `spec.py` validates design and composition, and calls `design.py` to resolve KDL defaults, density, overrides, color contrast and editorial font substitutions. The host resolves `auto` to `structured`, `creative` or `hybrid` before writing the brief. The CLI defaults absent modes to `structured`. |
| Illustrations | `import_raster.py` optionally normalizes authorized PNG and JPEG data using Pillow. The standard library checks normalized bytes and the operator-pinned manifest in `raster.py`. |
| Deterministic components and Open Packaging Convention profile | `layout.py`, `ooxml.py` |
| Release gates | `review_docx.py`, PDF object graph validation, and actual page inspection when available |
| Provenance | Package manifest, notices, and hash-pinned optional or development requirements |

The scope is a configurable A4 canvas with twelve native block types. A brief can mark inclusive prose ranges for continuous two-column sections. Wide material stays in the normal flow. Creative and hybrid briefs can use profile-free KDL, paired layouts with selected proportions, compact metadata rows, display values and high-contrast section entries. They reuse the same figure, cover, table, exercise and code paths. A cover can place approved wide artwork before or after the main title group. Figures preserve the aspect ratio of the prepared artwork. Adjacent editorial tables are separated by a native paragraph so Word preserves their independent grids.

Python tokenization emits semantic syntax roles and preserves all source characters. Plain and SQL listings keep exact text. Independently parsed output verifies text, bookmarks, section boundaries, figures, running text, paired cell geometry, selected paragraph and table roles, and editorial style settings. The host verifies source fidelity and rendered pages. Optional font declarations are reviewed operator inputs at the CLI boundary. The core uses fixed fallback families and does not add font paths, external font relationships or embedded fonts.

The generator uses an allowlisted namespace and part profile and publishes via an exclusive hard link from a flushed staged file on the same volume. NTFS and similarly capable filesystems support this publication path. Output validation remains independent from construction even though it runs before publication. Optional export bounds the PDF cross-reference table, object graph and page tree. Pagination depends on the target application's font metrics and Word layout behavior.

A manifest supplied through CLI options establishes which illustration bytes the operator approved. Briefs name assets by ID. The optional native decoder runs before generation and outside the dependency-free core. Its output is bounded and rechecked before use. Asset IDs keep the same brief usable when reviewed inputs move together with their workspace.
