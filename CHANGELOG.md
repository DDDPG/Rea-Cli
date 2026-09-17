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
