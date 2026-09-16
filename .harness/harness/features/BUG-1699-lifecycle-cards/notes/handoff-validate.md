# Handoff — BUG-1699-lifecycle-cards, validate → operator ruling — written at ed64ea9c, seq-7

## Next

Resume only from an operator-authored answer path named by Main. Resolve the four validation rulings recorded in `STATE.md`: authorize or reject QA-01 scope expansion, bind QA-02 to T-04 or reject that ownership, classify QA-04 for T-02/T-03 or reject it, and accept the completed goalcheck artifact or require harness-owner repair. If authorized, record a succession/regate judgement, move the complete card set to Building, and run the bounded validator-hosted fix team; otherwise return the declined item as the blocking ship decision.

## Trust

- The validate team reviewed immutable SHA `ed64ea9cc4ef92e3e54adfa0849a0147230b480b` with all five readers in one turn — `runs/2026-09-16-07-validate-validator/digest.md` — verified-at ed64ea9c.
- Every signed T-01 through T-05 focused command passed; the configured unit and integration matrix nevertheless failed on QA-01 and QA-02 — `notes/review-harness-qa-c0.md` — verified-at ed64ea9c.
- Code spec compliance passed, while the mechanical risk gate failed on CR-01 and CR-02; security passed and UI correctly scoped out — the three reader notes — verified-at ed64ea9c.
- The on-disk goalcheck is complete and grades all three signed perspectives, but its terminal structured return failed after the single permitted retry — `notes/research-BUG-1699-lifecycle-cards-goalcheck-validate-c0.md` — verified-at ed64ea9c.
- QA-02's failing behavior is in T-04-owned `board_lifecycle.py` commit `c67347cb`; QA-01 traces to inherited cycle-ledger commits `ed44a65f` and `af1c1d88`, outside T-01 through T-05.

## Dead ends

- Do not silently assign QA-01 to a lifecycle task or repair it without operator scope authority.
- Do not discard QA-02 merely because the reader called it unowned; the operator must rule on the demonstrated T-04 ownership.
- Do not rewrite QA-04's unsupported reader kind in the historical artifact; record the operator's classification prospectively.
- Do not rerun the initial validate team or goalcheck. The next allowed validation work is the bounded fix team's re-verification wave.
- Do not merge, open a pull request, deploy, or mark the feature Done.

## Working set

- .harness/harness/features/BUG-1699-lifecycle-cards/STATE.md
- .harness/harness/features/BUG-1699-lifecycle-cards/feature.json
- .harness/harness/features/BUG-1699-lifecycle-cards/runs/2026-09-16-07-validate-validator/digest.md
- .harness/harness/features/BUG-1699-lifecycle-cards/notes/review-harness-qa-c0.md
- .harness/harness/features/BUG-1699-lifecycle-cards/notes/review-harness-code-reviewer-c0.md

## Done when

Scope: obtain the operator's four validation rulings, then either complete the authorized bounded fix/re-verification loop or report the declined item as the concrete ship blocker
Authority: brief-perspective:.harness/harness/features/BUG-1699-lifecycle-cards/BRIEF.md#operator
Authority: brief-perspective:.harness/harness/features/BUG-1699-lifecycle-cards/BRIEF.md#orchestrator
Authority: brief-perspective:.harness/harness/features/BUG-1699-lifecycle-cards/BRIEF.md#code-maintainer
Authority: plan-task:T-01.verify
