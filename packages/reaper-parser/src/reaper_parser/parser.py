"""Lossless RPP documents, native tokenization and explicit dirty emission."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


class RPPParseError(SyntaxError):
    pass


# ---------------------------------------------------------------------------
# 行分词 (key + values; values 为语义值, 引号已剥)
# ---------------------------------------------------------------------------


def tokenize(text: str) -> list[str]:
    """REAPER/WDL tokens: three delimiters, literal backslashes (not C escapes)."""
    tokens = []
    i = 0
    while i < len(text):
        if text[i] in " \t":
            i += 1
            continue
        if text[i] in "\"'`":
            delimiter = text[i]
            end = text.find(delimiter, i + 1)
            if end < 0:
                raise RPPParseError(f"unterminated quote in line: {text!r}")
            tokens.append(text[i + 1 : end])
            i = end + 1
        else:
            end = i
            while end < len(text) and text[end] not in " \t":
                end += 1
            tokens.append(text[i:end])
            i = end
    return tokens


def quote_value(v: str) -> str:
    """Choose an unused native quote delimiter rather than inventing escape syntax."""
    if "\n" in v or "\r" in v:
        raise ValueError("Multiline value requires a text chunk")
    if v and not any(c in " \t\"'`" for c in v):
        return v
    for delimiter in "\"'`":
        if delimiter not in v:
            return delimiter + v + delimiter
    if v and v[0] not in "\"'`" and not any(c in " \t" for c in v):
        return v
    raise ValueError(
        "Value contains every REAPER quote delimiter; cannot emit losslessly"
    )


# ---------------------------------------------------------------------------
# 节点模型
# ---------------------------------------------------------------------------


@dataclass
class Line:
    """键值行或裸数据行 (如 base64)。key 为首 token; 裸数据行 values 为空。"""

    key: str
    values: list[str]
    raw: str  # 原始完整行 (含缩进)
    dirty: bool = False
    _eol: str | None = field(default=None, repr=False)

    def serialize(self) -> str:
        indent = self.raw[: len(self.raw) - len(self.raw.lstrip())]
        parts = [self.key] + [quote_value(v) for v in self.values]
        return indent + " ".join(parts)


@dataclass
class Element:
    """chunk: <TAG attrs... children... >"""

    tag: str
    attrs: list[str]
    children: list[Element | Line] = field(default_factory=list)
    raw_open: str = ""  # 原始开块行 (含缩进与 <)
    raw_close: str | None = None  # 原始闭块行 (保真回放; dirty 时重排)
    dirty: bool = False
    _open_eol: str | None = field(default=None, repr=False)
    _close_eol: str | None = field(default=None, repr=False)

    # --- 查询 ---
    def find_chunks(self, tag: str) -> list[Element]:
        return [c for c in self.children if isinstance(c, Element) and c.tag == tag]

    def find_chunk(self, tag: str) -> Element | None:
        return next(iter(self.find_chunks(tag)), None)

    def find_lines(self, key: str) -> list[Line]:
        return [c for c in self.children if isinstance(c, Line) and c.key == key]

    def find_line(self, key: str) -> Line | None:
        return next(iter(self.find_lines(key)), None)

    def iter_chunks(self, tag: str | None = None):
        for c in self.children:
            if isinstance(c, Element):
                if tag is None or c.tag == tag:
                    yield c
                yield from c.iter_chunks(tag)

    def serialize(self) -> list[str]:
        # dirty 只意味着"重排我的开块行" (tag/attrs 变化); 子节点变化不需要置父脏
        indent = self.raw_open[: len(self.raw_open) - len(self.raw_open.lstrip())]
        if self.dirty or not self.raw_open:
            open_line = (
                indent
                + "<"
                + " ".join([self.tag] + [quote_value(a) for a in self.attrs])
            )
        else:
            open_line = self.raw_open
        out = [open_line]
        for c in self.children:
            if isinstance(c, Element):
                out.extend(c.serialize())
            else:
                out.append(c.raw if not c.dirty else c.serialize())
        if not self.dirty and self.raw_close is not None:
            out.append(self.raw_close)
        else:
            out.append(indent + ">")
        return out


@dataclass
class Document:
    root: Element
    _original_text: str
    _dirty: bool = False
    _newline: str = "\n"  # 文档换行风格 (REAPER 写 CRLF, 实证)
    _trailing: list[str] = field(default_factory=list)  # 根块闭合后的尾部行
    _trailing_newline: bool = True  # 原文末尾是否有换行

    source_path: Path | None = None
    _bom: str = ""
    _tail_raw: str = ""

    @property
    def project(self):
        from .model import Project

        return Project(self, self.root)

    def save(self, path: str | Path, *, overwrite: bool = False) -> Path:
        target = Path(path)
        with target.open("wb" if overwrite else "xb") as f:
            f.write(self.text().encode("utf-8", errors="surrogateescape"))
        return target

    def text(self) -> str:
        if not self._dirty:
            return self._original_text

        def eol(value):
            return self._newline if value is None else value

        def walk(node):
            opening = (
                node.serialize()[0]
                if node.dirty or not node.raw_open
                else node.raw_open
            )
            yield opening + eol(node._open_eol)
            for child in node.children:
                if isinstance(child, Element):
                    yield from walk(child)
                else:
                    yield (child.serialize() if child.dirty else child.raw) + eol(
                        child._eol
                    )
            close = (
                node.raw_close
                if node.raw_close is not None and not node.dirty
                else node.raw_open[: len(node.raw_open) - len(node.raw_open.lstrip())]
                + ">"
            )
            yield close + eol(node._close_eol)

        return self._bom + "".join(walk(self.root)) + self._tail_raw

    def tracks(self) -> list[Element]:
        return self.root.find_chunks("TRACK")

    def markers(self) -> list[Line]:
        return self.root.find_lines("MARKER")

    def touch(self):
        self._dirty = True


# ---------------------------------------------------------------------------
# 解析
# ---------------------------------------------------------------------------


def parse(source: str | Path) -> Document:
    """Parse UTF-8 (including undecodable bytes) without normalizing line endings."""
    path = None
    if isinstance(source, Path) or (
        isinstance(source, str)
        and "\n" not in source
        and "\r" not in source
        and not source.lstrip("\ufeff \t").startswith("<")
    ):
        path = Path(source)
        text = path.read_bytes().decode("utf-8", errors="surrogateescape")
    else:
        text = source
    bom = "\ufeff" if text.startswith("\ufeff") else ""
    chunks = text[len(bom) :].splitlines(keepends=True)
    lines = []
    endings = []
    for chunk in chunks:
        ending = (
            "\r\n"
            if chunk.endswith("\r\n")
            else chunk[-1:]
            if chunk.endswith(("\n", "\r"))
            else ""
        )
        lines.append(chunk[: -len(ending)] if ending else chunk)
        endings.append(ending)
    if not lines or not lines[0].lstrip().startswith("<"):
        raise RPPParseError("not an RPP file (missing <REAPER_PROJECT header)")
    toks = tokenize(lines[0].strip()[1:])
    if not toks or toks[0] != "REAPER_PROJECT":
        raise RPPParseError("missing <REAPER_PROJECT header")
    root = Element(toks[0], toks[1:], raw_open=lines[0], _open_eol=endings[0])
    root._line_no = 1
    stack = [root]
    end = None
    for i in range(1, len(lines)):
        raw = lines[i]
        stripped = raw.strip()
        if stripped == ">":
            node = stack.pop()
            node.raw_close = raw
            node._close_eol = endings[i]
            if not stack:
                end = i + 1
                break
        elif stripped.startswith("<"):
            toks = tokenize(stripped[1:])
            if not toks:
                raise RPPParseError(f"empty chunk opener at line {i + 1}")
            node = Element(toks[0], toks[1:], raw_open=raw, _open_eol=endings[i])
            node._line_no = i + 1
            stack[-1].children.append(node)
            stack.append(node)
        else:
            # NOTES payload is text, not a property grammar.
            toks = [stripped] if stack[-1].tag == "NOTES" else tokenize(stripped)
            stack[-1].children.append(
                Line(toks[0] if toks else "", toks[1:], raw, _eol=endings[i])
            )
    if stack:
        raise RPPParseError(
            f"unclosed chunk <{stack[-1].tag}> (opened at line {stack[-1]._line_no})"
        )
    newline = next((e for e in endings if e), "\n")
    return Document(
        root,
        text,
        _newline=newline,
        _trailing=lines[end:],
        _trailing_newline=bool(endings[-1]),
        source_path=path.resolve() if path else None,
        _bom=bom,
        _tail_raw="".join(chunks[end:]),
    )


def emit(doc: Document) -> str:
    """序列化 Document → 文本。未修改文档保证与原文 byte-exact。"""
    return doc.text()
