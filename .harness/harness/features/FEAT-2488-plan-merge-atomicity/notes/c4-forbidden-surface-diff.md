# C4 forbidden-surface diff guard — FEAT-2488

base: 2491336e43310cb3e95ae3110d098726ed4dc454
head: e8d3031a14885588a567c6b8c922368a4642920c (the pin is the next station commit, which changes only this feature's directory)

```
$ git diff --name-only 2491336e43310cb3e95ae3110d098726ed4dc454..HEAD -- ':!.harness/harness/features/'
.claude/skills/harness/bin/feature_json_write.py
.claude/skills/harness/bin/harness_merge.py
.claude/skills/harness/bin/plan-merge.py
.claude/skills/harness/bin/plan_merge/amend.py
.claude/skills/harness/bin/plan_merge/amendments.py
.claude/skills/harness/bin/plan_merge/approval.py
.claude/skills/harness/bin/plan_merge/check.py
.claude/skills/harness/bin/plan_merge/guards.py
tests/integration/canonical-reader-classification.json
tests/integration/test-plan-merge.py
tests/unit/test-harness-merge-journal.py

$ git diff --name-only 2491336e43310cb3e95ae3110d098726ed4dc454..HEAD -- check-plan-routes.py test-check-plan-routes.py check_state/ plan_merge/union.py
(end; empty means untouched)
```
