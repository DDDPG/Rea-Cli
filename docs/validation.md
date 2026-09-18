# Validation

Validation uses synthetic projects and audio. Live checks run on prepared REAPER
installations with dedicated resources; they do not use personal projects.

## Coverage

The default suite is offline and does not launch REAPER. Live checks require
`RAC_TEST_LIVE=1` and an official REAPER 7.x host.

Live tests in this repository verify that:

- Generated Lua executes, writes a proof, saves a separate project, and produces
  the expected parsed project structure.
- REAPER can render a one-second 440 Hz WAV that passes duration, non-silence,
  clipping and dominant-frequency checks.
- Concurrent workers use distinct resource paths and independently verified outputs.
- Unicode and space-containing paths work for projects, scripts and resources.
- Stock ReaEQ, MIDI notes, routing, markers and native RGB colors match values
  read back from REAPER.

See [tests/test_live.py](../tests/test_live.py) and the live cases in
[tests/test_verify.py](../tests/test_verify.py).

CI runs the offline matrix (parser on macOS/Linux/Windows, rac offline on
macOS/Linux). It does not install REAPER or run live host checks.

## Reproduce the checks

Install the development dependencies and prepare REAPER as described in
[CONTRIBUTING.md](../CONTRIBUTING.md) and the [environment guide](environment.md).

```bash
python -m pytest -m "not live"
RAC_TEST_LIVE=1 python -m pytest -m live
reacli doctor --render --work-dir ./smoke-artifacts --json
```

`RAC_REAPER_BIN` can select an installation outside the normal discovery paths.

## Limits

These checks do not certify other REAPER versions, Intel Mac hardware, every
third-party plugin, MP3 output, macOS without a graphical login, or the musical
quality of a render. Windows currently supports the offline parser, not REAPER
execution through `rac`. A successful process exit does not prove the intended
edit; inspect the saved project or audio.
