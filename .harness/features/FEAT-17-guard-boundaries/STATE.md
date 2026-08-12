# STATE

## Current

- feature: FEAT-17-guard-boundaries
- branch: feat/FEAT-17-guard-boundaries
- status: Building
- review_sha: c6a28bd
- run: .harness/features/FEAT-17-guard-boundaries/runs/2026-08-12-09-panel-validator/digest.md

QA GATE PASSES, REVIEW PANEL FAILS WITH A HIGH. Both runs examined c6a28bd and both confirmed the
pin. The feature does NOT ship as it stands.

qa: `matrix_ok: true`, `must_fix: []`, `severity_max: med`. The blocking gate is satisfied on the
union of kinds, and the forbidden halves were proven rule-driven by MUTATION rather than by reading
— neutralising worktree_owner to None flipped four forbidden cases from 2 to 0 on both routes.

panel: FAIL, `severity_max: high`, three must_fix. `gates.review` is advisory_unless_high, so the
high one GATES. Both reviewers returned executed before/after flips, not readings.

F-A [HIGH] harness_boundary.py — three distinct parse failures each `return None`, and every caller
reads None as not-a-worktree, so the write is ALLOWED with no stderr. I verified this at source:
the `except Exception` on a non-UTF-8 read, the `re.match` non-match (the regex `$` is not MULTILINE,
so any second line fails it), and the basename test. One trailing \xff on a valid pointer flips the
identical target from BLOCKED to ALLOWED. That is #103's own failure direction reinstalled inside
#103's fix, and no test builds a malformed pointer.

F-B [MED] check-state.sh:967-971 — the FOURTH import route, and it is worse than the exit-1
hypothesis. Verified at source: `except Exception: _wt_seg = None` then `if _wt_seg:` skips every
INV-25 branch with no bad and no warn, so a session holding a pre-existing out-of-place worktree
prints "all state invariants hold" and exits 0. SC-08's fixture always has the module and SC-10's
module-absent fixture excludes check-state.sh, so coverage is zero.

F-C [MED, record] D-07 and DEC-193 assert in approved prose that product paths keep exactly today's
Bash-route behaviour. Executed before/after shows three cells changed with a MALFORMED
.harness/factory/fleet.yaml: resolve_fleet's internal sys.exit(2) is reached before the `..` filter
and blocks every Bash-route write outside the harness root. The runtime direction is fail-closed, so
the CODE is advisory — the RECORD is not.

NOTHING WAS FIXED AND NO FIX CYCLE WAS ROUTED. All four surfaces named are DEC-174 carve-out files
plus harness_boundary.py, which the operator makes directly. cycles_used stays 6 of 10 — no rework
was re-dispatched. Runs 10 of 20.

## Open Questions

- Q1 BLOCKING. F-A is a high finding and gates the review. Its fix changes worktree_owner's return
  contract, so it is the operator's to make directly. Panel's recommended order: decide F-C's shape
  first, then F-A, then F-B, and wrap domain_check last.
- Q2 The test matrix required `integration` only because T-01 is typed cross_module. `bugfix.always`
  is [unit] and its `when` names `__bug_class__`, which has no test_kinds entry and can never
  resolve. T-02/T-03/T-04 carry the actual #103 and #261 fixes and are all bugfix — a future guard
  change typed entirely bugfix clears this blocking gate on a run that never loads the code.
- Q3 classify's `shared` outcome is UNREACHABLE, not merely untested, so bash-write-guard.sh:571-577
  is dead code new in this diff. Filing "add a shared-path test" would spend a cycle on a test that
  must fail against correct code.
- Q4 F-C forces a choice that is not the panel's: strike DEC-193 under DEC-188, amend it to state
  the malformed-fleet column, or move the `..` continue back above classify.
- Q5 The worktree-creation scan was never tested against evasion — `sh -c`, `command git`, an alias,
  xargs. It is REQ-03's only mechanism.
- Q6 SC-07 is no longer not_met; the two post-goal-check cases close it. Run 08's goal-check verdict
  is stale on that criterion and pm should re-read it rather than carry it forward.
- Q7 Backlog, widened: `--kind unit` excludes test-check-state.py too, not just the two guard suites
  BRIEF names. The filed item understates its own scope.
