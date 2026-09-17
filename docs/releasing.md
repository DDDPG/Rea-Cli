# Ecosystem release candidates

The monorepo builds independent `reaper-parser` and `reacli` distributions.
Follow [the ecosystem guide](ecosystem/README.md) for installation and validation.

## Current release record

As of 2026-09-17, PyPI serves `reacli==0.1.0` and
`reaper-parser==0.1.0a1`, each as a wheel and source distribution. The exact
files, sizes, upload times and SHA-256 digests are recorded in
[`publication.json`](ecosystem/publication.json). The existing PyPI files are
immutable; changes to package metadata or README content require a new version.
The reviewed checkout contains post-upload runtime hardening and generated-data
privacy cleanup, so its runtime is intentionally newer than those immutable files;
do not reuse either published version for the next upload.

### Next release: version bump checklist

`reacli==0.1.0` and `reaper-parser==0.1.0a1` are immutable. The next upload must
use new version numbers — `reacli==0.1.1` and `reaper-parser==0.1.0a2` are the
planned pair, since the parser keeps its pre-release marker until its upload
channel is independently evidenced. Bump both together; `reacli` pins
`reaper-parser>=0.1.0a1,<0.2`, so a parser-only bump still satisfies the pin but
leaves the pair out of step.

Update every version reference in the same change:

- `packages/reacli/src/rac/__init__.py` (`__version__`, the single source for the
  `reacli` distribution version)
- `packages/reaper-parser/pyproject.toml` (`[project] version`)
- `packages/reacli/pyproject.toml` (the `reaper-parser` dependency pin)
- `integrations/agents/reaper-agent-cli/compatibility.json` (`reacli`,
  `reaper-parser`, and `bundle_version`)
- `CHANGELOG.md` (new section) and both READMEs
- `docs/ecosystem/publication.json` and `publication-audit.md` (recorded release
  facts) — add the new artifacts, do not rewrite the 0.1.0/0.1.0a1 records

`tests/test_distribution.py` and `scripts/check_dist.py` verify that package
metadata stays tied to `rac.__version__`; run them before building.


1. Install both packages and their development/audio extras; run the offline suite.
2. Run `python tools/generate_schema.py --check`.
3. Install website dependencies with `npm ci --prefix apps/reaperdoc`.
4. Run `python tools/build_release.py --output dist/NEW_CANDIDATE`.
   This checks/builds the website, builds both wheel/sdist pairs, compares archive
   runtime content to source, checks twine and creates ZIPs plus a hash manifest.
5. Install BOTH wheels in a fresh environment outside this repository and run the
   bundled data example on a prepared macOS host. Retain its proof manifests.
6. Record measured and untested platforms explicitly in the validation report.

Candidate builds never upload packages. Normal future publication requires source
permissions, package ownership and Trusted Publishing to be explicitly resolved in
`ecosystem/publication.json`; the current record keeps the global Trusted Publishing
gate closed because the parser upload channel has not been independently evidenced.
For first-project creation, the manual workflow exposes
explicit `testpypi-bootstrap` and `pypi-bootstrap` modes for one manifest-authorized
package at a time; the PyPI mode still requires an `ecosystem-v` tag and neither mode
bypasses the source gate. Package versions and compatibility.json must be updated
together for a new release; package indexes cannot replace already-published files.

The CI parser matrix covers macOS/Linux/Windows and Python 3.10–3.14. The rac offline
matrix retains macOS/Linux. CI configuration is not evidence those jobs ran locally.
REAPER and third-party plugins are not bundled or installed by ordinary CI.
