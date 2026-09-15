"""Check normal publication and explicit first-project TestPyPI bootstrap gates."""

from __future__ import annotations

import json
import os
from pathlib import Path

PUBLICATION_PATH = Path(__file__).resolve().parents[1] / "docs/ecosystem/publication.json"
REQUIRED = (
    "source_permissions_resolved",
    "package_ownership_verified",
    "trusted_publishing_configured",
)


class PublicationGateError(ValueError):
    """Raised when a publication mode is not authorized by the manifest."""


def evaluate(
    publication,
    *,
    target="",
    package="",
    mode="normal",
    ref_type="",
    ref_name="",
):
    """Validate one workflow invocation against the recorded publication state."""

    if mode not in ("", "normal", "testpypi-bootstrap"):
        raise PublicationGateError("Unknown publication mode: " + mode)

    if mode == "testpypi-bootstrap":
        if target != "testpypi":
            raise PublicationGateError(
                "TestPyPI bootstrap requires TARGET=testpypi"
            )
        if publication.get("source_permissions_resolved") is not True:
            raise PublicationGateError(
                "Publication prerequisites unresolved: source_permissions_resolved"
            )
        config = (
            publication.get("bootstrap_publish", {})
            .get("testpypi", {})
            .get(package, {})
        )
        if not package or config.get("allowed") is not True:
            raise PublicationGateError(
                "TestPyPI bootstrap not authorized for package: "
                + (package or "<missing>")
            )
        return

    missing = [key for key in REQUIRED if publication.get(key) is not True]
    if missing:
        raise PublicationGateError(
            "Publication prerequisites unresolved: " + ", ".join(missing)
        )
    if target == "pypi" and (
        ref_type != "tag" or not ref_name.startswith("ecosystem-v")
    ):
        raise PublicationGateError("Production requires an ecosystem-v release tag")


def main():
    publication = json.loads(PUBLICATION_PATH.read_text(encoding="utf-8"))
    try:
        evaluate(
            publication,
            target=os.environ.get("TARGET", ""),
            package=os.environ.get("PACKAGE", ""),
            mode=os.environ.get("MODE", "normal"),
            ref_type=os.environ.get("GITHUB_REF_TYPE", ""),
            ref_name=os.environ.get("GITHUB_REF_NAME", ""),
        )
    except PublicationGateError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
