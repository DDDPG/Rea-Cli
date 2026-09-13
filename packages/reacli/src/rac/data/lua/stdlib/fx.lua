-- stdlib/fx.lua — (粘贴片段: 全文拼入你的脚本即可用; 无 return, 无 require)
-- FX 链: add/probe/set_param/set_preset/enable
std_fx = std_fx or {}

local function _log(log, level, msg) if log then log(level, msg) end end
local function _tr(idx)
  local tr = reaper.GetTrack(0, idx)
  if not tr then return nil end
  return tr
end

-- name 支持友好名与精确名; 找不到返回 blocked:fx_not_found
-- creation 幂等: 链上已有同名 FX 则返回现有索引 (find-before-create)
function std_fx.add_by_name(track_idx, fx_name, log)
  local tr = _tr(track_idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  local existing = reaper.TrackFX_GetByName(tr, fx_name, false)
  if existing >= 0 then
    _log(log, "info", "fx.add_by_name: found existing " .. fx_name .. " at fx[" .. existing .. "]")
    return { ok = true, value = { fx_index = existing, existed = true },
             affected = { { kind = "fx", track = track_idx, fx = existing } } }
  end
  local idx = reaper.TrackFX_AddByName(tr, fx_name, false, -1)
  if idx < 0 then return { ok = false, reason = "blocked:fx_not_found" } end
  _log(log, "info", "fx.add_by_name track=" .. track_idx .. " " .. fx_name .. " -> fx[" .. idx .. "]")
  return { ok = true, value = { fx_index = idx, existed = false },
           affected = { { kind = "fx", track = track_idx, fx = idx } } }
end

-- 链快照: 一次调用全链 dump (名称/enabled/参数数/当前值)
function std_fx.probe(track_idx, log)
  local tr = _tr(track_idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  local chain = {}
  for i = 0, reaper.TrackFX_GetCount(tr) - 1 do
    local _, name = reaper.TrackFX_GetFXName(tr, i, "")
    local params = {}
    for p = 0, reaper.TrackFX_GetNumParams(tr, i) - 1 do
      local _, pname = reaper.TrackFX_GetParamName(tr, i, p, "")
      local val, minv, maxv = reaper.TrackFX_GetParam(tr, i, p)
      params[#params + 1] = { index = p, name = pname, value = val, min = minv, max = maxv }
    end
    chain[#chain + 1] = { index = i, name = name,
                          enabled = reaper.TrackFX_GetEnabled(tr, i),
                          offline = reaper.TrackFX_GetOffline(tr, i),
                          params = params }
  end
  return { ok = true, value = chain }
end

-- 归一化设参 (0..1); 实际值域用 TrackFX_GetParam 的 (val,min,max) 换算
function std_fx.set_param_normalized(track_idx, fx_idx, param_idx, norm, log)
  local tr = _tr(track_idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  if fx_idx < 0 or reaper.TrackFX_GetCount(tr) <= fx_idx then
    return { ok = false, reason = "blocked:fx_index_out_of_range" }
  end
  reaper.TrackFX_SetParamNormalized(tr, fx_idx, param_idx, norm)
  _log(log, "info", "fx.set_param_normalized [" .. track_idx .. "," .. fx_idx .. "," .. param_idx .. "] -> " .. norm)
  return { ok = true, affected = { { kind = "fx", track = track_idx, fx = fx_idx } } }
end

function std_fx.set_enabled(track_idx, fx_idx, enabled, log)
  local tr = _tr(track_idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  if fx_idx < 0 or reaper.TrackFX_GetCount(tr) <= fx_idx then
    return { ok = false, reason = "blocked:fx_index_out_of_range" }
  end
  reaper.TrackFX_SetEnabled(tr, fx_idx, enabled)
  _log(log, "info", "fx.set_enabled [" .. track_idx .. "," .. fx_idx .. "] -> " .. tostring(enabled))
  return { ok = true, affected = { { kind = "fx", track = track_idx, fx = fx_idx } } }
end

function std_fx.set_preset(track_idx, fx_idx, preset_name, log)
  local tr = _tr(track_idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  if fx_idx < 0 or reaper.TrackFX_GetCount(tr) <= fx_idx then
    return { ok = false, reason = "blocked:fx_index_out_of_range" }
  end
  local okp = reaper.TrackFX_SetPreset(tr, fx_idx, preset_name)
  if not okp then return { ok = false, reason = "blocked:preset_not_found" } end
  _log(log, "info", "fx.set_preset [" .. track_idx .. "," .. fx_idx .. "] -> " .. preset_name)
  return { ok = true, affected = { { kind = "fx", track = track_idx, fx = fx_idx } } }
end
