# Harness acceptance record

Tested on 2026-09-17, macOS arm64, REAPER 7.48, ReaCli 0.1.0,
reaper-parser 0.1.0a1, toolkit bundle 0.2.0a1.
[Machine-readable results](acceptance.json) retain requirements and artifact hashes.

Each attempt received a fresh project workspace, the installed toolkit, and the
[requirements-only brief](../../integrations/agents/acceptance/showcase-brief.md).
The initial instruction was:

> Use the reaper-agent-cli skill to independently implement requirements.md in this workspace, operate local REAPER through the installed CLI toolkit, and deliver the saved session, real audio preview and verified readback evidence.

No existing showcase implementation, RPP, rendered audio or another harness's output
was supplied. Reviewed command traces contained no reads of the repository showcase
sources. This is a reviewed trace boundary, not an OS-enforced filesystem sandbox.
Agents could inspect generic installed runtime APIs and templates, probe REAPER and
repair their own scripts within the same task. No MCP tools were enabled for these runs.

| Harness | CLI | Observed outcome |
| --- | --- | --- |
| Codex | 0.153.4 | Finished; independent saved-host and audio checks passed |
| Qwen Code | 0.23.0 | Project/audio passed independent checks; all 155 self-checks passed; 15-minute limit reached before final reply |
| Claude Code | 2.1.236 | After backend repair, 42 self-checks and independent host/audio checks passed |

For this explicitly authorized local evaluation, Codex ran with `--ignore-user-config`,
`--ephemeral` and `--sandbox danger-full-access`; Claude used a strict empty MCP config
and allowed only Bash/Read/Write/Edit/Glob/Grep/Skill; Qwen exposed file tools, skill
activation and shell execution. These are evaluation process options, not installer
settings or a recommendation to grant unrestricted access to arbitrary projects.
Codex and Qwen had a 15-minute attempt budget. Claude was extended to 30 minutes
within the same session, without another task instruction. Qwen used
`deepseek-v4.1-flash-expires-on-0910[1m]`; Claude's retry uses the user's
`deepseek-flash` configuration. Codex used its harness default model, whose identifier
was not reported in the captured event stream.

Each final project passed all 32 independent checks. The independent reviewer reopens the delivered RPP in a fresh isolated REAPER process;
it does not repair the output. Checks cover seven named tracks/folder structure,
five ReaSynth instruments, split Pulse items, MIDI notes, both C–Am–F–G chord takes,
16 melody notes, envelopes, a quiet parallel send, effect settings including the
100 Hz high-pass, markers/regions, project notes, and no external media dependency.
Audio is read separately: stereo, 48 kHz, 1,152,000 frames (24 seconds), finite,
non-silent and unclipped. These checks do not score musical aesthetics or require
bit-identical notes/audio to the original showcase.

| Output | Peak | RMS |
| --- | ---: | ---: |
| Codex | 0.890350 | 0.305535 |
| Qwen Code | 0.890350 | 0.276117 |
| Claude Code | 0.594727 | 0.145819 |

The reusable independent checker is
[verify.py](../../integrations/agents/acceptance/verify.py), with its
[read-only Lua inspector](../../integrations/agents/acceptance/inspect.body.lua).
Run with an installed ReaCli/audio Python, supplying the attempt workspace and a new
review output directory. Inputs must be `output/Show-Session.rpp` and `output/preview.wav`.

Local generated RPP/audio/source and review reports are retained under
`demo/harness-showcase-20260917/` (ignored). Raw harness traces, installation paths and
resource directories remain local; they are not bundled or published.

Installation checks separately passed all three project discovery layouts, CLI doctor,
existing-runtime binding, source installation, and a standalone extracted bundle plus
wheels from outside the repository. The bundle excludes local runtime bindings/caches
and contains no showcase solution. The offline suite passed 207 tests, with one optional
oracle skip and five live tests deselected; the host checks above ran explicitly.
Linux/Windows harness execution was not tested in this run. These results therefore
cover macOS arm64 only.

The JSFX gain starter also passed a separate real-host DSP check using
[verify_jsfx.py](../../integrations/agents/acceptance/verify_jsfx.py): a 440 Hz stereo
tone rendered at 0 dB and −6 dB produced RMS ratio 0.501178 (expected 0.501187).
This is a toolkit validation, not another harness-composition attempt. Both renders
use the same dedicated Effects resource; the high-level media renderer currently does
not copy newly authored project-local JSFX into its fresh resource directory.
