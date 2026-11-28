"""Check the installed CI dependency versions against OSV advisories."""

import json
from importlib.metadata import version
from urllib.request import Request, urlopen


def main():
    dependencies = {name: version(name) for name in ("Pillow", "pypdf", "ruff")}
    queries = [{"package": {"ecosystem": "PyPI", "name": name}, "version": value}
               for name, value in dependencies.items()]
    request = Request("https://api.osv.dev/v1/querybatch",
                      data=json.dumps({"queries": queries}).encode("utf-8"),
                      headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=20) as response:
        data = response.read(1024 * 1024 + 1)
    if len(data) > 1024 * 1024:
        raise ValueError("OSV response exceeds the size limit")
    results = json.loads(data)["results"]
    if len(results) != len(queries):
        raise ValueError("OSV result count differs from the request")
    failed = False
    for (name, value), result in zip(dependencies.items(), results):
        advisories = [item["id"] for item in result.get("vulns", [])]
        if advisories:
            failed = True
            print(f"{name} {value} FAIL {', '.join(advisories)}")
        else:
            print(f"{name} {value} PASS no matching OSV advisories")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
