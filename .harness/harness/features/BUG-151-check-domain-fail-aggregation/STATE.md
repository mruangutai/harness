# STATE

## Current

- feature: BUG-151-check-domain-fail-aggregation
- run: .harness/harness/features/BUG-151-check-domain-fail-aggregation/runs/2026-09-07-3-validator/state.yaml
- squad: validator
- status: in_progress

VALIDATE COMPLETE — PANEL PASS, `must_fix` EMPTY. Feature station stays `review` (plan.yaml); only
ship writes `done`. `review_sha` = `9b7b27d074924af2be46194536d6baca4ad4dd18`, the c1 fix commit.
cycles_used 4 of 10; 12 runs of an informational 20 — the count is high because this feature ran
three product runs and a plan panel before a line of code existed, and every run resolved something.

The validate phase, in one line each:
- Panel c0 (`2026-09-07-2-validator`): FAIL, severity_max high, matrix_ok true, on ONE finding. F-1 —
  the safeguard's predicate was pinned but its SEAM into `main()`'s discovery loop was not. Removing
  the `redirect_stdout(block_tee)` wrap left BUG-151's exact shape (print a column-0 FAIL, return 0)
  green across every committed case. qa, security and ui all PASSED and each looked before saying so.
- Fix cycle c1 (`2026-09-07-c1-eng`, harness-backend-dev): extracted `_run_block_captured(block_fn,
  label, stream=None)`. `main()`'s loop and a new permanent case now call THE SAME function, so the
  test crosses the seam instead of restating it. The fake block is nested and not `run_`-prefixed, so
  discovery still finds exactly 24 blocks and no FAIL line reaches the real stdout. Zero send-backs.
- Panel c1 (`2026-09-07-3-validator`): PASS. severity_max low, matrix_ok true, must_fix empty, zero
  send-backs. F-1 recorded CLOSED ON EVIDENCE, not dismissed: two independent mutations.

VERIFIED BY ME AT THE PIN, not taken from any digest:
- Non-vacuity, the point of the whole fix: I re-ran the mutation without editing source — patched the
  module's `contextlib.redirect_stdout` to a no-op and called the block. Control returns 0 with
  `ok    [bug151-selfcheck] wiring-seam-…`; mutated returns 1 with `FAIL  … wiring-seam-…`.
- Full suite: exit 0, 405 column-0 `ok` (404 + exactly the one new case), 0 column-0 `FAIL`,
  0 `aggregation safeguard` lines. Three independent derivations, no disagreement.
- Working tree clean at every commit; each commit staged by explicit pathspec.

MEASURED WARNING, still load-bearing: the local `main` ref in this worktree is STALE and does NOT
contain this branch's base `6d969ed3`. Diffing against `main` or `merge-base HEAD main` drags in SIX
unrelated files from already-merged BUG-208/BUG-254. The true code diff is
`6d969ed3..review_sha -- tests/integration/test-check-domain.py`, one file, nothing wider.

`gh-sync.py status <dir> review` ran at the seam: `plan.yaml station -> review` plus
`no parent recorded … parent station not written`. `gh-sync.py open` has never run — it runs at
mission ship — so there are no cards to move. The mirror is never a gate.

NEXT, and it is the ship phase's first act, not this one's:
1. pm's GOAL-CHECK of the five SCs by their declared `verify:` methods. Still outstanding, and NOT
   satisfied by qa's sc_status or by the panel's compliance grade — both said so themselves.
2. Then the CEO briefing (the backlog rows below are its table), then the ship gate.
Handoff written: `notes/handoff-validate.md`.

Signed rulings, carried forward:
- T-02 step 8(b)'s red proof is deliberately NOT a permanent test; SC-01(b) asks for a one-off
  recorded with the change. The permanent tests are T-01's synthetic cases plus the c1 wiring case.
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
  committed `9b7b27d0` and review_sha re-pinned there.
- 2026-09-07: panel c1 PASS, must_fix empty. Validate exits here; ship is a separate mission.

## Open Questions

- Backlog rows for the CEO briefing, unowned, and ANYTHING NOT LISTED THERE DIES SILENTLY:
  (1) V-1 (low, security-reviewer c1): a discovered block returning a NEGATIVE total while printing a
  column-0 FAIL satisfies the zeroness predicate and can cancel a genuine +1, so a printed FAIL could
  coexist with exit 0 — precondition absent today (all 24 blocks return non-negative counts), not
  introduced by this diff, one clamp to fix. (2) the two sibling suites carrying the identical
  un-safeguarded shape. (3) `main()`'s CASES loop still inlines its own tee rather than routing
  through `_run_block_captured`. (4) the column-0 print convention is stated authoritatively nowhere
  though 20+ test files depend on it. (5) the no-op ternary at `test-check-domain.py:5239`.
  Rows 1 and 2 are one defect class at two altitudes; 3, 4 and 5 are plausibly one ticket.
- Harness defect, non-blocking, SEEN THREE TIMES IN THIS FEATURE: a member returns a complete, valid
  fenced VERDICT/DIGEST block and the host still marks the job `failed (exit 1)` with "yield called
  with null data" — harness-backend-dev in build, harness-ui-reviewer in panel c0, harness-validator-lead
  itself in panel c1. Each time the return was accepted on its artifact, correctly. A well-formed
  agent whose job reads as failed is how a REAL failure gets normalised away.
- Harness defect, non-blocking, measured while writing `notes/handoff-validate.md`: for a
  worktree-hosted feature the handoff `Done when` resolver rebuilds the feature dir under the MAIN
  checkout root, so `brief-sc:` and `plan-task:` authorities can never resolve; only path-carrying
  `finding:`/`approval:` pointers work. The plan-phase handoff hit the same wall and worked around it
  silently.
- Harness defect, non-blocking: teams/plan-panel.yaml declares two readers, but check-state.sh
  INV-32 expects three, including `goalcheck`. Every plan panel run under the current team file has
  the same gap.
- Harness defect, non-blocking, CORROBORATED TWICE: the bash write-guard blocks a static `cp` or `>`
  redirect but not an equivalent Python-level file write, and then correctly refuses the `rm` of the
  path whose creation it never gated.
- Mirror state, non-blocking: no GitHub parent issue or milestone exists — `gh-sync.py open` runs at
  mission ship and has not run. Nothing is owed until ship.
