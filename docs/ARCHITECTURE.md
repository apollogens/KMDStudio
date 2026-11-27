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
| Design data and semantics | `document.schema.json` defines the brief. `spec.py` validates it and calls `design.py` to resolve KDL defaults, density, overrides and contrast once. |
| Illustrations | `import_raster.py` optionally normalizes authorized PNG and JPEG data using Pillow. The standard library checks normalized bytes and the operator-pinned manifest in `raster.py`. |
| Deterministic components and Open Packaging Convention profile | `layout.py`, `ooxml.py` |
| Release gates | `review_docx.py`, PDF object graph validation, and actual page inspection when available |
| Provenance | Package manifest, notices, and hash-pinned optional or development requirements |

The scope is one section model, a configurable A4 canvas, and ten block types. Six profile definitions share the same layout and component functions. Python tokenization emits semantic syntax roles and preserves all source characters. Headings, numbered steps, checklists, tables, and page numbers use native Word structures. Independently parsed output verifies text, bookmarks, figure descriptions, asset identity, running text and selected structural invariants. The host verifies the brief against the source and reviews rendered pages.

The generator uses an allowlisted namespace and part profile and publishes via an exclusive hard link from a flushed staged file on the same volume. NTFS and similarly capable filesystems support this publication path. Output validation remains independent from construction even though it runs before publication. Optional export bounds the PDF cross-reference table, object graph and page tree. Pagination depends on the target application's font metrics and Word layout behavior.

A manifest supplied through CLI options establishes which illustration bytes the operator approved. Briefs name assets by ID. The optional native decoder runs before generation and outside the dependency-free core. Its output is bounded and rechecked before use. Asset IDs keep the same brief usable when reviewed inputs move together with their workspace.
