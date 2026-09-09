#!/usr/bin/env python3
"""tests/test_verify.py — P5 verify 层回归 (结构/音频/协议/停滞)

venv python 运行; live 音频断言用自合成 wav。
"""
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).parent.parent


from rac.rpp import parse  # noqa: E402
from rac.rpp import patch  # noqa: E402
from rac.verify import expect, expect_audio, proof_check, is_noop_sequence  # noqa: E402
from rac.verify.expect import ExpectError  # noqa: E402
from rac.verify.audio import AudioExpectError  # noqa: E402

passed = failed = skipped = 0


from unittest import SkipTest


def check(name, fn):
    global passed, failed, skipped
    try:
        fn()
        passed += 1
        print(f"✅ {name}")
    except SkipTest as e:
        skipped += 1
        print(f"⏭️  {name} (skip: {e})")
    except Exception as e:
        failed += 1
        print(f"❌ {name}: {type(e).__name__}: {e}")


FIX = ROOT / "tests" / "fixtures"


def t_expect_structure():
    doc = parse(FIX / "minimal_after_reaper_save.rpp")
    expect(doc).track_count(1).track(0).name("smoke_vox")
    expect(doc).track(0).volume_db(-6.0, tol=0.02)
    expect(doc).has_marker(name="冒烟marker", pos=30.0)
    expect(doc).marker_count(1)


def t_expect_negative():
    doc = parse(FIX / "minimal_after_reaper_save.rpp")
    try:
        expect(doc).track_count(5)
    except ExpectError:
        pass
    else:
        raise AssertionError("负例未拦截")
    try:
        expect(doc).has_marker(name="不存在")
    except ExpectError:
        pass
    else:
        raise AssertionError("marker 负例未拦截")


def t_audio():
    expect_audio(FIX / "sine440_1s.wav").duration(1.0, tol=0.01) \
        .not_silent().dominant_freq(440, tol=5).no_clipping()


def t_audio_negative():
    # 静音文件
    import struct
    import tempfile
    sr = 8000
    silence = b"\x00\x00" * sr
    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        f.write(b"RIFF" + struct.pack("<I", 36 + len(silence)) + b"WAVE")
        f.write(b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, sr, sr * 2, 2, 16))
        f.write(b"data" + struct.pack("<I", len(silence)) + silence)
        f.flush()
        try:
            expect_audio(f.name).not_silent()
        except AudioExpectError:
            pass
        else:
            raise AssertionError("静音未拦截")


def t_proof_check():
    good = {"status": "ok", "reason_code": "completed", "duration_ms": 1,
            "log": [{"t_ms": 0, "level": "info", "msg": "x"},
                    {"t_ms": 5, "level": "info", "msg": "y"}],
            "state": {}, "state_hash": "40e58b9c", "result": None,
            "save": None, "error": None}
    proof_check(good)
    bad = dict(good, status="ok", reason_code="lua_error")
    try:
        proof_check(bad)
    except Exception:
        pass
    else:
        raise AssertionError("status/reason 不一致未拦截")
    bad2 = dict(good, log=[{"t_ms": 5, "level": "i", "msg": "a"},
                           {"t_ms": 1, "level": "i", "msg": "b"}])
    try:
        proof_check(bad2)
    except Exception as e:
        assert "monotonic" in str(e)
    else:
        raise AssertionError("非单调 log 未拦截")


def t_stagnation():
    class P:
        def __init__(self, h):
            self.state_hash = h
            self.ok = True
            self.state = {}
    assert not is_noop_sequence([P("a"), P("a")])         # 不足 window
    assert is_noop_sequence([P("a"), P("a"), P("a")])     # 连续 3 同
    assert not is_noop_sequence([P("a"), P("a"), P("b")])  # 有变化


def t_audio_harmonic():
    # A strong harmonic must not hide the louder 440 Hz fundamental.
    expect_audio(FIX / "harmonic_440_880.wav").dominant_freq(440, tol=5)


def t_audio_lufs():
    # Synthetic reference fixtures anchor the approximate loudness checks.
    expect_audio(FIX / "noise_peak01_2s.wav").lufs(-30.9, tol=1.5)
    expect_audio(FIX / "sine440_1s.wav").lufs(-9.8, tol=1.0)
    try:
        expect_audio(FIX / "noise_peak01_2s.wav").lufs(-20.0, tol=0.5)
    except AudioExpectError:
        pass
    else:
        raise AssertionError("LUFS 负例未拦截")


@pytest.mark.live
def t_dual_path_consistency():
    import tempfile
    with tempfile.TemporaryDirectory(prefix="reacli_dual_") as directory:
        _dual_path_consistency(Path(directory))


def _dual_path_consistency(tmp_path):
    """Compare equivalent Lua and RPP edits to levels, names and markers."""
    import os
    if os.environ.get("RAC_TEST_LIVE") != "1":
        raise SkipTest("live tests opt in with RAC_TEST_LIVE=1")
    from rac.runner.platform import find_reaper
    reaper_bin = find_reaper()
    from rac.runner import run
    from rac.luagen import generate

    TARGET_VOL = 0.25
    TARGET_NAME = "dual_path_vox"
    intent = {"ops": [{"op": "track.create", "args": [0, TARGET_NAME]},
                      {"op": "track.set_volume_db", "args": [0, -12.04]},
                      {"op": "track.set_name", "args": [0, TARGET_NAME]},
                      {"op": "marker.add", "args": [3, 12.5, "dual_marker"]}]}
    script = generate(intent, tmp_path / "dual.lua")
    out_a = tmp_path / "out.rpp"
    project = tmp_path / "input.rpp"
    project.write_bytes((FIX / "minimal.rpp").read_bytes())
    pa = run(project, script, timeout=45, reaper_bin=reaper_bin,
             save_as=out_a,
             run_root=tmp_path / "runs", state_dir=tmp_path / ".state",
             resource=tmp_path / "resource")
    assert pa.ok, pa.reason_code
    doc_a = parse(out_a)
    expect(doc_a).track(0).volume(TARGET_VOL, tol=0.01)
    expect(doc_a).track(0).name(TARGET_NAME)
    expect(doc_a).has_marker(name="dual_marker", pos=12.5)

    doc_b = parse(FIX / "minimal_after_reaper_save.rpp")
    tr = doc_b.tracks()[0]
    patch.set_track_volume(doc_b, tr, TARGET_VOL)
    patch.set_track_name(doc_b, tr, TARGET_NAME)
    patch.set_marker(doc_b, 3, 12.5, "dual_marker")
    expect(doc_b).track(0).volume(TARGET_VOL)
    expect(doc_b).track(0).name(TARGET_NAME)
    expect(doc_b).has_marker(name="dual_marker", pos=12.5)

    va = float(doc_a.tracks()[0].find_line("VOLPAN").values[0])
    vb = float(doc_b.tracks()[0].find_line("VOLPAN").values[0])
    assert abs(va - vb) < 0.01, f"volume 不一致: A={va} B={vb}"
    ma = [m for m in doc_a.markers() if m.values[2] == "dual_marker"][0]
    mb = [m for m in doc_b.markers() if m.values[2] == "dual_marker"][0]
    assert abs(float(ma.values[1]) - 12.5) < 1e-6
    assert abs(float(mb.values[1]) - 12.5) < 1e-6

    # Round trips compare equal; changed fields must remain visible.
    # 默认补全被容忍 (RENDER_CFG/METRONOME 等不进差异)
    from rac.verify.semantics import semantic_diff
    assert semantic_diff(doc_b, parse(doc_b.text())) == []
    assert semantic_diff(doc_a, parse(out_a)) == []
    doc_b2 = parse(doc_b.text())
    patch.set_track_volume(doc_b2, doc_b2.tracks()[0], 0.9)
    assert any("VOLPAN" in d for d in semantic_diff(doc_b, doc_b2))
    d = semantic_diff(parse(FIX / "minimal.rpp"),
                      parse(FIX / "minimal_after_reaper_save.rpp"))
    assert all("RENDER_CFG" not in x and "METRONOME" not in x for x in d), d[:5]
    assert any(m.values[0] == "3" for m in doc_a.markers())
    assert any(m.values[0] == "3" for m in doc_b.markers())


def t_semantic_diff_10_cases():
    """Semantic comparisons must distinguish intended changes from defaults."""
    from rac.verify.semantics import semantic_diff
    base = parse(FIX / "minimal_after_reaper_save.rpp")

    # 正例1: 自比空
    assert semantic_diff(base, parse(base.text())) == []
    # 正例2: 浮点容差 (0.501187 vs 0.5011870)
    d2 = parse(base.text())
    line = d2.tracks()[0].find_line("VOLPAN")
    line.values[0] = "0.5011870"
    line.dirty = True
    d2.touch()
    assert semantic_diff(base, d2) == []
    # 正例3: 默认补全容忍 (minimal vs 补全版, RENDER_CFG/METRONOME 不报)
    d3 = semantic_diff(parse(FIX / "minimal.rpp"), base)
    assert all("RENDER_CFG" not in x and "METRONOME" not in x for x in d3)
    # 负例1: 音量改
    n1 = parse(base.text())
    patch.set_track_volume(n1, n1.tracks()[0], 0.9)
    assert any("VOLPAN" in d for d in semantic_diff(base, n1))
    # 负例2: marker 名改
    n2 = parse(base.text())
    m = n2.markers()[0]
    m.values[2] = "renamed"
    m.dirty = True
    n2.touch()
    assert any("MARKER" in d for d in semantic_diff(base, n2))
    # 负例3: 加轨
    n3 = parse(base.text())
    from rac.rpp.parser import Element as _El
    newtr = _El(tag="TRACK", attrs=["{NEWGUID-0000-0000-0000-000000000000}"],
                raw_open="  <TRACK {NEWGUID-0000-0000-0000-000000000000}", dirty=True)
    newtr.raw_close = "  >"
    n3.root.children.append(newtr)
    n3.touch()
    assert any("chunk" in d for d in semantic_diff(base, n3))
    # 负例4: marker 位置改 (超出容差)
    n4 = parse(base.text())
    m4 = n4.markers()[0]
    m4.values[1] = "31.5"
    m4.dirty = True
    n4.touch()
    assert any("MARKER" in d for d in semantic_diff(base, n4))
    # 负例5: tempo 改
    n5 = parse(base.text())
    t5 = n5.root.find_line("TEMPO")
    t5.values[0] = "128"
    t5.dirty = True
    n5.touch()
    assert any("TEMPO" in d for d in semantic_diff(base, n5))
    # 正例4: 换行格式差异 (CRLF vs LF 同一内容)
    text_lf = base.text().replace("\r\n", "\n")
    assert semantic_diff(base, parse(text_lf)) == []
    # 负例6: blob 行改 (base64 精确比对; 硬守卫: 替换必须命中)
    n6_text = base.text().replace("ZXZhdxgAAQ==", "ZXZhdxgAAQ==X", 1)
    assert "ZXZhdxgAAQ==X" in n6_text, "替换未命中 (fixture 漂移?)"
    assert semantic_diff(base, parse(n6_text)) != []
    # Deleting opaque data must remain visible when defaults are tolerated.
    n7_text = "\n".join(l for l in base.text().splitlines()
                        if "ZXZhdxgAAQ==" not in l)
    assert "ZXZhdxgAAQ==" not in n7_text
    assert semantic_diff(base, parse(n7_text)) != [], "删除 blob 行被默认容忍吞掉"
    # Root attribute changes must remain visible.
    n8_text = base.text().replace('"7.62/macOS-arm64"', '"7.99/macOS-arm64"', 1)
    assert '"7.99/macOS-arm64"' in n8_text
    assert any("root attrs" in d for d in semantic_diff(base, parse(n8_text)))
    # GUID normalization can be disabled for strict identity comparisons.
    import re as _re
    n9_text = _re.sub(r"\{[0-9A-Fa-f-]+\}", "{AAAAAAAA-0000-0000-0000-000000000001}",
                      base.text(), count=1)
    assert semantic_diff(base, parse(n9_text)) == [], "GUID 归一应容忍"
    assert semantic_diff(base, parse(n9_text), strict_guid=True) != [], \
        "strict_guid 应捕获 GUID 变更"


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items()
                            if k.startswith("t_")}.items()):
        check(name, fn)
    print(f"\n{passed} passed, {failed} failed, {skipped} skipped")
    sys.exit(1 if failed else 0)
