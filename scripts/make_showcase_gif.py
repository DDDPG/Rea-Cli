"""Assemble one screenshot per numbered RPP into the README GIF (requires Pillow).

python scripts/make_showcase_gif.py ./demo/walkthrough/frames ./docs/assets/showcase.gif

Reads the capture manifest in build order and rejects missing or stale captures.
Only layout, captions, scaling and title-bar cropping are applied to screenshots.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

TITLES = {
    'blank': 'Blank session',
    'melody-lowcut-100hz': 'Melody / ReaEQ / 100 Hz low cut',
    'chords-long-reverb': 'Chords / ReaVerbate / long reverb',
    'bass-threshold-minus15db': 'Bass / ReaComp / threshold -15 dB',
    'bass-makeup-plus3db': 'Bass / ReaComp / makeup +3 dB',
    'master-threshold-minus4-5db': 'Master / ReaLimit / threshold -4.50 dB',
    'master-ceiling-minus1db': 'Master / ReaLimit / ceiling -1.00 dB',
    'finished-session': 'Complete session / ready to play',
}


def _manifest_file(base: Path, value, label: str) -> Path:
    """Resolve a manifest path only when it stays in the supplied root."""
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty relative path")
    base = base.resolve()
    raw = base / value
    if any(part.is_symlink() for part in (raw, *raw.parents) if part != base):
        raise ValueError(f"{label} must not traverse a symlink: {value}")
    candidate = raw.resolve()
    if candidate != base and base not in candidate.parents:
        raise ValueError(f"{label} escapes {base}: {value}")
    if not candidate.is_file():
        raise FileNotFoundError(f"{label} is not a file: {candidate}")
    return candidate


def assemble(frames: Path, output: Path, font_path: Path) -> None:
    steps = frames.parent / 'steps'
    entries = [json.loads(line) for line in
               (steps/'index.jsonl').read_text(encoding='utf-8').splitlines()]
    records = json.loads((frames/'index.json').read_text(encoding='utf-8'))
    if [r['file'] for r in records] != [e['file'] for e in entries]:
        raise RuntimeError('Capture every RPP in order before assembling the GIF')
    title_font = ImageFont.truetype(str(font_path), 27)
    caption_font = ImageFont.truetype(str(font_path), 18)
    images, durations = [], []
    for i, entry in enumerate(records):
        project = _manifest_file(steps, entry.get('file'), 'capture project')
        if hashlib.sha256(project.read_bytes()).hexdigest() != entry['rpp_sha256']:
            raise RuntimeError(f"Stale capture: {entry['file']}")
        image = _manifest_file(frames, entry.get('image'), 'capture image')
        with Image.open(image) as capture:
            capture = capture.convert('RGB')
            if entry['main_window']:
                # Captures are 2x Retina macOS windows; omit the license title bar.
                capture = capture.crop((0, 56, capture.width, capture.height))
            capture = ImageOps.contain(capture, (1248, 776), Image.Resampling.LANCZOS)
            canvas = Image.new('RGB', (1280, 900), '#171d24')
            canvas.paste(capture, ((1280-capture.width)//2, 80+(776-capture.height)//2))
        if entry.get('fx_track') is not None:
            if not entry.get('fx_image'):
                raise RuntimeError('Recapture FX stages with the DAW context before assembling')
            # Both windows come from the same loaded RPP. Keep the selected
            # track controls visible on the left, with its FX panel on the right.
            fx_image = _manifest_file(frames, entry['fx_image'], 'FX capture image')
            with Image.open(fx_image) as fx_capture:
                fx_capture = ImageOps.contain(fx_capture.convert('RGB'), (880, 550), Image.Resampling.LANCZOS)
                x, y = 1264-fx_capture.width, 842-fx_capture.height
                ImageDraw.Draw(canvas).rectangle((x-3,y-3,x+fx_capture.width+2,y+fx_capture.height+2), fill='#7ceac5')
                canvas.paste(fx_capture,(x,y))
        draw = ImageDraw.Draw(canvas)
        title = TITLES.get(entry['label'],entry['label'].replace('-',' ').capitalize())
        draw.text((24,16), f'{i:02d} / {len(records)-1:02d}   {title}', font=title_font, fill='#7ceac5')
        caption = f"{entry['tracks']} tracks  |  {entry['items']} items  |  {entry['file']}"
        draw.text((24,52),caption,font=caption_font,fill='#edf2f7')
        draw.text((24,866),'Rea-Cli  |  Independently opened RPP snapshots  |  MIDI + built-in REAPER FX',font=caption_font,fill='#a5b1be')
        draw.rectangle((0,896,round(1280*(i+1)/len(records)),899),fill='#7ceac5')
        images.append(canvas.quantize(colors=256,method=Image.Quantize.MEDIANCUT))
        durations.append(350)
    durations[0], durations[-1] = 900, 2250
    output.parent.mkdir(parents=True,exist_ok=True)
    images[0].save(output,save_all=True,append_images=images[1:],duration=durations,
                   loop=0,optimize=True,disposal=1)
    with Image.open(output) as result:
        assert result.n_frames==len(records) and result.size==(1280,900)
        total=0
        for i in range(result.n_frames):
            result.seek(i); total+=result.info['duration']
        assert total==sum(durations)
    print(json.dumps({'gif':str(output),'frames':len(records),'seconds':total/1000,'bytes':output.stat().st_size}))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frames',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--font',type=Path,default=Path('/System/Library/Fonts/Supplemental/Arial.ttf'),help='TrueType font path; override on Linux')
    args=parser.parse_args()
    assemble(args.frames,args.output,args.font)
