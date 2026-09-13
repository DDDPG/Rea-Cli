-- stdlib/take.lua — (粘贴片段: 全文拼入你的脚本即可用; 无 return, 无 require)
-- take: source info / rate / offset / name
std_take = std_take or {}

local function _get(track_idx, item_idx)
  local tr = reaper.GetTrack(0, track_idx)
  if not tr then return nil end
  local it = reaper.GetTrackMediaItem(tr, item_idx)
  if not it then return nil end
  return reaper.GetActiveTake(it)
end

function std_take.source_info(track_idx, item_idx, log)
  local take = _get(track_idx, item_idx)
  if not take then return { ok = false, reason = "blocked:take_not_found" } end
  local src = reaper.GetMediaItemTake_Source(take)
  local _, name = reaper.GetSetMediaItemTakeInfo_String(take, "P_NAME", "", false)
  return { ok = true, value = {
    name = name,
    file = reaper.GetMediaSourceFileName(src, ""),
    type = reaper.GetMediaSourceType(src, ""),
    length = reaper.GetMediaSourceLength(src),
    samplerate = reaper.GetMediaSourceSampleRate(src),
    channels = reaper.GetMediaSourceNumChannels(src),
    playrate = reaper.GetMediaItemTakeInfo_Value(take, "D_PLAYRATE"),
    start_offset = reaper.GetMediaItemTakeInfo_Value(take, "D_STARTOFFS"),
  } }
end

function std_take.set_name(track_idx, item_idx, name, log)
  local take = _get(track_idx, item_idx)
  if not take then return { ok = false, reason = "blocked:take_not_found" } end
  reaper.GetSetMediaItemTakeInfo_String(take, "P_NAME", name, true)
  return { ok = true, affected = { { kind = "take", track = track_idx, item = item_idx } } }
end

function std_take.set_rate(track_idx, item_idx, rate, log)
  local take = _get(track_idx, item_idx)
  if not take then return { ok = false, reason = "blocked:take_not_found" } end
  if rate <= 0 then return { ok = false, reason = "blocked:rate_nonpositive" } end
  reaper.SetMediaItemTakeInfo_Value(take, "D_PLAYRATE", rate)
  return { ok = true, affected = { { kind = "take", track = track_idx, item = item_idx } } }
end

function std_take.set_start_offset(track_idx, item_idx, offset, log)
  local take = _get(track_idx, item_idx)
  if not take then return { ok = false, reason = "blocked:take_not_found" } end
  reaper.SetMediaItemTakeInfo_Value(take, "D_STARTOFFS", offset)
  return { ok = true, affected = { { kind = "take", track = track_idx, item = item_idx } } }
end
