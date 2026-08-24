# T-01 receipt — behavioral coverage is green; production utility unchanged

## Result

T-01 adds real-subprocess integration coverage for every REQ-01..REQ-05 outcome. The controlled mutant made exactly the complete-check case red; the untouched real utility passed all seven named cases. No production source changed.

## Test-first evidence

Before authoring the test, the utility hash was:

```text
86cfff73c88a2baa1c74d2e516e3608e38954fef1c9e4ef344113b011e425c12  .agents/skills/harness/bin/merge-gitignore.sh
```

Controlled-mutant command (the wrapper delegates to the real utility but turns a successful `--check` into exit 1):

```sh
MERGE_GITIGNORE_BIN=/tmp/merge-gitignore-controlled-mutant.sh python3 .agents/skills/harness/bin/test-merge-gitignore.py
```

stdout:

```text
PASS preserves_existing_content
FAIL check_complete_is_read_only:
PASS check_incomplete_reports_missing_and_is_read_only
PASS absent_target_receives_each_rule_once
PASS partial_target_retains_present_rule_and_adds_missing_once
PASS second_merge_is_byte_identical
PASS explicit_project_root_ignores_caller_cwd
6 passed; 1 failed
```

stderr was empty; test-program exit status was `1`. The mutant was removed after the proof.

Untouched-real command:

```sh
python3 .agents/skills/harness/bin/test-merge-gitignore.py
```

stdout:

```text
PASS preserves_existing_content
PASS check_complete_is_read_only
PASS check_incomplete_reports_missing_and_is_read_only
PASS absent_target_receives_each_rule_once
PASS partial_target_retains_present_rule_and_adds_missing_once
PASS second_merge_is_byte_identical
PASS explicit_project_root_ignores_caller_cwd
7 passed; 0 failed
```

stderr was empty; exit status was `0`. The post-real-run utility hash was byte-identical:

```text
86cfff73c88a2baa1c74d2e516e3608e38954fef1c9e4ef344113b011e425c12  .agents/skills/harness/bin/merge-gitignore.sh
```

Named coverage maps to requirements: preservation (REQ-01); complete and incomplete read-only `--check`, including every missing-rule name (REQ-02); absent and partial targets with each canonical rule once (REQ-03); second-merge byte identity (REQ-04); and absolute explicit-root behavior from an unrelated cwd (REQ-05). Each case invokes the selected `MERGE_GITIGNORE_BIN` through `subprocess`; ordinary execution resolves the real utility relative to this test file.

## Registration and planned verification

`test-merge-gitignore.py` was added only to `INTEGRATION_SCRIPTS` in `.agents/skills/harness/bin/run-unit-tests.sh` and as the explicit `.agents/skills/harness/bin/test-merge-gitignore.py` member of `test_kinds.integration.detect` in `.harness/harness.json`. It was deliberately not added to `UNIT_SCRIPTS`; the existing unit catch-all remains overlapped while the explicit integration detector and runner cross-check establish authoritative integration classification.

The plan's T-01 `verify:` scalar was checked verbatim against, and executed as:

```sh
python3 .agents/skills/harness/bin/test-merge-gitignore.py &&
.agents/skills/harness/bin/run-unit-tests.sh --kind all
```

Exit status: `0` (145.18 seconds). The captured transcript showed no `MISCONFIGURED` or `KIND-DRIFT` line. Relevant literal output from the direct and all-kinds stages:

```text
PASS preserves_existing_content
PASS check_complete_is_read_only
PASS check_incomplete_reports_missing_and_is_read_only
PASS absent_target_receives_each_rule_once
PASS partial_target_retains_present_rule_and_adds_missing_once
PASS second_merge_is_byte_identical
PASS explicit_project_root_ignores_caller_cwd
7 passed; 0 failed
...
PASS test-merge-gitignore.py
```

The all-kinds transcript contained no `MISCONFIGURED` or `KIND-DRIFT` finding; the runner reached and passed the newly registered program. Full command transcript is retained by the execution artifact for this run; the literal lines above are the changed-surface evidence.

## Scope record

- Production changed: no; `.agents/skills/harness/bin/merge-gitignore.sh` is byte-identical before and after.
- Touched paths: `.agents/skills/harness/bin/test-merge-gitignore.py`, `.agents/skills/harness/bin/run-unit-tests.sh`, `.harness/harness.json`, and this receipt.
- Cycles: `0`.
