# STATE

## Current

- feature: BUG-151-check-domain-fail-aggregation
- run: .harness/harness/features/BUG-151-check-domain-fail-aggregation/runs/2026-09-07-02-eng/state.yaml
- squad: validator
- status: in_progress

VALIDATE ENTERED. Feature station `building` -> `review` (plan.yaml, via `plan-merge.py
set-feature-station`), `review_sha` PINNED at `e4efd774` — the seam commit itself, deliberately, not
the code tip `39ef365e`. INV-33 is a BYTE comparison of plan.yaml at the pin against plan.yaml on
disk, so pinning the code tip and then writing the station would have made the pin read STALE
immediately. The code under review is byte-identical between the two: `git diff 39ef365e..e4efd774`
touches only plan.yaml's station line. `gh-sync.py status <dir> review` ran and reported
`plan.yaml station -> review` plus `no parent recorded ... parent station not written` — this
feature has never run `gh-sync.py open` (that runs at mission ship), so there are no cards to move.
The mirror is never a gate; nothing is owed here before ship.

Build phase is complete through SIMPLIFY: both tasks station `done`, the qa blocking gate PASSED,
the SIMPLIFY pass applied nothing. Plan and BRIEF both approved (operator, 2026-09-07).
cycles_used 3 of 10; 9 runs of an informational 20.

All code lives in ONE file, `tests/integration/test-check-domain.py`, committed at `36446eb5` and
UNCHANGED since (sha256-verified after SIMPLIFY).

MEASURED, and it will mislead the next agent if unread: the local `main` ref in this worktree is
STALE and does NOT contain the branch base `6d969ed3`. Diffing against `main` or
`merge-base HEAD main` wrongly pulls in SIX unrelated files from already-merged BUG-208/BUG-254.
The feature's true code diff is `6d969ed3..review_sha` on that one file, nothing wider. Every
dispatch so far has carried this pin verbatim; the panel dispatch does too.

Verified at HEAD by me, not taken from a digest:
- qa gate: matrix `bugfix` -> required kind {integration}, satisfied. Suite re-run by me at
  `fffc62d9`: exit 0, 404 column-0 `ok`, 0 column-0 `FAIL`, 0 `aggregation safeguard` lines (SC-04).
- qa proved the fail-detector CAN report red, independently of the builder: monkeypatching `run_t12`
  to print a column-0 FAIL while returning 0 makes `main()` return 1 with the safeguard's own
  diagnostic. This matters more than the green: the artifact under gate IS a fail-detector.
- qa graded all five SCs met — recorded as qa's finding, NOT as the goal-check, which is pm's and
  has NOT run.
- SIMPLIFY: four read-only readers, zero applies. The one apply-shaped candidate (a no-op ternary at
  `:5239`) was declined on two grounds and is a briefing row instead.

NEXT, in this order:
1. Validator panel (`review` team, four readers, pinned at `e4efd774`) — DISPATCHED at this seam.
   Stop after it returns; ship is NOT this run's mission.
2. On panel PASS with `must_fix` resolved, validate exits. pm's goal-check of the five SCs is still
   outstanding and is NOT satisfied by qa's sc_status above.

Carry into the panel dispatch: T-02 step 8(b)'s red proof is deliberately NOT a permanent test — a
38s mutated end-to-end run does not earn a place in the suite. The permanent test is T-01's synthetic
`run_bug151_selfcheck_cases`. This ruling is signed; do not let a reviewer re-open it.

Log:
- 2026-09-07: station backlog -> plan. Feature dir instantiated from templates.
- 2026-09-07: plan drafted, goal-checked against issue #151, amended twice, panel-reviewed,
  panel transcribed. Returned to the main session for signature.
- 2026-09-07: operator signed BRIEF.md and plan.yaml `approved`; station plan -> building.
- 2026-09-07: build dispatch killed by a host-side timeout at ~15 min, leaving T-01's and T-02's
  code uncommitted on disk with only a T-01 receipt.
- 2026-09-07: verified that work against both tasks' own `verify:` commands and committed it at
  `36446eb5`. T-01 -> done.
- 2026-09-07: eng segment re-dispatched as assess-and-complete for T-02's missing step-8 evidence.
  PASS, no code edit needed. T-02 -> done.
- 2026-09-07: qa segment (2026-09-07-1-validator) PASS. Blocking gate cleared; suite re-verified by
  me at HEAD before the digest was accepted. Committed at `fffc62d9`.
- 2026-09-07: SIMPLIFY (2026-09-07-02-eng) PASS, zero applies, code byte-identical by sha256.
- 2026-09-07: station building -> review at `e4efd774`; review_sha pinned there; gh-sync status
  review run; validator panel dispatched.

## Open Questions

- Harness defect, non-blocking: teams/plan-panel.yaml declares two readers, but check-state.sh
  INV-32 (.claude/skills/harness/bin/check-state.sh:534) expects three, including `goalcheck`.
  The goalcheck reader row was transcribed by hand here because the team produces none. Every
  plan panel run under the current team file has the same gap.
- Harness defect, non-blocking, NOW CORROBORATED TWICE INDEPENDENTLY: the bash write-guard blocks a
  static `cp` or `>` redirect but not an equivalent Python-level file write. First hit placing the
  265KB SC-03 baseline; hit again by `harness-qa`, which created a file on another persona's surface
  (`tests/integration/_bug151_baseline_qa.py`) through a Python file op unseen by the guard — and was
  then CORRECTLY refused the `rm` of that same path, forcing `os.remove`. The guard gates Bash
  removal of a path whose creation it never gated. Two agents, two features' worth of surface, same
  hole: this is a real asymmetry, not a one-off. Routes to the harness owner, not to this feature.
- Coverage gap, triaged to a LATER ticket, deliberately not fixed here: the safeguard's WIRING carries
  no permanent regression test. `run_bug151_selfcheck_cases()` pins the `_aggregation_verdict`
  predicate on synthetic pairs; nothing permanent pins that `main()`'s discovery loop still routes
  captured output THROUGH it, so unhooking `_AggTee` would leave every committed case green. SC-01(a)
  is met on its literal wording, so this does not gate — but it is the first briefing row.
- Backlog rows from SIMPLIFY, unowned and needing a home in the CEO briefing: (1) the no-op ternary
  at `test-check-domain.py:5239`; (2) the printed-vs-counted safeguard covers only this one file
  though 20+ test files share the column-0 convention; (3) that convention is stated authoritatively
  nowhere. Rows 2 and 3 are wiring-adjacent to the coverage gap above and are plausibly one ticket.
- Mirror state, non-blocking: no GitHub parent issue or milestone exists for this feature —
  `gh-sync.py open` runs at mission ship and has not run, so `status review` wrote no card. Nothing
  is owed until ship.
- Harness defect, non-blocking: `harness-backend-dev` exited its job at 1 on a null-data `yield`
  while emitting a well-formed VERDICT/DIGEST block in its final turn. The eng lead re-derived the
  member's claims against the file rather than trusting the digest, and so did I. This is yield
  mechanics, NOT a work failure; do not read the exit code as a failed task.
