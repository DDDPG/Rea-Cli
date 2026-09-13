"""Generate all RPP consumers from the reviewed JSON source. --check never writes."""

from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def encode(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def products(root=ROOT):
    source = root / "schema/rpp/spec.json"
    data = json.loads(source.read_text(encoding="utf-8"))
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    keys = {}
    ids = set()
    sections = []
    for entry in data["entries"]:
        if entry["id"] in ids:
            raise ValueError("Duplicate entry: " + entry["id"])
        ids.add(entry["id"])
        positions = set()
        for f in entry["fields"]:
            if f["index"] is not None:
                if f["index"] < 1 or f["index"] in positions:
                    raise ValueError("Invalid field index: " + f["id"])
                positions.add(f["index"])
            if f["semantic_status"] == "confirmed" and not f["evidence"]:
                raise ValueError("Missing evidence: " + f["id"])
        keys[entry["context"] + ":" + entry["name"]] = entry
    for section in data["sections"]:
        entries = []
        for e in data["entries"]:
            if e["section"] != section["id"]:
                continue
            entries.append(
                {
                    "name": e["name"],
                    "description": e.get("description", ""),
                    "isChunk": e["is_chunk"],
                    "tags": e["tags"],
                    "sourceFile": e.get("sourceFile", ""),
                    "fields": [
                        {
                            "label": f["label"],
                            "description": f["description"],
                            "type": f["type"],
                            "subFields": f.get("enum_candidates") or [],
                            "tags": [f["semantic_status"]],
                        }
                        for f in e["fields"]
                    ],
                }
            )
        sections.append({**section, "entries": entries})
    meta = {
        "schema_version": data["schema_version"],
        "schema_sha256": digest,
        "source": "ReaperDoc @ " + data["source_commit"],
        "index_base": 1,
        "key_count": len(keys),
        "section_count": len(sections),
    }
    runtime = {
        "meta": meta,
        "keys": keys,
        "sections": [
            {"id": s["id"], "entry_count": len(s["entries"])} for s in sections
        ],
    }
    fields = [f for e in data["entries"] for f in e["fields"]]
    coverage = {
        "meta": meta,
        "field_records": len(fields),
        "confirmed_semantics": sum(f["semantic_status"] == "confirmed" for f in fields),
        "documented_semantics": sum(
            f["semantic_status"] == "documented" for f in fields
        ),
        "unknown_semantics": sum(f["semantic_status"] == "unknown" for f in fields),
        "typed_read": "generic field access for individually indexed fields; ranges remain raw",
        "parser_write_verified": sum(f["write_status"] == "verified" for f in fields),
        "note": "Entry count includes groups, aliases and chunks; not a format coverage percentage.",
    }
    outputs = {
        root / "schema/rpp/generated/runtime.json": encode(runtime),
        root / "schema/rpp/generated/docdata.json": encode(
            {"meta": meta, "sections": sections, "structure": data["structure"]}
        ),
        root / "schema/rpp/generated/coverage.json": encode(coverage),
    }
    # During the contract phase packages need not have migrated yet.
    targets = [
        root / "packages/reaper-parser/src/reaper_parser/data/rpp_schema.json",
        root / "packages/reacli/src/rac/data/knowledge/rpp_schema.json",
    ]
    if not (root / "packages/reacli").exists():
        targets[1] = root / "src/rac/data/knowledge/rpp_schema.json"
    for target in targets:
        if target.parent.exists():
            outputs[target] = encode(runtime)
    if (root / "apps/reaperdoc").exists():
        outputs[root / "apps/reaperdoc/generated.json"] = encode(
            {"meta": meta, "sections": sections, "structure": data["structure"]}
        )
    return outputs


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    a = p.parse_args()
    stale = []
    for path, text in products().items():
        if a.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    if stale:
        raise SystemExit("Stale generated files: " + ", ".join(stale))
    print("Schema consumers match" if a.check else "Schema consumers generated")


if __name__ == "__main__":
    main()
