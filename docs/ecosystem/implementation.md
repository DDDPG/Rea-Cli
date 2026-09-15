# Implementation record

P0: baseline archives and manifests retained; pre-existing changes committed separately.
P1: 181 source entries and 23 adopted field mappings share a deterministic JSON source.
P2/P3: independent lossless parser, parent-owned FX/take views, rac compatibility and schema diagnostics.
P4: monorepo paths and non-squashed ReaperDoc history imported; original siblings retained.
P5: explicit audio read/render/import APIs and deterministic NumPy example; zero import fades are deliberate.
P6: candidate builder, package checks, standalone agent bundle and cross-platform CI defined.

Native quoting now follows WDL's three delimiters with literal backslashes. The legacy
backslash-escape interpretation could misparse Windows directory paths before another
quoted value. The old rac fixtures still pass. Unrepresentable writes containing all
three delimiters and whitespace are rejected instead of emitting ambiguous host input.

The first live data run failed the final waveform assertion because REAPER added default
item fades. The import implementation now explicitly disables manual and automatic fades;
the second run passed at the original tolerance. Failure artifacts were retained locally.

Only macOS live results are claimed. GitHub Actions run 34756655368 passed all 22 jobs,
including Linux/macOS/Windows parser checks and Linux/macOS rac offline checks. Linux
candidate wheel isolation and 43 distribution checks passed. The first Windows run
exposed default-codepage decoding in an evidence test; explicit UTF-8 fixed all five
Python versions without changing runtime code. Existing
source attribution and the remaining package-index questions remain explicit in
publication.json; no package was uploaded.
The public set_field interface refuses fields without a verified write contract; low-level
set_raw/convenience setters remain raw patches, not claims of verified semantic writes.
