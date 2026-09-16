# BRIEF — BUG-1699-lifecycle-cards lifecycle cards

## Problem

Harness records a source issue, feature parent, and task issues for a feature, but their GitHub Project cards do not move as one feature through the delivery lifecycle. The current Ready transition moves task cards only, Building does not move cards, Review omits source cards, and a plan amendment resets approval without preserving enough lifecycle context to resume the interrupted phase after reapproval. Operators therefore see stale or contradictory cards, and existing active features need a bounded repair path.

## Done when — by perspective

**operator** — Every recorded source, parent, and non-abandoned task card displays the feature's current active lifecycle station: Plan, Ready, Building, or Review.
A first signature moves the complete recorded card set to Ready; ship moves the eligible recorded card set to Done under the existing open-child rules.
A signed-plan task amendment moves the complete active card set to Plan, and reapproval resumes at Ready, Building, or Review according to whether work had started and which phase was interrupted.
One bounded reconciliation command repairs existing active features and is idempotent when repeated.

**orchestrator** — Each lifecycle mutation has one explicit caller and checkpoint: plan mutation for Plan, signature for mirror opening and resume, ordinary Build entry for Building, ordinary validation entry for Review, and must-fix re-entry for Building followed by Review at the next validation boundary after the fix run returns.
Rework cycles remain in the existing signed ruling and fix-team flow; no extra agent spawn, reader serialization, or user approval is introduced between a must-fix ruling and its next validation boundary.
GitHub writes remain best-effort outbound synchronization and never become a local workflow gate.

**code maintainer** — One projection policy defines the expected station for every recorded card and is reused by mutation, drift detection, and reconciliation.
Current abandonment, detachment, closure, open-child, authentication, and project-discovery contracts remain intact.
The governing decisions and generated decision index state the current lifecycle timing without contradictory superseded prose.

## Success criteria

- SC-01 (operator) — On initial signed approval, one focused integration scenario proves that the signature's RESUME receipt drives idempotent mirror opening before status and places the source issue, parent issue, and every recorded non-abandoned task issue in Ready; the scenario is demonstrated failing against the pre-change task-only and no-signature-open behavior before it passes.
  verify: automated        evidence: integration
- SC-02 (operator) — At ordinary Build entry, one focused integration scenario proves that the complete recorded card set moves to Building before any task dispatch; the scenario is demonstrated failing against the pre-change missing phase transition before it passes.
  verify: automated        evidence: integration
- SC-03 (operator) — At ordinary validation entry, one focused integration scenario proves that the complete recorded card set moves to Review before the validation team is dispatched; the scenario is demonstrated failing against source-card omission or a transition placed after dispatch before it passes.
  verify: automated        evidence: integration
- SC-04 (orchestrator) — Before each must-fix team run is dispatched, one focused integration scenario proves that the complete recorded card set moves to Building without adding a fix-team step or agent spawn; the scenario is demonstrated failing when the transition is absent or occurs after dispatch before it passes.
  verify: automated        evidence: integration
- SC-05 (orchestrator) — After a must-fix run returns, one focused integration scenario proves that the complete recorded card set moves to Review at the next validation boundary, without serializing the fix team's independent readers behind a lifecycle-only step; the scenario is demonstrated failing when Review is placed inside the fix-team DAG or after the next validation dispatch before it passes.
  verify: automated        evidence: integration
- SC-06 (operator) — When a task-changing verb resets an active signed plan, one focused integration scenario proves that approval becomes pending, the interrupted phase is recorded, the local feature and complete recorded card set move to Plan, and no remote status call occurs without an APPROVAL-RESET receipt; the scenario is demonstrated failing against the pre-change local-only reset before it passes.
  verify: automated        evidence: integration
- SC-07 (operator) — On reapproval, focused integration scenarios prove that the recorded progress restores the complete card set to Ready for unstarted work, Building for started or interrupted non-terminal work, and Review only when validation was interrupted and every resulting task is terminal; each outcome is demonstrated failing before it passes.
  verify: automated        evidence: integration
- SC-08 (operator) — On ship, one focused integration scenario proves that every eligible recorded source, parent, and non-abandoned task card moves to Done; the all-card assertion is demonstrated failing against a task-only or parent-only mutation before it passes.
  verify: automated        evidence: integration
- SC-09 (operator) — One focused integration scenario proves that a single board-lifecycle reconcile apply invocation repairs source, parent, and task cards for existing active features from one bounded board snapshot, continues after a card failure, skips terminal, abandoned, factory, and foreign-repository records, and performs no mutations on an immediate second invocation; the scenario is demonstrated failing against the current parent-only repair before it passes.
  verify: automated        evidence: integration
- SC-10 (orchestrator) — Focused integration scenarios prove that lifecycle synchronization is outbound-only and best effort: local progress is recorded before each remote write, an individual card failure does not prevent later cards or local workflow progress, and plan mutation performs no hidden GitHub network write; the failure-continuation and no-network assertions are demonstrated failing before they pass.
  verify: automated        evidence: integration
- SC-11 (code maintainer) — A focused unit scenario proves that the projection exposes exactly the six configured stations and assigns each active top-level phase's exact lowercase station to every unique recorded source, parent, and non-abandoned task issue; the scenario is demonstrated failing against the current per-task projection before it passes.
  verify: automated        evidence: unit
- SC-12 (code maintainer) — Focused integration scenarios prove that abandoned tasks remain excluded from active and terminal lifecycle projection and that feature abandonment retains its existing detach, backlog, and close behavior; the scenarios are demonstrated failing if active projection includes an abandoned task or abandonment semantics change before they pass.
  verify: automated        evidence: integration
- SC-13 (code maintainer) — Focused integration scenarios prove that lifecycle status and ship transitions do not directly close ordinary source, parent, or task issues and that existing workflow-owned issue closure remains unchanged; the scenarios are demonstrated failing if a new direct close is introduced before they pass.
  verify: automated        evidence: integration
- SC-14 (code maintainer) — Focused integration scenarios prove that ship retains the existing open-child hold behavior for every eligible recorded card; the scenarios are demonstrated failing if a card with an open child is moved to Done before they pass.
  verify: automated        evidence: integration
- SC-15 (code maintainer) — At the pinned review SHA, an inspector can trace one active lifecycle projection policy through status writes, INV-26 drift checks, and reconciliation, while approval reset and resume metadata remain local and every lifecycle checkpoint has exactly one documented caller.
  verify: inspection       evidence: code-review
- SC-16 (code maintainer) — At the pinned review SHA, an inspector can verify that DEC-138, DEC-203, DEC-220, DEC-224, and DEC-229 state the new current truth in place, DEC-146's project-item discovery contract remains preserved, and the generated decision index contains no stale lifecycle summary.
  verify: inspection       evidence: code-review

## Verification gaps

- none — executable behavior is covered by focused unit and integration runners, while orchestration and authority wording are verified against the pinned review SHA.

## Constraints

- DEC-138 supplies the asymmetric-truth rule: Harness is authoritative locally, GitHub synchronization is best effort, and remote failure never blocks local progress.
- DEC-146 supplies uncapped issue-to-project-item discovery and remains unchanged.
- DEC-174 blocks team delegation for main-session hooks, validators, gates, and audit/control-plane enforcement surfaces.
- DEC-188 and DEC-205 require editing current decision truth in place rather than appending contradictory amendments.
- DEC-191 blocks adding lifecycle state outside the closed feature.json key set; any temporary resume metadata belongs in plan.yaml approval metadata.
- DEC-203 supplies the exact six lowercase stations, no aliases, ship open-child handling, abandonment behavior, and bounded readback model.
- DEC-220 supplies the mirror receipt and recovery contract; mirror opening moves from Build entry to immediately after signature without renaming the existing receipt schema.
- DEC-224's one-run owning-developer/independent-reader topology remains unchanged; no lifecycle-only step or serialization is inserted.
- DEC-226 supplies the signed rework-ruling contract and blocks repeated user approval during a fix cycle.
- DEC-229 supplies task-change approval reset behavior and the sign-approval writer boundary.
- DEC-232 supplies stable path, symbol, and exact-text task anchors.
- The exact station vocabulary remains backlog, plan, ready, building, review, done.
- Outbound GitHub mutations remain best effort and must continue after individual card failures.

## Out of scope

- Adding, renaming, aliasing, or reordering GitHub Project stations.
- Making GitHub synchronization a gate for local planning, build, validation, or ship progress.
- Changing abandonment, detach, issue-closure, or ship open-child semantics.
- Inferring or changing local approval state from inbound GitHub state.
- Renaming the existing github.build_entry receipt or adding a new feature.json lifecycle key.
- Syncing GitHub issues, entering Build, signing approval, or mutating run bookkeeping as part of this planning work.

## Approval

status: pending
approved-by:
date:
