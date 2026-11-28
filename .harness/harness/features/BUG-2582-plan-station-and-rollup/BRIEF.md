# BRIEF — BUG-2582-plan-station-and-rollup Plan phase: station-only dead end and reader-FAIL roll-up

## Problem

Two plan-phase defects cost whole runs on 2026-11-27 (issue #2582). First, check-state INV-34
tells the operator to give a plan-less feature a station-only `plan.yaml` (`station_only: true`,
`tasks: []`); once it exists, `plan-merge.py apply` of the real plan exits 5, because the loader
refuses the marker beside tasks and no verb removes it. BUG-2565 run `2026-11-27-01-plan-product`
returned BLOCKED for that alone. Second, in the plan team the readers return FAIL to carry their
findings, pm applies those findings in the same run, and the worst-member roll-up (DEC-123) still
forces the team verdict to FAIL. The orchestrator cannot tell "plan ready, findings applied" from
"plan failed" (BUG-2566 run `2026-11-27-01-plan-product`, BUG-2565 run `2026-11-27-02-plan-product`).

## Done when — by perspective

**operator** — When check-state tells me to create a station-only record, doing so no longer traps
the feature. The first plan run can start on that record, its `apply` turns the record into the
real plan, pending my signature, and the INV-34 message says so. The protections the marker exists
for still hold: a task-bearing plan can never wear it, and an emptied plan without it still fails
to load.

**orchestrator** — A plan run whose reader findings are all recorded `resolved` in `plan.yaml` can
come back PASS, so I can route "plan ready" apart from "plan failed". pm's own apply step records
what it resolved, so an ordinary plan run gets there without a special instruction. A reader
finding still open, or a resolution only the lead's digest claims, still forces FAIL. Every other
team rolls up exactly as before.

**code maintainer** — The decision record and the docs agree with the code. DEC-123, DEC-254 and
DEC-228 state what this feature changes, and no SPEC, skill or team text still claims a rule the
validator, `apply` or the plan team no longer applies.

## Success criteria

- SC-01 (operator): `plan_merge.union.apply_merge`, invoked as `apply` and as `add-tasks`, with a
  proposal carrying at least one task onto a station-only record (`schema: plan/1`, `feature:`,
  `status: plan`, `station_only: true`, `tasks: []`, no `approval:`, no `drafted_at`) returns
  without a refusal. The result reloads through `harness_yaml.validate_plan_doc` with no
  `station_only` key, the proposal's tasks, `approval: {status: pending}`, a writer-stamped
  `drafted_at`, and the base `status:` unchanged. The `apply` receipt prints a `CONVERTED` line and
  no `APPROVAL-RESET:` line. qa first shows this exact BUG-2565 repro failing with exit code 5
  against the base `union.py`.
  verify: automated        evidence: unit
- SC-02 (operator): The station-only safety pair is unchanged. A proposal that itself carries
  `station_only: true` beside tasks is still refused with exit 5 and nothing written. A
  station-only record at a finished station (`done`, `abandoned`, `rejected`) is not converted and
  is refused with exit 5 as at base. A proposal with `tasks: []` leaves the record station-only.
  A document with `tasks: []` and no marker still fails `validate_plan_doc`. Each case is its own
  assertion, and `harness_yaml.py` is byte-identical between the base and the review pin.
  verify: automated        evidence: unit
- SC-03 (operator): check-state INV-34's message for a feature with no `plan.yaml` still prescribes
  the station-only record, written through `plan-merge.py apply`. It also gains a line saying that
  a later `plan-merge.py apply` (or `add-tasks`) carrying tasks converts the record into the plan:
  it drops `station_only`, and seeds a pending approval and stamps `drafted_at` where either is
  absent. qa first shows, at the base check-state, the existing remedy present and only that line
  absent.
  verify: automated        evidence: unit
- SC-04 (operator): Signing a converted plan needs no special case. A reviewer cites, on the
  reviewed diff, that conversion leaves `plan_merge/approval.py` `cmd_sign_approval` and
  `check_state/plan.py` INV-32 untouched. The seeded `approval: {status: pending}` makes
  `check_state/plan.py` `_inv3_plan_yaml` report pending, not a missing block. The stamped
  `drafted_at` makes `plan_merge/check.py` `_eligibility` grade `decisions_affected:` on the
  converted draft.
  verify: inspection
- SC-05 (orchestrator): The plan-team carve-out applies only when all of these hold: a
  `harness-product-lead` digest with `DIGEST.team: plan`, the feature's `feature.json` `mission:
  plan`, exactly one member entry per reader step, and a reader member (`step` `scope`,
  `should-not-exist` or `design`) at `verdict: FAIL`. Under those conditions `validate-digest.py`
  accepts a lead `VERDICT: PASS` for that exact member when every team-digest finding attributed to
  it matches exactly one row of the feature's `plan.yaml` `panel.findings` by recomputed PF id,
  that row carries the same reader string and `disposition: resolved` exactly, and every other
  on-disk row attributed to that reader is `disposition: resolved` too. qa first shows this case
  refused with the worst-member error at the base validator.
  verify: automated        evidence: unit
- SC-06 (orchestrator): The carve-out fails closed. The lead `VERDICT: PASS` is still refused with
  the worst-member error when any one of these holds, and each case is its own assertion:
  - one of that reader's findings is `open` on disk, including an earlier finding the team digest
    no longer carries;
  - one of its team-digest findings is absent from `plan.yaml`;
  - the row carrying its PF id is attributed to another member, or its disposition is any spelling
    other than `resolved`;
  - a `panel.findings` row is malformed;
  - it has no attributed findings;
  - some finding matches no member, or more than one;
  - two member entries share a reader step, one of them at a stronger verdict;
  - `plan.yaml` is missing or does not load;
  - `mission` is not `plan`;
  - `team` is not `plan`;
  - the FAIL member is `draft`, `apply` or `goalcheck`, each its own case;
  - the reader's verdict is ESCALATE or BLOCKED, each its own case, which still outranks PASS.
  The refusal names why the carve-out did not apply.
  verify: automated        evidence: unit
- SC-07 (orchestrator): Every other team keeps DEC-123's roll-up. Two leads report `VERDICT: PASS`
  over a member at `verdict: FAIL` whose findings are all resolved on disk in a plan-mission
  feature: a `harness-eng-lead` digest with `team: build`, and a `harness-validator-lead` digest.
  Both are refused exactly as at base.
  verify: automated        evidence: unit
- SC-08 (code maintainer): At the review pin (`git show <review_sha>:<path>`):
  - DEC-123 in `.harness/harness/docs/DECISIONS.md` no longer carries its amended roll-up clause,
    qualifies its opening worst-wins statement, and states the plan-team reader carve-out.
  - DEC-254 no longer carries its "Ordinary edits neither stamp" clause and states that converting
    a station-only record is plan creation, which stamps `drafted_at`.
  - DEC-228's apply sequence names `set-panel` between `record-panel` and `check`.
  - `DECISIONS-INDEX.md` matches `gen-decisions-index.py --stdout`, and its DEC-123 row's ruling
    names the carve-out.
  - The roll-up paragraph in `.harness/harness/docs/SPEC.md` and the roll-up row in
    `.claude/skills/harness-team/SKILL.md` state the carve-out with its plan-mission, attribution
    and fail-closed conditions, not as "any resolved panel".
  verify: inspection
- SC-09 (code maintainer): The existing suites over the touched surfaces pass unchanged at the
  review pin, with `HARNESS_AGENT_TYPE` unset: `tests/integration/test-plan-merge.py`,
  `tests/integration/test-harness-yaml.py`, `tests/integration/test-check-state-plans.py` and
  `tests/integration/test-validate-digest.py`.
  verify: automated        evidence: integration
- SC-10 (operator): A feature whose station-only record was written through `plan-merge.py apply`,
  as INV-34 prescribes, can run its first plan. Through the real dispatch guard in a private-bin
  fixture, a `harness-product-lead` `HARNESS-MISSION: plan` start on that record is admitted; a
  following `plan-merge.py apply` of a one-task proposal exits 0 and leaves a plan with that task,
  no `station_only` and `approval: {status: pending}`. A hand-written record with no `approval:`
  is still refused before any claim. qa first shows the apply step exiting 5 with the marker
  diagnostic against the base `union.py`.
  verify: automated        evidence: integration
- SC-11 (orchestrator): The shipped `teams/plan.yaml` `apply` prompt orders `record-panel`, then
  `set-panel` marking `resolved` only the findings whose remedy pm applied in that step
  (`resolved_by` naming the carrying task where one exists; `scope: mission` and unremedied
  findings stay `open`), then `check`. A panel written by the real `plan-merge.py record-panel`
  from a fan-in digest, then resolved by `plan-merge.py set-panel`, makes `validate-digest.py`
  accept the `harness-product-lead` `VERDICT: PASS` over that reader's FAIL. qa first shows the
  base `apply` prompt carrying no `set-panel`, and the chain refused at the base validator.
  verify: automated        evidence: unit

## Verification gaps

- The feature touches Python under `.claude/skills/harness/bin/`, new files under `tests/unit/`,
  one case group in `tests/integration/test-lead-start-return.py`, the plan team's prompt in
  `.claude/skills/harness/teams/plan.yaml`, and markdown docs; `unit` and `integration` are active
  runners. `component` and `ui` (unresolved, `cmd: null`) detect only `.tsx`/`.ts`/e2e paths, none
  touched. SC-04 and SC-08 are inspection by choice, not by a missing runner.
- Not proven: that pm, dispatched with the new `apply` prompt, actually resolves exactly the
  findings it applied. That is agent conduct, which the `eval` kind would cover and DEC-187
  excludes. SC-11 carries the prompt's text and order and the real record-panel → set-panel →
  validate-digest chain instead; the first plan run after ship is the behavioural evidence.

## Constraints

- BLOCKS — DEC-174: plan-merge, the plan loader, check-state and validate-digest are enforcement
  surfaces; every task is `main-session-direct` and none executes through the gate it changes.
- BLOCKS — the loader's `_validate_station_only` pair (FEAT-41 MF-3 and HIGH-1, recorded in
  `harness_yaml.py`) stays as written in both directions; conversion happens in the writer, never
  by relaxing the reader.
- BLOCKS — DEC-123's worst-member rule for every team and mission other than the plan team's
  three reader slots; BLOCKED > ESCALATE > FAIL > PASS is unchanged. Reporting worse stays legal.
- BLOCKS — DEC-229: `sign-approval` stays the only writer of `approved`; conversion seeds only
  `status: pending`, the same mapping `_seed_new_plan` writes.
- SUPPLIES — DEC-254: `drafted_at` is writer-stamped creation provenance; this feature amends it so
  that conversion counts as creation.
- SUPPLIES — DEC-191: the station lives only in `plan.yaml`; conversion keeps the base `status:`.
- SUPPLIES — `panel_findings.finding_id` and `record-panel` (`plan_merge/panel.py`) give each
  finding a content id; `set-panel` is the only route that records `disposition: resolved`.
- Disclosure, not a decision: `disposition: resolved` is written by pm's own `set-panel` after
  pm's own apply, so the carve-out trusts pm's on-disk record rather than a re-read; this is the
  operator's settled ruling, and `sign-approval` and INV-32 already treat `resolved` the same way.
  A lead that omits a reader's finding from both its fan-in and its team digest is not caught.
  Those findings never reach disk, and the reader's own note is the only record.
- Disclosed choice (lead ruling, plan c1, overridable at signature): the plan team's `apply` step
  changes (T-05, D-03, DEC-228 amended) because Destination 2 has no trigger without it — the
  shipped prompt never resolved a finding. Strike T-05 at signature to exclude it; SC-11 and the
  DEC-228 amend row go with it.
- Disclosed choice (lead ruling, plan c1, overridable at signature): no `dispatch-guard.py` change
  (D-04). A station-only record written through `apply`, the route INV-34 prescribes, already
  carries `approval: {status: pending}` and starts the product plan lead (measured,
  `notes/research-plan-c1-apply.md`); a hand-written record without `approval:` stays refused for
  every plan-panel start, as at base. The validator lead and scope reader also start on an
  apply-written record; that is base behaviour this feature does not change.
- Disclosed choice (lead ruling, plan c1): the scope reader's binding and red-first findings are
  applied to T-01, T-02 and T-04 as stated in SC-03, SC-05, SC-06 and SC-10.

## Out of scope

- Changing the plan readers' contract — FAIL to carry findings stays (grilling).
- INV-34 firing time — it still fires when a feature has no `plan.yaml` (grilling).
- Any other roll-up rule — BLOCKED > ESCALATE > FAIL > PASS stays (grilling).
- #2622 (the practicality rule) and #2627 (worktree removal after squash-merge) — separate issues
  (grilling).

## Approval

status: approved
approved-by: operator
date: 2026-11-27
