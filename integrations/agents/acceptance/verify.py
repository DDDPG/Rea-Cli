"""Independent showcase readback and audio acceptance; never repairs candidate output."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np
import soundfile as sf
from rac.runner import run
from reaper_parser import parse

ROOT = Path(__file__).resolve().parent


def verify(workspace, output):
    workspace = Path(workspace).resolve(); output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    project = workspace / 'output/Show-Session.rpp'; audio = workspace / 'output/preview.wav'
    if not project.is_file() or not audio.is_file():
        raise FileNotFoundError('Expected output/Show-Session.rpp and output/preview.wav')
    module_path = ROOT.parent / 'reaper-agent-cli/scripts/toolkit.py'
    spec = importlib.util.spec_from_file_location('toolkit_composition', module_path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    module.compose(ROOT / 'inspect.body.lua', output / 'inspect.lua')
    proof = run(project, output / 'inspect.lua', run_root=output / 'runs',
                resource=workspace / '.reacli-toolkit/resource', timeout=60)
    (output / 'proof.json').write_text(json.dumps(proof.to_dict(),indent=2)+'\n')
    assert proof.ok, proof.to_dict()
    state = proof.result
    tracks = state['tracks']; checks = {}
    def check(name, value): checks[name] = bool(value)
    expected=['01 RHYTHM','02 Pulse','03 Ticks','04 Bass','05 Chords','06 Melody','07 Parallel bus']
    check('track_names_order', [t['name'] for t in tracks] == expected)
    check('tempo', abs(state['tempo']-120)<1e-6)
    check('time_signature',state['time_signature']==[4,4])
    check('folder', [t['folder'] for t in tracks]==[1,0,-1,0,0,0,0])
    if len(tracks)==7:
        check('five_synths',sum('reasynth' in f['name'].lower() and f['enabled'] for t in tracks for f in t['fx'])==5)
        pulse=tracks[1]['items']
        check('pulse_split',len(pulse)==2 and all(abs(i['position']-p)<1e-6 and abs(i['length']-8)<1e-6 for i,p in zip(pulse,[0,8])))
        check('instrument_spans',all(len(t['items'])==1 and abs(t['items'][0]['position'])<1e-6 and abs(t['items'][0]['length']-16)<1e-6 for t in tracks[2:6]))
        takes=tracks[4]['items'][0]['takes'] if tracks[4]['items'] else []
        check('distinct_chord_takes',len(takes)==2 and all(t['midi'] and t['notes']>0 for t in takes) and takes[0]['pitches']!=takes[1]['pitches'])
        expected_chords=[{0,4,7},{9,0,4},{5,9,0},{7,11,2}]
        check('harmony_both_takes',len(takes)==2 and all(
            {n['pitch']%12 for n in take['pitches'] if start<=n['start_time']<start+4}==chord
            for take in takes for start,chord in zip([0,4,8,12],expected_chords)))
        check('melody_16_notes',bool(tracks[5]['items']) and tracks[5]['items'][0]['takes'][0]['notes']==16)
        check('midi_instruments',all(tk['midi'] and tk['notes']>0 for t in tracks[1:6] for item in t['items'] for tk in item['takes']))
        check('pan_envelope',any('pan' in e['name'].lower() and e['points']==3 for e in tracks[3]['envelopes']))
        check('volume_envelope',any('volume' in e['name'].lower() and e['points']==5 for e in tracks[4]['envelopes']))
        check('quiet_parallel_send',any(r['source']=='05 Chords' and 0<r['volume']<1 for r in tracks[6]['receives']))
        check('colors',all(t['color']!=0 for t in tracks))
        def effect_parameters(track, name):
            return next((f['params'] for f in track if name in f['name'].lower() and f['enabled']), [])
        verb=effect_parameters(tracks[4]['fx'],'reaverbate')
        comp=effect_parameters(tracks[3]['fx'],'reacomp')
        limit=effect_parameters(state['master_fx'],'realimit')
        eq=effect_parameters(tracks[5]['fx'],'reaeq')
        def matches(params,name,target,tol=0.15):
            import re
            for p in params:
                if p['name'].lower()==name.lower():
                    n=re.search(r'[-+]?\d+(?:\.\d+)?',p['formatted'])
                    return bool(n and abs(float(n[0])-target)<=tol)
            return False
        check('verb_room',matches(verb,'Room size',90))
        check('verb_damp',matches(verb,'Dampening',20))
        check('verb_wet',matches(verb,'Wet',-12))
        check('verb_dry',matches(verb,'Dry',0))
        check('comp_threshold',matches(comp,'Threshold',-15))
        check('comp_makeup',matches(comp,'Wet',3))
        check('comp_auto_off',any('auto' in p['name'].lower() and 'make' in p['name'].lower() and (p['value']==0 or p['formatted'].lower() in ('off','no')) for p in comp))
        check('limit_threshold',matches(limit,'Threshold',-4.5))
        check('limit_ceiling',matches(limit,'Brickwall Ceiling',-1) or matches(limit,'Ceiling',-1))
        bands=next((f['bands'] for f in tracks[5]['fx'] if 'reaeq' in f['name'].lower() and f['enabled']),[])
        enabled=[b for b in bands if b['enabled']]
        check('eq_highpass_100_only',len(enabled)==1 and enabled[0]['type']==0 and abs(float(enabled[0]['frequency'].split()[0])-100)<0.1)
    check('markers_regions',state['markers']==3 and state['regions']==2)
    check('time_selection',abs(state['time_start'])<1e-6 and abs(state['time_end']-16)<1e-6)
    check('notes',bool(state['notes']))
    doc=parse(project)
    check('no_external_media',not any(n.find_line('FILE') for n in doc.root.iter_chunks('SOURCE')))
    samples,sr=sf.read(audio,always_2d=True,dtype='float32')
    peak=float(np.max(np.abs(samples)));rms=float(np.sqrt(np.mean(samples.astype(float)**2)))
    check('audio_layout',sr==48000 and samples.shape==(1152000,2))
    check('audio_finite',np.isfinite(samples).all())
    check('audio_audible_unclipped',rms>1e-5 and 1e-4<peak<1)
    report={'ok':all(checks.values()),'checks':checks,'host':state['host'],'audio':{'frames':len(samples),'sample_rate':sr,'channels':samples.shape[1],'peak':peak,'rms':rms},'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (project,audio)},'host_state':state,'limits':['Acceptance verifies structural and numerical requirements; musical aesthetics are not scored.']}
    (output/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('workspace');p.add_argument('output');a=p.parse_args()
    result=verify(a.workspace,a.output)
    print(json.dumps({k:v for k,v in result.items() if k!='host_state'},indent=2))
    raise SystemExit(0 if result['ok'] else 1)
