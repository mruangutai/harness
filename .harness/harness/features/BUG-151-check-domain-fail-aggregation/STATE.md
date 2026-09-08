# STATE

## Current

- feature: BUG-151-check-domain-fail-aggregation
- run: .harness/harness/features/BUG-151-check-domain-fail-aggregation/runs/2026-09-07-c1-eng/state.yaml
- squad: validator
- status: in_progress

IN VALIDATE, FIX CYCLE c1 APPLIED, RE-PANEL PENDING. Feature station `review` (plan.yaml).
cycles_used 4 of 10 (the +1 is the panel FAIL routed back; both segments in the cycle reported ZERO
send-backs internally); 11 runs of an informational 20.

Panel c0 (`2026-09-07-2-validator`) returned FAIL, severity_max high, matrix_ok true, on ONE finding:
F-1 — the safeguard's predicate was pinned but its SEAM into `main()`'s discovery loop was not.
`run_bug151_selfcheck_cases()` drove `_aggregation_verdict` on synthetic string pairs only; deleting
the `redirect_stdout(block_tee)` wrap around `total = block_fn()` left every committed case green
while BUG-151's exact shape (print a column-0 FAIL, return 0) sailed through. Three readers PASSED
(qa gate-only, security, ui) and each looked at the named file set before saying so.

Fix cycle c1 (`2026-09-07-c1-eng`, harness-backend-dev) extracted the discovery-loop body into
`_run_block_captured(block_fn, label, stream=None)`. `main()`'s loop and the new permanent case now
call THE SAME function, so the seam is crossed rather than restated. The fake block is nested inside
the case body and is not `run_`-prefixed, so discovery still finds exactly 24 blocks and no FAIL line
reaches the real stdout.

VERIFIED BY ME AT THE TIP, not taken from the digest:
- Non-vacuity, the point of the whole fix: I re-ran the mutation myself without editing the source —
  patched the module's `contextlib.redirect_stdout` to a no-op and called the block. Control:
  returns 0, `ok    [bug151-selfcheck] wiring-seam-…`. Mutated: returns 1,
  `FAIL  [bug151-selfcheck] wiring-seam-…`. The new case CAN report red.
- Full suite: exit 0, 405 column-0 `ok` (404 + exactly the one new case), 0 column-0 `FAIL`,
  0 `aggregation safeguard` lines. SC-03's set equality holds by construction: the diff adds one
  print and removes or renames none.
- `git status --porcelain` before the commit carried only the one source file plus feature-dir notes.

MEASURED WARNING, still true and still load-bearing: the local `main` ref in this worktree is STALE
and does NOT contain this branch's base `6d969ed3`. Diffing against `main` or
`merge-base HEAD main` wrongly drags in SIX unrelated files from already-merged BUG-208/BUG-254.
The feature's true code diff is `6d969ed3..review_sha -- tests/integration/test-check-domain.py`.

review_sha is RE-PINNED after the c1 commit (P-02: a pin at a commit that predates the work under
review grades a tree the work is absent from). The seam pin `e4efd774` is superseded and graded a
tree without the wiring case.

`gh-sync.py status <dir> review` ran at the seam: `plan.yaml station -> review`, plus
`no parent recorded … parent station not written`. This feature has never run `gh-sync.py open`
(that runs at mission ship), so there are no cards to move. The mirror is never a gate.

NEXT, in this order:
1. Re-run the `review` panel at cycle 1 against the re-pinned sha. Validate exits at panel PASS with
   `must_fix` resolved.
2. Then pm's goal-check of the five SCs — still outstanding, and NOT satisfied by qa's sc_status.
   It is the ship phase's first act, not this run's.
Ship is not this run's mission and must not be run.

Signed rulings, carried into every later dispatch:
- T-02 step 8(b)'s red proof is deliberately NOT a permanent test; a 38s mutated end-to-end run does
  not earn a place in the suite. The permanent tests are T-01's synthetic cases plus the c1 wiring
  case. No reader may re-open this.
- `test-validate-digest.py` and `test-bash-write-guard.py` are out of scope by an approved BRIEF
  constraint, their identical exposure measured and named there.

Log:
- 2026-09-07: station backlog -> plan. Feature dir instantiated from templates.
- 2026-09-07: plan drafted, goal-checked, amended twice, panel-reviewed, transcribed; returned for
  signature.
- 2026-09-07: operator signed BRIEF.md and plan.yaml `approved`; station plan -> building.
- 2026-09-07: build dispatch killed by a host-side timeout at ~15 min, leaving T-01/T-02 code
  uncommitted with only a T-01 receipt.
- 2026-09-07: verified that work against both tasks' own `verify:` and committed it at `36446eb5`.
- 2026-09-07: eng segment re-dispatched for T-02's step-8 evidence. PASS, no code edit. T-02 -> done.
- 2026-09-07: qa segment (2026-09-07-1-validator) PASS; blocking gate cleared. Committed `fffc62d9`.
- 2026-09-07: SIMPLIFY (2026-09-07-02-eng) PASS, zero applies, code byte-identical by sha256.
- 2026-09-07: station building -> review at `e4efd774`; review_sha pinned; gh-sync status review run.
- 2026-09-07: panel c0 FAIL on F-1 (high). cycles_used 3 -> 4.
- 2026-09-07: fix cycle c1 PASS; seam bound by `_run_block_captured`; mutation re-verified by me;
  committed and review_sha re-pinned. Re-panel dispatched.

## Open Questions

- Residual of the same class as F-1, NOT gating, raised by the eng lead as its Q1 and ruled on by me:
  `main()`'s CASES loop still inlines its own `_AggTee` + `redirect_stdout` rather than routing
  through `_run_block_captured`, so that one seam remains unpinned. It is materially weaker than
  F-1 was — the CASES loop prints and increments `fails` in the same body, so its two sides cannot
  drift the way a discovered block's can — and closing it is a one-line call-site change plus a
  case. Ruled a BRIEFING ROW, not a fix cycle; folds naturally into the propagation ticket.
- Harness defect, non-blocking: teams/plan-panel.yaml declares two readers, but check-state.sh
  INV-32 (.claude/skills/harness/bin/check-state.sh:534) expects three, including `goalcheck`.
  Every plan panel run under the current team file has the same gap.
- Harness defect, non-blocking, CORROBORATED TWICE: the bash write-guard blocks a static `cp` or `>`
  redirect but not an equivalent Python-level file write. Hit placing the 265KB SC-03 baseline, and
  again by `harness-qa`, which created a file on another persona's surface through a Python file op
  the guard never saw — and was then CORRECTLY refused the `rm` of that same path. The guard gates
  Bash removal of a path whose creation it never gated.
- Harness defect, non-blocking, NOW SEEN TWICE IN THIS FEATURE: a member returns a complete, valid
  fenced VERDICT/DIGEST block and the host still marks the job `failed (exit 1)` with "yield called
  with null data" — `harness-backend-dev` in the build phase, `harness-ui-reviewer` in panel c0. Both
  times the lead accepted the return on the artifact, correctly. A well-formed reader whose job reads
  as failed is how a real reader failure gets normalised away.
- Backlog rows for the CEO briefing, unowned: (1) the no-op ternary at `test-check-domain.py:5239`;
  (2) the printed-vs-counted safeguard covers only this one file though 20+ test files share the
  column-0 convention; (3) that convention is stated authoritatively nowhere; (4) the CASES-loop
  seam above. Rows 2, 3 and 4 are plausibly one ticket.
- Mirror state, non-blocking: no GitHub parent issue or milestone exists for this feature —
  `gh-sync.py open` runs at mission ship and has not run. Nothing is owed until ship.
