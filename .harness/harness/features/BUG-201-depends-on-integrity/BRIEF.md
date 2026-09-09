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
- REQ-05: A consumer that reads a plan carrying a dangling `depends_on` surfaces the specific
  validation error — the offending task id and the missing id — rather than silently degrading it to
  "no plan" or an empty mapping. The three sites that degrade it today, confirmed at source at
  `af859ee8`: `factory_claim.py` `_plan` (`:106-109`, to `plan = None`, which `_blocker_reason_text`
  at `:193-196` then renders as "the feature directory or its plan.yaml is missing or unparseable"),
  `gh-sync.py` `_projected_for` (`:1153-1156`, to `{}`) and `gh-sync.py` `_status_plan_doc`
  (`:1263-1266`, to `None`, after which the ready guard tells the operator that approval is not
  approved). This is the operator's ruling of 2026-09-07 on Q-A
  (`notes/answers-plan-c0.md`), in scope for BUG-201.

## Constraints

- **The operator's out-of-scope ruling, from the grilling of 2026-09-06** (`.harness/notes/grilling-depends-on-integrity-2026-09-06.md`,
  Settled + Out of scope): only a reference to a task id absent from the same plan is validated.
  Self-dependencies, cycles and task ordering are NOT validated, and broader DAG policy is not opened.
  This is the user's selection, not an implementation convenience.
- **ONE DECLARED WIDENING, put to the operator here rather than left in the tasks**: a
  `depends_on` that is not a list at all (a bare string) is also rejected, because the rule would
  otherwise iterate the string's characters and report phantom missing ids. Measured in this
  worktree on 2026-09-07: zero of the 68 live `plan.yaml` files carries a non-list `depends_on`, so
  the exposure is nil. It is recorded in `plan.yaml` T-01 case 5 and T-03's behaviour list.
- **DEC-182 / FEAT-41 SUPPLY the mechanism**: `plan.yaml` is real YAML and `validate_plan_doc` is the single
  home the reader (`load_plan`) and the writer (`plan-merge.py`) share, extracted so the two cannot
  disagree (FEAT-41 HIGH-1). Anything landing there is enforced on both routes with no new wiring.
- **DEC-174 BOUNDS who executes**: the enforcement layer is main-session-direct. `harness_yaml.py` is a
  library a gate imports, which DEC-174 states "is not itself a gate"; the lane reading is recorded as
  D-03 in `plan.yaml`.
- **DEC-217 / DEC-213 SUPPLY the test kind**: this is `change_type: bugfix` touching runtime code, so `unit`
  is obliged, and the directory `tests/unit/` is what selects that kind.
- **DEC-138 BOUNDS the consumer posture**: "GitHub is a mirror, never a gate". It SUPPLIES rather
  than blocks — `gh-sync.py:1160-1168` already refuses a vocabulary miss at exit 2 with one
  actionable line — and the per-site reconciliation with REQ-05 is recorded as D-05 in `plan.yaml`.
- Base sha `af859ee8`, branch `feat/BUG-201-depends-on-integrity`. The measurements this brief rests on
  were taken in that worktree at that sha.
- `## Approval` stays `pending`; only the main session signs it.

## Success Criteria

- SC-01: A plan document in which task `T-02` carries `depends_on: [T-99]`, with no `T-99` among its tasks,
  is refused by `harness_yaml.validate_plan_doc` with a `PlanSchemaError` whose message contains both
  `T-02` and `T-99`.
  verify: automated        evidence: unit
- SC-02: The dangling edge is refused on the WRITE route, with observations discriminating enough
  that a deny-everything write route fails them: `plan-merge.py apply` of a proposal adding
  `depends_on: [T-99]` onto a base that `load_plan` accepts exits with status EXACTLY 5, its
  combined output contains `ILLEGAL PLAN` and `T-99`, and the target file's sha256 is unchanged;
  AND the paired allow — the same proposal with `depends_on: [T-01]` — exits 0 and the reloaded
  plan carries the new task. Exit 9 (an unresolved `--file`) does not satisfy this criterion.
  verify: automated        evidence: integration
- SC-03: The corpus invariant holds: every `plan.yaml` found under `.harness/harness/features/`
  loads through `harness_yaml.load_plan` with the verdict it has today — zero failures, zero
  dangling references — and the walk finds AT LEAST the floor below. The count is a FLOOR with its
  provenance, never an equality: 67 committed `plan.yaml` files at `af859ee8` in the main checkout
  (`git ls-tree -r --name-only HEAD`), and 68 in this feature's worktree, which includes this
  feature's own `plan.yaml`. A walk that matches fewer than 67 fails; a corpus that has grown does
  not. No migration or grandfathering is needed, because zero of them is dangling today.
  verify: automated        evidence: unit
- SC-04: The rule has exactly one implementation, inside `validate_plan_doc`'s call tree. The
  reviewer greps the reviewed tree for `_validate_plan_depends_on` — the helper T-03 creates — and
  finds exactly one definition (`def _validate_plan_depends_on`) and exactly one call site, both
  inside `.claude/skills/harness/bin/harness_yaml.py`, and no further match anywhere else in the
  tree. No second implementation of the rule — no other code comparing a `depends_on` entry against
  the plan's own task ids, under any name — exists in `plan-merge.py`, in `check-plan-routes.py`, or
  in any other consumer.
  verify: inspection
- SC-05: The pre-rule run of the new unit file failed FOR THE RIGHT REASON, and the record shows
  which cases failed. In the recorded run against `harness_yaml.py` as of `af859ee8`: the file
  imports and reaches its cases (no `ImportError`, no fixture error, no collection error), the
  paired-allow cases PASS in that same run (T-01 cases 2 and 4, and case 6's two accept halves),
  and the FAIL lines it emits are exactly T-01 cases 1, 3, 5 and case
  6c. The same command passes in full after T-03 lands. A run that failed to import, or whose
  failure is a fixture error, does not satisfy this criterion.
  verify: inspection
- SC-06: A correct plan's `unit`-kind consumers behave as they do today, proven by their own
  suites and not by assertion: `tests/unit/test-factory-claim.py`,
  `tests/unit/test-factory-claim-mutation.py` and `tests/unit/test-harness-yaml-corpus.py` each
  pass after the change, and each is named in the `verify:` of every task that lands a production
  edit (T-03 and T-06).
  verify: automated        evidence: unit
- SC-07: A correct plan's `integration`-kind consumers behave as they do today, on the same terms:
  `tests/integration/test-gh-sync.py`, `tests/integration/test-check-plan-routes.py`,
  `tests/integration/test-harness-yaml.py`, `tests/integration/test-plan-merge.py`,
  `tests/integration/test-factory-decompose.py` and `tests/integration/test-check-state.py` each
  pass after the change, and each is named in the `verify:` of T-03 and T-06.
  The last two suites bind the two consumers the earlier list omitted, and the enumeration is
  stated so a reader can CHECK it rather than trust it. Every file that reads a plan through the
  shared validator, at `af859ee8` in `.claude/skills/harness/bin/`: `check-plan-routes.py:366`,
  `check-state.sh:140`, `factory_claim.py:107`, `factory_decompose.py:471` and `gh-sync.py:357`,
  `:1154`, `:1264` call `harness_yaml.load_plan`; `plan-merge.py` reaches the same rule through
  `validate_plan_doc` directly. That is six files, and SC-06 and SC-07 together name a suite for
  each of the six. Both added suites live under `tests/integration/`, which is the `integration`
  kind's `detect` glob, so SC-06's `unit` list is unchanged.
  verify: automated        evidence: integration
- SC-08: `factory_claim` reports the real cause. Over a fixture plan whose task `T-02` carries
  `depends_on: [T-99]`, the blocker reason a caller receives contains BOTH `T-02` and `T-99` and
  does NOT contain "no plan could be read"; the gate returns rather than raising, and a second
  legal candidate in the same poll is still evaluated. PAIRED CASE: over the same fixture with
  `depends_on: [T-01]`, the candidate's blocker verdict is exactly the one the suite's existing
  clear-candidate case asserts. A message reporting only that an error occurred, or omitting
  either id, fails this criterion.
  verify: automated        evidence: unit
- SC-09: `gh-sync` reports the real cause at both of its sites, with the postures D-05 records.
  Over the same dangling fixture: `gh-sync start-task <fixture> T-NN`, with a board configured —
  the invocation that reaches `_projected_for` — exits EXACTLY 2 with one stderr line containing
  both `T-02` and `T-99` and no `Traceback` anywhere in its output; and `gh-sync status <fixture>
  Ready` emits a stderr line containing both `T-02` and `T-99` while its exit status and existing
  refusal line are UNCHANGED from before the change — the diagnosis is additive, never a new gate.
  `status Ready` does NOT satisfy the first clause: its approval guard refuses at exit 2 on its own
  (`gh-sync.py:1306-1307`), so a build that repaired only `_status_plan_doc` would green it while
  `_projected_for` still returned `{}`; `start-task` discriminates, because with `_projected_for`
  unchanged that command prints "no station follows from the plan" and exits 0. PAIRED CASES: over
  the legal fixture both invocations behave exactly as the suite's existing cases for them assert.
  verify: automated        evidence: integration

## Verification gaps

- None on this surface. Both kinds this brief names are `active` with a real `cmd` (`harness.json`
  `test_kinds.unit`, `test_kinds.integration`), and their `detect` globs `tests/unit/**` and
  `tests/integration/**` match the files this feature touches. No SC here rests on a kind whose `cmd` is
  null.

## Approval

status: approved
approved-by: mruangutai
date: 2026-09-07
