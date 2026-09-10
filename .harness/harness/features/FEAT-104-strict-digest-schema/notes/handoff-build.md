# Handoff — FEAT-104-strict-digest-schema, build → build — written at 94e5428e, seq-3

## Next

Main session executes **T-01** directly, per `plan.yaml:102` `execution_mode: main-session-direct`;
its only dependency, T-10, is now `done`. In the same act, before `start-task`:
`plan-merge.py set-task-station --task T-01 --station building`, then
`gh-sync.py start-task <feature-dir> T-01`. Remaining order is T-01 → T-03 → {T-04, T-05} →
{T-06, T-07} → T-08, all main-session-direct; only then does T-09 (`harness-documentor`, via
`harness-product-lead`) become the first and only dispatchable team work.

## Trust

- T-10 has landed and its verify floor is met: commit `94e5428e`, manifest
  `notes/run-artifact-manifest-base.txt` 728 lines against `assert 726 <= n`, station `done` —
  verified-at 94e5428e
- Both approvals are signed: `plan.yaml:3-6` `approval.status: approved` and the BRIEF's approval
  section at `BRIEF.md:206-208` — verified-at 94e5428e
- Build entry is complete, not merely claimed: `feature.json` `github.build_entry: opened`,
  parent 1584, nine sub-issues 1585–1593 mapped one per task — verified-at 94e5428e
- Lane census, read task by task and not by file-global grep: T-01, T-03, T-04, T-05, T-06, T-07,
  T-08, T-10 are `main-session-direct`; T-09 alone is `team` —
  `plan.yaml:102,273,327,386,436,496,529,585,643` — verified-at 94e5428e
- The feature station is already `building`; it does not need writing again — `plan.yaml:7` —
  verified-at 94e5428e
- The nine INV-26 card/plan mismatches are mirror-side and gate nothing: eight cards at `backlog`
  vs plan `ready`, T-10's at `building` vs plan `done` — `check-state.sh` run in this worktree —
  verified-at 94e5428e

## Dead ends

- Do not follow `notes/handoff-plan.md` `## Next` "dispatch T-10 first to harness-eng-lead": it
  contradicted the approved plan's lane for T-10, and T-10 has since been executed by the main
  session — `plan.yaml:643-644` — verified-at 94e5428e
- Do not re-lane a main-session-direct task at execution time to unblock the build; the lane is an
  approved plan field and re-laning is pm's under operator approval — `DECISIONS.md` DEC-179 —
  verified-at 94e5428e
- Do not write a main-session-direct task's station as the orchestrator; station writes follow
  `execution_mode` — `.agents/skills/harness/references/github-mirror.md`, task-start and
  phase-transition rows — verified-at 94e5428e
- Do not write a literal `T-NN` placeholder into STATE.md; INV-26's sibling check scans it with
  `\bT-[0-9A-Za-z]+\b` and fails the id against the plan — `check-state.sh:356-361` —
  verified-at 94e5428e

## Working set

- `.harness/harness/features/FEAT-104-strict-digest-schema/plan.yaml`
- `.harness/harness/features/FEAT-104-strict-digest-schema/feature.json`
- `.agents/skills/harness/references/github-mirror.md`
- `.harness/harness/features/FEAT-104-strict-digest-schema/notes/run-artifact-manifest-base.txt`

## Done when

Scope: T-01 declares the passthrough and documented-optional tables and requires adequacy_notes
Authority: plan-task:T-01.verify
