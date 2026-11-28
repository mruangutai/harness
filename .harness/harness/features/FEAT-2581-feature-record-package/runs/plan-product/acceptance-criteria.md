# plan-product c1 — lead send-back criteria (written before any return)

Draft is sent back (or apply/goalcheck held) if any of:
1. BRIEF.md missing `## Approval` pending, or plan.yaml `approval.status` not pending / panel written at draft.
2. `plan-merge.py check` output not reported verbatim with exit 0.
3. Settled Q1 violated: any part of the feature.json domain (CLI verbs, feature_schema, feature_json_write, the artifact_accessors loader set) left outside feature_record/.
4. Settled Q2: module map differs without a recorded per-function reason.
5. Settled Q3: identity proof not a SEPARATE pin task, or invents a new proof framework instead of reusing FEAT-70's receipt-script structure; the three legs (same pre-existing cases pass both sides; CLI ledger argv/exit/stdout/stderr/feature.json bytes; replay of every tracked feature.json) not all present; differences not held red pending operator.
6. Settled Q4: not all 12 named functions raised to grade >= 4, or no bar on new helpers.
7. feature-json-merge.py, its test and its 3 classification rows not deleted; #2569 pieces (ctx.py `_load_hash_module` direct import, plan-merge.py re-export removal, DEC-259 exception note removal) missing.
8. Any shim/re-export, or feature-record.py entry path change.
9. Any `## Out of scope` item planned.
10. Any task not `execution_mode: main-session-direct`.
11. The two `## Not yet specified` items not settled at source and recorded.
12. SC verifies anchored on line numbers or counts the feature moves; figures pinned without re-measurement in the worktree.
13. `decisions_affected` omits DEC-259 (amend at minimum) or lacks a task owning DECISIONS.md.
14. source_issues does not carry both #2581 and #2569.
