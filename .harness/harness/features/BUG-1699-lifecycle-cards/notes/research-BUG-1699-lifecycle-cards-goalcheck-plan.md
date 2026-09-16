# Plan goal-check — BUG-1699-lifecycle-cards

## Question

> does this plan deliver the operator's stated intent?

**Yes.** The applied BRIEF and plan fully specify the lifecycle contract settled in the grilling intake. This is a judgment of plan coverage, not a claim that implementation has shipped.

## Perspective grades

| Perspective | Grade | SC and task evidence | Gap |
|---|---|---|---|
| Operator | pass | SC-01–SC-03 are carried by T-01 and T-03; SC-06–SC-07 by T-01, T-02, and T-03; SC-08 by T-01; SC-09 by T-04. Together they cover post-signature mirror opening and all-card Ready, ordinary Build all-card Building, ordinary validation all-card Review, approval-reset all-card Plan, progress-based reapproval to Ready/Building/Review, ship all-card Done, and bounded one-time reconciliation of existing active features. | None. |
| Orchestrator | pass | SC-04–SC-05 are carried by T-01 and T-03; SC-10 by T-01 through T-05. They place all-card Building before each must-fix dispatch, all-card Review at the next validation boundary after the fix run returns, preserve the existing fix-team reader topology, and keep synchronization outbound-only, per-card best effort, and non-gating. | None. |
| Code maintainer | pass | SC-11–SC-12 are carried by T-01, T-04, and T-05; SC-13–SC-14 by T-01 and T-05; SC-15 by T-01 through T-05; SC-16 by T-05. They centralize projection, retain exactly Backlog/Plan/Ready/Building/Review/Done, preserve abandonment and detach behavior, preserve workflow-owned issue closure, preserve ship open-child holds, and align governing decisions and their generated index. | None. |

## Settled lifecycle and preserved-contract check

- Initial signature: SC-01 and T-03 require the signature's RESUME receipt to drive idempotent mirror opening before status; T-01 projects the source, parent, and every non-abandoned task card to Ready.
- Ordinary Build: SC-02 and T-03 place the complete card set in Building before task dispatch, using T-01's shared projection.
- Ordinary validation: SC-03 and T-03 place the complete card set in Review before validation dispatch.
- Must-fix rework: SC-04 and SC-05, implemented through T-01/T-03, place all cards in Building before the fix team and in Review at the next validation boundary after that run returns; D-04 and T-03 explicitly leave the independent-reader DAG unchanged.
- Approval reset and reapproval: SC-06 and SC-07 span T-01/T-02/T-03. Task-changing verbs atomically reset approval and local status to Plan, the explicit APPROVAL-RESET caller mirrors Plan, and transient resume metadata causes reapproval to restore Ready, Building, or Review from recorded progress and interrupted phase.
- Ship: SC-08 and T-01 keep Done ship-owned and move every eligible recorded source, parent, and non-abandoned task card.
- Existing active features: SC-09 and T-04 define one bounded `board_lifecycle.py reconcile --apply` fleet repair, continuing after per-card failures and becoming mutation-free on immediate repetition.
- Synchronization authority and failure posture: SC-10 plus T-01–T-05 keep GitHub outbound-only and best effort, record local progress before remote writes, continue after individual card failures, and forbid a hidden network write from plan mutation.
- Vocabulary and terminal contracts: SC-11–SC-14 plus T-01/T-04/T-05 preserve the exact six stations, exclude abandoned tasks, retain feature abandonment/detach behavior, leave ordinary issue closure workflow-owned, and retain open-child holds before Done.

## Panel and signature state

The recorded panel findings have been applied even though their historical entries remain `disposition: open` for signature routing: the former compound checkpoints are now independently tagged as SC-01 through SC-16; T-03 now requires executable receipt/order mutations in the focused orchestration runner; and the proposed lifecycle-only fix-DAG step was removed in favor of existing orchestrator checkpoints. The applied c2 scope review records no remaining finding.

Approval remains pending in both authorities: `BRIEF.md` says `Status: pending`, and `plan.yaml` says `approval.status: pending`. The plan therefore delivers the complete stated intent as an approval-ready specification without claiming operator signature or implementation completion.
