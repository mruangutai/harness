# BUG-2349 — code review c0

PASS — T-01 satisfies the pinned implementation contract; no substantive or form findings.

Reviewed `e239d88156c508c948d49cd31238ea13b3b39865..2a476ca04c3516bdac3e69dfe66cec7eb372e243`. Git confirmed the base equals `merge-base origin/main <pin>` and feature.json carries the assigned pin. All four commits were inspected by log; no `[harness:human]` commits. Only feature.json was dirty, inside feature records; no tracked source modifications.

## Stage 1 — spec compliance

- **SC-03 inspection:** `.claude/skills/harness/bin/plan_merge/union.py:517-521` retains the base head when the base has items or the proposal has none. An empty base with proposal items falls through to the proposal head; proposal fallback and absent-key `None` remain. `_aligned_items` runs first (`:475-477`), making item-range emptiness equivalent to parsed-item emptiness for accepted inputs. Only union.py and tests/integration/test-plan-merge.py change outside feature records.
- **SC-01:** independent fresh CLI fixtures at `tests/integration/test-plan-merge.py:5092-5116` assert successful apply and literal reloaded fields for each key; the decisions case also checks existing tasks. Both are registered in CASES (`:5266-5267`). `notes/receipts/sc01-sc02-red.txt:671-712` records both applies and both reload assertions failing against the pre-fix implementation, not missing imports; the green receipt's final checks pass.
- **SC-02:** `tests/integration/test-plan-merge.py:5119-5129` uses a non-empty flow list of valid decision mappings, asserts exit 5 plus the alignment diagnostic, and checks byte preservation. `_aligned_items` and `_merge_union_key` are unchanged.
- **SC-04, pre-merge only:** `notes/receipts/sc01-sc02-sc04-green-prefix.txt:1-2,687-691` records the literal verify invocation, checkout SHA, scratch apply output, reloaded D-01/choice x and rc=0. `notes/red-first-T-01.md` explicitly identifies this as a working-tree fix atop 71f9aa45, not a clean fixed commit. Main still owns the post-merge rerun with an explicit surviving owner-root override; this is not a pre-merge must-fix.
- No plan decisions or build amendments were declared; notes/simplify-build-c0.md records no deviation. Product docs/spec.md, docs/decisions.md and docs/architecture.md are absent in the assigned checkout (docs listing inspected); no product guidance invented or substituted.

## Stage 2 — code quality

The changed condition implements exactly the promised truth table, leaves refusal ordering intact, and introduces no extra allocation or abstraction in production. The test helper shares fixture/apply/reload/cleanup across three callers; each assertion binds actual CLI behavior or written bytes. Reverting head selection reddens the two positive fixtures (recorded red); removing the flow refusal defeats the control's exit/message assertion. No new assertion is absence-only or fixture-asserts-fixture.

Ran only the explicitly assigned static risk grader, against the exact base and pin: five functions reported PASS, all grade 4. `_union_key_head`: cyclomatic 5, cognitive 6, ABC 9.4; test helper: 2/2/10.7; decisions case: 5/2/13.5; tasks case: 2/1/8.6; refusal case: 2/1/9.0. No grade-2 reasons required. No builds, tests, formatting, linting, smoke runs or mutants executed by this reader; red/green claims above are inspected receipts, not reruns.

## Principles applied

- **Delete First** — favored the existing selector's one-condition replacement over a second merge path; the diff removes the old condition before adding its bounded replacement, without rewriting refusal logic.

## Findings and open questions

Findings: none. Spec violations: none. Open questions: none. Remaining ship obligation: main's SC-04 post-merge verification.
