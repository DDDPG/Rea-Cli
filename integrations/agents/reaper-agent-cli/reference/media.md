# Audio data and host operations

```python
from rac.media import read_source, render, import_audio
raw = read_source('media.wav', project='session.rpp')
result = render('session.rpp', work_dir='new-render', time_range=(0, 1),
                sample_rate=48000, channels=2, tail_seconds=0, timeout=60)
audio = read_source(result)
assert audio.metadata['level'] == 'rendered'
```

AudioData.samples is float32 `(frames, channels)` and AudioData.sample_rate is an int.
Raw reading never applies FX/fades/playrate; it does not downmix or resample. For relative
files supply project. Foreign paths need explicit path_map; ambiguous mappings are errors.
Selected-track renders include connected send/folder dependencies through master, not
isolated stems. Render settings/time range/tail must be explicit for reproducible checks.
Use a fresh work_dir, preserve originals. MediaError has code and optional manifest_path.

NumPy processing: `processed = audio.samples * 0.5`; use soundfile.write with an
explicit sample rate and subtype. Import the resulting **absolute** audio path with
`import_audio(project, absolute_audio, work_dir='new-import', name='Processed', position=0)`.
The import result.path is a saved **RPP**, not WAV; reparse it and validate media references.
Do not call read_source on an import result as though it were a render result.

Custom JSFX need an additional resource check. `rac.media.render` currently creates a
fresh resource directory and does not copy project-local Effects from the toolkit resource.
For a newly authored JSFX, configure/save the render project with native Lua and run
`rac.runner.platform.build_command(..., '-renderproject', saved_project,
resource=the_same_resource)` through `rac.environment.run_bounded(..., timeout=60)`.
Keep that resource dedicated to the task, verify the effect loaded, and check the actual
DSP response. A missing custom effect must not be accepted as a successful processed render.
