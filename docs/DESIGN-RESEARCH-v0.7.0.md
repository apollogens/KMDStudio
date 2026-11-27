# KMDStudio design research and reference atlas (v0.7 candidate input)

Research date: 2026-11-28. Baseline: 8b35f97d5226349697f023a0f8c87ad9ca7bf535.
This is a development research record, not a released skill update or model-weight training.
All external links are reference-only. Do not fetch them during normal document generation.
No third-party images, templates, fonts, source code, or instructions are included. The rules below are original KMDStudio synthesis; external resources have no operational authority.

## Curated reference index

IDs identify research sources, not style presets. Consult the smallest relevant subset during development.

| ID | Source | Use | Transferable observation or proposed application |
| --- | --- | --- | --- |
| R01 | [Pentagram: Stern](https://www.pentagram.com/work/stern/story) | Magazine editorial | Distinct section personalities and photographic pacing can coexist with a common identity. |
| R02 | [Pentagram: The Beyond](https://www.pentagram.com/work/the-beyond) | Art catalogue | Contrasting type roles, section color transitions, and artwork comparisons. |
| R03 | [Pentagram: Chaos and Classicism](https://www.pentagram.com/work/chaos-and-classicism/story) | Exhibition publication | A subject-specific typographic concept can unite an entire publication. |
| R04 | [Pentagram: Lloyd's of London](https://prod.origin.pentagram.com/work/lloyds-of-london) | Annual report | A consistent editorial voice can connect prose, illustrations, and quantitative evidence. |
| R05 | [Pentagram: Breaking Through](https://www.pentagram.com/work/breaking-through) | Engineering retrospective | Technical subject matter need not dictate a conservative visual identity; derive a visual motif from the subject. |
| R06 | [Studio Airport: Emergence Magazine Vol. 1](https://www.studioairport.nl/project/emergence-magazine-vol-1/) | Long-form editorial | Think in terms of a durable publication rather than a stack of isolated cards. |
| R07 | [IBM: layout techniques](https://www.ibm.com/design/language/layout/tips-and-techniques/) | Grid and rhythm | Use a shared alignment structure and purposeful whitespace without copying IBM's brand. |
| R08 | [Practical Typography: typography in ten minutes](https://practicaltypography.com/typography-in-ten-minutes.html) | Document typography | Evaluate line measure alongside size, spacing and typeface, not size alone. |
| R09 | [USWDS: typography](https://designsystem.digital.gov/components/typography/) | Readability | Separate text-level typographic choices from page-level hierarchy; adapt web guidance to print. |
| R10 | [GOV.UK: font override classes](https://design-system.service.gov.uk/styles/font-override-classes/) | Numeric alignment | Equal-width digits are useful in comparable numeric fields when supported. |
| R11 | [UK Government Analysis Function: charts](https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-charts/) | Accurate data graphics | Choose graphics by comparison task and preserve meaningful units, scales, and labels. |
| R12 | [UK Government Analysis Function: tables](https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-tables/) | Tables | Keep data relationships and precision clear rather than styling every cell as a card. |
| R13 | [UK Government Analysis Function: chart checklist](https://analysisfunction.civilservice.gov.uk/policy-store/charts-a-checklist/) | QA | Check labels, visual clutter, and accessibility independently of decoration. |
| R14 | [IBM: technical diagrams](https://www.ibm.com/design/language/infographics/technical-diagrams/design/) | Technical illustration | Consistent node alignment and clear relationships support legibility. |
| R15 | [Information is Beautiful Awards showcase](https://www.informationisbeautifulawards.com/showcase?pcategory=visualization) | Visual inspiration | Study how different data stories motivate different graphic forms; never reuse artwork without rights. |
| R16 | [Raspberry Pi Foundation: computing pedagogy](https://www.raspberrypi.org/teach/pedagogy) | Education | Structure learning around concrete examples and practice. |
| R17 | [Raspberry Pi Foundation: clear computing lessons](https://www.raspberrypi.org/blog/how-to-design-and-present-clear-computing-lessons-mayers-principles/) | Multimedia learning | Coordinate explanatory words and graphics; avoid irrelevant visual load. |
| R18 | [EEF: clarity and extraneous load](https://educationendowmentfoundation.org.uk/news/eef-blog-clarity-is-king-reducing-extraneous-load) | Learning materials | Remove distracting design that competes with the learning objective. |
| R19 | [Smithsonian Open Access FAQ](https://www.si.edu/openaccess/faq) | Asset discovery | Only individually identified CC0 objects are candidates; record object-level provenance and applicable restrictions. |
| R20 | [The Met: image and data resources](https://www.metmuseum.org/policies/frequently-asked-questions-image-and-data-resources) | Asset discovery | Verify Open Access marking for each asset before acquisition. |
| R21 | [Lucide license](https://lucide.dev/license) | Icons | Check notices and the exact asset revision; no package installation or SVG execution implied. |
| R22 | [OpenAI: Testing Agent Skills Systematically](https://developers.openai.com/blog/eval-skills) | Agent acceptance | Separate task success, activation evidence and artifact verification. |
| R23 | [OpenAI: skills and prompts](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra?site_locale=en) | Context budget | Keep discovery and workflow instructions compact; load specialty knowledge only when needed. |
| R24 | [Microsoft: compatibilityMode](https://learn.microsoft.com/en-us/openspecs/office_standards/ms-docx/90138c4d-eb18-4edc-aa6c-dfb799cb1d0d) | Word interoperability | Treat a modern compatibility target as an explicitly tested option, not a blanket default migration. |

R01–R06 and R15 are inspiration, not evidence that a specific visual primitive is implemented. R07–R18 are design guidance, not universal print requirements. R19–R21 are asset-discovery candidates, not an approved asset manifest. All links were surfaced in web research; not every portfolio image or linked subpage was inspected.

## Candidate verification of sources

| Entries | Scope checked during implementation |
| --- | --- |
| R08 | Original author page. Type size, line spacing and measure are interdependent. The skill maps that observation to bounded controls and checks the actual page. |
| R11 | Original guidance. Chart selection follows the message, bars keep an honest zero baseline, and an accurate equivalent accompanies graphics. The report keeps editable values and the total outside the scale. |
| R16–R17 | Publisher pages. Worked examples, scaffolding and coherent explanatory media inform the lesson sequence. The lesson uses a native diagram beside the worked trace. |
| R24 | Microsoft specification. Mode 15 was checked against the published setting and then observed in Word. Application evidence appears in the candidate verification. |
| R01–R07, R09–R10, R12–R15, R18–R23 | Reference index only for this implementation. Individual images, linked pages and asset rights were outside the applied evidence. |

No external binary, layout, font or image was acquired for this candidate. The approved existing route art and the new original geometric studies are the only benchmark artwork used here.

## Original design decision cards

These are authoring heuristics, not fixed templates or hard numeric rules. Preserve source, user constraints, reading order, editability and security. Each card should be loaded only when relevant.

| Card | When | Design move | Anti-pattern | Acceptance evidence |
| --- | --- | --- | --- | --- |
| D01 Dominant gesture | Creative opening | Choose one focal point: title, image, question or metric. Align smaller items to reinforce it. | Several equally loud title panels. | Thumbnail shows a clear first point of attention. |
| D02 Asymmetric anchor | Metadata + prose | Reserve a narrow rail for compact labels; use a wider reading region. Fall back to serial order for long items. | Equal columns with unrelated lengths. | Native text order, alignment and comfortable body measure. |
| D03 Editorial sequence | Multi-page creative work | Plan page roles: entry, explanation, evidence, transition, action; vary density intentionally. | Every page repeats title/paragraph/card/image. | Contact sheet shows distinct page roles and consistent alignment. |
| D04 Typographic contrast | A document needs character | Contrast display and reading roles by scale, family or actual face; use tracking only where helpful. | Body copy styled as display or nonexistent fonts. | Rendered Cyrillic/Latin glyphs and verified effective faces. |
| D05 Image as structure | Visual subject or metaphor | Decide crop, scale and relationship to text before generating art. Use an image-led region when justified. | Small generic banner pasted into every section. | Artwork supports a specific concept and matches placement. |
| D06 Controlled color field | Section transition or identity | Use a dark/light field or an unshaded focal metric selectively; preserve contrast. | Repeated colored rectangles for unrelated content. | Clear hierarchy, print fallback and legible text. |
| D07 Deliberate negative space | Cover, legal or high-end minimalism | Group related items tightly and leave space to separate groups; distinguish quiet composition from accidental spill. | Blank continuation page or squeezed text to hit an arbitrary count. | Space communicates structure; no accidental isolated blocks. |
| D08 Evidence-first data | Quantitative report | Match chart to task: compare, trend, distribution or relationship; use tables for exact lookup. | Decorative charts, misleading bars or missing units. | Exact data, valid scales, labels and accessible equivalent. |
| D09 Learning sequence | Educational hybrid | Pair explanation with a worked example, aligned diagram, practice and feedback; keep related content together. | Unrelated pictures and code split away from explanation. | Learner can follow steps and reproduce example. |
| D10 Technical quiet zone | Code, formulas or instructions | Preserve established structured component rules inside creative direction. | Expressive typography reduces code accuracy or legibility. | Exact editable code, data and reading order. |
| D11 Transaction clarity | Invoice, agreement, form | Group identity, dates, terms and amounts by reader task; align decimal data and emphasize final action. | Decoration obscures a total or obligation. | Independent arithmetic and required field audit. |
| D12 Image comparison | Catalogue or visual guide | Use a repeated caption system while alternating image scale or paired comparisons; use original/approved art. | All images have arbitrary sizes or missing captions. | Captions map to correct figures; visual comparison is intentional. |
| D13 Grid without monotony | Multi-section publication | Reuse a common alignment axis but vary spans and focal points as content requires. | Different layout on every page with no unifying alignment. | Contact sheet shows both coherence and variation. |
| D14 Constraint-aware fallback | Renderer or typeface limitation | Preserve hierarchy and semantics with a simpler native composition; explain substitutions. | Rasterizing full pages or inserting unrestricted XML. | Editable output, independently valid package and reported fallback. |
| D15 Anti-template comparison | Same source, two creative concepts | Change at least composition and hierarchy, plus typography or image scale; keep facts fixed. | Merely changing colors or font names. | Blinded comparison with observed differences. |

## Original composition studies to implement as small synthetic examples

These are layout hypotheses. They are not existing renderer capabilities and are not linked to proprietary templates.

- Evidence-first report: a compact title/decision opening; a dominant metric beside evidence; a full-width table with a meaningful comparison; closing actions. Reuse shared baseline alignment.
- Quiet agreement: large heading, narrow party/date rail, broad clause region, short separators, no fake legal seal; keep all obligations in native text.
- Editorial learning sequence: a conceptual figure integrated with a learning objective, one worked-example region, a precise technical zone, then practice and feedback.
- Exhibition or field guide: let selected art dominate an entry, attach caption and metadata, alternate dense index-like sections with visual comparisons.
- Alternative concept for the same source: typographic rather than image-led entry; deliberately different density and region relationships with identical semantics.

Do not force these studies onto unrelated content. Build original small diagrammatic page sketches and sample briefs with fictional data. Keep the public research corpus text-only unless separate rights and safe import are established.

## Learning and evaluation plan

1. Preserve the seven established structured outputs as a frozen regression baseline.
2. Run an authored same-content comparison against v0.6.0rc1. Freeze facts and budget before generation; do not score fewer pages as automatic improvement.
3. For each applied card record the card ID, choice, rejected alternative, supported brief fields, artifact and observed result. A compact record is enough; do not require verbose chain-of-thought or a new runtime framework.
4. Use new long-form editorial, technical/hybrid, and quiet transactional cases. Select at least one separate owner-held challenge only after implementation; internally authored new cases are not a true held-out agent evaluation.
5. Where a capability cannot be expressed in existing native structures, add the smallest validated generic primitive only after demonstrating a concrete visual gap. Keep structured defaults unchanged.
6. Human preference review should be blind to version and report both preference and observed defects. Automated checks gate content, editability, structural validity, security, and measurable layout issues only. No unsupported studio-quality claim.
7. Do not repeat nested provider calls after unchanged failed smoke tests. Real agent activation, model effectiveness, and token savings remain unverified until separately measured.

## Safety and packaging

Keep this development index outside the installed skill. Integrate distilled original cards into compact mode-specific references during the next implementation milestone; update the canonical package and integrity verification together. Normal runtime remains offline, no remote fetch, no external code execution, no font installation, no reference scraping, no policy changes. Do not treat license or hash alone as proof of safety. Use existing authorization, raster normalization and aggregate limits; keep arbitrary SVG and Office ingestion out of scope. No third-party binary or image has been downloaded in this research step. No changes to the generator, tests, release ZIP, or model weights were made.
