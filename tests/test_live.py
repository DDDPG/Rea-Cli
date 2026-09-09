import os
import sys
import json
from pathlib import Path

import pytest

pytestmark = [pytest.mark.live, pytest.mark.skipif(
    os.environ.get("RAC_TEST_LIVE") != "1" or not (sys.platform.startswith("linux") or sys.platform == "darwin"),
    reason="Linux/macOS live tests opt in with RAC_TEST_LIVE=1")]


def test_live_lua_save_and_render(tmp_path):
    from rac.smoke import smoke_check
    report = smoke_check(render=True, work_dir=tmp_path, timeout=60,
                         seed_resource=tmp_path / "new-resource")
    assert report["status"] == "ok", report


def _add_runtime_probe(script, extra=""):
    from rac.luagen import validate
    probe = ('RUN.result = RUN.result or {}\n'
             'RUN.result.runtime = {resource_path=reaper.GetResourcePath(), version=reaper.GetAppVersion()}\n')
    script.write_text(script.read_text().replace("local state = collect_state()",
                      probe + extra + "\nlocal state = collect_state()", 1))
    validate(script)


def test_live_pool_isolated_resources(tmp_path, monkeypatch):
    from rac.luagen import generate
    from rac.resources import read_text
    from rac.rpp import parse
    from rac.runner.pool import Pool
    from rac.verify import expect
    monkeypatch.setenv("RAC_REAPER_RESOURCE", str(tmp_path / "wrong-shared-resource"))
    jobs = []
    for i in range(2):
        project = tmp_path / f"input{i}.rpp"
        project.write_text(read_text("examples/minimal.rpp"))
        script = generate({"ops": [{"op": "track.create", "args": [0, f"worker{i}"]}]}, tmp_path / f"edit{i}.lua")
        _add_runtime_probe(script)
        jobs.append({"project": project, "script": script, "save_as": tmp_path / f"out{i}.rpp"})
    proofs = Pool(tmp_path / "workers", 2).map(jobs, timeout=60, run_root=tmp_path / "runs")
    assert all(p.ok for p in proofs), [p.to_dict() for p in proofs]
    assert all(not p.teardown_killed for p in proofs)
    assert proofs[0].run_dir != proofs[1].run_dir
    actual_resources = {Path(p.result["runtime"]["resource_path"]).resolve() for p in proofs}
    expected_resources = set()
    for i, job in enumerate(jobs):
        expect(parse(job["save_as"])).track_count(1).track(0).name(f"worker{i}")
        resource = tmp_path / f"workers/w{i}"
        if sys.platform.startswith("linux"):
            resource /= "resource"
        assert (resource / "reaper.ini").is_file()
        expected_resources.add(resource.resolve())
    assert actual_resources == expected_resources
    assert not (tmp_path / "wrong-shared-resource").exists()
    (tmp_path / "proofs.json").write_text(json.dumps([p.to_dict() for p in proofs], indent=2))


def test_live_unicode_relative_media_native_fx_midi_and_color(tmp_path):
    import shutil
    from rac.luagen import generate
    from rac.rpp import parse
    from rac.runner import run
    from rac.verify import expect
    root = tmp_path / "中文 project with spaces"
    media = root / "媒体 assets"
    media.mkdir(parents=True)
    shutil.copy(Path(__file__).parent / "fixtures/sine440_1s.wav", media / "音频.wav")
    project = root / "输入 project.rpp"
    project.write_text('<REAPER_PROJECT 0.1 "7.0" 1\n  <TRACK\n    NAME "source"\n'
                       '    <ITEM\n      POSITION 0\n      LENGTH 1\n'
                       '      <SOURCE WAVE\n        FILE "媒体 assets/音频.wav"\n'
                       '      >\n    >\n  >\n>\n', encoding="utf-8")
    original = project.read_bytes()
    script = generate({"ops": [
        {"op": "track.set_name", "args": [0, "音频轨"]},
        {"op": "track.set_color", "args": [0, 31, 127, 223]},
        {"op": "fx.add_by_name", "args": [0, "VST: ReaEQ (Cockos)"]},
        {"op": "track.create", "args": [1, "MIDI 轨"]},
        {"op": "midi.create_item", "args": [1, 0, 1]},
        {"op": "midi.insert_note", "args": [1, 0, 60, 96, 0, 0.5]},
        {"op": "routing.create_send", "args": [0, 1]},
        {"op": "marker.add", "args": [7, 0.5, "标记"]},
    ]}, root / "编辑 script.lua")
    _add_runtime_probe(script, '''
local tr = reaper.GetTrack(0, 0)
local take = reaper.GetActiveTake(reaper.GetTrackMediaItem(tr, 0))
local source = reaper.GetMediaItemTake_Source(take)
local seconds = reaper.GetMediaSourceLength(source)
local _, fx_name = reaper.TrackFX_GetFXName(tr, 0, "")
local r,g,b = reaper.ColorFromNative(math.floor(reaper.GetMediaTrackInfo_Value(tr,"I_CUSTOMCOLOR")))
local midi_take = reaper.GetActiveTake(reaper.GetTrackMediaItem(reaper.GetTrack(0,1),0))
local _, notes = reaper.MIDI_CountEvts(midi_take)
RUN.result.media_seconds = seconds
RUN.result.fx_name = fx_name
RUN.result.color = {r,g,b}
RUN.result.midi_notes = notes
RUN.result.sends = reaper.GetTrackNumSends(tr, 0)
''')
    saved = root / "输出 project.rpp"
    proof = run(project, script, save_as=saved, timeout=45,
                resource=root / "独立 resource", run_root=root / "runs")
    (root / "result.json").write_text(json.dumps(proof.to_dict(), indent=2))
    # MIDI edits mark the project dirty. The runner's documented bounded
    # teardown may close a save-confirmation dialog after the verified save-copy.
    assert proof.ok, proof.to_dict()
    assert proof.result["media_seconds"] == pytest.approx(1, abs=0.001)
    assert "ReaEQ" in proof.result["fx_name"]
    assert proof.result["color"] == [31, 127, 223]
    assert proof.result["midi_notes"] == 1
    assert proof.result["sends"] == 1
    assert Path(proof.result["runtime"]["resource_path"]).resolve() == (root / "独立 resource").resolve()
    expect(parse(saved)).track_count(2).track(0).name("音频轨").item_count(1)
    assert project.read_bytes() == original
