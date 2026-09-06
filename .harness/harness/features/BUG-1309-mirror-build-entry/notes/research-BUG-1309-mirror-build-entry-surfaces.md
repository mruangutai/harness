# Research — BUG-1309 surfaces, measured at 4e8f5ea1

**BLUF.** Every surface the plan names was resolved with `check-domain.sh --resolve` at
`4e8f5ea115d84899abafb301ea390c6a333e4514`, and the four anchors a builder is most likely to get
wrong are recorded below as CONTENT, never line numbers.

## Lane resolution, verbatim output

| path | `--resolve` |
|---|---|
| `bin/gh-sync.py`, `bin/feature-schema.json`, `bin/check-state.sh`, `bin/post-merge-sweep.sh`, `bin/merge-gate.sh` | `harness-backend-dev harness-dev-ops` |
| `tests/integration/*`, `tests/unit/omp-hooks.test.ts` | `harness-backend-dev harness-dev-ops harness-qa` |
| `references/github-mirror.md`, `SKILL.md`, `.claude/settings.json`, `templates/settings.snippet.json`, `.omp/extensions/harness-hooks.ts` | **NOBODY** |
| `.harness/harness/docs/DECISIONS.md`, `DECISIONS-INDEX.md` | `harness-documentor` |

`check-plan-routes.py` exits 0 with three DEVIATION lines (T-04, T-06, T-07): granted paths declared
`main-session-direct` under the operator's DEC-174 carve-out. Only VIOLATION lines gate.

## The four anchors, by content

1. `save_recorded`'s `transform` REBUILDS `doc["github"]` from five keys plus optional `typed`. Any
   new field not added there is deleted by the next `open`, `start-task` or `status` call. This is
   why T-02 edit 2 exists.
2. `skip()` is the single funnel for every environmental no-go (`gh()` routes non-zero exits into
   it), which is what makes `skip(msg, build_entry=None)` a complete recording point rather than one
   of several.
3. `post-merge-sweep.sh` greps ship's combined stdout+stderr for the literal `gh-sync: SKIP` and
   `gh-sync: FAILED`. T-03 rewords the milestone SKIP message and must keep that prefix.
4. `check-state.sh` INV-26 `continue`s on `station_of(_fp) in ("done", TERMINAL_MARKER)` and again
   on `_derived is None and all(_s == "ready" for _s in _statuses)`. FEAT-55 hit both. INV-26's
   terminal exemption is load-bearing (`ship` writes `done`; the plan-derived station says `review`),
   so INV-37 is a separate loop, not a weakened exemption.

## Counts and free identifiers, measured

- Highest `INV-NN` in `check-state.sh`: **36** → this feature takes **INV-37**.
- Highest `DEC-NNN` in `DECISIONS-INDEX.md`: **219** → this feature takes **DEC-220**.
- Registered PreToolUse Bash gates today, in order: `branch-create-gate.sh`, `bash-write-guard.sh`,
  `gh-close-gate.sh`, `plan-sign-gate.sh` (`.claude/settings.json`) and the same four in
  `harness-hooks.ts`'s `firstBlock([...])`. BUG-1132 is the recorded cost of registering in one and
  not the other.
- `run-unit-tests.sh` discovers by glob (`tests/unit/test-*.py`, `tests/integration/test-*.py`), so
  a new test file needs no registration. `tests/unit/omp-hooks.test.ts` is executed by
  `tests/unit/test-omp-hooks.py`, which shells out to `bun`.
- `feature_schema.py` needs no change: it loads `feature-schema.json` and has no per-field code.

## Verify discrimination, proven on the unbuilt tree

- T-01's probe: `KeyError: 'build_entry'`, exit 1 — the field is genuinely undeclared today.
- T-08's block: exit 1, because `Build entry` appears in neither document yet.

## Open

- The Build-entry outcome is not backfilled for the ~50 existing features. INV-37 is bounded by a
  frozen era-exempt set generated at the implementing commit; BUG-1309 itself is inside it.
