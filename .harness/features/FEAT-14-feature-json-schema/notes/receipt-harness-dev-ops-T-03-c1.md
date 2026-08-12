# Receipt — harness-dev-ops — T-03 — c1

## Verify clause, as run verbatim (from plan.yaml T-03)

Cross-checked against T-03's `verify:` block in `plan.yaml` — identical string. Not `BLOCKED`.

```
python3 - <<'PY'
import sys, yaml
w = yaml.safe_load(open('.github/workflows/tests.yml'))
steps = w['jobs']['integration']['steps']
blob = yaml.safe_dump(steps)
bad = []
if 'jsonschema' not in blob: bad.append('integration job never installs jsonschema')
if 'validate-feature-json.py' not in blob: bad.append('integration job never runs the validator')
if '--kind unit' not in blob: bad.append('integration job never runs the unit suite, so the validator tests never run in CI')
if list(w['jobs']) != ['integration']: bad.append('jobs changed: %s' % list(w['jobs']))
raw = open('.harness/harness.json').read()
if 'feature.yaml' in raw: bad.append('harness.json still names feature.yaml')
print('\n'.join(bad) if bad else 'OK')
sys.exit(1 if bad else 0)
PY
```

**Output: `OK`. Exit: `0`.** (re-run after the final comment edit — same result.)

## Confirmations, by command output

- **Exactly one job, id `integration`, no `name:` key.**
  `python3 -c "import yaml; w=yaml.safe_load(open('.github/workflows/tests.yml')); print(list(w['jobs'])); print('name' in w['jobs']['integration'])"`
  → `['integration']` / `False`.
- **Step order** (`[s.get('name') for s in steps]`): `[None, 'Install PyYAML and jsonschema',
  'Unit suite', 'Integration suite', 'Validate feature execution state', 'Plan-route gate']` — Unit
  suite before Integration suite before Validate, Plan-route gate last and untouched.
- **`.harness/harness.json`** `feature.yaml` occurrence count: **1 before, 0 after**
  (`grep -c feature.yaml .harness/harness.json`). The diff is exactly one line, no key added:
  ```
  -    "_max_total_cycles_rationale": "...recorded in feature.yaml."
  +    "_max_total_cycles_rationale": "...recorded in feature.json."
  ```
  Still valid JSON: `python3 -c "import json; json.load(open('.harness/harness.json'))"` → no error.
- **Install step is one command, one step**: `python3 -m pip install --upgrade pyyaml jsonschema`,
  no second install step added.
- **Exec bit on the bare-invocation step**: `validate-feature-json.py` is `-rwxr-xr-x` — the
  `run: .claude/skills/harness/bin/validate-feature-json.py` step (no `python3` prefix) will execute.

## Files touched

- `.github/workflows/tests.yml` — install step now installs `jsonschema` alongside `pyyaml`; two
  new steps added to the `integration` job ("Unit suite" before the existing "Integration suite",
  "Validate feature execution state" after both); the now-false half of the standing comment above
  the integration step amended (kept the `#160` reasoning, corrected the unit-kind claim, restated
  the measured integration figure).
- `.harness/harness.json` — one string changed (`_max_total_cycles_rationale`), nothing else.
- This receipt.

## A finding that is not mine to fix — flagged, not silently absorbed

I ran the actual command the required `integration` context executes, not just my verify clause:

```
bash -c '.claude/skills/harness/bin/run-unit-tests.sh --kind integration; echo "EXIT: $?"'
```

**Exit 1.** `test-harness-yaml.py`'s `test_exactly_one_guarded_import_in_the_tree` FAILs:
`expected only harness_yaml.py, got ['feature_schema.py', 'harness_yaml.py']`. T-01's
`feature_schema.py` (per its own receipt) imports `jsonschema` inside a module-level
`try`/`except ImportError`, which this pre-existing assertion in `test-harness-yaml.py` did not
anticipate — it asserts `except ImportError` appears in exactly one file in `bin/` and names it.
This is real, reproducible on the current tree, and unrelated to my diff (`test-harness-yaml.py`
and `feature_schema.py` are both `bin/**`, outside my `files:` and outside dev-ops's lane). My own
`Unit suite` step (`--kind unit`) is green (12/12 scripts). The `Integration suite` step I wired up
is currently red for a reason inside T-01/T-05's surface, not mine.

I did not touch `test-harness-yaml.py` or `feature_schema.py` — both are prohibited to me. Reporting
this as `open_questions` below rather than fixing it or working around it.

## Open questions

- `{ id: Q1, question: "run-unit-tests.sh --kind integration currently exits 1 on the tree as
  landed: test-harness-yaml.py's test_exactly_one_guarded_import_in_the_tree fails because
  feature_schema.py (T-01) now also contains an except ImportError block, and that test asserts
  the pattern appears in exactly one bin/ file (harness_yaml.py). This means the required
  integration CI context I just wired up will be red on this PR until that assertion is updated
  or feature_schema.py's guard is reshaped to match it. Neither file is in my T-03 files: list or
  my lane. Who owns updating test-harness-yaml.py's assertion — backend-dev under T-01/T-05, or a
  new task?", blocking: true }`
- `{ id: Q2, question: "T-03's intent and plan.yaml both say 'test-check-plan-routes.py case 25
  reads this file and asserts that step is present and unneutered.' I grepped
  .claude/skills/harness/bin/*.py and the whole repo for case_25/case 25 and found no such case —
  test-check-plan-routes.py's functions are case_13 through case_24 (with lettered sub-cases) and
  none references .github/workflows/tests.yml or the Plan-route gate step. I did not touch that
  step regardless (compliance did not depend on the claim being true), but the claim itself
  appears false as stated; flagging rather than silently correcting the record.", blocking: false }`

## `.harness/features/FEAT-14-feature-json-schema/feature.yaml` and `STATE.md`

Show as modified in `git status` (orchestrator dispatch bookkeeping — `status`, `branch` etc., and
whatever T-01's run touched). I made no edit to either; not in my `files:` list.
