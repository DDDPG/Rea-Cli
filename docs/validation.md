# Validation

Validation uses synthetic projects and audio. Live checks run on explicitly
prepared REAPER installations with dedicated resources; they do not use personal
projects. CI and local live results are recorded separately.

## Current macOS startup validation (2026-09-09)

macOS 26.6.1 / Apple Silicon / REAPER 7.48 / Python 3.12.10 / Lua 5.4.7:
`RAC_TEST_LIVE=1 python -m pytest -q` passed all 167 tests (162 offline,
5 live) in 22.36 seconds. One Python `audioop` deprecation warning remained.
The live suite includes rendering, parallel isolated resources, Unicode paths,
relative media, ReaEQ, MIDI, colors, sends, and restart after SIGKILL.

Before the startup changes, the original four live tests took 208.03 seconds:
one passed and three timed out. Plugin scanning and a Cocoa reopen dialog were
observed. With VST indexes seeded and startup scanning disabled, those four
tests passed in 12.61 seconds. A separate forced-stop/restart probe completed
the subsequent Lua edit and save in 1.01 seconds. These are local observations,
not a guarantee for other machines or plugin sets. Linux execution was not
retested on this machine.

## Earlier validation baseline
On 2026-09-09, the complete suite passed **164 tests without failures or skips**
in each environment. This includes 160 offline cases and four live checks:

- macOS 15.5 / Apple Silicon / REAPER **7.62/macOS-arm64** / Python **3.14.6**:
  editable installation, **44.46 seconds**.
- The same macOS host / Python **3.10.20**: wheel installation, isolated Python
  launched outside the checkout, **42.36 seconds**.
- Linux x86_64 / REAPER **7.77/linux-x86_64** / Python **3.13.11**:
  independent installation, **18.89 seconds**.

macOS used Lua 5.4.9; Linux used Lua 5.4.4. The original macOS Lua 5.5 remained
installed separately. The 43 runtime files installed on Linux matched the tested
source snapshot and the delivery checkout. Tests did not modify the source tree.

Both archives passed `twine check` and the content verifier. New archive
regressions cover excluded references, missing/stale runtime files, metadata
mismatches, unsafe paths and links. Worker regressions cover overlapping and
missing seed paths before a rebuild can remove existing resources.

The English and Chinese README examples were checked for consistency. Their
offline steps and Lua generation passed, and the documented REAPER execution
saved the expected Vocal track at −6 dB. Public documentation links, workflow
YAML and shell-script syntax were also checked locally. These are local results,
not claims of a GitHub-hosted workflow run.

Machine-readable environment results are in [validation.json](validation.json).

## What the live checks verify

[Execution tests](../tests/test_live.py) verify:

- Generated Lua executes, writes a valid proof, saves a separate project, and
  produces the expected parsed project structure.
- REAPER renders a one-second 440 Hz WAV. The checker verifies duration,
  non-silence, clipping and dominant frequency.
- Concurrent workers return distinct actual `GetResourcePath()` values and
  independently verified output projects, even with a global resource override.
- Unicode and space-containing paths work for projects, scripts and resources.
  Relative project media resolves to the expected one-second source.
- Stock ReaEQ loads; MIDI notes, routing, markers and native RGB colors match
  the values read back from REAPER.

The [dual-path test](../tests/test_verify.py) compares equivalent Lua and direct
RPP edits for track levels, names and markers. All four live tests carry the
`live` marker and require `RAC_TEST_LIVE=1`.

The repository's Lua inspector example was also built, syntax-checked and run
against a synthetic project. It returned REAPER version, OS, resource path and
track information. Checksums of 2,390 files in the native macOS REAPER resource
tree were unchanged after the checks, with no additions or removals.

## Platform findings

macOS 7.62 prints valid official help but exits with status 1. Doctor accepts
that combination only when the usage header and required CLI capabilities are
present. Other failed or incomplete help output remains an error.

A fresh macOS INI containing only `audiocfgopen=0` did not start reliably.
Selective copying of initialized CoreAudio options into dedicated resources
resolved startup. No user startup scripts, plugin directories or unrelated
preferences are copied by this automatic initialization.

The default macOS pool shares an installed executable and starts separate
`-newinst` processes with distinct resource paths. This passed concurrent checks.
Copied and re-signed bundles timed out in the same validation; the explicit
legacy `copy_app=True` mode is not covered by the successful result.

MIDI edits can mark a project dirty. After a verified save-copy, REAPER can wait
at a save confirmation; the runner then closes its process group after the
configured grace period and reports `teardown_killed=true`. This occurred on
both platforms in the MIDI test. `proof.ok` alone does not assert a natural
process exit or the intended musical result.

## Reproduce the checks

Install the development dependencies and prepare REAPER as described in
[CONTRIBUTING.md](../CONTRIBUTING.md) and the [environment guide](environment.md).

```bash
python -m pytest -m "not live"
RAC_TEST_LIVE=1 python -m pytest -m live
reacli doctor --render --work-dir ./smoke-artifacts --json
python -m build
python -m twine check dist/*
python scripts/check_dist.py dist
```

`RAC_REAPER_BIN` can select an installation outside the normal discovery paths.
The archive verifier checks both wheel and sdist against the current runtime
source, including platform INIs, Lua templates, knowledge indexes and notices.
It rejects `reference/`, local environments, cached files, links, unsafe archive
paths and stale package contents. The repository-only collection has separate
source hashes and validation limits in [reference/SOURCES.md](../reference/SOURCES.md).

## Limits

These checks do not certify other REAPER versions, Intel Mac hardware, every
third-party AU/VST plugin, MP3 output, macOS without a graphical login, or the
musical quality of a render. No GitHub-hosted workflow execution is implied by
local passing tests. The CI matrix tests offline behavior; live REAPER checks
require a prepared host. Imported-data rights are tracked separately in
[THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).
