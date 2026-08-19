# qa gate re-measurement — FEAT-25, cycle 1, review_sha 8d7b273

GATE-ONLY. No source touched. All commands below were run by me, in the current working tree, HEAD
already at `8d7b273636cfec7fe1cc3d740f70c9153d170b84` — no worktree needed since the working tree
already sits on the pinned SHA (verified via `git rev-parse HEAD`).

## What the matrix actually requires (not assumed)

`.harness/harness.json` `test_matrix`, checked against each task's `change_type` in `plan.yaml`:

| Task | change_type | matrix `always` kinds |
|---|---|---|
| T-01 | bugfix | unit |
| T-02 | bugfix | unit |
| T-03 | logic | unit |

**Only `unit` is required by the matrix for this feature.** `integration` is not in the `always` list
for either `bugfix` or `logic` (it is required for `cross_module` and `feature`, neither of which
applies here). I ran `integration` anyway, since the prior cycle's dispute concentrated there and my
own independent number is the discriminating check requested.

## Commands run, actual exit codes

```
.claude/skills/harness/bin/run-unit-tests.sh --kind unit          -> exit 0
.claude/skills/harness/bin/run-unit-tests.sh --kind integration   -> exit 1
```

`--kind unit`: every script listed PASS, including `test-layout-migration.py` and
`test-board-station.py` as the tail entries. No red script.

`--kind integration`: **exactly one red script, named**: `test-gen-decisions-index.py`. Its failure
is a genuine named assertion (`test_committed_index_matches_a_fresh_regeneration`), not a
load/import/collection error — it reports a specific row mismatch: the committed
`DECISIONS-INDEX.md` carries a stale `refs:` list for DEC-196 that a fresh regeneration of the
generator does not reproduce. `test-factory-integration.py`, in the same run, is `PASS`. All other 12
integration scripts PASS (`test-validate-digest.py`, `test-gh-sync.py`, `test-check-state.py`,
`test-check-expertise.py`, `test-bash-write-guard.py`, `test-check-domain.py`,
`test-harness-yaml.py`, `test-upgrade-config.py`, `test-check-plan-routes.py`,
`test-merge-settings.py`, plus the case-level entries under `test-bash-write-guard.py`).

This independently reproduces the orchestrator's own working-tree measurement in
`gate-measurement-2026-08-19.md` — same single red name, same script — from my own run, not by
reading that note as evidence.

## Is the red owned by the graded diff

- `git status --porcelain .harness/harness/docs/DECISIONS.md` shows it **modified in the working
  tree**, i.e. held dirt not committed at `8d7b273`.
- `test-gen-decisions-index.py` does not import or reference `factory_claim.py`,
  `layout_fixtures.py`, or `layout_migration.py` (grepped, zero matches).
- `git status --porcelain` overall: only `.claude/agents/harness-{eng,product,validator}-lead.md`,
  `.harness/harness/docs/DECISIONS.md`, `.harness/harness/docs/SPEC.md` modified, plus three
  untracked FEAT-26/27/25-expertise directories — all named as held dirt in the dispatch, none of
  them one of the six graded files.
- The six graded files (`factory_claim.py`, `layout_fixtures.py`, `layout_migration.py`,
  `test-factory-claim.py`, `test-factory-integration.py`, `test-layout-migration.py`) show **zero**
  working-tree modification — `git status --porcelain` names none of them.

**No FEAT-25 file participates in the one red script.** The failure is entirely the pre-existing,
unrelated `DECISIONS.md`/`DECISIONS-INDEX.md` drift.

## The three FEAT-25 suites — PASS/FAIL and ok-line counts against plan thresholds

Run directly (`python3 <script>.py`), exit codes and counts are mine, not read from any note:

| Suite | Exit | ok-lines | Threshold | Result |
|---|---|---|---|---|
| `test-factory-claim.py` | 0 | 120 (`120/120 checks passed.`) | `>= 120` | PASS |
| `test-factory-integration.py` | 0 | 106 (`106/106 checks passed.`) | `>= 106` | PASS |
| `test-layout-migration.py` | 0 | 41 | `>= 41` | PASS |

All three meet or exactly hit the plan's post-T-02/T-03 threshold, with their own exit 0.

## Judgement

Per the matrix, only `unit` is required for this feature's three tasks (all `bugfix`/`logic`), and
`unit` is exit 0 with zero red scripts. `integration`, while not required by the matrix here, was
run for corroboration: it is exit 1, but the single red script (`test-gen-decisions-index.py`) is a
named, genuine assertion failure — not misconfiguration — and it is demonstrably unowned by this
diff: the drift lives entirely in the held-dirt `DECISIONS.md`/index disagreement, absent from
`8d7b273`'s own tree and absent from every one of the six graded files.

**I am not calling `integration` "satisfied by attribution."** I am reporting: it is not a required
kind for this change_type, and even where I ran it beyond the floor, the failure I measured
independently corroborates — not defers to — the orchestrator's own probe.

## SC evidence

The plan's task-level `verify:` blocks (not qa's matrix obligation, but the acceptance the tasks
were graded against) directly assert the same three suites and thresholds reported above:
- T-01's verify block: `test-factory-claim.py` ok-lines `>= 116`, `test-factory-integration.py`
  ok-lines `>= 106` — both exceeded/met (120, 106).
- T-02's verify block: `test-factory-claim.py` ok-lines `>= 120` — met (120).
- T-03's verify block: `test-layout-migration.py` ok-lines `>= 41`, plus
  `test-check-state.py` pass — both hold (`test-check-state.py` PASS confirmed in the integration
  run above).

## matrix_ok

**true.** Justification: the only matrix-required kind for this feature's change types (`unit`) is
exit 0 with zero red scripts, measured directly. The non-required `integration` kind I ran anyway is
exit 1 for one reason with a named cause, and that cause is independently confirmed — by my own
command output, not by citing the orchestrator's note — to be pre-existing held dirt untouched by
any of the six graded files.
