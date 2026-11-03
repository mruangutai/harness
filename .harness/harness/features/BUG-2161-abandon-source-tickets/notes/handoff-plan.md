# Handoff — BUG-2161-abandon-source-tickets, plan → build — written at 57222856, seq-4

## Next

Build entry (build-phase.md step 1–2): `github.build_entry` already reads `opened` (feature.json), so run `gh-sync.py status <feature-dir> building` for the whole card set, then `feature-record.py run-start --squad engineering --agent harness-eng-lead` (slug `build-eng`) and ONE `build` team dispatch to `harness-eng-lead` carrying T-01 and T-02 in plan order — T-02 `depends_on: [T-01]` — with `verify:` verbatim from `plan.yaml`. Inputs: `plan.yaml` T-01/T-02, `BRIEF.md` SC-01..SC-06, decisions D-01..D-03. The successor's `run-start` must carry `--succession` (seq-4).

## Trust

- Plan is signed: `plan.yaml` `approval.status: approved`, `status: ready`; BRIEF `## Approval` approved by operator 2026-11-03 — `notes/operator-signature-2026-11-03.md` — verified-at 57222856
- Rework ruling is 2 rounds / 90 minutes — `feature.json` `rework` — verified-at 57222856
- Mirror opened: milestone #104, parent #2162, T-01 #2163, T-02 #2164, source #2161; `github.build_entry: opened` — `feature.json` `github` — verified-at 57222856
- `signed_task_hashes` cover T-01 and T-02; any `intent`/`files`/`verify` change needs `plan-merge.py record-amendments` from the eng-lead digest — `feature.json` `signed_task_hashes` — verified-at 57222856
- Panel c0 (scope, should-not-exist, design, goalcheck) all ran; two `scope: task` proportionality findings applied — `plan.yaml` `panel` — verified-at 469e643c
- Four-angle simplify pass on the plan surface ran; F-01 (`_feature_station` reuse) and F-02 (generalize `_post_abandon_reason`/`_report_abandon_gaps` in place) folded into T-01 intent — `runs/2026-11-02-03-simplify-plan-eng/digest.md`, `notes/research-simplify-apply-2026-11-02-04.md` — verified-at 469e643c
- `gh-sync.py` resolves to harness-backend-dev / harness-dev-ops, so T-01 is squad work, never main-session-direct — `notes/research-abandon-source-tickets.md` lanes block — verified-at 469e643c
- `cycles_used: 0`; `max_total_cycles: 10` — `feature.json` — verified-at 57222856
- Leads in this runtime return by final message, so the SubagentStop hook never appends the fenced YAML to `runs/<id>/digest.md`; close-run's digest stage refuses until the validated object is appended by hand — `observations/harness-orchestrator.md` 2026-11-02 — verified-at 469e643c

## Dead ends

- No shared-ticket corpus check and no lookup detector test: issue #2161's Constraint is overruled; PF-a68755d85a05e098891d2d28274a6e7a dropped it — `plan.yaml` `panel.findings`, BRIEF `## Constraints` — verified-at 469e643c
- Run-dir slugs must end `-eng|-product|-validator`; `2026-11-02-02-engineering` was refused by dispatch-guard and closed BLOCKED at zero cycles — `feature.json` runs — verified-at 469e643c
- Plan-time gates are spent: no re-panel, no second goal-check before validate (SC-09); the next goal-check is inside `validate` — `plan-phase.md` — verified-at 57222856
- Operator-only SC-07 (live #1774 disposal) is post-merge `uat`; no run may claim it — BRIEF SC-07 — verified-at 57222856

## Working set

- .harness/harness/features/BUG-2161-abandon-source-tickets/plan.yaml
- .harness/harness/features/BUG-2161-abandon-source-tickets/BRIEF.md
- .harness/harness/features/BUG-2161-abandon-source-tickets/feature.json
- .harness/harness/features/BUG-2161-abandon-source-tickets/STATE.md
- /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/references/build-phase.md

## Done when

Scope: build team dispatched to harness-eng-lead for T-01 and T-02, each with a PASS run recorded
Authority: brief-perspective:.harness/harness/features/BUG-2161-abandon-source-tickets/BRIEF.md#code maintainer
Authority: plan-task:T-01.verify
Authority: plan-task:T-02.verify
