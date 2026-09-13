# reaper-parser

Standalone, dependency-free REAPER RPP documents with lossless emission and Python views.

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
