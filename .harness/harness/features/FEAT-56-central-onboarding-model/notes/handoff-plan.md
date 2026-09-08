# Handoff — FEAT-56-central-onboarding-model, plan → ready — written at 4b5dbb23, seq-1

## Next

Obtain the operator signature. The plan is drafted, panelled and clean: ask the main session to run
`plan-merge.py sign-approval --file <feature-dir>/plan.yaml --by <operator> --date <today>` and to
write BRIEF.md's `## Approval`. Then run `gh-sync.py open <feature-dir>` — the orchestrator owns that
subcommand — and only then the plan→ready station write. Build starts at T-04, the one task with no
`depends_on`; every other task depends on T-01, which is main-session-direct.

## Trust

- Both approval fragments read pending, so nothing downstream is unblocked yet —
  `plan.yaml` `approval.status` and `BRIEF.md` `## Approval` — verified-at 4b5dbb23
- The panel ran all three readers and the record shows it: should-not-exist (fable-advisor), scope
  and goalcheck, each `status: ran`, 13 findings, every open one at info/low/med so INV-32 passes
  once signed — `plan.yaml` `panel:` — verified-at 4b5dbb23
- Every finding id hashes its own recorded summary under the tool that owns identity —
  `panel_findings.finding_id` over all 13 — verified-at 4b5dbb23
- Four of the eight tasks are main-session-direct and no agent may write their files, T-01 included —
  `check-domain.sh --resolve` per path, and `check-plan-routes.py` exit 0 — verified-at 4b5dbb23
- T-01, T-02, T-05, T-06 and T-07 verify blocks were each observed RED at this sha, so they can
  grade their own tasks — `notes/research-FEAT-56-planfix-c2.md` — verified-at 4b5dbb23

## Dead ends

- Do not build issue #206 item 2, `.harness/products/<name>/`: it matches no resolver and would
  overturn DEC-174 — `runs/2026-09-08-01-plan-advisor-validator/digest.md` — verified-at 4b5dbb23
- Do not delete `templates/team-config.yaml` as orphaned: T-01 still instantiates the control
  plane's own copy from it, so it is repaired, not removed — `notes/research-FEAT-56-goalcheck-plan-c0.md`
  — verified-at 4b5dbb23
- Do not touch the pilot product's committed `.harness/` subtrees — `BRIEF.md` `## Non-goals` —
  verified-at 4b5dbb23

## Working set

- .harness/harness/features/FEAT-56-central-onboarding-model/plan.yaml
- .harness/harness/features/FEAT-56-central-onboarding-model/BRIEF.md
- .harness/harness/features/FEAT-56-central-onboarding-model/feature.json
- .harness/harness/features/FEAT-56-central-onboarding-model/notes/research-FEAT-56-init-audit.md
- .agents/skills/harness-init/SKILL.md

## Done when

Scope: operator signature recorded on both approval fragments
Authority: approval:.harness/harness/features/FEAT-56-central-onboarding-model/BRIEF.md#Approval
Authority: brief-sc:SC-01
