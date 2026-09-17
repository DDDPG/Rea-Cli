"""Checkout-only navigation and current provenance contracts (no remote requests)."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


def test_local_markdown_file_targets_exist():
    names = subprocess.check_output(
        ['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard', '--', '*.md'],
        cwd=ROOT,
    ).decode('utf-8').split('\0')
    missing = []
    for name in sorted(set(filter(None, names))):
        path = ROOT / name
        if not path.exists():  # A staged removal can still be in the index.
            continue
        in_fence = False
        for line_number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if line.lstrip().startswith(('```', '~~~')):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for target in re.findall(r'\]\((<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)', line):
                target = target.strip('<>')
                if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:|^#|^/', target):
                    continue
                relative = unquote(target.split('#')[0].split('?')[0])
                if relative and not (path.parent / relative).exists():
                    missing.append(f'{name}:{line_number}: {target}')
    assert not missing, '\n'.join(missing)


def test_current_reference_manifest_targets_and_hashes():
    manifest = json.loads((ROOT / 'reference/source-manifest.json').read_text(encoding='utf-8'))
    for entry in manifest['imported'] + manifest['authored']:
        path = ROOT / entry['destination']
        assert path.is_file(), entry['destination']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['destination_sha256'], str(path)
    for entry in manifest['already_bundled']:
        path = ROOT / entry['canonical']
        assert path.is_file(), entry['canonical']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['current_sha256'], str(path)
