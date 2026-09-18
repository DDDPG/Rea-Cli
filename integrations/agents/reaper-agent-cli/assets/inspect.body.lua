-- Composition body, not a standalone ReaScript. See build_inspector.py.
-- Read-only project inspection; the bundled entry controls proof and shutdown.
local function body()
  local tracks = {}
  for index = 0, reaper.CountTracks(0) - 1 do
    local track = reaper.GetTrack(0, index)
    local _, name = reaper.GetTrackName(track)
    tracks[#tracks + 1] = {
      index = index,
      name = name,
      volume_linear = reaper.GetMediaTrackInfo_Value(track, "D_VOL"),
      pan = reaper.GetMediaTrackInfo_Value(track, "D_PAN"),
    }
  end
  RUN.result = {
    reaper_version = reaper.GetAppVersion(),
    os = reaper.GetOS(),
    resource_path = reaper.GetResourcePath(),
    tracks = tracks,
  }
end
