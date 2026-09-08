# QA gate-only re-run at the pin — BUG-201-depends-on-integrity, c2

**VERDICT: MF-1 is closed and the segment's gate reproduces at the new pin.** `matrix_ok: true`.
All standing kinds and all nine feature-named suites exit 0; every case count matches the c1
baseline exactly — none collapsed. Grades confirm the contract precisely.

## Pin vs HEAD
`git rev-parse HEAD` = `626bb59934b8801bf1abdc86379aa313e021c77b` — HEAD IS the new pin. `git
status --porcelain` shows exactly one dirty file, `feature.json` (the pin-bookkeeping write, not
code) — no other drift. `6896ebe7..626bb599` touches exactly one production file
(`harness_yaml.py`, 37 ins/17 del) plus feature bookkeeping/notes/observations (7 files) — no test
file changed this cycle.

## The change (read directly, not from the contract)
`_validate_plan_depends_on`'s inline dangling-edge scan is split into two new helpers,
`_depends_on_entries` (coerces one task's `depends_on` to a list, raising the same
`PlanSchemaError` on a non-list) and `_dangling_edges` (the outer/inner loop building the
`(tid, entry)` pairs). Diffed line-by-line: identical control flow, identical exception text,
identical iteration order (outer over tasks, inner over entries) — a pure extraction, not a
behavior change. No new branch, no new code path introduced.

## Required kinds — resolved against the FULL feature diff (repo Expertise G-11), not this
## cycle's diff alone
This cycle's own diff touches only one production file and zero test files. Per G-11 the matrix's
change-type predicates are evaluated against `merge-base..HEAD` for the whole feature, which is
unchanged from c1: `touches_runtime_code` true → **unit** required (harness.json:206-209);
`fix_confined_to_tests_and_contract_docs` false, but the full diff still touches
`tests/integration/**` (test-plan-merge.py, test-gh-sync.py, test-check-plan-routes.py,
test-factory-decompose.py) matching `test_kinds.integration.detect` (harness.json:320) →
**integration** required by direct selection. Both `status: active` with real `cmd`
(harness.json:287, 322). `match_bug_class` still an unresolvable placeholder (repo G-08) — adds
nothing.

## Per-kind and per-suite results (all run `env -u HARNESS_AGENT_TYPE`, repo G-07)

| kind/suite | exit | discriminated count | vs. c1 baseline |
|---|---|---|---|
| `run-unit-tests.sh --kind unit` | 0 | 33 files, pool all PASS; `^FAIL ` count = 4 | 33 files — matches; the 4 FAIL lines are `test-factory-claim-mutation.py`'s own deliberate BUG-1290 mutation-proof red output inside a script that itself exits 0/PASS — confirmed by reading context (line 1258-1268), not unrelated regression |
| `run-unit-tests.sh --kind integration` | 0 | 49 files, pool all PASS; `^FAIL ` count = 0 | 49 files — matches |
| tests/unit/test-plan-depends-on.py | 0 | 12/12 | 12 — matches |
| tests/unit/test-harness-yaml-corpus.py | 0 | 16/16 | 16 — matches |
| tests/unit/test-factory-claim.py | 0 | 133/133 | 133 — matches |
| tests/integration/test-harness-yaml.py | 0 | 22 `ok` lines | 22 — matches |
| tests/integration/test-plan-merge.py | 0 | 298 `PASS` lines incl. bug201/bug201a/bug201b | 298 — matches |
| tests/integration/test-check-plan-routes.py | 0 | 122 (6 `ok` + 116 `PASS`), ends `ALL PASS` | 122 — matches |
| tests/integration/test-factory-decompose.py | 0 | 162/162 per the script's own printed total (162 distinct `ok`-format lines; naive `^ok` grep undercounts to 161 because one check at line 4 prints `ok   case (d)` with no leading dash/differs by 3 spaces — a counting-method artifact, not a missing case) | 162 — matches |
| tests/integration/test-gh-sync.py | 0 | 318 `ok` lines | 318 — matches |
| tests/integration/test-check-state.py | 0 | 217 `ok` lines (exercised inside the full `--kind integration` pool run, which reported 0 `^FAIL ` across all 49 files including this one; a standalone re-run corroborates 217) | 217 — matches |

No suite reported a discovery/case count of 0 or a suspiciously small number relative to the c1
figures. No collapse.

## Adequacy — does the matrix actually bind the changed unit?
Yes, directly and by name. `tests/unit/test-plan-depends-on.py` (12/12) calls
`_validate_plan_depends_on` — now a 3-line dispatcher over `_dangling_edges`/`_depends_on_entries`
— across all 12 of its cases (accept, deny, both type-coercion directions, the bare-string
`PlanSchemaError` shape case, and the "one exception naming every dangling edge" case), so every
new line in both new helpers is reached by this file alone. `test-harness-yaml-corpus.py` (16/16)
and `test-harness-yaml.py` (22 `ok`) additionally exercise the same call through the plan-loading
path on corpus/template fixtures. `test-plan-merge.py`'s `bug201`/`bug201a`/`bug201b` triplet
exercises the write-time enforcement route through the same function. This is not a near-vacuous
green: the extraction's entire surface (both new helpers) is inside the one function every one of
these suites was already built to hit.

## Grades — MF-1 closure confirmed directly (not merely cited from the contract)
Ran `code-grade.py` on `harness_yaml.py` myself:
- `_validate_plan_depends_on` (line 427): cyclomatic 4 / cognitive 1 / ABC 7.3 → **grade 5**, driver
  cyclomatic+cognitive+abc, bar 4. PASS, closes MF-1 (was grade 3 at c1's pin).
- `_depends_on_entries` (line 391, new): cyclomatic 4 / cognitive 4 / ABC 6.8 → **grade 4**, driver
  cognitive, bar 4. PASS.
- `_dangling_edges` (line 411, new): cyclomatic 4 / cognitive 6 / ABC 6.9 → **grade 4**, driver
  cognitive, bar 4. PASS.

All three at or above the grade-4 production bar. Matches the orchestrator's contract figures
exactly, independently re-derived.

## Findings
None. No kind missing, misconfigured, or locally-run-without-a-record. No collapsed count. MF-1
confirmed closed by direct grade measurement, not by trusting the contract. The extraction is
behavior-preserving on direct line-by-line diff read.

## Scope note
Per dispatch this is gate-only: no test, fixture, source, or plan edit authored. I did not
re-litigate the four c1-dismissed findings (D-1..D-5) or the pre-existing grade-3/grade-2 records
named out of scope.
