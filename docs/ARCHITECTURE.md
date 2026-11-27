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
| Design data and semantics | `document.schema.json` defines the brief. `spec.py` validates design and composition, and calls `design.py` to resolve KDL defaults, density, overrides and contrast. The host records visual reference observations before selecting these controls. |
| Illustrations | `import_raster.py` optionally normalizes authorized PNG and JPEG data using Pillow. The standard library checks normalized bytes and the operator-pinned manifest in `raster.py`. |
| Deterministic components and Open Packaging Convention profile | `layout.py`, `ooxml.py` |
| Release gates | `review_docx.py`, PDF object graph validation, and actual page inspection when available |
| Provenance | Package manifest, notices, and hash-pinned optional or development requirements |

The scope is a configurable A4 canvas and ten block types. A brief can mark inclusive prose ranges for native continuous two-column sections. Wide material stays in the normal flow. A bounded text-and-figure row places plain text before an inline image and caption. The cover can embed an approved illustration. Six profile definitions share layout functions. Python tokenization emits semantic syntax roles and preserves all source characters. Independently parsed output verifies text, bookmarks, section boundaries, figure relationships, running text and selected native structures. The host verifies source fidelity and rendered pages.

The generator uses an allowlisted namespace and part profile and publishes via an exclusive hard link from a flushed staged file on the same volume. NTFS and similarly capable filesystems support this publication path. Output validation remains independent from construction even though it runs before publication. Optional export bounds the PDF cross-reference table, object graph and page tree. Pagination depends on the target application's font metrics and Word layout behavior.

A manifest supplied through CLI options establishes which illustration bytes the operator approved. Briefs name assets by ID. The optional native decoder runs before generation and outside the dependency-free core. Its output is bounded and rechecked before use. Asset IDs keep the same brief usable when reviewed inputs move together with their workspace.
