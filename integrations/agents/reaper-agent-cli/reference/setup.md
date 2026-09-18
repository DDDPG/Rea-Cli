# Environment and invocation

The project installer creates a private Python environment and binds this skill to it.
`runtime.json` contains relative paths; moving a Python venv is unsupported. Reinstall
for a moved workspace. It leaves harness login/settings/approval policy untouched.

Use `python3 TOOL doctor --profile offline --json`, then `--profile full` for host work.
`rac init` initializes only the configured dedicated resource. The toolkit sets
RAC_REAPER_RESOURCE to the project's `.reacli-toolkit/resource` unless already explicitly
set. REAPER must be installed and licensed separately. Do not install a DAW silently.
macOS needs a logged-in GUI session and a CoreAudio output configured by the user;
Linux needs a display or Xvfb and the runner dependencies. Windows supports offline
parser work, not the host runner. Host smoke: `python3 TOOL rac doctor --smoke --work-dir NEW_DIR --json`.

Lua 5.3/5.4 `luac` is needed: `RAC_LUAC_BIN` can select it. On macOS Homebrew's
lua@5.4 is discovered even when keg-only; on Linux use the lua5.4 package.
`RAC_REAPER_BIN` selects a nonstandard host executable. A doctor success does not
prove plugins or audio output work. Built-in plugin indexes are seeded from the native
installation on macOS; a missing plugin needs a deliberate scan of the dedicated resource.

The harness remains responsible for approving shell execution and file access.
If its sandbox blocks host startup, surface that specific failure and have the user
allow the required local execution. Do not alter global permissions or use a daemon.
Use the harness's existing authentication; the installer neither reads nor writes tokens.

Do not invoke the REAPER executable with `--version`: that switch is not a portable
version probe and can launch a GUI instance that waits indefinitely. Discover the
executable through doctor and obtain `reaper.GetAppVersion()` inside an isolated
script when the actual host version matters. Bound all host work with runner timeouts.
