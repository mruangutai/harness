# Plan-panel scope review — BUG-276 — reader: harness-code-reviewer

**Conclusion: the plan is sound. No new orphan REQ/SC, no bad `depends_on`, no verify/SC mismatch,
no files-list omission, and every intent-cited line/anchor I checked against the real source
resolves to the code it claims — with one exception, a low-severity citation drift.**

## What I checked

Cross-referenced every `traces:` id against BRIEF's REQ-01..04 (all four traced, none orphaned) and
every SC-01..06 against a task's `verify:` (SC-01/02/05 → T-02's case27a/b/c; SC-03 → T-01's direct
`compute_union` call; SC-04 → re-run of pre-existing `case_add_only_compatibility`, already recorded
as F-06/legitimate reuse; SC-06 → `inspection`, discharged by T-01 step 3). `depends_on`: T-01→[],
T-02→[T-01] is a real dependency — T-02 drives the real CLI end-to-end and needs T-01's guard in
place for its exit-11 assertions to be true, not just topologically satisfiable.

Verified every file:line anchor named in the shared context against the actual source at this
checkout (not the plan's prose) — `compute_union` at line 114, `_check_proposal_ambiguity` at
305-317 (message differs from the new guard only by "ops"→"entries", confirmed), docstring
exit-code table 14-19 (only 0/6/7/8 present, confirmed), `check-expertise.sh` duplicate-id check at
202-207 (matches "~202-206"), `cmd_apply`'s stdout print of refusal lines at line 538 (exact),
`test-expertise-ops.py` bindings — `compute_union`=24, `MergeRefusal`=25, `check`=42,
`base_sections`=46, `case_u9`=131, `case_u10`=142 with its `compute_union` unpack at line 150 exactly,
`main()`=361 with `case_u22()` call at line 382 exactly — and `test-expertise-merge.py` — `check`=55,
`write_file`=59, `write_entries`=75, `target`=88, `run_apply`=102, `case_new_file`=256,
`case_add_only_compatibility`=614, `_assert_case24_ambiguous`=1190, `_run_all_cases`=1310 with
`case_ops_target_grammar_well_formed(root)` as its final call at line 1335, `_report_results`'s
`PASS` print at line 1342 exactly. All of these are precise, several to the exact line.

Confirmed `compute_union` currently drops the second same-id entry silently (traced the loop:
`if eid not in seen: … else skip`, no exception, no code path returns non-empty `conflicts` for a
proposal-only duplicate) — the guard's proposed placement as `compute_union`'s first statement,
scoped to `prop_sections`/`prop_order` only, fires independent of `base_sections`, so it reaches
`case27c`'s absent-destination path (`cmd_apply`'s `transform` calls `compute_union` unconditionally
whether `base_bytes` is `None` or not) and REQ-02/SC-05 hold as planned.

## Findings

- **reader: scope · low · one intent citation lands mid-fixture, not on the pattern it names.**
  T-02's intent (`plan.yaml`, T-02 STEP text) says "hashlib.sha256 as `case_atomic_failure` does at
  lines 597-606" (`tests/integration/test-expertise-merge.py`). `case_atomic_failure` itself spans
  583-611; its two actual `hashlib.sha256(...)` calls are at lines 589 and 601, not 597-606 — that
  range instead covers the `ops_path = write_ops(...)` JSON-op literal and a blank line. Consequence
  is minor: the pattern is also named literally ("hashlib.sha256"), so `harness-backend-dev` will
  grep the right lines regardless; nothing downstream verifies this citation mechanically. Pointer:
  `plan.yaml` T-02 intent, sentence citing "lines 597-606"; actual sites
  `tests/integration/test-expertise-merge.py:589,601`.

No other candidate findings survived cross-check — everything else I traced (guard placement,
message-token order, `files:` completeness for both tasks, the `_run_all_cases`/`main()`
registration points, the STEP-1-red/STEP-2-guard/STEP-3-docstring ordering, REQ-02/REQ-03/REQ-04
coverage) matched the real source exactly. I did not re-raise F-01..F-06 from the goal-check; I
looked for a reason to disagree with a closure and found none with a concrete consequence.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Plan traces cleanly REQ-to-task-to-SC with one low-severity anchor citation drift; no orphan ids, no bad depends_on, no verify/SC mismatch."
  reviewed: "plan:/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-276-expertise-merge-duplicate-id/.harness/harness/features/BUG-276-expertise-merge-duplicate-id/plan.yaml"
  code_grade: n_a
  severity_max: low
  findings: 1
  must_fix: []
  spec_violations: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-276-expertise-merge-duplicate-id/.harness/harness/features/BUG-276-expertise-merge-duplicate-id/notes/review-harness-code-reviewer-planpanel-c0.md
```
