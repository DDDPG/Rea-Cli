-- ============================================================================
-- entry.lua — Path A 状态返回约定骨架 (reaper_agent_cli)
-- 用法: 抄写本文件, 在 body() 中编写你的 ReaScript 操作, 把要回传的数据放进
--       RUN.result。脚本产出 proof.json 后自动退出 REAPER。
-- 约定:
--   * 禁用 defer (一次性脚本, 同步执行到底)
--   * 业务逻辑都在 body() 内 — body 由 pcall 包裹, 错误是数据不是崩溃
--     (骨架自身的 state 采集/proof 写出为极简路径, 不在 pcall 内)
--   * 环境变量 RAC_RUN_DIR 决定 proof.json 输出目录 (缺省 /tmp)
--   * 环境变量 RAC_SAVE_AS 若设置, body 成功后按该绝对路径 save-copy (opts=4;
--     经唯一临时路径 + os.rename 防旧文件冒充新鲜写入)
-- ============================================================================

local RUN_DIR = os.getenv("RAC_RUN_DIR") or "/tmp"
local SAVE_AS = os.getenv("RAC_SAVE_AS") -- 必须是绝对路径
local EXPECT_HASH = os.getenv("RAC_EXPECT_STATE_HASH") -- 停滞检测: 若与本次 state_hash 一致则 completed_noop
local RUN = { t0 = reaper.time_precise(), log = {}, result = nil }

-- JSON null 哨兵 (table 的 nil 值会丢 key, 显式 null 需要哨兵)
local JSON_NULL = setmetatable({}, { __tostring = function() return "null" end })
-- 空对象哨兵 (空 table 一律编码为 []; 需要 {} 语义时显式使用)
local JSON_EMPTY_OBJECT = setmetatable({}, { __tostring = function() return "{}" end })

local function log(level, msg)
  RUN.log[#RUN.log + 1] = {
    t_ms = math.floor((reaper.time_precise() - RUN.t0) * 1000),
    level = level, msg = tostring(msg),
  }
end

-- ---------------------------------------------------------------------------
-- JSON encoder (UTF-8 直出, CJK 安全; 支持 table/array/string/number/boolean/nil)
-- ---------------------------------------------------------------------------
local function json_encode(v, buf)
  buf = buf or {}
  if v == JSON_NULL then
    buf[#buf + 1] = "null"
    return table.concat(buf)
  end
  if v == JSON_EMPTY_OBJECT then
    buf[#buf + 1] = "{}"
    return table.concat(buf)
  end
  local t = type(v)
  if t == "nil" then
    buf[#buf + 1] = "null"
  elseif t == "boolean" then
    buf[#buf + 1] = tostring(v)
  elseif t == "number" then
    if v ~= v then
      buf[#buf + 1] = '"NaN"'          -- JSON 无 NaN, 字符串化防非法 JSON
    elseif v == math.huge then
      buf[#buf + 1] = '"Infinity"'
    elseif v == -math.huge then
      buf[#buf + 1] = '"-Infinity"'
    else
      buf[#buf + 1] = tostring(v)
    end
  elseif t == "string" then
    local s = v:gsub('[%z\1-\31\\"]', function(c)
      local m = { ['"'] = '\\"', ['\\'] = '\\\\', ['\n'] = '\\n',
                  ['\r'] = '\\r', ['\t'] = '\\t' }
      return m[c] or string.format('\\u%04x', c:byte())
    end)
    buf[#buf + 1] = '"' .. s .. '"'
  elseif t == "table" then
    local n = #v
    if n > 0 then -- array
      buf[#buf + 1] = "["
      for i = 1, n do
        if i > 1 then buf[#buf + 1] = "," end
        json_encode(v[i], buf)
      end
      buf[#buf + 1] = "]"
    elseif next(v) == nil then
      -- 空 table 一律编码为 [] (proof 语义中的空集合都是数组: log/tracks_summary/markers;
      -- 需要空对象 {} 语义请用 JSON_EMPTY_OBJECT 哨兵)
      buf[#buf + 1] = "[]"
    else -- object: 确定性 key 排序 (state_hash 一致性的前提)
      local keys, map = {}, {}
      for k, val in pairs(v) do
        local sk = tostring(k)
        keys[#keys + 1] = sk
        map[sk] = val
      end
      table.sort(keys)
      buf[#buf + 1] = "{"
      for i, k in ipairs(keys) do
        if i > 1 then buf[#buf + 1] = "," end
        json_encode(k, buf)
        buf[#buf + 1] = ":"
        json_encode(map[k], buf)
      end
      buf[#buf + 1] = "}"
    end
  else
    buf[#buf + 1] = '"' .. t .. ':unsupported"'
  end
  return table.concat(buf)
end

-- ---------------------------------------------------------------------------
-- FNV-1a 32-bit: 变更检测用哈希 (非加密; 连续执行对比 state 是否变化)
-- ---------------------------------------------------------------------------
local function fnv1a(str)
  local hash = 2166136261
  for i = 1, #str do
    hash = (hash ~ str:byte(i)) * 16777619 & 0xFFFFFFFF
  end
  return string.format("%08x", hash)
end

-- ---------------------------------------------------------------------------
-- state 采集: 工程快照摘要 (有界: tracks>50 截断, 完整结构由调用方另行落盘)
-- ---------------------------------------------------------------------------
local function collect_state()
  local tracks, n = {}, reaper.CountTracks(0)
  for i = 0, math.min(n, 50) - 1 do
    local tr = reaper.GetTrack(0, i)
    local _, name = reaper.GetTrackName(tr)
    tracks[#tracks + 1] = {
      index = i, name = name,
      n_items = reaper.CountTrackMediaItems(tr),
      n_fx = reaper.TrackFX_GetCount(tr),  -- 覆盖 FX 重复添加 (codex Low)
      volume = reaper.GetMediaTrackInfo_Value(tr, "D_VOL"),
      mute = reaper.GetMediaTrackInfo_Value(tr, "B_MUTE") == 1,
    }
  end
  local _, projfn = reaper.EnumProjects(-1, "")
  -- markers/regions: hash 必须覆盖 (否则只改 marker 的操作会 false noop)
  local markers = {}
  local _, nmk, nrgn = reaper.CountProjectMarkers(0)
  local n_total = nmk + nrgn
  for i = 0, math.min(n_total, 50) - 1 do
    local _, isrgn, pos, rgnend, name, midx = reaper.EnumProjectMarkers(i)
    markers[#markers + 1] = {
      index = midx, pos = pos, name = name,
      is_region = isrgn, region_end = isrgn and rgnend or JSON_NULL,
    }
  end
  return {
    project_path = projfn,
    track_count = n,
    tracks_summary = tracks,
    tracks_truncated = n > 50,
    marker_count = nmk,
    region_count = nrgn,
    markers = markers,
    markers_truncated = n_total > 50,
    cursor_pos = reaper.GetCursorPosition(),
    dirty = reaper.IsProjectDirty(0) == 1,
  }
end

-- ===========================================================================
-- body(): ==== 在这里编写你的操作 ====
-- ===========================================================================
local function body()
  reaper.InsertTrackAtIndex(0, true)
  local tr = reaper.GetTrack(0, 0)
  reaper.GetSetMediaTrackInfo_String(tr, "P_NAME", "smoke_vox", true)
  reaper.SetMediaTrackInfo_Value(tr, "D_VOL", 0.501187)
  reaper.AddProjectMarker(0, false, 30.0, 0.0, "冒烟marker", 1)
  RUN.result = { track = 0, marker_idx = 1 }
end
-- ===========================================================================

local ok, err = pcall(body)

local state = collect_state()
-- state_hash 只覆盖工程"内容", 不含易变字段:
--   project_path = 文件身份 (另存后即变, 与内容无关)
--   dirty        = 持久化标志 (首轮改完为 true, 幂等复跑无改动为 false — 两者内容一致)
local hash_state = {}
for k, v in pairs(state) do
  if k ~= "project_path" and k ~= "dirty" then hash_state[k] = v end
end
local state_hash = fnv1a(json_encode(hash_state))

-- 存盘先于 proof 写出, 且结果纳入 proof (proof 必须反映最终执行结果)。
-- 只在 body 成功时存盘: body 失败时工程可能处于部分修改态, 存盘会持久化坏状态。
-- 防 stale-output 假成功: 保存到唯一临时路径再 os.rename —— 临时文件的存在
-- 本身就是"本次确实写入"的证明 (目标已存在的旧文件无法冒充)。
local save_field = JSON_NULL
if SAVE_AS and ok then
  local tmp = SAVE_AS .. ".racpart_" .. tostring(math.floor(reaper.time_precise() * 1000))
  os.remove(tmp)
  local ok_save, save_err = pcall(reaper.Main_SaveProjectEx, 0, tmp, 4) -- 4 = save copy
  local fcheck = io.open(tmp, "r")
  local tmp_exists = fcheck ~= nil
  if fcheck then fcheck:close() end
  local renamed = false
  if ok_save and tmp_exists then
    renamed = os.rename(tmp, SAVE_AS) == true
    if not renamed then
      os.remove(tmp) -- rename 失败清理临时文件, 防 .racpart_* 残留
    end
  end
  local saved = ok_save and tmp_exists and renamed
  save_field = {
    saved = saved, path = SAVE_AS,
    error = saved and JSON_NULL or tostring(
      (not ok_save and save_err)
      or (not tmp_exists and "temp save target not produced (save silently failed)")
      or (not renamed and "rename to final path failed")
      or "unknown save failure"),
  }
  if not saved then
    ok = false
    err = save_field.error
  end
end

local err_field = JSON_NULL
if not ok then
  err_field = {
    class = save_field ~= JSON_NULL and "save" or "lua_runtime",
    message = tostring(err),
    retriable = false,
    lua_traceback = save_field ~= JSON_NULL and JSON_NULL or debug.traceback(tostring(err)), -- 不传 level: C 边界错误(level 2 会丢帧)
  }
end

local reason
if ok then
  reason = (EXPECT_HASH and EXPECT_HASH == state_hash) and "completed_noop" or "completed"
elseif save_field ~= JSON_NULL then
  reason = "save_failed"  -- 只在 body 成功后存盘, save_failed 必属存盘环节
else
  reason = "lua_error"
end

local duration = math.floor((reaper.time_precise() - RUN.t0) * 1000) -- 含存盘 I/O

local proof = {
  status = ok and "ok" or "error",
  reason_code = reason,
  duration_ms = duration,
  log = RUN.log,
  state = state,
  state_hash = state_hash,
  result = RUN.result or JSON_NULL, -- nil 会丢 key, 显式 null
  save = save_field,
  error = err_field,
}

local f = io.open(RUN_DIR .. "/proof.json", "w")
if f then
  f:write(json_encode(proof))
  f:close()
end

reaper.Main_OnCommand(40004, 0) -- File: Quit REAPER (必须显式退出)
