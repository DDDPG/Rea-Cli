# reaper-parser

Standalone, dependency-free REAPER RPP documents with lossless emission and Python views.

Install the published parser from PyPI:

```sh
python -m pip install "reaper-parser==0.1.0a1"
```

The release is independent from the `reacli` execution layer; install
`reacli==0.1.0` separately when REAPER execution and audio helpers are needed.

```python
from reaper_parser import parse
project = parse("session.rpp")
for track in project.project.tracks:
    print(track.name, track.volume)
project.save("copy.rpp")  # refuses overwrite by default
```

`fields()` exposes original values and field-level evidence status. Unknown semantics remain raw.
The raw tree is not an rppxml object. REAPER is required only by the separate reacli execution layer.

## Source development

From the monorepo root: `python -m pip install -e ./packages/reaper-parser`, then
install pytest and run `python -m pytest tests/conformance -q`.
See the [API and field contracts](https://github.com/DDDPG/Rea-Cli/blob/main/docs/ecosystem/api.md)
([中文](https://github.com/DDDPG/Rea-Cli/blob/main/docs/ecosystem/api.zh-CN.md)) and [contributor guide](https://github.com/DDDPG/Rea-Cli/blob/main/CONTRIBUTING.md)
in a complete checkout. These relative links target repository browsing; the
standalone source archive does not include the monorepo documentation.

`doc.tracks()` returns raw elements; `doc.project.tracks` returns shared views.
Use `raw()` to distinguish missing fields from convenience-property fallbacks.
`fields()` indexes are 1-based, `set_raw()` indexes are 0-based, and `set_field()`
requires a verified write contract. Host audio interpretation belongs to `rac.media`.
A source checkout may be newer than the last PyPI upload.

## License

Project-owned parser code and original documentation are [MIT licensed](../../LICENSE).
Bundled reference descriptions retain their own source terms and attribution. See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for provenance and redistribution
information.
