"""Opt-in REAPER integration checks, always using fresh projects and resources."""
from __future__ import annotations

import math
import shutil
import struct
import tempfile
import wave
from pathlib import Path


def smoke_check(*, reaper_bin=None, seed_resource=None, render=False,
                timeout=60, work_dir=None) -> dict:
    """Generate Lua, execute it, verify saved RPP, optionally render a sine wave."""
    from rac.environment import run_bounded, resolve_executable
    from rac.luagen import generate
    from rac.resources import read_text
    from rac.rpp import parse
    from rac.rpp.parser import quote_value
    from rac.runner import run, platform
    from rac.verify import expect, expect_audio

    temporary = None
    retained = None
    try:
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("timeout must be positive and finite")
        if work_dir:
            Path(work_dir).mkdir(parents=True, exist_ok=True)
            root = Path(tempfile.mkdtemp(prefix="reacli_smoke_", dir=work_dir)).resolve()
            retained = str(root)
        else:
            temporary = tempfile.TemporaryDirectory(prefix="reacli_smoke_")
            root = Path(temporary.name)
        resource = root / "resource"
        if seed_resource and Path(seed_resource).expanduser().is_dir():
            shutil.copytree(Path(seed_resource).expanduser(), resource)
        platform.ensure_resource(resource)
        project, saved = root / "input.rpp", root / "saved.rpp"
        project.write_text(read_text("examples/minimal.rpp"), encoding="utf-8")
        script = generate({"ops": [{"op": "track.create", "args": [0, "reacli smoke"]}]}, root / "smoke.lua")
        proof = run(project, script, save_as=saved, reaper_bin=reaper_bin,
                    resource=resource, run_root=root / "runs", timeout=timeout)
        if not proof.ok:
            raise RuntimeError(f"{proof.reason_code}: {proof.error}; artifacts: {proof.run_dir if retained else 'use --work-dir to retain logs'}")
        expect(parse(saved)).track_count(1).track(0).name("reacli smoke")
        detail = "Generated Lua executed; valid proof and saved project verified"
        if render:
            source, output = root / "source.wav", root / "rendered.wav"
            sr = 8000
            pcm = b"".join(struct.pack("<h", round(0.25 * 32767 * math.sin(2 * math.pi * 440 * i / sr))) for i in range(sr))
            with wave.open(str(source), "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(sr)
                wav.writeframes(pcm)
            render_project = root / "render.rpp"
            render_project.write_text(
                '<REAPER_PROJECT 0.1 "7.0" 1\n'
                '  SAMPLERATE 8000 1 0\n'
                f'  RENDER_FILE {quote_value(str(output))}\n'
                '  RENDER_PATTERN ""\n  RENDER_FMT 0 2 8000\n'
                '  RENDER_RANGE 1 0 0 0 0\n'
                '  <TRACK\n    NAME "sine"\n    VOLPAN 1 0 1 -1\n'
                '    <ITEM\n      POSITION 0\n      LENGTH 1\n      VOLPAN 1 0 1 -1\n'
                f'      <SOURCE WAVE\n        FILE {quote_value(str(source))}\n'
                '      >\n    >\n  >\n>\n', encoding="utf-8")
            binary = resolve_executable(platform.find_reaper(reaper_bin))
            command = platform.build_command(binary, "-renderproject", str(render_project),
                                             "-nosplash", "-ignoreerrors", resource=resource)
            proc = run_bounded(command, timeout=timeout)
            (root / "render.log").write_text(proc.stdout + proc.stderr, encoding="utf-8")
            if proc.returncode:
                raise RuntimeError(f"Render exited {proc.returncode}: {proc.stderr[-1000:]}")
            expect_audio(output).duration(1, tol=0.1).not_silent().no_clipping().dominant_freq(440, tol=5)
            detail += "; WAV render passed duration, non-silence, clipping and 440 Hz checks"
        return {"name": "smoke", "status": "ok", "detail": detail, "hint": "", "artifacts": retained}
    except Exception as exc:
        return {"name": "smoke", "status": "error", "detail": f"{type(exc).__name__}: {exc}",
                "hint": "Run with --work-dir to retain logs. Check REAPER first-launch dialogs and external dependencies.", "artifacts": retained}
    finally:
        if temporary:
            temporary.cleanup()
