"""Fluent assertions for REAPER project structure.

Use ``expect(document)`` to check track names, levels, items and markers.
"""
from __future__ import annotations

from rac.rpp import Document
from rac.rpp.parser import Element, Line


class ExpectError(AssertionError):
    pass


def _approx(a: float, b: float, tol: float) -> bool:
    return abs(a - b) <= tol


class TrackExpect:
    def __init__(self, el: Element, ctx: str):
        self.el = el
        self.ctx = ctx

    def _line(self, key: str) -> Line:
        line = self.el.find_line(key)
        if line is None:
            raise ExpectError(f"{self.ctx}: missing line {key}")
        return line

    def name(self, expected: str) -> "TrackExpect":
        line = self._line("NAME")
        actual = line.values[0] if line.values else ""
        if actual != expected:
            raise ExpectError(f"{self.ctx}.NAME: expect {expected!r}, got {actual!r}")
        return self

    def volume(self, linear: float, tol: float = 1e-6) -> "TrackExpect":
        actual = float(self._line("VOLPAN").values[0])
        if not _approx(actual, linear, tol):
            raise ExpectError(f"{self.ctx}.VOLPAN[1]: expect {linear}, got {actual}")
        return self

    def volume_db(self, db: float, tol: float = 0.01) -> "TrackExpect":
        """dB 域断言 (tol 单位 dB, 不是 linear)。"""
        import math
        actual = float(self._line("VOLPAN").values[0])
        actual_db = 20 * math.log10(max(actual, 1e-10))
        if abs(actual_db - db) > tol:
            raise ExpectError(
                f"{self.ctx}.VOLPAN[1]: expect {db}dB±{tol}, got {actual_db:.2f}dB")
        return self

    def pan(self, pan: float, tol: float = 1e-6) -> "TrackExpect":
        actual = float(self._line("VOLPAN").values[1])
        if not _approx(actual, pan, tol):
            raise ExpectError(f"{self.ctx}.VOLPAN[2]: expect {pan}, got {actual}")
        return self

    def item_count(self, n: int) -> "TrackExpect":
        actual = len(self.el.find_chunks("ITEM"))
        if actual != n:
            raise ExpectError(f"{self.ctx}: expect {n} items, got {actual}")
        return self


class Expect:
    def __init__(self, doc: Document):
        self.doc = doc

    def track_count(self, n: int) -> "Expect":
        actual = len(self.doc.tracks())
        if actual != n:
            raise ExpectError(f"track_count: expect {n}, got {actual}")
        return self

    def track(self, idx: int) -> TrackExpect:
        tracks = self.doc.tracks()
        if idx >= len(tracks):
            raise ExpectError(f"track[{idx}] not exist (only {len(tracks)} tracks)")
        return TrackExpect(tracks[idx], f"track[{idx}]")

    def has_marker(self, name: str | None = None, pos: float | None = None,
                   tol: float = 1e-6) -> "Expect":
        for m in self.doc.markers():
            if name is not None and (len(m.values) < 3 or m.values[2] != name):
                continue
            if pos is not None and not _approx(float(m.values[1]), pos, tol):
                continue
            return self
        raise ExpectError(f"marker not found: name={name!r} pos={pos}")

    def marker_count(self, n: int) -> "Expect":
        actual = len(self.doc.markers())
        if actual != n:
            raise ExpectError(f"marker_count: expect {n}, got {actual}")
        return self

    def line_value(self, section_chunk: Element | None, key: str, index: int,
                   expected: str) -> "Expect":
        if section_chunk is None:
            raise ExpectError("section_chunk is None")
        line = section_chunk.find_line(key)
        if line is None or len(line.values) <= index - 1:
            raise ExpectError(f"{key}[{index}] not found")
        if line.values[index - 1] != expected:
            raise ExpectError(
                f"{key}[{index}]: expect {expected!r}, got {line.values[index-1]!r}")
        return self


def expect(doc: Document) -> Expect:
    return Expect(doc)
