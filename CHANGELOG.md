# Changelog

## 0.1.0 — 2026-09-17

### Distribution

- Published `reacli==0.1.0` and `reaper-parser==0.1.0a1` to PyPI as both wheel
  and source distribution. The live artifact names, upload timestamps and
  SHA-256 values are indexed in [the publication audit](docs/ecosystem/publication-audit.md)
  and `docs/ecosystem/publication.json`.

### Post-publication maintenance

- The reviewed main candidate adds resource, archive, parser and audio safety guards and
  removes a local media path from generated public data. These changes are not part of the
  immutable `0.1.0`/`0.1.0a1` archives; bump versions before the next upload.

### Public-readiness cleanup (unreleased, no version bump)

Documentation and packaging-metadata pass toward a public repository state.
Runtime behavior is unchanged and `0.1.0`/`0.1.0a1` remain the published versions.

- Rewrite both READMEs: a name table for the two distributions and their import
  names, installation split into PyPI and source-checkout paths, a prerequisites
  table, and an explicit statement that SWS, ReaPack and MCP are not required.
- Remove the tracked binary images (~10.6 MB) and link the showcase animation
  instead; regenerate such assets under the Git-ignored `demo/` tree.
- Record the maintainer's 2026-09-17 decision that the Git-only `reference/` and
  `schema/rpp/evidence/` corpus may be published with its sources attributed,
  clearing it as a public-release blocker. Those files are unchanged and still
  tracked in Git, so a clone still distributes them; the `cc-by-nc` entry keeps
  its noncommercial condition, which attribution does not discharge.
- Add the PEP 561 `py.typed` marker to the `rac` package with its `package-data`
  and `MANIFEST.in` entries.
- Add `schema/rpp/README.md`, which explains that `sourceFile` is relative to the
  `reaper_agent_cli` source workspace while `source_commit`/`source_files` are
  ReaperDoc provenance. The generated consumers now carry `source_file_base` and
  `source_file_note`, so the shipped `rpp_schema.json` is self-describing.
- Mark `.state/` evidence paths as local-only, and separate the current 167-test
  macOS run from the dated 164-test release baseline in `docs/validation.md`.
- Record the next version pair (`reacli==0.1.1`, `reaper-parser==0.1.0a2`) and the
  files that must move together in `docs/releasing.md`.

### Repository maintenance

- Repair monorepo handbook paths and installation commands; share the contributor guide.
- Document shared parser/media APIs in English and Chinese, including indexing,
  fallback values, write verification and source/rendered lineage boundaries.
- Record independent ReaperDoc maintenance and deferred public entry points.
- Cover component dependencies and repository documentation/provenance checks.

### Added

- Standalone `reacli` distribution, `rac` Python namespace, and both command-line
  entry points.
- RPP parsing, patching and semantic comparisons; Lua generation and syntax
  checks; structured execution proofs and PCM WAV assertions.
- Bundled Lua templates, RPP/API indexes, semantic defaults and platform INIs.
- Environment diagnostics, resource initialization, and opt-in Lua/save/render
  integration checks.
- Concurrent workers with independent resource directories and output guards.
- Repository-only RPP, ReaScript and JSFX reference material, provenance records
  and a composed Lua inspector example.
- English and Chinese quick starts, API/setup guides, contribution and security
  guidance, and GitHub issue/pull-request templates.
- Offline Linux/macOS CI matrix, distribution-content checks, dependency update
  configuration and manual Trusted Publishing workflow with production tag checks.

### Platform support

- Linux dummy-audio configuration and Xvfb routing, with a standalone bootstrap
  script and fallback display wrapper.
- macOS resource isolation, selective CoreAudio initialization, official help
  exit-code handling and Homebrew Lua 5.4 discovery.
- Default macOS workers share the installed application across independent
  processes. The copied-bundle implementation remains an explicit legacy option.
- Python 3.13+ compatibility through `audioop-lts`; optional RPP oracle dependency.

### Reliability

- Dedicated resources default to cached VST discovery; macOS seeds missing VST
  indexes from the native resource and defaults missing CLAP paths to a local
  directory. Explicit plugin preferences remain authoritative.
- macOS automation commands disable Cocoa state restoration with a trailing
  `-ApplePersistence NO`; a live regression verifies restart after SIGKILL.

- Validate Lua arguments, escaping, module names and finite timeouts.
- Preserve unrelated INI keys, unknown RPP content and line endings.
- Use unique run directories, fresh-save checks and structured error results.
- Reject invalid worker counts and overlapping or missing resource seeds before
  rebuilding a worker.
- Keep package version metadata tied to `rac.__version__` and verify release
  archives against source, rejecting stale files, unsafe entries and local or
  repository-only payload.

See [validation](docs/validation.md) for tested environments and known limits.
The repository currently records the two PyPI releases above. Package-index
publication evidence is not a substitute for the repository's source,
attribution or host-execution limitations.
