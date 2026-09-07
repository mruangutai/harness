# STATE

## Current

- feature: BUG-442-docs-grant-witness-test
- run: none yet this phase
- squad: eng
- status: building

BUILD phase opened. Signature verified ON DISK, both halves (G-09): `plan.yaml`
`approval.status: approved` (`approved_by: operator`, 2026-09-07) and `BRIEF.md`
`## Approval` -> `status: approved`, `by: operator`. Both arrived uncommitted in this
worktree and are committed by the orchestrator's build-phase pen (DEC-153) together with
the station transition `plan -> building` (feature) and `ready -> building` (T-01), both
written through `plan-merge.py`, never by hand.

Sequence for this phase, orchestrator-sequenced squad segments: eng (T-01, `build` team
resolved at `.agents/skills/harness/teams/build.yaml` — `.harness/teams/build.yaml` does
not exist), then qa (`test_matrix` hard gate), then SIMPLIFY to eng-lead, then pin
`review_sha` and run the validator panel. Ship is NOT ours: the main session runs it.

Working memory lives here, in `## Current`, deliberately. `notes/handoff-<phase>.md`
cannot be written from a feature worktree for a feature that is not yet on the default
branch — check-domain's handoff shape gate resolves `Authority:` pointers against the MAIN
checkout root, not this worktree. Already diagnosed, already raised as a defect below; not
re-diagnosed here. The plan-phase handoff (`notes/handoff-plan.md`) landed only because it
used the explicit-path `approval:` pointer form as a workaround.

Panel finding `PF-049c59c515c538bc41da6616176f8987` (info, the hand-pinned census) stays
`open` as a deliberate non-action per the plan and per the dispatch. No ruling is needed
for an info-severity finding.

Log — station transitions:
- 2026-09-07: backlog -> plan. Feature dir instantiated; BRIEF.md and plan.yaml drafted;
  panel run at cycle 0; handoff written to notes/handoff-plan.md. Awaiting signature.
- 2026-09-07: plan -> building. Operator signature landed on both artifacts; T-01 moved
  ready -> building; eng segment dispatched to harness-eng-lead with the `build` team.

## Open Questions

- Harness defect, non-blocking, for the harness owner. Guards resolve a relative path
  against the MAIN checkout instead of the caller's worktree, so worktree-based flows —
  which is how the harness actually runs every feature — hit false denials. Three
  independent sightings: (1) `handoff_done_when.py:359-364` matches FEATURE_RE against a
  worktree-relative `rel_path` then joins it to the main root, so `plan-task:` and
  `brief-sc:` authority pointers CANNOT resolve from a worktree; worked around by using the
  explicit-path `approval:` form. (2) `bash-write-guard.sh` rejected a `rm` issued with a
  relative path from inside the worktree, naming the main-checkout path as the target;
  the identical command with an absolute worktree path was allowed. (3) The same root cause
  makes `notes/handoff-<phase>.md` unwritable from a worktree for a feature not yet on the
  default branch, so build-phase working memory is kept in this `## Current` instead.
- Harness defect, non-blocking, raised by harness-validator-lead. `check-domain.sh:1312-1318`
  permits correcting a recorded run digest only by APPENDING, but `validate-digest.py`'s
  `parse_digest` binds the FIRST `DIGEST:` block and stops at the first dedent. The permitted
  route and the enforced contract therefore do not intersect: no contract defect inside a
  recorded digest can be repaired by any governed agent.
