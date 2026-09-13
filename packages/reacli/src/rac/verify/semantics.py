"""rac.verify.semantics — RPP 语义 diff

与文本 diff 的区别:
- 结构对齐 (chunk 按 tag 配对, 行按 key 配对)
- **默认补全容忍**: REAPER 保存会全量补默认字段; 一侧缺失的 KEY 若等于
  默认值表中的值 → 不算差异 (默认值表来自实机保存 fixture)
- **浮点容差**: 数值 token 按 float_tol 比较 (REAPER 重存可能改精度格式)
- base64/blob 行按原文精确比较 (blob_denylist)
"""
from __future__ import annotations

from pathlib import Path

from rac.rpp.parser import Document, Element, Line, parse
from rac.resources import read_text

# 默认补全参照: 实机 REAPER 7.62/macOS 保存极简工程的产物
_DEFAULTS_FIXTURE = "defaults/minimal_after_reaper_save.rpp"


def _load_defaults() -> dict[str, tuple[str, ...]]:
    # 只收根级行 (容忍仅根级生效; 全树收集会在极端场景误吞)
    doc = parse(read_text(_DEFAULTS_FIXTURE))
    out = {}
    for c in doc.root.children:
        if isinstance(c, Line) and c.key:
            out.setdefault(c.key, tuple(c.values))
    return out


def _iter_lines(el: Element):
    for c in el.children:
        if isinstance(c, Line):
            yield c
        else:
            yield from _iter_lines(c)


def _is_float(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def _line_eq(a: Line, b: Line, float_tol: float,
             strict_guid: bool = False) -> bool:
    if a.key != b.key or len(a.values) != len(b.values):
        return False
    for x, y in zip(a.values, b.values):
        if x == y:
            continue
        if _is_float(x) and _is_float(y) and abs(float(x) - float(y)) <= float_tol:
            continue
        if not strict_guid and _GUID_TOKEN_RE.match(x) and _GUID_TOKEN_RE.match(y):
            continue  # MARKER/FXID 等 GUID 值同 attrs 规则归一
        return False
    return True


_GUID_TOKEN_RE = __import__("re").compile(r"^\{[0-9A-Fa-f-]+\}$")


def _attrs_eq(a: list[str], b: list[str], strict_guid: bool = False) -> bool:
    """chunk attrs 比对: 默认 GUID token 归一 (REAPER 重生成 GUID 属正常扰动);
    strict_guid=True 时全精确 (检测引用破坏场景)。"""
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if x == y:
            continue
        if not strict_guid and _GUID_TOKEN_RE.match(x) and _GUID_TOKEN_RE.match(y):
            continue
        return False
    return True


def _diff_children(a: Element, b: Element, path: str, float_tol: float,
                   defaults: dict, diffs: list, strict_guid: bool):
    # chunk 按 (tag, 序号) 配对
    ca = [c for c in a.children if isinstance(c, Element)]
    cb = [c for c in b.children if isinstance(c, Element)]
    if len(ca) != len(cb):
        diffs.append(f"{path}: chunk 数不同 {len(ca)} vs {len(cb)}")
    for i, (x, y) in enumerate(zip(ca, cb)):
        if x.tag != y.tag:
            diffs.append(f"{path}>[{i}]: tag {x.tag} != {y.tag}")
            continue
        if not _attrs_eq(x.attrs, y.attrs, strict_guid):
            diffs.append(f"{path}>{x.tag}[{i}]: attrs {x.attrs} != {y.attrs}")
        _diff_children(x, y, f"{path}>{x.tag}[{i}]", float_tol, defaults, diffs,
                       strict_guid)

    # 行按 key 分组配对 (同 key 多行按出现序)
    la = [c for c in a.children if isinstance(c, Line) and c.key]
    lb = [c for c in b.children if isinstance(c, Line) and c.key]
    keys = []
    for l in la + lb:
        if l.key not in keys:
            keys.append(l.key)
    for key in keys:
        xa = [l for l in la if l.key == key]
        xb = [l for l in lb if l.key == key]
        for i in range(max(len(xa), len(xb))):
            va = xa[i] if i < len(xa) else None
            vb = xb[i] if i < len(xb) else None
            if va is None:
                if _is_default(key, vb.values, defaults, path):
                    continue
                diffs.append(f"{path}: {key}[{i}] 仅右存在: {vb.values}")
            elif vb is None:
                if _is_default(key, va.values, defaults, path):
                    continue
                diffs.append(f"{path}: {key}[{i}] 仅左存在: {va.values}")
            elif not _line_eq(va, vb, float_tol, strict_guid):
                diffs.append(f"{path}: {key}[{i}]: {va.values} != {vb.values}")


_KEY_NAME_RE = __import__("re").compile(r"^[A-Z0-9_]+$")


def _is_default(key: str, values: list[str], defaults: dict, path: str) -> bool:
    """默认补全容忍: 仅对工程根级 (path=="root") 的**具名标量 KEY** 生效。

    排除规则（确保 blob 删除仍然报告差异）:
    - key 必须是具名 KEY (^[A-Z0-9_]+$)——base64 数据行 (RENDER_CFG 等的
      blob 内容) 混有大小写/符号, 天然被排除
    - 必须带 values——裸数据行 (无 values 的 base64) 不容忍
    深嵌套同名 KEY 也不容忍 (防误吞)。
    """
    if path != "root":
        return False
    if not values or not _KEY_NAME_RE.match(key):
        return False
    d = defaults.get(key)
    return d is not None and tuple(values) == d


def semantic_diff(doc_a: Document, doc_b: Document, *,
                  float_tol: float = 1e-4,
                  use_defaults: bool = True,
                  strict_guid: bool = False) -> list[str]:
    """语义 diff: 返回差异描述列表; 空 = 语义等价。
    strict_guid=True 时 GUID 也精确比对 (引用破坏检测)。"""
    defaults = _load_defaults() if use_defaults else {}
    diffs: list[str] = []
    if not _attrs_eq(doc_a.root.attrs, doc_b.root.attrs, strict_guid):
        diffs.append(f"root attrs: {doc_a.root.attrs} != {doc_b.root.attrs}")
    _diff_children(doc_a.root, doc_b.root, "root", float_tol, defaults, diffs,
                   strict_guid)
    return diffs
