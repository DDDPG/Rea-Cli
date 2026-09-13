"""Publication remains explicit and gated by recorded source/ownership resolutions."""

import json, os
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "docs/ecosystem/publication.json"
r = json.loads(p.read_text())
required = (
    "source_permissions_resolved",
    "package_ownership_verified",
    "trusted_publishing_configured",
)
missing = [key for key in required if r.get(key) is not True]
if missing:
    raise SystemExit("Publication prerequisites unresolved: " + ", ".join(missing))
if os.environ.get("TARGET") == "pypi" and (
    os.environ.get("GITHUB_REF_TYPE") != "tag"
    or not os.environ.get("GITHUB_REF_NAME", "").startswith("ecosystem-v")
):
    raise SystemExit("Production requires an ecosystem-v release tag")
