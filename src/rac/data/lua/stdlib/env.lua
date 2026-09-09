-- stdlib/env.lua — (粘贴片段: 全文拼入你的脚本即可用; 无 return, 无 require)
-- 轨道 envelope: get-or-create 习语 + 批量设点 + 求值 + 删除区间
-- get-or-create 是核心资产: 先查 GetTrackEnvelopeByName, 无则 action 显示一次再取
-- (action 为 toggle 语义, 已存在时绝不能调, 否则反而关掉)
std_env = std_env or {}

local function _log(log, level, msg) if log then log(level, msg) end end

-- action ID 映射 (cli_behavior/actions_index 交叉验证):
--   40406 = Track: View track volume envelope
--   40407 = Track: View track pan envelope
--   40867 = Track: View track mute envelope
local ENV_ACTIONS = { Volume = 40406, Pan = 40407, Mute = 40867 }

local function _track(idx)
  return reaper.GetTrack(0, idx)
end

function std_env.get_or_create(track_idx, env_name, log)
  local tr = _track(track_idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  local env = reaper.GetTrackEnvelopeByName(tr, env_name)
  if not env then
    local action = ENV_ACTIONS[env_name]
    if not action then return { ok = false, reason = "blocked:unknown_env_name" } end
    -- action 作用于"当前选中轨": 必须先选中目标轨; 选中态用完即恢复
    local prev_sel = {}
    for i = 0, reaper.CountSelectedTracks(0) - 1 do
      prev_sel[#prev_sel + 1] = reaper.GetSelectedTrack(0, i)
    end
    reaper.SetOnlyTrackSelected(tr)
    reaper.Main_OnCommand(action, 0)  -- 只在不存在时调 (toggle 语义!)
    env = reaper.GetTrackEnvelopeByName(tr, env_name)
    reaper.Main_OnCommand(40297, 0)  -- unselect all
    for _, t in ipairs(prev_sel) do reaper.SetTrackSelected(t, true) end
  end
  if not env then return { ok = false, reason = "blocked:env_create_failed" } end
  _log(log, "info", "env.get_or_create track=" .. track_idx .. " " .. env_name)
  -- 返回标识而非指针 (指针纪律: userdata 不进返回表, 序列化即垃圾)
  return { ok = true, value = { track = track_idx, name = env_name } }
end

-- 内部解析 (不进公共返回): 各函数按需取指针, 用完即弃
local function _resolve(track_idx, env_name)
  local tr = _track(track_idx)
  if not tr then return nil end
  return reaper.GetTrackEnvelopeByName(tr, env_name)
end

-- 批量设点 (先清空再插入): points = {{time, db, shape}, ...}; shape 缺省 0
-- 域换算 (实机钉死, DB2SLIDER 对照):
--   写入: raw = ScaleToEnvelopeMode(scaling, linear)   [linear->raw, 写方向]
--   读出: linear = ScaleFromEnvelopeMode(scaling, raw) [raw->linear, 读方向]
--   mode=0 时两方向恒等 — 用 From 写入的 bug 会被 mode=0 掩盖 (MCP 桥同款隐患)
function std_env.set_points_db(track_idx, env_name, points, log)
  local r = std_env.get_or_create(track_idx, env_name, log)
  if not r.ok then return r end
  local env = _resolve(track_idx, env_name)
  if not env then return { ok = false, reason = "blocked:env_not_found" } end
  reaper.DeleteEnvelopePointRange(env, -0.000001, 999999999)
  local scaling = reaper.GetEnvelopeScalingMode(env)
  for _, p in ipairs(points) do
    local t, db, shape = p[1], p[2], p[3] or 0
    local val = reaper.ScaleToEnvelopeMode(scaling, 10 ^ (db / 20))
    reaper.InsertEnvelopePoint(env, t, val, shape, 0, false, true)
  end
  reaper.Envelope_SortPoints(env)
  _log(log, "info", "env.set_points_db " .. env_name .. " n=" .. #points)
  return { ok = true, affected = { { kind = "envelope", track = track_idx, name = env_name } } }
end

-- 求值: raw 经 ScaleFromEnvelopeMode 回读 linear (读方向), dB 可直接算出
function std_env.evaluate(track_idx, env_name, time, log)
  local tr = _track(track_idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  local env = reaper.GetTrackEnvelopeByName(tr, env_name)
  if not env then return { ok = false, reason = "blocked:env_not_found" } end
  local _, raw = reaper.Envelope_Evaluate(env, time, 0, 0)
  local scaling = reaper.GetEnvelopeScalingMode(env)
  local linear = reaper.ScaleFromEnvelopeMode(scaling, raw)
  local db = linear > 0 and 20 * math.log(linear, 10) or -150.0
  return { ok = true, value = { raw = raw, linear = linear, db = db } }
end

-- dB → RAW 域换算 (写方向, 与 set_points_db 一致)
function std_env.db_to_raw(track_idx, env_name, db, log)
  local tr = _track(track_idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  local env = reaper.GetTrackEnvelopeByName(tr, env_name)
  if not env then return { ok = false, reason = "blocked:env_not_found" } end
  local scaling = reaper.GetEnvelopeScalingMode(env)
  return { ok = true, value = reaper.ScaleToEnvelopeMode(scaling, 10 ^ (db / 20)) }
end

function std_env.delete_range(track_idx, env_name, t1, t2, log)
  local tr = _track(track_idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  local env = reaper.GetTrackEnvelopeByName(tr, env_name)
  if not env then return { ok = false, reason = "blocked:env_not_found" } end
  reaper.DeleteEnvelopePointRange(env, t1, t2)
  _log(log, "info", "env.delete_range " .. env_name .. " [" .. t1 .. "," .. t2 .. "]")
  return { ok = true, affected = { { kind = "envelope", track = track_idx, name = env_name } } }
end

function std_env.count_points(track_idx, env_name, log)
  local tr = _track(track_idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  local env = reaper.GetTrackEnvelopeByName(tr, env_name)
  if not env then return { ok = false, reason = "blocked:env_not_found" } end
  return { ok = true, value = reaper.CountEnvelopePoints(env) }  -- 单返回值
end
