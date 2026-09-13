# Changelog

## 0.1.0 — unreleased

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
No package-index release has been published from this project.
