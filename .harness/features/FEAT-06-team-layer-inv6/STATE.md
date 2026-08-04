# STATE

## Current

- feature: FEAT-06-team-layer-inv6
- phase: validate
- run: runs/goalcheck-product/ (complete, FAIL — SC-05 unmet as declared)
- squad: product
- status: awaiting_user

**BUILD AND VALIDATE ARE COMPLETE. The feature is at the user's gate with TWO blocking questions,
batched as one round trip.** The briefing is `notes/ship-review-FEAT-06.md`.

- **Q1 — SC-05 unmet as declared.** Its count conjunct has no assertion:
  `test-harness-yaml-corpus.py:180-181` asserts `n > 0` per root, and the `2` in its output is an
  f-string LABEL at `:174-175`. pm ruled it; I verified the premise at source twice.
  **Recommend FIXING (one `check()` line) over waiving** — waiving amends a signed BRIEF.
  **TRAP: the line belongs in `test-harness-yaml-corpus.py`, NOT `test-team-catalog.py`**, whose
  signed verify requires exactly TEN checks.
- **Q2 — SC-13 is the only `uat` criterion** and `gates.uat` is blocking. The user reads
  `teams/build.yaml` and `SKILL.md:40-53` and rules. No test settles it.

**All gates green: qa `matrix_ok: true`, panel PASS (`severity_max: low`, `must_fix` empty),
`run-unit-tests.sh` 0, `check-docs.sh` 0, `check-state.sh` zero violations.** Every one re-run at
the orchestrator's own tier, not taken on report. **13 of 14 non-uat SCs met.**

**10 of 10 tasks passed first time; `cycles_used` is 5 of 10** — 4 spent in planning, 1 for the
SC-05 fix now routed.

**Four defects were caught mid-execution that would each have shipped green** — detail in the
briefing. The load-bearing one: Python `glob` does not descend into dotted directories, so T-05's
widened gate would have scanned **0** files forever while the tree holds 54. And T-07's ten checks
were proven to discriminate — 10 of 10 FAILING at `635ef14`, 10/10 at HEAD — by re-running them
against a detached worktree, not by trusting a green first run.

**COST IS 1.5-2x OVER AND SAID PLAINLY: $154-199 measured against the $100 allowance.** The range is
the reporter's shared window; no figure is invented. **The dominant line is the orchestrator's own
session at ~$88, 45-57%** — DEC-148's square-of-session-length effect, measured. Nine of ten tasks
also ran at depth-0 and are not separable, so the true total is higher.

**Three steps skipped, each with a disclosed reason, none hidden:** feature-close distillation
(would add ~$40-60 at this session's most expensive point — recommend a separate `/harness-curate`;
logs are on disk); the three-lead parallel briefing report (all digests already held, and eng-lead
did no build or validate work); ship-refresh (genuine no-op, `.harness/codebase/` does not exist).

**Commits `f45fd0f`, `510b7ff`, `9f87c48` on `main` — not pushed, not merged.** All 10 mirror
issues closed under milestone #1. `review_sha` is pinned to `9f87c48`, pinned BEFORE the first
`squad: validator` run entry was written — this feature's own `feature.yaml` is INV-6's first
real subject.

## Open Questions

- **Q1 (BLOCKING, user):** SC-05 — fix with one line, or waive? Orchestrator recommends fixing.
- **Q2 (BLOCKING, user):** SC-13 UAT — read `teams/build.yaml` and `SKILL.md:40-53` and rule.
- Non-blocking, for ship acceptance: the eight-item proposed backlog in the briefing. Anything the
  user strikes there dies silently, so the list is complete on purpose.
