# FEAT-53 colour-contract scope amendment — 2026-09-22

## Conclusion

T-32 now carries the design-authorized colour predicate path and exact semantic token-reference obligations without changing its full-lane verify. The task amendment is complete, but the signed acceptance bundle is not reset: both approval fragments remain approved because they are main-session-only, and Main declined the requested resets after citing a later, conflicting rounds-3/4 ruling. No additional engineering round is authorized by this amendment.

needs_approval: true

## Authority and evidence

- DESIGN.md rows DIR-KPI-IDENTITY and DIR-STATUS-LABEL define the amended executable contract.
- notes/mockups/colour-contract-amendment-2026-09-22.md defines exactly eight KPI selector/property roles, unresolved authored token-reference ownership, the intentional shared resolved value #F58BC2, preserved neutral treatments, and unchanged projects, routes, marks, captures, and palette.
- runs/2026-09-22-t32-round2-eng/ui/results.json records ten false KPI offenders for KPI 1–3 and 5–7, eleven for KPI 4, and the false Over Budget/KPI 4 collision in both desktop projects.
- notes/receipt-harness-frontend-dev-T-32-c2.md independently identifies the wrapper/descendant contradiction and equal-resolved-colour contradiction.

## Exact plan fields changed

- T-32.files: retained all four existing entries and appended only .claude/skills/harness/bin/dashboard/client/e2e/colour-placement.e2e.spec.ts.
- T-32.intent: replaced the obsolete absolute predicate-edit ban only for DIR-KPI-IDENTITY and DIR-STATUS-LABEL; specified the exact eight selector/property roles, required unresolved winning authored references, exclusive token-reference ownership, status/KPI semantic separation despite equal #F58BC2, preserved neutral treatment and all existing lane evidence, and recorded that two authorized rounds are exhausted and another requires explicit operator authorization.
- T-32.verify: unchanged byte-for-byte. The amendment changes the predicate implementation obligations, not the required verification boundary; the complete UI lane, independent gate, committed results, WebPs, and eight trace ZIPs remain necessary to cover the two corrected checks and the six remaining red checks.
- No other task, decision, check, lane, gate, source, distribution, or predicate file was changed.

## Exact plan-merge mutation receipts

T-32.files:

    AMENDED tasks:T-32.files
    APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard/plan.yaml

T-32.intent:

    AMENDED tasks:T-32.intent
    APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard/plan.yaml

Neither task-field amendment emitted an APPROVAL-RESET receipt. The current plan-merge.py intentionally preserves approval for existing task-field amendments, so gh-sync.py status was not run. No reset receipt exists to record.

## Approval state and blocker

- plan.yaml approval.status remains approved with its stale approved_by and date fields.
- BRIEF.md Approval remains approved with stale approved-by, date, and scope fields.
- Both fragments are reserved to the main session. Main was given the exact changed fields and asked to reset both to pending and unsigned, but declined and instructed this PM to return awaiting_user because of a later conflicting rounds-3/4 ruling. This PM did not forge, revoke, or re-sign either operator-owned record.

Blocking question: Will the operator reset and sign the amended BRIEF plus plan acceptance bundle, and separately grant explicit authorization for any additional T-32 engineering round? Until both are explicit, approval is required and no additional round is authorized.

## Scoped plan check

The required scoped command ran and resolved T-32's five anchors. It exited 1 on four pre-existing, out-of-scope anchors in T-20 and T-25:

    FAIL T-20 files: .claude/commands/harness-plan.md does not exist under /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53 and neither does its directory
    FAIL T-20 files: .claude/commands/harness.md does not exist under /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53 and neither does its directory
    FAIL T-25 files: .claude/commands/harness-plan.md does not exist under /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53 and neither does its directory
    FAIL T-25 files: .claude/commands/harness-patch.md does not exist under /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53 and neither does its directory
    CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53: 32 task(s), 128 anchor(s) resolved, 4 failure(s)

The assignment forbids touching other tasks or the lane/gate framework, so T-20/T-25 were not amended. No tests, builds, formatters, linters, or project-wide validation ran.

## Principles applied

- Redesign From First Principles — replaced the obsolete colour-predicate assumption inside T-32 rather than appending a competing exception, while propagating the authority into file scope and implementation obligations.
- Outcome-Oriented Execution — retained the complete UI lane and evidence boundary rather than narrowing verification to the two amended predicates or granting an unapproved transitional engineering round.
