# Security

The supported workflow accepts a UTF-8 JSON brief and verified packaged PNGs. It writes new DOCX and optional PDF files after structural checks. Keep the skill and its manifest in a trusted, reviewed location. Use an approved host sandbox and an owner-controlled workspace, especially when invoking a native renderer.

Use the [local security contract](skills/kmdstudio/references/security.md) for operational rules and the [threat model](docs/threatmodel.md) for controls and residual risks. The DOCX and PDF checks are scoped to generated documents. Arbitrary Office, PDF, SVG, and raster inputs are unsupported. The project has not undergone independent release review.

Report suspected vulnerabilities privately to the project owner or maintainer through the channel where you obtained KMDStudio. Include the affected version, expected behavior, and sanitized evidence. Share any potentially sensitive material only with the maintainer's authorization. No public security reporting address has been designated for this milestone.
