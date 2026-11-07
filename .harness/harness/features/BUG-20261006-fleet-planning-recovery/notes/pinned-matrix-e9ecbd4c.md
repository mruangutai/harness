# Pinned matrix receipt — e9ecbd4c

Review SHA: `e9ecbd4c4e4fc41d19402042b591f33b186b4b36`.
The configured active unit and integration commands each ran once, after T-02 and before any T-03 activation. Neither passed. This failed receipt must not be rewritten as a pass or silently replaced by another full run.

- `.agents/skills/harness/bin/run-unit-tests.py --kind unit`: exit 1; 55 files, 27.92s pool wall / 28.33s command wall. `test-digest-schemas.py` failed; other 54 files passed. Complete output: session artifact 277.
- `.agents/skills/harness/bin/run-unit-tests.py --kind integration`: exit 1; 83 files, 99.20s pool wall / 99.60s command wall. Five files failed: `test-checker-structure-locks.py`, `test-factory-integration.py`, `test-hooks-install.py`, `test-feature-corpus.py` and `test-station-argument-spelling.py`. Complete output: session artifact 278. The initial chat count of six was a counting error; the runner contains exactly these five failed-file headings.
- Pinned code grading ran against baseline `63cac11a3216aa8d34792665a05fcb185f7cf73b`; full output is session artifact 280. The pre-pin named reasons are in `build-verification-2026-10-18.md`; no unconditional grading pass is claimed.

## Hypotheses before corrective edits

1. The newly optional backend count violates OpenAI's strict object-shape contract because the property is not required. Preserve its optional caller semantics with two closed nested `anyOf` variants, each fully required, rather than exempting the schema from that guard. Falsifier: the existing strict-shape test still rejects the variants, or ordinary backend omission / explicit nonnegative counts fail real validation.
2. The new arbitrary-evidence read trigger dropped the original explicit digest path declarations, and broad recovery catches violate the established zero ceiling. Restore actual digest read declarations alongside arbitrary evidence triggering, and narrow handlers to the real boundary classes without increasing the ceiling. Falsifier: the structure-lock tool still reports missing reads or the real uncertain-outcome tests stop preserving durable intent.
3. Remaining board/corpus/merge/sweep fixtures omit the now-required binding provenance or call the old audit signature. Migrate fixtures to explicit, matching repository/board receipts and migrate every caller; never add a permissive production shim. Falsifier: valid migrated fixtures still fail, or invalid provenance no longer refuses.
4. The lifecycle checkpoint test asserts incidental prose phrasing/order and mutates exact strings no longer present. Delete that obsolete prose assertion and its private scaffolding, rather than re-pin wording. Preserve genuine CLI station acceptance tests. Falsifier: investigation finds a consumer-observable behavior in that case not covered elsewhere, requiring behavioral coverage before removal.

Any revised full-matrix execution requires an operator amendment to the explicit EXACTLY ONCE ruling. Kaya operations, installation, merge and deployment remain unauthorized.

## Corrective verification

All five failed integration files and the failed unit file subsequently passed targeted runs; the original pinned matrix remains FAILED. See `build-verification-2026-10-18.md` for exact chains and timings. No second full matrix has run.

Confirmed fixes: two closed fully-required backend variants preserve ordinary omission and explicit count semantics; the counted variant enforces nonnegativity. Original explicit digest read declarations coexist with arbitrary feature-local evidence triggers. Recovery catches now name process/parse/atomic-writer failure types without increasing the broad-catch ceiling. Remaining fixtures explicitly declare binding and provenance, and the board audit caller supplies the matching board/repository. The obsolete prose-order case and its private helpers are deleted, not repinned; accepted/invalid station-argument checks remain.

The real CLI caught a missing nonnegative constraint before correction; its permanent regression went red then green. A regression injecting the atomic writer's actual `MergeRefusal` class also went red then green and proves pending intent survives without a second create. These injected remote-error cases do not claim a live remote outage.

Canonical files-only amendment preserved approval and original task signatures; feature metadata comparison found only the appended amendment judgement and cleared stale review pin changed. All prior run records, counts, judgements and mirror generation stayed unchanged. Current logical-path pre-pin risk assessment has zero high findings, the same 35 named grade-2 reasons, and no findings from four separate corrective quality-angle readers.
