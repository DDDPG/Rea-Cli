<p align="center"><img src="docs/assets/reacli-icon.png" width="160" alt="Rea-Cli icon"></p>
<h1 align="center">Rea-Cli</h1>

<p align="center"><strong>REAPER coding. REAPER executing. REAPER verifying.</strong></p>
<p align="center">RPP as code · Lua/ReaScript · Agent integration · Project/audio verification</p>
<p align="center">
  English · <a href="README.zh-CN.md">简体中文</a> ·
  <a href="docs/README.md">Documentation</a> ·
  <a href="examples/create_project.py">Example</a>
</p>

---

Rea-Cli is a Python library, CLI, and reference environment that can be plugged
into mainstream agentic harnesses for [REAPER](https://www.reaper.fm/). Treat RPP
files as project source: an agent can author or modify them, `rac` can pre-check
and inspect them, and REAPER remains the authoritative parser and execution
environment. The library also supports Lua ReaScript authoring, isolated
execution, and checks of the saved project or rendered audio.

Rea-Cli is not a complete agent harness or a persistent REAPER control server.
Use the Python library for code-driven workflows, the CLI for checks and
isolated execution, and the repository skill to inject Rea-Cli's project-specific
knowledge into an agent.

Rea-Cli drives REAPER's **native ReaScript API only**. It does not require the
**SWS extension**, **ReaPack**, or any other REAPER add-on, and it installs none
of them. Bundled historical references and example projects may mention SWS
actions; those are lookup data, not runtime dependencies.

## Quick start

If you have not installed Rea-Cli yet, choose a path in [Installation](#installation)
below and then run the commands that match your workflow.

### Offline quick start (no REAPER)

Inspect a bundled empty project and query the packaged knowledge indexes:

```bash
reacli doctor --profile offline --json
reacli resources --output ./quickstart
reacli rpp validate ./quickstart/minimal.rpp
reacli knowledge api GetTrack
```

Validation reports `ok: true` and zero tracks. Resource export protects existing
files; use a fresh output directory on reruns. This path needs Python only.

### Build a playable session (requires REAPER)

![From blank to a playable REAPER session, 52 numbered build states](https://res.cloudinary.com/ybukqfxy/image/upload/v1789647834/showcase_compressed.gif)

This walkthrough builds a self-contained, playable REAPER session from a blank
project. After installing from a source checkout and configuring REAPER with the
[environment guide](docs/environment.md), run from the repository root:

```bash
reacli init
reacli doctor --json
python examples/show_session.py ./demo/my-first-session
```

Open **`demo/my-first-session/Show-Session.rpp`** in REAPER and press Play. The
project uses embedded MIDI and REAPER's built-in **ReaSynth**, so it needs no
audio assets or third-party instruments. Use a new output directory on each run.
Add `--render` when you also want a local WAV preview. If ReaSynth discovery
fails, prepare the dedicated VST index as described in the
[environment guide](docs/environment.md#plugin-discovery-and-macos-window-restoration).

`examples/show_session.py` and `examples/create_project.py` export their own
resources into the output directory, so they do not need the `quickstart` export
above. Both need a source checkout, because the examples live in the repository
rather than in the wheel.

For the session layout, effect settings, verification boundaries and the 52
build checkpoints behind the GIF, see the [playable show demo guide](examples/README.md#playable-show-demo).

## Names at a glance

The project uses several names. They map as follows:

| Name | Kind | Where it appears |
|---|---|---|
| `reacli` | PyPI distribution and primary CLI command | `pip install reacli`, `reacli doctor` |
| `rac` | Python import package **and** CLI alias | `import rac`, `rac doctor` |
| `reaper-parser` | PyPI distribution for the standalone parser | `pip install reaper-parser` |
| `reaper_parser` | Python import package of that parser | `from reaper_parser import parse` |
| `reacli[audio]` | Optional extra for WAV checks and rendering | `pip install './packages/reacli[audio]'` |

`reacli` and `rac` are the same command-line program: the distribution registers
both entry points. `reacli` declares `reaper-parser` as a dependency, so
installing the pair in one command keeps their versions aligned.

## Installation

Use **Python 3.10+**. REAPER, Lua and all system libraries are installed
separately; see [prerequisites](#prerequisites).

### Path A — install the released packages

For using the CLI and the Python API without this repository:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install "reacli==0.1.0" "reaper-parser==0.1.0a1"
reacli --version
```

Reacli's WAV and render checks need the optional audio extra:

```bash
python -m pip install "reacli[audio]==0.1.0"
```

See [`reacli` on PyPI](https://pypi.org/project/reacli/0.1.0/) and
[`reaper-parser` on PyPI](https://pypi.org/project/reaper-parser/0.1.0a1/).

### Path B — work from a source checkout

Needed for the runnable examples, the `reference/` handbook, and development:

```bash
git clone https://github.com/DDDPG/Rea-Cli.git
cd Rea-Cli
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install ./packages/reaper-parser ./packages/reacli
reacli --version
```

### Which version should I install?

**Status:** `0.1.0` alpha. The published `reacli==0.1.0` and
`reaper-parser==0.1.0a1` archives are immutable and were uploaded before the
resource, archive, parser and audio safety guards now present in this
repository. Installing from PyPI therefore gives you the earlier runtime;
installing from a current checkout gives you the hardened one. The API may
evolve either way. Path B above installs the newer code. The next upload will use
the next version numbers (see [releasing](docs/releasing.md)); until then the two
paths are not byte-identical, and that is expected rather than a bug.

The distribution and CLI are named `reacli`; Python imports use `rac`.

## Prerequisites

Installing `reacli` does not install REAPER, Lua or system libraries. Choose only
what your workflow needs:

| Requirement | Needed for | Notes |
|---|---|---|
| Python 3.10+ | everything | A system interpreter reporting 3.9 cannot run this package. On macOS check `python3 --version`. |
| REAPER 7.x, official build | execution, rendering, live checks | Not certified to a minimum minor version. Download from [reaper.fm](https://www.reaper.fm/download.php) and install it separately; REAPER is proprietary and supplied under [Cockos's terms](https://www.reaper.fm/purchase.php). |
| A graphical session | execution, rendering | macOS runs on the **logged-in desktop session** — a desktop-less service or CI runner is not supported. Linux needs a reachable `DISPLAY`, or `xvfb-run`, `Xvfb` and `xauth`. |
| macOS: first launch done | execution, rendering | Open REAPER once and pick an output in **Preferences > Audio > Device**. A configured CoreAudio output is required **even for offline rendering**. |
| Linux: GTK3, ALSA, Xvfb, xauth | execution, rendering | See the [Linux commands](docs/environment.md#linux) for Debian/Ubuntu and Fedora package names. |
| Lua 5.3 or 5.4 `luac` | generating Lua from the CLI | Syntax pre-check only — REAPER executes scripts with its embedded Lua. Lua 5.5 is not supported. |
| SWS, ReaPack, MCP server | — | **Not required.** Rea-Cli uses REAPER's native ReaScript API and installs no add-ons. |

**Operating systems:** execution supports macOS and Linux. Windows currently
supports the offline parser and RPP checks but **not** REAPER execution through
`rac`.

On macOS, Homebrew users can install a newer Python and `lua@5.4`:

```bash
brew install python lua@5.4
```

See the [environment guide](docs/environment.md) for platform setup, executable
discovery and troubleshooting.

## A small Python example

This example uses the `quickstart` resources exported in the offline quick start
above. It creates a **Vocal** track at **−6 dB**, saves a copy and checks the
saved state:

```python
from pathlib import Path
from rac.luagen import generate
from rac.rpp import parse
from rac.runner import run
from rac.verify import expect

root = Path("quickstart")
script = generate({"ops": [
    {"op": "track.create", "args": [0, "Vocal"]},
    {"op": "track.set_volume_db", "args": [0, -6.0]},
]}, root / "create.lua")

proof = run(
    root / "minimal.rpp", script,
    save_as=root / "created.rpp",
    run_root=root / "runs",
)
assert proof.ok, proof.to_dict()
expect(parse(root / "created.rpp")).track_count(1).track(0) \
    .name("Vocal").volume(10 ** (-6 / 20))
print(proof.run_dir)
```

`generate(...)` writes `quickstart/create.lua`. The CLI can then run that same
generated script — the file has to exist first, so run the snippet above before
copying this command:

```bash
reacli exec --project ./quickstart/minimal.rpp \
  --script ./quickstart/create.lua --save-as ./quickstart/created.rpp \
  --run-root ./quickstart/runs
```

A complete runnable example that exports its own resources is available in
[examples/create_project.py](examples/create_project.py).

## Harness quick start

Already using **Claude Code, Codex or Qwen Code**? Give your agent this instruction:

> Read https://github.com/DDDPG/Rea-Cli and its `docs/harness/README.md` installation guide. Install the ReaCli CLI toolkit and `reaper-agent-cli` skill for the harness I am using into a new `my-reaper-work` project. Check Python, CLI, Lua and local REAPER availability, and tell me how to start using it.

This installs a project-level **CLI toolkit + skill** using the harness's existing
shell tools. See the [full installation guide](docs/harness/README.md) for each
harness's skill location, prerequisites and candidate-bundle installation.

**Prefer installing it yourself?** From a local checkout's root, run with Python 3.10+:

```sh
python integrations/agents/reaper-agent-cli/scripts/install.py --source . --project ../my-reaper-work --harness all
```

Open Claude Code, Codex or Qwen Code in that directory and ask:
“Use the reaper-agent-cli skill to check my environment, create a new REAPER session,
save it and verify the rendered audio.” The project-local skill uses shell tools and
an isolated Python runtime; it requires no MCP service. REAPER/Lua and harness login
are separate prerequisites. Candidate wheels from a release bundle also work without
a checkout.

See the [three-harness quick start](docs/harness/README.md),
[one-instruction showcase brief](integrations/agents/acceptance/showcase-brief.md),
and [actual acceptance results](docs/harness/acceptance.md).

## Highlights

| Focus | Rea-Cli | Compared with common alternatives |
|---|---|---|
| Turn-based agents | Designed for explicit agent turns: source in, isolated execution, artifacts and verification out | [`reapy`](https://github.com/RomeoDespres/reapy), [`reaper-daemon`](https://github.com/wretcher207/reaper-daemon), OSC and similar projects are better suited to continuous live sessions, which also carry more implicit session state |
| REAPER API access | Keeps native Lua/ReaScript as the escape hatch. Reference material lets an agent author host-native operations without waiting for every API to become a wrapped tool | High-level wrappers and tool catalogs such as [`reaper-cli`](https://github.com/EmNudge/reaper-cli) offer ready-made commands, but their breadth becomes another maintenance surface |
| RPP as code | Treats RPP as project source / a declarative project language. `rac` provides pre-checks, queries and diffs; REAPER is the authoritative parser and executor | RPP libraries such as [`rpp`](https://github.com/Perlence/rpp) focus on parsing and emitting files; live-control tools focus on sending host commands |
| Verification | Connects syntax checks, saved-project assertions, execution proof and rendered-audio checks | In many live-control integrations, command transport and acceptance checks are separate concerns |
| Harness integration | Python library, CLI and repository skill can be added to an existing agent harness; Rea-Cli does not try to replace that harness | MCP servers, daemons and standalone agents usually provide their own control surface and lifecycle |
| Execution model | One-shot isolated runs do not require an always-on bridge for each task, while `Pool` supports independent jobs | Persistent bridges and OSC are preferable when low-latency interactive control is the actual requirement |

In this workflow, large-scale RPP changes are authored by the agent or its
surrounding harness. `rac` is the pre-check and verification layer; it does not
replace REAPER's parser, project semantics or execution environment.

## What you can do

- **Work with RPP source.** Pre-check, inspect and compare tracks, items and markers;
  preserve untouched text and opaque plugin data while the agent authors project changes.
- **Author scripts.** Build standalone Lua from supported operations, including
  track edits, MIDI notes, effects, sends and markers.
- **Run REAPER.** Use isolated resources and concurrent workers, save a project
  copy, and retain input snapshots, logs and execution proofs.
- **Check the result.** Assert project properties and test PCM WAV duration,
  silence, clipping and the dominant frequency of a test tone.
- **Look up APIs and formats.** Query bundled indexes or explore the repository's
  [developer handbook](reference/README.md).

The workflow is simple:

```text
Agent / Python / CLI → RPP or Lua source → rac pre-check → REAPER → saved project / audio → verification
```

## Default startup behavior

Existing `run()` and `Pool.map()` calls need no additional parameters:

- Missing VST scan preferences default to **no startup rescan**. On macOS, missing
  VST indexes are seeded from the local REAPER installation.
- Missing macOS CLAP paths use a directory inside the isolated resource.
- macOS automation disables window restoration to avoid the reopen dialog after
  a forced stop.

Explicit plugin preferences are preserved. New plugins need an intentional scan;
custom CLAP paths can still trigger discovery. These defaults do not prevent
plugins used by a project from loading their own dialogs. See
[plugin setup](docs/environment.md#plugin-discovery-and-macos-window-restoration).

## Behavior and limits

- A completed process does not prove that every requested operation succeeded.
  Inspect `proof.result` and logs, then assert the project or audio you need.
- Scripts run with the current user's permissions. The runner opens the original
  path to preserve relative media references; generated scripts support saving a
  copy. Use copies when experimenting with important projects.
- Execution supports macOS and Linux. Windows execution is not implemented.
  Third-party plugins and different REAPER versions need local verification.
- Audio checks support mono/stereo 16/24-bit PCM WAV. Loudness is approximate;
  project-structure comparison does not prove identical sound.
- Rea-Cli calls REAPER's native ReaScript API. It does not install, load or
  require SWS, ReaPack or any other extension, so scripts that depend on a
  third-party extension are outside the verified scope.

See [validation evidence](docs/validation.md) for tested systems and boundaries.

## Development

```bash
python -m pip install -e ./packages/reaper-parser -e './packages/reacli[audio,dev]'
python -m pytest                         # offline suite; live tests opt out
RAC_TEST_LIVE=1 python -m pytest -m live  # requires the prepared REAPER host
npm ci --prefix apps/reaperdoc
python tools/build_release.py --output dist/new-candidate
python -m twine check dist/new-candidate/reacli/* dist/new-candidate/reaper-parser/*
python scripts/check_dist.py dist/new-candidate/reacli
```

The repository keeps runtime code, examples and research references separate:

```text
packages/reacli/src/rac/     Python library, CLI and bundled runtime resources
packages/reaper-parser/     Host-independent lossless parser
apps/reaperdoc/             Integration copy of independent ReaperDoc
schema/rpp/                Versioned specification, evidence and generated data
tools/                     Cross-component generation and build tools
examples/    Runnable workflows
tests/      Offline tests, opt-in live tests and synthetic fixtures
docs/       Setup, API, validation and release documentation
reference/   Bilingual developer handbook and historical evidence; Git-only
integrations/agents/  Standalone agent bundle source
scripts/     Host bootstrap and distribution checks
.github/     CI, issue templates and manual publishing workflow
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for development conventions.
Virtual environments, REAPER run artifacts and local configuration are ignored by Git.

### Attribution for Git-only reference material

`reference/` and `schema/rpp/evidence/` are excluded from every wheel, sdist,
documentation site and agent bundle. That is a packaging boundary, not a license
boundary: the files are tracked in Git, so cloning this repository clones them
too. They are not covered by the project's MIT license. Each upstream item remains
under its own license and terms; attribution alone does not broaden those rights.
Do not include an item in a public artifact unless its source terms or a separate
redistribution permission allow it. Every retained file keeps its attribution and
source link.

Two conditions travel with that material and are not discharged by attribution:
one source is labelled `cc-by-nc`, so **its noncommercial condition still
applies**, and part of the specification derives from a GPL-3.0 repository. Read
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and the
[source and redistribution audit](docs/ecosystem/source-license-audit.md) before
redistributing this repository or any part of it, especially for commercial use.

## Rea-Cli agent skill

The [agent bundle source](integrations/agents/reaper-agent-cli/SKILL.md) packages a
self-contained skill, concise reference and examples. Candidate releases include
`reaper-agent-cli.zip`; install the matching Python wheels and configure REAPER/Lua
separately. No checkout or persistent MCP server is required by the installed bundle.

## Documentation

- [Setup and prerequisites](docs/environment.md)
- [Python API and CLI behavior](docs/api.md)
- [Validation records](docs/validation.md)
- [Shared parser and media API](docs/ecosystem/api.md)
- [Automation developer handbook](reference/README.md): [Invocation](reference/workflow/README.md) · [RPP](reference/rpp/README.md) · [ReaScript](reference/reascript/README.md) · [Lua](reference/lua/README.md) · [JSFX](reference/jsfx/README.md)
- [REAPER agent skill](integrations/agents/reaper-agent-cli/SKILL.md) · [Repository skill usage](integrations/agents/README.md)
- [Changelog](CHANGELOG.md) · [Release process](docs/releasing.md)

## License

Project-owned code and original documentation are [MIT licensed](LICENSE).
Imported reference data and other upstream materials remain under their own
licenses and terms; the MIT license does not relicense them. See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for provenance and redistribution
conditions. REAPER and third-party plugins are not included and remain subject to
their own licenses. This project is independent of Cockos.
