# Release process

The monorepo builds independent `reaper-parser` and `reacli` distributions.
Follow [the ecosystem guide](ecosystem/README.md) for installation and validation.

## Published versions

PyPI currently serves `reacli==0.1.0` and `reaper-parser==0.1.0a1`. Those
archives are immutable. A source checkout may contain later fixes; do not
re-upload the same version numbers.

## Version bump checklist

Update every version reference in the same change:

- `packages/reacli/src/rac/__init__.py` (`__version__`, the source for `reacli`)
- `packages/reaper-parser/pyproject.toml` (`[project] version`)
- `packages/reacli/pyproject.toml` (the `reaper-parser` dependency pin)
- `integrations/agents/reaper-agent-cli/compatibility.json`
- `CHANGELOG.md` and both package READMEs
- `docs/ecosystem/publication.json` (gate flags and published version numbers)

`reacli` pins `reaper-parser>=0.1.0a1,<0.2`. Bump both packages together so the
pair stays aligned. `tests/test_distribution.py` and `scripts/check_dist.py`
verify that package metadata stays tied to `rac.__version__`.

## Build a candidate

1. Install both packages and their development/audio extras; run the offline suite.
2. Run `python tools/generate_schema.py --check`.
3. Install website dependencies with `npm ci --prefix apps/reaperdoc`.
4. Run `python tools/build_release.py --output dist/NEW_CANDIDATE`.
5. Install both wheels in a fresh environment outside this repository and run a
   live smoke check on a prepared host.

```bash
python tools/build_release.py --output dist/new-candidate
python -m twine check dist/new-candidate/reacli/* dist/new-candidate/reaper-parser/*
python scripts/check_dist.py dist/new-candidate/reacli
```

Candidate builds never upload packages. Production publication requires an
`ecosystem-v*` tag and the gates in `docs/ecosystem/publication.json`.
Run `python tools/check_publish.py` before using `.github/workflows/publish.yml`.
