# QA gate-only re-run at the pin — BUG-201-depends-on-integrity, c1

**VERDICT: the segment's PASS reproduces at the pin.** `matrix_ok: true`. All standing kinds and
all ten T-03/T-06-named suites exit 0 with case counts matching the segment's recorded baseline
exactly — none collapsed.

## Pin vs HEAD
`git rev-parse HEAD` = `6896ebe7c02df49df7b9d8c5f6e7a92a37dcd5e4` — **HEAD IS the pin**, not an
ancestor/descendant relation to resolve. `af859ee8..6896ebe7` carries 9 commits (plan, T-01..T-06,
SIMPLIFY, QA-c1 PASS, panel-record). Working tree: `git status --porcelain` shows exactly one
dirty file, `feature.json`, and its only hunk is `review_sha: "none" -> "6896ebe7..."` — the pin
bookkeeping write itself, not code. No other drift. This run is against the pin as committed.

## Required kinds (bugfix, all T-01..T-06 `change_type: bugfix`)
- `touches_runtime_code` is true (`harness_yaml.py`, `factory_claim.py`, `gh-sync.py` all in the
  diff) → **unit required** by `test_matrix.bugfix.when` (harness.json:206-209).
- `fix_confined_to_tests_and_contract_docs` is **false** (production files are touched), so the
  matrix's own `when` clause does not independently obligate `integration`. It is required anyway
  by direct selection: the diff touches `tests/integration/**` (`test-plan-merge.py`,
  `test-gh-sync.py`, `test-check-plan-routes.py`, `test-factory-decompose.py`), matching
  `test_kinds.integration.detect` (harness.json:320). Both kinds are `status: active` with real,
  non-null `cmd`.
- `__bug_class__`/`match_bug_class`: per repo Expertise G-08, this predicate is an unresolvable
  placeholder in this project — it never fires for any diff. Correctly does not add a kind here.

## Per-kind and per-suite results (all run `env -u HARNESS_AGENT_TYPE`, per repo Expertise G-07)

| kind/suite | exit | count | vs. segment baseline |
|---|---|---|---|
| `run-unit-tests.sh --kind unit` | 0 | 33 files, pool all PASS | 33 — matches |
| `run-unit-tests.sh --kind integration` | 0 | 49 files, pool all PASS | 49 — matches |
| tests/unit/test-plan-depends-on.py | 0 | 12/12 | 12 — matches |
| tests/integration/test-plan-merge.py | 0 | 298 `PASS` lines incl. bug201/bug201a/bug201b | new suite, n/a |
| tests/unit/test-harness-yaml-corpus.py | 0 | 16/16 | 16 — matches |
| tests/integration/test-harness-yaml.py | 0 | 22 `ok` lines | n/a |
| tests/unit/test-factory-claim.py | 0 | 133/133 | 133 — matches |
| tests/unit/test-factory-claim-mutation.py | 0 | BASELINE 3/3 ok; MUTANT reddens 3/3 then key-collapse 1/1 (the `FAIL` lines are the proof's own deliberate red output, not real failures) | n/a |
| tests/integration/test-gh-sync.py | 0 | 318 `ok` lines | n/a |
| tests/integration/test-check-plan-routes.py | 0 | 122 `PASS` lines, ends `ALL PASS` | n/a |
| tests/integration/test-factory-decompose.py | 0 | 162/162 | 162 — matches |
| tests/integration/test-check-state.py | 0 | 217 `ok -` lines | n/a |

No suite reported a discovery/case count of 0 or a suspiciously small number relative to the
segment's recorded figures — none is a sweep-over-nothing false green.

## Discrimination judgement for SC-05 / SC-02 — MEASURED, not merely reasoned

I directly observed the paired-allow half of every deny case execute and pass at the pin, which is
what makes each corresponding deny assertion non-vacuous:

- **T-01** (SC-05 unit half): `test-plan-depends-on.py` line 2, "a depends_on entry naming a task
  id present in the same plan is accepted" — `ok`, alongside case 1's deny. Cases 6a/6b (opposite
  type-coercion directions) and 6c (deny) all `ok`.
- **T-02/T-03** (SC-02, write route): `test-plan-merge.py` — `bug201a` denies (exit 5, `ILLEGAL
  PLAN`, `T-99`, byte-identical file) immediately followed by `bug201b` "the paired apply naming a
  real dependency exits 0" and "T-03 is present after the allowed apply" — both `PASS`, both
  observed executing.
- **T-05** (SC-05/SC-02 consumer half): `test-factory-claim.py` line 96, "(D0) load_plan RETURNS
  on the paired legal fixture" and line 100 "(Dc) poll does not crash... #790 claimed despite
  #780's dangling plan" — both `ok`. `test-gh-sync.py` lines 309-310 (case e, start-task paired
  allow) and 314-315 (case g, status-Ready paired allow) both `ok`, bracketing the case-d/case-f
  deny+diagnose assertions at lines 306-307 and 311-313.

Every deny case I checked has its documented paired-allow case executing and green beside it at
this exact pin — the suites are discriminating, not deny-everything. This is a measured
observation over the executed run (O-03: this is measured, since I read the actual paired-allow
lines execute, not merely reasoned from the test source).

## Findings
None. No kind is missing, misconfigured, or locally-run-without-a-record (no `locally_run` kind's
`detect` glob matches this diff's changed files). No collapsed count.

## Note on scope
Per dispatch, I did not restate `qa-harness-qa-c1.md`'s own content — that PASS is not what I
graded. This note establishes that PASS is reproducible, independently, at the pinned sha.
