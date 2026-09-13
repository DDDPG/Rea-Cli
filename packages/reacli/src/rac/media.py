"""Explicit source audio, isolated host rendering and import. Audio dependencies are optional."""

from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path, PureWindowsPath
import subprocess
from typing import Any


class MediaError(RuntimeError):
    def __init__(self, code, message, manifest_path=None):
        super().__init__(message)
        self.code = code
        self.manifest_path = manifest_path


@dataclass
class AudioData:
    samples: Any
    sample_rate: int
    metadata: dict


@dataclass
class MediaResult:
    path: Path
    manifest_path: Path
    metadata: dict
    proof: Any = None


def _audio():
    try:
        import numpy as np
        import soundfile as sf
    except ImportError as exc:
        raise MediaError(
            "missing_dependency", "Install reacli[audio] to use audio interfaces"
        ) from exc
    return np, sf


def _hash(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for data in iter(lambda: f.read(1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()


def _versions():
    import rac, reaper_parser
    from reaper_parser import schema

    meta = schema.load()["meta"]
    return {
        "rac": rac.__version__,
        "parser": reaper_parser.__version__,
        "schema": meta["schema_version"],
        "schema_sha256": meta["schema_sha256"],
    }


def _resolve(value, project=None, path_map=None):
    text = str(value).replace("\\", "/")
    matches = []
    for old, new in (path_map or {}).items():
        prefix = str(old).replace("\\", "/").rstrip("/")
        if text == prefix or text.startswith(prefix + "/"):
            matches.append(Path(new) / text[len(prefix) :].lstrip("/"))
    if len(matches) > 1:
        raise MediaError("ambiguous_media", f"Multiple mappings match {value}")
    if matches:
        path = matches[0]
    else:
        path = Path(text).expanduser()
        if PureWindowsPath(str(value)).is_absolute() and not path.is_absolute():
            raise MediaError(
                "missing_media",
                f"Foreign absolute path requires an explicit mapping: {value}",
            )
        if not path.is_absolute():
            if project is None:
                raise MediaError(
                    "missing_project", "A project path is required for relative media"
                )
            path = Path(project).resolve().parent / path
    path = path.expanduser().resolve()
    if not path.is_file():
        raise MediaError("missing_media", f"Media does not exist: {path}")
    return path


def read_source(source, *, project=None, path_map=None) -> AudioData:
    """Read unprocessed samples as float32 (frames, channels), never resample or downmix.

    A Take/Source can supply its document path. A MediaResult retains rendered lineage.
    SECTION and MIDI require explicit host rendering, not a guessed offline transformation.
    """
    identifiers = {}
    level = "source"
    lineage = None
    if isinstance(source, MediaResult):
        level = source.metadata.get("level", "source")
        lineage = str(source.manifest_path)
        source = source.path
    elif hasattr(source, "document"):
        project = project or source.document.source_path
        identifiers = {"take_guid": getattr(source, "guid", None)}
        for track in source.document.project.tracks:
            for item in track.items:
                if item.node is source.node:
                    identifiers.update(track_guid=track.guid, item_guid=item.guid)
                    break
        if hasattr(source, "source"):
            source = source.source
        if source is None or source.type in {"MIDI", "SECTION", "RPP_PROJECT"}:
            raise MediaError(
                "unsupported_source", "This source requires host interpretation"
            )
        if source.file_path is None:
            raise MediaError("missing_media", "Source has no FILE reference")
        source = source.file_path
    path = _resolve(source, project, path_map)
    np, sf = _audio()
    try:
        samples, sr = sf.read(path, dtype="float32", always_2d=True)
    except (RuntimeError, ValueError) as exc:
        raise MediaError("decode_failed", str(exc)) from exc
    return AudioData(
        samples,
        sr,
        {
            "level": level,
            "path": str(path),
            "sha256": _hash(path),
            "sample_rate": sr,
            "channels": samples.shape[1],
            "frames": len(samples),
            "dtype": "float32",
            "layout": "frames,channels",
            "time_range": [0, len(samples) / sr],
            "identifiers": identifiers,
            "project_sha256": _hash(project)
            if project and Path(project).is_file()
            else None,
            "lineage": lineage,
            "versions": _versions(),
        },
    )


def _write(path, data):
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf8"
    )


def _prepare(project, work_dir, path_map):
    from rac.rpp import parse
    from rac.rpp.patch import set_value

    original = Path(project).resolve()
    if not original.is_file():
        raise MediaError("missing_project", str(original))
    root = Path(work_dir).resolve()
    root.mkdir(parents=True, exist_ok=False)
    manifest = {
        "input_project": {"path": str(original), "sha256": _hash(original)},
        "media": [],
        "versions": _versions(),
        "checks": {"structure": False, "fields": False, "host": False, "audio": False},
        "status": "running",
    }
    _write(root / "manifest.json", manifest)
    try:
        doc = parse(original)
        for chunk in doc.root.iter_chunks("SOURCE"):
            for line in chunk.find_lines("FILE"):
                if not line.values:
                    raise MediaError("missing_media", "Empty FILE reference")
                path = _resolve(line.values[0], original, path_map)
                manifest["media"].append({"path": str(path), "sha256": _hash(path)})
                set_value(doc, line, 0, str(path))
        clone = doc.save(root / "input.rpp")
        manifest["checks"]["structure"] = True
        _write(root / "manifest.json", manifest)
        return root, clone, manifest
    except Exception as exc:
        raise _failure(root, manifest, exc) from exc


def _script(path, body):
    from rac.resources import read_text
    from rac.luagen.generator import BODY_PAT, validate

    text = BODY_PAT.sub(
        lambda _: "local function body()\n" + body + "\nend\n-- " + "=" * 75,
        read_text("lua/entry.lua"),
    )
    path.write_text(text, encoding="utf8")
    validate(path)
    return path


def _run(root, clone, body, save_as, reaper_bin, timeout):
    from rac.runner import run

    script = _script(root / "operation.lua", body)
    proof = run(
        clone,
        script,
        save_as=save_as,
        resource=root / "resource",
        run_root=root / "runs",
        state_dir=root / "state",
        reaper_bin=reaper_bin,
        timeout=timeout,
    )
    _write(root / "proof.json", proof.to_dict())
    if not proof.ok:
        raise MediaError(proof.reason_code, str(proof.error), root / "manifest.json")
    if not isinstance(proof.result, dict) or not proof.result.get("ok"):
        raise MediaError("operation_failed", str(proof.result), root / "manifest.json")
    if not save_as.is_file():
        raise MediaError(
            "save_failed", "Host did not save output", root / "manifest.json"
        )
    return proof


def _failure(root, manifest, exc):
    code = (
        exc.code
        if isinstance(exc, MediaError)
        else "timeout"
        if isinstance(exc, subprocess.TimeoutExpired)
        else "operation_failed"
    )
    manifest.update(status="error", error={"code": code, "message": str(exc)})
    _write(root / "manifest.json", manifest)
    return MediaError(code, str(exc), root / "manifest.json")


def render(
    project,
    *,
    work_dir,
    sample_rate=48000,
    channels=2,
    time_range=None,
    tail_seconds=0,
    track_guids=None,
    path_map=None,
    reaper_bin=None,
    timeout=60,
) -> MediaResult:
    """Render master output, optionally retaining the send/folder dependency component.

    Track selection is not an isolated stem. Original track mute/solo state is retained.
    The output and all host operations live in a newly created work directory.
    """
    from rac.luagen.generator import _lua_literal as lua
    from rac.environment import run_bounded, resolve_executable
    from rac.runner import platform

    _audio()
    if (
        not isinstance(sample_rate, int)
        or sample_rate <= 0
        or not isinstance(channels, int)
        or channels < 1
    ):
        raise ValueError("Positive integer sample rate and channel count required")
    if (
        not math.isfinite(tail_seconds)
        or tail_seconds < 0
        or not math.isfinite(timeout)
        or timeout <= 0
    ):
        raise ValueError("Invalid tail or timeout")
    if time_range is not None and (
        len(time_range) != 2
        or not all(math.isfinite(v) for v in time_range)
        or not 0 <= time_range[0] < time_range[1]
    ):
        raise ValueError("Invalid time range")
    if track_guids is not None and (
        not track_guids or len(set(track_guids)) != len(track_guids)
    ):
        raise ValueError("Track GUIDs must be nonempty and unique")
    root, clone, manifest = _prepare(project, work_dir, path_map)
    try:
        output = root / "rendered.wav"
        saved = root / "render.rpp"
        body = """local tracks, edges, selected, plugins = {}, {}, {}, {}
for i=0,reaper.CountTracks(0)-1 do
 local tr=reaper.GetTrack(0,i); tracks[i+1]=tr; edges[tr]={}
 for fx=0,reaper.TrackFX_GetCount(tr)-1 do
  local _,name=reaper.TrackFX_GetFXName(tr,fx,"")
  plugins[#plugins+1]={track=reaper.GetTrackGUID(tr),name=name,offline=reaper.TrackFX_GetOffline(tr,fx),guid=reaper.TrackFX_GetFXGUID(tr,fx),version="unavailable"}
 end
end
for _,tr in ipairs(tracks) do
 local parent=reaper.GetParentTrack(tr)
 if parent then edges[tr][parent]=true;edges[parent][tr]=true end
 for j=0,reaper.GetTrackNumSends(tr,0)-1 do
  local dest=reaper.GetTrackSendInfo_Value(tr,0,j,"P_DESTTRACK")
  if dest and edges[dest] then edges[tr][dest]=true;edges[dest][tr]=true end
 end
end
"""
        body += "local wanted=" + lua(track_guids) + "\n"
        body += """if wanted then
 for _,guid in ipairs(wanted) do
  local found=false
  for _,tr in ipairs(tracks) do if reaper.GetTrackGUID(tr)==guid then selected[tr]=true;found=true end end
  if not found then error("Unknown track GUID: "..guid) end
 end
 local changed=true
 while changed do
  changed=false
  for tr in pairs(selected) do for adjacent in pairs(edges[tr]) do if not selected[adjacent] then selected[adjacent]=true;changed=true end end end
 end
 for _,tr in ipairs(tracks) do if not selected[tr] then reaper.SetMediaTrackInfo_Value(tr,"B_MUTE",1) end end
else for _,tr in ipairs(tracks) do selected[tr]=true end end
local included={}
for _,tr in ipairs(tracks) do if selected[tr] then included[#included+1]=reaper.GetTrackGUID(tr) end end
"""
        config = {
            "RENDER_SETTINGS": 0,
            "RENDER_SRATE": sample_rate,
            "RENDER_CHANNELS": channels,
            "RENDER_BOUNDSFLAG": 0 if time_range else 1,
            "RENDER_TAILFLAG": 1 if tail_seconds else 0,
            "RENDER_TAILMS": tail_seconds * 1000,
            "RENDER_DITHER": 0,
            "RENDER_NORMALIZE": 0,
            "RENDER_ADDTOPROJ": 0,
        }
        if time_range:
            config.update(RENDER_STARTPOS=time_range[0], RENDER_ENDPOS=time_range[1])
        for key, value in config.items():
            body += f"reaper.GetSetProjectInfo(0,{lua(key)},{lua(value)},true)\n"
        for key, value in {
            "RENDER_FILE": str(root),
            "RENDER_PATTERN": "rendered",
            "RENDER_FORMAT": "ZXZhdxAAAA==",
        }.items():
            body += f"reaper.GetSetProjectInfo_String(0,{lua(key)},{lua(value)},true)\n"
        for key, value in config.items():
            body += f'assert(math.abs(reaper.GetSetProjectInfo(0,{lua(key)},0,false)-{lua(value)})<0.000001,"Render setting readback failed: {key}")\n'
        body += "RUN.result={ok=true,host=reaper.GetAppVersion(),tracks=included,plugins=plugins}\n"
        proof = _run(root, clone, body, saved, reaper_bin, timeout)
        manifest["checks"]["host"] = True
        command = platform.build_command(
            resolve_executable(platform.find_reaper(reaper_bin)),
            "-renderproject",
            str(saved),
            "-nosplash",
            "-ignoreerrors",
            resource=root / "resource",
        )
        try:
            proc = run_bounded(command, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            (root / "render.log").write_text("Timed out: " + str(exc), encoding="utf8")
            raise
        (root / "render.log").write_text(proc.stdout + proc.stderr, encoding="utf8")
        if proc.returncode:
            raise MediaError("render_failed", f"REAPER exited {proc.returncode}")
        if not output.is_file():
            raise MediaError("output_missing", "REAPER produced no rendered.wav")
        audio = read_source(output)
        np, _ = _audio()
        if (
            audio.sample_rate != sample_rate
            or audio.samples.shape[1] != channels
            or not len(audio.samples)
            or not np.isfinite(audio.samples).all()
        ):
            raise MediaError(
                "audio_invalid",
                "Rendered rate/channels/sample data do not match request",
            )
        if time_range and abs(
            len(audio.samples) / sample_rate
            - (time_range[1] - time_range[0] + tail_seconds)
        ) > max(0.02, 2 / sample_rate):
            raise MediaError(
                "audio_invalid",
                "Rendered duration differs from requested range and tail",
            )
        metadata = {
            **audio.metadata,
            "level": "rendered",
            "time_range": list(time_range)
            if time_range
            else [0, len(audio.samples) / sample_rate],
            "tail_seconds": tail_seconds,
            "scope": "dependency-component-through-master" if track_guids else "master",
            "requested_tracks": track_guids,
            "included_tracks": proof.result["tracks"],
        }
        manifest.update(
            status="ok",
            output=metadata,
            host=proof.result["host"],
            plugins=proof.result["plugins"],
            render_config=config,
            proof="proof.json",
        )
        manifest["checks"].update(fields=True, audio=True)
        _write(root / "manifest.json", manifest)
        return MediaResult(output, root / "manifest.json", metadata, proof)
    except Exception as exc:
        raise _failure(root, manifest, exc) from exc


def import_audio(
    project,
    audio,
    *,
    work_dir,
    name="Processed audio",
    position=0,
    path_map=None,
    reaper_bin=None,
    timeout=60,
) -> MediaResult:
    """Add a new track and item using the host; save a new project and verify it."""
    from rac.luagen.generator import _lua_literal as lua
    from rac.rpp import parse

    if not math.isfinite(position) or position < 0:
        raise ValueError("Position must be finite and nonnegative")
    data = read_source(audio)
    path = Path(data.metadata["path"])
    np, _ = _audio()
    if not len(data.samples) or not np.isfinite(data.samples).all():
        raise MediaError("audio_invalid", "Cannot import empty or nonfinite audio")
    root, clone, manifest = _prepare(project, work_dir, path_map)
    try:
        saved = root / "saved.rpp"
        body = f"""local index=reaper.CountTracks(0)
reaper.InsertTrackAtIndex(index,true)
local track=reaper.GetTrack(0,index)
assert(track,"Track creation failed")
reaper.GetSetMediaTrackInfo_String(track,"P_NAME",{lua(name)},true)
local item=reaper.AddMediaItemToTrack(track)
local take=reaper.AddTakeToMediaItem(item)
local source=reaper.PCM_Source_CreateFromFile({lua(str(path))})
assert(source,"Media source could not be loaded")
reaper.SetMediaItemTake_Source(take,source)
reaper.SetMediaItemInfo_Value(item,"D_FADEINLEN",0)
reaper.SetMediaItemInfo_Value(item,"D_FADEOUTLEN",0)
reaper.SetMediaItemInfo_Value(item,"D_FADEINLEN_AUTO",-1)
reaper.SetMediaItemInfo_Value(item,"D_FADEOUTLEN_AUTO",-1)
reaper.SetMediaItemInfo_Value(item,"D_POSITION",{lua(position)})
reaper.SetMediaItemInfo_Value(item,"D_LENGTH",{lua(len(data.samples) / data.sample_rate)})
local _,iguid=reaper.GetSetMediaItemInfo_String(item,"GUID","",false)
local _,tguid=reaper.GetSetMediaItemTakeInfo_String(take,"GUID","",false)
RUN.result={{ok=true,host=reaper.GetAppVersion(),track_guid=reaper.GetTrackGUID(track),item_guid=iguid,take_guid=tguid}}
"""
        proof = _run(root, clone, body, saved, reaper_bin, timeout)
        doc = parse(saved)
        tracks = [t for t in doc.project.tracks if t.guid == proof.result["track_guid"]]
        if len(tracks) != 1 or tracks[0].name != name or len(tracks[0].items) != 1:
            raise MediaError("verification_failed", "Saved track differs")
        item = tracks[0].items[0]
        take = item.takes[0]
        if (
            abs(item.position - position) > 1e-8
            or abs(item.length - len(data.samples) / data.sample_rate) > 1e-6
        ):
            raise MediaError("verification_failed", "Saved timing differs")
        if _resolve(take.source.file_path, saved) != path:
            raise MediaError("verification_failed", "Saved media reference differs")
        metadata = {
            "level": "project",
            "path": str(saved),
            "sha256": _hash(saved),
            "track_guid": tracks[0].guid,
            "item_guid": item.guid,
            "take_guid": take.guid,
            "time_range": [position, position + item.length],
        }
        manifest.update(
            status="ok",
            output=metadata,
            imported_audio=data.metadata,
            proof="proof.json",
            host=proof.result["host"],
        )
        manifest["checks"].update(fields=True, host=True, audio=True)
        _write(root / "manifest.json", manifest)
        return MediaResult(saved, root / "manifest.json", metadata, proof)
    except Exception as exc:
        raise _failure(root, manifest, exc) from exc
