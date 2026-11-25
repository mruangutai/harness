# Observations — harness-qa — FEAT-2537-registry-record-cleanup

- 2026-11-25: Swapping a module via INFLIGHT_REGISTRY_DIR needs a full copy of bin/ beside it — subprocess/CLI cases (case7, 9, 35, 41, feat65) import siblings (harness_boundary, harness_merge) from the swapped dir and red with ModuleNotFoundError otherwise, an environment red unrelated to the mutant.
- 2026-11-25: A scripted shape-matrix probe (base vs candidate, strict+writer, ret/stderr/bytes) surfaced a surviving mutant (default missing schema_version to 2) that the named witness case missed; case-by-case fixtures cover only the shapes the author enumerated.
- 2026-11-25: check-state INV-26 reads the live GitHub board, so running it at a review pin that predates a station-move commit reports a false projection mismatch; compare against the feature tip before calling it a defect.
- 2026-11-25: With a full bin/ copy beside the swapped module, the a24eacee base swap at 635b5c15 reds only the 12 case-18 lines; the CLI-subprocess reds (7, 9, 35, 40, 41, feat65) the fix receipt reports do not occur, confirming they were a partial-copy harness artifact.
- 2026-11-25: case 18's _file_bytes reads in text mode (universal newlines), so a writer emitting CRLF bytes survives 200/200 — 'raw bytes' assertions should open files 'rb' to be literal.
- 2026-11-25: r-4 c1-completion: a stderr-noise mutant (print on _parse entry) reds only 2 of 3 silent case-18 rows; the missing-file writer never reaches _parse, so that silent row is unexercised by a _parse-level stderr mutant.
- 2026-11-25: r-4: CRLF writer mutant red 8/200 at c67ba818 and green 200/200 against the 635b5c15 test file — the one-factor control that attributes the literal-bytes witness to the c1-completion edit.
