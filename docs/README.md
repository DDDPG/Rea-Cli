# Documentation

Start with the [English README](../README.md) or [中文 README](../README.zh-CN.md)
for installation and a working example.

- [Environment setup](environment.md): Python, Lua, REAPER, Linux displays,
  macOS CoreAudio, resource initialization and troubleshooting.
- [API and behavior](api.md): Python modules, CLI output and exit codes, proofs,
  retries, media paths, concurrency and execution limits.
- [Validation](validation.md): the tested platform combinations and what the
  tests establish.
- [Contributing](../CONTRIBUTING.md): development setup, tests and review expectations.
- [Release process](releasing.md): local artifacts, package checks and GitHub publishing setup.
- [Security policy](../SECURITY.md): execution trust boundaries and vulnerability reporting.
- [Third-party notices](../THIRD_PARTY_NOTICES.md): imported data and attribution.

## Repository knowledge

The [reference collection](../reference/README.md) expands the runtime indexes
with RPP notes, ReaScript pitfalls, historical action data, JSFX material and Lua
composition examples. It is available in the Git checkout, not in wheel or sdist.
Historical notes carry their own version and evidence limits; current setup and
API documentation take precedence for supported usage.

[`source-baseline.json`](source-baseline.json) preserves hashes of the original
project-relative files used to extract the library. It is a provenance snapshot,
not a checksum list for the current release. Supplemental sources and subsequent
edits are recorded separately in the reference collection's manifest.
