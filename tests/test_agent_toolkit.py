"""Project installer contracts: isolation, collision refusal and real CLI binding."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import json
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'integrations/agents/reaper-agent-cli/scripts/install.py'
spec = importlib.util.spec_from_file_location('agent_install', SCRIPT)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


def test_collision_refuses_all_targets_before_mutation(tmp_path):
    existing = tmp_path / '.qwen/skills/reaper-agent-cli'
    existing.mkdir(parents=True)
    (existing / 'keep.txt').write_text('user skill')
    with pytest.raises(FileExistsError):
        installer.install(tmp_path, ['claude', 'codex', 'qwen'], runtime_python=sys.executable)
    assert (existing / 'keep.txt').read_text() == 'user skill'
    assert not (tmp_path / '.reacli-toolkit').exists()
    assert not (tmp_path / '.claude').exists()


def test_project_install_executes_bound_cli_and_exports_starters(tmp_path):
    pytest.importorskip('numpy'); pytest.importorskip('soundfile')
    # Existing harness configuration is outside installer ownership.
    config = tmp_path / '.claude/settings.json'
    config.parent.mkdir(); config.write_text('{"custom":true}')
    report = installer.install(tmp_path, list(installer.LOCATIONS), runtime_python=sys.executable)
    assert report['doctor']['ok']
    assert config.read_text() == '{"custom":true}'
    for directory in report['skills'].values():
        tool = Path(directory) / 'scripts/toolkit.py'
        result = subprocess.run([sys.executable, str(tool), 'doctor', '--profile', 'offline', '--json'], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)['ok']
        assert (Path(directory) / 'assets/gain_simple.jsfx').is_file()
    tool = Path(report['skills']['codex']) / 'scripts/toolkit.py'
    destination = tmp_path / 'starters'
    command = [sys.executable, str(tool), 'templates', str(destination)]
    subprocess.run(command, check=True, capture_output=True)
    assert (destination / 'coding/inspect.body.lua').is_file()
    assert (destination / 'minimal.rpp').is_file()
    assert subprocess.run(command, capture_output=True).returncode != 0


def test_lua_composition_validates_before_writing_and_refuses_overwrite(tmp_path):
    import shutil
    if not shutil.which('luac'):
        pytest.skip('Lua compiler unavailable')
    spec = importlib.util.spec_from_file_location('toolkit_compose', SCRIPT.with_name('toolkit.py'))
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    body = tmp_path / 'body.lua'; output = tmp_path / 'script.lua'
    body.write_text('local function body()\n  RUN.result={answer=42}\nend\n')
    helper.compose(body, output)
    original = output.read_bytes()
    assert b'answer=42' in original
    with pytest.raises(FileExistsError):
        helper.compose(body, output)
    assert output.read_bytes() == original
    body.write_text('local function body()\n this is not Lua\nend\n')
    with pytest.raises(SyntaxError):
        helper.compose(body, tmp_path / 'invalid.lua')
    assert not (tmp_path / 'invalid.lua').exists()
