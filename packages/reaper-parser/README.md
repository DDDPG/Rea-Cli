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
Bundled reference descriptions retain their source terms; see THIRD_PARTY_NOTICES.md.


## Source development

From the monorepo root: `python -m pip install -e ./packages/reaper-parser`, then
install pytest and run `python -m pytest tests/conformance -q`.
See the [API and field contracts](../../docs/ecosystem/api.md)
([中文](../../docs/ecosystem/api.zh-CN.md)) and [contributor guide](../../CONTRIBUTING.md)
in a complete checkout. These relative links target repository browsing; the
standalone source archive does not include the monorepo documentation.

`doc.tracks()` returns raw elements; `doc.project.tracks` returns shared views.
Use `raw()` to distinguish missing fields from convenience-property fallbacks.
`fields()` indexes are 1-based, `set_raw()` indexes are 0-based, and `set_field()`
requires a verified write contract. Host audio interpretation belongs to `rac.media`.
The reviewed checkout may contain post-upload parser hardening that is not part of
the immutable `0.1.0a1` artifact.
