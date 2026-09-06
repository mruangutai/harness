# STATE

## Current

- feature: BUG-1290-factory-claim-repo-root
- run: none in flight — B-3 fix cycle complete, back at the operator ship decision
- squad: none
- status: awaiting-user

The operator struck briefing row **B-3** and directed a fix cycle before the ship decision
(`notes/answers-2026-09-06-b3.md`). **B-3 is closed.** `tests/unit/test-factory-claim.py`'s two
BUG-1290 segment fixtures now carry NON-EMPTY, DIFFERING `factory.issues` maps, and the harness
segment's `T-77` depends on a blocker only its own map resolves — so case 5b discriminates BOTH of
`_BlockerCache`'s caches instead of only the plan cache. Test-only: no production file changed,
+14/-9 in one file.

Orchestrator's own before/after mutant control, measured independently of every squad
(`/tmp/bug1290-orch-probe.py`): unmutated all `ok` on both trees; `_plans` re-keyed on `feature`
alone → 5b FAIL before AND after (the plan half did not regress while the other half was
strengthened); `_issue_maps` re-keyed on `feature` alone → **all `ok` before** (blind, which is
exactly what B-3 reported) and **5b FAIL after**.

Gates: eng PASS (0 send-backs; a second persona independently reproduced 8/8 claims); qa
test-matrix **PASS** (`matrix_ok: true`, `must_fix: []`); simplify an **empty pass** over four
angles, nothing applied, subject file byte-unchanged; validation panel **PASS**, `must_fix: []`,
four reviewers ran and none skipped; goal-check **9 SC MET, 0 unmet**, SC-02 re-graded from
scratch with pm's own mutant. `review_sha` re-pinned at **`7104aa43`** — production code is
byte-identical to the previous pin `76e26386`. Plan station `review`, all five tasks `done`;
mirror at review (milestone #51, parent #1359, tasks #1360..#1364).

Briefing: `notes/ship-review-2026-09-06-07-ship.md` (rendered `.html` beside it). Handoff:
`notes/handoff-ship.md` (seq-2). No PR, no merge, nothing shipped — the operator's
ship/fix/re-scope/stop decision is the next act.

**Budgets, both surfaced in the briefing.** 8 rework cycles of a hard 10. **19 runs of an
informational 20** — the crossing point. My read: the runs still earn their place, but this
cycle's four extra runs are not all honest work — one was my own dispatch error, and two were
simplify send-backs on a 14-line test diff, machinery heavier than the change warranted.

## Open Questions

- Q1 (RESOLVED by the orchestrator, rung 1 — no operator input needed): eng and qa both escalated,
  blocking, that T-01's approved `verify:` exits 1 and no fixture work can make it pass. Measured:
  it exits 1 at this pin AND exited 1 at `53a5d658` before this cycle began. It is a test-first RED
  gate written at `eb9d044e` asserting the six `5x` cases FAIL while the seam is ABSENT; T-03
  landed the seam, so the cases are `ok` and its grep finds no FAIL marker. Its own recorded text
  says so. Satisfiable exactly once, between T-01 and T-03, and the build digest records it green
  there. This cycle did not move it. **No plan amendment is owed.**
  **Correction to the record:** the seq-1 handoff's Trust line "All five task `verify:` commands
  pass on the committed tree" is FALSE for T-01 and always was — the predecessor verified the test
  FILE was green, not that gate.
- Q2 (RESOLVED by the orchestrator, rung 1): qa FAILed the matrix with `MATRIX-01` because **I**
  scoped a feature-level gate to the incremental uncommitted diff. A fix cycle is not a change_type;
  the matrix grades what the feature ships, and the feature ships two changed `tests/integration/**`
  files. Re-scoped, the integration leg never fires and qa withdrew the finding explicitly. Cost one
  rework cycle. Briefing row B-22 proposes stating the diff object in the protocol.
- Q3 (non-blocking, operator backlog, row B-16): SC-02's proof is **proven but not defended** —
  deleting `depends_on=["T-99"]` at `tests/unit/test-factory-claim.py:382` returns 5b to the
  pre-B-3 blind state with 124/124 still green. Reproduced by the orchestrator. pm graded SC-02
  MET-with-residue; the panel did not gate it. Natural companion to B-1 and B-2.
- Q4 (non-blocking, operator only, row B-10): the REQ-05 wording correction, carried unchanged. The
  operator gave no ruling and directed that approved artifacts stay unchanged.
- Q5 (non-blocking, harness defects, rows B-11..B-15 and B-18..B-22): `check-domain` claim scoping;
  lead digest clobber; hardlink edit desync; **null-yield returns, which recurred twice this
  cycle**; main-checkout leakage (no recurrence this cycle, re-checked); the test matrix keying a
  required kind on a directory label; the write-guard refusing a shell append to an agent's own
  in-domain path; reviewer `files_touched` under-reporting.
