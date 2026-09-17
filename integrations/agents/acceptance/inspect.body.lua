-- Independent readback only. Does not create or repair the candidate.
local function body()
  local function effects(track)
    local out = {}
    for f=0,reaper.TrackFX_GetCount(track)-1 do
      local _, name = reaper.TrackFX_GetFXName(track,f,'')
      local params = {}
      local bands = {}
      for p=0,reaper.TrackFX_GetNumParams(track,f)-1 do
        local _, key = reaper.TrackFX_GetParamName(track,f,p,'')
        local _, formatted = reaper.TrackFX_GetFormattedParamValue(track,f,p,'')
        local valid,bandtype,bandidx,paramtype = reaper.TrackFX_GetEQParam(track,f,p)
        if valid and paramtype==0 then
          bands[#bands+1]={type=bandtype,index=bandidx,enabled=reaper.TrackFX_GetEQBandEnabled(track,f,bandtype,bandidx),frequency=formatted}
        end
        params[#params+1]={name=key,formatted=formatted,value=reaper.TrackFX_GetParam(track,f,p)}
      end
      out[#out+1]={name=name,enabled=reaper.TrackFX_GetEnabled(track,f),params=params,bands=bands}
    end
    return out
  end
  local tracks={}
  for t=0,reaper.CountTracks(0)-1 do
    local track=reaper.GetTrack(0,t)
    local _,name=reaper.GetTrackName(track)
    local items={}
    for i=0,reaper.CountTrackMediaItems(track)-1 do
      local item=reaper.GetTrackMediaItem(track,i)
      local takes={}
      for k=0,reaper.CountTakes(item)-1 do
        local take=reaper.GetTake(item,k)
        local pitches={}
        local ok,notes=reaper.MIDI_CountEvts(take)
        if ok then
          for n=0,notes-1 do
            local _,_,_,startppq,endppq,channel,pitch,velocity=reaper.MIDI_GetNote(take,n)
            pitches[#pitches+1]={pitch=pitch,velocity=velocity,start_time=reaper.MIDI_GetProjTimeFromPPQPos(take,startppq),startppq=startppq,endppq=endppq}
          end
        end
        takes[#takes+1]={midi=reaper.TakeIsMIDI(take),notes=ok and notes or 0,pitches=pitches}
      end
      items[#items+1]={position=reaper.GetMediaItemInfo_Value(item,'D_POSITION'),length=reaper.GetMediaItemInfo_Value(item,'D_LENGTH'),takes=takes}
    end
    local envelopes={}
    for e=0,reaper.CountTrackEnvelopes(track)-1 do
      local env=reaper.GetTrackEnvelope(track,e);local _,ename=reaper.GetEnvelopeName(env,'')
      envelopes[#envelopes+1]={name=ename,points=reaper.CountEnvelopePoints(env)}
    end
    local receives={}
    for i=0,reaper.GetTrackNumSends(track,-1)-1 do
      local src=reaper.GetTrackSendInfo_Value(track,-1,i,'P_SRCTRACK')
      local _,srcname=reaper.GetTrackName(src)
      receives[#receives+1]={source=srcname,volume=reaper.GetTrackSendInfo_Value(track,-1,i,'D_VOL')}
    end
    tracks[#tracks+1]={name=name,folder=reaper.GetMediaTrackInfo_Value(track,'I_FOLDERDEPTH'),color=reaper.GetTrackColor(track),items=items,envelopes=envelopes,fx=effects(track),receives=receives}
  end
  local _,markers,regions=reaper.CountProjectMarkers(0)
  local first,last=reaper.GetSet_LoopTimeRange(false,false,0,0,false)
  local notes=reaper.GetSetProjectNotes(0,false,'')
  local numerator,denominator=reaper.TimeMap_GetTimeSigAtTime(0,0)
  RUN.result={time_signature={numerator,denominator},tracks=tracks,master_fx=effects(reaper.GetMasterTrack(0)),tempo=reaper.Master_GetTempo(),markers=markers,regions=regions,time_start=first,time_end=last,notes=notes,host=reaper.GetAppVersion()}
end
