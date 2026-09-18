"""Deterministic source → render → NumPy gain → new track → selected render.

Run with reacli[audio] installed and REAPER/Lua configured:
python examples/data_roundtrip.py /absolute/new-directory
"""

import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import soundfile as sf
from rac.media import read_source, render, import_audio
from rac.rpp import parse
from rac.rpp.parser import quote_value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--reaper-bin")
    args = parser.parse_args()
    root = args.output.resolve()
    root.mkdir(parents=True, exist_ok=False)
    sr = 48000
    t = np.arange(sr, dtype=np.float64) / sr
    signal = np.stack(
        [0.25 * np.sin(2 * np.pi * 440 * t), 0.125 * np.sin(2 * np.pi * 660 * t)],
        axis=1,
    ).astype("float32")
    source = root / "source.wav"
    sf.write(source, signal, sr, subtype="FLOAT")
    project = root / "input.rpp"
    project.write_text(
        "<REAPER_PROJECT 0.1 7.48 1\n  SAMPLERATE 48000 1 0\n  <TRACK {10000000-0000-0000-0000-000000000001}\n    NAME Source\n    VOLPAN 1 0 1 -1 1\n    <ITEM\n      POSITION 0\n      LENGTH 1\n      IGUID {10000000-0000-0000-0000-000000000002}\n      GUID {10000000-0000-0000-0000-000000000003}\n      VOLPAN 1 0 1 -1\n      <SOURCE WAVE\n        FILE "
        + quote_value(str(source))
        + "\n      >\n    >\n  >\n>\n"
    )
    before = hashlib.sha256(project.read_bytes()).hexdigest()
    raw = read_source(parse(project).project.tracks[0].items[0].takes[0])
    np.testing.assert_array_equal(raw.samples, signal)
    first = render(
        project,
        work_dir=root / "render",
        sample_rate=sr,
        channels=2,
        time_range=(0, 1),
        reaper_bin=args.reaper_bin,
    )
    rendered = read_source(first)
    assert (
        rendered.metadata["level"] == "rendered" and raw.metadata["level"] == "source"
    )
    assert (
        rendered.samples.shape == signal.shape
        and np.max(np.abs(rendered.samples)) > 0.1
    )
    processed = rendered.samples * np.float32(0.5)
    output = root / "processed.wav"
    sf.write(output, processed, sr, subtype="FLOAT")
    np.testing.assert_array_equal(read_source(output).samples, processed)
    imported = import_audio(
        project,
        output,
        work_dir=root / "import",
        name="NumPy gain 0.5",
        reaper_bin=args.reaper_bin,
    )
    final = render(
        imported.path,
        work_dir=root / "verify-render",
        sample_rate=sr,
        channels=2,
        time_range=(0, 1),
        track_guids=[imported.metadata["track_guid"]],
        reaper_bin=args.reaper_bin,
    )
    actual = read_source(final).samples
    np.testing.assert_allclose(actual, processed, atol=2 / 32768, rtol=0)
    assert hashlib.sha256(project.read_bytes()).hexdigest() == before
    report = {
        "ok": True,
        "source": raw.metadata,
        "rendered": rendered.metadata,
        "gain": 0.5,
        "output_project": str(imported.path),
        "proof_manifests": [
            str(first.manifest_path),
            str(imported.manifest_path),
            str(final.manifest_path),
        ],
        "checks": {
            "original_unchanged": True,
            "source_exact": True,
            "numpy_gain_exact": True,
            "rendered_gain_tolerance": 2 / 32768,
        },
        "host": first.proof.result["host"],
    }
    (root / "roundtrip.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
