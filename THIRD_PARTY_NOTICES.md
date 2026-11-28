# Third-party notices

## Bundled artwork

The included PNGs are recolored, locally rasterized derivatives of two line icons from [Lucide 0.468.0](https://github.com/lucide-icons/lucide/tree/0.468.0). The code icon is ISC and the right arrow derives from MIT-licensed Feather. The [manifest](skills/kmdstudio/assets/manifest.json) records source paths, version, integrity hashes and licenses. See the [Lucide notice](skills/kmdstudio/assets/licenses/lucide.txt) and the [Feather MIT notice](skills/kmdstudio/assets/licenses/feather.txt). The derivative script uses explicit geometry reviewed against the tagged upstream paths.

## Local tooling

| Component | Role | Terms and provenance |
| --- | --- | --- |
| CPython 3.11+ | Base runtime, including XML, JSON, ZIP, tokenization and subprocess support | [Python Software Foundation license](https://docs.python.org/3/license.html). Use an official, patched interpreter. |
| pypdf 7.2.0 | Optional PDF structure check, Python 3.10+ and no mandatory dependencies on supported versions | BSD-3-Clause, [PyPI release and upstream wheel attestation](https://pypi.org/project/pypdf/7.2.0/). |
| Pillow 13.0.0 | Optional PNG and JPEG decoder, Python 3.11+ with no mandatory Python dependencies | MIT-CMU, [PyPI files and provenance](https://pypi.org/project/pillow/13.0.0/#files), [upstream license](https://github.com/python-pillow/Pillow/blob/13.0.0/LICENSE). Published x86-64 wheels are pinned for Windows and Linux. |
| LibreOffice | Operator-provided optional renderer, excluded from the skill package | [LibreOffice licensing](https://www.libreoffice.org/about-us/licenses/). The tested Windows artifact came from The Document Foundation. |
| PyYAML 6.0.4 | Development check with the official skill-creator validator | MIT, [PyPI Windows CPython 3.15 wheel](https://pypi.org/project/PyYAML/6.0.4/), no mandatory transitive packages. |
| Ruff 0.17.6 | Development lint | MIT, [PyPI Windows x86-64 wheel](https://pypi.org/project/ruff/0.17.6/), no mandatory transitive packages. |

Windows fonts referenced by the examples are system resources. Their original font files are not included. Review renderer embedding permissions when choosing a font. See [font research](docs/RESEARCH.md).

The [study vessel](examples/benchmarks/visual-intelligence/assets/study-vessel.png) is original synthetic artwork generated with OpenAI ImageGen for this project. The [benchmark notes](examples/benchmarks/visual-intelligence/README.md) record the prompt and import provenance. It depicts a fictional object.
