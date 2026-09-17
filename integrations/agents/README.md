# REAPER CLI harness integration

[Quick start](../../docs/harness/README.md) · [中文](../../docs/harness/README.zh-CN.md)

The shared [skill](reaper-agent-cli/SKILL.md) supports Claude Code, Codex and Qwen Code.
The project installer binds a Python runtime, checks CLI availability and copies the skill
into each harness's native discovery directory. It does not configure MCP or global permissions.
The [requirements-only evaluation](acceptance/showcase-brief.md) contains no solution script.

```sh
python integrations/agents/reaper-agent-cli/scripts/install.py --source . --project ../my-reaper-work --harness all
```

The candidate ZIP includes this installer's code and generic coding assets. It can install
from candidate wheels without a source checkout. See
[recorded outcomes](../../docs/harness/acceptance.md) for live validation boundaries.
