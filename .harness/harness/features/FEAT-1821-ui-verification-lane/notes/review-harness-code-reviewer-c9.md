# Pinned code review — FEAT-1821 — c9

**BLUF: FAIL.** T-14's gate accepts a corrupt, non-ZIP trace whenever its first four bytes are a ZIP local-header signature, so the signed replayability contract fails open at immutable pin `c5fab95615c035e97109f90bd4aa91fc2e4b78a5`. Stage 1 therefore fails; Stage 2 was limited to the defect's fail-open path and the mandatory mechanical grade.

## Scope and prior boundary

Reviewed only signed amendment tasks T-14 through T-18 in `102cd2d7..c5fab95615c035e97109f90bd4aa91fc2e4b78a5`; HEAD and the read object both resolved to the exact pin. Prior c7/c8 conclusions, including the c8 T-01 title repair at `01636575`, remain preserved and were not reopened. The working tree's orchestration-owned `STATE.md`, `feature.json`, and `plan.yaml` were dirty, so specification and implementation claims were bound to committed pin bytes; no dirty source path was reviewed.

## Stage 1 — spec compliance: FAIL

**F-01 — substance, high — T-14, owner Main — `.claude/skills/harness/bin/ui_contract.py:261-265`, consumed by `_trace_file_problem` at `:383-392`.** `_is_zip` checks only `path.read_bytes()[:4] == b"PK\x03\x04"`. Concrete failure: a truncated or fabricated trace containing `PK\x03\x04not-a-zip` is present and non-empty, so the gate accepts it as replayable even though Python's ZIP parser rejects it. This violates T-14's requirement to reject a non-ZIP and permits structurally incomplete/unreadable trace evidence to avoid a trace-contract reason. Executed falsification at the exact pin printed `gate_is_zip= True stdlib_is_zip= False`. The shipped test covers arbitrary non-ZIP bytes but does not carry the ZIP-signature mutant, so it does not discriminate this fail-open.

No separate defect was found in the amended DESIGN ownership, generic/no-hardcoded-id path, explicit SC-04 pixel-baseline opt-in, location-based ignore policy, shared `UiResultRecord.trace`, reporter publication paths, T-17 policy mutants, or committed T-18 accounting/provenance. Those claims do not cure F-01.

## Stage 2 — code quality

The same weak signature check is the substantive fail-open path. Mechanical grading over the canonical merge-base range `23d6745b..c5fab956` yields `grade_2` for two test helpers: pre-existing `tests/unit/test-suite-layout.py::_literal_key_present` and amended `tests/unit/test-ui-reviewer-policy.py::main`. Both are declarative test-orchestration functions rather than shipped production paths; their grade-2 shape is non-blocking beside the high correctness finding. The T-14 amendment-only Python range itself has 18 functions at grades 4–5.

## Focused evidence

- T-14 signed verify: PASS, 27 tests; receipt tokens and ignore probes passed.
- T-15 signed verify: PASS; exact four traced IDs and no IDs in generic tooling.
- T-16 signed verify: PASS, 15/15 reporter probes.
- T-17 signed verify: PASS, all 18 clauses and their mutants plus shape checks.
- T-18 committed pin inspection: `served_bundle_commit=e94bc953…`, failed summary, 23 records (18 failed / 4 evidence / 1 passed), eight trace fields. Its exact rerun could not complete because the shared `feat53-dashboard` already occupied port 8972; the attempted reporter startup overwrote the working copy of `results.json`, which was escalated to the validator/orchestrator for restoration. This environmental rerun failure is not the substantive verdict basis; F-01 is independently executed against pinned code.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "T-14 fails open on corrupt trace artifacts: a PK local-header prefix is treated as a replayable ZIP without validating ZIP structure."
  severity_max: high
  findings:
    - kind: substance
      scope: task
      severity: high
      reader: code-reviewer
      task: T-14
      owner: Main
      summary: "ui_contract.py accepts a non-ZIP trace beginning with PK\\x03\\x04."
      why: "A truncated or fabricated trace passes the gate as replayable; exact-pin probe returned gate_is_zip=True while zipfile.is_zipfile=False."
  must_fix:
    - "T-14: validate trace ZIP structure fail-closed and add the PK-signature/non-ZIP mutant to the gate contract test."
  spec_violations:
    - kind: mismatch
      path: .claude/skills/harness/bin/ui_contract.py
      ref: SC-06
  code_grade: grade_2
  grade_2_reasons:
    - "tests/unit/test-suite-layout.py::_literal_key_present is a pre-existing declarative test helper outside T-14..T-18; its grade-2 complexity does not affect shipped behavior."
    - "tests/unit/test-ui-reviewer-policy.py::main is a linear declarative policy-contract runner whose ABC count comes from applying each independent clause mutant; splitting it would obscure the one-clause/one-mutant audit table."
  reviewed: "102cd2d7..c5fab95615c035e97109f90bd4aa91fc2e4b78a5"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-code-reviewer-c9.md
```
