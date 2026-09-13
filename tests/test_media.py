import json
import numpy as np
import pytest
import soundfile as sf
from rac.media import read_source, render, MediaError, _resolve
from rac.rpp import parse


def test_source_preserves_channels_and_values(tmp_path):
    samples = np.array([[0.25, -0.5], [0, 0.125]], dtype="float32")
    sf.write(tmp_path / "stereo.wav", samples, 44100, subtype="FLOAT")
    result = read_source("stereo.wav", project=tmp_path / "project.rpp")
    np.testing.assert_array_equal(result.samples, samples)
    assert result.sample_rate == 44100 and result.metadata["channels"] == 2
    assert result.metadata["level"] == "source"


def test_foreign_paths_require_explicit_unambiguous_mapping(tmp_path):
    sf.write(tmp_path / "a.wav", np.zeros((8, 1)), 8000)
    assert (
        _resolve("C:/audio/a.wav", path_map={"C:/audio": tmp_path})
        == tmp_path / "a.wav"
    )
    with pytest.raises(MediaError) as e:
        _resolve("C:/audio/a.wav")
    assert e.value.code == "missing_media"
    with pytest.raises(MediaError) as e:
        _resolve("C:/audio/a.wav", path_map={"C:/audio": tmp_path, "C:": tmp_path})
    assert e.value.code == "ambiguous_media"


def test_source_section_is_not_silently_treated_as_raw(tmp_path):
    doc = parse(
        "<REAPER_PROJECT 0.1 7.48 1\n<TRACK\n<ITEM\n<SOURCE SECTION\n<SOURCE WAVE\nFILE a.wav\n>\n>\n>\n>\n>\n"
    )
    with pytest.raises(MediaError) as e:
        read_source(doc.project.tracks[0].items[0].takes[0])
    assert e.value.code == "unsupported_source"


def test_render_refuses_existing_output_before_host(tmp_path):
    p = tmp_path / "a.rpp"
    p.write_text("<REAPER_PROJECT 0.1 7.48 1\n>\n")
    with pytest.raises(FileExistsError):
        render(p, work_dir=tmp_path)


def test_host_failure_has_separate_manifest_and_keeps_input(tmp_path, monkeypatch):
    import rac.media as media

    p = tmp_path / "a.rpp"
    original = "<REAPER_PROJECT 0.1 7.48 1\n>\n"
    p.write_text(original)

    def fail(*a, **kw):
        raise MediaError("proof_missing", "synthetic failure")

    monkeypatch.setattr(media, "_run", fail)
    with pytest.raises(MediaError) as e:
        render(p, work_dir=tmp_path / "run")
    report = json.loads(e.value.manifest_path.read_text())
    assert report["status"] == "error" and report["checks"]["audio"] is False
    assert report["error"]["code"] == "proof_missing" and p.read_text() == original


def test_missing_media_keeps_diagnostic_manifest(tmp_path):
    p = tmp_path / "input.rpp"
    p.write_text(
        "<REAPER_PROJECT 0.1 7.48 1\n<TRACK\n<ITEM\n<SOURCE WAVE\nFILE absent.wav\n>\n>\n>\n>\n"
    )
    with pytest.raises(MediaError) as caught:
        render(p, work_dir=tmp_path / "run")
    report = json.loads(caught.value.manifest_path.read_text())
    assert report["error"]["code"] == "missing_media"
    assert report["checks"]["host"] is False
