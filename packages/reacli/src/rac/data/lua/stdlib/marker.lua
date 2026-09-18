-- stdlib/marker.lua — (粘贴片段: 全文拼入你的脚本即可用; 无 return, 无 require) 工程 marker/region 片段 (自包含, 整段可抄)
-- 返回约定同 track.lua; find-before-create 幂等 (creation 身份策略 P4 §4.1c)
std_marker = std_marker or {}  -- 全局表, 幂等重定义

local function _log(log, level, msg) if log then log(level, msg) end end

-- 添加 marker; 同 index 已存在则更新 (find-before-create)
-- 注意: EnumProjectMarkers 枚举序号横跨 marker+region 全集, 必须遍历 nmk+nrgn
function std_marker.add(index, pos, name, log)
  local _, nmk, nrgn = reaper.CountProjectMarkers(0)
  for i = 0, nmk + nrgn - 1 do
    local _, isrgn, _, _, _, midx = reaper.EnumProjectMarkers(i)
    if not isrgn and midx == index then
      reaper.SetProjectMarker(index, false, pos, 0, name)
      _log(log, "info", "marker.add: update existing index=" .. index)
      return { ok = true, value = { updated = true }, affected = { { kind = "marker", index = index } } }
    end
  end
  reaper.AddProjectMarker(0, false, pos, 0, name, index)
  _log(log, "info", "marker.add index=" .. index .. " pos=" .. pos .. " name=" .. tostring(name))
  return { ok = true, value = { updated = false }, affected = { { kind = "marker", index = index } } }
end

-- 批量: markers = {{index, pos, name}, ...}; 一次调用全部就位
function std_marker.add_batch(markers, log)
  local affected = {}
  for _, m in ipairs(markers) do
    local r = std_marker.add(m[1], m[2], m[3], log)
    if not r.ok then return r end
    affected[#affected + 1] = { kind = "marker", index = m[1] }
  end
  return { ok = true, affected = affected }
end

function std_marker.delete(index, log)
  local _, nmk, nrgn = reaper.CountProjectMarkers(0)
  for i = 0, nmk + nrgn - 1 do  -- 枚举序号横跨 marker+region
    local _, isrgn, _, _, _, midx = reaper.EnumProjectMarkers(i)
    if not isrgn and midx == index then
      reaper.DeleteProjectMarkerByIndex(0, i)
      _log(log, "info", "marker.delete index=" .. index)
      return { ok = true, affected = { { kind = "marker", index = index } } }
    end
  end
  return { ok = false, reason = "blocked:marker_not_found" }
end

function std_marker.get_all(log)
  local out = {}
  local _, nmk, nrgn = reaper.CountProjectMarkers(0)
  for i = 0, nmk + nrgn - 1 do
    local _, isrgn, pos, rgnend, name, midx = reaper.EnumProjectMarkers(i)
    out[#out + 1] = { index = midx, pos = pos, name = name,
                      is_region = isrgn, region_end = isrgn and rgnend or nil }
  end
  return { ok = true, value = out }
end

-- region: index 语义同 marker (region 与 marker 共享编号空间)
function std_marker.add_region(index, pos_start, pos_end, name, log)
  local _, nmk, nrgn = reaper.CountProjectMarkers(0)
  for i = 0, nmk + nrgn - 1 do
    local _, isrgn, _, _, _, midx = reaper.EnumProjectMarkers(i)
    if isrgn and midx == index then
      reaper.SetProjectMarker(index, true, pos_start, pos_end, name)
      _log(log, "info", "marker.add_region: update existing index=" .. index)
      return { ok = true, value = { updated = true }, affected = { { kind = "region", index = index } } }
    end
  end
  reaper.AddProjectMarker(0, true, pos_start, pos_end, name, index)
  _log(log, "info", "marker.add_region index=" .. index)
  return { ok = true, value = { updated = false }, affected = { { kind = "region", index = index } } }
end

