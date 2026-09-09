#!/usr/bin/env python3
"""tests/test_extractor.py — extract_reaperdoc 正负例回归 (纯标准库)

用法: python3 tests/test_extractor.py  (从 repo 根目录)
"""
import sys
from pathlib import Path

from rac.knowledge.extract_reaperdoc import TSLiteralParser, extract_const  # noqa: E402

passed = failed = 0


def check(name, fn):
    global passed, failed
    try:
        fn()
        passed += 1
        print(f"✅ {name}")
    except AssertionError as e:
        failed += 1
        print(f"❌ {name}: {e}")


# --- 正例 ---
def t_basic_object():
    v = TSLiteralParser('{ name: "VOLPAN", n: 3, f: 0.5, b: true }').parse_value()
    assert v == {"name": "VOLPAN", "n": 3, "f": 0.5, "b": True}, v


def t_nested_and_comments():
    v = TSLiteralParser(
        '{ // line comment\n a: [1, /* block */ 2, { k: "v" }], }').parse_value()
    assert v == {"a": [1, 2, {"k": "v"}]}, v


def t_trailing_comma():
    v = TSLiteralParser('{ a: 1, b: [2, 3,], }').parse_value()
    assert v == {"a": 1, "b": [2, 3]}, v


def t_strings_with_quotes():
    v = TSLiteralParser('''{ d: "it's ok", s: 'say "hi"', e: "a\\nb" }''').parse_value()
    assert v["d"] == "it's ok" and v["s"] == 'say "hi"' and v["e"] == "a\nb", v


def t_extract_const_anchored():
    text = '// DOC_DATA = [fake]\nconst s = "DOC_DATA = [x]"\nexport const DOC_DATA: T[] = [ {a:1} ];\n'
    v = extract_const(text, "DOC_DATA")
    assert v == [{"a": 1}], v


# --- 负例 (必须报错, 不得静默接受) ---
def _expect_syntax_error(src):
    try:
        TSLiteralParser(src).parse_value()
    except SyntaxError:
        return
    raise AssertionError(f"非法输入被接受: {src!r}")


def t_missing_comma_object():
    _expect_syntax_error('{a:1 b:2}')


def t_missing_comma_array():
    _expect_syntax_error('[1 2]')


def t_unterminated_string():
    _expect_syntax_error('{a: "abc}')


def t_garbage():
    _expect_syntax_error('{a: @}')


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items()
                            if k.startswith("t_")}.items()):
        check(name, fn)
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
