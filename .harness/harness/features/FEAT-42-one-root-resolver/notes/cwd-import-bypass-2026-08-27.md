# The cwd supplied the boundary rule — #556's real cause — 2026-08-27

## What #556 said, and what it actually was

The ticket reads: `test-bash-write-guard.py` and `test-check-domain.py` are cwd-sensitive,
exit 1 from inside `bin/` and 0 from the repository root. Reproduced at sha `7179095`, both
files, both directions.

The tests were the symptom. The cause is in the gates.

## The measurement

Python puts the invoking directory at `sys.path[0]`, **ahead of `PYTHONPATH`**:

```
$ cd cwdside && PYTHONPATH=../pathside python3 - <<'PY'
import hb_probe; print(hb_probe.WHO)
PY
cwd
```

Every gate script sets `PYTHONPATH="$_selfdir"` and then imports `harness_boundary`. So a
`harness_boundary.py` sitting in the governed agent's working directory was the resolver the
gate consulted. Measured end to end against `check-domain.sh` at `7179095`:

| cwd | verdict |
| --- | --- |
| clean | `exit=2` — `check-domain: BLOCKED — harness-backend-dev may not write .harness/harness/docs/SPEC.md` |
| holds a stub `harness_boundary.py` returning `/definitely/not/the/harness` | `exit=0` — `no /definitely/not/the/harness/.harness/team-config.yaml — enforcement OFF` |

The domain gate switched off entirely, by a file the agent it governs can write. The same
shadowing reaches the standard library: a `json.py` in the cwd is imported by every
`python3 -c 'import json'` line in these scripts.

## The fix

`python3 -P` on all 19 python launches across the ten gate scripts in `bin/`. Nine of them import `harness_boundary`; `check-expertise.sh` runs python without it and is patched for the stdlib half of the same shadowing. `-P` removes the
invoking directory from `sys.path` at the interpreter, so nothing later in a script can put
it back — the guarantee is not code a future edit can delete.

Cost stated rather than discovered: `-P` needs python 3.11 (October 2022). CI runs whatever
`ubuntu-latest` ships, by owner decision recorded in `.github/workflows/tests.yml`, which is
3.12 or newer. An older interpreter rejects the flag loudly instead of ignoring it, which is
the safe direction for an enforcement gate.

## The second cause, and it was a test

Two sites in `test-check-domain.py` read the cwd directly:

1. Case 14 joined `.harness/team-config.yaml` onto `(HARNESS_PROJECT_DIR or CLAUDE_PROJECT_DIR)
   or "."` — the retired two-name chain with a cwd fall-through — so it reported the
   repository's own record missing when it was not. Now `ROOT`, which comes from `__file__`.
2. Cases (g) and (h) were the only relative `file_path` payloads in the suite. The gate
   resolves a relative target with `os.path.abspath`, against the cwd. Claude Code sends an
   absolute path; these now say what production sends.

## What keeps it shut

Three test pairs, each with its paired half so a guard that refuses everything cannot satisfy it:

- `test-check-domain.py` — clean cwd refuses, hostile cwd returns the same verdict.
- `test-bash-write-guard.py` — the same pair on the Bash route.
- `test-no-distribution.py` case 7 — every `python3` launch in `bin/*.sh` carries `-P`, plus a
  count floor so a broken pattern cannot read as a clean tree. This is the one that catches the
  next gate script added without the flag.

All three verified load-bearing by mutation: `-P` stripped from a copy of the two hooks turns
both hook pairs red while their controls stay green; `-P` stripped from `check-expertise.sh`
turns case 7 red.

## Still open

`check-domain.sh` resolves a relative `file_path` against the cwd rather than the root
(`os.path.abspath` at lines 970 and 1000). Not reachable from Claude Code, which sends
absolute paths, and not fixed here — there is no decision saying which base a relative target
should take, and guessing in an enforcement gate is worse than the current state. Raised for
the review panel.

## Why the `.py` hooks are not patched

`validate-digest.py` and `context-watch-hook.py` are registered in `.claude/settings.json` by
path, and a script launched by path gets its OWN directory at `sys.path[0]`, not the cwd —
measured, not assumed. Only the `python3 -` and `python3 -c` forms take the cwd, and those live
entirely in `bin/*.sh`.
