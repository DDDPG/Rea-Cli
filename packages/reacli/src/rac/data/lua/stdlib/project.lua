-- stdlib/project.lua — (粘贴片段: 全文拼入你的脚本即可用; 无 return, 无 require)
-- 工程: save/save_as/notes/ext_state/tempo
std_project = std_project or {}

local function _log(log, level, msg) if log then log(level, msg) end end

-- save-copy 到绝对路径 (opts=4, 不动 tab 身份); 防 stale: 临时路径+rename
function std_project.save_as(abs_path, log)
  if abs_path:sub(1, 1) ~= "/" then
    return { ok = false, reason = "blocked:path_not_absolute" }
  end
  local tmp = abs_path .. ".racpart_" .. tostring(math.floor(reaper.time_precise() * 1000))
  os.remove(tmp)
  reaper.Main_SaveProjectEx(0, tmp, 4)
  local f = io.open(tmp, "r")
  if not f then return { ok = false, reason = "blocked:save_produced_no_file" } end
  f:close()
  if not os.rename(tmp, abs_path) then
    os.remove(tmp)
    return { ok = false, reason = "blocked:rename_failed" }
  end
  _log(log, "info", "project.save_as -> " .. abs_path)
  return { ok = true, affected = { { kind = "project", path = abs_path } } }
end

function std_project.save(log)
  reaper.Main_SaveProject(0, false)
  _log(log, "info", "project.save")
  return { ok = true, affected = { { kind = "project" } } }
end

function std_project.set_tempo(bpm, log)
  reaper.SetCurrentBPM(0, bpm, false)
  _log(log, "info", "project.set_tempo -> " .. bpm)
  return { ok = true, affected = { { kind = "project" } } }
end

function std_project.set_notes(text, log)
  reaper.GetSetProjectNotes(0, true, text)
  _log(log, "info", "project.set_notes len=" .. #text)
  return { ok = true, affected = { { kind = "project" } } }
end

function std_project.get_notes(log)
  return { ok = true, value = reaper.GetSetProjectNotes(0, false, "") }
end

function std_project.set_ext_state(key, value, log)  -- section 固定 "rac"
  reaper.SetProjExtState(0, "rac", key, value)
  _log(log, "info", "project.set_ext_state rac/" .. key)
  return { ok = true, affected = { { kind = "ext_state", key = key } } }
end

function std_project.get_ext_state(key, log)
  local _, val = reaper.GetProjExtState(0, "rac", key)
  return { ok = true, value = val }
end
