# Receipt — harness-dev-ops — FEAT-104-strict-digest-schema — 2026-09-10-16-simplify-eng-digestcheck2

## Task
Re-validate the corrected lead digest (appended block, validator slices from last line-start
`VERDICT:` anchor) and take the final DEC-174 carve-out tree witness. No files were edited.

## 1. Digest validation

Command:
```
cd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-104-strict-digest-schema
env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/validate-digest.py harness-eng-lead .harness/harness/features/FEAT-104-strict-digest-schema/runs/2026-09-10-16-simplify-eng/digest.md
rc=$?
echo "EXIT=$rc"
```

Verbatim stdout/stderr:
```
digest ok
EXIT=0
```

Exit status captured immediately after the command (not piped): **EXIT=0**.

## 2. Final DEC-174 carve-out witness

Command:
```
git -C /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-104-strict-digest-schema status --porcelain -- .claude/skills/harness/bin/check-domain.sh .claude/skills/harness/bin/run-state-schema.json tests/integration/test-check-domain.py
```

Verbatim stdout:
```
(empty)
```

The output was **EMPTY** — all three DEC-174 read-only files
(`check-domain.sh`, `run-state-schema.json`, `test-check-domain.py`) are byte-identical to HEAD.

Command:
```
git -C /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-104-strict-digest-schema rev-parse HEAD
```

Verbatim stdout:
```
984bd26b4dc339ea984d2532221477d465a2b05c
```

HEAD SHA matches the lead's expected `984bd26b`. ✓

## Conclusion

Validator exit code 0 AND carve-out-scoped git status empty → both acceptance conditions met.
