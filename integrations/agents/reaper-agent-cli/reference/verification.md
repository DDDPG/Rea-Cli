# Acceptance layers

- Structure: reparse the saved file and check tracks/items/takes, GUIDs, sources,
  routing, markers/regions and envelope nodes. Assert expected values, not only parse.
- Host: reopen the saved file in another isolated run; use native APIs to inspect
  plugin parameters, MIDI and envelopes. Require proof.ok and absence of operation errors.
- Audio: explicitly render via rac.media.render into a new directory, decode using
  read_source(result), check frames/sample rate/channels, finite samples, non-silence
  and peak. A musical showcase is not a byte-for-byte audio comparison.
- Evidence: retain authored source, doctor output, proofs, saved projects, manifests,
  hashes and concise check results. A failed layer is a failed deliverable for that claim.

`run()` can return a Proof with ok=false rather than throwing; inspect it.
`from rac.verify import expect` checks supported project/audio assertions.
A bounded host timeout should leave diagnosis; do not kill the user's other sessions.
A host-supported edit must be saved, reopened and checked when persistence matters.
