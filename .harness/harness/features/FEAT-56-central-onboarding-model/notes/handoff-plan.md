# Handoff — FEAT-56-central-onboarding-model, plan → ready — written at 52f8866a, seq-4

SUPERSEDES seq-1. The operator re-scoped this feature at the UAT gate after the first eight tasks
had shipped-ready; the plan phase ran a second time, at panel cycle 1, over a revised task set.

## Next

Obtain the operator signature on the REVISED plan. Both fragments read pending. Ask the main
session to run `plan-merge.py sign-approval --file <feature-dir>/plan.yaml --by <operator> --date
<today>` and to write BRIEF.md's `## Approval`. No `--overrule` flags — no finding is open above
`low`. Then `gh-sync.py open <feature-dir>` for T-09..T-17, then the plan→ready station write, then
build at T-09, the only ready task with no `depends_on`.

## Trust

- Both approval fragments read pending, so nothing downstream is unblocked —
  `plan.yaml` `approval.status` and `BRIEF.md` `## Approval` — verified-at 52f8866a
- The panel is complete at cycle 1 with all three readers `ran`, 34 findings, zero open above `low`,
  and every id verifying against `panel_findings.finding_id` — `plan.yaml` `panel:` — verified-at
  52f8866a
- T-01..T-08 remain `done` with landed commits; the operator rejected the SHAPE, not the work —
  `plan.yaml` `tasks[].status` and `git log 4b5dbb23..HEAD` — verified-at 52f8866a
- No prior grade is retained: all five already-met SC markings were dropped, four of them because a
  new task rewrites their subject — `notes/research-FEAT-56-replanfix-c1.md` — verified-at 52f8866a
- Six of the nine new tasks are main-session-direct and no agent may write their files —
  `check-plan-routes.py` 0 violations, `check-domain.sh --resolve` per path — verified-at 52f8866a
- D-12 is pm's decision on the one thing the plan had left undecided and is the operator's to
  overrule at signature — `plan.yaml` `decisions:` — verified-at 52f8866a
- Budget has headroom: `cycles_used` 13 of `max_total_cycles` 22, the operator's raise for this
  replan — `feature.json` — verified-at 52f8866a

## Dead ends

- Do not split this into a successor feature: the advisor recommended it and the operator overruled
  them in writing — `notes/answers-rescope-2026-09-08.md` decision 1 — verified-at 52f8866a
- Do not build issue #206 item 2, `.harness/products/<name>/` — `notes/analysis-FEAT-56-rescope-advisor.md`
  — verified-at 52f8866a
- Do not clear another flow's live persona claim to unblock a squad write: check-domain enforces
  single-flight by agent TYPE across every worktree, so the collision is structural and the fix is a
  ticket, not a release — `BUG-1507` registry, `supervisor_pid` 71129 alive — verified-at 52f8866a

## Working set

- .harness/harness/features/FEAT-56-central-onboarding-model/plan.yaml
- .harness/harness/features/FEAT-56-central-onboarding-model/BRIEF.md
- .harness/harness/features/FEAT-56-central-onboarding-model/notes/answers-rescope-2026-09-08.md
- .harness/harness/features/FEAT-56-central-onboarding-model/notes/research-FEAT-56-goalcheck-plan-c1.md
- .claude/skills/harness-init/SKILL.md

## Done when

Scope: operator signature recorded on both approval fragments of the revised plan
Authority: approval:.harness/harness/features/FEAT-56-central-onboarding-model/BRIEF.md#Approval
Authority: brief-sc:SC-01
