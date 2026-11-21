# Red first — T-04 digest slice (common.json, validate-digest.py, dispatch-guard.py)

Tests were written first in the three owned test files and run against the pre-change
sources. Raw output: `/tmp/t04d/red-unit.txt`, `/tmp/t04d/red-dg.txt`,
`/tmp/t04d/red-vd-groups.txt` (green: `/tmp/t04d/final-*.txt`).

## 1. `python3 tests/unit/test-digest-schemas.py` — RED: exit 1, 2 failures

- `test_expertise_update_shapes` (items without `persona`, a non-canonical persona and
  `fable-advisor` were still accepted)
- `test_expertise_persona_enum_is_the_canonical_sixteen` (no `persona` in `required`)

## 2. `python3 tests/integration/test-dispatch-guard.py` — RED: exit 1, 141 of 157

16 failures, all new cases; every positive control (distill start with the marker, children
with marker and tree, ordinary `r1-eng` dispatch) already passed:

- case 32: eng-lead distill start with no mission / a conflicting mission / two missions
- case 33: for eng-lead -> backend-dev, validator-lead -> code-reviewer and validator-lead -> qa,
  each of: no mission, a conflicting mission, no feature-tree root, a foreign feature-tree root
- case 34: a distill lead's child declaring another feature

## 3. `python3 tests/integration/test-validate-digest.py` — RED: 22 failures in the new groups

Run per group (`--only run_member_expertise_{leaf,lead,supersession}_cases`) against the
pre-change validator, with the new schema already in place (so the persona refusal itself
held; its wording did not name `persona`):

- leaf: an applied item without persona is refused (new returns require it)
- leaf: an item naming another persona is refused
- leaf: a fabricated item no receipt records is refused
- leaf: an applied op the return omits is refused, never silently cleared
- leaf: an empty list on distill with applied ops is refused too
- leaf: no distill mission on the dispatch refuses a nonempty list
- leaf: a conflicting mission refuses a nonempty list
- leaf: a spoofed parent the live claim does not record is refused
- leaf: a direct file-tool change the receipt does not match is refused
- leaf: items with no receipt at all are refused, never invented
- lead: omitting a child's applied op is refused
- lead: a child's op relabelled as the lead's own is refused
- lead: a same-persona op from a run that is not its child is refused (persona equality is not provenance)
- lead: an empty list beside applied ops is refused
- durable: a file changed after application fails the durable check
- durable: feature-record.py close-run refuses that run at its digest stage
- durable: a bare JSON object with applied ops has no trusted distill context
- context: a member whose parent's registered run is not a distill run is refused
- context: a lead whose registered run is not a distill run is refused
- supersession: a lead consolidating the retired batch is refused
- withdrawal: no applied item is invented for the withdrawn batch
- orchestrator: confirming a member's op as its own list is refused

The positive controls (leaf/lead/orchestrator verified pass, re-dispatched replacement,
empty withdrawal, durable record readable and unrewritten) passed before and after.

## GREEN (after the change)

- `python3 tests/unit/test-digest-schemas.py` — exit 0, `Ran 34 tests ... OK`
- `python3 tests/integration/test-dispatch-guard.py` — exit 0, `157 of 157 cases passed`
- `python3 tests/integration/test-validate-digest.py` — exit 0, `ALL PASSED.`
  (13/13 leaf, 13/13 lead, 8/8 supersession member-expertise checks; every prior group green)

The two pre-existing #1855 distill fixtures (`QA_DISTILL`, `REVIEWER_DISTILL`) now carry
`expertise_update: []`: they pin the mission's gate fields, and their old unverified,
persona-less items are exactly what this slice refuses.
