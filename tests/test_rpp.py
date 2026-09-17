#!/usr/bin/env python3
"""tests/test_rpp.py — rac.rpp 回归套件 (纯标准库, 从 repo 根目录运行)

覆盖: round-trip byte-exact / oracle 交叉 / patch 幂等与最小 diff /
      单双引号 / schema 访问器
"""
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).parent.parent


from rac.rpp import parse, emit  # noqa: E402
from rac.rpp import patch, schema  # noqa: E402
from rac.rpp.oracle import oracle_diff  # noqa: E402

FIXTURES = ["minimal", "minimal_after_reaper_save", "missing_media", "caption_demo"]

passed = failed = 0


def check(name, fn):
    global passed, failed
    try:
        fn()
        passed += 1
        print(f"✅ {name}")
    except Exception as e:
        failed += 1
        print(f"❌ {name}: {type(e).__name__}: {e}")


def t_roundtrip():
    for name in FIXTURES:
        p = ROOT / "tests" / "fixtures" / f"{name}.rpp"
        # Compare bytes; read_text would normalize CRLF and hide differences.
        assert emit(parse(p)).encode("utf-8") == p.read_bytes(), f"{name} not byte-exact"


def t_crlf_preserved_when_dirty():
    # Editing a CRLF project must preserve its line endings.
    p = ROOT / "tests" / "fixtures" / "minimal_after_reaper_save.rpp"
    assert p.read_bytes().count(b"\r\n") > 100, "fixture 应为 CRLF"
    doc = parse(p)
    patch.set_track_volume(doc, doc.tracks()[0], 0.25)
    out = emit(doc).encode("utf-8")
    assert out.count(b"\r\n") > 100, f"CRLF 丢失: {out.count(bytes([13,10]))}"
    assert b"\n" not in out.replace(b"\r\n", b""), "混入裸 LF"
    # 语义重解析
    doc2 = parse(out.decode("utf-8"))
    assert doc2.tracks()[0].find_line("VOLPAN").values[0] == "0.25"


def t_unclosed_chunk_raises():
    from rac.rpp.parser import RPPParseError
    try:
        parse('<REAPER_PROJECT 0.1 "7.0" 0\n  <TRACK\n    NAME x\n')
    except RPPParseError as e:
        assert "unclosed" in str(e) and "TRACK" in str(e) and "line 2" in str(e), e
    else:
        raise AssertionError("未闭合 chunk 未报错")


def test_parser_safety_limits(monkeypatch):
    import reaper_parser.parser as parser

    monkeypatch.setattr(parser, "MAX_RPP_BYTES", 5)
    with pytest.raises(parser.RPPParseError, match="byte safety limit"):
        parse("<éé>")

    monkeypatch.setattr(parser, "MAX_RPP_BYTES", 64 * 1024 * 1024)
    monkeypatch.setattr(parser, "MAX_RPP_LINES", 1)
    with pytest.raises(parser.RPPParseError, match="line safety limit"):
        parse("<ROOT\r\n>\r\n")

    monkeypatch.setattr(parser, "MAX_RPP_LINES", 1_000_000)
    monkeypatch.setattr(parser, "MAX_RPP_NESTING", 1)
    with pytest.raises(parser.RPPParseError, match="level safety limit"):
        parse("<REAPER_PROJECT 0.1 7.0 0\n<CHILD\n>\n>\n")


def test_semantic_diff_safety_limit(monkeypatch):
    from rac.verify import semantics

    doc = parse(ROOT / "tests" / "fixtures" / "minimal.rpp")
    monkeypatch.setattr(semantics, "MAX_SEMANTIC_DIFF_NODES", 0)
    with pytest.raises(ValueError, match="node safety limit"):
        semantics.semantic_diff(doc, doc)


def t_typed_validation():
    from rac.rpp.schema import validate_value, enum_check
    # 类型拒绝 (阻断)
    assert validate_value("track", "VOLPAN", 1, "0.5") is None
    assert validate_value("track", "VOLPAN", 1, "abc") is not None
    assert validate_value("project", "MARKER", 1, "1") is None
    assert validate_value("project", "MARKER", 1, "1.5") is not None
    # Accept common floating-point spellings: .5 / 1. / +1.
    assert validate_value("track", "VOLPAN", 1, ".5") is None
    assert validate_value("track", "VOLPAN", 1, "1.") is None
    assert validate_value("track", "VOLPAN", 1, "+1") is None
    # Extracted enum descriptions are not an exhaustive validation contract.
    assert validate_value("track", "BEAT", 1, "0") is None   # ReaperDoc 只记了 -1
    assert validate_value("track", "PANMODE", 1, "0") is None  # 文档缺 0
    # enum_check 警告通道: RECMODE 完整集内无警告, 越集有警告不阻断
    assert enum_check("project", "RECMODE", 1, "1") is None
    assert enum_check("project", "RECMODE", 1, "7") is not None
    assert "warning" in enum_check("project", "RECMODE", 1, "7")
    # 位标志形式不检查
    assert enum_check("project", "AUTOXFADE", 1, "999999") is None
    # patch 层联动: 类型非法 raise; 枚举偏差不 raise
    doc = parse(ROOT / "tests" / "fixtures" / "minimal_after_reaper_save.rpp")
    try:
        patch.set_value(doc, doc.tracks()[0].find_line("VOLPAN"), 0, "xyz",
                        section="track")
    except ValueError as e:
        assert "float" in str(e), e
    else:
        raise AssertionError("非法 float 未被拦截")
    patch.set_value(doc, doc.tracks()[0].find_line("VOLPAN"), 1, "0",
                    section="track")  # 文档有 0, 无警告
    assert enum_check("track", "VOLPAN", 2, "0") is None


def t_raw_close_kept_when_only_children_dirty():
    # Preserve the parent closing line when only a child is dirty.
    text = '<REAPER_PROJECT 0.1 "7.0" 0\n  <TRACK {A}\n    NAME x\n  >   \n>\n'
    doc = parse(text)
    track = doc.tracks()[0]
    patch.set_track_name(doc, track, "y")
    out = emit(doc)
    assert "  >   \n" in out, f"raw_close 尾部空白丢失:\n{out!r}"


def t_oracle():
    from rac.rpp.oracle import PERLENCE_AVAILABLE
    if not PERLENCE_AVAILABLE:
        __import__("pytest").skip("install reacli[oracle] for independent parser check")
    for name in FIXTURES:
        diffs = oracle_diff(ROOT / "tests" / "fixtures" / f"{name}.rpp")
        assert not diffs, f"{name}: {diffs[:3]}"


def t_patch_idempotent_and_minimal_diff():
    import difflib
    p = ROOT / "tests" / "fixtures" / "minimal_after_reaper_save.rpp"
    orig = p.read_text(encoding="utf-8")
    doc = parse(p)
    tr = doc.tracks()[0]
    patch.set_track_volume(doc, tr, 0.25)
    patch.set_marker(doc, 9, 99.0, "x")
    out1 = emit(doc)
    patch.set_track_volume(doc, tr, 0.25)
    patch.set_marker(doc, 9, 99.0, "x")
    assert emit(doc) == out1, "patch 不幂等"
    diff = [l for l in difflib.unified_diff(orig.splitlines(), out1.splitlines())
            if l[0] in "+-" and not l.startswith(("+++", "---"))]
    assert not any("REAPER_PROJECT" in l for l in diff), f"根行被改: {diff}"
    assert any("VOLPAN" in l for l in diff), f"VOLPAN 未改: {diff}"
    # 重解析验证语义
    doc2 = parse(out1)
    assert doc2.tracks()[0].find_line("VOLPAN").values[0] == "0.25"


def t_quotes():
    doc = parse(ROOT / "tests" / "fixtures" / "minimal_after_reaper_save.rpp")
    patch.set_track_name(doc, doc.tracks()[0], "my vocal track")
    out = emit(doc)
    assert '"my vocal track"' in out
    assert parse(out).tracks()[0].find_line("NAME").values[0] == "my vocal track"


def t_single_quote_ext():
    doc = parse(ROOT / "tests" / "fixtures" / "caption_demo.rpp")
    found = False
    for ext in doc.root.iter_chunks("EXT"):
        for line in ext.find_lines("omnicap"):
            assert line.values[0].startswith('{"sidecar":'), line.values[0][:40]
            found = True
    assert found, "omnicap EXT line not found"


def t_schema():
    assert schema.field_description("track", "VOLPAN", 1) == "volume trim"
    assert schema.key_meta("item", "VOLPAN")["section"] == "item"
    assert schema.key_meta("track", "NONEXISTENT") is None


def t_unknown_preserved():
    p = ROOT / "tests" / "fixtures" / "minimal.rpp"
    text = p.read_text(encoding="utf-8").replace("  TEMPO 120 4 4 0",
                                                 "  TEMPO 120 4 4 0\n  XUNKNOWNKEY 1 2 3")
    doc = parse(text)
    out = emit(doc)
    assert "XUNKNOWNKEY 1 2 3" in out, "未知 KEY 丢失"


def t_single_quote_value_write():
    # Values containing single quotes still need valid double-quoted serialization.
    doc = parse(ROOT / "tests" / "fixtures" / "minimal_after_reaper_save.rpp")
    patch.set_track_name(doc, doc.tracks()[0], "it's mine")
    out = emit(doc)
    doc2 = parse(out)
    assert doc2.tracks()[0].find_line("NAME").values[0] == "it's mine"


def t_trailing_content_preserved():
    text = '<REAPER_PROJECT 0.1 "7.0" 0\n  TEMPO 120 4 4 0\n>\nTAIL_DATA_HERE\n'
    doc = parse(text)
    doc.touch()
    out = emit(doc)
    assert "TAIL_DATA_HERE" in out, "根块尾部内容丢失"


def t_blank_lines_preserved():
    # cursor M2: 空行必须进树保真
    text = '<REAPER_PROJECT 0.1 "7.0" 0\n  TEMPO 120 4 4 0\n\n  <TRACK {A}\n\n    NAME x\n  >\n>\n'
    doc = parse(text)
    doc.touch()
    out = emit(doc)
    assert out == text, f"空行丢失或被改:\n{out!r}"


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items()
                            if k.startswith("t_")}.items()):
        check(name, fn)
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
