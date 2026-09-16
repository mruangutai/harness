# Code review c1 — BUG-1716-build-amendments

**BLUF: FAIL.** Stage 1 passes for the complete pinned range `33f45262a9346b62a0e81d3a21786ab2b761cf4e..f602c7eee7761ce4325accba7a04678794c7ed69`. Stage 2 closes the prior code-grade classes V-02 through V-08, but V-01 survives: the rollback covers only a `MergeRefusal`, so an ordinary ledger I/O failure leaves `plan.yaml` amended without its required judgement.

## Stage 1 — spec compliance: PASS

Every changed path in the complete 39-path pinned diff traces to SC-01..SC-07 and D-01..D-08 through T-01..T-09; no unowned product change or `[harness:human]` commit appears in the range. The c1 refactor's new `amendment_contract.py` is within T-02/T-04 and correctly centralizes the closed amendment-entry shape consumed by both `validate-digest.py` and `plan-merge.py` (`.claude/skills/harness/bin/amendment_contract.py:1-98`, `validate-digest.py:395-425`, `plan-merge.py:2085-2095`). `spec_violations: []`.

Inspection criteria remain satisfied at the pin:
- **SC-05:** Stage 1 is explicitly anchored on BRIEF success criteria and decisions, while Stage 2 remains pinned-diff based (`.claude/skills/harness-code-review/SKILL.md:34-46`).
- **SC-06:** the three BUG-285 recommendations remain represented and applied as eligible amendments (`tests/integration/test-plan-merge.py:3699-3730`).
- **SC-07:** DEC-23/32/157/229/230 remain the current-truth authority in `.harness/harness/docs/DECISIONS.md`, with DEC-226 as the audit precedent and the three task-text-independent checks preserved.

## Stage 2 — code quality: FAIL

### Prior blocking-class disposition

- **V-01 — SURVIVES (high, substance, owner T-04).** `_record_amendments_locked` replaces the plan, calls the feature-ledger writer, and restores the plan only under `except harness_merge.MergeRefusal` (`.claude/skills/harness/bin/plan-merge.py:2239-2259`). `feature_json_write.write_feature_json` delegates to a tempfile/fsync/`os.replace` writer and does not translate arbitrary filesystem errors into `MergeRefusal` (`.claude/skills/harness/bin/feature_json_write.py:131-223`). If the feature.json tempfile write, fsync, or replace raises `OSError` after the plan replace—for example disk exhaustion or an I/O fault—the exception bypasses rollback: `plan.yaml` contains the amendment while `feature.json` has no corresponding judgement. The new test covers lock refusal, which is a `MergeRefusal`, not this failure class (`tests/integration/test-plan-merge.py:3897-3933`). This violates SC-02/D-04's same-invocation/all-or-nothing contract and the global byte-identity-on-mutation-failure constraint.
- **V-02 — CLOSED.** `_select_amendment` is decomposed; all selector functions pass the pinned grade (`feature-record.py:208-238`).
- **V-03 — CLOSED.** `cmd_record_amendments` and its preflight/locked stages each pass the pinned production bar (`plan-merge.py:2239-2289`).
- **V-04 — CLOSED.** INV-40 helpers and split scenarios pass their pinned production/test bars (`check-state.py:2904-2955`; `test-check-state-feat59.py:440-503`).
- **V-05 — CLOSED.** deterministic-hash claims are split into focused passing-grade scenarios (`test-plan-merge.py:3647-3697`).
- **V-06 — CLOSED.** BUG-285 splice, isolation, ledger, validity, and replay claims are split into passing-grade scenarios (`test-plan-merge.py:3699-3801`).
- **V-07 — CLOSED.** the feature-schema runner is data-driven through `CASES`, eliminating the grade-1 accumulator.
- **V-08 — CLOSED.** amendment-shape validation is owned once by `amendment_contract.py`; its shared entry validator and both consumers pass the pinned production bar.

### Pinned code grade

The explicitly assigned command was run exactly as requested:

`python3 .claude/skills/harness/bin/code-grade.py --base origin/main --head f602c7eee7761ce4325accba7a04678794c7ed69`

It exited 0 with `PASSING: 87`; no `SEVERITY:` or `REASON REQUIRED` record was emitted. Therefore `code_grade: pass`.

No test suite, formatter, linter, build, or other validation command was run.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Stage 1 passes and code-grade is clean, but V-01 survives because non-MergeRefusal ledger I/O failures bypass plan rollback."
  severity_max: high
  findings:
    - { kind: substance, scope: task, severity: high, reader: code-reviewer, summary: "T-04 record-amendments leaves plan.yaml amended when the feature-ledger write raises an ordinary I/O exception.", why: "After plan replacement, plan-merge.py:2251-2259 catches only MergeRefusal; an OSError from feature_json_write bypasses restoration and leaves no corresponding judgement." }
  must_fix:
    - "T-04: make cross-file record-amendments restore or otherwise recover consistently for every ledger-write failure class, not only MergeRefusal, and prove an ordinary post-plan-write I/O failure leaves both files byte-identical."
  spec_violations: []
  code_grade: pass
  reviewed: "33f45262a9346b62a0e81d3a21786ab2b761cf4e..f602c7eee7761ce4325accba7a04678794c7ed69"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - .harness/harness/features/BUG-1716-build-amendments/notes/review-harness-code-reviewer-c1.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1716-build-amendments/.harness/harness/features/BUG-1716-build-amendments/notes/review-harness-code-reviewer-c1.md
```
