# Receipt — harness-backend-dev — T-03 (depends_on referential-integrity rule)

## Verdict: ESCALATE

The rule was implemented exactly as specified, in the one file `files:` names. It cannot be
landed as a green T-03 because the task's own acceptance clause — "All TEN suites in the verify
block pass" — is unsatisfiable without editing files that are outside T-03's `files:` AND outside
every other task's `files:` in this signed plan. Escalating rather than editing the plan or
reaching into those files.

## What was built (confirmed correct against T-01/T-02's own oracles)

`.claude/skills/harness/bin/harness_yaml.py`: added module-level `_validate_plan_depends_on(tasks,
path)` immediately after `_validate_plan_tasks(tasks, path)` inside `validate_plan_doc` (single
call site, single definition). Behaviour matches the intent verbatim: `known` from `str(t["id"])`
over all tasks; `None`/`[]` skipped; non-list `depends_on` raises naming the task id and the field;
every dangling `(task id, entry)` pair across the whole document is collected and raised as ONE
`PlanSchemaError`; no self-dependency/cycle/ordering logic added.

Confirms the required "green for the right reason" cases:
- T-01's `tests/unit/test-plan-depends-on.py`: **10/10 checks passed** — cases 1, 3, 5, 6c (the
  ones the sibling recorded RED) are now green, plus the untouched cases stay green.
- T-02's `tests/integration/test-plan-merge.py`: **`bug201a`'s three assertions now PASS** — exit
  5, output contains `ILLEGAL PLAN` and `T-99`, base file byte-identical; `bug201b` (paired allow)
  and the pre-existing 294 cases all still pass (`test-plan-merge.py` prints `PASS
  test-plan-merge.py`, its own all-clear line).
- `PlanSchemaError` text for the two-dangling-edge case (T-01's case 3 fixture: T-02→T-98,
  T-03→T-99), read directly from the raise:
  `depends_on names task ids absent from this plan - T-02 to T-98, T-03 to T-99`

## The blocker: 4 of the 10 required suites fail, and none for a defect in the rule

Ran the full `&&` chain (env -u HARNESS_AGENT_TYPE), then each of the ten individually per the
dispatch's instruction to report every suite's status. **Literal final line of each:**

1. `tests/unit/test-plan-depends-on.py` → `10/10 checks passed.` — **PASS**
2. `tests/integration/test-plan-merge.py` → `PASS test-plan-merge.py` — **PASS**
3. `tests/unit/test-harness-yaml-corpus.py` → `16/16 checks passed.` — **PASS**
4. `tests/integration/test-harness-yaml.py` → `ok test_load_plan_accepts_a_station_only_record_and_only_with_a_station` (all `ok`, no FAIL) — **PASS**
5. `tests/unit/test-factory-claim.py` → `16 of 125 FAILING.` — **FAIL**
6. `tests/unit/test-factory-claim-mutation.py` → `KEY-COLLAPSE PROOF: FAIL BUG-1290 5b printed` / `BASELINE INCOMPLETE` — **FAIL**
7. `tests/integration/test-gh-sync.py` → (run standalone) all `ok`, exit 0 — **PASS**
8. `tests/integration/test-check-plan-routes.py` → `1 FAILURE(S): ['case_23j_every_budgeted_field_counts_exactly_once']` — **FAIL**
9. `tests/integration/test-factory-decompose.py` → `FAIL (18) exits 0` (`code=2 err=factory: decompose: unexpected failure: PlanSchemaError...`) — **FAIL**
10. `tests/integration/test-check-state.py` → `ok - exit code unchanged by INV-21 (a: 1, b: 1)` (all `ok`) — **PASS**

Confirmed by running the SAME four failing suites against the pre-edit tree (`git stash`): all
four pass at 125/125, 3/3-mutation-reddened, `ALL PASS`, and 163/163 respectively. **The rule, not
a coincidence, causes all four regressions.**

## Root cause: pre-existing fixtures elsewhere encode the exact bug being fixed

Every one of the four failures traces to a synthetic `depends_on` in a test fixture — not a real
committed `plan.yaml` — that names a task id absent from its own plan document, written *before*
BUG-201 to exercise a DIFFERENT feature's behaviour when a blocker reference doesn't resolve:

- `tests/unit/test-factory-claim.py`: `FEAT-02-block`'s fixture plan (line ~369) has
  `task_dict("T-10", depends_on=["T-99"])` where T-99 is not a task in that plan — built on
  purpose for the SC-22 "unresolvable blocker" case. Also `kaya_seg`/`harness_seg` fixtures (lines
  377, 382) use `depends_on=["T-88"]` / `depends_on=["T-99"]` for the unrelated BUG-1290
  segment-resolution cases. `load_plan` now refuses the whole document before factory_claim's
  blocker-gate logic ever runs, so 16 cases (B1, B3, B4, B5, B5-bis, B5-ter, X/SC-13(b),
  BUG-1290 5a/5b/5g) regress from their designed verdict to a generic "no plan could be read".
- `tests/unit/test-factory-claim-mutation.py`: its baseline harness re-runs `test-factory-claim.py`
  and diffs against expectations for BUG-1290 5a/5b — with #5 now failing outright, the mutation
  baseline is incomplete and the suite fails closed.
- `tests/integration/test-check-plan-routes.py`, `case_23j`: its `BUDGETED_FIELDS`-counting fixture
  (line ~987) sets `depends_on: [T-00, T-01]` on the plan's only task `T-01` — T-00 does not exist.
  The plan now fails to load, so no "machine-field lines" total is ever printed.
- `tests/integration/test-factory-decompose.py`, case `(18)`: an EXISTING, pre-BUG-201 case
  expects `factory:decompose` to exit 0 while silently skipping a `blocked_by` edge for a missing
  blocker id (`T-99-missing`), reporting the skip only via stderr diagnostics. The plan now fails
  to *load* at all, so decompose exits 2 with `PlanSchemaError`, not 0.

## Why this is ESCALATE, not a fix-forward

- `test-factory-claim.py` is owned by **T-05**, but T-05's intent is scoped to *adding* a new,
  separate dangling-fixture pair for consumer-diagnosis cases — it does not touch the pre-existing
  `FEAT-02-block`/`kaya_seg`/`harness_seg` fixtures, and T-05 has not run yet regardless.
- `tests/integration/test-check-plan-routes.py` and `tests/integration/test-factory-decompose.py`
  (and `factory_decompose.py` itself) appear in **no task's `files:`** anywhere in this plan. There
  is no task, present or future, assigned to reconcile them.
- T-03's own `files:` is `harness_yaml.py` only. I have no path to make these four suites green
  without editing files this task does not own.
- The plan's own non-migration claim ("all 67/68 committed plan.yaml files... load, so no
  migration is needed") is true and unaffected — this gap is entirely in synthetic test fixtures
  the measurement never covered.

## Recommendation for the operator/PM

Either (a) add a task (or extend T-05/T-06) whose `files:` include
`tests/unit/test-factory-claim.py`, `tests/integration/test-check-plan-routes.py`, and
`tests/integration/test-factory-decompose.py` to update the three dangling fixtures to reference a
real (or now-existing) task id, and to update `test-factory-decompose.py` case (18)'s expectation
from "exit 0, silently skip" to whatever T-06's new consumer-side surfacing makes it become; or
(b) descope T-03's verify block to the suites it can actually govern (1–4, 7, 10) and let T-05/T-06
carry 5–6, with 8–9 tracked as a new, explicitly-scoped follow-up.

## Files touched

- `.claude/skills/harness/bin/harness_yaml.py` (the rule; left in place — it is correct per
  T-01/T-02's own oracles and per the intent as written)

Nothing else touched. Nothing committed.
