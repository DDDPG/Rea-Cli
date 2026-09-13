-- stdlib/track.lua — (粘贴片段: 全文拼入你的脚本即可用; 无 return, 无 require) 轨道操作片段 (自包含, 整段可抄)
-- 返回约定: {ok=true, value=..., affected={...}} / {ok=false, reason="blocked:..."}
-- 所有函数 set-based 幂等; 可选 log(level,msg) 参数
std_track = std_track or {}  -- 全局表, 幂等重定义

local function _log(log, level, msg) if log then log(level, msg) end end
local function _get(idx)
  local tr = reaper.GetTrack(0, idx)
  if not tr then return nil end
  return tr
end

function std_track.count()
  return { ok = true, value = reaper.CountTracks(0) }
end

function std_track.get_info(idx, log)
  local tr = _get(idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  local _, name = reaper.GetTrackName(tr)
  return { ok = true, value = {
    index = idx, name = name,
    volume = reaper.GetMediaTrackInfo_Value(tr, "D_VOL"),
    pan = reaper.GetMediaTrackInfo_Value(tr, "D_PAN"),
    mute = reaper.GetMediaTrackInfo_Value(tr, "B_MUTE") == 1,
    solo = reaper.GetMediaTrackInfo_Value(tr, "I_SOLO") > 0,
    n_items = reaper.CountTrackMediaItems(tr),
    guid = reaper.GetTrackGUID(tr),
  } }
end

function std_track.list_all(log)
  local out = {}
  for i = 0, reaper.CountTracks(0) - 1 do
    local info = std_track.get_info(i)
    if info.ok then out[#out + 1] = info.value end
  end
  return { ok = true, value = out }
end

-- creation 幂等: name 提供时按名 find-before-create (重复执行不重复建轨);
-- name 缺省时身份即"新建一条轨", 天然非幂等 — 文档明示
function std_track.create(idx, name, log)
  if name and name ~= "" then  -- "" 视为无名 (Lua 中 "" 为真值, 防空名误命中)
    for i = 0, reaper.CountTracks(0) - 1 do
      local _, n = reaper.GetTrackName(reaper.GetTrack(0, i))
      if n == name then
        _log(log, "info", "track.create: found existing name=" .. name .. " at " .. i)
        return { ok = true, value = { existed = true, index = i },
                 affected = { { kind = "track", index = i } } }
      end
    end
  end
  reaper.InsertTrackAtIndex(idx, true)
  if name then
    reaper.GetSetMediaTrackInfo_String(reaper.GetTrack(0, idx), "P_NAME", name, true)
  end
  _log(log, "info", "track.create idx=" .. idx .. " name=" .. tostring(name))
  return { ok = true, value = { existed = false, index = idx },
           affected = { { kind = "track", index = idx } } }
end

function std_track.delete(idx, log)
  local tr = _get(idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  reaper.DeleteTrack(tr)
  _log(log, "info", "track.delete idx=" .. idx)
  return { ok = true, affected = { { kind = "track", index = idx } } }
end

function std_track.set_name(idx, name, log)
  local tr = _get(idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  reaper.GetSetMediaTrackInfo_String(tr, "P_NAME", name, true)
  _log(log, "info", "track.set_name idx=" .. idx .. " -> " .. name)
  return { ok = true, affected = { { kind = "track", index = idx } } }
end

function std_track.set_volume_db(idx, db, log)
  local tr = _get(idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  local linear = 10 ^ (db / 20)  -- dB↔linear: -6dB ≈ 0.501187
  reaper.SetMediaTrackInfo_Value(tr, "D_VOL", linear)
  _log(log, "info", string.format("track.set_volume_db idx=%d -> %.2fdB (%.6f linear)", idx, db, linear))
  return { ok = true, value = { linear = linear },
           affected = { { kind = "track", index = idx } } }
end

function std_track.set_pan(idx, pan, log)  -- pan: -1.0(L) .. 1.0(R)
  local tr = _get(idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  if pan < -1 or pan > 1 then return { ok = false, reason = "blocked:pan_out_of_range" } end
  reaper.SetMediaTrackInfo_Value(tr, "D_PAN", pan)
  _log(log, "info", "track.set_pan idx=" .. idx .. " -> " .. pan)
  return { ok = true, affected = { { kind = "track", index = idx } } }
end

function std_track.set_mute(idx, muted, log)
  local tr = _get(idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  reaper.SetMediaTrackInfo_Value(tr, "B_MUTE", muted and 1 or 0)
  _log(log, "info", "track.set_mute idx=" .. idx .. " -> " .. tostring(muted))
  return { ok = true, affected = { { kind = "track", index = idx } } }
end

function std_track.set_solo(idx, soloed, log)
  local tr = _get(idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  reaper.SetMediaTrackInfo_Value(tr, "I_SOLO", soloed and 1 or 0)
  _log(log, "info", "track.set_solo idx=" .. idx .. " -> " .. tostring(soloed))
  return { ok = true, affected = { { kind = "track", index = idx } } }
end

function std_track.set_color(idx, r, g, b, log)
  local tr = _get(idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  local native = reaper.ColorToNative(r, g, b) | 0x1000000  -- 高位标志位必须置位
  reaper.SetMediaTrackInfo_Value(tr, "I_CUSTOMCOLOR", native)
  _log(log, "info", "track.set_color idx=" .. idx)
  return { ok = true, affected = { { kind = "track", index = idx } } }
end

