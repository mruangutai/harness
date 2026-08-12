# FEAT-14 fix cycle — eight must_fix closed, none declined

**BLUF.** All eight architecture-review `must_fix` are addressed in `BRIEF.md` and `plan.yaml`. The
design is untouched: enforcement point, twelve-key survivor list, six-value enum, `jsonschema` as a
required dependency, and both census pins (`3569a20`, `06ae963`) stand exactly as written.
`check-plan-routes.py` is **0 violations across 10 plans**. Task budgets unchanged where they were
tight: **T-04 = 50, T-08 = 49** (cap 50, `>50` fails).

## The two source facts that decided the shape

- `check-domain.sh:256` — the no-`agent_type` carve-out is the `_governed` **FLAG, not an exit**
  (comment block :243-255: "It used to be a bare `sys.exit(0)`, which silently took the DEC-150
  SHAPE gate below with it"). So the shape phase runs for the **main session**, and fail-closed does
  govern T-04/T-07/T-08's own writes. `.harness/team-config.yaml:15-16` ("check-domain exits 0 when
  a payload carries no `agent_type`") is a **false comment** — raised as Q1, not fixed here.
- `require_or_bootstrap` is reached only under `if _run_domain:` (`check-domain.sh:333`), so the
  shape route has **no bootstrap escape**. None is needed: the remedy is `pip install jsonschema`, a
  Bash command no gate denies — unlike the missing-PARSER case, where the gate cannot read its own
  manifest. Also pinned: this branch needs **stdlib `json` + `jsonschema` only, never PyYAML**, so
  the user-ruled `_no_parser` fail-open at `check-domain.sh:685` must not be copied onto it.

## Eight in, eight out

| # | Disposition |
|---|---|
| MF-1 | **Addressed.** Adopted the advisory: `bin/feature_schema.py` imported **in process** by `check-domain.sh` (D-03 rewritten), so a checker that cannot run is an `except ImportError` branch that appends to `problems` → **exit 2**, and messages go through the existing `_head()` naming the real target. New **SC-16** states the acceptance behaviourally (valid payload + unavailable checker → exit 2, not 1; real path, not a tempfile; one message per sweep). Asserted in T-06's `test-check-domain.py` cases. |
| MF-2 | **Addressed.** T-06's false "shares the bootstrap escape" comment replaced with the verified facts above, including the explicit instruction not to extend the `state.yaml` `_no_parser` fail-open. |
| MF-3 | **Addressed.** Three distinct CLI exit codes in T-01: `0` valid, `1` a file failed validation, `3` the checker could not run. SC-07's test asserts **exactly 3**, and neither 0 nor 1. Distinct codes survive the module adoption because T-03/T-04/T-07/T-08 all read `returncode` from the CLI. |
| MF-4 | **Addressed.** Prohibition now spans **T-04 → T-08** (the reviewer's window), scoped to invoking `gh-sync.py` / `factory_decompose.py` / `factory_claim.py` **against the live `.harness/features/` corpus** — fixture-based suites stay legal, so T-05's own `run-unit-tests.sh` verify is not contradicted. Cites `gh-sync.py:255-256` and `:236-243`. |
| MF-5 | **Addressed.** Receipt renamed `notes/receipt-feature-key-drop.md` (no date; same-line change, free). Never overwritten. Resume semantics pinned so "exactly 14" stays runnable: already-reduced file → skip and count; receipt present but file unreduced → recompute and compare, identical means proceed with the rewrite, different means STOP. |
| MF-6 | **Addressed.** T-03 adds a `--kind unit` step to the **same** `integration` job (the required context is that job's id; no new job, no `name:` key), and amends `tests.yml`'s now-false comment that the unit kind "would have caught none of the defects". Verify asserts `--kind unit` present and `jobs == ['integration']`. |
| MF-7 | **Addressed in T-01, costing T-08 nothing.** The validator dispatches by extension: `.json` → `json.load`, else `harness_yaml.load_file`. A YAML-but-not-JSON `.json` file is rejected. T-08's existing `validator exit` check therefore proves JSON validity for all fourteen for free. |
| MF-8 | **Addressed.** `BRIEF.md` prose corrected to **three** (`check-state.sh`, `check-domain.sh`, `validate-digest.py`; `bash-write-guard.sh` untouched) and states the carve-out is not widened — DEC-174 already names four. The disposition table left alone. |

## Reviewer questions

- **Q1 landing unit — resolved as plan content:** one branch, one PR, written into BRIEF constraints
  (both red windows are working-tree-only; incremental landing leaves the required `integration`
  context red). Carried as a constraint, not a `D-NN` — it fails DEC-149's hard-to-reverse limb.
- **Q2 — resolved as build conduct** in T-07 (respawn the orchestrator, or keep FEAT-14's own state
  writes main-session-direct) and re-stated in T-08, which self-detects the failure.
- **Q3 splitting T-06 — DECLINED, with reason.** Splitting adds a task to T-08's `depends_on`,
  taking T-08 from 49 to 50 and leaving it zero headroom against a hard cap, for a non-blocking
  finding. T-06 is verified by the fixture-based integration suite, and its new cases are per-change
  assertions, which is most of what the split was buying.
- **Q4 — resolved:** schema findings emit the redirection sentence and **not** the `ROUTING`
  constant; the line-budget finding on the same path keeps `deny()` and keeps `ROUTING`.
- **Q5 — resolved free:** T-05 adds a subset assertion (`SHIPPED_STATUSES ⊆ schema status enum`) to
  `test-check-plan-routes.py`, intent-only, covered by the task's existing verify.

## Folded in as content

- **Precondition widened to THREE live flows** — FEAT-12, FEAT-13 and **FEAT-15-domain-product-base**
  (BRIEF, plus T-04 and T-08 intent), and a flow crossing from signature into build **during** the
  window is caught too. FEAT-15 is outside the migration set (no execution-state file) and inside the
  precondition.
- A trap found while editing, closed in T-01: the CLI's no-argument sweep globs
  `.harness/features/*/feature.*` filtered to `.json/.yaml/.yml` rather than naming a literal second
  filename, and fixtures are named neutrally. A hard-coded `feature.yaml` there would have reddened
  T-08's own survivor sweep at the end of the build.

## Evidence

- `python3 .claude/skills/harness/bin/check-plan-routes.py` → `0 violation(s) across 10 plan(s)`.
- Per-task budget recomputed with `BUDGETED_FIELDS` (`check-plan-routes.py:283-287`) against
  `MACHINE_LINES_PER_TASK = 50`: T-01 17, T-02 22, T-03 26, T-04 **50**, T-05 32, T-06 32, T-07 41,
  T-08 **49**, T-09 28, T-10 10.
- `yaml.safe_load` on `plan.yaml`: 10 tasks, 9 decisions, `approval.status: pending`.
- No `notes:` field at any level (the one grep hit is prose inside T-06's `intent:`).

---

# Cycle 2 — the import cost, measured; two preconditions added

**BLUF.** The unbacked "so this costs nothing" is gone. **Importing `jsonschema` costs +42.6 ms**, so
the import is **deferred into the `RE_FEATURE_JSON` branch** rather than sitting at module level. Two
build preconditions are now written where they are checkable: the `unit` suite is **green at
`96d5d5c`**, and **`jsonschema` is NOT installed on this machine**, which would deny T-04/T-07/T-08's
own writes the moment T-06 lands. Design, survivor list, enforcement point and both census pins
(`3569a20`, `06ae963`) are untouched. All three changes are `intent:` or BRIEF prose, and
`intent:` is excluded from the budget by name (`check-plan-routes.py:282-287`), so **T-04 stays 50
and T-08 stays 49**.

## 1. The measurement, and what it decided

Method the operator named — isolated interpreter launches, median of 10, `jsonschema` 4.26.0 installed
to a scratch `--target` dir on `PYTHONPATH` (the repo environment is **not** mutated), python3 3.14.5,
warm bytecode:

| launch | median ms | delta vs bare |
|---|---|---|
| `python3 -c pass` | 17.3 | — |
| `import json` (stdlib) | 17.6 | **+0.2** |
| `import yaml` | 23.7 | **+6.4** |
| `import jsonschema` | 59.9 | **+42.6** |

First (cold, no `.pyc`) import: **395 ms** — `-X importtime` cumulative.

**Material, so it is deferred.** +42.6 ms more than triples a bare interpreter start-up. It is a
*different measurement* from the file's own `~38 ms of ~42 ms` per post-Bash call
(`check-domain.sh:534`) and `104.7 ms` governed path (`:92`) — those are whole-hook figures taken on
another day — so the comparison is order-of-magnitude, not arithmetic. Either way a module-level
import charges it on **every `Write`, `Edit` and `Bash` in the repo**, not on the rare `feature.json`
write. In-file precedent: `check-domain.sh:139` already defers `harness_yaml` for exactly this reason.

**Nothing else moves, and T-06's own verify still passes as written:**

- **T-01 is unchanged.** `sys.modules` caches the first import, so a POST sweep pays the 42.6 ms
  once per invocation, not per file — the exact property T-01's module-level `jsonschema` import was
  written to protect (`plan.yaml` T-01 intent), and the once-per-invocation message flag with it.
- **MF-1's acceptance still holds.** T-01 has `feature_schema` swallow the `jsonschema` `ImportError`
  behind a flag and **return** the REQUIRED line, so it arrives as a returned problem, not a raise:
  `problems` → exit 2, real target path, no tempfile.
- **The new tight `try` catches a different failure** — `feature_schema` itself unimportable
  (`PYTHONPATH` unset, syntax error, file missing). It sits **inside** the branch and appends to
  `problems`; a raise escaping the per-file loop exits 1, which `:14` says is non-blocking, i.e. fail
  open in the one case the checker exists for.
- T-06's verify asserts on the **exit code from running the hook**, never on source text
  (`plan.yaml` T-06 verify), so the deferral changes no assertion.

## 2. `--kind unit` at HEAD — green, measured on the committed tree

`run-unit-tests.sh --kind unit` → **exit 0, 10 scripts PASS, 0 FAIL, 0 SKIP**, run from a
`git worktree add --detach` at **`96d5d5c`** (main HEAD, clean tree). The detached run was necessary:
the session working tree carries uncommitted edits to `run-unit-tests.sh` and three of its test files,
and CI evaluates the committed tree. Both runs produced an **identical** PASS set (md5 of the sorted
PASS lines matches), so the uncommitted edits change nothing here. `--kind unit` exists at `96d5d5c`
(`run-unit-tests.sh:23`), so MF-6 does not put an unrecognised flag on a required job.
**Not a permanent property:** this is green for the suite *before* T-01/T-02 add theirs, and those
need a real `jsonschema`. Re-check immediately before T-03 lands.

## 3. `jsonschema` is absent here — new precondition, operator action

`python3 -m pip list` → PyYAML 6.0.3 and nothing else; `python3 -c "import jsonschema"` →
`ModuleNotFoundError`, observed at `96d5d5c`. The shape phase is fail-closed and deliberately governs
the main-session-direct tasks **T-04, T-07, T-08 — which write `feature.json` themselves**. So the
moment T-06 lands on a machine without the package, those writes are DENIED with exit 2. T-03 installs
it in **CI only**; T-02 **declares** it in `harness-init` and `CLAUDE.md` only. Nothing installs it
here, and nothing should — it is one operator command, not a task. Raised as **Q6 (non-blocking)** —
numbered on from cycle 1's Q1-Q5 above, so no id in this file means two things.

## 4. One disambiguating clause

BRIEF's three-flow precondition now states it is **run 01's Q5**, widened by the operator's own
measurement that found FEAT-15 — **not** run 01's Q3, the baseline/HEAD question already closed.

## Evidence — cycle 2

- `python3 .claude/skills/harness/bin/check-plan-routes.py` → **`0 violation(s) across 9 plan(s)`**,
  exit 0. **Nine is the right total, enumerated rather than assumed:** 15 feature dirs hold 13 plan
  files (5 `plan.yaml`, 8 `PLAN.md`; FEAT-01 and FEAT-13 hold neither), and `_is_shipped`
  (`check-plan-routes.py:386`, `SHIPPED_STATUSES = ("shipped", "abandoned")`) skips exactly four of
  them — FEAT-02, FEAT-03, FEAT-04, FEAT-05. 13 - 4 = 9. Nothing is silently unread: no dir carries
  BOTH plan files, none fails the `X_OK`/`R_OK` checks, and any unreadable path would have exited 2
  with a named list (`:590-595`). **Why cycle 1 recorded 10 against the same tree is NOT determined**
  — flagged as **Q7 (non-blocking)**. It is a counting discrepancy in a note, not a finding about
  this plan.
- `yaml.safe_load` on `plan.yaml`: 10 tasks, 9 decisions, `approval.status: pending`; BRIEF
  `status: pending` at `BRIEF.md:461`. Both census pins still present (8 hits in `plan.yaml`, 13 in
  `BRIEF.md`).
- Budget unchanged by construction: `BUDGETED_FIELDS` excludes `intent:` by name
  (`check-plan-routes.py:282-287`), and every cycle-2 plan edit is inside T-06's `intent:`.
- Line anchors re-read at `96d5d5c` before citing: `check-domain.sh` `:14`, `:92`, `:139`, `:534`.
