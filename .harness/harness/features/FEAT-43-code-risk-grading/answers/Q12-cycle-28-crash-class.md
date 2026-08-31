# Q12 — Cycle 28 authorized for the optional-AST-field crash class

**Decisions issued by the operator on 2026-08-29**, answering Q1 and Q3 of
`notes/ship-review-c27.md`. `max_total_cycles` and `cycles_used` both become **28**.

## 1. Cycle 27's scope expansion is RATIFIED

The engineering lead read "the CI blocker" as covering all three `df63193`/`REVIEW_SHA` history
dependencies in `test-validate-digest.py`, since all three reddened the same CI run. It reported the
call rather than hiding it. Ratified.

## 2. Cycle 28 is authorized for the crash class — all three sites

`code_grade._Counter` visits three ASDL-optional AST fields without a `None` guard, so the engine
raises `AttributeError` instead of grading:

| site | field | trigger |
|---|---|---|
| `visit_With` | `item.optional_vars` | `with lock:` — no `as` |
| `visit_Try` | `handler.type` | bare `except:` |
| `visit_AnnAssign` | `node.value` | `x: int` — annotation only |

All three were independently reproduced. `visit_Assert` guards `node.msg is not None` correctly in
the same class, so the pattern was present and omitted three times. 16 of the harness's 99
`bin/*.py` crash, including production `harness_merge.py` and `harness_boundary.py`. Introduced by
`1ac1bd0`, this feature's first commit.

**Required tests: mutation-sensitive and behavioural.** Ordinary bare `with`, bare `except:` and an
annotation-only assignment must each grade without crashing **and preserve their intended metrics**.
Removing any one guard must fail a named test.

**Use QA's corrected metric expectations (`notes/qa-delta-c27.md`). Do NOT assert that bare `with`
and `with … as …` are metric-identical** — they are not; `abc_a` differs by 1, because the `as`
target is an assignment and the bare form has none. An earlier draft spec asserted identity and
would have written a failing test.

## 3. Scope discipline — no bundling

The med fail-open (B26) and the low containment item (B27) are **not** to be folded in merely
because they sit in the same two files. Touching the same file is not a shared root cause. They stay
as backlog rows unless the squad can demonstrate they are the same defect as the crash class — and
if it can, it must say so with evidence rather than assume it.

## Sequence

Focused QA, self-grading and range grading, delta review, state gate, commit by explicit pathspec,
re-pin `review_sha`, refresh the goal-check and briefing, return ship-ready. The operator pushes PR
#978 and awaits CI. **No merge, ship, deploy or close.**
