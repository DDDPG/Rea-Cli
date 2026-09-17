# Independently authored playable REAPER showcase

Create a new, self-contained session from these requirements. Do not read, execute,
copy or import any existing showcase generator, finished project, repository demo
or another harness's output. You may use only installed toolkit documentation,
packaged generic CLI resources/API metadata, native REAPER API help and your own code.
The musical note choices are yours; exact identity to a prior composition is not required.

- Eight bars, 120 BPM, 4/4 (16 seconds), C–Am–F–G over two bars per chord.
- Seven named tracks in this order: `01 RHYTHM`, `02 Pulse`, `03 Ticks`, `04 Bass`,
  `05 Chords`, `06 Melody`, `07 Parallel bus`.
- RHYTHM is a folder containing Pulse and Ticks. Five instrument tracks use built-in
  ReaSynth, real editable MIDI, no external samples and no Python-synthesized substitute.
- Pulse has two MIDI items split at 8 seconds; Ticks, Bass, Chords and Melody span 16 seconds.
- Bass has a three-point pan envelope; Chords a five-point volume envelope and two
  playable MIDI takes with distinct voicings. Melody has exactly 16 notes.
- Parallel bus receives a quiet send from Chords. Add three markers and two regions,
  0–16 time selection, track colors, and project notes.
- Melody ReaEQ: enabled high-pass at 100 Hz, other bands disabled.
- Chords ReaVerbate: Room size 90, dampening 20, Wet −12 dB, Dry 0 dB.
- Bass ReaComp: threshold −15 dB, manual makeup +3 dB using plugin Wet output,
  automatic makeup off. This is distinct from host FX wet mix.
- Master ReaLimit: threshold −4.5 dB and ceiling −1 dB.
- Use host-discovered parameter names/units and validate actual formatted values.
  No third-party plugins. Avoid clipping; the exact note voicing is not prescribed.
- Produce `output/Show-Session.rpp` and stereo `output/preview.wav` at 48 kHz,
  24 seconds total (16 seconds of arrangement plus 8 seconds tail).
- Author your own Python/Lua in this workspace. Run the CLI environment check, validate
  Lua, execute through rac, save, reopen in a second isolated host run and check the
  requirements using native APIs. Render through rac.media and check audio numerically.
- Save `output/acceptance.json` with each requirement/check, operation errors, proof and
  manifest paths. Deliver readable source scripts, saved project, WAV and proof artifacts.
  A successful process exit alone is not acceptance. Fix diagnosed failures within this
  task, retaining failed attempts and using new work directories when needed.

Work only in this fresh workspace and dedicated toolkit resources. Do not modify the
user's other projects, native REAPER configuration, global harness settings or credentials.
Do not use MCP, web browsing, delegated agents or any prebuilt showcase solution.
