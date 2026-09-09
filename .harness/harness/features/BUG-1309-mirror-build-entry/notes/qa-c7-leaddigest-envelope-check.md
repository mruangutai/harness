# QA — panel c7 — lead digest envelope check

BLUF: all three `validate-digest.py lead` invocations exit 0 with `digest ok`. No repair needed on
any of the three digests. `state.yaml` for the c7 run parses as valid YAML and its `run_uid`
matches `.run-identity.json` in the same directory.

## Command 1

```
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/validate-digest.py lead /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1309-mirror-build-entry/.harness/harness/features/BUG-1309-mirror-build-entry/runs/2026-09-08-panelc7-validator/digest.md
```

Exit code: `0`

stdout/stderr (complete, verbatim):
```
digest ok
```

## Command 2

```
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/validate-digest.py lead /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1309-mirror-build-entry/.harness/harness/features/BUG-1309-mirror-build-entry/runs/2026-09-07-03-validator/digest.md
```

Exit code: `0`

stdout/stderr (complete, verbatim):
```
digest ok
```

## Command 3

```
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/validate-digest.py lead /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1309-mirror-build-entry/.harness/harness/features/BUG-1309-mirror-build-entry/runs/2026-09-06-panelc1-validator/digest.md
```

Exit code: `0`

stdout/stderr (complete, verbatim):
```
digest ok
```

## state.yaml / .run-identity.json cross-check (panel c7)

Path checked: `runs/2026-09-08-panelc7-validator/`

- `state.yaml` parses as valid YAML: **yes** (plain read; well-formed mapping with `steps:` list and
  a trailing `run_uid` scalar; no syntax errors observed).
- `run_uid` in `state.yaml`: `57bceb23909b4467a45875c4581bc557`
- `run_uid` in `.run-identity.json`: `57bceb23909b4467a45875c4581bc557`
- Match: **yes**, exact string match.

## Notes

- This dispatch ran no test suite and no source/digest edits were made — mechanical envelope check
  only, per assignment scope.
- All three digests are lead-role digests (`validate-digest.py lead`); no `member`-role validation
  was requested or performed.
