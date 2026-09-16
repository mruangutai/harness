# Product squad digest — BUG-1286-test-tree-enforcement — run 2026-09-04-17-product

**The twice-amended plan delivers the operator's intent: 11/11 acceptance criteria delivered, both
operator-selected fixes CLOSED, and the goal-check is clean except for one genuine residual it
constructed itself — a substituted directory-only `unit.detect` glob rooted outside `tests/` keeps
the new assertion green while re-creating the counted-but-never-run defect.**

One step, one member, zero send-backs.

| Step | Persona | Verdict | Lead verdict |
|---|---|---|---|
| goalcheck-plan-c5 | harness-pm | PASS | PASS |

Artifact: `notes/research-BUG-1286-test-tree-enforcement-goalcheck-plan-c5.md`

## What I assessed rather than accepted

Send-back criteria were fixed before the return landed
(`runs/2026-09-04-17-product/send-back-criteria.md`), so the bar was not fitted to the answer.

Four checks I ran at my own tier rather than take on trust:

1. **GAP-1's central premise, at source.** `plan.yaml:429-433` takes the final `/`-separated segment
   and never inspects the glob's directory prefix; `:438-439` asserts *exactly one* glob is out of
   scope, which catches **adding** a directory-only glob and not **substituting** the existing
   `tests/unit/**`. The gap is real and correctly derived, not padding.
2. **The corrected strip intermediate.** `plan.yaml:436-438` reads `"test_*.py"` **unchanged** with
   the `str.strip` reasoning attached — the c4 follow-up correction landed, and pm's grep for a
   stale `test_.py` returning zero hits is consistent with the text I read.
3. **`panel:` untouched.** Still `cycle: 4`, `last_run: 2026-09-04-14-validator`, both findings
   present (`plan.yaml:134-136, :165, :173`). The frozen record was not disturbed.
4. **No prior note overwritten.** c1 (10.9KB), c2 (14.4KB) and c4 (12.9KB) are intact at their
   original sizes; only c5 is new.

Spot-checked one fence site directly (P-02): `BRIEF.md:122-127` carries `EXACTLY ONE fenced block`
and names the two-or-more failure with its exit-2 refusal. Matches the cited contract.

## The one judgement pm could not make

**GAP-1 does not reopen Fix 1, and the digest must not be read as saying it does.** The property the
operator demanded was whether the new assertion is *capable of failing under its own mutant, or a
source-text tautology in disguise*. The widen-both-files mutant is measurably inside the red set
(`**/*.spec.*` → `x.spec.x` RED while the template-equality assertion stays GREEN). The assertion is
therefore not a tautology and Fix 1 is CLOSED. GAP-1 concerns a **different mutant class** —
substitution rather than addition — that the fix was never scoped to cover. CLOSED-with-residual is
the correct grade and I adopt it.

**Re-ranked against what the project does next.** GAP-1 is `low` by severity and non-blocking, but
the next step is the fresh adversarial panel, and REQ-09/SC-19 is the newest text and the one the
operator just ordered — the surface a panel grades hardest. Its remedy is also window-sensitive in
exactly the way the two cycle-4 findings were: tightening one clause of T-01's `intent:` is cheap
while the plan is unsigned and expensive afterwards, because the builder would otherwise implement
the weaker partition rule as written. That is an operator call, not mine — it changes an artifact
under signature — so it rides up as a non-blocking `open_question` with the window named.

## Surviving gap

1. **GAP-1 (low, REQ-09/SC-19).** `detect: docs/**|**/*.test.*|**/*_test.*|**/test_*.py` keeps T-01
   case 11 GREEN (pm measured it) while every tracked file under `docs/` is counted a unit test,
   sits outside `tests/`, is not test-shaped, and is run by nothing. Cause: the partition treats a
   wildcard-only final segment as unable to produce a file outside `tests/`, which holds only
   because today's one such glob happens to be rooted inside `tests/`. Cheapest remedy, for the
   orchestrator to route and the operator to accept or decline: make out-of-scope conditional on the
   glob's literal prefix starting with `tests/`, and assert the one out-of-scope glob is that
   prefix. **Reported, not applied.**

Nothing else. Both approvals remain `pending`; no implementation, test, config or decision file was
touched, and `harness.json` is read-only in the plan by explicit instruction (`plan.yaml:462`).
