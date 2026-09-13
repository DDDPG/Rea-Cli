"""Generate standalone Lua scripts from validated operations and bundled templates.

OP_REGISTRY defines supported operations and their argument types. Scripts
include the proof protocol and the required standard-library snippets, then
pass through Lua 5.3/5.4 syntax checking before being returned to the caller.
For custom script bodies, export the entry skeleton with ``reacli resources``.
"""
from __future__ import annotations

import math
import re
import subprocess
import tempfile
from pathlib import Path
from rac.resources import asset
from rac.environment import find_luac

ENTRY = asset("lua/entry.lua")
STDLIB = asset("lua/stdlib")
BODY_PAT = re.compile(r"local function body\(\).*?\nend\n-- ={10,}", re.S)

# op 白名单: op 名 → (模块, 函数, 参数类型)
OP_REGISTRY = {
    "track.create": ("track", "create", (int, str)),
    "track.set_volume_db": ("track", "set_volume_db", (int, float)),
    "track.set_pan": ("track", "set_pan", (int, float)),
    "track.set_mute": ("track", "set_mute", (int, bool)),
    "track.set_name": ("track", "set_name", (int, str)),
    "track.set_color": ("track", "set_color", (int, int, int, int)),
    "marker.add": ("marker", "add", (int, float, str)),
    "marker.add_batch": ("marker", "add_batch", (list,)),
    "marker.add_region": ("marker", "add_region", (int, float, float, str)),
    "item.insert_media": ("item", "insert_media", (int, str, float)),
    "item.set_position": ("item", "set_position", (int, int, float)),
    "item.set_length": ("item", "set_length", (int, int, float)),
    "item.set_fade": ("item", "set_fade", (int, int, float, float)),
    "item.set_mute": ("item", "set_mute", (int, int, bool)),
    "item.split_at": ("item", "split_at", (int, int, float)),
    "env.set_points_db": ("env", "set_points_db", (int, str, list)),
    "fx.add_by_name": ("fx", "add_by_name", (int, str)),
    "fx.set_param_normalized": ("fx", "set_param_normalized", (int, int, int, float)),
    "fx.set_enabled": ("fx", "set_enabled", (int, int, bool)),
    "midi.create_item": ("midi", "create_item", (int, float, float)),
    "midi.insert_note": ("midi", "insert_note", (int, int, int, int, float, float)),
    "render.set_config": ("render", "set_config", (dict,)),
    "project.set_tempo": ("project", "set_tempo", (float,)),
    "project.set_notes": ("project", "set_notes", (str,)),
    "routing.create_send": ("routing", "create_send", (int, int)),
}


def _lua_literal(v) -> str:
    if v is None:
        return "nil"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        if isinstance(v, float) and not math.isfinite(v):
            raise ValueError("Lua numeric arguments must be finite")
        return repr(v)
    if isinstance(v, str):
        # Lua does not accept JSON's \uXXXX escapes. Fixed-width decimal
        # escapes handle control characters without consuming following digits.
        return '"' + ''.join(('\\' + c if c in '\\"' else
                              f'\\{ord(c):03d}' if ord(c) < 32 or ord(c) == 127
                              else c) for c in v) + '"'
    if isinstance(v, list):
        return "{" + ", ".join(_lua_literal(x) for x in v) + "}"
    if isinstance(v, dict):
        items = ", ".join(f"[{_lua_literal(k)}] = {_lua_literal(val)}" for k, val in v.items())
        return "{" + items + "}"
    raise TypeError(f"unsupported arg type: {type(v)}")


def _check_types(op: str, args: list):
    spec = OP_REGISTRY[op]
    expected = spec[2]
    if len(args) != len(expected):
        raise ValueError(f"{op}: expects {len(expected)} args, got {len(args)}")
    for i, (a, t) in enumerate(zip(args, expected)):
        if t is float and isinstance(a, (int, float)) and not isinstance(a, bool):
            if isinstance(a, float) and not math.isfinite(a):
                raise ValueError(f"{op} arg{i}: number must be finite")
            continue  # int 可升 float
        if t is bool and isinstance(a, bool):
            continue
        if not isinstance(a, t) or (t in (int, float) and isinstance(a, bool)):
            raise TypeError(f"{op} arg{i}: expect {t.__name__}, got {type(a).__name__}")


def generate(intent: dict, out_path: str | Path | None = None) -> Path:
    """intent = {"modules": [...], "ops": [{"op": "track.create", "args": [0, "x"]}],
                 "save_as": "/abs/out.rpp" (可选, 仅写入脚本注释供 runner 读)}"""
    ops = intent.get("ops", [])
    modules = list(intent.get("modules", []))
    available = {p.name[:-4] for p in STDLIB.iterdir() if p.name.endswith(".lua")}
    if any(not isinstance(m, str) or m not in available for m in modules):
        raise ValueError("Unknown Lua module; select a bundled stdlib module")
    for o in ops:
        op_name = o.get("op")
        if op_name not in OP_REGISTRY:
            raise ValueError(f"op not whitelisted: {op_name}")
        _check_types(op_name, o.get("args", []))
        mod = OP_REGISTRY[op_name][0]
        if mod not in modules:
            modules.append(mod)

    lines = []
    for i, o in enumerate(ops):
        mod, fn, _ = OP_REGISTRY[o["op"]]
        args = ", ".join(_lua_literal(a) for a in o.get("args", []))
        call = f"std_{mod}.{fn}({args}{', ' if args else ''}log)"
        lines.append(f'  local r_{i} = {call}')
        lines.append(f'  if not r_{i}.ok then RUN.result = RUN.result or {{}}; '
                     f'RUN.result["op_{i}_error"] = r_{i}.reason; log("error", '
                     f'"op {o["op"]} blocked: " .. tostring(r_{i}.reason)) end')
    lines.append('  RUN.result = RUN.result or { ok = true }')
    body = "\n".join(lines)

    lib = "\n".join(STDLIB.joinpath(f"{m}.lua").read_text(encoding="utf-8")
                    for m in modules)
    body_with_lib = lib + "\nlocal function body()\n" + body + "\nend"
    script = BODY_PAT.sub(lambda _: body_with_lib + "\n-- " + "=" * 75,
                          ENTRY.read_text(encoding="utf-8"))

    if out_path is None:
        with tempfile.NamedTemporaryFile(prefix="reacli_", suffix=".lua", delete=False) as stream:
            out_path = Path(stream.name)
    out_path = Path(out_path)
    out_path.write_text(script, encoding="utf-8")
    validate(out_path)  # Validate before returning the generated script.
    return out_path


def validate(script: str | Path, *, luac_bin: str | None = None) -> None:
    """luac -p 语法预检; 失败 raise SyntaxError (绝不发给 REAPER)。"""
    r = subprocess.run([find_luac(luac_bin), "-p", str(Path(script).resolve())],
                       capture_output=True, text=True, timeout=15)
    if r.returncode != 0:
        raise SyntaxError(f"lua syntax error in {script}: {r.stderr.strip()}")
