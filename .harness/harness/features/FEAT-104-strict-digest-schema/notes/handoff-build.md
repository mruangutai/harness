# Handoff — FEAT-104-strict-digest-schema, build → build — written at 81901ea5, seq-2

## Next

Main session executes **T-10** directly, at the OWNER ROOT `/Users/molchairuangutai/GitHub/harness`,
per `plan.yaml` T-10 `execution_mode: main-session-direct`. In the same act, before `start-task`:
`plan-merge.py set-task-station --task T-10 --station building`, then
`gh-sync.py start-task <feature-dir> T-10`, and — because no eng segment will ever dispatch on this
feature — `plan-merge.py set-feature-station --station building`. Eight of nine tasks are
main-session-direct; only T-09 (`harness-documentor`, via product-lead) is team work, and it is
blocked on T-04, T-06, T-07, T-08. No lead may be dispatched until then.

## Trust

- Both approvals are signed: `plan.yaml:3-6` `approval.status: approved` and `BRIEF.md:206-208`
  `## Approval status: approved — 2026-09-09` — verified-at 81901ea5
- Build entry is complete, not merely claimed: `feature.json` `github.build_entry: opened`,
  parent 1584, nine sub-issues 1585–1593 mapped one per T-NN — verified-at 81901ea5
- Lane census, read task by task and not by file-global grep: T-01, T-03, T-04, T-05, T-06, T-07,
  T-08, T-10 are `main-session-direct`; T-09 alone is `team` —
  `plan.yaml:102,273,327,386,436,496,529,585,643` — verified-at 81901ea5
- T-10's deliverable is absent from disk, so T-10 has not run —
  no `notes/run-artifact-manifest-base.txt` — verified-at 81901ea5
- The worktree is clean and rebased on local main; `git status --porcelain` is empty at
  `81901ea5 chore(feat-104): enter ready station` — verified-at 81901ea5
- T-10's lane rests on TOOL REACH, not on DEC-174 — its `execution_reason` cites the owner-root
  manifest and gitignored `runs/`, not the enforcement carve-out — `plan.yaml:644` —
  verified-at 81901ea5

## Dead ends

- Do not follow `notes/handoff-plan.md` `## Next` "dispatch T-10 first to harness-eng-lead": it
  contradicts the approved plan's own lane for T-10 and the plan governs — `plan.yaml:643-644` —
  verified-at 81901ea5
- Do not re-lane a main-session-direct task at execution time to unblock the build; the lane is an
  approved plan field and re-laning is pm's under operator approval — `DECISIONS.md` DEC-179 —
  verified-at 81901ea5
- Do not write T-10's or any main-session-direct task's station as the orchestrator; station writes
  follow `execution_mode` — `.agents/skills/harness/references/github-mirror.md`, task-start and
  phase-transition rows — verified-at 81901ea5
- Do not treat the plan-panel finding PF-4bd91290deaf98062943319ff3ea5641 as open; all four `PF-`
  findings read `disposition: resolved` — `plan.yaml` `panel.findings` — verified-at 81901ea5

## Working set

- `.harness/harness/features/FEAT-104-strict-digest-schema/plan.yaml`
- `.harness/harness/features/FEAT-104-strict-digest-schema/feature.json`
- `.agents/skills/harness/references/github-mirror.md`
- `.harness/harness/features/FEAT-104-strict-digest-schema/notes/handoff-plan.md`

## Done when

Scope: T-10 captures the run-artifact baseline manifest at the owner root, before any other task
Authority: plan-task:T-10.verify
