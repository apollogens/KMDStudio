# Creative and hybrid benchmarks

The [frozen source](source.md) defines the synthetic facts. The JSON briefs supply the exact editable content and document settings. See the [rendered review sets and editable files](../../../artifacts/v0.5.0rc1) and the [verification record](../../../docs/VERIFICATION-v0.5.0rc1.md).

| Benchmark | Brief | Selected direction |
| --- | --- | --- |
| B and E | [A cooler route, editorial](cooler-route-editorial.json), [A cooler route, structured](cooler-route-structured.json) | A civic field study with a warm paper tint, petrol entry, large serif figures, two street-level views and asymmetric reading on the action page. A denser atlas with repeated maps would imply spatial detail the source lacks. The paired structured edition uses the technical profile and serial composition. |
| C | [Fieldwork agreement](fieldwork-agreement.json) | Heavy sans title, quiet neutral paper, a narrow order sidebar, short clauses and a native line-item table. One page lets the parties confirm scope, dates and the EUR 1,800 total together. |
| D | [Как данные связаны](relational-databases.json) | A tactile card-catalogue metaphor, warm accents and deep violet entries frame a full-width reading and coding spine. A comic sequence was considered. The catalogue concept provides a single visual metaphor and more room for the actual relations and query result. |
| F | [Night relay](night-relay.json) | A radio performance score with a right-aligned serif title and dark timing cue followed by an editable rehearsal grid. This brief uses elapsed cues, alternating speakers and silence as native source data. |

## Artwork

The three benchmark illustrations were generated for this project with built-in ImageGen using the prompts below. No external asset or supplied reference image was used as input. Each selected image was visually inspected and normalized with `import_raster.py`. The [manifest](assets/manifest.json) records provenance and digests. The assets are outside the portable skill ZIP.

**`canopy.png`**

> Create a single original panoramic editorial illustration, ratio 3:1, for a synthetic city walking study. Image only, no lettering. A sunlit pedestrian passage through a fictional waterfront city, a blue-green fabric shade canopy casting cool diagonal shadows over terracotta brick and concrete, two very small anonymous figures walking, long horizontal perspective and a rhythm of canopy supports. Art direction: richly textured screenprinted travel reportage, restrained deep petrol blue, muted ochre and warm chalk, clear graphic composition and readable silhouettes. Edge-to-edge crop. No text, no brand, no map, no data. The image illustrates possible shade design and does not depict an actual site.

**`benches.png`**

> Create a single original landscape editorial illustration, 3:2 ratio, for a synthetic city walking study. A view from street level of two free public benches in a shaded recess under a taut blue-green awning, with alternating light and shadow over terracotta paving and one sliver of bright sky. Make the benches and circulation clear. Richly textured screenprinted reportage, deep petrol blue, muted ochre and chalk, quiet composition. No letters, logos, data or identifiable location. Full bleed.

**`catalogue.png`**

> Create a single original panoramic landscape editorial image, ratio 3:1, for a Russian lesson on relational databases. A real-looking still life of two overlapping sets of punched library index cards in soft lilac and orange on a deep ink-blue desktop, with colored cotton thread loosely linking some cards across the sets, photographed at a low angle. Tactile paper fibers, hard sideways light, contemporary art-magazine crop with strong horizontal balance. The image serves as a metaphor for linking records; make the cards blank with absolutely no writing, numbers, chart, logos or human figures. Full bleed.

## Reproduce

```powershell
$brief = 'examples/benchmarks/creative/relational-databases.json'
$manifest = 'examples/benchmarks/creative/assets/manifest.json'
$digest = '754b9b648552f01659071528a43abffcbdfe775b6b48f6c164fd6fec853fee6f'
python -E -s -B skills/kmdstudio/scripts/generate.py --root (Get-Location).Path --spec $brief --output artifacts/relational-databases-local.docx --asset-manifest $manifest --asset-manifest-sha256 $digest
```

Run `tools/verify_bundle.py` with `--creative-output` and an existing empty output directory to reproduce the five DOCX files from a fresh skill extraction.
