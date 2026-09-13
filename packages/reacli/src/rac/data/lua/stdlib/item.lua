-- stdlib/item.lua — (粘贴片段: 全文拼入你的脚本即可用; 无 return, 无 require)
-- item 操作: 位置/长度/淡入淡出/mute/split/delete/insert_media
std_item = std_item or {}

local function _log(log, level, msg) if log then log(level, msg) end end
local function _get(track_idx, item_idx)
  local tr = reaper.GetTrack(0, track_idx)
  if not tr then return nil end
  return reaper.GetTrackMediaItem(tr, item_idx)
end

function std_item.get_info(track_idx, item_idx, log)
  local it = _get(track_idx, item_idx)
  if not it then return { ok = false, reason = "blocked:item_not_found" } end
  return { ok = true, value = {
    track = track_idx, item = item_idx,
    position = reaper.GetMediaItemInfo_Value(it, "D_POSITION"),
    length = reaper.GetMediaItemInfo_Value(it, "D_LENGTH"),
    mute = reaper.GetMediaItemInfo_Value(it, "B_MUTE") == 1,
    fade_in = reaper.GetMediaItemInfo_Value(it, "D_FADEINLEN"),
    fade_out = reaper.GetMediaItemInfo_Value(it, "D_FADEOUTLEN"),
  } }
end

function std_item.set_position(track_idx, item_idx, pos, log)
  local it = _get(track_idx, item_idx)
  if not it then return { ok = false, reason = "blocked:item_not_found" } end
  reaper.SetMediaItemInfo_Value(it, "D_POSITION", pos)
  _log(log, "info", "item.set_position [" .. track_idx .. "," .. item_idx .. "] -> " .. pos)
  return { ok = true, affected = { { kind = "item", track = track_idx, item = item_idx } } }
end

function std_item.set_length(track_idx, item_idx, len, log)
  local it = _get(track_idx, item_idx)
  if not it then return { ok = false, reason = "blocked:item_not_found" } end
  if len <= 0 then return { ok = false, reason = "blocked:length_nonpositive" } end
  reaper.SetMediaItemInfo_Value(it, "D_LENGTH", len)
  _log(log, "info", "item.set_length [" .. track_idx .. "," .. item_idx .. "] -> " .. len)
  return { ok = true, affected = { { kind = "item", track = track_idx, item = item_idx } } }
end

function std_item.set_fade(track_idx, item_idx, fade_in, fade_out, log)
  local it = _get(track_idx, item_idx)
  if not it then return { ok = false, reason = "blocked:item_not_found" } end
  reaper.SetMediaItemInfo_Value(it, "D_FADEINLEN", fade_in)
  reaper.SetMediaItemInfo_Value(it, "D_FADEOUTLEN", fade_out)
  _log(log, "info", "item.set_fade [" .. track_idx .. "," .. item_idx .. "] in=" .. fade_in .. " out=" .. fade_out)
  return { ok = true, affected = { { kind = "item", track = track_idx, item = item_idx } } }
end

function std_item.set_mute(track_idx, item_idx, muted, log)
  local it = _get(track_idx, item_idx)
  if not it then return { ok = false, reason = "blocked:item_not_found" } end
  reaper.SetMediaItemInfo_Value(it, "B_MUTE", muted and 1 or 0)
  _log(log, "info", "item.set_mute [" .. track_idx .. "," .. item_idx .. "] -> " .. tostring(muted))
  return { ok = true, affected = { { kind = "item", track = track_idx, item = item_idx } } }
end

-- 在 abs_time 处切开 item; 返回右半 item 的索引 (split 后左半保持 item_idx)
function std_item.split_at(track_idx, item_idx, abs_time, log)
  local it = _get(track_idx, item_idx)
  if not it then return { ok = false, reason = "blocked:item_not_found" } end
  local pos = reaper.GetMediaItemInfo_Value(it, "D_POSITION")
  local len = reaper.GetMediaItemInfo_Value(it, "D_LENGTH")
  if abs_time <= pos or abs_time >= pos + len then
    return { ok = false, reason = "blocked:split_outside_item" }
  end
  local right = reaper.SplitMediaItem(it, abs_time)
  _log(log, "info", "item.split_at [" .. track_idx .. "," .. item_idx .. "] @ " .. abs_time)
  return { ok = true, value = { right_item_index = item_idx + 1 },
           affected = { { kind = "item", track = track_idx, item = item_idx },
                        { kind = "item", track = track_idx, item = item_idx + 1 } } }
end

function std_item.delete(track_idx, item_idx, log)
  local it = _get(track_idx, item_idx)
  if not it then return { ok = false, reason = "blocked:item_not_found" } end
  local tr = reaper.GetTrack(0, track_idx)
  reaper.DeleteTrackMediaItem(tr, it)
  _log(log, "info", "item.delete [" .. track_idx .. "," .. item_idx .. "]")
  return { ok = true, affected = { { kind = "item", track = track_idx, item = item_idx } } }
end

-- 导入音频到轨道: abs_pos 为 item 放置位置 (经 edit cursor); 路径必须绝对
-- 成功判定按 item 计数增量 (InsertMedia 返回值语义不可靠, codex M3 finding)
-- 副作用: 选中态与 edit cursor 会恢复
function std_item.insert_media(track_idx, abs_path, abs_pos, log)
  if abs_path:sub(1, 1) ~= "/" then
    return { ok = false, reason = "blocked:path_not_absolute" }
  end
  local tr = reaper.GetTrack(0, track_idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  -- creation 身份策略: (轨道, 源文件 basename, 位置±1ms, 源长度±1ms) 已存在则复用
  -- 不用绝对路径全等: REAPER 保存时可能重定位/复制媒体 (实测: 源被复制到
  -- 源目录 Media/ 子目录, RPP 内 FILE 改写), 绝对路径比对会漏匹配
  local want_base = abs_path:match("[^/]+$")
  local target_src = reaper.PCM_Source_CreateFromFile(abs_path)
  local want_len = target_src and reaper.GetMediaSourceLength(target_src) or nil
  if target_src then reaper.PCM_Source_Destroy(target_src) end
  for i = 0, reaper.CountTrackMediaItems(tr) - 1 do
    local it = reaper.GetTrackMediaItem(tr, i)
    local pos = reaper.GetMediaItemInfo_Value(it, "D_POSITION")
    if math.abs(pos - abs_pos) < 0.001 then
      local take = reaper.GetActiveTake(it)
      if take then
        local src = reaper.GetMediaItemTake_Source(take)
        local src_file = reaper.GetMediaSourceFileName(src, "")
        local len_ok = (not want_len)
            or math.abs(reaper.GetMediaSourceLength(src) - want_len) < 0.001
        if src_file:match("[^/]+$") == want_base and len_ok then
          _log(log, "info", "item.insert_media: found existing at item[" .. i .. "]")
          return { ok = true, value = { item_index = i, existed = true },
                   affected = { { kind = "item", track = track_idx, item = i } } }
        end
      end
    end
  end
  local n_before = reaper.CountTrackMediaItems(tr)
  local prev_cursor = reaper.GetCursorPosition()
  local prev_sel = {}
  for i = 0, reaper.CountSelectedTracks(0) - 1 do
    prev_sel[#prev_sel + 1] = reaper.GetSelectedTrack(0, i)
  end
  reaper.SetOnlyTrackSelected(tr)
  reaper.SetEditCurPos(abs_pos, false, false)
  reaper.InsertMedia(abs_path, 0)  -- 0=add to current track at edit cursor
  local n_after = reaper.CountTrackMediaItems(tr)
  -- 恢复副作用
  reaper.SetEditCurPos(prev_cursor, false, false)
  reaper.Main_OnCommand(40297, 0)  -- Track: Unselect all tracks
  for _, t in ipairs(prev_sel) do reaper.SetTrackSelected(t, true) end
  if n_after <= n_before then
    return { ok = false, reason = "blocked:insert_media_failed" }
  end
  _log(log, "info", "item.insert_media track=" .. track_idx .. " @" .. abs_pos .. " " .. abs_path)
  return { ok = true, value = { item_index = n_after - 1, existed = false },
           affected = { { kind = "item", track = track_idx } } }
end

function std_item.list_on_track(track_idx, log)
  local tr = reaper.GetTrack(0, track_idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  local out = {}
  for i = 0, reaper.CountTrackMediaItems(tr) - 1 do
    local info = std_item.get_info(track_idx, i)
    if info.ok then out[#out + 1] = info.value end
  end
  return { ok = true, value = out }
end
