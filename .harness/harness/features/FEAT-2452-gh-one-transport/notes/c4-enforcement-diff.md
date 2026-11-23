# C4 enforcement diff guard — FEAT-2452

base (merge-base origin/main): b788e9dac342ee112106a3bc5aa7430d4467cbcb
head: 943d2e7926553fd1e571bedbb2b81630028c6d28 (the pin is the next station commit; it changes only this feature's directory)

```
$ git diff --name-only b788e9dac342ee112106a3bc5aa7430d4467cbcb..HEAD -- branch-create-gate merge-gate check_state/ctx GH_BIN-sites
(end; empty means unchanged)

$ git grep -l GH_BIN HEAD -- .claude/skills/harness/bin | changed?
unchanged .claude/skills/harness/bin/branch-create-gate.py
unchanged .claude/skills/harness/bin/merge-gate.py
```
