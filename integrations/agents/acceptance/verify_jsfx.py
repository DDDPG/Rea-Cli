"""Verify the bundled stereo JSFX gain starter in an isolated real REAPER render."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import shutil
import numpy as np
import soundfile as sf
from rac.environment import run_bounded
from rac.resources import read_text
from rac.runner import run, platform
from rac.luagen.generator import _lua_literal as lua


def verify(output):
    root = Path(output).resolve()
    root.mkdir(parents=True, exist_ok=False)
    bundle = Path(__file__).resolve().parents[1] / 'reaper-agent-cli'
    spec = importlib.util.spec_from_file_location('toolkit', bundle / 'scripts/toolkit.py')
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    resource = platform.ensure_resource(root / 'resource')
    (resource / 'Effects').mkdir(exist_ok=True)
    effect = bundle / 'assets/gain_simple.jsfx'
    shutil.copy2(effect, resource / 'Effects/gain_simple.jsfx')
    sr = 48000
    tone = 0.1 * np.sin(2*np.pi*440*np.arange(sr)/sr)
    sf.write(root / 'tone.wav', np.column_stack([tone, tone]), sr, subtype='FLOAT')
    base = root / 'empty.rpp'; base.write_text(read_text('examples/minimal.rpp'))
    proofs = {}
    for label, db in [('unity', 0), ('attenuated', -6)]:
        body = f'''local function body()
  reaper.InsertMedia({lua(str(root/'tone.wav'))},1)
  local tr=reaper.GetTrack(0,0)
  assert(tr and reaper.CountTracks(0)==1)
  local fx=reaper.TrackFX_AddByName(tr,'JS: gain_simple.jsfx',false,-1)
  assert(fx>=0,'JSFX discovery failed')
  assert(reaper.TrackFX_SetParam(tr,fx,0,{db}))
  for key,value in pairs({{RENDER_SETTINGS=0,RENDER_SRATE=48000,RENDER_CHANNELS=2,RENDER_BOUNDSFLAG=0,RENDER_STARTPOS=0,RENDER_ENDPOS=1,RENDER_TAILFLAG=0,RENDER_DITHER=0,RENDER_NORMALIZE=0}}) do
    reaper.GetSetProjectInfo(0,key,value,true)
  end
  reaper.GetSetProjectInfo_String(0,'RENDER_FILE',{lua(str(root))},true)
  reaper.GetSetProjectInfo_String(0,'RENDER_PATTERN',{lua(label)},true)
  reaper.GetSetProjectInfo_String(0,'RENDER_FORMAT','ZXZhdxAAAA==',true)
  RUN.result={{host=reaper.GetAppVersion(),gain=reaper.TrackFX_GetParam(tr,fx,0)}}
end
'''
        source = root / (label+'.body.lua'); source.write_text(body)
        script = root / (label+'.lua'); helper.compose(source, script)
        project = root / (label+'.rpp')
        proof = run(base, script, save_as=project, resource=resource,
                    run_root=root/(label+'-runs'),timeout=60)
        proofs[label] = proof.to_dict()
        (root/(label+'-proof.json')).write_text(json.dumps(proofs[label],indent=2)+'\n')
        assert proof.ok, proof.to_dict()
        result = run_bounded(platform.build_command(platform.find_reaper(),'-renderproject',str(project),'-nosplash','-ignoreerrors',resource=resource),timeout=60)
        (root/(label+'.log')).write_text(result.stdout+result.stderr)
        assert result.returncode==0
    unity, rate = sf.read(root/'unity.wav',always_2d=True)
    attenuated, rate2 = sf.read(root/'attenuated.wav',always_2d=True)
    expected = 10**(-6/20)
    ratio = float(np.sqrt(np.mean(attenuated**2)/np.mean(unity**2)))
    checks = {'layout':rate==rate2==sr and unity.shape==attenuated.shape==(sr,2),
              'finite':bool(np.isfinite(unity).all() and np.isfinite(attenuated).all()),
              'audible':float(np.max(np.abs(unity)))>0.09,
              'gain':abs(ratio-expected)<0.001}
    report={'ok':all(checks.values()),'checks':checks,'expected_gain':expected,'measured_gain':ratio,
            'host':proofs['unity']['result']['host'],'asset_sha256':hashlib.sha256(effect.read_bytes()).hexdigest()}
    (root/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('output');args=parser.parse_args()
    report=verify(args.output);print(json.dumps(report,indent=2))
    raise SystemExit(0 if report['ok'] else 1)
