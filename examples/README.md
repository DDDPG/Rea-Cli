# Examples

Install Rea-Cli from the repository root and complete the
[REAPER environment setup](../docs/environment.md) before running live examples.

## Create and verify a track

```bash
python examples/create_project.py ./demo/first-project
```

The script exports a minimal project, generates Lua, creates a **Vocal** track
at **−6 dB** in REAPER, saves `created.rpp`, and verifies its contents.
Use a new output directory for each run: exported resources are not overwritten.
The result printed to stdout includes the execution status and artifact path.

## Parser and audio roundtrip

```bash
python examples/data_roundtrip.py /absolute/new-directory
```

Requires `reacli[audio]` and a prepared REAPER host. The script synthesizes a
tone, renders, applies a NumPy gain, imports the result, and checks the
roundtrip. Use a new output directory for each run.

## Explore without REAPER

The [README quick start](../README.md#offline-quick-start-no-reaper) shows offline validation and
knowledge lookup. The [API guide](../docs/api.md) covers direct RPP edits,
project assertions, WAV checks, and concurrent workers.

## Compose a custom Lua inspector

The repository-only [Lua examples](../reference/lua/README.md) demonstrate how
to combine the packaged entry template with a custom script body.

## Playable show demo

```bash
python examples/show_session.py ./demo/my-first-session
```

Open **Show-Session.rpp** and press Play. MIDI embedded in the project drives
REAPER's built-in **ReaSynth** live. There are no samples to download, no WAV
source files, no Python audio synthesis and no third-party instruments.
Only the generator's Python/Lua source is stored in this repository.

Requires installed rac, REAPER, a compatible Lua compiler, and ReaSynth in the
resource's VST index. Missing-plugin errors fail the build rather than producing
a silent success. Prepare the dedicated index once if necessary; see
[plugin discovery](../docs/environment.md#plugin-discovery-and-macos-window-restoration).

### Explore the session

The eight bars at 120 BPM follow C–Am–F–G:

- **01 RHYTHM** is a folder containing **02 Pulse** and **03 Ticks**. Pulse is
  split into two MIDI items at 8 seconds. These are synthesized tones, not sampled drums.
- **04 Bass** has a three-point pan envelope moving right, left, then center.
- **05 Chords** has a five-point volume envelope and two MIDI takes. Select the
  item and press `T` to switch between warm triads and a brighter octave.
- **06 Melody** contains 16 editable notes played by ReaSynth.
- **07 Parallel bus** receives a quiet dry send from Chords.
- Three markers, two regions, a time selection, track colors and project notes
  make the session easy to inspect.

### Track and master effects

| Location | Insert | Settings |
| --- | --- | --- |
| Melody, after ReaSynth | ReaEQ | Enabled high-pass at 100 Hz; other bands disabled |
| Chords, after ReaSynth | ReaVerbate | Room size 90, dampening 20, Wet −12 dB, Dry 0 dB |
| Bass, after ReaSynth | ReaComp | Threshold −15 dB; manual makeup +3 dB; auto makeup off |
| Master output | ReaLimit | Threshold −4.5 dB; ceiling −1 dB |

ReaComp's plugin **Wet** output implements manual makeup gain; its host Wet mix
is a separate parameter. Parameter names and displayed values are read from the
actual plugins, so a normalized value is never mistaken for dB. ReaVerbate is
algorithmic: no impulse-response file is required. The parallel bus remains a
quiet send from Chords; the limiter processes the complete mix on Master.

### API boundaries

Registered rac operations create tracks, MIDI items/notes, synth FX, sends,
volume automation, markers and regions. `rac.rpp` adds the initial marker offline.
Custom Lua executed through rac handles folder depth, a second MIDI take, pan
envelope points, send level, EQ band controls, plugin-specific parameter units,
Master FX, view/render settings and detailed readback. These
are extension examples, not new high-level Python methods. Volume points use
`env.set_points_db`; pan values use their own domain. The native FX controls
follow the [REAPER ReaScript API](https://www.reaper.fm/sdk/reascript/reascripthelp.html#TrackFX_SetEQParam).

The builder checks operation errors, saves and reparses the RPP, then reopens it
in REAPER. It verifies track/folder/item/take structure, MIDI, envelopes, sends,
markers, all five ReaSynth instances, the four effect inserts and their saved parameter values,
and absence of external media sources.
The `.rpp` can be moved by itself; the destination REAPER must include ReaSynth.
The render destination is local to the original build folder; change it after moving.

### Optional audio preview

```bash
python examples/show_session.py ./demo/session-with-preview --render
```

This explicitly renders a 24-second local WAV (16 seconds of music plus 8 seconds
for the reverb tail) and checks duration, non-silence and clipping.
Preview audio, generated RPPs, resource indexes and execution logs stay under
Git-ignored `demo/`. The default command produces no WAV files.

### Numbered build states

```bash
python examples/show_session.py ./demo/walkthrough --steps
```

This writes **52 independent RPP files** under `steps/`, from `000-blank.rpp` to
`051-finished-session.rpp`. They are real saved build states, not reverse edits
of the finished session. Screenshot capture and GIF assembly stay under
Git-ignored `demo/`; the root README links a hosted copy of the animation.

## Development contracts / 开发规范

See the [English handbook](../reference/README.md) or [中文规范](../reference/README.zh-CN.md) for RPP, ReaScript, Lua, FX and verification boundaries. The [repository skill](../integrations/agents/reaper-agent-cli/SKILL.md) applies the same contracts to new tasks.
