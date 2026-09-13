-- stdlib/midi.lua — (粘贴片段: 全文拼入你的脚本即可用; 无 return, 无 require)
-- MIDI: 建 item + 插音符/CC + PPQ 换算
std_midi = std_midi or {}

local function _log(log, level, msg) if log then log(level, msg) end end

-- 在 track 上 [start_sec, end_sec] 建空白 MIDI item
-- creation 身份策略: (轨道, start±1ms, end±1ms) 已有 MIDI item 则复用
function std_midi.create_item(track_idx, start_sec, end_sec, log)
  local tr = reaper.GetTrack(0, track_idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  for i = 0, reaper.CountTrackMediaItems(tr) - 1 do
    local it = reaper.GetTrackMediaItem(tr, i)
    local pos = reaper.GetMediaItemInfo_Value(it, "D_POSITION")
    local len = reaper.GetMediaItemInfo_Value(it, "D_LENGTH")
    if math.abs(pos - start_sec) < 0.001
        and math.abs(pos + len - end_sec) < 0.001
        and reaper.TakeIsMIDI(reaper.GetActiveTake(it)) then
      _log(log, "info", "midi.create_item: found existing at item[" .. i .. "]")
      return { ok = true, value = { item_index = i, existed = true },
               affected = { { kind = "item", track = track_idx, item = i } } }
    end
  end
  local item = reaper.CreateNewMIDIItemInProj(tr, start_sec, end_sec, false)
  _log(log, "info", "midi.create_item track=" .. track_idx .. " [" .. start_sec .. "," .. end_sec .. "]")
  return { ok = true, value = { item_index = reaper.CountTrackMediaItems(tr) - 1, existed = false },
           affected = { { kind = "item", track = track_idx } } }
end

-- 插单个音符: pitch 0-127, vel 1-127, 时间秒 (内部转 PPQ)
-- creation 幂等: 同 pitch+start 音符已存在则更新 vel/end (find-before-create)
function std_midi.insert_note(track_idx, item_idx, pitch, vel, start_sec, end_sec, log)
  local tr = reaper.GetTrack(0, track_idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  local item = reaper.GetTrackMediaItem(tr, item_idx)
  if not item then return { ok = false, reason = "blocked:item_not_found" } end
  local take = reaper.GetActiveTake(item)
  local ppq_start = reaper.MIDI_GetPPQPosFromProjTime(take, start_sec)
  local ppq_end = reaper.MIDI_GetPPQPosFromProjTime(take, end_sec)
  for i = 0, select(2, reaper.MIDI_CountEvts(take)) - 1 do
    local _, _, _, s, _, _, p = reaper.MIDI_GetNote(take, i)
    if p == pitch and math.abs(s - ppq_start) < 0.5 then
      reaper.MIDI_SetNote(take, i, false, false, ppq_start, ppq_end, 0, pitch, vel, true)
      reaper.MIDI_Sort(take)
      _log(log, "info", "midi.insert_note: update existing pitch=" .. pitch)
      return { ok = true, value = { updated = true },
               affected = { { kind = "midi_note", track = track_idx, item = item_idx } } }
    end
  end
  reaper.MIDI_InsertNote(take, false, false, ppq_start, ppq_end, 0, pitch, vel, true)
  reaper.MIDI_Sort(take)
  _log(log, "info", "midi.insert_note pitch=" .. pitch .. " [" .. start_sec .. "," .. end_sec .. "]")
  return { ok = true, value = { updated = false },
           affected = { { kind = "midi_note", track = track_idx, item = item_idx } } }
end

-- creation 幂等: 同 cc_num+time(±0.5ppq) 已存在则更新值 (cursor Low)
function std_midi.insert_cc(track_idx, item_idx, cc_num, val, at_sec, log)
  local tr = reaper.GetTrack(0, track_idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  local item = reaper.GetTrackMediaItem(tr, item_idx)
  if not item then return { ok = false, reason = "blocked:item_not_found" } end
  local take = reaper.GetActiveTake(item)
  local ppq = reaper.MIDI_GetPPQPosFromProjTime(take, at_sec)
  for i = 0, select(3, reaper.MIDI_CountEvts(take)) - 1 do
    local _, _, _, ppos, _, _, cnum = reaper.MIDI_GetCC(take, i)
    if cnum == cc_num and math.abs(ppos - ppq) < 0.5 then
      reaper.MIDI_SetCC(take, i, false, false, ppq, 0xB0, 0, cc_num, val, true)
      reaper.MIDI_Sort(take)
      return { ok = true, value = { updated = true },
               affected = { { kind = "midi_cc", track = track_idx, item = item_idx } } }
    end
  end
  reaper.MIDI_InsertCC(take, false, false, ppq, 0xB0, 0, cc_num, val)
  reaper.MIDI_Sort(take)
  return { ok = true, value = { updated = false },
           affected = { { kind = "midi_cc", track = track_idx, item = item_idx } } }
end

function std_midi.count_events(track_idx, item_idx, log)
  local tr = reaper.GetTrack(0, track_idx)
  if not tr then return { ok = false, reason = "blocked:no_track_at_index" } end
  local item = reaper.GetTrackMediaItem(tr, item_idx)
  if not item then return { ok = false, reason = "blocked:item_not_found" } end
  local take = reaper.GetActiveTake(item)
  -- MIDI_CountEvts: retval, notes, ccs, textsyx (首值为总有效标志)
  local _, notes, ccs, texts = reaper.MIDI_CountEvts(take)
  return { ok = true, value = { notes = notes, ccs = ccs, text_events = texts } }
end
