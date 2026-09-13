"""Open each numbered RPP independently and capture its REAPER window on macOS.

Requires rac, REAPER, Swift and macOS Screen Recording permission for the terminal.
Uses screencapture; no simulated clicks, keyboard shortcuts or project edits.
Outputs remain beneath the supplied demo directory. Existing captures are skipped.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from rac.runner import platform

WINDOWS_SWIFT = '''import CoreGraphics
import Foundation
let ws = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]] ?? []
let pid = Int(CommandLine.arguments[1])!
for w in ws where (w[kCGWindowOwnerPID as String] as? Int) == pid {
 let info: [String: Any] = ["id":w[kCGWindowNumber as String]!, "name":w[kCGWindowName as String] ?? ""]
 print(String(data: try! JSONSerialization.data(withJSONObject:info), encoding:.utf8)!)
}
'''


def capture(root: Path, resource_seed: Path | None, limit: int | None) -> None:
    if sys.platform != 'darwin':
        raise RuntimeError('This capture helper requires macOS')
    root = root.resolve()
    entries = [json.loads(line) for line in (root/'steps/index.jsonl').read_text().splitlines()]
    frames = root/'frames'
    frames.mkdir(exist_ok=True)
    resource = root/'capture-resource'
    if not resource.exists():
        shutil.copytree(resource_seed or root/'resource', resource)
    swift = frames/'windows.swift'
    swift.write_text(WINDOWS_SWIFT)
    binary = frames/'windows'
    if not binary.exists():
        subprocess.run(['swiftc', str(swift), '-o', str(binary)], check=True)
    captured = 0
    for entry in entries:
        project = (root/'steps'/entry['file']).resolve()
        stem = project.stem
        output = frames/(stem+'.png')
        evidence = frames/(stem+'.capture.json')
        digest = hashlib.sha256(project.read_bytes()).hexdigest()
        if output.exists() and evidence.exists():
            old = json.loads(evidence.read_text())
            context_ok = entry.get('fx_track') is None or (
                old.get('fx_image') and (frames/old['fx_image']).exists() and old.get('main_window'))
            if old.get('rpp_sha256') == digest and context_ok:
                continue
        if limit is not None and captured >= limit:
            break
        ready, done = frames/(stem+'.ready'), frames/(stem+'.done')
        ready.unlink(missing_ok=True)
        done.unlink(missing_ok=True)
        # The script only sets the view, checks the loaded file, and waits for capture.
        fx = entry.get('fx_track')
        show_fx = ''
        if fx is not None:
            tr = 'reaper.GetMasterTrack(0)' if fx == 'master' else f'reaper.GetTrack(0,{fx})'
            show_fx = f'local tr={tr}; reaper.SetOnlyTrackSelected(tr); reaper.TrackFX_Show(tr,reaper.TrackFX_GetCount(tr)-1,1)'
            if fx == 'master':
                show_fx += '; reaper.SetMasterTrackVisibility(1)'
            show_fx += '; reaper.TrackList_AdjustWindows(false); reaper.UpdateArrange()'
        script = frames/(stem+'.lua')
        script.write_text(f'''
local _, loaded = reaper.EnumProjects(-1, "")
assert(loaded == {json.dumps(str(project))}, "Wrong project loaded")
assert(reaper.CountTracks(0) == {entry['tracks']}, "Wrong track count")
assert(reaper.CountMediaItems(0) == {entry['items']}, "Wrong item count")
reaper.GetSet_ArrangeView2(0,true,0,0,0,17)
reaper.TrackList_AdjustWindows(false)
reaper.UpdateArrange()
{show_fx}
local started = reaper.time_precise()
local announced = false
local function tick()
 if not announced and reaper.time_precise()-started > 1.5 then
  local f=assert(io.open({json.dumps(str(ready))},"w")); f:write(loaded); f:close()
  announced=true
 end
 local f=io.open({json.dumps(str(done))},"r")
 if f then
  f:close()
  -- Discard capture-only selection/master-visibility changes before closing.
  reaper.Main_openProject("noprompt:" .. loaded)
  reaper.Main_OnCommand(40004,0)
  return
 end
 reaper.defer(tick)
end
reaper.defer(tick)
''')
        command = platform.build_command(platform.find_reaper(), '-nosplash', str(project), str(script), resource=resource)
        with (frames/(stem+'.log')).open('w') as log:
            proc = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            try:
                deadline = time.monotonic()+25
                while not ready.exists():
                    if proc.poll() is not None or time.monotonic()>deadline:
                        raise RuntimeError(f'{stem}: REAPER did not confirm project readiness; see log')
                    time.sleep(.1)
                windows = [json.loads(line) for line in subprocess.check_output([str(binary),str(proc.pid)],text=True).splitlines()]
                matches = [w for w in windows if w['name'].startswith(stem+' ') and ' - REAPER ' in w['name']]
                if len(matches)!=1:
                    raise RuntimeError(f'{stem}: expected one capture window, found {len(matches)}')
                subprocess.run(['screencapture','-x','-o','-l',str(matches[0]['id']),str(output)],check=True)
                fx_evidence = {}
                if fx is not None:
                    fx_windows = [w for w in windows if w['name'].startswith('FX:')]
                    if len(fx_windows) != 1:
                        raise RuntimeError(f'{stem}: expected one FX window')
                    fx_output = frames/(stem+'.fx.png')
                    subprocess.run(['screencapture','-x','-o','-l',str(fx_windows[0]['id']),str(fx_output)],check=True)
                    fx_evidence = {'fx_image':fx_output.name, 'fx_window_id':fx_windows[0]['id']}
                evidence.write_text(json.dumps({**entry, 'image':output.name, 'rpp_sha256':digest,
                    'loaded_project':ready.read_text(), 'pid':proc.pid, 'window_id':matches[0]['id'],
                    'main_window':True, **fx_evidence},indent=2))
                captured+=1
                print(f"{stem}: captured ({captured} this run)",flush=True)
            finally:
                done.touch()
                try:
                    proc.wait(timeout=4)
                except subprocess.TimeoutExpired:
                    proc.terminate()
                    try:
                        proc.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        proc.kill(); proc.wait()
    records = [json.loads((frames/(Path(e['file']).stem+'.capture.json')).read_text())
               for e in entries if (frames/(Path(e['file']).stem+'.capture.json')).exists()]
    (frames/'index.json').write_text(json.dumps(records,indent=2))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('demo',type=Path)
    parser.add_argument('--resource-seed',type=Path,help='Optional prepared local resource directory; copied, never modified')
    parser.add_argument('--limit',type=int,help='Capture at most this many new frames (resume by running again)')
    args=parser.parse_args()
    capture(args.demo,args.resource_seed,args.limit)
