# SC-05 evidence — the feature's own `plan.yaml` recorded at `status: building`

**Conclusion: SC-05's observation is recorded — this feature's `plan.yaml` reads `status: building`,
written at the moment the eng segment began, by the orchestrator, by hand from the worktree copy of
the instruction T-03 adds.**

- actor: `harness-orchestrator` (BUG-1507's build-phase orchestrator), itself
- when: 2026-09-09T04:58Z, immediately before the first build work of the eng segment (T-01, the
  first main-session-direct carve-out edit) and before any lead dispatch
- worktree: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1507-ready-station-signature`
- HEAD at the write: `acc8bf634016b36606f7dfd0ff2f8a699ee7fe04`

## The command, verbatim

```
python3 .claude/skills/harness/bin/plan-merge.py set-feature-station \
  --file .harness/harness/features/BUG-1507-ready-station-signature/plan.yaml \
  --station building
```

Output, verbatim:

```
STATION .../features/BUG-1507-ready-station-signature/plan.yaml -> building
APPLIED .../features/BUG-1507-ready-station-signature/plan.yaml
exit 0
```

## The observed `status:` line

`grep -n '^status:' plan.yaml` immediately after the write:

```
3:status: building
```

The approval mapping was untouched by the write and still reads, at lines 6-7:

```
  approved_by: operator
  status: approved
```

## Disclosure, per SC-05's own wording

The write was performed **by hand**. The orchestrator's loaded `SKILL.md` comes from the
control-plane checkout, which does not carry T-03's build-phase instruction until this branch
merges; the instruction being followed is the **worktree's**
`.claude/skills/harness/SKILL.md` (T-03's deliverable), gradeable at
`git show <review_sha>:.claude/skills/harness/SKILL.md` per SC-04. This feature therefore
demonstrates the station being **recorded**, not the instruction being obeyed automatically —
exactly the limit SC-05 states.
