# Receipt — harness-backend-dev — BUG-201-depends-on-integrity — T-03 c2

BLUF: All ten verify suites are now green. Three pre-existing synthetic fixtures were repaired to
construct legal plans; no assertion was weakened, deleted, or retargeted anywhere except the three
drops explicitly authorized for decompose case 18. No `factory.issues` map changed. No case that was
green before this cycle reddened.

## Repair 1 — `tests/unit/test-factory-claim.py`

Added task entries so every `depends_on` id resolves to a real task in its fixture's `plan.yaml`,
via the file's own `task_dict` helper (no second fixture style):
- `FEAT-02-block` plan (`:365-374`): added `task_dict("T-02")`, `task_dict("T-03")`,
  `task_dict("T-04")`, `task_dict("T-99")`.
- kaya `SEG_FEATURE` plan (`:377`): added `task_dict("T-88")` alongside the existing `T-77`.
- harness `SEG_FEATURE` plan (`:382`): added `task_dict("T-99")` alongside the existing `T-77`.

Confirmed: every `feature.json` `factory.issues` map is byte-for-byte unchanged (`:371-373` block
map still `{"T-02": 601, "T-03": 602, "T-04": 603}`, no `T-99`; `:378` kaya map still `{"T-77": 850}`,
no `T-88`; `:387` harness-seg map still `{"T-99": 954}`). No asserted edge was deleted or retargeted
— every existing `depends_on` list is untouched; only new sibling task entries were appended.
125/125 checks pass, including all 16 previously-failing cases; no previously-green case reddened.

## Repair 2 — `tests/integration/test-check-plan-routes.py:987`

Changed the `depends_on` budget filler from `[T-00, T-01]` (T-00 dangling) to `[T-01, T-01]` — both
entries name the plan's sole task `T-01` (self-reference is the rule's documented null action;
duplicates are not rejected). Added one comment line (`:987-988`) stating the entries are budget
filler pointing at the plan's own task. `N_DEPS` (`:972`) and `EXPECTED` (`:973-974`) are untouched.
`case_23j_every_budgeted_field_counts_exactly_once` and `case_23j2_...` both pass; full suite: ALL PASS.

## Repair 3 — `tests/integration/test-factory-decompose.py` case 18 (`:728-740`)

Rewritten to disposition A, keeping the existing fixture `task("T-01", depends_on=["T-99-missing"])`.
Retitled to state the new subject (a dangling blocker refused at load, before any remote write).
Kept/added assertions:
- exit code exactly `2` (was: exit 0)
- stderr contains both `T-01` and `T-99-missing` (kept, unchanged)
- `"Traceback"` appears nowhere in stdout or stderr (new)
- `rec.mutating_calls() == []` (new; shape has precedent at case 19's third run, `:782`)

Dropped (per disposition A, all three explicitly authorized): the exit-0 assertion, both payload
assertions (`edges_skipped`, `edges_drawn`), and the `json.loads(out)` call that fed them — there is
no payload on a refusal, and that `json.loads` is what previously aborted the suite. Did NOT assert
the absence of "unexpected failure", so the case survives a later typed-refusal upgrade. Measured
behavior before the edit: exit `2`, stderr
`factory: decompose: unexpected failure: PlanSchemaError: failed to parse YAML in <path>: depends_on
names task ids absent from this plan - T-01 to T-99-missing — re-run with FACTORY_DEBUG=1 for a
traceback` (no literal "Traceback" substring). 162/162 checks pass; full suite green.

No edit made to `factory_decompose.py` (the dead skip branch at `:641-648` was left untouched, per
Q-ADV-8). No edit made to `harness_yaml.py`, `test-factory-claim-mutation.py`, the plan, or the BRIEF.

## The ten final lines (each run individually, `env -u HARNESS_AGENT_TYPE python3 <path>` from worktree root)

1. `tests/unit/test-plan-depends-on.py` → `12/12 checks passed.`
2. `tests/integration/test-plan-merge.py` → `PASS test-plan-merge.py`
3. `tests/unit/test-harness-yaml-corpus.py` → `16/16 checks passed.`
4. `tests/integration/test-harness-yaml.py` → `ok   test_load_plan_accepts_a_station_only_record_and_only_with_a_station` (exit 0)
5. `tests/unit/test-factory-claim.py` → `125/125 checks passed.`
6. `tests/unit/test-factory-claim-mutation.py` → `KEY-COLLAPSE PROOF: FAIL BUG-1290 5b printed` (exit 0; recovered with NO edit to this file, as required)
7. `tests/integration/test-gh-sync.py` → `ok    F-01 (set-feature-station exits non-zero): and that line carries a literal post-merge-sweep.sh gates on, so the sweep keeps the worktree holding the only record of the station` (exit 0)
8. `tests/integration/test-check-plan-routes.py` → `ALL PASS`
9. `tests/integration/test-factory-decompose.py` → `162/162 checks passed.`
10. `tests/integration/test-check-state.py` → `ok - exit code unchanged by INV-21 (a: 1, b: 1)` (exit 0)

All ten green. No reddened case to report.

## Working tree

Worktree `git status --porcelain` shows only: `tests/unit/test-factory-claim.py`,
`tests/integration/test-check-plan-routes.py`, `tests/integration/test-factory-decompose.py`, this
receipt, plus pre-existing T-01/T-02 work (`harness_yaml.py`, `test-plan-merge.py`,
`test-plan-depends-on.py`, feature.json/plan.yaml, earlier receipts). Main checkout at
`/Users/molchairuangutai/GitHub/harness/` confirmed clean for all four files this task touches — an
earlier leaked edit to `tests/unit/test-factory-claim.py` there was caught mid-cycle (edit tool call
using a relative path resolved against the main checkout instead of the worktree) and reverted with
`git checkout --` before the correct, worktree-absolute-path edit was made.

Not committed. No formatters, linters, or project-wide suites run beyond the ten named above.
