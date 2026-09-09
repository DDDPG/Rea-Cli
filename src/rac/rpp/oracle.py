"""rac.rpp.oracle — Perlence/rpp 交叉验证 oracle (D2)

对同一 fixture 分别用自研 parser 与 Perlence parser 解析,
归一化后做结构 diff。空 diff = 两实现语义一致。
"""
from __future__ import annotations

from pathlib import Path

try:
    import rpp as perlence  # noqa: E402
    PERLENCE_AVAILABLE = True
except ImportError:  # vendor 依赖 (ply/attrs) 缺失时降级: oracle 测试跳过
    perlence = None
    PERLENCE_AVAILABLE = False

from .parser import Element, Line, parse  # noqa: E402


def _norm_mine(node: Element):
    """自研树 → 归一化 (tag, attrs, children|lines)."""
    out = []
    for c in node.children:
        if isinstance(c, Element):
            out.append(_norm_mine(c))
        else:
            toks = [c.key] + c.values
            out.append(tuple(toks))
    return (node.tag, tuple(node.attrs), tuple(out))


def _norm_perlence(el):
    """Perlence Element → 同款归一化。
    Perlence children 三形态: Element(chunk) / list(kv 行) / str(裸数据行, 如 base64)。"""
    out = []
    for c in el.children:
        if hasattr(c, "tag") and hasattr(c, "children"):
            out.append(_norm_perlence(c))
        elif isinstance(c, str):
            out.append((c,))  # 裸数据行: 与自研 Line(key, values=[]) 对齐
        else:
            out.append(tuple(str(v) for v in c))
    return (el.tag, tuple(str(a) for a in el.attrib), tuple(out))


def oracle_diff(path: str | Path) -> list[str]:
    """返回 diff 描述列表; 空 = 一致. Perlence 不可用时 raise RuntimeError."""
    if not PERLENCE_AVAILABLE:
        raise RuntimeError("Perlence/rpp unavailable; install with: pip install 'reacli[oracle]'")
    text = Path(path).read_text(encoding="utf-8")
    mine = _norm_mine(parse(text).root)
    theirs = _norm_perlence(perlence.loads(text))
    if mine == theirs:
        return []
    return _diff_nodes(mine, theirs, path_prefix="root")


def _diff_nodes(a, b, path_prefix: str, depth: int = 0) -> list[str]:
    diffs = []
    if depth > 6:
        return [f"{path_prefix}: subtree mismatch (deep)"]
    if a[0] != b[0]:
        return [f"{path_prefix}: tag {a[0]!r} != {b[0]!r}"]
    if a[1] != b[1]:
        diffs.append(f"{path_prefix}/{a[0]}: attrs {a[1]!r} != {b[1]!r}")
    ca, cb = a[2], b[2]
    if len(ca) != len(cb):
        diffs.append(f"{path_prefix}/{a[0]}: children count {len(ca)} != {len(cb)}")
    for i, (x, y) in enumerate(zip(ca, cb)):
        if x != y:
            if isinstance(x, tuple) and len(x) == 3 and isinstance(y, tuple) and len(y) == 3:
                diffs.extend(_diff_nodes(x, y, f"{path_prefix}/{a[0]}[{i}]", depth + 1))
            else:
                diffs.append(f"{path_prefix}/{a[0]}[{i}]: {x!r} != {y!r}")
            if len(diffs) > 10:
                diffs.append("... (truncated)")
                break
    return diffs
