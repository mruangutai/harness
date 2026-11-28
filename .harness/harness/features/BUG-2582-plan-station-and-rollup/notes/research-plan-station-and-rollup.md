# Research — BUG-2582 plan station and roll-up (2026-11-27, base e69608659e313e9c176560098c5d94f87482fe1f)

BLUF: both defects are confined to one function each (`plan_merge/union.py` `apply_merge`,
`validate-digest.py` `_lead_rollup_errors`). Defect 1 needs more than dropping the marker: a
converted record has no `approval:` and no `drafted_at`, so it must be seeded like a new plan or
INV-3 and the DEC-254 era check misread it. Defect 2's relief is reachable today only when the
lead's fan-in tells pm to run `set-panel`; the shipped team file never requires it (OQ-1).

## Defect 1 — station-only record cannot become a plan

- Refusal path: `apply_merge` merges `station_only` as a plain key (`_merge_plain_key`: base value
  kept), unions the proposal's tasks, then `_verify_schema_preserved` sees a legal base and an
  illegal result and raises `MergeRefusal(5)` with `_refuse_a_minted_marker`'s text
  (`harness_yaml.py` `_refuse_a_minted_marker`). A proposal carrying `station_only: false` hits
  the exit-7 CONFLICT in `_merge_plain_key`. Matches the grilling's measured exit 5.
- `add-tasks` shares `apply_merge` (`union.py` module docstring; `verb` parameter), so the same fix
  covers both verbs.
- The INV-34 record shape (`check_state/plan.py` `inv_34` text) carries no `approval:` and no
  `drafted_at`. `apply_merge` never writes approval on an existing base (`_merge_key` approval
  branch) and only `_seed_new_plan` stamps `drafted_at`. Consequences of a marker-drop alone:
  - INV-3: `_inv3_plan_yaml` reports "has no `approval:` block" (bad) once the marker is gone.
  - DEC-254 era: `plan_merge/check.py` `_eligibility` skips a plan with no `drafted_at`, so the
    converted plan would escape the `decisions_affected:` requirement. That is a silent exemption.
  - sign-approval: `approval.py` `_signed_approval_bytes` inserts an approval block when absent,
    so signing works either way; with a seeded pending block it takes the normal update path.
  - `_maybe_reset_approval` (`stations.py` `_approval_reset_context`) returns None for a base with
    no approval mapping, so conversion prints no `APPROVAL-RESET:` receipt and needs no gh-sync.
  - INV-32 grades approved plans only (`check_state/plan.py` INV-32 branch), so a converted plan is
    graded exactly like any plan once signed; no special case.
  - INV-3 and INV-5 exemptions are keyed on `station_only is True` (`_inv3_plan_yaml`,
    `_inv5_plan_yaml`); dropping the marker re-enables both — the safe direction.
- Finished stations: `reject-path.md` writes a station-only record at `rejected`; INV-44 requires a
  rejected record to have exactly one shape. Converting a finished-station record would make that
  record illegal elsewhere, so conversion is limited to non-finished stations
  (`factory_config.FINISHED_STATIONS`, already used by `check.py` `_is_draft`).
- No current main-checkout plan carries `station_only: true` (grep of `.harness/*/features/*/plan.yaml`),
  so no corpus record changes shape.
- No DEC governs the station-only marker itself (DECISIONS.md has no "station-only"/"station_only");
  the rules live in FEAT-41 T-19/MF-3/HIGH-1 comments in `harness_yaml.py` and `check_state/plan.py`.
  DEC-254 governs `drafted_at` ("Ordinary edits neither stamp an undated legacy plan nor change an
  existing stamp."), so stamping at conversion amends DEC-254.

## Defect 2 — reader FAIL forces team FAIL

- Roll-up: `validate-digest.py` `_family_errors` -> `_lead_rollup_errors(seen, verdict)` ->
  `_member_rank_errors` / `_worst_member` / `_member_verdict`. No feature context reaches it today;
  `_family_errors` already receives `feature_dir`, and `_resolve_feature_dir(artifact, feature_dir)`
  derives it from the lead's `artifact` (`runs/<run>/digest.md`) in CLI mode, which is how
  `feature-record.py close-run` invokes the validator (`_close_run_stages`, no feature arg).
- Plan-mission identification: `DIGEST.team` (lead schema, text) plus feature.json `mission`
  (written with its judgement by `feature-record.py` `cmd_set_mission`). Both are needed: `team` is
  the lead's word; `mission` is on disk.
- Member entries carry `step` and `persona` (common.json `member_ran`/`member_skipped`). The reader
  steps are the panel slots `scope`, `should-not-exist`, `design` (`teams/plan.yaml` step ids;
  `panel_findings.PANEL_READERS` minus `goalcheck`).
- `findings[].reader` is NOT stable. Observed in the main corpus:
  - BUG-2566 run 01 team digest and plan.yaml: `code-reviewer`, `ui-reviewer`, `should-not-exist`.
  - BUG-2565 runs 02-04 and plan.yaml: `harness-code-reviewer`, `should-not-exist`.
  `panel_findings.py` and the plan template say it is the reporting persona; the fable prompt in
  `teams/plan.yaml` tells that reader to write `should-not-exist`. So a tie must accept the slot
  name or the persona in any spelling `digest_schema.canonical_persona` resolves, and must fail
  closed on a finding that matches no member or more than one.
- record-panel ids: `plan_merge/panel.py` `_digest_finding` computes
  `panel_findings.finding_id(reader, summary)` and always writes `disposition: open`; a finding
  already on disk keeps its own disposition. The team digest carries the same reader/summary
  (`teams/plan.yaml` tail), so recomputing the id from the team digest binds this run's findings to
  disk; a lead that spells them differently produces an id not found -> relief denied.

## Reachability of the relief (OQ-1)

- Nothing in `teams/plan.yaml` `apply` prompt runs `set-panel`; findings land `open`.
- Observed: BUG-2566 run 01 left both highs open and the team returned FAIL (its digest headline).
  BUG-2566 runs 02 and 03 and BUG-2565 cycle 4 resolved findings only because the lead's fan-in
  file instructed pm to run `set-panel` after `record-panel` (`runs/2026-11-27-03-plan-product/panel-c3.md`,
  `notes/research-apply-c2.md`, `notes/research-answers-c4-apply.md`).
- So the relief fires only on runs whose lead adds that instruction. Making it routine needs one
  sentence in the plan team's `apply` prompt (and DEC-228's description of apply), which is outside
  the operator's listed scope. Raised as blocking OQ-1 with a recommendation; not planned.

## Verify timings measured at base (HARNESS_AGENT_TYPE unset)

- tests/integration/test-plan-merge.py 13 s; test-check-state-plans.py 11 s; test-harness-yaml.py
  2 s; test-validate-digest.py 34 s. Split across T-01 and T-02 verifies to stay under 60 s each.

## Hook-mode feature binding (why deriving the feature from the lead's artifact is safe)

- In hook mode `validate()` gets `feature_dir` from `_hook_feature_dir` (None on mismatch), and the
  carve-out falls back to `_resolve_feature_dir(artifact, None)`. A lead artifact naming another
  feature is refused anyway: `check_artifact_file` appends only through
  `digest_destination.authorized_digest`, which [INFERENCE from the call site and its
  AuthorizationError refusal; not traced into digest_destination.py] binds the path to the
  registered run. The PF-id recomputation from the team digest is a second bind.

## Draft receipts (2026-11-28, HARNESS_AGENT_TYPE unset, control-plane plan-merge.py)

- `apply --proposal` (new plan): `APPLIED .../plan.yaml`, exit 0; no `APPROVAL-RESET:` line, so
  no gh-sync call. The check-state echo listed the expected pre-signature violations (BRIEF not
  approved; INV-37 no Build-entry receipt).
- `check --root <worktree>`: 3 tasks, 9 anchors resolved, 0 failures, exit 0; no OVERLAP lines.
