"""Build a playable 8-bar REAPER session using rac and REAPER's built-in ReaSynth.

    python examples/show_session.py ./demo/show-session

Requires REAPER and Lua 5.3/5.4. Refuses to overwrite an existing directory.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from rac.luagen import generate, validate
from rac.resources import read_text
from rac.rpp import emit, parse, patch
from rac.runner import run
from rac.runner import platform
from rac.environment import run_bounded
from rac.verify import expect, expect_audio

NAMES = ["01 RHYTHM / folder", "02 Pulse", "03 Ticks", "04 Bass",
         "05 Chords / two takes", "06 Melody", "07 Parallel bus"]


def compose(script: Path, root: Path, section: str, checkpoints: dict[int, str] | None = None) -> None:
    """Extend generated Lua through its body, retaining rac's proof/save protocol."""
    custom = Path(__file__).with_name('show_session.lua').read_text(encoding='utf-8')
    anchor = 'local ok, err = pcall(body)'
    source = script.read_text(encoding='utf-8')
    if source.count(anchor) != 1:
        raise RuntimeError('rac entry template changed; review demo composition')
    source = source.replace('local function body()', 'local demo_checkpoint\nlocal function body()')
    for index, label in (checkpoints or {}).items():
        op_anchor = f'  local r_{index} = '
        if source.count(op_anchor) != 1:
            raise RuntimeError('rac operation template changed; review demo checkpoints')
        source = source.replace(op_anchor, f'  demo_checkpoint({json.dumps(label)})\n' + op_anchor)
    extension = ('local DEMO_STEPS = ' + ('true' if checkpoints else 'false') + '\n'
                 + 'local DEMO_ROOT = ' + json.dumps(str(root), ensure_ascii=False) + '\n'
                 + custom + '\nlocal generated_body = body\n'
                 + 'body = function()\n generated_body()\n'
                 + ' for k in pairs(RUN.result or {}) do assert(not k:match("_error$"), k) end\n'
                 + (" demo_checkpoint(\"melody-complete\")\n build_details()\n build_effects()\n demo_checkpoint(\"finished-session\")\n" if section == 'build' else '')
                 + ' inspect_demo()\nend\n' + anchor)
    script.write_text(source.replace(anchor, extension), encoding='utf-8')
    validate(script)


def verify(proof) -> None:
    if not proof.ok:
        raise RuntimeError(json.dumps(proof.to_dict(), ensure_ascii=False, indent=2))
    r = proof.result
    assert r['names'] == NAMES, r
    assert r['folders'] == [1, 0, -1, 0, 0, 0, 0], r
    assert r['items'] == [0, 2, 1, 1, 1, 1, 0], r
    assert r['takes'] == 2 and r['active_take'] == 'Warm triads', r
    assert r['midi_notes'] == 16 and not r['midi_muted'], r
    assert r['synths'] == 5 and r['alternate_notes'] == 12, r
    assert r['volume_points'] == 5 and r['pan_points'] == 3, r
    assert r['sends'] == 1 and r['send_destination'] == NAMES[6], r
    assert r['markers'] == 3 and r['regions'] == 2, r
    fx = r['effects']
    for key, target in {'melody_lowcut_hz': 100, 'bass_threshold_db': -15,
                        'bass_makeup_db': 3, 'master_threshold_db': -4.5,
                        'reverb_room_size': 90, 'reverb_wet_db': -12}.items():
        assert abs(fx[key] - target) <= .11, fx
    assert fx['bass_auto_makeup'] == 0 and fx['enabled'] == 4, fx
    assert r['tempo'] == 120 and r['external_sources'] == 0, r


def build(root: Path, render: bool = False, steps: bool = False) -> Path:
    root = root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=False)
    if steps:
        (root / 'steps').mkdir()
    checkpoints = {}
    def checkpoint(label: str) -> None:
        if steps:
            checkpoints[len(ops)] = label
    project = root / 'seed.rpp'
    project.write_text(read_text('examples/minimal.rpp'), encoding='utf-8')
    if steps:
        (root / 'steps' / '000-blank.rpp').write_text(project.read_text(), encoding='utf-8')
        (root / 'steps' / 'index.jsonl').write_text(json.dumps({'file': '000-blank.rpp', 'label': 'blank', 'tracks': 0, 'items': 0}) + '\n', encoding='utf-8')
    # A real offline rac edit, then a live Lua build. No handwritten RPP chunks.
    doc = parse(project)
    patch.set_marker(doc, 1, 0, 'START / 120 BPM')
    project.write_text(emit(doc), encoding='utf-8')
    ops = [{'op': 'project.set_tempo', 'args': [120]}]
    checkpoint('tempo-and-start-marker')
    colors = [(82, 155, 210)] * 3 + [(219, 162, 76), (111, 189, 145), (177, 138, 214), (188, 188, 188)]
    for i, name in enumerate(NAMES):
        ops += [{'op': 'track.create', 'args': [i, name]},
                {'op': 'track.set_color', 'args': [i, *colors[i]]},
                {'op': 'track.set_volume_db', 'args': [i, -6 if i != 6 else -18]}]
        checkpoint(f'track-{i + 1}-{name.split()[1].lower()}')
    # MIDI is embedded in the RPP; ReaSynth ships with REAPER.
    for i in range(1, 6):
        ops += [{'op': 'midi.create_item', 'args': [i, 0, 16]},
                {'op': 'fx.add_by_name', 'args': [i, 'VSTi: ReaSynth (Cockos)']}]
        checkpoint(f'midi-item-and-reasynth-track-{i + 1}')
    for beat in range(32):
        ops.append({'op': 'midi.insert_note', 'args': [1, 0, 36, 90, beat * .5, beat * .5 + .1]})
        if (beat + 1) % 8 == 0:
            checkpoint(f'pulse-{beat + 1}-notes')
    for tick in range(64):
        ops.append({'op': 'midi.insert_note', 'args': [2, 0, 96, 45, tick * .25, tick * .25 + .04]})
        if (tick + 1) % 16 == 0:
            checkpoint(f'ticks-{tick + 1}-notes')
    for block, notes in enumerate([(48, 52, 55), (45, 48, 52), (41, 45, 48), (43, 47, 50)]):
        for note in notes:
            ops.append({'op': 'midi.insert_note', 'args': [4, 0, note, 65, block * 4, block * 4 + 3.8]})
        for beat in range(8):
            t = block * 4 + beat * .5
            ops.append({'op': 'midi.insert_note', 'args': [3, 0, notes[0] - 12, 80, t, t + .4]})
        checkpoint(f'chords-and-bass-section-{block + 1}')
    edits = [{'op': 'item.split_at', 'args': [1, 0, 8]},
            {'op': 'track.set_pan', 'args': [2, .25]},
            {'op': 'routing.create_send', 'args': [4, 6]},
            {'op': 'env.set_points_db', 'args': [4, 'Volume', [[0, -18, 0], [2, -6, 0], [8, -10, 0], [14, -6, 0], [16, -24, 0]]]},
            {'op': 'marker.add', 'args': [2, 8, 'B / alternate take available']},
            {'op': 'marker.add', 'args': [3, 16, 'END']},
            {'op': 'marker.add_region', 'args': [10, 0, 8, 'A / C - Am']},
            {'op': 'marker.add_region', 'args': [11, 8, 16, 'B / F - G']}]
    for edit in edits:
        ops.append(edit)
        checkpoint(edit['op'].replace('.', '-') + '-' + str(len(ops)))
    for i in range(16):
        ops.append({'op': 'midi.insert_note', 'args': [5, 0, [60, 64, 67, 72][i % 4], 88, i, i + .4]})
        if (i + 1) % 4 == 0 and i < 15:
            checkpoint(f'melody-{i + 1}-notes')
    script = generate({'modules': ['take', 'env'], 'ops': ops}, root / 'build.lua')
    compose(script, root, 'build', checkpoints)
    session = root / 'Show-Session.rpp'
    t = time.monotonic()
    proof = run(project, script, save_as=session, resource=root / 'resource', run_root=root / 'runs')
    (root / 'build-proof.json').write_text(json.dumps(proof.to_dict(), indent=2), encoding='utf-8')
    verify(proof)
    expect(parse(session)).track_count(7).track(4).name(NAMES[4]).item_count(1)
    # No audio sources should be serialized: MIDI lives inside the project.
    saved = parse(session)
    def check_sources(element):
        for child in element.children:
            if hasattr(child, 'children'):
                check_sources(child)
            elif child.key == 'FILE':
                raise RuntimeError('Demo unexpectedly depends on an external media file')
    check_sources(saved.root)
    check = generate({'ops': []}, root / 'inspect.lua')
    compose(check, root, 'inspect')
    reopened = run(session, check, resource=root / 'resource', run_root=root / 'runs')
    (root / 'reopen-proof.json').write_text(json.dumps(reopened.to_dict(), indent=2), encoding='utf-8')
    verify(reopened)
    if render:
        command = platform.build_command(platform.find_reaper(), '-renderproject', str(session),
                                         '-nosplash', '-ignoreerrors', resource=root / 'resource')
        result = run_bounded(command, timeout=60)
        (root / 'render.log').write_text(result.stdout + result.stderr, encoding='utf-8')
        if result.returncode:
            raise RuntimeError('Render failed; see render.log')
        expect_audio(root / 'Show-Session.wav').duration(24, tol=.1).not_silent().no_clipping()
    print(json.dumps({'project': str(session), 'verified': True, 'rendered': render,
                      'seconds': round(time.monotonic() - t, 2)}, indent=2))
    return session


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='New output directory')
    parser.add_argument('--render', action='store_true', help='Also render and verify a 24-second WAV (includes reverb tail)')
    parser.add_argument('--steps', action='store_true', help='Also save build checkpoints for screenshots')
    args = parser.parse_args()
    build(args.output, args.render, args.steps)
