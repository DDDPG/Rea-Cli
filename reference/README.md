# REAPER automation developer handbook

[中文](README.zh-CN.md) · [Project](../README.md) · [API signatures](../docs/api.md) · [Agent skill](../skills/reaper-agent-cli/SKILL.md)

This handbook defines how to choose, implement and verify REAPER automation with reacli. It complements the API reference with units, object identity, execution lifecycle and evidence requirements. Start with a topic below; exact signatures remain in the implementation and packaged indexes.

## Topics

| Guide | What to check | 中文 |
|---|---|---|
| [Invocation and delivery](workflow/README.md) | Environment, path selection, proof, retry, concurrency | [调用规范](workflow/README.zh-CN.md) |
| [RPP](rpp/README.md) | Context, units, safe patches, opaque data, semantic diff | [RPP 规范](rpp/README.zh-CN.md) |
| [ReaScript](reascript/README.md) | Track/folder/item/take/envelope/MIDI, FX, actions, render | [宿主 API 规范](reascript/README.zh-CN.md) |
| [Lua](lua/README.md) | Generator registry, custom bodies, snippets and execution | [Lua 规范](lua/README.zh-CN.md) |
| [JSFX](jsfx/README.md) | EEL2 source, instance state, DSP checks and examples | [JSFX 规范](jsfx/README.zh-CN.md) |
| [Evidence archive](knowledge/README.md) | Every imported note/index, versions and known gaps | [资料目录](knowledge/README.zh-CN.md) |

For a working project, use the [quick start](../README.md) or [native-synthesis showcase](../examples/README.md). For an agent, use the repository [reaper-agent-cli skill](../skills/reaper-agent-cli/SKILL.md), which routes to these same guides without copying the runtime.

## Source of truth

- **Current invocation contract:** [environment](../docs/environment.md), [API guide](../docs/api.md), implementation in `src/rac/`, and these paired language guides. The English and Chinese pages describe the same scope; update them together.
- **Current test evidence:** [validation](../docs/validation.md). New prose does not constitute a new live test.
- **Historical evidence:** `knowledge/` retains source language, dates, limitations and attribution. `live` / `verified-live` refer to source-reported experiments; `doc` / `human` describe documentary or editorial evidence. None certifies the current host.
- **Unknowns:** check the gap registry and target host. Neither schema coverage nor an old action index proves feature availability.

## Canonical resources and distribution

`rac knowledge api GetTrack` reads the [API index](../src/rac/data/knowledge/api_index.json); `rac knowledge rpp track:VOLPAN` reads the [RPP schema](../src/rac/data/knowledge/rpp_schema.json). `rac resources --output ./templates` exports the [entry](../src/rac/data/lua/entry.lua), minimal project and 11 [Lua snippets](../src/rac/data/lua/stdlib/). Do not maintain duplicate copies in the skill.

`reference/` and `skills/` are delivered in Git, not in wheel or sdist. Runtime indexes/templates remain packaged. The skill requires this checkout and an installed reacli; it is not a zero-dependency standalone runtime.

## Maintenance

Keep immutable source hashes in [source-manifest.json](source-manifest.json). When changing imported content, update its destination hash and editorial change record. New guide translations are maintained prose, not translations of every historical dataset. Preserve original identifiers and source paths so external reviewers can trace a statement to evidence.

See [sources and attribution](SOURCES.md) and [third-party notices](../THIRD_PARTY_NOTICES.md) for provenance and redistribution limits. Do not copy personal REAPER settings, license files, plugin caches or machine-specific media into documentation or skills.
