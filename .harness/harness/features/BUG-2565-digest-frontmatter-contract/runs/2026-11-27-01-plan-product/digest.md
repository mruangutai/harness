# BUG-2565 plan run 2026-11-27-01-plan-product — BLOCKED at draft

**BLUF:** pm wrote the BRIEF (11 SCs) and a 6-task proposal that passes check on a scratch copy, but the proposal cannot be written to plan.yaml. The seeded `plan.yaml` carries `station_only: true`, and `harness_yaml._validate_station_only` (control-plane `bin/harness_yaml.py`) refuses that marker next to any tasks. No plan-merge verb removes it: `apply` exits 5 or 7, and `set-key` to null is refused. plan.yaml is outside this lead's domain and outside pm's grant. The reader wave, apply and goalcheck did not run.

## To unblock (main session)
1. Delete the `station_only: true` line from `<tree>/.harness/harness/features/BUG-2565-digest-frontmatter-contract/plan.yaml`.
2. Re-dispatch this plan run. It can reuse this run with the draft re-dispatched, or open a new run. pm then lands `notes/research-plan-proposal.md` via `plan-merge.py apply --proposal` and runs `plan-merge.py check`.

## Draft assessment against the pre-written send-back criteria (sendback-criteria.md)
- All 6 tasks are `execution_mode: main-session-direct`.
- Ordering: the fail-closed refusal (T-02) and the projection (T-03) both come before the frontmatter/check-omp-port task (T-04). This meets the "with or before" constraint.
- `decisions_affected` has 11 rows (DEC-100/126/127/206/208/237/174/179/233/188/254). DECISIONS is amended in place by T-06.
- The two "Not yet specified" items are carried as live probes: T-01 measures the yield-refusal retry behaviour and T-05 runs the binding probe. Neither is decided silently.
- No criterion would trigger a send-back. This is not reader review: no reader has seen the draft.

## pm's non-blocking questions for signature
- Q-03: D-04 goes beyond the grilling. It refuses data-less `type: result` yields. Extra stale sites were added: SPEC §8.3, the DEC-100 table and the harness-team SKILL line.
- Q-04: should #2482 be added to source_issues?
- Q-05: T-02's verify may run over 60s.

## Harness defect
There is no path from a station-only seed to a plan with tasks (`_validate_station_only` together with `union._verify_schema_preserved`). Whoever seeds feature directories this way leaves pm unable to draft.

```yaml
VERDICT: BLOCKED
DIGEST:
  headline: 'BUG-2565 BRIEF (11 SCs) and a checked 6-task proposal are drafted but
    can''t land: the seeded plan.yaml''s station_only:true marker can''t be removed
    by any plan-merge verb. Main must delete that line, then re-run the plan team.
    Readers, apply and goal-check have not run.'
  open_questions:
  - id: Q-01
    question: 'Delete the `station_only: true` line from <tree>/.harness/harness/features/BUG-2565-digest-frontmatter-contract/plan.yaml.
      harness_yaml._validate_station_only refuses it once tasks exist; apply exits
      5 or 7 and set-key null is refused. Then re-dispatch the plan run: pm lands
      notes/research-plan-proposal.md with `plan-merge.py apply --proposal` and runs
      check. The reader wave, apply and goal-check follow.'
    blocking: true
  - id: Q-02
    question: 'Harness defect: there is no route from a station-only seeded plan.yaml
      to a plan with tasks (_validate_station_only together with union._verify_schema_preserved).
      Whoever seeds feature dirs this way leaves pm unable to draft through plan-merge.'
    blocking: false
  - id: Q-03
    question: "pm's D-04 goes past the grilling: it refuses data-less `type: result`\
      \ yields, because strict mode can't be set from frontmatter. T-06 also adds\
      \ stale sites the grilling didn't list: SPEC \xA78.3, the DEC-100 table and\
      \ a harness-team SKILL line. The operator can prune these at signature."
    blocking: false
  - id: Q-04
    question: 'Add #2482 (superseded) to source_issues so ship closes it?'
    blocking: false
  - id: Q-05
    question: T-02's verify (bun install + bun test + typecheck) may run over 60 s.
      It was untimed because the worktree has no node_modules.
    blocking: false
  files_touched:
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/BRIEF.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-digest-frontmatter-contract.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-plan-proposal.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/observations/harness-pm.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-01-plan-product/state.yaml
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-01-plan-product/sendback-criteria.md
  expertise_update: []
  team: plan
  steps_run: 1
  cycles_used: 0
  members:
  - step: draft
    persona: harness-pm
    verdict: BLOCKED
    headline: 'BRIEF and a 6-task plan proposal are ready (scratch check: 6 tasks,
      34 anchors, 0 failures), but they can''t be applied while the seeded station_only
      marker is in plan.yaml'
    files_touched:
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/BRIEF.md
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-digest-frontmatter-contract.md
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-plan-proposal.md
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/observations/harness-pm.md
  must_fix:
  - 'Remove `station_only: true` from the feature''s plan.yaml so plan-merge apply
    can land the proposal'
  branch: none
  escalations: []
  adequacy_notes:
  - Lead pre-check of the proposal against the pre-written send-back criteria found
    no send-back. All 6 tasks are main-session-direct. Fail-closed (T-02) and the
    projection (T-03) come before the frontmatter/check-omp-port task (T-04). decisions_affected
    has 11 rows. The grilling's two unspecified items are carried as live probes in
    T-01 and T-05. No plan reader has reviewed it yet.
  - I confirmed the station_only refusal at the control-plane source (bin/harness_yaml.py
    _validate_station_only); plan.yaml is outside this lead's write domain.
  sc_status: []
  needs_approval: false
  severity_max: none
  matrix_ok: none
  coverage_gaps: []
  findings: []
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2565-digest-frontmatter-contract/.harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-01-plan-product/digest.md
```
