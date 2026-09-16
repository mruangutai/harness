# SC-01 evidence — post-signature ready write

Actor: main session, immediately after writing the plan.yaml/BRIEF.md signature at
commit f085e632.

Command run from the worktree root:
```
python3 .claude/skills/harness/bin/gh-sync.py status .harness/harness/features/BUG-1507-ready-station-signature ready
```

Output:
```
gh-sync: plan.yaml station -> ready
gh-sync: station ready — no sub-issues recorded, nothing to move
```
Exit: 0

Observations against SC-01's three required points:

(a) `gh-sync.py status <feature-dir> ready` exited 0 and printed
`gh-sync: plan.yaml station -> ready` — met.
(b) `plan.yaml`'s top-level `status:` now reads `ready` — met (checked with
`grep '^status:' plan.yaml`).
(c) `feature.json` carries no `github` key at 4b5dbb23-descendant state (this feature has not
yet been mirrored to GitHub sub-issues) — zero sub-issues recorded, zero cards moved. This
observation is the documented zero-recorded case; per the criterion's own text this is not
graded `met`.

**Verdict: partial** — (a) and (b) discharged, (c) not applicable/not met because this feature
has no recorded T-NN sub-issues yet.
