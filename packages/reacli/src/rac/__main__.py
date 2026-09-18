#!/usr/bin/env python3
"""reacli — REAPER project, scripting and audio verification tools

Usage: reacli <command> [options]

  rpp validate FILE                 Check RPP syntax and structure
  rpp diff BEFORE AFTER             Compare project semantics
  rpp get FILE QUERY                Query tracks, markers or track:N:KEY
  knowledge rpp KEY                 Look up an RPP field (for example track:VOLPAN)
  knowledge api NAME                Look up a ReaScript API signature
  resources --output DIR            Export Lua templates and a minimal project
  verify audio FILE --expect K=V    Check duration, level, frequency or loudness
  exec --project P --script S       Run a script; optionally --save-as OUTPUT
  pool exec --jobs JSON             Run independent jobs with isolated workers
  init [--resource DIR]             Initialize dedicated REAPER resources
  doctor [--json] [--smoke|--render] Check dependencies and optional live behavior
  --version                         Show the installed version

Python namespace: rac. The rac command is an alias for reacli.
Exit codes: 0 success; 2 validation/data or argparse error; 3 retriable execution
failure; 4 environment/dispatch error. See docs/api.md for command-specific details.
"""
import json
import sys
from pathlib import Path

from rac.rpp import parse  # noqa: E402
from rac.rpp.parser import RPPParseError  # noqa: E402
from rac.environment import EnvironmentError
from rac.runner.pool import PoolBlocked


def _json_out(obj, code=0):
    print(json.dumps(obj, ensure_ascii=False))
    return code


def cmd_rpp_validate(args):
    f = Path(args[0])
    try:
        doc = parse(f)
    except RPPParseError as e:
        return _json_out({"ok": False, "error": str(e)}, 2)
    return _json_out({"ok": True, "tracks": len(doc.tracks()),
                      "markers": len(doc.markers())})


def cmd_rpp_diff(args):
    from rac.verify.semantics import semantic_diff
    a, b = parse(Path(args[0])), parse(Path(args[1]))
    diff = semantic_diff(a, b)
    # Semantic differences are a validation failure, not a successful comparison.
    return _json_out({"ok": len(diff) == 0, "mode": "semantic",
                      "identical": len(diff) == 0,
                      "diff": diff[:200], "diff_count": len(diff)},
                     0 if len(diff) == 0 else 2)


def cmd_rpp_get(args):
    doc = parse(Path(args[0]))
    q = args[1]
    if q == "tracks":
        out = []
        for i, tr in enumerate(doc.tracks()):
            name = tr.find_line("NAME")
            vol = tr.find_line("VOLPAN")
            out.append({"index": i,
                        "name": name.values[0] if name and name.values else "",
                        "volume": vol.values[0] if vol and vol.values else None,
                        "items": len(tr.find_chunks("ITEM"))})
        return _json_out({"ok": True, "tracks": out})
    if q == "markers":
        return _json_out({"ok": True, "markers": [
            {"index": m.values[0], "pos": m.values[1],
             "name": m.values[2] if len(m.values) > 2 else ""}
            for m in doc.markers()]})
    if q.startswith("track:"):
        # track:N:KEY — 取第 N 轨 KEY 行的 values
        _, idx_s, key = q.split(":")
        line = doc.tracks()[int(idx_s)].find_line(key)
        return _json_out({"ok": True, "values": line.values if line else None})
    return _json_out({"ok": False, "error": f"unknown query {q!r}"}, 4)


def cmd_verify_audio(args):
    from rac.verify import expect_audio
    from rac.verify.audio import AudioExpectError
    f = args[0]
    kv_args = [a for a in args[1:] if a != "--expect"]  # cookbook 风格 --expect k=v 兼容
    expects = dict(kv.split("=", 1) for kv in kv_args)
    unknown = set(expects) - {"duration", "tol", "not_silent", "dominant_freq",
                              "freq_tol", "lufs", "lufs_tol", "no_clipping"}
    if unknown:
        raise ValueError(f"Unknown audio expectations: {sorted(unknown)}")
    try:
        e = expect_audio(f)
        if "duration" in expects:
            e.duration(float(expects["duration"]), tol=float(expects.get("tol", 0.1)))
        if "not_silent" in expects:
            e.not_silent()
        if "dominant_freq" in expects:
            e.dominant_freq(float(expects["dominant_freq"]),
                            tol=float(expects.get("freq_tol", 10)))
        if "lufs" in expects:
            e.lufs(float(expects["lufs"]), tol=float(expects.get("lufs_tol", 1.5)))
        if "no_clipping" in expects:
            e.no_clipping()
    except AudioExpectError as ex:
        return _json_out({"ok": False, "error": str(ex)}, 2)
    out = {"ok": True, "file": f, "rms": round(e.rms, 6),
           "duration": round(e.frames / e.sr, 3)}
    return _json_out(out)


def cmd_exec(args):
    import argparse
    p = argparse.ArgumentParser(prog="reacli exec")
    p.add_argument("--project", required=True)
    p.add_argument("--script", required=True)
    p.add_argument("--save-as")
    p.add_argument("--timeout", type=float, default=60)
    p.add_argument("--reaper-bin")
    p.add_argument("--resource")
    p.add_argument("--run-root", default="runs")
    a = p.parse_args(args)
    from rac.runner import run
    proof = run(a.project, a.script, timeout=a.timeout, save_as=a.save_as,
                reaper_bin=a.reaper_bin, resource=a.resource, run_root=a.run_root)
    out = proof.to_dict()
    out.pop("state", None)  # stdout 有界: state 大了走 run_dir/proof.json
    return _json_out(out, 0 if proof.ok else (3 if proof.retriable else 2))


def cmd_pool_exec(args):
    import argparse
    p = argparse.ArgumentParser(prog="reacli pool exec")
    p.add_argument("--jobs", required=True, help="jobs.json: [{project,script,save_as?}]")
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--timeout", type=float, default=120)
    import tempfile
    p.add_argument("--workers-root", default=None)
    p.add_argument("--seed-config", default=None)
    a = p.parse_args(args)
    from rac.runner.pool import MAX_JOBS, Pool, PoolBlocked
    jobs_path = Path(a.jobs).expanduser().resolve()
    if jobs_path.stat().st_size > 4 * 1024 * 1024:
        raise PoolBlocked("blocked:jobs_file_too_large (maximum 4 MiB)")
    jobs = json.loads(jobs_path.read_text(encoding="utf-8"))
    if not isinstance(jobs, list) or len(jobs) > MAX_JOBS:
        raise PoolBlocked(f"blocked:too_many_jobs (maximum {MAX_JOBS})")
    if a.workers_root:
        proofs = Pool(a.workers_root, a.workers, seed_config_dir=a.seed_config).map(jobs, timeout=a.timeout)
    else:
        with tempfile.TemporaryDirectory(prefix="reacli_pool_") as root:
            proofs = Pool(root, a.workers, seed_config_dir=a.seed_config).map(jobs, timeout=a.timeout)
    out = [{"status": p_.status, "reason_code": p_.reason_code,
            "run_id": p_.run_id} for p_ in proofs]
    all_ok = all(p_.ok for p_ in proofs)
    return _json_out({"ok": all_ok, "results": out},
                     0 if all_ok else 2)


def cmd_knowledge(args):
    if not args:
        print("usage: rac knowledge rpp <KEY> | api <fn>", file=sys.stderr)
        return 4
    domain, query = args[0], " ".join(args[1:])
    if domain == "rpp":
        from rac.rpp import schema as rpp_schema
        if ":" in query:
            section, key = query.split(":", 1)
        else:
            section, key = "track", query
        meta = rpp_schema.key_meta(section, key)
        return _json_out({"ok": meta is not None, "entry": meta},
                         0 if meta else 2)
    if domain == "api":
        from rac.resources import read_text
        idx = json.loads(read_text("knowledge/api_index.json"))
        fn = idx["functions"].get(query)
        return _json_out({"ok": fn is not None, "entry": fn}, 0 if fn else 2)
    return _json_out({"ok": False, "error": f"unknown domain {domain}"}, 4)


def cmd_doctor(args):
    import argparse
    from rac.environment import doctor
    p = argparse.ArgumentParser(prog="reacli doctor", description="Check external dependencies; no installation")
    p.add_argument("--profile", choices=["offline", "lua", "runner", "full"], default="full")
    p.add_argument("--json", action="store_true")
    p.add_argument("--reaper-bin")
    p.add_argument("--resource")
    p.add_argument("--smoke", action="store_true", help="Execute generated Lua and save/reparse a temporary project")
    p.add_argument("--render", action="store_true", help="Also render and verify a 440 Hz WAV (implies --smoke)")
    p.add_argument("--work-dir", help="Retain smoke artifacts in a unique subdirectory here")
    p.add_argument("--timeout", type=float, default=60)
    a = p.parse_args(args)
    if (a.smoke or a.render) and a.profile in {"offline", "lua"}:
        p.error("--smoke/--render requires --profile runner or full")
    report = doctor(profile=a.profile, reaper_bin=a.reaper_bin, resource=a.resource)
    import reaper_parser
    from reaper_parser import schema
    report["ecosystem"] = {"parser_version": reaper_parser.__version__, **schema.load()["meta"]}
    if a.smoke or a.render:
        if report["ok"]:
            from rac.smoke import smoke_check
            check = smoke_check(reaper_bin=a.reaper_bin, seed_resource=a.resource,
                                render=a.render, timeout=a.timeout, work_dir=a.work_dir)
            report["checks"].append(check)
            report["ok"] = check["status"] == "ok"
        else:
            report["checks"].append({"name": "smoke", "status": "skipped", "detail": "Fix prerequisite errors first", "hint": ""})
    if a.json:
        return _json_out(report, 0 if report["ok"] else 4)
    for check in report["checks"]:
        print(f"[{check['status'].upper()}] {check['name']}: {check['detail']}")
        if check.get("hint") and check["status"] != "ok":
            print(f"  {check['hint']}")
    return 0 if report["ok"] else 4


def cmd_init(args):
    import argparse
    from rac.runner import platform
    p = argparse.ArgumentParser(prog="reacli init")
    p.add_argument("--resource")
    a = p.parse_args(args)
    if not (platform.IS_LINUX or platform.IS_MAC):
        raise EnvironmentError("REAPER resource initialization supports Linux and macOS")
    target = platform.ensure_resource(platform.resource_dir(a.resource))
    return _json_out({"ok": True, "resource": str(target), "ini": str(target / "reaper.ini")})


def cmd_resources(args):
    import argparse
    from rac.resources import export_resources
    p = argparse.ArgumentParser(prog="reacli resources")
    p.add_argument("--output", required=True)
    a = p.parse_args(args)
    return _json_out({"ok": True, "output": str(export_resources(a.output))})


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0 if argv else 4
    if argv[0] in ("--version", "-V"):
        from rac import __version__
        print(f"reacli {__version__} (import rac)")
        return 0
    cmd, args = argv[0], argv[1:]
    try:
        if cmd == "doctor":
            return cmd_doctor(args)
        if cmd == "init":
            return cmd_init(args)
        if cmd == "resources":
            return cmd_resources(args)
        if cmd == "rpp":
            sub = args[0] if args else ""
            if sub == "validate" and len(args) == 2:
                return cmd_rpp_validate(args[1:])
            if sub == "diff" and len(args) == 3:
                return cmd_rpp_diff(args[1:])
            if sub == "get" and len(args) == 3:
                return cmd_rpp_get(args[1:])
            print("usage: rac rpp validate|diff|get ...", file=sys.stderr)
            return 4
        if cmd == "verify" and args and args[0] == "audio":
            return cmd_verify_audio(args[1:])
        if cmd == "exec":
            return cmd_exec(args)
        if cmd == "pool" and args and args[0] == "exec":
            return cmd_pool_exec(args[1:])
        if cmd == "knowledge":
            return cmd_knowledge(args)
        print(f"unknown command: {cmd}", file=sys.stderr)
        return 4
    except (EnvironmentError, OSError, PoolBlocked) as e:
        return _json_out({"ok": False, "error": f"{type(e).__name__}: {e}"}, 4)
    except (RPPParseError, RecursionError, IndexError, KeyError, ValueError, TypeError) as e:
        # Data failures use the same JSON output channel as successful results.
        return _json_out({"ok": False, "error": f"{type(e).__name__}: {e}"}, 2)


if __name__ == "__main__":
    sys.exit(main())
