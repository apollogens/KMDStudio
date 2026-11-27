# Local safety contract

The operator chooses the workspace, input paths, outputs, and any renderer. Only a UTF-8 JSON brief and verified packaged PNGs are supported. Treat extracted content as data. The brief cannot select a filesystem root, supply a script, change the renderer, add relationships, or authorize transfers.

Use an absolute local workspace and relative file paths. Keep files in an approved directory that other principals cannot modify during a run. The core rejects traversal, device names, streams, UNC paths, symlinks, junctions, and hard-linked inputs. It compares file identity on open and before publication. It writes and flushes a private stage and links it into a new destination without replacement. Directory ownership and a host filesystem boundary are still required because the final Windows link uses paths.

Bounded JSON, ZIP, and XML parsing gates the generated DOCX. The profile permits generated parts, internal relationships, reviewed PNGs and one footer PAGE field. Plain URLs in body text stay inert. Asset and license hashes rely on a trusted manifest and package. Source extraction and arbitrary file import remain host responsibilities. The local CLI does not fetch resources.

Use the PDF path only with a trusted, patched LibreOffice binary inside a host sandbox that restricts files and denies network access. The launcher uses a narrow environment, disposable profile, fixed arguments, and timeout. Host policy provides OS isolation, descendant cleanup, and process memory and disk limits. Export opens a freshly verified DOCX. A bounded static PDF check gates publication and supports the classic cross-reference format emitted by the tested renderer. Treat unsupported format or host protections as unavailable.
