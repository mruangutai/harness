# STATE

## Current

- feature: FEAT-56-central-onboarding-model
- run: .harness/harness/features/FEAT-56-central-onboarding-model/runs/2026-09-08-panelfix-c1-product/state.yaml
- squad: none
- status: awaiting-user

Revised in place on the operator's re-scope of 2026-09-08 and now SIGNATURE-READY at 52f8866a,
pushed. Two artifacts: `harness-init` isolated to first-time configuration of a fresh Harness
checkout, and a new provider-neutral `harness-add-repo` skill registering a repository into the
configured control plane; the OMP command-door port lands in this same feature; first-BRIEF,
approval and design move out of onboarding, routing to `/harness-plan`.

plan.yaml: 17 tasks — T-01..T-08 `done` with landed commits, T-09..T-17 `ready`. 12 decisions.
Station `plan`. Panel complete at cycle 1: all three readers `ran`, 34 findings, zero open above
`low`, every id verifying. BRIEF.md: 13 SCs, no prior grade retained. check-plan-routes 0
violations. cycles_used 13 of 22.

Blocked only on the operator signature. Nothing else in the plan phase remains, and no build has
started — T-09 onward would be building against an unapproved task set.

## Open Questions

- Operator signature on BRIEF.md `## Approval` and plan.yaml `approval:`, via `plan-merge.py
  sign-approval`. Main session only. No `--overrule` flags needed: no finding is open above `low`.
- D-12 wants the operator's eye before they sign: `harness-init` keeps the CLI 2.1.217 floor as a
  runtime-conditional check — a hard STOP under Claude Code, no stop under any other runtime —
  rather than an unconditional Claude-only STOP. pm decided it because the panel found the plan had
  left it undecided, and it sits against the operator's own "rather than implementing a
  Claude-Code-only path". Overridable either way.
- Harness defect for a ticket of its own, six recurrences this feature: `check-domain` enforces
  single-flight by agent TYPE across every linked worktree, so any concurrently-running feature
  holding `harness-pm` or `harness-validator-lead` refuses this feature's squad writes mid-run.
  Structural, not stale-claim debris.
