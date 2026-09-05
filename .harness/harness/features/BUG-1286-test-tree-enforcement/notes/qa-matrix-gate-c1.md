PASS

# QA test_matrix gate — BUG-1286-test-tree-enforcement (c1)

**BLUF: PASS.** Both required kinds (`unit`, `integration`) are satisfied with named, non-vacuous
tests; own commands corroborate the orchestrator's figures exactly; T-01's test-first order is
genuinely demonstrated (recorded RED with traceback, then GREEN); the case-11 positive control and
the integration ordering assertion are both non-vacuous by inspection and by a passing run that
distinguishes from the failure mode each guards against. `suite-census.py` is correctly a manual
instrument, not a running kind, and is not credited as coverage. HEAD unchanged at `d2ccea0a`,
nothing staged.

## 1. Change type and required kinds

Diff spans a `cross_module` production+unit task (T-01, `suite_layout.py` +
`tests/unit/test-suite-layout.py`), two `scaffolding` tasks (T-02 integration test, T-03 census
script), and two `docs` tasks (T-04 audit note, T-05 DEC-213). `test_matrix` (`harness.json:173-177`):
`cross_module.always = [unit, integration]`. `scaffolding.always = []`, `docs.always = []` — these
contribute nothing beyond what `cross_module` already floors. Feature is a BUG: `bugfix.always =
[unit]` (already subsumed) and `bugfix.when = [{kind: __bug_class__, if: match_bug_class}]`. I
grepped the tree (`.claude/skills/harness/bin`) for `match_bug_class`/`bug_class` — no
implementation exists anywhere in this checkout (consistent with repo Expertise G-08: the
predicate is an unresolvable placeholder, no bug-class taxonomy entry fires for any diff yet). No
`when` clause fires. **Required set: `unit`, `integration`. No more, no less.**

## 2. State per required kind

- **unit — satisfied.** `tests/unit/test-suite-layout.py` (diff-added, 11 new cases) run inside the
  `unit` bucket by `run-unit-tests.sh --kind unit`. Named evidence: cases 1–11, e.g. `case 1: rogue
  tracked file reported exactly once`, `case 11 behavioural: positive control offender is detected`,
  `case 11 hygiene: every running-kind detect pattern is certified` (all PASS, see run log below).
- **integration — satisfied.** `tests/integration/test-run-unit-tests-layout.py` (diff-added, 5 new
  git-backed cases) run both directly and inside the full `integration` bucket
  (`run-unit-tests.sh --kind integration`, 1240/0 across 46 files, includes this file). Named
  evidence: `git tracked rogue refused before sentinels`, `git three tracked rogues reported in
  sorted path order`, `git enumeration failure refused before sentinels`, `git untracked rogue is
  not reported and both sentinels run`, `git clean tree runs both sentinels` — all PASS.

## 3. Commands run — own exit status and counts

| Command | Exit | PASS | FAIL | Notes |
|---|---|---|---|---|
| `run-unit-tests.sh --kind unit` | 0 | 341 | 0 | 27 files — **corroborates** orchestrator's 341/0/27 exactly |
| `python3 tests/integration/test-run-unit-tests-layout.py` | 0 | 14 | 0 | **corroborates** orchestrator's 14/0 exactly |
| `run-unit-tests.sh --check-layout` | 0 | — | — | silent/clean, no `MISCONFIGURED:` lines |
| (extra, G-04) `run-unit-tests.sh --kind integration` | 0 | 1240 | 0 | 46 files, full bucket bind confirmed (own-command binding, not just detect-glob match) |

All four run with `env -u HARNESS_AGENT_TYPE` (repo Expertise G-07: with it set, `test-plan-merge.py`
fails 11 checks unrelated to this diff). `$?` captured directly, no pipe.

## 4. T-01 test-first audit

Receipt `notes/receipt-harness-backend-dev-T-01-c1.md` §1 records a genuine RED: ran
`python3 tests/unit/test-suite-layout.py` against the **unmodified** `suite_layout.py` and captured
an actual traceback (`AttributeError: module 'suite_layout' has no attribute 'DOCUMENTED_EXCEPTIONS'`,
exit 1) plus a named `FAIL case 1: ...` line — this is recorded failing output, not a bare claim of
red. §2 records GREEN after the implementation (46/46, exit 0). This is evidence of *order*, not
just of correctness — **verdict: satisfied.**

## 5. Falsifiability of the three surfaces (step 5)

- **`tests/unit/test-suite-layout.py` case 11 — non-vacuous, present, config-derived.** Read
  `select_control_candidate` (`test-suite-layout.py:482-490`): iterates a fixed literal
  `CANDIDATE_CORPUS` (:473-479) but *selects* using the live matcher
  (`code_grade._is_test_path`, `suite_layout.is_test_shaped`) against `test_kinds_cfg` loaded from
  the real `harness.json` (`repo_cfg["test_kinds"]`, not a copied/hardcoded value). It is not
  hardcoded to a path. The control is **not** silently skipping: my own `run-unit-tests.sh --kind
  unit` run shows `PASS case 11 behavioural: positive control offender is detected` (not the
  `INAPPLICABLE` print path at line 524-526), i.e. a candidate qualified and the assertion fired and
  passed for real. The control's subject (`.harness/tools/test_dir/gen.py`) is exactly the
  disclosed BRIEF residual — a path the runner's `**/test_*.py` glob counts via directory-component
  crossing but whose basename no vocabulary can refuse — so a genuine implementation bug in
  `offenders()`'s leak-detection (e.g. always returning `[]`) would flip this specific assertion red
  while `real_tracked` stays green; it is not testing something structurally guaranteed to be true
  by its own selection precondition. **Verdict: non-vacuous.**
- **Integration ordering assertion — non-vacuous.** `git tracked rogue refused before sentinels`
  (`test-run-unit-tests-layout.py:82-93`) asserts `p.returncode == 2 AND
  "PASS test-unit.py" not in p.stdout`. A runner that ran the unit sentinel *before* checking
  layout and only refused afterward would still have printed `PASS test-unit.py` to stdout before
  exiting 2 — the assertion would then read `False` and redden. Both orderings are NOT
  indistinguishable to this check. **Verdict: non-vacuous.**
- **`tests/manual/suite-census.py` — correctly a manual instrument, not a running kind.** It lives
  under `tests/manual/`, which no `active`/`locally_run` `test_kinds` entry's `detect` selects for
  execution (only `omp_session_accessor` and `handoff_comprehension` reach specific
  `tests/manual/probe-*.py` files by exact name, and `suite-census.py` is neither). It is not run by
  any of the three gate commands above and I do not credit it toward `unit`/`integration` coverage —
  it is T-03/T-04 scaffolding+docs evidence (census/audit), out of this gate's required-kind scope.

## 6. Worktree state

`HEAD` = `d2ccea0a686bbff06f2b3782e7fe346340bcb503` (unchanged). `git status --porcelain`: only
`STATE.md`, `feature.json` (modified) and two `observations/*.md` (untracked) under this feature's
own tracking directory — pre-existing orchestrator/sibling checkpointing, not touched by this gate
run. Nothing staged. No mutation probe was needed for this gate (case 11's control already fires for
real against the live tree, and the receipt's own six-scenario probe at
`/tmp/bug1286_probe` — read, not re-run by me — already exercises the hygiene mutants); no scratch
copies were made in this session.

## Open questions

None — matrix fully resolved, no BLOCKED conditions encountered.
