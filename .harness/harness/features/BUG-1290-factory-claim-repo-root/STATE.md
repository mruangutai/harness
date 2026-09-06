# STATE

## Current

- feature: BUG-1290-factory-claim-repo-root
- run: none in flight — B-3 fix cycle complete, validation panel and goal-check next
- squad: none
- status: in_progress (returning to the operator ship decision)

The operator struck briefing row **B-3** and directed a fix cycle before the ship decision
(`notes/answers-2026-09-06-b3.md`). B-3 is closed. `tests/unit/test-factory-claim.py`'s two
BUG-1290 segment fixtures now carry NON-EMPTY, DIFFERING `factory.issues` maps, so case 5b
discriminates BOTH of `_BlockerCache`'s caches instead of only the plan cache. Test-only: no
production file changed, +14/-9 in one file.

Orchestrator's own before/after mutant control, measured independently of the squads
(`/tmp/bug1290-orch-probe.py`): unmutated all `ok` both trees; `_plans` re-keyed on `feature`
alone → 5b FAIL before AND after (the plan half did not regress); `_issue_maps` re-keyed on
`feature` alone → **all `ok` before** (blind, which is what B-3 reported) and **5b FAIL after**.

Gates this cycle: eng PASS (0 send-backs, a second persona independently re-measured 8/8 items);
qa test-matrix **PASS**, `matrix_ok: true`, `must_fix: []`; simplify an **empty pass** over four
angles, nothing applied, subject file byte-unchanged. Plan station back at `review`, T-01 back at
`done`.

Cycles 8 of a hard 10 — 15 runs of an informational 20. One of those cycles is mine, not the
work's: the first qa run FAILed with `MATRIX-01` because I scoped a feature-level gate to the
incremental uncommitted diff. Re-scoped to `main`..`HEAD` the integration leg never fires and
`MATRIX-01` was explicitly withdrawn.

## Open Questions

- Q1 (RESOLVED by the orchestrator, rung 1 — no operator input needed): eng and qa both escalated
  that T-01's approved `verify:` exits 1 and no fixture work can make it pass. Measured: it exits 1
  on this tree AND exited 1 on `HEAD` before this cycle began. It is a test-first RED gate written
  at `eb9d044e` that asserts the six `5x` cases FAIL while the seam is ABSENT; T-03 landed the seam,
  so the cases are `ok` and its grep finds no FAIL marker. Its own recorded text says so. It was
  satisfiable exactly once, in the window between T-01 and T-03, and the build digest records it
  green there. This cycle did not move it. **No plan amendment is owed.** Correction to the record:
  the ship handoff's Trust line "All five task `verify:` commands pass on the committed tree" is
  FALSE for T-01 and always was; the predecessor verified the test FILE was green, not that gate.
- Q2 (non-blocking, operator harness-config backlog): `test_kinds.integration.detect` keys a
  REQUIRED kind on a directory label (`tests/integration/**`) rather than on the changed surface.
  It gates nothing here, but it is the mechanism that produced the withdrawn `MATRIX-01` and will
  recur on the next fix-only cycle that strengthens unit-resident fixtures.
- Q3 (non-blocking, harness defect): the write-guard refused `harness-backend-dev` a bash `>>`
  append to its OWN in-domain receipt path while permitting an editor write to the same path.
- Q4 (non-blocking, operator only): the REQ-05 wording correction — carried unchanged from the
  previous cycle. The operator gave no ruling on it and directed that approved artifacts stay
  unchanged. Briefing row B-10.
- Q5 (non-blocking, harness defect, carried): `check-domain` matches inflight claims by bare
  agent-type across every linked worktree with no session scoping. Briefing row B-11.
