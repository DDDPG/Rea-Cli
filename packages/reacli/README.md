# ReaCli

REAPER execution, RPP inspection and verification, built on reaper-parser.

Install the released pair from PyPI:

```sh
python -m pip install "reacli==0.1.0" "reaper-parser==0.1.0a1"
```

Optional audio interfaces:
`python -m pip install "reacli[audio]==0.1.0"`.

For source development, install `./packages/reaper-parser` and
`./packages/reacli` from the monorepo root instead of mixing a checkout with
an already-published package. The reviewed checkout may contain post-upload
hardening that is not part of the immutable `0.1.0` artifact.

`rac` and `reacli` remain equivalent CLI commands; Python imports use `rac`.
Run `rac doctor --profile offline --json` without REAPER, or configure a REAPER host for execution.
See https://github.com/DDDPG/Rea-Cli for the ecosystem guide and source.

Bundled reference data retains its source terms and attribution; see the package notices.
