#!/usr/bin/env python3
"""Project-scoped CLI toolkit bootstrap. No registry upload or harness settings edits."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv

BUNDLE = Path(__file__).resolve().parents[1]
LOCATIONS = {'claude': '.claude', 'codex': '.agents', 'qwen': '.qwen'}


def inventory(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file()
            and '__pycache__' not in p.parts and p.suffix != '.pyc'}


def install(project, harnesses, source=None, wheels=None, runtime_python=None):
    project = Path(project).expanduser().resolve()
    project.mkdir(parents=True, exist_ok=True)
    targets = [project / LOCATIONS[h] / 'skills/reaper-agent-cli' for h in harnesses]
    state = project / '.reacli-toolkit'
    # Preflight every target before changing any of them. Reinstall in a fresh project.
    for path in [state, *targets]:
        if path.exists() or path.is_symlink():
            raise FileExistsError(f'Refusing to overwrite {path}; choose a fresh project or remove the prior toolkit explicitly')
    if source:
        source = Path(source).expanduser().resolve()
        for package in ('reaper-parser', 'reacli'):
            if not (source / 'packages' / package / 'pyproject.toml').is_file():
                raise ValueError(f'Not an ecosystem source checkout: {source}')
    if wheels:
        wheels = Path(wheels).expanduser().resolve()
        selected = []
        for name in ('reaper_parser', 'reacli'):
            found = list(wheels.rglob(name + '-*.whl'))
            if len(found) != 1:
                raise ValueError(f'Expected exactly one {name} wheel')
            selected.append(str(found[0]))
    created = []
    state.mkdir()
    try:
        if runtime_python:
            python = Path(runtime_python).expanduser().absolute()
            if not python.is_file():
                raise ValueError(f'Python not found: {python}')
        else:
            venv.EnvBuilder(with_pip=True).create(state / 'venv')
            python = state / 'venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
            packages = ([str(source / 'packages/reaper-parser'), str(source / 'packages/reacli') + '[audio]']
                        if source else [*selected, 'numpy>=1.24', 'soundfile>=0.12'])
            with (state / 'install.log').open('w', encoding='utf-8') as log:
                subprocess.run([str(python), '-m', 'pip', 'install', *packages],
                               stdout=log, stderr=subprocess.STDOUT, check=True, timeout=600)
        probe = subprocess.run([str(python), '-m', 'rac', 'doctor', '--profile', 'offline', '--json'],
                               capture_output=True, text=True, timeout=30)
        doctor = json.loads(probe.stdout)
        if probe.returncode or not doctor.get('ok'):
            raise RuntimeError(f'Offline doctor failed: {doctor}')
        subprocess.run([str(python), '-c', 'import numpy, soundfile, reaper_parser'], check=True, timeout=30)
        versions = {}
        for h, target in zip(harnesses, targets):
            executable = shutil.which('claude' if h == 'claude' else h)
            if executable:
                try:
                    result = subprocess.run([executable, '--version'], capture_output=True, text=True, timeout=15)
                    versions[h] = {'available': result.returncode == 0, 'version': result.stdout.strip()}
                except subprocess.TimeoutExpired:
                    versions[h] = {'available': False, 'reason': 'version_probe_timeout'}
            else:
                versions[h] = {'available': False, 'reason': 'not_on_path'}
            target.parent.mkdir(parents=True, exist_ok=True)
            created.append(target)
            shutil.copytree(BUNDLE, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'runtime.json'))
            config = {'python': os.path.relpath(python, target),
                      'resource': os.path.relpath(state / 'resource', target)}
            (target / 'runtime.json').write_text(json.dumps(config, indent=2) + '\n', encoding='utf-8')
        report = {'ok': True, 'harnesses': versions, 'doctor': doctor,
                  'skills': {h: str(t) for h, t in zip(harnesses, targets)},
                  'python': str(python), 'source_mode': 'checkout' if source else 'wheels' if wheels else 'existing-runtime',
                  'files': {h: inventory(t) for h, t in zip(harnesses, targets)},
                  'host_checked': False, 'permissions_changed': False}
        (state / 'installation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        return report
    except BaseException:
        # Keep diagnostics, but no partially discoverable skills.
        for target in created:
            if target.exists():
                shutil.rmtree(target)
        (state / 'FAILED').write_text('Installation failed; inspect install.log and rerun in a fresh target.\n')
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--harness', choices=[*LOCATIONS, 'all'], default='all')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--source', type=Path, help='Local checkout used as the source for the install')
    mode.add_argument('--wheels', type=Path, help='Candidate folder with exactly one wheel per package')
    mode.add_argument('--runtime-python', type=Path, help='Reuse an already installed Python with rac, parser and audio dependencies')
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        parser.error('Python 3.10+ required')
    selected = list(LOCATIONS) if args.harness == 'all' else [args.harness]
    try:
        result = install(args.project, selected, args.source, args.wheels, args.runtime_python)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)})); return 1
    print(json.dumps(result, indent=2)); return 0


if __name__ == '__main__':
    raise SystemExit(main())
