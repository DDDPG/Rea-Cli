#!/usr/bin/env python3
"""Run bound ReaCli/Python, export starters, or compose validated native Lua."""
from __future__ import annotations
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

SKILL = Path(__file__).resolve().parents[1]


def compose(body_path, output):
    from rac.resources import read_text
    from rac.luagen import validate
    body = Path(body_path).read_text(encoding='utf-8')
    if not re.search(r'local\s+function\s+body\s*\(', body):
        raise ValueError('Supply a local function body() ... end; see assets/inspect.body.lua')
    script, count = re.subn(r'local function body\(\).*?\nend(?=\n-- ={10,})',
                            lambda _: body.rstrip(), read_text('lua/entry.lua'), flags=re.S)
    if count != 1:
        raise ValueError('Runtime entry boundary changed; review composition contract')
    with tempfile.TemporaryDirectory(prefix='rac-compose-') as temp:
        staged = Path(temp) / 'script.lua'; staged.write_text(script, encoding='utf-8')
        validate(staged)
        with Path(output).open('x', encoding='utf-8') as stream:
            stream.write(script)
    return str(Path(output).resolve())


def main():
    args = sys.argv[1:]
    if not args or args[0] in ('-h', '--help'):
        print('toolkit.py doctor [rac doctor options] | rac ARGS | python ARGS | compose BODY OUTPUT | templates NEW_DIR')
        return 0
    config_file = SKILL / 'runtime.json'
    if config_file.exists():
        config = json.loads(config_file.read_text(encoding='utf-8'))
        python = (SKILL / config['python']).absolute()
        os.environ.setdefault('RAC_REAPER_RESOURCE', str((SKILL / config['resource']).resolve()))
        # Never resolve the venv Python symlink: its invoked path selects the environment.
        if '--bound' not in args:
            return subprocess.call([str(python), str(Path(__file__).resolve()), '--bound', *args])
    elif '--bound' not in args:
        raise RuntimeError('Toolkit is not installed; run scripts/install.py first')
    if args[0] == '--bound': args.pop(0)
    command, *rest = args
    if command == 'python':
        return subprocess.call([sys.executable, *rest])
    if command in ('rac', 'doctor'):
        return subprocess.call([sys.executable, '-m', 'rac', *(['doctor'] if command == 'doctor' else []), *rest])
    if command == 'compose' and len(rest) == 2:
        print(json.dumps({'ok': True, 'script': compose(*rest)})); return 0
    if command == 'templates' and len(rest) == 1:
        from rac.resources import export_resources
        target = Path(rest[0])
        if target.exists(): raise FileExistsError(target)
        export_resources(target)
        shutil.copytree(SKILL / 'assets', target / 'coding')
        print(json.dumps({'ok': True, 'directory': str(target.resolve())})); return 0
    raise ValueError('Unknown command or invalid arguments; use --help')


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}), file=sys.stderr)
        raise SystemExit(1)
