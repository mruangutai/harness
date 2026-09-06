# Handoff — BUG-1303, validate → ship — written at e2c800f1, seq-1

## Next

Present `notes/ship-review-2026-09-05-validate.md` to the operator and take one decision: ship, or
rule F-02 first. Nothing is gated — panel `must_fix` is empty, `severity_max` is `med`, and
`gates.review` is `advisory_unless_high`. On acceptance the ship sequence is `gh-sync.py ship` run
from the MAIN checkout with `--body-file` pointing at that briefing (it refuses at exit 1 when the
feature dir resolves inside `.claude/worktrees/`), then the PR and the merge, which are user-gated.
F-02 and the DEC-217 wording reconciliation are both main-session-only surfaces — no squad can be
dispatched at either.

## Trust

- 8 of 8 BRIEF success criteria met at the pin, per-item on the three enumerating criteria —
  `notes/research-BUG-1303-goalcheck-validate-c5.md` — verified-at e2c800f1
- Both panel `must_fix` resolved and independently confirmed, MF-2's probe proven to reach the real
  rejection branch rather than an early return — `notes/review-harness-code-reviewer-c5.md` —
  verified-at e2c800f1
- Digest-validator suite exit 0, zero `^FAIL `, `ALL PASSED`; `test-config-shape-matrix.py` 19/19;
  `run-unit-tests.sh --kind integration` exit 0 over 46 files — orchestrator ran all three, exit
  status captured in a variable — verified-at e2c800f1
- `gen-decisions-index.py --stdout | diff -q -` is silent at exit 0, so SC-06's idempotence clause is
  now true; it was FALSE at the superseded pin 59c5de97 — orchestrator run — verified-at e2c800f1
- `check-state.sh` exits 0 from this worktree; its notes name other features, none BUG-1303 —
  orchestrator run — verified-at e2c800f1
- `review_sha` e2c800f1 is HEAD and the tree is clean, so the pin covers every reviewed byte —
  `git status --porcelain` empty — verified-at e2c800f1
- Test-first ordering for T-01 still rests on the main session's report; cdfce3cb bundles T-01..T-03
  in one commit, so no git artifact shows the declared red state — UNVERIFIED

## Dead ends

- Do not dispatch a squad at F-02's two skill files — `check-domain.sh --resolve` returns `NOBODY`
  for both — orchestrator ran the guard per path — verified-at e2c800f1
- Do not re-run the c4 panel's security or ui lenses — each PASSED on a measured census and the fix
  commit adds no surface for either — `runs/2026-09-05-14-validator/digest.md` `not_rerun` —
  verified-at e2c800f1
- Do not edit `.claude/skills/harness/bin/validate-digest.py` — SC-04 asserts the reviewed range
  names no file under that directory — `BRIEF.md` SC-04 — verified-at e2c800f1
- Do not re-open DEC-217's substance — it is a delegated-Advisor ruling; only its documentation gap
  (F-02) and its worked-example wording are live — `STATE.md` open questions — verified-at e2c800f1

## Working set

- .harness/harness/features/BUG-1303-plan-code-review-digest/notes/ship-review-2026-09-05-validate.md
- .harness/harness/features/BUG-1303-plan-code-review-digest/STATE.md
- .harness/harness/features/BUG-1303-plan-code-review-digest/feature.json
- .harness/harness/features/BUG-1303-plan-code-review-digest/notes/research-BUG-1303-goalcheck-validate-c5.md
- .harness/harness/features/BUG-1303-plan-code-review-digest/runs/2026-09-05-14-validator/digest.md

## Done when

Scope: the operator's ship-or-rule decision on the briefing
Authority: finding:.claude/worktrees/harness/BUG-1303-plan-code-review-digest/.harness/harness/features/BUG-1303-plan-code-review-digest/STATE.md#F-02
