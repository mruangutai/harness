# STATE

## Current

- feature: BUG-442-docs-grant-witness-test
- run: .harness/harness/features/BUG-442-docs-grant-witness-test/runs/2026-09-07-04-product/state.yaml
- squad: none
- status: awaiting-user

Plan phase COMPLETE and the plan is signature-ready. `plan.yaml` carries station `plan`,
one task (T-01), three decisions, and the cycle-0 `panel:` record. `approval.status` is
`pending` in both plan.yaml and BRIEF.md — only the main session signs. `check-state.sh`
reports nothing against this feature but the expected unapproved-BRIEF user gate.

Panel outcome: PASS, `severity_max: med`, `must_fix` empty. Both readers RAN — no skips.
Three advisory findings (2 med, 1 low) were folded into T-01 before the plan was closed;
the fourth (info, the hand-pinned census) is recorded `open` as a deliberate non-action.
`cycles_used: 1` — the plan work itself passed first-pass; the one cycle is the digest
send-back below.

Recorded as a failure, not smoothed over: the validator lead emitted its panel digest
TWICE. The second copy, `runs/2026-09-07-02-validator/`, put `status: ran` on its member
entries, where the lead contract reserves `status:` for skips — so it failed
`validate-digest.py` and reddened `check-state.sh` against this feature. Routed back to the
lead, which correctly returned BLOCKED rather than faking a repair: every write route open
to it was refused, and an append (the one route check-domain.sh permits on a recorded
digest) cannot cure a defect inside the first DIGEST block. The orchestrator then removed
the duplicate directory: it was gitignored, never committed, never in `feature.json`'s
`runs:`, and wholly superseded by `runs/2026-09-07-03-validator/`, which is and always was
the canonical record. Nothing that any record referenced was deleted.

Log — station transitions:
- 2026-09-07: backlog -> plan. Feature dir instantiated; BRIEF.md and plan.yaml drafted;
  panel run at cycle 0; handoff written to notes/handoff-plan.md. Awaiting signature.

## Open Questions

- Harness defect, non-blocking, for the harness owner. Guards resolve a relative path
  against the MAIN checkout instead of the caller's worktree, so worktree-based flows —
  which is how the harness actually runs every feature — hit false denials. Two independent
  sightings today: (1) `handoff_done_when.py:359-364` matches FEATURE_RE against a
  worktree-relative `rel_path` then joins it to the main root, so `plan-task:` and
  `brief-sc:` authority pointers CANNOT resolve from a worktree; worked around by using the
  explicit-path `approval:` form. (2) `bash-write-guard.sh` rejected a `rm` issued with a
  relative path from inside the worktree, naming the main-checkout path as the target;
  the identical command with an absolute worktree path was allowed.
- Harness defect, non-blocking, raised by harness-validator-lead. `check-domain.sh:1312-1318`
  permits correcting a recorded run digest only by APPENDING, but `validate-digest.py`'s
  `parse_digest` binds the FIRST `DIGEST:` block and stops at the first dedent. The permitted
  route and the enforced contract therefore do not intersect: no contract defect inside a
  recorded digest can be repaired by any governed agent.
