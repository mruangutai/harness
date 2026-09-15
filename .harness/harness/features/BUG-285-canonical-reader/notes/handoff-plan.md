# Handoff — BUG-285-canonical-reader, plan → build — written at e07521b2, seq-3

## Next

Do not dispatch build work until the main session signs both pending approvals and records the
operator's rework ruling. The generated baseline is 3 rounds / 135 minutes. Once
`approval.status` and BRIEF `## Approval` both read `approved`, set the feature station to
`building`, execute team-routed prerequisite T-09, then continue in dependency order with T-01
main-session-direct and T-02 through T-08 according to each task's recorded DEC-174 route.

## Trust

- The refreshed plan covers the current PR 1688 Python entrypoints and keeps all enforcement
  sources and their tests main-session-direct — `plan.yaml` T-01, T-05, T-06, T-07 and lanes,
  verified-at e07521b2.
- The one-accessor-module direction and issue 1682 hardening remain explicit — `BRIEF.md` SC-02,
  SC-03 and `plan.yaml` D-01/T-02, verified-at e07521b2.
- All recorded panel findings are resolved, all four required readers ran, and every goal-check
  perspective passed — `plan.yaml` panel and `notes/research-BUG-285-canonical-reader-goalcheck-plan.md`,
  verified-at e07521b2.
- BRIEF and plan approvals are pending — `BRIEF.md` Approval and `plan.yaml` approval, verified-at
  e07521b2; this is the build-entry precondition the main session must discharge.

## Dead ends

- Do not restore a `.sh` exclusion or defer `manifest_domains`; issue 1674 is closed and PR 1688
  made the former entrypoints AST-visible — `BRIEF.md` SC-01/SC-02 and `plan.yaml` D-03,
  verified-at e07521b2.
- Do not dispatch hooks, gates, validators, or their tests to a squad merely because they now use
  `.py`; DEC-174 remains category-based — `plan.yaml` lanes and task execution modes,
  verified-at e07521b2.
- Do not retain the dead `sh-to-py-differential.py` as an inventory exemption; T-09 deletes it
  before T-01 — `plan.yaml` T-09 and T-01 dependencies, verified-at e07521b2.

## Working set

- .harness/harness/features/BUG-285-canonical-reader/BRIEF.md
- .harness/harness/features/BUG-285-canonical-reader/plan.yaml
- .harness/harness/features/BUG-285-canonical-reader/feature.json
- .harness/harness/features/BUG-285-canonical-reader/notes/research-BUG-285-canonical-reader-goalcheck-plan.md
- .harness/harness/features/BUG-285-canonical-reader/runs/2026-09-14-plan-refresh-product/digest.md

## Done when

Scope: approve the refreshed plan and begin its dependency-ordered build
Authority: brief-perspective:.harness/harness/features/BUG-285-canonical-reader/BRIEF.md#operator
Authority: approval:.harness/harness/features/BUG-285-canonical-reader/BRIEF.md#Approval
Authority: plan-task:T-09.verify
Authority: plan-task:T-01.verify
