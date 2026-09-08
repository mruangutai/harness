# STATE

## Current

- feature: BUG-151-check-domain-fail-aggregation
- run: .harness/harness/features/BUG-151-check-domain-fail-aggregation/runs/2026-09-07-02-eng/state.yaml
- squad: eng
- status: in_progress

BUILD PHASE COMPLETE THROUGH SIMPLIFY. Both tasks station `done`; the qa blocking gate PASSED; the
SIMPLIFY pass ran and applied nothing. The feature station stays `building` because `review_sha` is
NOT yet pinned and the validate segment has not been entered — that is the next dispatch's first act,
deliberately withheld from this one. Plan approved (operator, 2026-09-07).
cycles_used 3 of 10 (both segments reported ZERO send-backs); 9 runs of an informational 20.

All code lives in ONE file, `tests/integration/test-check-domain.py`, committed at `36446eb5` and
UNCHANGED since. Verified by sha256 after SIMPLIFY: working copy == `36446eb5` == `da26d305aa12…`.

MEASURED, and it will mislead the next agent if unread: the local `main` ref is STALE and does NOT
contain the branch base `6d969ed3` (`git merge-base --is-ancestor 6d969ed3 main` → false). Diffing
this branch against `main` or `merge-base HEAD main` wrongly pulls in SIX unrelated files from
already-merged BUG-208 and BUG-254. The feature's true code diff is `6d969ed3..HEAD` on that one
file, nothing wider. Both segment dispatches carried this pin; the validate dispatch must too.

Verified at HEAD by me, not taken from a digest:
- qa gate: matrix `bugfix` → required kind {integration}, satisfied. Suite re-run by me at
  `fffc62d9`: exit 0, 404 column-0 `ok`, 0 column-0 `FAIL`, 0 `aggregation safeguard` lines (SC-04).
- qa proved the fail-detector CAN report red, independently of the builder: monkeypatching `run_t12`
  to print a column-0 FAIL while returning 0 makes `main()` return 1 with the safeguard's own
  diagnostic. This matters more than the green: the artifact under gate IS a fail-detector, so a
  passing suite proves nothing until the detector is shown able to fire.
- qa graded all five SCs met (SC-01a/b, SC-03, SC-04 automated; SC-02, SC-05 inspection) — recorded
  as qa's finding, NOT as the goal-check, which is pm's and has not run.
- SIMPLIFY: four separate read-only readers (reuse, simplification, efficiency, altitude), zero
  applies. The one apply-shaped candidate — a no-op ternary at `:5239` — was declined on two grounds:
  it sits inside the protected `run_bug151_selfcheck_cases()` and on a branch no green run executes,
  so a post-apply re-run would have exercised none of it. An empty pass here is a real outcome.

NEXT, in this order, and none of it has been done:
1. Pin `review_sha` at the tip that CONTAINS the work (INV-6). Re-pin after any later commit.
2. `gh-sync.py status <feature-dir> review` — station argument LOWERCASE.
3. Only then dispatch the review panel. Name the exact file set; the diff pin above goes in verbatim.
4. pm's goal-check of the five SCs is still outstanding and is NOT satisfied by qa's sc_status above.

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
  Ending here at a clean step boundary, BEFORE the pin, so the panel grades an unmoved tip.

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
- Harness defect, non-blocking: `harness-backend-dev` exited its job at 1 on a null-data `yield`
  while emitting a well-formed VERDICT/DIGEST block in its final turn. The eng lead re-derived the
  member's claims against the file rather than trusting the digest, and so did I. This is yield
  mechanics, NOT a work failure; do not read the exit code as a failed task.
