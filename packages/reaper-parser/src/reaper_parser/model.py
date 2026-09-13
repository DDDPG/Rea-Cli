"""Views reference their owning document. Ranges use node identity, never copied trees."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .parser import Document, Element, Line
from . import schema


@dataclass(frozen=True)
class FieldValue:
    token: str
    index: int  # 1-based, matching the specification
    raw: str
    metadata: dict | None
    location: str

    @property
    def semantic_status(self):
        return (
            self.metadata.get("semantic_status", "unknown")
            if self.metadata
            else "unknown"
        )

    @property
    def value(self) -> Any:
        if self.semantic_status == "unknown":
            return self.raw
        kind = (self.metadata.get("type") or "").lower()
        if "float" in kind:
            return float(self.raw)
        if "int" in kind:
            return int(self.raw)
        return self.raw

    @property
    def write_status(self):
        return (
            self.metadata.get("write_status", "unverified")
            if self.metadata
            else "unverified"
        )


def _identity_index(nodes, target):
    for i, node in enumerate(nodes):
        if node is target:
            return i
    raise ValueError("View is detached from its parent document")


class View:
    context = "project"

    def __init__(
        self, document: Document, node: Element, start=None, stop=None, *, ranged=False
    ):
        self.document = document
        self.node = node
        self._start = start
        self._stop = stop
        self._ranged = ranged

    def _bounds(self):
        children = self.node.children
        a = _identity_index(children, self._start) if self._start is not None else 0
        b = (
            _identity_index(children, self._stop)
            if self._stop is not None
            else len(children)
        )
        return a, b

    @property
    def children(self):
        a, b = self._bounds()
        return self.node.children[a:b]

    def _lines(self, key):
        return [c for c in self.children if isinstance(c, Line) and c.key == key]

    def _chunks(self, key):
        return [c for c in self.children if isinstance(c, Element) and c.tag == key]

    def raw(self, key, index=0, default=None):
        rows = self._lines(key)
        return (
            rows[0].values[index] if rows and len(rows[0].values) > index else default
        )

    def _meta(self, key, index):
        return schema.field_meta(self.context, key, index)

    def fields(self):
        """Enumerate every direct field, including unknown values and repeated rows."""
        if not self._ranged:
            for i, value in enumerate(self.node.attrs, 1):
                yield FieldValue(
                    self.node.tag,
                    i,
                    value,
                    self._meta(self.node.tag, i),
                    f"{self.context}/@{self.node.tag}",
                )
        for row, c in enumerate(self.children):
            if isinstance(c, Line):
                for i, value in enumerate(c.values, 1):
                    yield FieldValue(
                        c.key,
                        i,
                        value,
                        self._meta(c.key, i),
                        f"{self.context}/{c.key}/{row}",
                    )

    def set_raw(self, key, index, value):
        """Low-level patch. No semantic validation claim; does not fabricate missing slots."""
        if index < 0:
            raise IndexError(index)
        text = str(value)
        if "\n" in text or "\r" in text:
            raise ValueError("Use a text chunk for multiline values")
        rows = self._lines(key)
        if rows:
            line = rows[0]
            if index > len(line.values):
                raise ValueError("Missing preceding fields; supply a complete raw row")
            if index == len(line.values):
                line.values.append(text)
            elif line.values[index] == text:
                return
            else:
                line.values[index] = text
        else:
            if index != 0:
                raise ValueError("Cannot invent preceding fields")
            # Insert inside the owning range, before FX WAK and before take SOURCE.
            a, b = self._bounds()
            insert = b
            for i in range(a, b):
                c = self.node.children[i]
                if (isinstance(c, Line) and c.key == "WAK") or (
                    isinstance(c, Element) and c.tag == "SOURCE"
                ):
                    insert = i
                    break
            indent = (
                self.node.raw_open[
                    : len(self.node.raw_open) - len(self.node.raw_open.lstrip())
                ]
                + "  "
            )
            line = Line(key, [text], indent + key, dirty=True)
            self.node.children.insert(insert, line)
        line.dirty = True
        self.document.touch()

    def set_field(self, key, index, value):
        """Typed edit: spec field indexes are 1-based; unverified writes are rejected."""
        meta = self._meta(key, index)
        if not meta or meta.get("write_status") != "verified":
            raise ValueError(
                f"No verified write contract for {self.context}/{key}[{index}]"
            )
        err = schema.validate_value(self.context, key, index, str(value))
        if err:
            raise ValueError(err)
        self.set_raw(key, index - 1, value)

    def remove(self):
        """Remove a range from its actual parent; document-scoped root removal is invalid."""
        if not self._ranged:
            raise ValueError("Only a range can be removed using this method")
        a, b = self._bounds()
        del self.node.children[a:b]
        self.document.touch()

    @property
    def envelopes(self):
        return [
            Envelope(self.document, c)
            for c in self.children
            if isinstance(c, Element) and ("ENV" in c.tag or c.tag == "PARMENV")
        ]


class Project(View):
    @property
    def tracks(self):
        return [Track(self.document, n) for n in self._chunks("TRACK")]

    @property
    def tempo(self):
        value = self.raw("TEMPO")
        return float(value) if value is not None else None

    @property
    def master(self):
        return MasterTrack(self.document, self.node)

    @property
    def markers(self):
        return self._lines("MARKER")


class Track(View):
    context = "track"

    @property
    def guid(self):
        return self.node.attrs[0] if self.node.attrs else self.raw("TRACKID")

    @property
    def name(self):
        return self.raw("NAME", 0, "")

    @name.setter
    def name(self, value):
        self.set_raw("NAME", 0, value)

    @property
    def volume(self):
        return float(self.raw("VOLPAN", 0, "1"))

    @volume.setter
    def volume(self, value):
        self.set_raw("VOLPAN", 0, value)

    @property
    def pan(self):
        return float(self.raw("VOLPAN", 1, "0"))

    @pan.setter
    def pan(self, value):
        self.set_raw("VOLPAN", 1, value)

    @property
    def muted(self):
        return self.raw("MUTESOLO", 0, "0") != "0"

    @muted.setter
    def muted(self, value):
        self.set_raw("MUTESOLO", 0, int(value))

    @property
    def items(self):
        return [Item(self.document, n) for n in self._chunks("ITEM")]

    @property
    def fx_chain(self):
        nodes = self._chunks("FXCHAIN")
        return FXChain(self.document, nodes[0]) if nodes else None

    @property
    def receives(self):
        return self._lines("AUXRECV")

    @property
    def hardware_outputs(self):
        return self._lines("HWOUT")


class MasterTrack(View):
    @property
    def fx_chain(self):
        nodes = self._chunks("MASTERFXLIST")
        return FXChain(self.document, nodes[0]) if nodes else None


class Item(View):
    context = "item"

    @property
    def guid(self):
        return self.raw("IGUID")

    @property
    def position(self):
        value = self.raw("POSITION")
        return float(value) if value is not None else None

    @position.setter
    def position(self, value):
        self.set_raw("POSITION", 0, value)

    @property
    def length(self):
        value = self.raw("LENGTH")
        return float(value) if value is not None else None

    @length.setter
    def length(self, value):
        self.set_raw("LENGTH", 0, value)

    @property
    def takes(self):
        markers = [c for c in self.children if isinstance(c, Line) and c.key == "TAKE"]
        # The first take has no delimiter and shares the ITEM prefix. Filter its fields below.
        starts = [None] + markers
        stops = markers + [None]
        return [
            Take(self.document, self.node, a, b, ranged=True, first=i == 0)
            for i, (a, b) in enumerate(zip(starts, stops))
        ]


class Take(View):
    context = "take"

    def __init__(self, *args, first=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.first = first

    def remove(self):
        raise ValueError(
            "Take removal requires a host operation; implicit item fields must be preserved"
        )

    def _meta(self, key, index):
        return schema.field_meta("item" if self.first else "take", key, index)

    def fields(self):
        allowed = {
            "NAME",
            "VOLPAN",
            "SOFFS",
            "PLAYRATE",
            "CHANMODE",
            "GUID",
            "TKM",
            "SM",
            "TMINFO",
            "TM",
        }
        for value in super().fields():
            if not self.first or value.token in allowed:
                yield value

    @property
    def name(self):
        return self.raw("NAME", 0, "")

    @name.setter
    def name(self, value):
        self.set_raw("NAME", 0, value)

    @property
    def guid(self):
        return self.raw("GUID")

    @property
    def selected(self):
        if not self.first:
            return "SEL" in self._start.values
        return not any(
            isinstance(c, Line) and c.key == "TAKE" and "SEL" in c.values
            for c in self.node.children
        )

    @property
    def source(self):
        nodes = self._chunks("SOURCE")
        return source_view(self.document, nodes[0]) if nodes else None

    @property
    def fx_chain(self):
        nodes = self._chunks("TAKEFX")
        return FXChain(self.document, nodes[0]) if nodes else None


class FXChain(View):
    context = "fx"

    def get_fxs(self):
        children = self.children
        starts = [
            i
            for i, c in enumerate(children)
            if isinstance(c, Line) and c.key == "BYPASS"
        ]
        result = []
        for offset, start in enumerate(starts):
            limit = starts[offset + 1] if offset + 1 < len(starts) else len(children)
            end = next(
                (
                    i + 1
                    for i in range(start, limit)
                    if isinstance(children[i], Line) and children[i].key == "WAK"
                ),
                limit,
            )
            result.append(
                FX(
                    self.document,
                    self.node,
                    children[start],
                    children[end] if end < len(children) else None,
                    ranged=True,
                )
            )
        return result

    @property
    def fxs(self):
        return self.get_fxs()


class FX(View):
    context = "fx"

    @property
    def guid(self):
        return self.raw("FXID")

    @property
    def plugin(self):
        return next(
            (
                c
                for c in self.children
                if isinstance(c, Element) and c.tag not in {"PARMENV", "PROGRAMENV"}
            ),
            None,
        )

    @property
    def wet(self):
        return float(self.raw("WET", 0, "1"))

    @wet.setter
    def wet(self, value):
        self.set_raw("WET", 0, value)

    @property
    def bypass_state(self):
        return self.raw("BYPASS", 0, "0") != "0"

    @bypass_state.setter
    def bypass_state(self, value):
        self.set_raw("BYPASS", 0, int(value))


class Envelope(View):
    context = "envelope"

    @property
    def points(self):
        return [
            [
                FieldValue("PT", i, v, self._meta("PT", i), self.node.tag)
                for i, v in enumerate(line.values, 1)
            ]
            for line in self._lines("PT")
        ]


class Source(View):
    context = "source"

    @property
    def type(self):
        return self.node.attrs[0] if self.node.attrs else None

    @property
    def file_path(self):
        return self.raw("FILE")

    @property
    def sources(self):
        return [source_view(self.document, n) for n in self._chunks("SOURCE")]


class MidiSource(Source):
    @property
    def events(self):
        return [
            c
            for c in self.children
            if isinstance(c, Line) and c.key in {"E", "e", "Em", "em"}
        ]

    @property
    def sysex(self):
        return [
            c for c in self.children if isinstance(c, Element) and c.tag in {"X", "x"}
        ]


def source_view(document, node):
    return (MidiSource if node.attrs and node.attrs[0] == "MIDI" else Source)(
        document, node
    )
