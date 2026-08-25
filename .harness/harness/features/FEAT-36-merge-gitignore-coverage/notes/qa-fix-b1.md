# QA gate — B-1 exact diagnostic assertion

```yaml
VERDICT: PASS
DIGEST:
  headline: "B-1 exact stderr bullet-set regression is discriminating and all required configured gates are green."
  suite: pass
  failures: 0
  matrix_ok: true
  must_fix: []
  kinds:
    - { kind: unit, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 23 }
    - { kind: integration, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 23 }
  coverage_gaps: []
  sc_evidence:
    - { id: SC-02, test: ".agents/skills/harness/bin/test-merge-gitignore.py:62-83" }
  open_questions: []
  files_touched: [.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/qa-fix-b1.md]
  expertise_update: []
artifact: .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/qa-fix-b1.md
```

## Scope and matrix

The live B-1 diff changes only `.agents/skills/harness/bin/test-merge-gitignore.py`: it replaces per-rule stderr substring checks with exact equality of all `  - ` diagnostic rules against `set(RULES[1:])`. No production-script diff exists. The feature matrix requires `unit` and `integration`; the `ui` predicate does not fire. The changed test is explicitly present in `INTEGRATION_SCRIPTS` and `test_kinds.integration.detect`, and is absent from `UNIT_SCRIPTS` as required.

## Executions

- `python3 .agents/skills/harness/bin/test-merge-gitignore.py`: exit 0; 7 named cases passed, 0 failed.
- `.agents/skills/harness/bin/run-unit-tests.sh --kind unit`: exit 0; 23 registered scripts passed, 0 failed.
- `.agents/skills/harness/bin/run-unit-tests.sh --kind integration`: exit 0; 23 registered scripts passed, including `test-merge-gitignore.py` with 7/0 named behavioral cases.
- Literal plan verify matched `plan.yaml:56-57` exactly and passed: `python3 .agents/skills/harness/bin/test-merge-gitignore.py && .agents/skills/harness/bin/run-unit-tests.sh --kind all`; direct 7/0, then 46 registered scripts (23 unit + 23 integration) passed.

No execution emitted `MISCONFIGURED`, a runner `KIND-DRIFT:` finding, no-tests condition, or load/import/collection/syntax error. Thus neither configured required kind silently matched zero tests.

## Discriminating red proof and identity

I audited the engineering receipt and independently reproduced its controlled mutation in `/tmp/fix-b1-qa.etQRim` (removed afterward): copied the production utility plus its relative snippet fixture, inserted exactly `  - .claude/worktrees/NOT-THE-RULE` in check-mode diagnostic output, then ran `MERGE_GITIGNORE_BIN=/tmp/fix-b1-qa.etQRim/bin/merge-gitignore.sh python3 .agents/skills/harness/bin/test-merge-gitignore.py`. It exited 1 with only `check_incomplete_reports_missing_and_is_read_only` failing; 6 passed, 1 failed; its exact assertion reported `missing=[] unexpected=['.claude/worktrees/NOT-THE-RULE']`. The real direct run was green, so the red proof is discriminating rather than an exit-code-only claim.

Engineering evidence reports pre/post SHA-256 `86cfff73c88a2baa1c74d2e516e3608e38954fef1c9e4ef344113b011e425c12`; the QA remeasurement returned that same SHA and `git diff --quiet -- .agents/skills/harness/bin/merge-gitignore.sh` succeeded. Protected production source is byte-identical. Test history shows the behavioral suite was introduced in `ac85338`; B-1 is a test-only uncommitted assertion strengthening with no production edit.
