-- stdlib/render.lua — (粘贴片段: 全文拼入你的脚本即可用; 无 return, 无 require)
-- 渲染配置批处理 (SetRenderConfig 模式: 9 项 RENDER_* 一次就位)
-- 注意: 实际渲染执行优先用官方 `reaper -renderproject` (cli_behavior 契约);
--       脚本内渲染用 render_project (Main_OnCommand 41824, 部分场景弹窗需探针)
std_render = std_render or {}

local function _log(log, level, msg) if log then log(level, msg) end end

-- config 键: bounds(0自定义/1整工程/2时间选区/3region/4item/5选中region),
--   channels, srate, tail_flag, tail_ms, dither, output_file(目录或全路径), pattern
function std_render.set_config(config, log)
  local set = {
    RENDER_BOUNDSFLAG = config.bounds, RENDER_CHANNELS = config.channels,
    RENDER_SRATE = config.srate, RENDER_TAILFLAG = config.tail_flag,
    RENDER_TAILMS = config.tail_ms, RENDER_DITHER = config.dither,
  }
  for key, val in pairs(set) do
    if val ~= nil then reaper.GetSetProjectInfo(0, key, val, true) end
  end
  if config.output_file then
    reaper.GetSetProjectInfo_String(0, "RENDER_FILE", config.output_file, true)
  end
  if config.pattern then
    reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", config.pattern, true)
  end
  if config.t0 and config.t1 then  -- bounds=2 时需时间选区
    reaper.GetSet_LoopTimeRange(true, false, config.t0, config.t1, false)
  end
  _log(log, "info", "render.set_config applied")
  return { ok = true, affected = { { kind = "render_config" } } }
end

-- 触发渲染 (整工程, 用当前 RENDER_* 配置); 弹窗风险见 cli_behavior
function std_render.render_project(log)
  reaper.Main_OnCommand(41824, 0)  -- File: Render project, using the most recent render settings
  _log(log, "info", "render.render_project triggered (41824)")
  return { ok = true, affected = { { kind = "render" } } }
end

-- 读当前渲染配置 (核验用)
function std_render.get_config(log)
  local _, rf = reaper.GetSetProjectInfo_String(0, "RENDER_FILE", "", false)
  local _, rp = reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", "", false)
  return { ok = true, value = {
    bounds = reaper.GetSetProjectInfo(0, "RENDER_BOUNDSFLAG", 0, false),
    channels = reaper.GetSetProjectInfo(0, "RENDER_CHANNELS", 0, false),
    srate = reaper.GetSetProjectInfo(0, "RENDER_SRATE", 0, false),
    output_file = rf, pattern = rp,
  } }
end
