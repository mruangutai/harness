# Research — BUG-1699 lifecycle cards

## Research frame

- Baseline: `c280792f2719145a1a41fb3df12075fdb3eebd40`.
- Intake: `.harness/notes/grilling-bug-1699-lifecycle-cards-2026-09-15.md`, sourced from issue #1699. Issue #1675 is the historical approval-reset defect; the current plan merger now performs the reset but does not preserve lifecycle resume context.
- Configuration: GitHub sync is enabled for `mruangutai/harness`, Project 3, field `Status`. The only station values are `backlog`, `plan`, `ready`, `building`, `review`, and `done`.
- Scope is outbound board lifecycle projection only. Inbound GitHub state is not approval truth.

## Lifecycle mutation sites and timing

| Phase | Current code path | Current board effect | Required timing and complete effect |
|---|---|---|---|
| Plan | `plan-merge.py` resets an approved plan after task changes | Approval becomes pending locally; cards remain at their previous stations | In the same locked task mutation, retain transient resume context and set the local feature to Plan. The PM caller reacts to the reset receipt by invoking `gh-sync.py status … plan`, which attempts every recorded source, parent, and non-abandoned task card. |
| Ready | `plan-merge.py sign-approval`, then plan/patch command invokes `gh-sync.py status … ready` | Signature does not open the mirror; Ready status targets task issues only | Immediately after signature, the main session invokes idempotent `gh-sync.py open` and then `gh-sync.py status` with the emitted resume station. Initial signatures resume Ready and affect the entire recorded card set. |
| Building | `harness` skill Build entry invokes `gh-sync.py open`; `start-task` moves an individual task and derived parent | Top-level Building is recorded locally without a complete board transition | Build entry invokes `gh-sync.py status … building` after the signature-created mirror receipt exists. Every recorded card becomes Building. `start-task` remains an idempotent per-task prerequisite/receipt path, not a competing feature-phase policy. |
| Review | Build phase invokes `gh-sync.py status … review` after execution | Parent and task cards move; source cards do not | Validation entry moves the complete recorded set to Review. In a must-fix cycle, the orchestrator moves all cards to Building before the fix team, and an intermediate dev-ops team step moves all cards to Review after the developer and before readers. |
| Done | `gh-sync.py ship` | Eligible task, source, and parent issues move to Done, with open-child skips | Preserve this sole Done writer and its existing open-child, close, best-effort, and bounded-readback behavior. |
| Abandoned | `gh-sync.py abandon` | Existing Backlog/detach/close behavior | Preserve unchanged; abandoned task cards are not projected as active feature cards. |

The direct runtime concentration is `.claude/skills/harness/bin/gh-sync.py#cmd_status`: its Ready branch currently moves only tasks, its Building branch performs no remote writes, and its Review branch omits sources. `.claude/skills/harness/bin/gh_board.py#project` currently derives task stations individually and parent/source stations separately. Because check-state INV-26 already consumes `project`, changing this projection to a single active-feature station makes mutation, drift detection, and reconciliation share one policy rather than creating a second mapping.

## Approval reset and resume

Relevant symbols are `.claude/skills/harness/bin/plan-merge.py#_reset_approval_lines`, `#_maybe_reset_approval`, `#_signed_approval_bytes`, and `#cmd_sign_approval`. The reset currently adds `reset_at` and `reset_reason`; signing removes reset metadata but has no resume receipt.

The bounded design is:

1. For a task mutation of an active signed plan in Plan, Ready, Building, or Review, atomically set approval pending, retain `approval.resume_station`, and set top-level status to Plan.
2. Resume Ready if work had not started; resume Building for started work or an interrupted Building/Review phase with non-terminal resulting work; resume Review only when Review was interrupted and every resulting task is done or abandoned.
3. Recompute the resume target on another pending task mutation so newly added ready work cannot incorrectly return to Review.
4. Do not reopen terminal Done or Abandoned features.
5. `sign-approval` emits a machine-readable resume station and removes transient reset metadata. It performs no GitHub I/O.
6. Explicit callers perform best-effort GitHub writes: the PM sends Plan after an approval-reset receipt; the main session opens/reuses the mirror and sends the resume station after signing.

This uses `plan.yaml` approval metadata and does not extend the closed `feature.json` key set. The existing `github.build_entry` receipt name can remain stable even though creation moves earlier than Build.

## Must-fix timing

`.claude/skills/harness/teams/fix.yaml` currently places one owning developer before four independent readers in a single team run, as required by DEC-224. Splitting the fix and validation into separate user-visible runs would weaken that contract. The compatible change is an intermediate `phase-review` step routed to `harness-dev-ops`, dependent on the developer and required by every reader. It invokes the mechanical Review transition after the fix and before readers. The orchestrator invokes Building before launching the must-fix run. No extra user approval is introduced because DEC-226 keeps the signed rework ruling authoritative for the cycle.

Canonical call-site documentation includes:

- `.omp/commands/harness-plan.md` and `.omp/commands/harness-patch.md`; generated `.claude/commands/` adapters must be synchronized.
- `.claude/skills/harness/SKILL.md` and `.claude/skills/harness/references/build-phase.md` for Build/validation timing.
- `.claude/skills/harness/references/github-mirror.md` for command ownership and board semantics.
- `.claude/skills/harness-spec-driven/SKILL.md` and the plan team draft/apply prompts for reacting to `APPROVAL-RESET`.
- `.omp/agents/harness-validator-lead.md` and its generated agent adapter for fix-team orchestration.
- `.claude/skills/harness/teams/fix.yaml` for the developer-to-transition-to-reader DAG.

`tests/integration/test-plan-team.py` currently treats every non-fix fix-team member as a reader. It must recognize the dev-ops phase transition as an engineering step while preserving the owning-author versus independent-reader invariant.

## Existing-feature reconciliation

The bounded one-time entry point already exists: `.claude/skills/harness/bin/board_lifecycle.py reconcile --apply`. `_status_findings` currently compares only the parent issue with the top-level feature station, and `_apply_fix` writes only `finding.data["parent"]`.

Extend this command rather than adding a migration CLI:

- For active Plan, Ready, Building, and Review features, consume `gh_board.project(plan, github_receipt)` and emit one STATUS finding per unique mismatched recorded source, parent, or non-abandoned task issue.
- Preserve the command's single board-station snapshot, bounded reads, and per-card best-effort write behavior.
- Make STATUS repair address the finding's issue number.
- Keep Done ship-only, Abandoned exempt, factory features exempt, and foreign-repository self-skip unchanged.
- An immediate repeat must report no mutations. This makes one fleet invocation the one-time backfill while remaining a safe future repair path.

## Focused tests

- `tests/unit/test-gh-board.py`: projection set, exact station vocabulary, duplicate handling, and abandoned-task exclusion.
- `tests/integration/test-gh-sync-record.py`: current Ready/task-only and Review/parent-plus-task expectations; replace with complete-card active-phase and partial-failure expectations.
- `tests/integration/test-check-state-inv26.py`: shared projection and drift behavior.
- `tests/integration/test-gh-sync-open.py`, `test-gh-sync-start-task.py`, `test-gh-sync-ship.py`, and `test-gh-sync-abandon.py`: preserved mirror receipt, per-task idempotence, Done/open-child, and abandonment contracts.
- `tests/integration/test-plan-merge.py`: approval reset, repeated pending mutation, resume classification, terminal non-reopening, and sign receipt cleanup.
- `tests/integration/test-board-lifecycle.py`: all-card findings, apply/dry-run/idempotence, partial failures, and terminal/factory/foreign skips.
- `tests/integration/test-plan-team.py`: fix-team phase-transition placement and reader independence.
- Adapter synchronization checks cover canonical command and agent changes.

## Authorities and rulings

- DEC-138: Harness remains local authority; outbound GitHub synchronization is orchestrator-executed and best effort. Its lifecycle prose must be revised in place from task-specific timing to complete-card phase timing.
- DEC-146: issue-to-project-item discovery has no result cap and station writes remain best effort. Preserve it unchanged.
- DEC-174: main-session hooks, validators, gates, and audit/control-plane enforcement plus their tests are main-session-direct. This routes plan-merge enforcement, reconciliation, canonical command/agent/team wiring, and authority edits directly.
- DEC-188 and DEC-205: current truth replaces stale flat contradictions; revise the existing decisions rather than layering amendments.
- DEC-191: do not add a feature.json lifecycle key.
- DEC-203: supplies exact six-station vocabulary, no aliases, ship/open-child behavior, abandonment behavior, best-effort writes, and bounded readback. Revise its active lifecycle clause in place.
- DEC-220: supplies the current Build-entry mirror receipt/recovery contract. Move creation to post-signature while preserving the receipt schema and explicit recovery.
- DEC-224: preserve one-run owning-developer then independent-reader fix topology; add the mechanical transition between them.
- DEC-226: preserve signed rework rulings and no repeated user approval in a fix cycle.
- DEC-229: supplies task-change approval reset and the sole sign-approval writer; extend it with transient resume metadata and a resume receipt.
- DEC-232: every plan task uses a stable symbol or exact quoted-content anchor.

## Preserved contracts and exclusions

- No station additions, aliases, renames, or status-field schema changes.
- No synchronization gate and no inbound GitHub-to-approval inference.
- No changes to abandonment, detach, closure, or open-child rules.
- No hidden network I/O in plan mutation or signing.
- No production mutation, mirror synchronization, approval signature, Build entry, or run-bookkeeping change occurs during this planning step.

## Planning and routing conclusion

Five tasks form the shortest dependency graph: shared runtime projection and status mutation; approval reset/resume enforcement; explicit orchestration call sites and fix-team DAG; existing-feature reconciliation; then authority/index updates. Runtime GitHub behavior can route to `harness-backend-dev`. DEC-174 enforcement, audit/reconciliation, canonical orchestration surfaces, and authority updates remain main-session-direct. Documentation follows implementation so it records verified current truth rather than an aspirational variant.
