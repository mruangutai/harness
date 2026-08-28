# Observations - harness-security-reviewer

- 2026-08-27: FEAT-37 review dispatch named 9 changed files but its own suggested `git diff --stat 8fc87f8..4e652f9` returned 141 (a merge of unrelated FEAT-42 history was pulled into the range). Derived the correct base by bisecting to the commit whose diff to 4e652f9 reproduces exactly the 9 named files: 766d7b6 (parent of 8a3653e, the commit that added the backlog note). Reviewed against that base instead of the stated range.
