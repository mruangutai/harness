# STATE

## Current

- feature: BUG-1290-factory-claim-repo-root
- run: none in flight — ship phase complete at the operator ship decision
- squad: none
- status: awaiting-user

Every gate green. Build T-01..T-05 PASS (1 send-back), qa test-matrix PASS (the project's only
blocking gate), simplify an empty pass over four angles, validation panel PASS with `must_fix: []`
and `severity_max: med` (non-gating), goal-check all nine SC MET verified by pm's own runs.
`review_sha` pinned at `76e26386`; plan station `review`, all five tasks `done`; mirror at review
(milestone #51, parent #1359, tasks #1360..#1364). 13 runs of an informational 20, 4 rework cycles
of a hard 10. Briefing:
`notes/ship-review-2026-09-05-13-ship.md` (rendered `.html` beside it). Handoff:
`notes/handoff-ship.md`. No PR, no merge, nothing shipped — the operator's ship/fix/re-scope/stop
decision is the next act.

## Open Questions

- Q1 (non-blocking, operator only): REQ-05 and D-01 say the segment rule is called by
  `factory_claim.py`, `feature-worktree.py:resolve_repo` and `factory_config.workspace_path`.
  Measured at the pin, `segment_of`'s direct callers are `features_root`, `workspace_path` and
  `feature-worktree.py:86`; `factory_claim.py` reaches it transitively through `features_root`.
  SC-06 is MET on its own words. pm recommends a one-line record correction as an operator ruling
  on the approved BRIEF; no agent may edit it. Briefing row B-10.
- Q2 (non-blocking, operator only): REQ-02's issue-map clause is delivered
  (`factory_claim.py:135` keys on `(repo, feature)`) but unproven — a mutant re-keying the issue map
  on feature alone reddens nothing, because both `5b` fixtures carry an empty `factory.issues` map.
  Test-only gap, owner T-01, ~2 lines. SC-02's text gates the cached task, which is proven, so this
  gates nothing. Fix cycle now, or ship as disclosed residue? Briefing row B-3.
- Q3 (harness defect, for the harness owner): `check-domain` matches inflight claims by bare
  agent-type across every linked worktree with no session scoping, so a concurrent same-role session
  on an unrelated flow becomes that role's only binding. It refused six read-only agents' note
  writes across two consecutive runs; every analysis survived only by inline transcription.
  Briefing row B-11.
