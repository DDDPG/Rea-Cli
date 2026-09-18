# Contributing to reacli

Development and tests are maintained at the monorepo root. Follow the
[shared contributor guide](../../CONTRIBUTING.md) from a complete checkout.
The source distribution alone does not contain the full contributor workspace.

From the repository root:

```sh
python -m pip install -e ./packages/reaper-parser -e './packages/reacli[audio,dev]'
python -m pytest -m 'not live'
```

For an extracted package archive, use the repository URL recorded in package metadata
to obtain the full checkout; the relative guide link above is for repository browsing.
