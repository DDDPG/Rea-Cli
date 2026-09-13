import hashlib
import importlib.util
import json
from pathlib import Path
from reaper_parser import parse, schema

ROOT = Path(__file__).resolve().parents[2]


def test_generated_consumers_are_current_and_deterministic():
    spec = importlib.util.spec_from_file_location(
        "generator", ROOT / "tools/generate_schema.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    first = module.products()
    assert first == module.products()
    for path, content in first.items():
        assert path.read_text(encoding="utf8") == content, str(path)


def test_all_adopted_fields_have_real_two_value_saved_evidence():
    source = ROOT / "schema/rpp/evidence/live-validation.json"
    data = json.loads(source.read_text())
    assert len(data["probes"]) == 23
    for probe in data["probes"]:
        assert probe["ok"] and probe["values"][0] != probe["values"][1]
        observed = []
        for filename in probe["files"]:
            path = ROOT / "schema/rpp" / filename
            doc = parse(path)
            nodes = [doc.root] if probe["scope"] == "project" else doc.tracks()
            rows = [row for node in nodes for row in node.find_lines(probe["token"])]
            assert rows
            observed.append(float(rows[0].values[probe["index"] - 1]))
        assert observed == probe["values"]
        meta = schema.field_meta(probe["scope"], probe["token"], probe["index"])
        assert meta["semantic_status"] == "confirmed"
        assert (
            meta["evidence"][0]["sha256"]
            == hashlib.sha256(source.read_bytes()).hexdigest()
        )


def test_unknown_and_missing_defaults_not_promoted():
    data = schema.load()
    assert len(data["keys"]) == 181
    fields = [f for e in data["keys"].values() for f in e["fields"]]
    assert sum(f["semantic_status"] == "confirmed" for f in fields) == 23
    assert all(f["default_status"] == "unknown" for f in fields)
