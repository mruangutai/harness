# STATE

## Current

- feature: BUG-1290-factory-claim-repo-root
- run: none in flight — B-27 fix cycle complete, back at the operator ship decision
- squad: none
- status: awaiting-user

The operator directed the B-27 fix AND the literal case-`5b` failure form, and raised
`max_total_cycles` to 11 (`notes/answers-2026-09-06-b27.md`). **Both directives are closed.**
Test-only, two files, production byte-identical to the previous pin `c488218e`.

1. **B-27 closed.** `5g`'s bare negation is replaced by the mutation's six-clause specific
   observable (`tests/unit/test-factory-claim.py:1340-1349`), so a mutant that merely raises no
   longer passes. It left the suite green at 125/125 before; it reddens `5g` now.
2. **The literal form, at two seams.** `_emit_5b(record)` is case `5b`'s single verdict path; `5g`
   reruns THAT emitter under the mutant through a capturing shim, so the False verdict is keyed by
   `name_5b`. And `tests/unit/test-factory-claim-mutation.py` gained a second arm that patches
   `factory_claim._BlockerCache` module-level and re-executes the whole suite, which PRINTS
   `FAIL  BUG-1290 5b`. Reached-marker guarded; negative control proves it goes red when the
   collapse is neutered while the mutant is still reached.
3. **No leak into `5c`-`5f`:** fresh cache per run, `id()` identical before/after, and only `5b`
   reddens under a whole-suite collapse.

Orchestrator's own five-arm control, on out-of-tree copies (`/tmp/b27-orch-control.py`,
`/tmp/b27-orch-control2.py`): intact 125/125; raising mutant RED on `5g` (B-27, reproduced then
closed); `depends_on=["T-99"]` deleted RED; issue map emptied RED on `5b`; captured verdict keyed by
`name_5b`, False, cache restored; new arm RED when the collapse is neutered but the mutant reached.

Gates, all green, **zero send-backs anywhere — this cycle spent NO rework budget**: eng PASS x2
(runs 13-eng, 14-eng); qa test-matrix **PASS** `matrix_ok: true` (15-validator); simplify an **empty
pass**, two candidates declined on measured grounds (16-eng); validation panel **PASS**
`must_fix: []`, `severity_max: med` carried entirely by two pre-existing grade-2 functions, four
reviewers ran and none skipped (17-validator); goal-check **9/9 SC MET**, every row re-derived
(18-product). `review_sha` pinned at **`72a97b99`**; mirror re-synced at review (milestone #51,
parent #1359, tasks #1360..#1364). Plan station `review`, all five tasks `done`.

Briefing: `notes/ship-review-2026-09-06-19-ship.md` (+ rendered HTML). Handoff:
`notes/handoff-ship.md` (seq-4). HEAD `ecc21dbe`. No PR, no merge, nothing shipped — the operator's
ship/fix/re-scope/stop decision is the next act.

**Budgets.** 9 rework cycles of the operator-raised hard **11**; zero spent this cycle. **30 runs of
an informational 20** — my read: today's six runs each earned their place.

The operator paused mid-cycle after the panel returned and resumed immediately; nothing was in
flight at the pause and no state was left inconsistent.

## Open Questions

- Q1 (**RESOLVED at rung 1, this cycle**): the literal-`5b` ruling the previous cycle carried. The
  operator ruled: deliver the literal form, not the `5g` equivalent. Delivered at two seams, graded
  satisfied independently by the panel and by pm. Closed.
- Q2 (**RESOLVED, closed**): B-27, the fail-open negation. Fixed and verified by the arm that used
  to pass.
- Q3 (RESOLVED, rung 1, carried): T-01's approved `verify:` exits 1 and is a settled test-first RED
  gate, unsatisfiable after T-03 landed the seam. Re-confirmed unchanged: production did not move.
- Q4 (non-blocking, operator only, row B-10): the REQ-05 wording correction, carried unchanged. The
  operator has declined to rule three times and directed that approved artifacts stay unchanged.
- Q5 (**RESOLVED by me, rung 1, row B-38**): the validation lead asked whether to send the ui
  reviewer back for returning `severity_max: n/a`, not a valid enum value. I accepted the trade —
  its verdict was stated, its note complete and lead-verified. Logged, not re-litigated.
- Q6 (non-blocking, harness defects, rows B-11..B-15, B-18..B-22, B-26, B-31, B-38): claim scoping;
  lead digest clobber; hardlink edit desync; **null-yield returns, which recurred a fourth
  consecutive cycle — the eng lead's simplify return exited 1 with its digest already on disk**;
  main-checkout leakage (no recurrence, re-checked); the matrix keying a required kind on a directory
  label; the write-guard's two routes disagreeing; reviewer `files_touched` under-reporting; scratch
  worktrees (none new this cycle — the standing `qa-c2-*` trees predate today, created 2026-09-05);
  the permanently inert `match_bug_class` leg (third consecutive grading, re-raised by qa); and the
  reviewer digest-contract violation above.
- Q7 (pre-existing, NOT introduced by this cycle, row B-24): no `notes/handoff-build.md` — the build
  seam was crossed without one by a predecessor. Confirmed absent again. Writing one now for a phase
  nobody ran would falsify the record, so it stays open and reported.
- Q8 (**measurement I could not take**, non-blocking): `check-state.sh` resolves features through the
  project root, where this feature's directory does not exist on `main`, so run from this worktree it
  reports nothing at all about BUG-1290 — 814 lines, zero mentions. That is an absent measurement,
  not a clean bill.
