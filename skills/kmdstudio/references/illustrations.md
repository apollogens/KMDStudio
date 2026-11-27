# Illustrations

Choose an image when it shows something that readers need to observe, such as surface detail, spatial context or visual comparison. Identify the teaching or editorial job, subject, crop, focal point, lighting, aspect ratio, and intended placement before generating or selecting an image. Ask for unlabeled artwork and keep exact diagrams, code, quantities and notation in editable Word content. Use the host's image generation only with authorized inputs and transfers. Review the actual image against the source and the brief.

The optional importer accepts static local PNG and JPEG files in the approved workspace. In an isolated Python environment install the pinned wheel with `python -m pip install --require-hashes --only-binary=:all: -r <skill>/requirements-raster.lock`. Run the decoder in an operator-approved environment with restricted files, network, memory, and execution time.

```text
python -E -s -B <skill>/scripts/import_raster.py --root <absolute-workspace> --input source.jpg --output figure.png --id local-figure --origin authorized-local --credit "Source and permission reference"
```

Use `host-generated` for host-generated artwork and record the generator and source or rights reference in the credit. The CLI accepts up to 8 MiB and 8 million source pixels with an edge limit of 4,096. It applies EXIF orientation and exports a static RGB or RGBA PNG with no auxiliary chunks. Output fits within 1,600 pixels per edge and 768 KiB. It downsamples as needed. It does not apply embedded color profiles. Review the normalized image for color changes, cropping, artifacts, and approved content.

Save the printed receipt as UTF-8 JSON without a BOM. A trusted operator can combine up to three receipt entries, review the resulting manifest, and record its SHA-256 through a trusted channel. Supply both `--asset-manifest <relative-manifest.json>` and `--asset-manifest-sha256 <approved-hash>` to `generate.py`. Compute the digest after review. The brief selects figures by ID only. Hashes tie the generation run to reviewed bytes. Source credits and source hashes are operator records of provenance.

Set `figure.width_mm` to suit the image and reading order. Figures can use up to 165 mm of width within the content column and 155 mm of height. Use `align: "left"` to line up with body text or `"center"` to center the figure and caption. The caption gives the reader the image's purpose or context. Alternative text describes its meaningful visual content. Both are editable in Word. Check the rendered page for legible detail and the caption next to the figure.
