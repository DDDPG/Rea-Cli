-- Custom ReaScript extension executed by rac; not additional Python API methods.
-- Folder depth, multiple takes and pan envelopes need this lower-level layer.
local function track(index) return assert(reaper.GetTrack(0, index)) end
local function item(index) return assert(reaper.GetTrackMediaItem(track(index), 0)) end

-- Optional, real build-state projects for a screenshot walkthrough (no audio).
local step_number = 0
demo_checkpoint = function(label, fx_track)
  if not DEMO_STEPS then return end
  for key in pairs(RUN.result or {}) do assert(not key:match("_error$"), key) end
  for i=0,reaper.CountTracks(0)-1 do
    reaper.SetMediaTrackInfo_Value(track(i), "I_HEIGHTOVERRIDE", 62)
  end
  reaper.GetSet_ArrangeView2(0, true, 0, 0, 0, 17)
  reaper.TrackList_AdjustWindows(false)
  reaper.UpdateArrange()
  step_number = step_number + 1
  local filename = string.format("%03d-%s.rpp", step_number, label)
  local path = DEMO_ROOT .. "/steps/" .. filename
  reaper.Main_SaveProjectEx(0, path, 0)
  local saved = assert(io.open(path, "r"), "Checkpoint was not saved: " .. filename)
  saved:close()
  local manifest = assert(io.open(DEMO_ROOT .. "/steps/index.jsonl", "a"))
  manifest:write(json_encode({file=filename, label=label,
    tracks=reaper.CountTracks(0), items=reaper.CountMediaItems(0), fx_track=fx_track}), "\n")
  manifest:close()
end

local function parameter(tr, fx, name)
  -- First exact match: ReaComp/ReaVerbate also have REAPER's host Wet control.
  for p=0,reaper.TrackFX_GetNumParams(tr, fx)-1 do
    local _, found = reaper.TrackFX_GetParamName(tr, fx, p, "")
    if found == name then return p end
  end
  error("Missing FX parameter: " .. name)
end

local function display_value(tr, fx, name)
  local _, value = reaper.TrackFX_GetFormattedParamValue(tr, fx, parameter(tr, fx, name), "")
  return assert(tonumber(value), "Non-numeric FX parameter: " .. name .. " = " .. value)
end

local function set_raw(tr, fx, name, value)
  assert(reaper.TrackFX_SetParam(tr, fx, parameter(tr, fx, name), value))
end

local function set_display(tr, fx, name, target)
  -- Room size has a plugin-specific scale; use its displayed value, not guessed units.
  local p, lo, hi = parameter(tr, fx, name), 0, 1
  for _=1,32 do
    local mid = (lo + hi) / 2
    assert(reaper.TrackFX_SetParamNormalized(tr, fx, p, mid))
    local current = display_value(tr, fx, name)
    if math.abs(current - target) < .000001 then return end
    if current < target then lo = mid else hi = mid end
  end
  error("Unable to set FX parameter: " .. name)
end

local function require_fx(tr, name)
  local fx = reaper.TrackFX_GetByName(tr, name, false)
  assert(fx >= 0, "Missing built-in " .. name)
  assert(reaper.TrackFX_GetEnabled(tr, fx) and not reaper.TrackFX_GetOffline(tr, fx))
  return fx
end

local function build_effects()
  -- Track inserts use existing rac FX operations. Master/EQ-specific controls
  -- use the native API through the same rac runner.
  assert(std_fx.add_by_name(5, "ReaEQ (Cockos)").ok)
  local eq = require_fx(track(5), "ReaEQ (Cockos)")
  demo_checkpoint("melody-insert-reaeq", 5)
  assert(reaper.TrackFX_SetEQParam(track(5), eq, 0, 0, 0, 100, false))
  local bands = {}
  for p=0,reaper.TrackFX_GetNumParams(track(5), eq)-1 do
    local ok, kind, index = reaper.TrackFX_GetEQParam(track(5), eq, p)
    if ok and kind >= 0 then bands[kind .. ":" .. index] = {kind, index} end
  end
  for _, band in pairs(bands) do
    assert(reaper.TrackFX_SetEQBandEnabled(track(5), eq, band[1], band[2], band[1] == 0 and band[2] == 0))
  end
  demo_checkpoint("melody-lowcut-100hz", 5)

  assert(std_fx.add_by_name(4, "ReaVerbate (Cockos)").ok)
  local verb = require_fx(track(4), "ReaVerbate (Cockos)")
  demo_checkpoint("chords-insert-reaverbate", 4)
  set_display(track(4), verb, "Room size", 90)
  set_raw(track(4), verb, "Dampening", .2)
  set_raw(track(4), verb, "Wet", 10 ^ (-12 / 20))
  set_raw(track(4), verb, "Dry", 1)
  demo_checkpoint("chords-long-reverb", 4)

  assert(std_fx.add_by_name(3, "ReaComp (Cockos)").ok)
  local comp = require_fx(track(3), "ReaComp (Cockos)")
  demo_checkpoint("bass-insert-reacomp", 3)
  set_raw(track(3), comp, "Threshold", 10 ^ (-15 / 20))
  demo_checkpoint("bass-threshold-minus15db", 3)
  set_raw(track(3), comp, "Wet", 10 ^ (3 / 20))
  set_raw(track(3), comp, "Dry", 0)
  set_raw(track(3), comp, "Auto Make Up Gain", 0)
  demo_checkpoint("bass-makeup-plus3db", 3)

  local master = reaper.GetMasterTrack(0)
  assert(reaper.TrackFX_AddByName(master, "ReaLimit (Cockos)", false, -1) >= 0)
  local limit = require_fx(master, "ReaLimit (Cockos)")
  demo_checkpoint("master-insert-realimit", "master")
  set_display(master, limit, "Threshold", -4.5)
  demo_checkpoint("master-threshold-minus4-5db", "master")
  set_display(master, limit, "Ceiling", -1)
  demo_checkpoint("master-ceiling-minus1db", "master")
end

local function inspect_effects()
  local eq = require_fx(track(5), "ReaEQ (Cockos)")
  local hz
  for p=0,reaper.TrackFX_GetNumParams(track(5), eq)-1 do
    local ok, kind, index, param = reaper.TrackFX_GetEQParam(track(5), eq, p)
    if ok and kind == 0 and index == 0 and param == 0 then
      assert(reaper.TrackFX_GetEQBandEnabled(track(5), eq, 0, 0))
      local _, value = reaper.TrackFX_GetFormattedParamValue(track(5), eq, p, "")
      hz = assert(tonumber(value))
    end
  end
  assert(hz, "Missing enabled high-pass band")
  local comp = require_fx(track(3), "ReaComp (Cockos)")
  local verb = require_fx(track(4), "ReaVerbate (Cockos)")
  local master = reaper.GetMasterTrack(0)
  local limit = require_fx(master, "ReaLimit (Cockos)")
  return {enabled=4, melody_lowcut_hz=hz,
    bass_threshold_db=display_value(track(3), comp, "Threshold"),
    bass_makeup_db=display_value(track(3), comp, "Wet"),
    bass_auto_makeup=reaper.TrackFX_GetParam(track(3), comp, parameter(track(3), comp, "Auto Make Up Gain")),
    reverb_room_size=display_value(track(4), verb, "Room size"),
    reverb_wet_db=display_value(track(4), verb, "Wet"),
    master_threshold_db=display_value(master, limit, "Threshold")}
end

local function build_details()
  reaper.SetMediaTrackInfo_Value(track(0), "I_FOLDERDEPTH", 1)
  reaper.SetMediaTrackInfo_Value(track(2), "I_FOLDERDEPTH", -1)
  for i=0,6 do reaper.SetMediaTrackInfo_Value(track(i), "I_HEIGHTOVERRIDE", 62) end

  demo_checkpoint("rhythm-folder")

  assert(std_take.set_name(4, 0, "Warm triads").ok)
  local first = reaper.GetActiveTake(item(4))
  local second = assert(reaper.AddTakeToMediaItem(item(4)))
  -- CreateNewMIDIItemInProj initializes a usable MIDI source; an empty
  -- PCM_Source_CreateFromType("MIDI") alone cannot accept notes on REAPER 7.48.
  local temporary = assert(reaper.CreateNewMIDIItemInProj(track(4), 0, 16, false))
  local temporary_take = reaper.GetActiveTake(temporary)
  local source = reaper.GetMediaItemTake_Source(temporary_take)
  reaper.SetMediaItemTake_Source(temporary_take, reaper.PCM_Source_CreateFromType("MIDI"))
  reaper.SetMediaItemTake_Source(second, source)
  reaper.DeleteTrackMediaItem(track(4), temporary)
  local _, count = reaper.MIDI_CountEvts(first)
  for i=0,count-1 do
    local ok, selected, muted, startppq, endppq, chan, pitch, vel = reaper.MIDI_GetNote(first, i)
    assert(ok)
    assert(reaper.MIDI_InsertNote(second, false, false, startppq, endppq, chan, pitch + 12, vel, true))
  end
  reaper.MIDI_Sort(second)
  reaper.GetSetMediaItemTakeInfo_String(second, "P_NAME", "Bright octave / alternate", true)
  reaper.SetActiveTake(first)
  reaper.SetMediaItemInfo_Value(item(4), "B_ALLTAKESPLAY", 0)
  assert(std_take.set_name(5, 0, "16 notes / built-in ReaSynth").ok)

  demo_checkpoint("chords-alternate-take")

  assert(std_env.get_or_create(3, "Pan").ok)
  local pan = assert(reaper.GetTrackEnvelopeByName(track(3), "Pan"))
  reaper.DeleteEnvelopePointRange(pan, -1, 1000)
  for _, point in ipairs({{0, -.3}, {8, .3}, {16, 0}}) do
    assert(reaper.InsertEnvelopePoint(pan, point[1], point[2], 0, 0, false, true))
  end
  reaper.Envelope_SortPoints(pan)
  -- Read automation, not write/touch. The send is intentionally a quiet dry parallel bus.
  reaper.SetMediaTrackInfo_Value(track(3), "I_AUTOMODE", 1)
  reaper.SetMediaTrackInfo_Value(track(4), "I_AUTOMODE", 1)
  reaper.SetTrackSendInfo_Value(track(4), 0, 0, "D_VOL", .25)
  demo_checkpoint("bass-pan-envelope-and-send-level")
  reaper.GetSet_LoopTimeRange(true, false, 0, 16, false)
  reaper.GetSetProjectInfo(0, "RENDER_BOUNDSFLAG", 0, true)
  reaper.GetSetProjectInfo(0, "RENDER_STARTPOS", 0, true)
  reaper.GetSetProjectInfo(0, "RENDER_ENDPOS", 24, true)
  reaper.GetSetProjectInfo(0, "RENDER_TAILFLAG", 0, true)
  reaper.GetSetProjectInfo(0, "RENDER_CHANNELS", 2, true)
  reaper.GetSetProjectInfo(0, "RENDER_SRATE", 22050, true)
  reaper.GetSetProjectInfo_String(0, "RENDER_FORMAT", "ZXZhdxAAAA==", true)
  reaper.GetSetProjectInfo_String(0, "RENDER_FILE", DEMO_ROOT, true)
  reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", "Show-Session", true)
  reaper.GetSetProjectNotes(0, true, "Rea-Cli show demo | 120 BPM | 8 bars\n"
    .. "Press Play: MIDI drives REAPER built-in ReaSynth; no media files required.\n"
    .. "Rhythm is a folder; Pulse is split at 8s. Chords has two takes: select it and press T.\n"
    .. "Chords: volume automation; Bass: pan automation. Parallel bus receives Chords.\n"
    .. "Melody: ReaEQ 100 Hz low cut. Chords: long ReaVerbate insert.\n"
    .. "Bass: ReaComp -15 dB threshold, +3 dB manual makeup. Master: ReaLimit -4.5 dB threshold.\n"
    .. "Folders, alternate take and pan envelope use custom Lua through rac, not high-level ops.")
  reaper.SetEditCurPos(0, false, false)
  reaper.GetSet_ArrangeView2(0, true, 0, 0, 0, 17)
  reaper.TrackList_AdjustWindows(false)
  reaper.UpdateArrange()
end

local function inspect_demo()
  local names, folders, items = {}, {}, {}
  for i=0,reaper.CountTracks(0)-1 do
    local _, name = reaper.GetTrackName(track(i))
    names[#names+1] = name
    folders[#folders+1] = reaper.GetMediaTrackInfo_Value(track(i), "I_FOLDERDEPTH")
    items[#items+1] = reaper.CountTrackMediaItems(track(i))
  end
  local active = reaper.GetActiveTake(item(4))
  local _, take_name = reaper.GetSetMediaItemTakeInfo_String(active, "P_NAME", "", false)
  local _, notes = reaper.MIDI_CountEvts(reaper.GetActiveTake(item(5)))
  local _, markers, regions = reaper.CountProjectMarkers(0)
  local volume = assert(reaper.GetTrackEnvelopeByName(track(4), "Volume"))
  local pan = assert(reaper.GetTrackEnvelopeByName(track(3), "Pan"))
  local dest = reaper.GetTrackSendInfo_Value(track(4), 0, 0, "P_DESTTRACK")
  local _, dest_name = reaper.GetTrackName(dest)
  local external_sources, synths = 0, 0
  for ti=1,5 do
    local _, fxname = reaper.TrackFX_GetFXName(track(ti), 0, "")
    assert(fxname:find("ReaSynth", 1, true), "missing built-in ReaSynth")
    synths = synths + 1
    for ii=0,reaper.CountTrackMediaItems(track(ti))-1 do
      local it = reaper.GetTrackMediaItem(track(ti), ii)
      for tk=0,reaper.CountTakes(it)-1 do
        local take = reaper.GetTake(it, tk)
        assert(reaper.TakeIsMIDI(take), "demo take is not MIDI")
        local file = reaper.GetMediaSourceFileName(reaper.GetMediaItemTake_Source(take), "")
        if file ~= "" then external_sources = external_sources + 1 end
      end
    end
  end
  local _, alternate_notes = reaper.MIDI_CountEvts(reaper.GetTake(item(4), 1))
  RUN.result = {names=names, folders=folders, items=items,
    takes=reaper.CountTakes(item(4)), active_take=take_name,
    midi_notes=notes, midi_muted=reaper.GetMediaTrackInfo_Value(track(5), "B_MUTE") == 1,
    volume_points=reaper.CountEnvelopePoints(volume), pan_points=reaper.CountEnvelopePoints(pan),
    sends=reaper.GetTrackNumSends(track(4), 0), send_destination=dest_name,
    markers=markers, regions=regions, tempo=reaper.Master_GetTempo(),
    external_sources=external_sources, synths=synths, alternate_notes=alternate_notes,
    effects=inspect_effects(), resource=reaper.GetResourcePath()}
end
