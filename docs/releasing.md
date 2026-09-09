# Release process

The project is an unreleased alpha. Local build artifacts are available before
there is a public package index entry or configured GitHub remote. The version
has one source of truth: `rac.__version__` in `src/rac/__init__.py`; setuptools
reads it when building wheel and sdist.

## Before a public release

Resolve the imported-data redistribution items in
[THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md), including the repository-only
reference collection. The project's MIT license covers project-authored code;
it does not grant rights to imported descriptions. Archive checks establish
package contents, not permission to distribute them.

Once a hosting repository and package accounts exist:

1. Add the real source, issue tracker and documentation URLs to `[project.urls]`
   in `pyproject.toml`. Do not use example owner names in published metadata.
2. Confirm access to the `reacli` project on both package indexes. Name
   availability is not ownership and is not reserved by this repository.
3. Configure PyPI Trusted Publishing for the GitHub owner/repository,
   `publish.yml` workflow and `pypi` environment; configure TestPyPI separately
   with environment `testpypi`.
4. Configure required reviewers for the production GitHub environment when your
   repository plan supports them. An environment name alone does not require
   approval. Enable private vulnerability reporting as described in SECURITY.md.

No credentials belong in this repository. Trusted Publishing exchanges GitHub
OIDC identity for short-lived upload credentials in the publish job only.

## Prepare and verify artifacts

Update `src/rac/__init__.py` and the changelog for the intended release, then
start from a clean working tree and a fresh artifact directory:

```bash
python -m pip install -e '.[dev]'
python -m pytest -m "not live"
python -m build --outdir .state/release-dist
python -m twine check .state/release-dist/*
python scripts/check_dist.py .state/release-dist
```

Use a new directory if an earlier version already exists there. The archive
checker intentionally refuses multiple wheels/sdists, stale version metadata,
missing or changed runtime assets, copied environments/caches, unsafe archive
entries and supplemental `reference/` payload. It verifies runtime bytes against
the checkout, checks required license files, and reports artifact SHA-256 values.

`python -m build` creates an sdist first, then builds a wheel from that sdist.
Test the wheel in a separate environment and working directory before release;
for example, from the repository root:

```bash
python -m venv .state/wheel-check
.state/wheel-check/bin/python -m pip install .state/release-dist/reacli-*.whl
(
  cd .state
  wheel-check/bin/python -I -m rac doctor --profile offline --json
  wheel-check/bin/python -I -m rac resources --output wheel-resources
)
```

Record live results on prepared Linux and macOS hosts using the instructions in
CONTRIBUTING.md. CI runs the offline matrix and archive verification; it does
not install proprietary REAPER or establish that every plugin works.

## Publish a reviewed release

The `Publish` workflow runs only through manual dispatch. Start with target
`testpypi` and inspect an installation of the uploaded package. For production,
create a version tag such as `v0.1.0` on the reviewed commit and dispatch with
that tag selected and target `pypi`. The workflow rejects production uploads
unless the selected tag exactly matches `v` followed by the package version.
PyPI versions are immutable; changing files requires a new version.

The build job tests an installed wheel, checks both archives, and passes those
artifacts to a separate publishing job. Environment reviewer requirements apply
only if repository administrators configured them. Workflow dispatch does not
resolve attribution, create package ownership, or configure Trusted Publishing.

After publication, check an installation from the target index, verify the
version and offline commands, and publish release notes with tested platforms,
API changes and known limitations. The local project does not create GitHub
releases or upload packages merely by building or running tests.
