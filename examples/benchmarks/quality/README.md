# Quality benchmarks

The [source freeze](source.md) links the existing report and lesson facts and records the two new synthetic briefs. [Correction records](records) retain the initial, intermediate and final brief and DOCX paths and digests. The handover's initial version contains the intentional pagination defect. The catalogue and lesson keep intermediate attempts for inspection.

| Benchmark | Final brief | Record |
| --- | --- | --- |
| Refined creative report | [A cooler route](cooler-route-refined.json) | [Report](records/report.json) |
| Refined hybrid lesson | [Как данные связаны](relational-databases-refined.json) | [Lesson](records/lesson.json) |
| Unseen hybrid catalogue | [Five objects under glass](objects-under-glass.json) | [Catalogue](records/catalogue.json) |
| Defect-driven correction | [Saturday handover](saturday-handover-refined.json) | [Handover](records/handover.json) |

Reproduce from the repository root with Python 3.11 or newer. Use a new output file in an existing directory.

```powershell
$manifest = 'examples/benchmarks/creative/assets/manifest.json'
$digest = '754b9b648552f01659071528a43abffcbdfe775b6b48f6c164fd6fec853fee6f'
python -E -s -B skills/kmdstudio/scripts/generate.py --root (Get-Location).Path --spec examples/benchmarks/quality/cooler-route-refined.json --output artifacts/cooler-route-refined-local.docx --asset-manifest $manifest --asset-manifest-sha256 $digest
python -E -s -B skills/kmdstudio/scripts/review_quality.py --root (Get-Location).Path --record examples/benchmarks/quality/records/report.json
python -E -s -B tools/verify_bundle.py --archive artifacts/v0.6.0rc1/kmdstudio-0.6.0rc1.zip
```

Use `--quality-output` with an existing empty directory to retain all seven regenerated stages. The [anonymous review sheets](../../../artifacts/v0.6.0rc1/review) and [verification record](../../../docs/VERIFICATION-v0.6.0rc1.md) document the actual rendering.
