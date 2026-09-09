# STATE

## Current

- feature: FEAT-56-central-onboarding-model
- run: .harness/harness/features/FEAT-56-central-onboarding-model/runs/2026-09-09-01-opamend-c2-product/state.yaml
- squad: none
- status: awaiting-user

Revised in place on the operator's re-scope of 2026-09-08, then amended on their two signature
conditions of 2026-09-09. Signature-ready. Two artifacts: `harness-init` isolated to first-time
configuration of a fresh Harness checkout, and a new provider-neutral `harness-add-repo` skill
registering a repository into the configured control plane; the OMP command-door port lands in this
same feature; first-BRIEF, approval and design move out of onboarding, routing to `/harness-plan`.

plan.yaml: 17 tasks — T-01..T-08 `done` with landed commits, T-09..T-17 `ready`. Decisions D-01..D-13.
Station `plan`. Panel recorded at cycle 1: all three readers `ran`, 34 findings, zero open above
`low`. BRIEF.md: 14 live success criteria (SC-09 struck when the re-scope killed its subject), no
prior grade retained. check-plan-routes 0 violations. cycles_used 15 of 22.

THE OPERATOR'S TWO CONDITIONS, both applied and verified at source. D-12 removes the Claude CLI
2.1.217 floor from `harness-init`'s preflight ENTIRELY — not kept, not made runtime-conditional, and
not downgraded to a warning; the conditional form was pm's earlier compromise and the operator
overruled it. SC-15 is a required live OMP UAT: the operator opens an OMP session and confirms
`/harness-plan` resolves from `.omp/commands`, with both FAIL shapes named and distinguishable.

Blocked only on the operator signature. No build has started — T-09 onward would build against an
unapproved task set.

## Open Questions

- Operator signature on BRIEF.md `## Approval` and plan.yaml `approval:`, via `plan-merge.py
  sign-approval`. Main session only. No `--overrule` flags: no finding is open above `low`.
- D-13, recorded OPEN with no task: `cli_min_version: "2.1.217"` remains in six files and in signed
  DEC-83. With no onboarding step reading it, it is either a documented Claude Code compatibility
  floor that no gate enforces or it is dead config. pm recommends keeping the key and amending
  DEC-83 to say the former. Touches a signed decision, so it is the operator's to rule at signature.
- Harness defect for a ticket of its own: `check-domain` enforces single-flight by agent TYPE across
  every linked worktree, so a concurrently-running feature's squad refuses this feature's squad
  writes mid-run. Measured: a live BUG-1309 review panel holds six persona claims at one live
  supervisor PID. NOT stale-claim debris — do not release them. Two releases were already made
  against BUG-1309 on an empty-roster reading, and the potential impact on that flow is recorded for
  its owner.
