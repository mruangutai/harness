# STATE

## Current

- feature: FEAT-29-graphql-budget
- run: none in flight — `runs/2026-08-20-16-product/` returned BLOCKED
- squad: none
- status: Review — SC-08 and SC-09 unmet at the current pin; budget exhausted at 11 of 11

**The re-grade at the current pin `1f585fc` found a defect I created.**
`.harness/harness/expertise/harness-orchestrator.md` G-01 told **every orchestrator spawn** to expect
"roughly 500 GraphQL points from INV-26's whole-board read" — no board, no item count, no commit, and
falsified at the pin, where `measurement-after.md` reads `delta: 5`. I wrote that line during this
feature's own distillation, *after* the fix landed. It is the exact rot this feature exists to kill,
recreated in the memory file injected into every spawn. Corrected: the entry now carries both figures
with their conditions and drops the `FACTORY_GH` workaround, whose premise a 5-point read removed.

**Re-pinning worked, and it changed a verdict.** SC-09's rule conjunct is now genuinely met —
`git show 1f585fc:CLAUDE.md` line 55 forbids shell wait loops and names Monitor and
`run_in_background`. At `4f2e5d0` the file held no rule at all. SC-09 remains unmet only on a second
conjunct about main-session *behaviour* that no file can evidence.

**Q5 is resolved and is not an error.** `506` under two conditions is two real measurements:
`measurement-before.md:19` records 506 at 486 items (`e1bcdc1`) against 490–506 measured earlier at
473 items (`6bbd706`). Both stand.

The result, every figure with conditions: `check-state.sh` costs **5 GraphQL points** (board 3, 473
items, `8c2c24d`) against **506** before (board 3, 486 items, `e1bcdc1`). Board 6, four items, both
shapes at `8c2c24d`: **old 102, new 1**, `board_items: 4` on both sides. Orchestrator spend across the
feature: **46 GraphQL points**, this repository, 2026-08-19 to 08-20.

Nine of nine tasks done, both suites green, `matrix_ok: true`, panel PASS, SIMPLIFY zero applies,
close-out complete. **No cycle remains** — both live routes are operator signature, not squad work.

## Open Questions

- Q1 (blocking, operator): SC-09 conjunct (a), main-session `gh pr checks` polling, is **ungradable by
  inspection at any pin** — it was live conduct, never a recorded artifact. Rewrite the clause or
  change its `verify:` method; no retry can settle it.
- Q2 (blocking, operator): the required condition set is defined three ways — signed decision D-03
  (`plan.yaml:167-172`) requires **two** tokens, board and item count, and **no commit**; the recording
  rule requires **three**; SC-08's worked example names **four**. Which governs decides the remedy's
  scope.
- Q3 (blocking, operator): SC-08 clause (b) does not say whether *its condition* is **per-figure** or
  **per-document**. Read per-figure, the signed `BRIEF.md` and `plan.yaml` fail too — reinstating the
  unmeetable-criterion defect the 2026-08-20 amendment was written to cure.
- Q4 (non-blocking, harness defect): repository-tier Expertise under `.harness/harness/expertise/` is
  injected every spawn but belongs to no feature, so nothing re-checks its factual claims when a
  feature falsifies one. This is how G-01 rotted within hours of being written.
- Q5 (resolved): two measurements, not a transcription error. See above.
