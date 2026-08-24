# T-01 rework receipt

The strengthened real-process case proves an explicit project root updates the requested project's initially absent `.gitignore` while preserving a distinct pre-existing caller `.gitignore` byte-for-byte.

## Invocation and result

```text
python3 .agents/skills/harness/bin/test-merge-gitignore.py
PASS preserves_existing_content
PASS check_complete_is_read_only
PASS check_incomplete_reports_missing_and_is_read_only
PASS absent_target_receives_each_rule_once
PASS partial_target_retains_present_rule_and_adds_missing_once
PASS second_merge_is_byte_identical
PASS explicit_project_root_ignores_caller_cwd
7 passed; 0 failed
Exit status: 0
```

## Scope

Only the test case and this receipt were changed in this run. A clean `git diff --quiet -- .agents/skills/harness/bin/merge-gitignore.sh ':(glob)**/*registry*'` check confirms the production utility and registry paths are untouched.
