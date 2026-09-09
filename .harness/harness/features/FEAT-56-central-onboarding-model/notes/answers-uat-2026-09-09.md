# Operator UAT result — FEAT-56, revised (relayed by the main session, 2026-09-09)

**UAT: PASS.** All three criteria met. Recorded by the orchestrator from the main session's relay;
the operator's verdict is theirs and is not inferred here. The evidence they reported, per step:

## SC-11 — `harness-init` as a fresh-checkout procedure

- A-1: all six steps target only the harness checkout.
- A-2: no registration, BRIEF, approval or design work remains in it.
- A-3: `--upgrade` routes only to retained instructions.

## SC-12 — `harness-add-repo` as a registration procedure

- B-1: the preflight stops on an unconfigured control plane and on an unauthenticated or missing
  `gh`, and routes to init.
- B-2: it lands the product `harness.json` BEFORE fleet registration, and states the reason — which
  is D-04's ordering rule, the one whose reversal has no symptom but an unattributed `FleetError`.
- B-3: it stops at registration and routes BRIEF, approval and design to `/harness-plan`.

## SC-15 — the live OMP session

- C-1: an OMP session was launched in this feature's worktree and `/harness-plan` printed
  `OMP-ROOT-PROBE-SEEN`, so the door resolved from `.omp/commands/` and not from the generated
  `.claude/commands/` adapter. The marker was then removed and
  `git status --porcelain .omp/commands/harness-plan.md` came back empty.

**Probe revert independently verified by the orchestrator** at 6c2aa581: that path is clean in
`git status`, the marker string occurs zero times in the file, and the whole worktree is clean. So
the probe left nothing behind — which matters, because a UAT that mutates a graded file and does not
prove the revert would have contaminated the very blob every content criterion is cited against.

This is the criterion three prior UAT rounds could not reach. Nothing else in this feature observes a
live provider resolving a door: `check-omp-port.py` checks existence and
`sync-command-adapters.py --check` compares bytes, and both are blind to which root a provider
actually reads.

## Backlog

Not yet disposed. The operator asked to see the C-1..C-16 table before choosing. No issues are
created and no row is struck until they do.
