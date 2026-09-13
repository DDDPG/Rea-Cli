-- stdlib/snapshot.lua — (粘贴片段: 全文拼入你的脚本即可用; 无 return, 无 require)
-- 全量快照: 一次调用拿全工程结构 (替代 N+1 查询; 源自 MCP_TracksSnapshot 模式)
std_snapshot = std_snapshot or {}

function std_snapshot.tracks()
  local out = {}
  for i = 0, reaper.CountTracks(0) - 1 do
    local tr = reaper.GetTrack(0, i)
    local _, name = reaper.GetTrackName(tr)
    local items = {}
    for j = 0, reaper.CountTrackMediaItems(tr) - 1 do
      local it = reaper.GetTrackMediaItem(tr, j)
      items[#items + 1] = {
        index = j,
        position = reaper.GetMediaItemInfo_Value(it, "D_POSITION"),
        length = reaper.GetMediaItemInfo_Value(it, "D_LENGTH"),
        mute = reaper.GetMediaItemInfo_Value(it, "B_MUTE") == 1,
      }
    end
    out[#out + 1] = {
      index = i, name = name,
      volume = reaper.GetMediaTrackInfo_Value(tr, "D_VOL"),
      pan = reaper.GetMediaTrackInfo_Value(tr, "D_PAN"),
      mute = reaper.GetMediaTrackInfo_Value(tr, "B_MUTE") == 1,
      solo = reaper.GetMediaTrackInfo_Value(tr, "I_SOLO") > 0,
      guid = reaper.GetTrackGUID(tr),
      items = items,
    }
  end
  return { ok = true, value = out }
end

function std_snapshot.project()
  local _, projfn = reaper.EnumProjects(-1, "")
  local markers = {}
  local _, nmk, nrgn = reaper.CountProjectMarkers(0)
  for i = 0, nmk + nrgn - 1 do
    local _, isrgn, pos, rgnend, name, midx = reaper.EnumProjectMarkers(i)
    markers[#markers + 1] = { index = midx, pos = pos, name = name,
                              is_region = isrgn, region_end = isrgn and rgnend or nil }
  end
  return { ok = true, value = {
    path = projfn,
    tempo = reaper.Master_GetTempo(),
    track_count = reaper.CountTracks(0),
    markers = markers,
    dirty = reaper.IsProjectDirty(0) == 1,
  } }
end
