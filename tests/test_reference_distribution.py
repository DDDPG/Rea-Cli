"""The supplemental Git knowledge must not become pip runtime payload."""
from importlib.metadata import distribution
from pathlib import PurePosixPath


def test_supplemental_knowledge_is_not_installed():
    files = distribution("reacli").files
    assert files, "Distribution must expose a file manifest"
    forbidden_files = {
        "actions_index.json", "api_pitfalls.json", "jsfx_reference.json",
        "source-manifest.json", "inspect_project.body.lua", "build_inspector.py",
        "gain_simple.jsfx", "delay_basic.jsfx", "midi_monitor.jsfx",
    }
    for file in files:
        path = PurePosixPath(str(file))
        assert "reference" not in path.parts, str(path)
        assert path.name not in forbidden_files, str(path)
