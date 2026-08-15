# Receipt — T-07 — delete deploy.sh

**BLUF: PASS.** `.claude/skills/harness/bin/deploy.sh` deleted with a plain `rm` (unstaged). Verify
command run exactly as specified — exit status 0, PASS count 85, FAIL count 0.

## Cross-check against plan.yaml T-07

Read `.harness/features/FEAT-12-end-copy-distribution/plan.yaml` lines 505-533 before acting.
`intent:` and `verify:` in the dispatch matched the plan verbatim — no mismatch.

Pre-checks (matching claims in `intent:`):
- `wc -l .claude/skills/harness/bin/deploy.sh` → 287 (matches).
- `find . -iname '*deploy*' -not -path './.git/*'` → exactly
  `./.claude/commands/harness-deploy.md` and `./.claude/skills/harness/bin/deploy.sh` (matches:
  no test-deploy.sh / test-deploy.py anywhere).

## Action

`rm .claude/skills/harness/bin/deploy.sh` — plain `rm`, not `git rm`. No staging, no commit.

## Verify — invocation form: exact command from the task, executed verbatim, output redirected
(not piped) as instructed

```
test ! -e .claude/skills/harness/bin/deploy.sh && .claude/skills/harness/bin/run-unit-tests.sh > /tmp/feat12-t07.log 2>&1; s=$?; grep -c '^PASS ' /tmp/feat12-t07.log; grep -c '^FAIL ' /tmp/feat12-t07.log; exit $s
```

Observed:
- exit status: **0**
- PASS count: **85**
- FAIL count: **0**

FAIL count is zero, so no `FAIL <script>` lines to report.

## git status after the change (unstaged deletion, as required)

```
 D .claude/skills/harness/bin/deploy.sh
 M .harness/features/FEAT-12-end-copy-distribution/feature.yaml
```

`deploy.sh` shows as an unstaged deletion (` D`, not staged `D `). The modified `feature.yaml`
predates this task's work — it was not touched by this run; not part of the declared file for
T-07.

## Scope

Only `.claude/skills/harness/bin/deploy.sh` was touched, per the declared-files list. No other
file was edited, staged, committed, or pushed. No carve-out file
(`check-domain.sh`/`bash-write-guard.sh`/`validate-digest.py`/`check-state.sh`) was touched.
