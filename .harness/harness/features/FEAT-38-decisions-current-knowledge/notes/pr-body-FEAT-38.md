# FEAT-38 — `DECISIONS.md` states current knowledge

`.harness/harness/docs/DECISIONS.md` recorded what *was* true, in layers: a decision, then dated
amendment sub-sections correcting it, sometimes a third correcting the second. A reader had to
date-sort the file in their head to find out what the project currently believes. This branch makes
every entry state current truth in its own voice.

- **The amendment convention is ended** (DEC-205). An entry states current truth directly; a
  correction rewrites the entry it corrects; a claim the tree has falsified survives as **one clause**
  of that truth, so it cannot be re-proposed as new; the amendment sub-section is deleted.
- **Supersession is deletion.** 15 entries removed — 7 struck with a named successor, 8 superseded,
  DEC-90 the recorded exception. No `SUPERSEDED BY` markers, no append-only mandate.
- **One mechanical check guards the file**: anchor rot — every file-and-line anchor must name a file
  that exists and a line within its length (`check-decision-anchors.py`).
- **The executable-claims mechanism is DELETED, not redesigned**, per the operator's 2026-08-29
  ruling that no document-driven command execution is acceptable. The loss of any detector for
  semantic citation rot is an accepted, recorded cost.
- 7414 → 6305 lines. Size was never a goal.

## Merged with `origin/main`, and what that took

FEAT-44 (the OMP-native context advisory, PRs #982 and #995) shipped while this feature was in
flight and touched three of the same files. `origin/main` is merged (`a382827`, re-merged at
`141eca6`) and the branch is **0 behind**.

Three conflicts, resolved and independently graded:

- **`.harness/harness.json`** `test_kinds.integration` — deliberately **not a union**. FEAT-44
  retired and deleted `test-context-watch-cli.py` and `test-context-watch-hook.py`; a union would
  have resurrected two registrations naming absent files. 29 → **27**, every concrete entry
  confirmed present on disk.
- **`run-unit-tests.sh`** — the same shape; `--check-kinds` agrees with `harness.json`.
- **`DECISIONS-INDEX.md`** — generated, so **regenerated rather than hand-merged**. Proved by the
  committed file being byte-identical to a fresh generation. 188 rows, 188 live headings, zero
  orphans. FEAT-44 changed zero index rulings.

## The three amendments the merge brought in

FEAT-44 appended three new amendment sub-sections on 2026-08-29 — to `DEC-159`, `DEC-198` and
`DEC-201`. `test-gen-decisions-index.py::test_no_amendment_construct_survives_in_the_authority`
caught all three, exactly as designed, and they are now folded (`3767624`).

`DEC-201`'s evidence bounds are preserved item for item: one OMP build measured twice on one machine,
the committed probe path, the version-floor risk, that `probe-omp-session-accessor.py` fails rather
than skips, that the check is **MANUAL and not a CI gate**, and that this is one build's observed
behaviour rather than a property of the OMP API. Its retired nonce scheme is recorded as
correct-but-inapplicable rather than wrong.

## Verification

| Gate | Result |
|---|---|
| full unit suite | **exit 0**, zero `FAIL` lines |
| blocking qa gate at `review_sha` `37676244` | **PASS** — `matrix_ok: true`, `must_fix: []` |
| targeted panel on the merge + fold delta | **PASS** — `severity_max: med`, `must_fix: []` |
| SC-11 read-back of the three folds | **3 of 3 PASS**, by a reader who did not write them |
| goal-check | 17 of 17 live success criteria met |
| SC-13 (operator UAT) | `passed`, 2026-08-30 |

`review_sha` moved from `635cd3ba` to **`37676244`**: the merge changed source under the old pin and
the fold then changed the authority itself, so the old pin no longer described what ships.

## Notes

- This branch carries `79e2639`, a fix to a fail-open substring assertion in
  `test-validate-feature-json.py`. That is **`main`'s work** (PR #997), here by merge, not FEAT-38's.
- It also carries `16f86e3` and `7a23d74` — a FEAT-46 grilling note and the operator's hold entry.
  They touch only `.harness/logs/2026-08-30.md` and a note under FEAT-46; splitting them out would
  need a history rewrite. Stated so it is not silent.

Milestone 31 · parent #935 · sub-issues #936–#958 and #973–#977.
