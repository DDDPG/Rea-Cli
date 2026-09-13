# Ecosystem release candidates

The monorepo builds independent `reaper-parser` and `reacli` distributions.
Follow [the ecosystem guide](ecosystem/README.md) for installation and validation.

1. Install both packages and their development/audio extras; run the offline suite.
2. Run `python tools/generate_schema.py --check`.
3. Install website dependencies with `npm ci --prefix apps/reaperdoc`.
4. Run `python tools/build_release.py --output dist/NEW_CANDIDATE`.
   This checks/builds the website, builds both wheel/sdist pairs, compares archive
   runtime content to source, checks twine and creates ZIPs plus a hash manifest.
5. Install BOTH wheels in a fresh environment outside this repository and run the
   bundled data example on a prepared macOS host. Retain its proof manifests.
6. Record measured and untested platforms explicitly in the validation report.

Candidate builds never upload packages. Source permissions, package ownership and
Trusted Publishing must be explicitly resolved in `ecosystem/publication.json` before
manual publication. Public TestPyPI also requires these prerequisites. Production
requires an `ecosystem-v` tag. Package versions and compatibility.json must be updated
together for a new release; package indexes cannot replace already-published files.

The CI parser matrix covers macOS/Linux/Windows and Python 3.10–3.14. The rac offline
matrix retains macOS/Linux. CI configuration is not evidence those jobs ran locally.
REAPER and third-party plugins are not bundled or installed by ordinary CI.
