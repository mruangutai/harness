# Protected-source byte-identity receipt

**PASS:** the protected production script is byte-identical to QA's recorded SHA-256, has no worktree diff, and the B-1 exact-set assertion remains intact.

## Current checks

| Check | Command / inspected location | Observed value | Result |
| --- | --- | --- | --- |
| SHA-256 | `shasum -a 256 .agents/skills/harness/bin/merge-gitignore.sh` | `86cfff73c88a2baa1c74d2e516e3608e38954fef1c9e4ef344113b011e425c12` | Matches QA-recorded value exactly |
| Worktree diff | `git diff --quiet -- .agents/skills/harness/bin/merge-gitignore.sh` | exit `0` | No diff for protected path |
| B-1 assertion | `.agents/skills/harness/bin/test-merge-gitignore.py:71-81` | `require(actual_missing_rules == expected_missing_rules, ...)` remains present | Exact actual/expected set equality intact |
| Mismatch diagnostics | `.agents/skills/harness/bin/test-merge-gitignore.py:77-81` | Diagnostic retains both `expected_missing_rules - actual_missing_rules` and `actual_missing_rules - expected_missing_rules` | Missing and unexpected diagnostics intact |

No source files were edited. Tests, suites, formatters, linters, and builds were intentionally not run: this is a no-apply protected-source receipt.
