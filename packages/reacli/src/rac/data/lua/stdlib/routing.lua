-- stdlib/routing.lua — (粘贴片段: 全文拼入你的脚本即可用; 无 return, 无 require)
-- 路由: send 创建/删除/音量
std_routing = std_routing or {}

local function _log(log, level, msg) if log then log(level, msg) end end

-- creation 幂等: src→dst send 已存在则返回现有索引 (find-before-create)
function std_routing.create_send(src_track_idx, dst_track_idx, log)
  local src = reaper.GetTrack(0, src_track_idx)
  local dst = reaper.GetTrack(0, dst_track_idx)
  if not src or not dst then return { ok = false, reason = "blocked:no_track_at_index" } end
  for i = 0, reaper.GetTrackNumSends(src, 0) - 1 do
    local dst_ptr = reaper.GetTrackSendInfo_Value(src, 0, i, "P_DESTTRACK")
    if dst_ptr == dst then
      _log(log, "info", "routing.create_send: found existing at send[" .. i .. "]")
      return { ok = true, value = { send_index = i, existed = true },
               affected = { { kind = "send", src = src_track_idx, dst = dst_track_idx } } }
    end
  end
  local send_idx = reaper.CreateTrackSend(src, dst)
  if send_idx < 0 then return { ok = false, reason = "blocked:create_send_failed" } end
  _log(log, "info", "routing.create_send " .. src_track_idx .. " -> " .. dst_track_idx)
  return { ok = true, value = { send_index = send_idx, existed = false },
           affected = { { kind = "send", src = src_track_idx, dst = dst_track_idx } } }
end

function std_routing.set_send_volume(track_idx, send_idx, linear, log)
  local tr = reaper.GetTrack(0, track_idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  if send_idx < 0 or send_idx >= reaper.GetTrackNumSends(tr, 0) then
    return { ok = false, reason = "blocked:send_index_out_of_range" }
  end
  reaper.SetTrackSendInfo_Value(tr, 0, send_idx, "D_VOL", linear)
  _log(log, "info", "routing.set_send_volume [" .. track_idx .. "," .. send_idx .. "] -> " .. linear)
  return { ok = true, affected = { { kind = "send", track = track_idx, send = send_idx } } }
end

function std_routing.remove_send(track_idx, send_idx, log)
  local tr = reaper.GetTrack(0, track_idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  if send_idx < 0 or send_idx >= reaper.GetTrackNumSends(tr, 0) then
    return { ok = false, reason = "blocked:send_index_out_of_range" }
  end
  if not reaper.RemoveTrackSend(tr, 0, send_idx) then
    return { ok = false, reason = "blocked:remove_send_failed" }
  end
  _log(log, "info", "routing.remove_send [" .. track_idx .. "," .. send_idx .. "]")
  return { ok = true, affected = { { kind = "send", track = track_idx, send = send_idx } } }
end

function std_routing.list_sends(track_idx, log)
  local tr = reaper.GetTrack(0, track_idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  local out = {}
  for i = 0, reaper.GetTrackNumSends(tr, 0) - 1 do
    local dst = reaper.GetTrackSendInfo_Value(tr, 0, i, "P_DESTTRACK")
    out[#out + 1] = { index = i, vol = reaper.GetTrackSendInfo_Value(tr, 0, i, "D_VOL") }
  end
  return { ok = true, value = out }
end
