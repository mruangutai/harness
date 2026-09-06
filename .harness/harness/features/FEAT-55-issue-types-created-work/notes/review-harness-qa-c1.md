# QA test-matrix gate — FEAT-55-issue-types-created-work — pinned `cd6a3c0d`

## Verdict: PASS — `matrix_ok: true`

Independently re-ran the gate at `cd6a3c0dee795ca9261d0ecf2e67df09d2e47b86`. **Full agreement**
with the dispatching lead's ten-file + unit-driver measurement — no divergence. This supersedes
the earlier `qa-2026-09-05-01-validator.md` FAIL note, which was measured at an *older* commit
(`ef591a53`) before T-12's anchor-path fix landed; that regression is gone here.

## Floor derivation (unchanged from the prior note, re-verified against `plan.yaml` at `cd6a3c0d`)

| Task(s) | change_type | Matrix obligation |
|---|---|---|
| T-01, T-03, T-05, T-07, T-10 | `scaffolding` | none |
| T-02, T-04, T-06 | `logic` | `unit` (always) |
| T-08 | `cross_module` | `unit` + `integration` (always) |
| T-09 | `config` | `touches_config_shape` = **false** — additive `test_kinds.issue_types_live` entry, identical shape to the two existing `locally_run` siblings; no existing key's container type/required-ness/nesting changed. Moot anyway: T-08 already floors `integration`. |
| T-11, T-12 | `docs` | none |

**Floor for the whole diff = `unit` + `integration`.** No other kind is obligated.

## Suite-driver runs (rc captured in a variable, never inferred; every invocation `env -u HARNESS_AGENT_TYPE`)

| invocation | rc | `^FAIL ` count |
|---|---|---|
| `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | **0** | **0** |
| `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | **0** | **0** |

Unit log: 1270 lines, nine `N/N checks passed` self-test tallies, all green — final driver line
not read as a whole-suite summary (per Expertise G-04). Integration log: 3532 lines, 49 files,
all green including `test-anchor-directions.py` (the file that failed at the older commit) and
`test-check-state.py`/`test-check-domain.py` (the slow standing sweeps).

## Per-file table — the ten files the dispatching lead cited, run standalone (own `rc=$?` each)

| path | rc | `^FAIL ` count |
|---|---|---|
| tests/integration/test-anchor-directions.py | 0 | 0 |
| tests/unit/test-issue-types-pin.py | 0 | 0 |
| tests/unit/test-issue-types.py | 0 | 0 |
| tests/integration/test-gh-issue-types.py | 0 | 0 |
| tests/integration/test-gh-sync.py | 0 | 0 |
| tests/integration/test-gh-backlog-issue-types.py | 0 | 0 |
| tests/integration/test-factory-issue-types.py | 0 | 0 |
| tests/unit/test-factory-gh.py | 0 | 0 |
| tests/integration/test-factory-decompose.py | 0 | 0 |
| tests/integration/test-factory-integration.py | 0 | 0 |

**Agrees exactly with the dispatch's given measurement (exit 0 / FAIL 0, all ten) and with the
unit driver.** No disagreement to flag.

## Adequacy — do the green kinds actually bind the changed production units?

- `gh_issue_types.py` (net-new, T-02): directly imported and exercised by
  `tests/unit/test-issue-types.py` (12 assertion groups per-value, not loop-wide counts, per the
  task's own verify contract) — bound.
- `gh-sync.py`, `factory_gh.py`, `factory_decompose.py` each carry `import gh_issue_types`
  (confirmed by direct grep at :92, :29, :44 respectively) and are exercised end-to-end by the
  integration suites that spawn them as subprocesses against a fake `gh` — bound, not merely
  co-located.
- The F-02 ruling is visibly landed, not just claimed: `test-gh-sync.py:763-766`'s single amended
  assertion now checks the exact GraphQL `owner=implentio`/`name=fake` values on an `api graphql`
  line, replacing the old blanket `--repo` check — confirmed by direct read, not inference.
- `feature-schema.json`'s two new optional `typed` mappings (T-04 §9) are exercised by both
  `test-gh-issue-types.py` and `test-factory-issue-types.py`, which write real receipts through
  the schema and would refuse (`MergeRefusal`) on a wrong shape — bound.
- No coverage gap found between Phase-1-derived expectations (BRIEF REQ-01..REQ-11) and what
  actually runs: every REQ traced in `plan.yaml` maps to a task whose named test(s) above are
  green and were confirmed test-first via the earlier validator note's receipt audit (T-01→T-02,
  T-03→T-04, T-05→T-06, T-07→T-08, all supported) — not re-audited here since the commits since
  then only added T-12's anchor fix, not new production logic.

## `issue_types_live` (manual/locally-run kind, T-09/T-10)

Per operator ruling F-03, resolved as **locally-run, recorded — capability genuinely absent**.
Independently ran the probe directly at `cd6a3c0d` (read-only default per D-19, no network
mutation attempted):

```
$ python3 tests/manual/probe-issue-types.py
probe-issue-types: CAPABILITY ABSENT mruangutai/harness declares no native issue types
rc=0
```

This note is itself the recorded run the verification-rules skill requires for a diff touching
this kind's `detect` surface. Not a gate failure; not counted toward the matrix floor (the matrix
never obligates `issue_types_live` — it isn't in `test_matrix`, only in `test_kinds`).

## Kinds not obligated (soft skip, unchanged reasoning from the prior note)

`component`, `ui`, `eval`, `functional`, `typecheck`, `omp_session_accessor`,
`handoff_comprehension` — none obligated by this diff's change types, none touched.

## Cleanliness

`git status --porcelain` before this write showed only `feature.json` (pre-existing, not
mine) and two sibling reviewers' own new notes — none of it mine, none touched. This note and my
observations-log append are my only writes.
