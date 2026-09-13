# Contributing to reacli

Contributions that make REAPER automation easier to reproduce, inspect, and
verify are welcome. Keep each change focused and include enough context for a
reviewer to reproduce the behavior. This project is an alpha; changes to public
commands, Python APIs, or proof fields should be described explicitly.

## Set up a development environment

Use Python 3.10+ and a virtual environment from the repository root:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
python -m pytest
```

Install a Lua 5.3/5.4 compiler to run the generation tests. On macOS use
`brew install lua@5.4`; its keg-only compiler is discovered automatically.
On Debian/Ubuntu use `sudo apt-get install lua5.4`. Use a newer Python if the
system interpreter reports 3.9. The [environment guide](docs/environment.md)
covers host preparation and compiler overrides.

Tests import the installed `rac` package through the `src/` layout. Do not add
checkout-specific `PYTHONPATH` entries or `sys.path` modifications. Both
`test_*` and existing `t_*` test functions are collected by pytest.

## Run the checks that cover your change

The default suite does not launch REAPER. Lua-dependent cases are skipped if
a compatible compiler is unavailable, so check the skip summary when changing
generation or templates. Run a relevant test file during development, then the
full suite before submitting:

```bash
python -m pytest tests/test_rpp.py
python -m pytest
```

Build and inspect the distributions when changing package metadata, resources,
manifests, or installation behavior:

```bash
python -m build
python -m twine check dist/*
python scripts/check_dist.py dist
```

Also install the wheel into a clean environment and verify it from outside the
checkout. The [release guide](docs/releasing.md) documents archive inspection
and installation checks. CI runs offline tests and distribution checks on the
configured Python/platform matrix; it does not install or live-test REAPER.
Local results and recorded live validation are distinct from CI results.

## Live integration tests

Prepare an official REAPER installation and Lua 5.3/5.4 using the
[environment guide](docs/environment.md), then run:

```bash
reacli init
reacli doctor --json
RAC_TEST_LIVE=1 python -m pytest -m live
reacli doctor --render --work-dir ./smoke-artifacts --json
```

Live tests create synthetic projects, render audio, and start REAPER processes.
Use dedicated resource directories and generated output paths. Do not point
tests at personal projects or use the native REAPER resource tree as a writable
test target. Record OS, CPU architecture, Python, REAPER, Lua versions, the exact
command, and pass/skip/failure counts with live results. See the
[validation record](docs/validation.md) for established coverage and limits.

Linux uses dummy audio and an X display or Xvfb. macOS uses initialized CoreAudio
settings and independent `-newinst` processes. The default macOS pool shares the
installed app with separate worker resources; it needs no signing tools.
Keep legacy `copy_app=True` testing separate: it copies and signs bundles and
has not passed the recorded live validation.

## Implementation expectations

- Preserve untouched RPP text, unknown fields, line endings, and opaque plugin
  chunks. An edit to one known field should not rewrite unrelated content.
- Keep CLI exit codes and JSON responses consistent, including failure paths.
  A process exit or a valid proof alone does not establish the intended edit;
  check the saved state or audio when that is the behavior under test.
- Treat Lua argument validation, proof fields, timeout cleanup, save freshness,
  and worker isolation as compatibility-sensitive behavior. Add a focused
  regression test for a reproducible defect, rather than a test that merely
  repeats the implementation.
- Keep platform behavior explicit. Mock the native home/resource paths in
  offline tests; never depend on a developer's audio device, personal INI,
  installed plugins, or running desktop session.
- Preserve the doctor's read-only behavior unless `--smoke` or `--render` was
  explicitly requested. Resource initialization belongs in initialization or
  execution paths.

Use synthetic audio and small fixtures. Do not commit REAPER executables,
plugin binaries, proprietary media, license keys, credentials, generated run
directories, virtual environments, or personal paths. Share logs only after
removing private file paths and device details.

## Documentation and knowledge changes

Keep [README.md](README.md) and [README.zh-CN.md](README.zh-CN.md) aligned for
installation, quick starts, supported platforms, and important limitations.
Put detailed API behavior in `docs/api.md`, setup and troubleshooting in
`docs/environment.md`, and reusable workflow material in `reference/`.

`reference/` must remain outside wheels and source distributions. Canonical
knowledge and Lua assets belong in `src/rac/data/`: maintain one copy of the two JSON
indexes and 12 Lua files, and link to them from repository notes. Record sources
and permissions for new reference material. Public availability alone is not
redistribution permission; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
and [reference/SOURCES.md](reference/SOURCES.md).

Check relative links and run documented examples with a fresh output directory.
Keep machine-specific validation artifacts separate from public documentation;
publish concise, reproducible evidence with private details removed.

## Report a bug or submit a change

For a bug report, include the shortest reproduction, expected and actual
behavior, reacli/Python/OS versions, and relevant sanitized logs. For execution
issues, include the REAPER version and `reacli doctor --json` output. State
whether the problem reproduces with bundled fixtures and stock REAPER plugins.
Follow [SECURITY.md](SECURITY.md) for potentially sensitive reports.

A pull request should explain the user-visible problem, the resulting behavior,
and the checks performed. Include screenshots only when they clarify actual
REAPER behavior, and avoid unrelated formatting or generated artifacts. Update
the changelog for user-visible behavior changes and note known limits instead
of implying validation that has not been run.

## Working together

Keep discussion constructive and specific. Explain the behavior or evidence
behind a concern, respect differing experience levels, and review the change
rather than the person. Personal attacks and harassment do not belong in issues,
reviews or other project discussions.

## Developer handbook and repository skill

Maintain the English and Chinese [developer guides](reference/README.md) together. Keep current invocation rules separate from original versioned evidence. Preserve source hashes and update destination hashes in `reference/source-manifest.json` when changing tracked reference content.

The [repository skill](skills/reaper-agent-cli/SKILL.md) uses the installed package and these guides. Update its routing when adding topics, without vendoring rac or Lua templates. Check local links, run affected examples, validate the skill frontmatter, and build distributions to confirm `reference/` and `skills/` remain Git-only. Documentation checks do not establish new live REAPER validation.

同步维护[双语开发规范](reference/README.zh-CN.md)，将当前调用约定与历史证据分开。保留来源哈希，修改纳入清单的资料后更新目标哈希。Skill 共用包内资源；变更后检查链接、相关示例、skill 格式及分发范围，不将文档检查记为实机测试。
