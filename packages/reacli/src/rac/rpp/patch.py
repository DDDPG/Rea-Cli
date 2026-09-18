"""rac.rpp.patch — RPP 声明式修改 API (set-based 幂等, D6)

所有操作: 传入 = 目标状态, 重复执行终态相同 (重复执行 diff 为空)。
修改只标脏不重排; 新增内容经 insert_* 显式指定位置。
"""
from __future__ import annotations

from .parser import Document, Element, Line, quote_value
from .schema import validate_value


def _mark(doc: Document, *nodes):
    doc.touch()
    for n in nodes:
        n.dirty = True


# --- 通用行字段 ---

def set_value(doc: Document, line: Line, index: int, value: str,
              *, section: str | None = None) -> Line:
    """把 line 的第 index 个 value 设为 value (0 基)。不足补位。
    提供 section 时按 rpp_schema 做类型/枚举校验, 失败 raise ValueError。"""
    if section:
        err = validate_value(section, line.key, index + 1, value)
        if err:
            raise ValueError(err)
    while len(line.values) <= index:
        line.values.append("")
    if line.values[index] != value:
        line.values[index] = value
        _mark(doc, line)
    return line


def ensure_line(doc: Document, parent: Element, key: str,
                values: list[str] | None = None, indent: str = "  ") -> Line:
    """find-or-create: parent 下已有 key 行则返回首个, 否则新建 (幂等)。"""
    existing = parent.find_line(key)
    if existing is not None:
        return existing
    line = Line(key=key, values=values or [], raw=indent + key, dirty=True)
    parent.children.append(line)
    _mark(doc, line)  # 只脏新行; 父块开块行无需重排
    return line


# --- Track ---

def set_track_name(doc: Document, track: Element, name: str) -> None:
    line = track.find_line("NAME") or ensure_line(doc, track, "NAME", indent="    ")
    set_value(doc, line, 0, name)


def set_track_volume(doc: Document, track: Element, linear: float) -> None:
    """VOLPAN field 1 = linear gain。set-based: N 次执行同终态。"""
    line = track.find_line("VOLPAN") or ensure_line(doc, track, "VOLPAN",
                                                    ["1", "0", "-1", "-1", "1"],
                                                    indent="    ")
    set_value(doc, line, 0, f"{linear:g}", section="track")


def set_track_pan(doc: Document, track: Element, pan: float) -> None:
    line = track.find_line("VOLPAN") or ensure_line(doc, track, "VOLPAN",
                                                    ["1", "0", "-1", "-1", "1"],
                                                    indent="    ")
    set_value(doc, line, 1, f"{pan:g}", section="track")


def set_track_mute(doc: Document, track: Element, muted: bool) -> None:
    line = track.find_line("MUTESOLO") or ensure_line(doc, track, "MUTESOLO",
                                                      ["0", "0", "0"], indent="    ")
    set_value(doc, line, 0, "1" if muted else "0")


# --- Item ---

def set_item_position(doc: Document, item: Element, seconds: float) -> None:
    line = item.find_line("POSITION")
    if line is None:
        raise ValueError("item has no POSITION line")
    set_value(doc, line, 0, f"{seconds:g}", section="item")


def set_item_length(doc: Document, item: Element, seconds: float) -> None:
    line = item.find_line("LENGTH")
    if line is None:
        raise ValueError("item has no LENGTH line")
    set_value(doc, line, 0, f"{seconds:g}", section="item")


# --- Marker (project 根级 MARKER 行) ---

def set_marker(doc: Document, index: int, pos: float, name: str) -> Line:
    """find-before-create: 已有同 index 的 MARKER 则改, 否则在根级末尾插入。
    中段字段(field 5-7, 见 gap_registry)按 REAPER 样本默认 '0 0 1 B'。"""
    for line in doc.root.find_lines("MARKER"):
        if line.values and line.values[0] == str(index):
            set_value(doc, line, 1, f"{pos:g}", section="project")
            set_value(doc, line, 2, name, section="project")
            return line
    import uuid
    line = Line(key="MARKER",
                values=[str(index), f"{pos:g}", name, "0", "0", "1", "B",
                        "{%s}" % str(uuid.uuid4()).upper(), "0", "2"],
                raw="", dirty=True)
    line.raw = "  " + line.key  # indent 占位, serialize 重算
    doc.root.children.append(line)
    _mark(doc, line)  # 只脏新行
    return line


def delete_marker(doc: Document, index: int) -> bool:
    """删除指定 index 的 MARKER 行; 不存在则 noop (幂等)。"""
    for i, line in enumerate(doc.root.children):
        if (isinstance(line, Line) and line.key == "MARKER"
                and line.values and line.values[0] == str(index)):
            del doc.root.children[i]
            doc.touch()
            return True
    return False
