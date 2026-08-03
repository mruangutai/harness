# STATE

## Current

- feature: FEAT-05-pyyaml-file-parsers
- run: .harness/features/FEAT-05-pyyaml-file-parsers/runs/2026-08-02-03-product/state.yaml
- squad: product
- status: awaiting-user

Phase `plan` COMPLETE, 2026-08-02. Three runs, one rework cycle. BRIEF.md (7 REQs / 13 SCs) and
PLAN.md (17 tasks, 13 decisions) both `status: pending`, awaiting one bundled signature. Seam note
at `notes/handoff-plan.md`. Build does not start until the user signs.

## Open Questions

- Q1/Q2/Q3 — three BRIEF statements planning measured FALSE. REQ-01 names `cost-report.py`, which
  reads no YAML; SC-03's parenthetical undercounts the surviving regex calls; SC-02's exit-0 baseline
  is stale. Amendments ride the signature. USER RULES.
- Q5 — the main session appends `## Approval` (`status: pending`) to BOTH artifacts. No agent may.
- Q7 — routing wall, third recurrence. `dev-ops` is granted neither `.gitignore`, nor
  `templates/**`, nor `harness-init/SKILL.md`, so T-10 and T-11 are MAIN-SESSION steps inside the
  build spine and T-12 blocks on T-10. The org grants the paths or accepts the step. USER RULES.
- Q4 — session identity in a PreToolUse hook subprocess is unconfirmed. T-09 probes it in-band and
  ESCALATEs if nothing resolves. Not a user question yet.
- Q6 — harness defect: the `SubagentStop` validator resolves a different `validate-digest.py` than
  the worktree's, so worktree digests are judged by the main checkout's rules. Backlog.
- Cost — $92 of the $120 budget spent in the plan phase alone. Reported, not gating (DEC-134).
