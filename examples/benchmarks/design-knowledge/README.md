# Design knowledge benchmarks

The [acceptance plan](../../../docs/PLAN-v0.7.0.md) and [frozen source](source.md) define these authored artifact tests. Image placement, reading order, type and page roles originate in the briefs. The [candidate artifacts](../../../artifacts/v0.7.0rc1) retain final and initial stages, and the [preview sheets](../../../artifacts/v0.7.0rc1/review) support independent review.

| Files | Chosen decisions and alternative considered | Verification evidence |
| --- | --- | --- |
| `cooler-route-evidence.json` | D01, D03, D04, D06, D08, D13. Continue the title into the evidence. Counter the large standalone cover with a smaller locating image and a larger action-page illustration. Give evidence the first page and implementation its own entry. | Two pages. All route counts, summary and the three bars stay together. Both approved images and their editable captions match the baseline. The [record](records/cooler-route-evidence.json) tracks the spilled total and its correction. |
| `cooler-route-place.json` | D01, D02, D05, D06, D12, D15. Give the place image the largest region and a page of its own. Use a smaller right-aligned title, a panel entry for findings and a compact supporting action image. The other concept prioritizes the measurement. | Two pages. The second page carries evidence and actions. The [record](records/cooler-route-place.json) tracks the correction to label and value alignment. |
| `edge-of-the-water.json` | D01–D05, D07, D12–D13. Use one art-led entrance, asymmetry for orientation, a large study, a dense index, same-scale views and a quiet exercise. The alternative was a repeated print-and-label sequence. | Six pages. Readers see the cover print together with its title, then compare two 134 mm views. The index and closing exercise use quieter pages. The [record](records/edge-of-the-water.json) tracks the initial split cover. |
| `rolling-window.json` | D04, D08–D10, D14. Use the precise update itself as the visual idea. Prefer a native explanation and trace to a conceptual illustration. Keep the listing and practice on the second page. | Two pages with exact Python, three checked values, a native sequence and practice with feedback. Zero layout corrections. Word mode 15 and the Accessibility Assistant were checked on this lesson. |
| `reading-room-booking.json` | D02, D04, D07, D11. Compose a single document around identity, access, charges and reply. Use a narrow metadata rail and quiet space. No illustrative subject serves this reader task. | One page. Dates and response details are easy to locate in the rendered page. Native columns present the checked £155.00 total. Zero layout corrections. |

There are five matching final DOCX names. The three `intermediate` briefs reproduce the corresponding `-initial.docx` artifacts. Both route comparisons share the frozen v0.6.0rc1 report, including its image and source text order. Review the two report sheets before opening the stage records or candidate verification if you want a blinded comparison. Record first focal point, ease of finding evidence and the action, preference, and any visible defect. Distinguish intended whitespace from missing material or accidental spill.

## Generate the documents

From the project root, run the normal CLI with a new local output directory. Choose a different directory for additional runs.

```powershell
$root = (Get-Location).Path
$base = 'examples/benchmarks/design-knowledge'
New-Item -ItemType Directory .tools/design-knowledge-reproduction
$assets = [ordered]@{
    'cooler-route-evidence' = 'examples/benchmarks/creative/assets/manifest.json'
    'cooler-route-place' = 'examples/benchmarks/creative/assets/manifest.json'
    'edge-of-the-water' = "$base/assets/manifest.json"
    'rolling-window' = $null
    'reading-room-booking' = $null
}
$approved = @{
    'examples/benchmarks/creative/assets/manifest.json' = '754b9b648552f01659071528a43abffcbdfe775b6b48f6c164fd6fec853fee6f'
    "$base/assets/manifest.json" = '2a765a55978a9940ec41e1085a61ceadd187b3269ab5ba896d7fe862c07995fc'
}
foreach ($name in $assets.Keys) {
    $options = @()
    if ($manifest = $assets[$name]) {
        $options = @('--asset-manifest', $manifest, '--asset-manifest-sha256', $approved[$manifest])
    }
    python -E -s -B skills/kmdstudio/scripts/generate.py --root $root --spec "$base/$name.json" --output ".tools/design-knowledge-reproduction/$name.docx" @options
    if ($LASTEXITCODE) { throw "Generation failed for $name" }
}
python -E -s -B tools/verify_bundle.py --archive artifacts/v0.7.0rc1/kmdstudio-0.7.0rc1.zip
```

The three new art inputs come from [make_art.py](make_art.py) using the existing optional Pillow environment. The figures are original geometric study prints, with pale and dark bands giving each contour a distinct reading task. Output is unlabeled, RGB and landscape at 5:3. This avoids needing to cut away the contour for the cover, the detail or the comparison. Recreate the source PNGs in a new directory, open and inspect them, then run the normal `import_raster.py` workflow with `--origin authorized-local` and credit `KMDStudio original geometric study, make_art.py`. Compare the resulting bytes with the pinned [manifest](assets/manifest.json) before using them for generation. Runtime receives only the reviewed assets. No asset inside the installed skill changed.

## Render the sheets

With an authorized local QA renderer and Ghostscript, convert the five final DOCX files and the v0.6.0rc1 report under a disposable Writer profile. Use an absolute profile URI passed as `-env:UserInstallation=<file-uri>` and `--headless --convert-to pdf --outdir <local-qa-folder>`. Rasterize each diagnostic PDF with `-dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -r120 -sOutputFile=<pages>/<document-name>/page-%02d.png`. Supply that pages directory and a fresh output folder to `make_review.py` in the existing Pillow environment. Diagnostic PDF stays local. Use [the project review tool](../../../tools/review_word.ps1) with authorized Word and an SDK assembly for independent structure and pagination evidence.

## Owner holdout

1. The owner chooses one unseen task after the candidate is fixed. Retain the exact prompt, fixtures, rights, reference scope and SHA-256 digests in a local workspace. Freeze required facts, exact passages and code, target viewer, task-specific visual criteria, and pass or fail structural gates before looking at results.
2. Qualify a separately authorized standalone agent environment with the randomized local-tool gate in [evals](../../../evals/README.md). Record the user-approved model, tools, permissions and time budget. Use identical inputs and budgets for ordinary, 0.6.0rc1, and candidate arms. Preserve the bounded runner and judge. The owner case needs a matching fixture and exact-content rubric before scoring. Keep its raw data and traces in the approved workspace.
3. Require successful fixture access, completed artifact, editable source fidelity, mandatory acceptance and, in the skill arms, activation evidence. Report token usage only if the completed traces supply it. Record elapsed time and number of corrections.
4. Render all qualifying outputs on the same host. Randomize anonymous labels while keeping the key private until the owner evaluates the frozen criteria. Record preference and objective defects separately. A holdout with an unavailable host, missing artifacts or failed activation has no measured agent effectiveness.
