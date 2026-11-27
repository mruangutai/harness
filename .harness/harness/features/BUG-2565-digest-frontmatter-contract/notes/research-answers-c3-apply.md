# BUG-2565 — answers c3 applied (Q-R3-1, PF-120f5374, Q-A1)

T-01 is now keyed on what its receipt guarantees, and PF-120f5374 is folded into T-02. Two `plan-merge.py apply` calls replaced T-01 verify+intent and T-02 verify+intent. Neither printed an `APPROVAL-RESET:` receipt, so gh-sync was not run. `plan-merge.py check` reports 6 tasks, 36 anchors and 0 failures (exit 0). approval.status is still `pending`. BRIEF.md is unchanged: SC-03 and SC-11 already state these outcomes.

| Item | Task · field | What now carries it |
|---|---|---|
| 1a refuse exactly first N | T-01 · intent, paragraph "Extension contract, refuse exactly the first N yield calls" | The counter n starts at 0 and is incremented before the decision, so attempt = n and is 1-based. The rule is `refuse = PROBE_REFUSE unset or n <= N`. The worked examples (unset refuses all, 0 refuses none, 3 refuses attempts 1–3 and passes 4) are copied into the note's Method section. |
| 1b one parsed Result block | T-01 · verify (python), and intent paragraph "Write …research-yield-refusal-probe.md" | The verify requires exactly one `RESULT BEGIN` line, followed by exactly one `RESULT END` line. Only the lines between them are parsed, and each must be `key: value` with a known key. Duplicate, missing and unknown keys are refused, and so are stray lines. Lines outside the block are never read. |
| 1c match every refused attempt before classification; a leak anywhere stops | T-01 · intent, "Step 1, match", "Step 2, leak", "Step 3, classify" and "D-03 gate". T-01 · verify keys `refused_attempts_all_invocations`, `refused_attempts_matched_to_transcript` and `run_c_invocations`, with the cross-checks matched == all and all ≥ Run A + 3 | Steps 1 and 2 cover every Run A and Run C invocation, including deviated and inconclusive ones. Classification runs only after them. A leak from any invocation sets parent_receives_refused_payload to yes, which fails the verify. |
| 2 PF-120f5374 | T-02 · intent, "Tests in tests/unit/omp-hooks.test.ts", last sentence. Tests-first list and expected-result line in T-02 · intent. T-02 · verify, last line | There are six named cases: flat-output-only, flat-mode-only and flat-both, plus batch-output-only, batch-mode-only and batch-both, each batch case having -qa and -scout items. Each case runs for Main and for a governed lead. Each asserts no block, no input key, and an unmutated host call. Each guard tool_input must be toStrictEqual to the literal {agent, task, name}. The verify greps that every witness name is present. |
| Q-A1 | — | Accepted as is, with no edit (SC-09 org.html clause). |

Guard input shape: `normalizeTaskDispatches` in `.omp/extensions/harness-hooks.ts` emits {agent, task, name?, model?}. With an explicit name and no model, the exact tool_input is {agent, task, name}.

Self-check (not a build or test run): I ran the new T-01 verify parser, read from plan.yaml, on synthetic receipts. A good receipt exits 0. Each of these exits 1 with its own reason: duplicate key, Result contradicting an Evidence-only line, missing key, unmatched count, two blocks, stray line, leak, and total below Run A + 3.

## Principles applied
- Attack the Premise: two cycles of point fixes to T-01 shared the premise that the receipt is valid if each key's success line appears somewhere in the note and the prose semantics are understood. This pass rejects that premise. The verify now parses one delimited block, and the counter rule is written as code, with worked examples.
