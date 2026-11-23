# T-06 receipt: real omp 19.1.0 task-child getContextUsage observation (FEAT-2397, #2194)

Main ran this directly under DEC-174, satisfying sign-off condition 3 (`notes/answers-2026-11-22-signoff.md`).
It was a real, credentialled run on the operator's host, with no mocks and no stubs. An earlier
informal smoke run of the same probe is recorded in `notes/tripwire-after-t04.md`.

## Identity

| Field | Value |
|---|---|
| Launcher invoked | `/Users/molchairuangutai/.bun/bin/omp` (`command -v omp`) |
| Reported version | `omp/19.1.0` (`omp --version`) |
| Tree observed | worktree HEAD `59c3becfd751ea2f2419ba82c4f832367b36be33` |
| Repaired probe | `tests/manual/probe-omp-session-accessor.py`, blob `81a28131c1e233c415aacdf6162faa9583344236`, last changed in `29f80049` (T-04) |
| Repaired companion | `tests/manual/probe-session-accessors.ts`, blob `8c3e9153faf876d97e3ef4c0c25f6c03a54c1e6d`, last changed in `29f80049` (T-04) |
| Date | 2026-11-22 (the session files carry the host UTC stamp 2026-11-23T05:41Z) |

The review pin is whatever later SHA validate pins. These blob ids identify the repaired probe at
that pin: `git rev-parse <review_sha>:tests/manual/probe-omp-session-accessor.py` must equal
`81a28131…`, and likewise for the companion.

## Command, stdout, stderr, exit

Run from the worktree root:

```
python3 tests/manual/probe-omp-session-accessor.py
```

The probe makes its own fresh output directory (`tempfile.mkdtemp(prefix="feat44-accessor-")`). On
this run that was `<workdir>` = `$TMPDIR/feat44-accessor-mweqpczl`. The probe dispatches one real
`sonic` task child under `--model anthropic/claude-sonnet-5` with
`--no-extensions --no-skills --no-rules --auto-approve`.

stdout:

```
PASS - case1: the omp binary is on PATH
PASS - case1: the committed probe extension exists
PASS - case2: the probe produced at least one observation
PASS - case3: a nested task child session was observed, identified by its session path
PASS - case4: that child's getContextUsage returned finite tokens, contextWindow and percent
PASS - case5: a flat main session was observed
PASS - case6: the measured child and the main are distinct sessions
PASS - 7/7 checks passed
```

stderr: empty (0 bytes). **exit: 0.** Wall time: about 13 s.

## Sanitized raw observations

Rows come from `<workdir>/out.jsonl`. The temp path is replaced with `<workdir>`. The
`allMembers` / `probed` getter dumps (106 sessionManager members) are omitted. Nothing else is
removed, and the rows contain no secrets or transcript text.

Each row's role is decided by the probe's own `is_nested` / `is_flat_main`, applied to the
`getSessionFile()` path. Usage plays no part in that decision.

| session | role (by path) | getSessionFile() | tokens | contextWindow | percent | usageDefined |
|---|---|---|---|---|---|---|
| `8wcr` | **nested child** | `<workdir>/sessions/2026-11-23T05-41-09-505Z_01a206ec-2701-7613-baab-d2e8a313e55e/HissingOwl.jsonl` | 6827 | 500000 | 1.3654 | true |
| `3z54` | **flat main** | `<workdir>/sessions/2026-11-23T05-41-09-505Z_01a206ec-2701-7613-baab-d2e8a313e55e.jsonl` | 13653 | 1000000 | 1.3653 | true |

Raw rows, trimmed of the getter dumps:

```json
{"session": "3z54", "usageDefined": true, "usage": {"tokens": 13653, "contextWindow": 1000000, "percent": 1.3653}, "sessionManagerType": "object", "memberCount": 106}
{"session": "8wcr", "usageDefined": true, "usage": {"tokens": 6827, "contextWindow": 500000, "percent": 1.3654}, "sessionManagerType": "object", "memberCount": 106}
```

## What this establishes

- On omp 19.1.0, a real task child's `ctx.getContextUsage()` returns finite numbers for tokens,
  contextWindow and percent.
- The child (`8wcr`) is identified by its nested session path alone, and it is a different
  session from the flat main (`3z54`).
- This is the host evidence DEC-198/201 name. The source evidence (upstream #10097, fixed by
  #10098 in v18.0.11; floor ≥18.0.11) stays separate.
- It also confirms #2194: the probe now classifies sessions by path.
