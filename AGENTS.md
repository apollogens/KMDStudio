# KMDStudio development

- Keep the canonical, self-contained skill under `skills/kmdstudio`.
- Use English for code and technical documentation. Keep each fixture in its intended document language.
- Update the schema, content verification, and security checks together when adding a component.
- Run `python -E -s -B -m unittest discover -s tests -v` before handing off changes. Check output from the normal CLI for changes to generation, and render changed examples when a suitable host is available.
- Keep dependencies and asset changes explicit. Follow [SECURITY.md](SECURITY.md) and the host's permissions.
