# Documentation

Start with the [English README](../README.md) or [中文 README](../README.zh-CN.md)
for installation and a working example. Both open with a name table, because the
project uses two distributions with distinct import names (`reacli` / `rac`,
`reaper-parser` / `reaper_parser`).

- [Environment setup](environment.md): Python, Lua, REAPER, Linux displays,
  macOS CoreAudio, resource initialization and troubleshooting.
- [API and behavior](api.md): Python modules, CLI output and exit codes, proofs,
  retries, media paths, concurrency and execution limits.
- [Validation](validation.md): what the tests cover and the known limits.
- [Contributing](../CONTRIBUTING.md): development setup, tests and review expectations.
- [Release process](releasing.md): local artifacts, package checks and GitHub publishing.
- [Security policy](../SECURITY.md): execution trust boundaries and vulnerability reporting.
- [Third-party notices](../THIRD_PARTY_NOTICES.md): imported data and attribution.
- [Landing page](index.html): static GitHub Pages `/docs` prototype; see [its notes](site.md).

- [Harness installation and one-instruction workflows](harness/README.md) ([中文](harness/README.zh-CN.md)).

## Ecosystem components

- [Shared parser and media API](ecosystem/api.md) ([中文](ecosystem/api.zh-CN.md)): document views, field status, raw audio, rendering and import.
- [Ecosystem installation and demonstration](ecosystem/README.md).
- [ReaperDoc independent maintenance](ecosystem/reaperdoc-maintenance.md).

## Repository knowledge

The [developer handbook](../reference/README.md) ([中文](../reference/README.zh-CN.md)) defines invocation, RPP, ReaScript, Lua and JSFX development contracts. Each topic has paired English and Chinese guides, with a separate [historical evidence catalog](../reference/knowledge/README.md). Use it to select an implementation path, check units and object identity, and verify results beyond a successful process exit.

The repository [REAPER agent skill](../integrations/agents/reaper-agent-cli/SKILL.md) uses these contracts and the installed rac package. See [skill usage](../integrations/agents/README.md). Both directories are Git-only deliverables, excluded from wheel and sdist. Current setup/API docs take precedence over historical observations.

The [RPP specification source](../schema/rpp/README.md) documents `schema/rpp/spec.json`,
its generated consumers and the regeneration gate.

[`source-baseline.json`](source-baseline.json) preserves hashes of the original
project-relative files used to extract the library. It is a provenance snapshot,
not a checksum list for the current release.
