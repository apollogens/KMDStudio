# Font evidence for 0.6.0rc1

The Windows [font probe](../tools/check_fonts.ps1) asks WPF for the named system families. It checks non-simulated upright faces and representative Latin, Russian Cyrillic, digit, code and technical glyphs. It reports the local face version and embedding flags. The probe adds no dependency to the generator and does not configure the renderer. An available face can still be substituted by a particular application. [Microsoft GlyphTypeface documentation](https://learn.microsoft.com/en-us/dotnet/api/system.windows.media.glyphtypeface)

| Requested role | Host evidence | Actual Writer rendering |
| --- | --- | --- |
| Report display and metric | Cambria 6.99 regular, 6.98 bold. Both cover all sampled categories. | Cambria regular at 60 and 54 pt. The earlier report used Georgia 62 and 54 pt. |
| Report body and section headings | Calibri 6.27 regular and bold. Both cover all sampled categories. | Calibri 12 pt body and 28 pt bold heads. The earlier report used Arial. |
| Lesson display and headings | Verified Calibri Bold and Cambria Bold. | Calibri Bold 46 pt Cyrillic title with Cambria Bold 25 pt headings. The earlier request for Literata resolved to Georgia Bold 58 pt. |
| Lesson code | Consolas 7.01 regular and bold. Both cover all sampled categories. | Consolas 10 pt on the exact SQL listing. |
| Baseline alternates | Arial 7.07 regular/bold and Arial Black 5.23 cover the sample. Georgia 5.59 regular/bold lacks sampled `U+2192` and `U+2193`. | The report still uses Arial Bold for small metadata labels. Georgia is suitable for sampled display text; choose an arrow-capable face where the arrow glyphs are required. |

The selected Windows faces report editable embedding flags. The generated DOCX references those faces by name. Microsoft documents separate terms for distributing font files and document embedding. Record the actual target application's substitutions before qualifying another host. [Microsoft font redistribution and embedding FAQ](https://learn.microsoft.com/en-us/typography/fonts/font-faq)

## Reviewed open candidates

Read the official Google Fonts metadata and adjacent `OFL.txt` files at commit [`5026800714d07231937d92eb4cceabf06e05d74e`](https://github.com/google/fonts/tree/5026800714d07231937d92eb4cceabf06e05d74e/ofl). Each candidate declares Latin and Cyrillic subsets and SIL Open Font License 1.1. Published variable weight ranges include 400 and 700. These metadata ranges describe the referenced source. An application still needs to expose and render the intended instances. None of the nine named open families was found as a matching regular or bold face on the tested host.

| Family | Source revision | Published weight axis | Potential role |
| --- | --- | --- | --- |
| Manrope | [`6f81ebecdf65e4463b798cc07b16a4f8d5216917`](https://github.com/googlefonts/manrope/tree/6f81ebecdf65e4463b798cc07b16a4f8d5216917) | 200–800 | Geometric display or metadata |
| Onest | [`8739b1910618a15335e4cc48842052d0ee739ade`](https://github.com/simpals/onest/tree/8739b1910618a15335e4cc48842052d0ee739ade) | 100–900 | Contemporary prose and labels |
| Golos Text | [`58e7cb1b36693c4d017c33c2c52dc60027449053`](https://github.com/googlefonts/golos-text/tree/58e7cb1b36693c4d017c33c2c52dc60027449053) | 400–900 | Cyrillic text and headings |
| Inter | [`66647c0bbbe41a850d79d9c76fb13add3378940f`](https://github.com/rsms/inter/tree/66647c0bbbe41a850d79d9c76fb13add3378940f) | 100–900 | Structured sans and data text |
| Unbounded | [`f3ec43228a864a72487e41552e2140efab9884ea`](https://github.com/googlefonts/unbounded/tree/f3ec43228a864a72487e41552e2140efab9884ea) | 200–900 | Short, wide display |
| Geologica | [`685f38d7c9e86b0c8530204c97ddcaf6558dd17b`](https://github.com/googlefonts/geologica/tree/685f38d7c9e86b0c8530204c97ddcaf6558dd17b) | 100–900 | Display and editorial labels |
| Literata | [`0c2761b727a1b3a7cffd313c37f0f5163dfc7a63`](https://github.com/googlefonts/literata/tree/0c2761b727a1b3a7cffd313c37f0f5163dfc7a63) | 200–900 | Editorial serif prose and display |
| IBM Plex Sans | [`3e312890b3b9e47378b30dedfe4196a42151243c`](https://github.com/googlefonts/plex/tree/3e312890b3b9e47378b30dedfe4196a42151243c) | 100–700 | Documentation and analytical tables |
| JetBrains Mono | [`19371302b95d218af43299bce79ddbddd0bc364d`](https://github.com/JetBrains/JetBrainsMono/tree/19371302b95d218af43299bce79ddbddd0bc364d) | 100–800 | Code |

OFL 1.1 permits embedding in documents and redistribution under its terms, including preserving notices when distributing font software and observing Reserved Font Names for modified distributions. The pilot checked metadata and license text. It did not acquire binaries or verify these candidates' glyph maps, embedding flags, Word variable-weight behavior or actual render. Unbounded and Geologica remain research candidates outside the current allowlist. [SIL OFL FAQ](https://openfontlicense.org/ofl-faq/)

When qualifying an open face, have the operator choose the exact reviewed package and renderer environment. Verify its digest, license, real regular and bold instances and glyph requirements outside the core. Qualify with a small rendered specimen, then pass `--available-font` for the verified family where the brief uses it. Preserve the default family fallback when this evidence is unavailable.
