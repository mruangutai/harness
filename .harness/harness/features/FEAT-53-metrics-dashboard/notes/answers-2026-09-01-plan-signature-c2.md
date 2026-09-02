# Answers — FEAT-53 plan-signature briefing, pass 2 — 2026-09-01

## Q1 — PF-45518258 (high, T-16/T-21 ordering gap)
**Ruling: FIX.** Add `T-21` (or `T-22`, whichever actually produces the mounted-chart bundle) to
`T-16`'s `depends_on`, so the production `dist/` build always happens after the chart is wired into
the panel. Do not ship this as a known issue — it reproduces the exact DEC-4 defect already ordered
fixed once.

## Q2 — cycle-time origin
**Ruling: Option A — match REQ-03 (measure from BRIEF approval).** The grilling and REQ-03 both
already said BRIEF approval; plan.yaml approval.date is not an acceptable substitute just because
it's cheaper to build. Capture a machine-readable BRIEF-approval date — this rides on the same act
as signing BRIEF.md's `## Approval` section, so it should not require new ceremony, just a recorded
timestamp at that existing signature. Update D-14, T-06, D-21 and the trend record accordingly.
`B-6` is now redundant — strike it.

## Q3 — backlog B-11..B-14
**Ruling: FIX B-11 now.** The epoch file (`.harness/metrics/instrumented_at`) and `touchpoints.jsonl`
need an explicit git disposition: they must be COMMITTED (not gitignored, not treated as ephemeral
scratch), and whichever task first creates them must also commit them in the same step so the tree
is never left dirty. State the disposition explicitly (a comment in `.gitignore` confirming these
paths are deliberately NOT ignored, plus the commit step in the owning task's intent) — this is not
a bare main-session `.gitignore` edit, it's a task-design fix pm must make, since it determines which
task is responsible for the commit.

**ACCEPT B-12, B-13, B-14 as backlog**, labeled "Dashboard" same as B-1..B-10. B-12 cannot be fixed
until the plan-merge.py tool defect is fixed anyway.

## Harness defects (this pass)
Noted, not actioned: `plan-merge.py apply`'s unremovable spliced comment block, the worktree-vendored
`.claude/skills` making new `bin/` verbs unreachable in-tree, and BUG-1080 reproducing on
`validate-digest.py`'s yield path. All added to the same BUG filing as the earlier-found defects.
