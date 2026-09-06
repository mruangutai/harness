# QA test-matrix gate — FEAT-55-issue-types-created-work — 2026-09-05

## Verdict: FAIL

A required kind (`integration`) is genuinely red: `tests/integration/test-anchor-directions.py`
fails on two lines T-12 added to `github-mirror.md`. This is a real, named assertion failure, not
misconfiguration, and it traces directly to this feature's own diff. Route back to **T-12**.

## Change-type derivation (from the diff, not the dispatch's framing)

Read the matrix from the worktree's post-change `.harness/harness.json:156-234` (this file is
itself in the diff; the POST-change version is what ships). Per-task `change_type` from
`plan.yaml`:

| Task | change_type | Matrix obligation |
|---|---|---|
| T-01, T-03, T-05, T-07, T-10 | `scaffolding` | `always: []` — none |
| T-02, T-04, T-06 | `logic` | `always: [unit]` |
| T-08 | `cross_module` | `always: [unit, integration]` |
| T-09 | `config` | `always: []`, `when: [integration if touches_config_shape]` |
| T-11, T-12 | `docs` | `always: []` — none |

**Predicates evaluated:**
- `touches_config_shape` (config, T-09): **false**. T-09 adds one net-new key
  (`test_kinds.issue_types_live`) to `.harness/harness.json`, in the identical shape as the two
  sibling `locally_run` entries already present (`omp_session_accessor`, `handoff_comprehension`
  at :282-295) — same keys (`detect`/`exclude`/`cmd`/`status`/`runner_note`), no existing key's
  container type, required-ness, or nesting changed. This is an additive instance of an
  already-recognized shape, not a shape change (contrast DEC-212's `stations` mapping→list
  example). Moot regardless: T-08's `cross_module` already floors `integration` unconditionally.
- No task is `bugfix`, `frontend`, `feature`, `api`, or `ai_behavior` — those `when`/`always`
  clauses do not fire anywhere in this diff.

**Floor for the whole diff = `unit` (always, from `logic`/`cross_module`) + `integration`
(always, from `cross_module` T-08).** No other required kind.

## Per-kind matrix table

| kind | required? | resolution state | evidence path | verdict |
|---|---|---|---|---|
| unit | yes (logic, cross_module) | **satisfied** | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | contributes PASS |
| integration | yes (cross_module T-08) | **missing/red — named test fails** | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` → `test-anchor-directions.py` | **FAIL** |
| component | no (no `frontend` task) | not applicable (unresolved, not obligated) | — | soft skip |
| ui | no (no `has_interaction_flow`) | not applicable (unresolved, not obligated) | — | soft skip |
| eval | no (no `ai_behavior` task) | not applicable (`status: excluded`, DEC-187, and not obligated anyway) | — | soft skip |
| functional | n/a | not applicable (`status: excluded`, DEC-187) | — | soft skip |
| typecheck | no | not applicable (not in matrix, no `.ts`/`.tsx` touched) | — | soft skip |
| omp_session_accessor | not touched by this diff | not applicable — surface untouched | — | soft skip |
| handoff_comprehension | not touched by this diff | not applicable — surface untouched | — | soft skip |
| issue_types_live | touched (probe added, kind registered by T-09) | **locally-run, recorded** | ran `tests/manual/probe-issue-types.py` directly (see below) | recorded, not a gate failure |

## Suite-driver runs (each `rc=$?` captured immediately, never a log tail read)

Driver resolved: only `.agents/skills/harness/bin/run-unit-tests.sh` exists in this repo — there
is no separate `tests/run-unit-tests.sh` (confirmed: `ls tests/run-unit-tests.sh` → No such
file). One driver, two kind invocations.

| invocation | rc | `^FAIL ` count | verdict |
|---|---|---|---|
| `env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh --kind unit` | **0** | **0** | satisfied |
| `env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh --kind integration` | **1** | **2** | FAIL — both FAILs are one named test: `test-anchor-directions.py` |

The unit run's log (`/tmp/qa-unit.log`, 1270 lines) shows nine `N/N checks passed` self-test
tallies (33, 64, 244, 30, 120, 112, 16, 15, 39, 10) and 318 `^PASS ` script lines — read for
content, not tailed for the driver's own final line (which per G-04/harness-qa Expertise is not
the per-script verdict).

The integration run's log (`/tmp/qa-integration.log`, 3532 lines) shows every other script green;
the sole failure:

```
----- test-anchor-directions.py (exit 1, 2.24s) -----
PASS - SC-04 S1 read qa gate
... (11 PASS lines) ...
FAIL - reviewed-sha whole scope
VIOLATION .claude/skills/harness/references/github-mirror.md:19: unanchored instruction path: .claude/skills/harness/bin/gh_issue_types.py
VIOLATION .claude/skills/harness/references/github-mirror.md:24: unanchored instruction path: .harness/harness.json
scanned 62 file(s), 2 violation(s)
FAIL test-anchor-directions.py
```

**Confirmed this is a genuine feature regression, not pre-existing drift**: `git diff
eb9d044e..7dc0ee92 -- .claude/skills/harness/references/github-mirror.md` shows both flagged
lines (19 and 24) are net-new content added by T-12 ("Add the eighth read-back purpose and the
label paragraph to github-mirror.md"). Line 19's new table row names
`.claude/skills/harness/bin/gh_issue_types.py`; line 24's new paragraph names
`.harness/harness.json`. Neither path carries the `<HARNESS_CONTROL_PLANE_ROOT>/` anchor
`check-instruction-paths.py` requires of instruction prose (`.agents/skills/harness/bin/check-instruction-paths.py:90-94`).
`test-anchor-directions.py` is a standing whole-repo sweep (not new to this diff), and it is
exactly the mechanism doing its job: catching an instruction-anchoring regression this feature's
own new prose introduced. **Owning task: T-12.**

## Per-file table — the seven directly-named files (each run standalone, separate `rc=$?`)

Corroborating the orchestrator's claim independently, not restating it:

| path | rc | `^FAIL ` count |
|---|---|---|
| tests/integration/test-gh-issue-types.py | 0 | 0 |
| tests/integration/test-gh-sync.py | 0 | 0 |
| tests/integration/test-gh-backlog-issue-types.py | 0 | 0 |
| tests/integration/test-factory-issue-types.py | 0 | 0 |
| tests/integration/test-factory-decompose.py | 0 | 0 |
| tests/unit/test-factory-gh.py | 0 | 0 |
| tests/integration/test-factory-integration.py | 0 | 0 |

**Agrees with the orchestrator's measurement on all seven files.** No disagreement to report.

## Test-first audit (T-01→T-02, T-03→T-04, T-05→T-06, T-07→T-08)

The branch is a single squashed commit (`ef591a53`, "nine of twelve tasks landed") over the
whole range — `git log` over per-file paths cannot show intra-feature ordering; **ordering by
git history alone is undetermined**, per instruction not inferred from mtimes either. Ordering
**is** supported by the build-time receipts, read directly:

- **T-01 → T-02, supported.** `receipt-harness-backend-dev-T-01-c1.md` shows
  `test-issue-types.py` red with `ModuleNotFoundError: No module named 'gh_issue_types'` (module
  did not exist yet) and the pin guard 2-FAILED, *before* `gh_issue_types.py` existed.
  `receipt-harness-backend-dev-T-02-c1.md` shows the identical test file, proven untouched
  (`git status --porcelain` still `??`, same as T-01 left it), now `ALL PASSED` (55 checks)
  after T-02 wrote only `gh_issue_types.py`.
- **T-03 → T-04, supported (with a documented interruption).** `receipt-...-T-04-c1.md` shows
  `test-gh-issue-types.py` at 24 FAILED before the fix, all traced to two named blockers
  (a `feature-schema.json` refusal and a label-suppression gap), and the cycle returned
  `BLOCKED` rather than a false green. The current tree (measured above: 0 FAIL) shows the
  blockers were resolved in a later cycle — consistent with, not contradicting, test-first order.
- **T-05 → T-06, supported.** `receipt-...-T-06-c1.md` explicitly runs
  `test-gh-issue-types.py` "FAILS UNAIDED, as forecast" (19 FAIL, traced to the same
  pre-existing schema defect, not T-06's), then reports `test-gh-backlog-issue-types.py` and
  `test-gh-sync.py` green **unaided**, and the full gh-sync suite green.
- **T-07 → T-08, supported.** `receipt-...-T-08-c1.md` shows `test-factory-issue-types.py` and
  `test-factory-decompose.py` failing with `MergeRefusal(11): undeclared key 'typed'` (28 FAILED)
  before the schema fix landed, then `ALL PASSED, EXIT=0` after, with a scoped
  `git status --porcelain` showing `test-factory-issue-types.py` untouched (still `??`, T-07's
  file, unmodified by T-08).

No violation found in this audit; the record supports red-before-green in all four pairs.

## `issue_types_live` — manual/locally-run resolution

Ran the probe directly (not registered `cmd`, just observation — no live network call was
attempted; the probe's own default is read-only per D-19):

```
$ python3 tests/manual/probe-issue-types.py
rc=0
probe-issue-types: CAPABILITY ABSENT mruangutai/harness declares no native issue types
```

Resolves as **locally-run, recorded** — capability genuinely absent for this repository, reported
correctly, exit 0, one verdict line naming the repo. Not a gate failure. **This note is the
recorded run** required by the verification-rules skill for a diff that touches this kind's
`detect` surface (T-09 registered the kind; T-10 added the probe).

`suite_layout.py`'s registration rule (`.claude/skills/harness/bin/suite_layout.py:29-33`, "no
test-shaped file remains under bin") is satisfied: the probe lives under `tests/manual/`, not
`bin/`. Cross-checked uniqueness directly against `harness.json`'s `test_kinds`: exactly one
`locally_run` kind (`issue_types_live`) names `tests/manual/probe-issue-types.py` in its
`detect`; the other two `locally_run` kinds name different probe files. Registration rule fully
satisfied.

## `matrix_ok`

**false.** A required kind (`integration`) is red on a named, feature-caused assertion failure.

## git status --porcelain (verbatim, run before this artifact write)

```
(empty)
```

No test-only fix was made; this artifact and the observations-log append are the only writes by
this run.

## Open questions

None that need routing beyond the FAIL itself (which names its owning task, T-12, and is not a
harness defect — `test-anchor-directions.py` did exactly its job).
