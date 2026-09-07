# BRIEF — BUG-201 depends_on referential integrity

## Problem

Nothing checks that a `depends_on` entry names a task that exists in the same plan. The shared plan
validator checks task shape, unique ids, `files:` type and `execution_mode` (`.claude/skills/harness/bin/harness_yaml.py`
`_validate_plan_tasks`, observed at `af859ee8`) and never looks at the dependency edges at all; the plan
writer's pre-write check delegates to the same function (`plan-merge.py` `_schema_error`), so it is blind
in the same way. A typo, or a task renamed during a plan revision, therefore leaves a dangling edge that
survives the operator's signature and reaches decomposition, where FEAT-10 turns each entry into a GitHub
`blocked_by` edge pointing at nothing and `factory_claim.py` reads the unresolvable entry as a blocker — a
signed plan that can never be claimed, diagnosed at claim time by whoever is unlucky rather than at the
moment the bad id was typed (issue #201).

## Goal

A plan cannot carry a dependency on a task that is not in it. The author finds out while writing the plan
— on the write route, before a signature exists — and any consumer reading such a plan refuses it loudly
instead of acting on an edge that resolves to nothing. Plans that are correct today behave exactly as they
do today.

## Requirements

- REQ-01: A plan in which a task's `depends_on` names a task id absent from that same plan is rejected
  rather than loaded.
- REQ-02: The rejection names both the task carrying the bad entry and the id that is missing, so the
  author can repair it from the message alone.
- REQ-03: A dangling entry cannot be introduced into a plan through the plan writer, so it never reaches a
  signature or a consumer.
- REQ-04: Every plan already on disk keeps the verdict it has today, and every consumer of a correct plan
  behaves as it does today.

## Constraints

- **The operator's out-of-scope ruling, from the grilling of 2026-09-06** (`.harness/notes/grilling-depends-on-integrity-2026-09-06.md`,
  Settled + Out of scope): only a reference to a task id absent from the same plan is validated.
  Self-dependencies, cycles and task ordering are NOT validated, and broader DAG policy is not opened.
  This is the user's selection, not an implementation convenience.
- **DEC-182 / FEAT-41 SUPPLY the mechanism**: `plan.yaml` is real YAML and `validate_plan_doc` is the single
  home the reader (`load_plan`) and the writer (`plan-merge.py`) share, extracted so the two cannot
  disagree (FEAT-41 HIGH-1). Anything landing there is enforced on both routes with no new wiring.
- **DEC-174 BOUNDS who executes**: the enforcement layer is main-session-direct. `harness_yaml.py` is a
  library a gate imports, which DEC-174 states "is not itself a gate"; the lane reading is recorded as
  D-03 in `plan.yaml`.
- **DEC-217 / DEC-213 SUPPLY the test kind**: this is `change_type: bugfix` touching runtime code, so `unit`
  is obliged, and the directory `tests/unit/` is what selects that kind.
- Base sha `af859ee8`, branch `feat/BUG-201-depends-on-integrity`. The measurements this brief rests on
  were taken in that worktree at that sha.
- `## Approval` stays `pending`; only the main session signs it.

## Success Criteria

- SC-01: A plan document in which task `T-02` carries `depends_on: [T-99]`, with no `T-99` among its tasks,
  is refused by `harness_yaml.validate_plan_doc` with a `PlanSchemaError` whose message contains both
  `T-02` and `T-99`.
  verify: automated        evidence: unit
- SC-02: The same document is refused on the WRITE route — `plan-merge.py apply` against a legal base exits
  non-zero and leaves the target file byte-identical — so a dangling edge cannot be written into a plan and
  then signed.
  verify: automated        evidence: integration
- SC-03: Every `plan.yaml` under `.harness/harness/features/` loads through `harness_yaml.load_plan` with the
  same verdict as before the change. Measured at `af859ee8` in this worktree: 67 files, 67 load, 0 fail,
  0 dangling references — so the required post-change result is 67 load, 0 fail, and no migration or
  grandfathering is needed.
  verify: automated        evidence: unit
- SC-04: The rule has exactly one implementation, inside `validate_plan_doc`'s call tree. No second copy
  exists beside `check-plan-routes.py`, in `plan-merge.py`, or in any other consumer — a reviewer greps the
  reviewed tree for the check and finds it once.
  verify: inspection
- SC-05: The unit case asserting SC-01 was demonstrably RED before the rule existed: the recorded run of
  the new test file against `harness_yaml.py` as of `af859ee8` fails, and the same command passes after the
  rule lands. The failing run is cited in the build record.
  verify: inspection

## Verification gaps

- None on this surface. Both kinds this brief names are `active` with a real `cmd` (`harness.json`
  `test_kinds.unit`, `test_kinds.integration`), and their `detect` globs `tests/unit/**` and
  `tests/integration/**` match the files this feature touches. No SC here rests on a kind whose `cmd` is
  null.

## Approval

status: pending
approved-by:
date:
