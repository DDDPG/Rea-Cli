"""rac.rpp.schema — ReaperDoc 语义层 (消费 docs/knowledge/rpp/rpp_schema.json)

为验证层/patch 层提供字段级元数据查询与类型化写入校验。
键制 <section>:<KEY> (上下文敏感)。
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from rac.resources import asset

SCHEMA_PATH = asset("knowledge/rpp_schema.json")


@lru_cache(maxsize=1)
def load(path: str | Path | None = None) -> dict:
    p = Path(path) if path else SCHEMA_PATH
    return json.loads(p.read_text(encoding="utf-8"))


def key_meta(section: str, key: str, path: str | Path | None = None) -> dict | None:
    """('track','VOLPAN') -> {name, section, fields, tags, verified} 或 None"""
    return load(path)["keys"].get(f"{section}:{key}")


def field_meta(section: str, key: str, index: int,
               path: str | Path | None = None) -> dict | None:
    """('track','VOLPAN',1) -> {index,label,type,description,enum_candidates} 或 None"""
    meta = key_meta(section, key, path)
    if not meta:
        return None
    for f in meta["fields"]:
        if f["index"] == index:
            return f
    return None


def field_description(section: str, key: str, index: int,
                      path: str | Path | None = None) -> str | None:
    f = field_meta(section, key, index, path)
    return f["description"] if f else None


# ---------------------------------------------------------------------------
# 类型化读写校验
# ---------------------------------------------------------------------------

_INT_RE = re.compile(r"^[+-]?\d+$")
_FLOAT_RE = re.compile(r"^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$")
_GUID_RE = re.compile(r"^\{[0-9A-Fa-f-]+\}$")


_EXACT_EQ = re.compile(r"^(-?\d+)\s*=\s*")
_EXACT_DASH = re.compile(r"^(-?\d+)\s+-\s+")


def _enum_allowed(enum_candidates: list[str]) -> set[str] | None:
    """enum_candidates → 可校验的精确值集合; 不可精确化返回 None (不校验)。

    ReaperDoc 两种精确枚举分隔符: '0 = off' 与 '1 - normal'。
    位标志形式 ('+2 = ...' / '-64 = ...' 修饰义) 整表降级为不校验。
    """
    allowed = set()
    for item in enum_candidates:
        if item.startswith("+"):
            return None  # 位标志修饰义 → 整表不校验
        m = _EXACT_EQ.match(item) or _EXACT_DASH.match(item)
        if not m:
            return None  # 含不可解析条目 → 整表不校验
        allowed.add(m.group(1))
    return allowed if allowed else None


def validate_value(section: str, key: str, index: int, value: str,
                   path: str | Path | None = None) -> str | None:
    """类型校验 value 是否可写入该字段。返回 None=通过, 否则错误描述。

    只做类型级拒绝 (int/float/GUID)。枚举不在此拒绝——
    ReaperDoc 的 enum_candidates 是文档摘录而非穷尽契约 (实证:
    track:BEAT 只记了 -1 但合法值为 0-3), 枚举偏差走 enum_check 警告通道。
    """
    f = field_meta(section, key, index, path)
    if not f:
        return None  # 未知字段不校验 (tier-3 透传)
    t = (f.get("type") or "").lower()
    if "guid" in t and not _GUID_RE.match(value):
        return f"{section}:{key}[{index}] expects GUID, got {value!r}"
    if "int" in t and "float" not in t and not _INT_RE.match(value):
        return f"{section}:{key}[{index}] expects int, got {value!r}"
    if "float" in t and not _FLOAT_RE.match(value):
        return f"{section}:{key}[{index}] expects float, got {value!r}"
    return None


def enum_check(section: str, key: str, index: int, value: str,
               path: str | Path | None = None) -> str | None:
    """枚举偏差警告 (非阻断): 可精确化的候选集中不含该值时返回警告, 否则 None。

    警告 = "文档未记载但不必然非法"; 位标志形式返回 None (不检查)。"""
    f = field_meta(section, key, index, path)
    if not f or not f.get("enum_candidates"):
        return None
    allowed = _enum_allowed(f["enum_candidates"])
    if allowed is not None and value not in allowed:
        return (f"enum warning: {section}:{key}[{index}] value {value!r} "
                f"not documented in {sorted(allowed)} (may still be legal)")
    return None


def validate_line(section: str, line, path: str | Path | None = None) -> list[str]:
    """对整行做类型校验, 返回错误列表 (空 = 通过)。"""
    errors = []
    for i, v in enumerate(line.values):
        err = validate_value(section, line.key, i + 1, v, path)
        if err:
            errors.append(err)
    return errors
