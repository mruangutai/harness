# BUG-2565 — answers c4 applied (Q-R4-1)

T-01 now passes only when every Run A and Run C invocation is matched in its own right, and the leak is evaluated first. T-02's two batch targets now carry distinct task literals, each asserted literally. Five findings are resolved: two closed directly and three through supersession. All four verbs exited 0. None printed an `APPROVAL-RESET:` receipt, so gh-sync was not run, and approval.status is still `pending`. `check` reports 6 tasks, 36 anchors and 0 failures. BRIEF.md is unchanged, because SC-03 and SC-11 already state the outcome. SC-03 requires that dispatch-guard receives each target through the normalized input. SC-11 requires that no refused payload reached the parent.

## PF -> disposition -> change

| PF | Disposition | Change |
|---|---|---|
| PF-3e23c499bba318c133baf80026c1592a (med) | resolved, resolved_by T-01 | **Intent, Step 1.** Each invocation records its own matched flag: `run_a_matched`, `run_c_first_matched` and `run_c_repeat_matched` (`none` when there was no repeat). A pass requires every flag to be yes. Equal totals alone never pass. **Intent, Result block.** It now has fifteen lines, with the three flags added. **Intent, D-03 gate.** The leak is evaluated first, and an unmatched flag is inconclusive. **Verify.** It adds the three keys and computes `leak` straight after parsing, then prints the LEAK line before every other check. It requires both `run_a_matched` and `run_c_first_matched` to be yes. It requires `run_c_repeat_matched` to be yes when `run_c_invocations` is 2 and `none` otherwise. It then runs the existing totals checks. The verify is still a literal `\|` block. |
| PF-cbf8dece633693ce07ab5a284be1a0cf (high) | resolved, resolved_by T-01 | Superseded by PF-3e23 (operator, Q-R4-1). The schema has only open and resolved, so the finding is recorded as resolved by the task that closes PF-3e23. |
| PF-25a87adffad1fd1f463f52b21ddb5b3e (high) | resolved, resolved_by T-01 | Superseded by PF-3e23, recorded the same way as PF-cbf8dece. |
| PF-50024d3fe46e0d0aeb31788c55e947bf (med) | resolved, resolved_by T-02 | **Intent.** In each batch case, the harness-qa item has task probe-qa and the scout item has task probe-scout. Each target's toStrictEqual literal names its own task, for example {agent: harness-qa, task: probe-qa, name: batch-both-qa}. A normalizer that gives both targets one item's task fails. The expected-result line names both literals. **Verify.** A new last line greps for `"probe-qa"` and `"probe-scout"`. The flat cases keep task probe. |
| PF-120f5374d27296822e9d10ea9d8adab9 (med) | resolved, resolved_by T-02 | Superseded by PF-5002 (operator, Q-R4-1). It is recorded as resolved by the task that closes PF-5002. |

No other disposition changed.

## Verbs (stdout captured in the run transcript)

1. `apply`, with a proposal of T-01 intent and verify plus T-02 intent and verify: REPLACED ×4, APPLIED, exit 0.
2. `set-panel`, with the whole panel mapping and only those five findings changed: `PANEL cycle 3`, APPLIED, exit 0.
3. `record-panel --digest runs/2026-11-27-05-plan-product/panel-c4.md --cycle 4`: `PANEL cycle 4`, APPLIED, exit 0. Its readers come from panel-c4.md, and last_run is 2026-11-27-05-plan-product.
4. `check --root <worktree>`: 6 tasks, 36 anchors resolved, 0 failures, exit 0.

Every verb's check-state footer repeats the same standing lines: BRIEF is unsigned, INV-29 for FEAT-2557, and INV-37 because there is no Build-entry receipt yet. None of these is caused by this pass.

## Open findings after the pass

| PF | Severity |
|---|---|
| PF-dc87fd07daa503d6178f16b7b25b805c | med |
| PF-74363a2501221419e2475264503983a1 | low |
| PF-09dfb53f96962654c91322daa41e5b9e | low |
| PF-6cd5d02cb2ff1de49c5f2a16a5be474f | low |
| PF-d6fbd15ebcb6fe0d377aa9069fdca23c | info |
| PF-24f8f80a14ba59b516aa2d0fd5d07732 | info |
| PF-6b295706d3f269ba3acc966eeb91b461 | info |

No high, critical or unrated finding is open.

## Self-check (not a build or test)

I ran the new T-01 verify parser, taken from plan.yaml, on synthetic receipts:

| Receipt | Exit | Result |
|---|---|---|
| Reviewer's case: first Run C invocation unmatched, totals equal (6/6) | 1 | names `run_c_first_matched` |
| Clean, with two Run C invocations | 0 | passes |
| Clean, with one Run C invocation | 0 | passes |
| `run_c_repeat_matched` none while `run_c_invocations` is 2 | 1 | fails |
| A flag missing | 1 | fails |
| Leak together with an unmatched invocation | 1 | prints the LEAK line first |

## Principles applied
- Attack the Premise: the premise that totals equality proves matching had failed twice. The receipt now carries each invocation's own flag instead of a derived count.
