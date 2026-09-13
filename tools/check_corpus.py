"""Local corpus conformance and repeatable baseline; reports no performance claims."""

import argparse, hashlib, json, statistics, time, tracemalloc
from pathlib import Path
from reaper_parser import parse


def main():
    p = argparse.ArgumentParser()
    p.add_argument("corpus", type=Path)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    paths = sorted(
        f for f in a.corpus.rglob("*") if f.suffix.lower() in {".rpp", ".rpp-bak"}
    )
    result = {
        "files": len(paths),
        "roundtrip": 0,
        "assembled_roundtrip": 0,
        "failures": [],
        "timings_seconds": {},
    }
    values = {key: [] for key in ["parse", "traverse", "lookup", "patch", "serialize"]}
    tracemalloc.start()
    for path in paths:
        try:
            raw = path.read_bytes()
            start = time.perf_counter()
            doc = parse(path)
            values["parse"].append(time.perf_counter() - start)
            result["roundtrip"] += doc.text().encode("utf8", "surrogateescape") == raw
            doc.touch()
            result["assembled_roundtrip"] += (
                doc.text().encode("utf8", "surrogateescape") == raw
            )
            start = time.perf_counter()
            for track in doc.project.tracks:
                list(track.fields())
                for item in track.items:
                    list(item.fields())
                    for take in item.takes:
                        list(take.fields())
            values["traverse"].append(time.perf_counter() - start)
            start = time.perf_counter()
            for track in doc.project.tracks:
                for _ in range(10):
                    track.name
            values["lookup"].append(time.perf_counter() - start)
            start = time.perf_counter()
            if doc.project.tracks:
                doc.project.tracks[0].name = "Corpus probe"
            values["patch"].append(time.perf_counter() - start)
            start = time.perf_counter()
            parse(doc.text())
            values["serialize"].append(time.perf_counter() - start)
        except Exception as e:
            result["failures"].append(
                {
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "error": str(e),
                }
            )
    result["peak_bytes"] = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    result["timings_seconds"] = {
        key: {"sum": sum(v), "median": statistics.median(v) if v else None}
        for key, v in values.items()
    }
    result["note"] = (
        "Local related corpus, one instrumented pass; serialize includes reparse. Not a comparative speed claim."
    )
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if (
        result["failures"]
        or result["roundtrip"] != len(paths)
        or result["assembled_roundtrip"] != len(paths)
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
