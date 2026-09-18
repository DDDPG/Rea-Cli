"""Create and save one track using an isolated REAPER configuration.

Run: python examples/create_project.py /absolute/path/to/new-output-directory
"""
import argparse
import json
from rac.luagen import generate
from rac.resources import export_resources
from rac.rpp import parse
from rac.runner import run
from rac.verify import expect


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_directory")
    args = parser.parse_args()
    output = export_resources(args.output_directory)
    script = generate({"ops": [
        {"op": "track.create", "args": [0, "Vocal"]},
        {"op": "track.set_volume_db", "args": [0, -6.0]},
    ]}, output / "create.lua")
    proof = run(output / "minimal.rpp", script, save_as=output / "created.rpp",
                resource=output / "resource", run_root=output / "runs")
    if proof.ok:
        expect(parse(output / "created.rpp")).track_count(1).track(0) \
            .name("Vocal").volume(10 ** (-6 / 20))
    print(json.dumps(proof.to_dict(), indent=2, ensure_ascii=False))
    raise SystemExit(0 if proof.ok else 2)


if __name__ == "__main__":
    main()
