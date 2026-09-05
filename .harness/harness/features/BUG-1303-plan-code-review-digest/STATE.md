# STATE

## Current

- feature: BUG-1303-plan-code-review-digest
- run: .harness/harness/features/BUG-1303-plan-code-review-digest/runs/2026-09-05-10-product/state.yaml
- squad: product
- status: awaiting-user

Plan phase complete and signature-ready with NO overrule required. BRIEF.md (REQ-01..05, SC-01..08)
and plan.yaml (T-01..T-04, D-01..D-07) carry `approval.status: pending`; only the main session signs.
The adversarial panel ran three times: cycle 1 FAIL (one high), cycle 2 PASS at severity_max med with
three findings left open, cycle 3 PASS at `severity_max: none` with both readers `ran` and zero new
findings. All 11 findings on the record are `resolved`; zero open. Handoff: notes/handoff-plan.md.
cycles_used 3 of 8.

## Open Questions

- Harness defect, not a BUG-1303 finding: inside a worktree, `handoff_done_when` authority pointers
  and a panel reader's structured `yield` both resolve against the MAIN checkout, because
  check-domain strips the `.claude/worktrees/<seg>/` prefix for glob matching and then reuses the
  stripped path for resolution. Measured; worked around here by spelling the authority root-relative
  through `.claude/worktrees/`. Blocked on: infra-tier attention.
- Build-time sequencing, for the main session: T-04 appends a decision to DECISIONS.md numbered
  max+1 at edit time, while five sibling bug flows plan concurrently. The plan pins the ruling TEXT
  and never the number, so no anchor rots, but concurrent appends can collide on the integer.
  Serialize the DECISIONS.md appends at build time. Noted, not implemented.
- Harness defect: bash-write-guard.sh parses the whole command line textually, so plan-merge.py's
  sanctioned `apply --proposal -` stdin route is refused when the proposal body contains an angle
  bracket; and `amend --value-file -` is not wired to stdin although `apply --proposal -` is.
