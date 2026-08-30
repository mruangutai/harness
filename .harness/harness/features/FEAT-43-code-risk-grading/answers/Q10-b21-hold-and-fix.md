# Q10 — B21: hold and fix. One narrowly scoped cycle 26.

**Decision issued by the operator on 2026-08-29**, answering Q2 of
`notes/ship-review-validate-final-c25.md`. Recorded before any work began.

## The ruling

**Hold and fix B21.** The operator does not accept shipping with the two spec-traced branches
untested, and authorizes **exactly one** cycle beyond the previous 25 ceiling. `max_total_cycles`
becomes **26**; `cycles_used` becomes **26**. This is not a general reopening of the budget.

## Scope — narrow, and enumerated

Only mutation-sensitive **behavioural** tests for the two branches the cycle-25 delta review proved
untested:

1. **`_strip_docstring`** — D-03's literal "excluding the docstring", which underwrites D-02's
   promise that a docstring edit cannot fire the gate by construction.
2. **`_qualname`** — the class-prefix join that prevents same-named methods of different classes
   colliding during pre-image resolution.

The bar is the mutation the delta review used to expose the gap: reducing `_qualname` to
`return name`, and reducing `_strip_docstring` to a no-op, each left the full suite **and** the
self-grade at exit 0. After this cycle, each of those mutations must fail a **named** test.

**Out of scope, explicitly:** any refactor, any other backlog row (B1–B20, B22), any behaviour change
to production code, any change not required to test these two branches. A test that passes by
asserting less is a regression dressed as a fix.

## Method and sequence

Test-first. Then: prove both prior mutations now fail named tests; run the focused suites and the
engine self-grade; commit by explicit pathspec; re-pin `review_sha`; **update the `review_sha` line
in `notes/uat-sc11-c21.md` to the new pin**; run the delta review, QA and state gates and a refreshed
goal-check; return the ready SC-11 UAT handoff and the updated briefing.

## The ceiling

**If any finding remains after this cycle, the outcome is terminal `BLOCKED`.** There is no further
repair loop and no cycle 27. No PR, merge, deploy, ship or issue closure is authorized by this
decision.
