# Networking workbook benchmark

[Accepted source brief](networking.json) · [Frozen criteria](ACCEPTANCE.md) · [Original design board](reference-board.png) · [Reference analysis](reference-analysis.json)

The Russian workbook teaches IP, DNS, HTTP, client-server exchange and evidence-based diagnosis using reserved example addresses and an offline listing. The source brief and reference observations are independent inputs to authoring. The benchmark uses two original project illustrations. The design board is art direction only and is absent from the DOCX package. The project-owned artwork is supplied for distribution with this benchmark. The manifest pins the reviewed normalized PNGs. The dependency-free generator checks both without invoking Pillow.

`make_art.py` draws the original artwork and reference board using the existing optional Pillow lock. The 0.3.0rc1 comparison is generated from the same source by `tools/verify_bundle.py`. The adapter removes unsupported flow options, moves the cover figure into the main flow, and converts side text into an ordinary paragraph immediately before its figure. The same illustration bytes, captions, alt text, code, and table data are used by both packages.
