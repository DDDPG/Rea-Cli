# ReaCli in Claude Code, Codex and Qwen Code

[中文](README.zh-CN.md) · [Shared APIs](../ecosystem/api.md)

This is a CLI toolkit: the harness writes code, invokes local shell commands, and
checks REAPER outputs. There is no MCP server, daemon or new model account.

## One-command project installation

Prerequisites: Python 3.10+ with venv/pip and an already installed/authenticated harness.
Host work also needs local REAPER 7.x and Lua 5.3/5.4; macOS needs a logged-in desktop
and configured CoreAudio device. Linux host setup is in the [environment guide](../environment.md).
Windows currently supports the offline parser, not REAPER execution through rac.

Install from a local checkout of the repository:

```sh
# Point --source at your checkout. No GitHub request is made for the source.
REACLI_SOURCE=/absolute/path/to/Rea-Cli
python "$REACLI_SOURCE/integrations/agents/reaper-agent-cli/scripts/install.py" \
  --source "$REACLI_SOURCE" --project ./my-reaper-work --harness all
```

This creates a project-local venv, installs BOTH packages plus audio dependencies, checks the
CLI, and installs the shared skill in the three project discovery locations. It does
not edit global harness permissions, login or MCP configuration. Choose one harness
with `--harness claude`, `--harness codex` or `--harness qwen` instead of `all`.
Python dependencies may be downloaded. The installed runtime uses package copies,
not editable links to the checkout.

Alternative inputs (mutually exclusive):

```sh
# After extracting a candidate's reaper-agent-cli.zip:
python reaper-agent-cli/scripts/install.py --wheels /absolute/candidate \
  --project ./my-reaper-work --harness all

# Advanced: explicitly bind an existing environment instead of making a new venv.
python reaper-agent-cli/scripts/install.py --runtime-python /absolute/venv/bin/python \
  --project ./another-workspace --harness codex
```

`--wheels` requires exactly one wheel for each package in the candidate tree. This
path does not require source or sibling checkouts. `--runtime-python` validates rac,
parser and audio imports. Existing toolkit/skill destinations are never overwritten;
use a fresh directory for upgrades. Preserve generated projects before manually removing
an old installation. Do not move an installed venv; reinstall after relocating a workspace.

The report is `.reacli-toolkit/installation.json`; missing harness executables are
reported separately from successful package installation. It does not prove model
login, REAPER startup or audio output. On failure, inspect `.reacli-toolkit/install.log`
and `FAILED`. Personal paths in installation reports are local diagnostics.

## Start your harness and give it one instruction

```sh
cd my-reaper-work
claude   # or: codex / qwen
```

| Harness | Installed project skill | Explicit instruction |
| --- | --- | --- |
| Claude Code | `.claude/skills/reaper-agent-cli` | `/reaper-agent-cli Check my environment, create a new eight-bar MIDI session in REAPER, save a copy and verify its rendered audio.` |
| Codex | `.agents/skills/reaper-agent-cli` | `$reaper-agent-cli Check my environment, create a new eight-bar MIDI session in REAPER, save a copy and verify its rendered audio.` |
| Qwen Code | `.qwen/skills/reaper-agent-cli` | `Use the reaper-agent-cli skill to check my environment, create a new eight-bar MIDI session in REAPER, save a copy and verify its rendered audio.` |

The harness uses its existing shell/file tools and approval policy. Allow the requested
local host execution for your task. A container or restrictive sandbox cannot necessarily
start your desktop REAPER; grant appropriate local execution in the harness. The installer
does not automatically disable sandboxes or approvals. Skill folders are guidance, not
an OS sandbox. The host opens isolated REAPER instances and saved copies, not an attached
live editing session.

For headless runs use `claude -p 'Use the reaper-agent-cli skill to …'`,
`codex exec 'Use the reaper-agent-cli skill to …'`, or
`qwen 'Use the reaper-agent-cli skill to …'`. Authenticate first and configure the
specific tool permissions required by that run; an unattended run cannot answer an
interactive permission prompt. Avoid relying on interactive slash-command expansion in
headless mode; naming the skill works across all three.

## What the toolkit provides

Use the `scripts/toolkit.py` within the chosen installed skill, with Python 3.10+:

```sh
python .agents/skills/reaper-agent-cli/scripts/toolkit.py doctor --profile offline --json
python .agents/skills/reaper-agent-cli/scripts/toolkit.py doctor --profile full --json
python .agents/skills/reaper-agent-cli/scripts/toolkit.py rac init
python .agents/skills/reaper-agent-cli/scripts/toolkit.py templates ./new-starters
python .agents/skills/reaper-agent-cli/scripts/toolkit.py compose authored.body.lua authored.lua
python .agents/skills/reaper-agent-cli/scripts/toolkit.py python authored.py
```

Replace `.agents` with `.claude` or `.qwen` as appropriate. The helper binds the runtime
through `runtime.json`, so conflicting system Python/CLI installations do not take over.
It selects project-local REAPER resources unless RAC_REAPER_RESOURCE was explicitly set.
`doctor` is read-only; `init` is explicit and initializes those dedicated resources.

- CLI: RPP validation/query/diff, API lookup, resource export, execution/proof and audio checks.
- Python: shared parser views/patch, Lua generation, run/Pool, assertions, NumPy read/render/import.
- Native code: a syntax-checked Lua body composer, read-only inspector starter, JSFX gain starter,
  and guidance for MIDI, FX parameter units, envelopes and DSP acceptance.
- Evidence: separate structure, host readback and audio checks, with hashes/manifests and failure logs.

JSFX is EEL2 and requires host/audio validation; passing Lua syntax checks does not validate it.
The bundle does not include the showcase solution.

## Reproduce the showcase from requirements

Copy the [requirements-only brief](../../integrations/agents/acceptance/showcase-brief.md)
into the new workspace as `requirements.md`. Give any harness this single instruction:

> Use the reaper-agent-cli skill to independently implement requirements.md in this workspace, operate local REAPER through the installed CLI toolkit, and deliver the saved session, real audio preview and verified readback evidence.

The brief describes the README arrangement and effect targets, not implementation code.
Agents must author their own music/scripts; no `show_session.py`, existing `.rpp`, or
another harness's answer is supplied. Note choices may differ; this is functional
reproduction, not bit-identical music or the 52-frame GIF capture pipeline.
Installing the CLI is not an end-to-end host pass.

## Adapter references

Discovery locations and invocation were checked against the installed CLI help and
[Claude skills](https://code.claude.com/docs/en/skills),
[Codex skills](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills),
and [Qwen skills](https://qwenlm.github.io/qwen-code-docs/en/users/features/skills/).
Local CLI presence alone is not a live-test pass. See [validation](../validation.md)
for host-check coverage.
