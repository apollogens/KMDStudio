# KMDStudio 0.2.0

KMDStudio is a standalone Agent Skill for designed, editable A4 documents. The KMDStudio Design Language (KDL) defines six visual profiles with bounded semantic overrides. A single generator converts a JSON brief into verified DOCX. An optional LibreOffice path exports a structurally checked PDF on a host with verified isolation.

## Use locally

Run the following from the project root in PowerShell with Python 3.11 or newer on PATH. If Python is available only by absolute path, use that path for the first command.

```powershell
python -m venv .venv
$python = '.venv/Scripts/python.exe'
& $python -E -s -B skills/kmdstudio/scripts/generate.py --root (Get-Location).Path --spec examples/benchmarks/python-oop-lecture.json --output artifacts/lecture-local.docx
& $python -E -s -B -m unittest discover -s tests -v
```

Use a new output name in an existing directory. Keep brief and output paths relative to the authorized root. See the [brief contract](skills/kmdstudio/references/workflow.md), [design reference](skills/kmdstudio/references/design.md), and [benchmark inputs](examples/benchmarks).

### Codex discovery

The canonical source is [skills/kmdstudio](skills/kmdstudio). To activate it with a reference in the current session, ask Codex to use `skills/kmdstudio/SKILL.md` for the task. To enable normal discovery, an operator with write access to the repository's configuration can create a repo-local junction pointing to the reviewed source, then reload Codex. The junction is a discovery entry. Generation inputs and outputs still reject reparse points.

```powershell
$skillSource = (Resolve-Path -LiteralPath 'skills/kmdstudio').Path
New-Item -ItemType Directory -Path '.agents/skills' -Force | Out-Null
New-Item -ItemType Junction -Path '.agents/skills/kmdstudio' -Target $skillSource
```

Leave an existing discovery entry untouched until you verify what it points to. A plain copy of the skill folder is also suitable when junctions are unavailable. Update any discovery copy from the canonical source after changes. Invoke `$kmdstudio` explicitly or request a designed Word document to exercise implicit activation. [Codex skill discovery](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)

### Optional PDF

Install the hash-pinned PDF validator into the project virtual environment as a separate development step. Use approved official PyPI access or a reviewed local wheelhouse. Use a trusted LibreOffice executable inside a host sandbox with restricted network and filesystem access.

```powershell
& $python -I -B -m pip --isolated --disable-pip-version-check install --index-url https://pypi.org/simple --require-hashes --only-binary=:all: -r skills/kmdstudio/requirements-pdf.lock
& $python -E -s -B skills/kmdstudio/scripts/render_pdf.py --root (Get-Location).Path --spec examples/python-oop-lecture.json --output artifacts/lecture-local.pdf --renderer 'C:/trusted/LibreOffice/program/soffice.com'
```

The [v0.2.0 artifacts](artifacts/v0.2.0) include three editable DOCX files, comparison previews, and the portable skill ZIP. See [verification evidence](docs/VERIFICATION.md), [architecture](docs/ARCHITECTURE.md), and [security and reporting](SECURITY.md). The project license remains an owner decision before external release. Third-party terms are recorded in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
