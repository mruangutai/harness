# B-1 T-01 receipt — exact missing-rule diagnostics

**Conclusion:** The missing-diagnostic test now compares the emitted `  - ` bullet set exactly to the canonical missing-rule set. The real production utility passes unchanged.

## Scoped change

- Edited only `.agents/skills/harness/bin/test-merge-gitignore.py` in implementation scope.
- The strengthened assertion extracts `line[len("  - "):]` from every stderr line beginning `  - `, compares that set to `set(RULES[1:])`, and reports sorted `missing` and `unexpected` set differences.
- No production defect was established; `.agents/skills/harness/bin/merge-gitignore.sh` was not edited.

## Discriminating RED evidence

A disposable controlled mutant was copied from the production script to `/tmp/fix-b1-mutant/bin/merge-gitignore.sh`, supplied its normal relative snippet fixture, and was diff-confirmed to add exactly this diagnostic output before its check-mode exit:

```text
  - .claude/worktrees/NOT-THE-RULE
```

Command (exit **1**):

```sh
MERGE_GITIGNORE_BIN=/tmp/fix-b1-mutant/bin/merge-gitignore.sh python3 .agents/skills/harness/bin/test-merge-gitignore.py
```

Relevant result:

```text
FAIL check_incomplete_reports_missing_and_is_read_only: missing-rule bullets differ: missing=[] unexpected=['.claude/worktrees/NOT-THE-RULE']
6 passed; 1 failed
```

The mutation was therefore the sole failing case; all six unrelated cases passed. An earlier mutant placement without the script's required relative snippet fixture failed unrelated cases and was discarded rather than counted as red evidence.

## GREEN evidence

The operator-authorized narrowed verification command (the first direct command of T-01's plan verify) ran against the real production utility:

```sh
python3 .agents/skills/harness/bin/test-merge-gitignore.py
```

Exit **0**:

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

`plan.yaml` specifies the broader `python3 .agents/skills/harness/bin/test-merge-gitignore.py && .agents/skills/harness/bin/run-unit-tests.sh --kind all`; per operator constraint, the second command was not run.

## Production byte identity

- Before SHA-256: `86cfff73c88a2baa1c74d2e516e3608e38954fef1c9e4ef344113b011e425c12`
- After SHA-256: `86cfff73c88a2baa1c74d2e516e3608e38954fef1c9e4ef344113b011e425c12`
- Disposition: byte-identical; production script was read/executed/hashed only.

The disposable mutant fixture was removed after proof. No formatter, linter, runner, registry, or project-wide suite was run.
