# Handoff - BUG-1128, build -> validate - written at 58742037, seq-2

## Next

Dispatch `harness-validator-lead` to run the reviewer panel against `review_sha` `58742037`.
The diff is two files, +510/-0: `plan-merge.py` (+206) and `test-plan-merge.py` (+304).

- `.claude/skills/harness/bin/plan-merge.py:916-1091` - the `amend` block: `_item_range`,
  `_field_block`, `_render_field`, `cmd_amend`
- `.claude/skills/harness/bin/plan-merge.py:1112` - `_register_amend`, deliberately not a
  `VERBS` row
- `.claude/skills/harness/bin/test-plan-merge.py` - ten `case_amend_*` cases
- `issue://1128` - the defect and its two probes
- `.harness/harness/features/BUG-1128-plan-amend-verb/notes/` - panel notes go here

## Trust

- claim - 218 PASS / 0 FAIL on `test-plan-merge.py`, full `run-unit-tests.sh` exit 0 with zero
  FAIL lines - verified-at 58742037 - source: this build ran both.
- claim - red first - verified-at 58742037 - source: before the verb existed the suite was 204
  PASS / 9 failing new assertions, and every pre-existing case passed throughout.
- claim - it works on the real motivating file - verified-at 58742037 - source: `--show` against
  FEAT-46's actual `plan.yaml` located and hashed `D-05.because`, `D-14.because` and
  `T-23.verify`; the `T-23` block starts at `verify: |` and captures zero sibling keys; an
  absent id refuses by name.
- claim - the gate's one violation is not this feature's - verified-at 58742037 - source:
  `check-state.sh` reports exactly one, `INV-26` on `BUG-1081-code-grade-enforcement`, another
  session's feature.

## Dead ends

- A hand-written plain-vs-block quoting rule - source: written, then deleted. It handled `: `
  and leading indicators and would still have written `title: yes`, which reloads as the
  boolean `True` with no error anywhere. `_field_lines`'s docstring already said why: PyYAML
  knows the whole set and a local rule re-derives part of it. There is now ONE renderer.
- Trusting the pre-lock hash check alone - source: it is kept for a fast, precise refusal, but
  the check that is load-bearing is the one inside `transform`, under the lock.

## Working set

- `.claude/skills/harness/bin/plan-merge.py`
- `.claude/skills/harness/bin/test-plan-merge.py`
- `.harness/harness/features/BUG-1128-plan-amend-verb/feature.json`

## Not done here, and deliberately

The eight staged amendment blocks in FEAT-46 are NOT applied. This feature ships the route;
applying them is FEAT-46's next cycle, after this merges. Applying them from here would put two
features' work on one branch.
