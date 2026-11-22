# Handoff — FEAT-2340, build → validate — written at acd655c7, seq-1

## Next

Dispatch ONE `validate` run to `harness-validator-lead` (slug `validate-validator`,
`HARNESS-MISSION: validate`) over the pinned `review_sha` — the seam commit that marks T-01 and
T-02 `done`. Inputs: BRIEF.md SC-01..SC-04, plan.yaml T-01/T-02, the T-02 verify receipts under
`notes/verify-T02-*`, `notes/simplify-pass.md`. Readers: qa (test_matrix, SC-03 integration
evidence), code, security, ui (self-scopes out: no UI diff), pm goalcheck (one grade per
perspective: code maintainer, operator). Fixes, if any, are main-session-direct (DEC-174 /
DEC-179): a `must_fix` returns to Main, never to a `fix` run.

## Trust

- T-01 landed in exactly the three guidance files (angle-reuse, angle-simplification, model-the-domain) — `git show df6ae1cc --stat` — verified-at df6ae1cc
- T-02 touches only check-domain.py; `_I`, `_RE_HANDOFF_CYCLE`, `VERB` absent; `re.IGNORECASE` spelled out — `git show ffe320f5 --stat`, `notes/verify-T02-post.receipt` — verified-at ffe320f5
- T-02 baseline verify ran ~11 s, inside the 55 s budget; the 300 s authorization was unused — `notes/verify-T02-baseline.receipt` — verified-at ffe320f5
- SIMPLIFY pass (four angles, read-only) found nothing — `notes/simplify-pass.md` — verified-at acd655c7
- T-01 precedes T-02 in history (df6ae1cc < ffe320f5) — `git log --oneline b3c32171..acd655c7` — verified-at acd655c7
- Unit and integration suites rc 0 at ffe320f5; touched functions grade 4/5/5 — Main's build report (dispatch text) — UNVERIFIED
- Fixture `tests/integration/fixtures/prior-check-domain.fixture` untouched — `git diff --stat e239d881..acd655c7 -- tests/` — UNVERIFIED

## Dead ends

- Cross-file consolidation groups (F, J, Y, O, E, S, G, identical non-path matchers) are backlog rows at ship, not findings — BRIEF.md `## Out of scope`, `notes/inventory-Inv2340.md` — verified-at acd655c7
- A mechanical lint for aliases/duplicate matchers is deferred, not a gap — BRIEF.md `## Out of scope` — verified-at acd655c7
- The control-plane copy of check-domain.py governs hooks for subagents and still carries `_I`/`_RE_HANDOFF_CYCLE` until merge; readers grade the worktree copy at `review_sha` only — `.claude/skills/harness/bin/check-domain.py` in the main checkout — verified-at acd655c7
- No `fix` run exists for this plan: every task is main-session-direct, so there is no owning dev to host — plan.yaml T-01/T-02 `execution_mode` — verified-at acd655c7

## Working set

- .harness/harness/features/FEAT-2340-gate-one-pattern-per-concept/BRIEF.md
- .harness/harness/features/FEAT-2340-gate-one-pattern-per-concept/plan.yaml
- .harness/harness/features/FEAT-2340-gate-one-pattern-per-concept/feature.json
- .harness/harness/features/FEAT-2340-gate-one-pattern-per-concept/notes/simplify-pass.md
- .harness/harness/features/FEAT-2340-gate-one-pattern-per-concept/notes/verify-T02-post.receipt

## Done when

Scope: validate run returned over the pinned review_sha with a consolidated must-fix list
Authority: brief-perspective:.harness/harness/features/FEAT-2340-gate-one-pattern-per-concept/BRIEF.md#operator
Authority: brief-perspective:.harness/harness/features/FEAT-2340-gate-one-pattern-per-concept/BRIEF.md#code maintainer
