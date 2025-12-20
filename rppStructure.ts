import { RPPNode } from './types';

export const RPP_STRUCTURE: RPPNode = {
  key: "<REAPER_PROJECT>",
  values: "0.1 \"7.48/macOS-arm64\" 1766225573",
  sectionId: "project",
  children: [
    { key: "TITLE", values: "\"Project Title\"", sectionId: "project" },
    { key: "AUTHOR", values: "KDW", sectionId: "project" },
    { 
      key: "<NOTES", 
      values: "0 0", 
      sectionId: "project",
      children: [
        { key: "|This is Project Settings Note", sectionId: "project" }
      ]
    },
    { key: "RIPPLE", values: "0 5", sectionId: "project" },
    { key: "GROUPOVERRIDE", values: "1 0 0 0", sectionId: "project" },
    { key: "AUTOXFADE", values: "192", sectionId: "project" },
    { key: "ENVATTACH", values: "1", sectionId: "project" },
    { key: "MIXERUIFLAGS", values: "16 3", sectionId: "project" },
    { key: "PEAKGAIN", values: "1.21", sectionId: "project" },
    { key: "PANLAW", values: "1", sectionId: "project" },
    { key: "PANMODE", values: "5", sectionId: "project" },
    { key: "CURSOR", values: "16.552", sectionId: "project" },
    { key: "VZOOMEX", values: "6.86831951 0", sectionId: "project" },
    { key: "RECMODE", values: "1", sectionId: "project" },
    { key: "SMPTESYNC", values: "0 30 90 45 1000 300 0 -0.00332 1 23 12", sectionId: "project" },
    { key: "LOOP", values: "0", sectionId: "project" },
    { key: "RECORD_PATH", values: "\"Audio files\" \"\"", sectionId: "project" },
    { key: "RENDER_PATTERN", values: "$project-mix", sectionId: "project" },
    { key: "COMP", values: "1 \"Comp 1\"", sectionId: "project" },
    { key: "TEMPO", values: "116 4 4 0", sectionId: "project" },
    { key: "PLAYRATE", values: "1 0 0.75 1.5", sectionId: "project" },
    { key: "SELECTION", values: "194.486 213.107", sectionId: "project" },
    { key: "MASTERAUTOMODE", values: "0", sectionId: "project" },
    { key: "MASTERTRACKHEIGHT", values: "74 0", sectionId: "project" },
    { key: "MASTERMUTESOLO", values: "0", sectionId: "project" },
    { key: "MASTER_VOLUME", values: "1 0 -1 -1 1", sectionId: "project" },
    { key: "MASTER_PANMODE", values: "-1", sectionId: "project" },
    { key: "MASTER_FX", values: "1", sectionId: "project" },
    { key: "MASTER_SEL", values: "0", sectionId: "project" },
    {
      key: "<MASTERFXLIST>",
      sectionId: "project",
      children: [
        { key: "WNDRECT", values: "763 1603 981 394", sectionId: "fx" },
        { key: "SHOW", values: "0", sectionId: "fx" },
        { key: "DOCKED", values: "0", sectionId: "fx" }
      ]
    },
    { key: "MARKER", values: "1 10.344 \"\" 1 0 1 B {GUID} 0", sectionId: "project" },
    {
      key: "<TRACK",
      values: "{CD21E59C-94D9-1F4A-959F-69580F714C49}",
      sectionId: "track",
      children: [
        { key: "NAME", values: "receive", sectionId: "track" },
        { key: "PEAKCOL", values: "33513868", sectionId: "track" },
        { key: "BEAT", values: "-1", sectionId: "track" },
        { key: "AUTOMODE", values: "0", sectionId: "track" },
        { key: "PANMODE", values: "6", sectionId: "track" },
        { key: "PANLAWFLAGS", values: "3", sectionId: "track" },
        { key: "VOLPAN", values: "1 -0.596 1 -1 0.196", sectionId: "track" },
        { key: "MUTESOLO", values: "0 0 0", sectionId: "track" },
        { key: "IPHASE", values: "0", sectionId: "track" },
        { key: "PLAYOFFS", values: "0 1", sectionId: "track" },
        { key: "ISBUS", values: "0 0", sectionId: "track" },
        { key: "BUSCOMP", values: "0 0 0 0 0", sectionId: "track" },
        { key: "SHOWINMIX", values: "1 1 0.314286 1 0.675958 0 0 0 0", sectionId: "track" },
        { key: "FIXEDLANES", values: "8 0 0 0 0", sectionId: "track" },
        { key: "LANESOLO", values: "1 0 0 0 0 0 0 0", sectionId: "track" },
        { key: "LANENAME", values: "C1 lane2", sectionId: "track" },
        { key: "SEL", values: "0", sectionId: "track" },
        { key: "REC", values: "1 1024 1 0 0 0 0 0", sectionId: "track" },
        { key: "TRACKHEIGHT", values: "0 0 0 0 0 0 0", sectionId: "track" },
        { key: "INQ", values: "0 0 0 0.5 99 0 0 100", sectionId: "track" },
        { key: "NCHAN", values: "4", sectionId: "track" },
        { key: "<RECCFG", values: "0", sectionId: "track", children: [{key: "ZXZhdyEkAQ==", sectionId: "track"}]},
        { key: "FX", values: "1", sectionId: "track" },
        { key: "PERF", values: "0", sectionId: "track" },
        { key: "AUXRECV", values: "1 0 1 0 0 0 0 0 0 -1:U 0 -1 ''", sectionId: "track" },
        { key: "MIDIOUT", values: "-1", sectionId: "track" },
        { key: "MAINSEND", values: "1 0", sectionId: "track" },
        { key: "HWOUT", values: "2 0 1 0 0 0 0 -1:U -1", sectionId: "track" },
        { 
          key: "<FXCHAIN", 
          sectionId: "fx",
          children: [
            { key: "WNDRECT", values: "488 1146 1181 626", sectionId: "fx" },
            { key: "SHOW", values: "0", sectionId: "fx" },
            { key: "LASTSEL", values: "1", sectionId: "fx" },
            { key: "DOCKED", values: "0", sectionId: "fx" },
            { key: "BYPASS", values: "1 0 0", sectionId: "fx" },
            { 
              key: "<VST", 
              values: "\"VST3: bx_digital V3 (Plugin Alliance)\" \"bx_digital V3.vst3\" 0 \"\" 1846886468{5653546278643362785F646967697461} \"\"", 
              sectionId: "fx",
              children: [
                { key: "REAVbu5e7f4CAAAAAQAAAAAAAAACAAAAAAAAAAIAAAABAAAAAAAAAAIAAAAAAAAAIBQAAAEAAAD//wAA", sectionId: "fx" },
                { key: "CAoAAAEAAABCWENrAAAKAEVmY3QAAAnsUG10cgAACdQAAAncAAAAfQAAAAQAAAAAQnlwYQAAAAAAAAAAAAAAAAAAAABCYW5rAAAAAAAAAAAAAAAAAAAAAEduSW4/AAAA", sectionId: "fx" },
                { key: "dGhpcyBpcyBqdXN0IG1vY2sgZGF0YS4uLiBwbGVhc2UgaW1hZ2luZSBhIHJlYWwgcGx1Z2luIHN0YXRlIGhlcmU=", sectionId: "fx" }
              ]
            },
            { key: "WET", values: "0.329946 0", sectionId: "fx" },
            { key: "FLOATPOS", values: "421 1163 1024 731", sectionId: "fx" },
            { key: "FXID", values: "{33537175-3F37-6E48-9243-5A83ED47FABD}", sectionId: "fx" },
            { 
              key: "<PARMENV", 
              values: "0:1115254881 0 1 0.5 \"Bypass / bx_digital V3\"", 
              sectionId: "envelope",
              children: [
                { key: "EGUID", values: "{4DAEBD23-A6E5-EA41-973A-A17D6336064D}", sectionId: "envelope" },
                { key: "ACT", values: "0 -1", sectionId: "envelope" },
                { key: "VIS", values: "0 1 1", sectionId: "envelope" },
                { key: "LANEHEIGHT", values: "0 0", sectionId: "envelope" },
                { key: "ARM", values: "0", sectionId: "envelope" },
                { key: "DEFSHAPE", values: "1 -1 -1", sectionId: "envelope" },
                { key: "PT", values: "4.138 0 1", sectionId: "envelope" }
              ] 
            },
            { key: "WAK", values: "0 0", sectionId: "fx" },
            { key: "BYPASS", values: "0 0 0", sectionId: "fx" },
            { 
              key: "<VST", 
              values: "\"VST3: Pro-Q 4 (FabFilter)\" \"FabFilter Pro-Q 4.vst3\" 0 \"\" 934538646{ED57BD725C60467EA64DD2F400758B6F} \"\"", 
              sectionId: "fx",
              children: [
                { key: "lu2zN+5e7f4EAAAAAQAAAAAAAAACAAAAAAAAAAQAAAAAAAAACAAAAAAAAAACAAAAAQAAAAAAAAACAAAAAAAAAMYKAAABAAAAAAAAAA==", sectionId: "fx" },
                { key: "eAkAAAEAAABGRkJTAQAAAFgCAAAAAIA/AAAAAHia1EAAAAAAAAAAPwAAAAAAAABAAAAAQAAAgD8AAAAAAACAPwAAgD8AAIA/AABIQgAASEIAAAAAAAAAAHia1EDczzhB", sectionId: "fx" },
                { key: "YW5vdGhlciBwbGFjZWhvbGRlciBmb3IgdGhlIHZzdCBkYXRhIGJsb2NrIHdoaWNoIGlzIHR5cGljYWxseSB2ZXJ5IGxvbmc=", sectionId: "fx" }
              ]
            },
            { key: "PRESETNAME", values: "\"Program 1\"", sectionId: "fx" },
            { key: "FLOATPOS", values: "794 1374 950 623", sectionId: "fx" },
            { key: "FXID", values: "{26C746C5-5741-9F41-A20F-1EFB1A52E098}", sectionId: "fx" },
            { 
              key: "<PARMENV", 
              values: "737:bypass 0 1 0.5 \"Bypass / Pro-Q 4\"", 
              sectionId: "envelope",
              children: [
                { key: "EGUID", values: "{F54364D5-ED6E-D84E-BDE0-BFEAA484745E}", sectionId: "envelope" },
                { key: "ACT", values: "0 -1", sectionId: "envelope" },
                { key: "VIS", values: "0 1 1", sectionId: "envelope" },
                { key: "LANEHEIGHT", values: "0 0", sectionId: "envelope" },
                { key: "ARM", values: "0", sectionId: "envelope" },
                { key: "DEFSHAPE", values: "1 -1 -1", sectionId: "envelope" },
                { key: "PT", values: "4.138 0 1", sectionId: "envelope" }
              ] 
            },
            { key: "WAK", values: "0 0", sectionId: "fx" }
          ]
        },
        {
          key: "<ITEM",
          sectionId: "item",
          children: [
            { key: "POSITION", values: "2.0689", sectionId: "item" },
            { key: "SNAPOFFS", values: "0", sectionId: "item" },
            { key: "LENGTH", values: "2.0689", sectionId: "item" },
            { key: "LOOP", values: "1", sectionId: "item" },
            { key: "ALLTAKES", values: "0", sectionId: "item" },
            { key: "FADEIN", values: "2 0 0 2 0 1 1", sectionId: "item" },
            { key: "FADEOUT", values: "1 0.01 0 3 0 0 0", sectionId: "item" },
            { key: "MUTE", values: "0 0", sectionId: "item" },
            { key: "BEAT", values: "1", sectionId: "item" },
            { key: "SEL", values: "0", sectionId: "item" },
            { key: "IGUID", values: "{455A7CC8-0CE8-D049-9BEC-44911C9736A2}", sectionId: "item" },
            { key: "COMP", values: "1 1 0", sectionId: "item" },
            { key: "NAME", values: "test_audio.mp3", sectionId: "item" },
            { key: "VOLPAN", values: "1 0 1 1", sectionId: "item" },
            { key: "SOFFS", values: "0", sectionId: "item" },
            { key: "PLAYRATE", values: "1.000 1 33 -65536 0 0.0023", sectionId: "item" },
            { key: "CHANMODE", values: "0", sectionId: "item" },
            { key: "GUID", values: "{4BCE0917-FE2F-F24E-8B32-12144D8D0F44}", sectionId: "item" },
            { key: "TKM", values: "22.24 take_marker 0 0", sectionId: "item" },
            { 
              key: "<SOURCE", 
              values: "MP3", 
              sectionId: "source",
              children: [
                 { key: "FILE", values: "\"/path/to/project/audio/test_audio.mp3\" 1", sectionId: "source" }
              ]
            },
            {
              key: "<PANENV",
              sectionId: "envelope",
              children: [
                { key: "ACT", values: "0 -1", sectionId: "envelope" },
                { key: "VIS", values: "0 1 1", sectionId: "envelope" },
                { key: "PT", values: "0 0 0", sectionId: "envelope" },
                { key: "PT", values: "2.069 0 0", sectionId: "envelope" }
              ]
            },
            { key: "TAKE", values: "SEL", sectionId: "take" },
            { key: "NAME", values: "\"test_audio.wav\"", sectionId: "take" },
            { key: "TAKEVOLPAN", values: "0 1 0", sectionId: "take" },
            { key: "SOFFS", values: "0", sectionId: "take" },
            { key: "PLAYRATE", values: "2 1 0 -1 0 0.0025", sectionId: "take" },
            { key: "CHANMODE", values: "0", sectionId: "take" },
            { key: "GUID", values: "{ADC20F9D-1BBD-1F40-B8C8-461BF438D098}", sectionId: "take" },
            { 
              key: "<SOURCE", 
              values: "WAVE", 
              sectionId: "source",
              children: [
                { key: "FILE", values: "\"Audio files/test_audio.wav\"", sectionId: "source" }
              ]
            }
          ]
        },
        {
          key: "<ITEM",
          sectionId: "item",
          comment: "MIDI Item Example",
          children: [
            { key: "POSITION", values: "4.138", sectionId: "item" },
            { key: "LENGTH", values: "39.311", sectionId: "item" },
            { key: "LOOP", values: "1", sectionId: "item" },
            { key: "NAME", values: "07-MIDI", sectionId: "item" },
            { 
              key: "<SOURCE", 
              values: "MIDI", 
              sectionId: "source",
              children: [
                { key: "HASDATA", values: "1 960 QN", sectionId: "source" },
                { key: "CCINTERP", values: "32", sectionId: "source" },
                { key: "e", values: "3840 90 3e 31", sectionId: "source" },
                { key: "e", values: "5760 80 3e 00", sectionId: "source" },
                { key: "E", values: "960 90 41 66", sectionId: "source" },
                { key: "GUID", values: "{3EA4022F-E009-BF41-9C78-A1A6097CB1CA}", sectionId: "source" },
                { key: "IGNTEMPO", values: "1 116 4 4", sectionId: "source" },
                { key: "EVTFILTER", values: "0 -1 -1 -1 -1 0 0 0 0 -1 -1 -1 -1 0 -1 0 -1 -1", sectionId: "source" },
                { key: "VELLANE", values: "-1 100 0 0 1", sectionId: "source" },
                { key: "CFGEDIT", values: "1 1 0 1 0 0 1 1 1 1 1 0.125 ...", sectionId: "source" }
              ]
            }
          ]
        },
      ]
    },
    {
      key: "<EXTENSIONS",
      sectionId: "project",
      children: [
         { 
           key: "<SWSAUTOCOLOR", 
           sectionId: "project",
           children: [
             { key: "{CD21E59C...}", values: "59531775 \"\" \"\" \"\"", sectionId: "project"}
           ]
         }
      ]
    }
  ]
};
