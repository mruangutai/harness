# BUG-2190 — offline binding intake

Pending patch intake is ready for main's signature: BRIEF.md has six traced criteria; plan.yaml has exactly T-01, source_issues [2190], three exact file anchors and DEC-174 main-session-direct mode/agent plus three matching lane rows. Both authorized intake gates pass. No implementation, signing, panel, goal-check or production test/build/lint/format run occurred.

## Findings and bounded choices

- Root resolution returned /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2190-inv37-offline-binding. The control-plane HEAD used for lanes.resolved_at was f68c472c88071801be8f6f09d95b0f734bb4d724; this is not a production-test baseline.
- Source issue: https://github.com/mruangutai/harness/issues/2190. Required open-backlog research completed with gh issue list --repo mruangutai/harness --state open --limit 100 (exit 0); #2181 remains separate. Settled scope comes from .harness/notes/grilling-inv37-offline-binding-2026-11-07.md in the feature tree, not the backlog vote.
- Product docs/spec.md, docs/decisions.md and docs/architecture.md are absent. Product AGENTS.md, Project map, explicitly identifies .harness/harness/docs/SPEC.md and DECISIONS.md. Consulted SPEC.md section 13 and the control-plane decision index/DEC-174, DEC-182, DEC-217, DEC-220, DEC-221, DEC-225. No standalone architecture document was invented; component relationships are visible in check_state/board.py and feature_schema.py.
- Authority conflict is explicit in BRIEF Constraints and T-01.intent: DEC-221 says unavailable remote bound INV-37 verification fails closed; the assigned operator/advisor grilling authorizes the narrower offline exception only inside INV-37. Shared resolve_binding and its other consumers remain unchanged. Approval remains pending; this intake does not itself amend a signed decision.
- Product .claude/skills/harness/bin/check_state/board.py#_inv37_feature currently resolves every enabled binding before local receipt/provenance checks. feature_schema.py#_bound_mirror_binding already defines raw repository syntax and local fleet validation before remote product_config. Reuse the predicate and fleet APIs locally only when ctx.gh_ok(FACTORY_GH or gh) is false; retain full authenticated resolution and all downstream receipt predicates.
- Existing integration INV-37 home located: tests/integration/test-check-state-records.py#case_t06_build_entry_invariant. Choose the allowed dedicated sibling tests/integration/test-check-state-inv37-offline.py to avoid enlarging that branching legacy scenario. Reuse check_state_support read-only. Add tests/unit/test-check-state-inv37-offline.py for DEC-217, exercising the real gate and local validation with a minimal context and recorded remote boundaries. Small independent cases cover offline success, receipt/provenance refusal, invalid local binding, online read failures and owner/unbound preservation; no giant scenario or grade-waiver comment.
- Optional offline note: omit it. This reversible output choice needs no D-NN; the verification limitation is disclosed in the BRIEF. No new public interface, flag, resolver mode or production file beyond board.py is planned. Existing comments/new test docstrings carry the bounded explanatory update. Merge before the Kaya corpus PR.

## Authorized intake acceptance — final proposal

Both commands ran from /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2190-inv37-offline-binding and completed with exit 0. Route checking names this feature's plan, not unrelated live plans. The TASK DEVIATION is the intentional DEC-174 carve-out, not a violation.

Command:
```text
python3 /Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/check-plan-routes.py /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2190-inv37-offline-binding/.harness/harness/features/BUG-2190-inv37-offline-binding/plan.yaml
```
Stdout:
```text
MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml
DEVIATION T-01 .claude/skills/harness/bin/check_state/board.py, tests/integration/test-check-state-inv37-offline.py, tests/unit/test-check-state-inv37-offline.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
0 violation(s) across 1 plan(s)
```

Command:
```text
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2190-inv37-offline-binding/.harness/harness/features/BUG-2190-inv37-offline-binding/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2190-inv37-offline-binding
```
Stdout:
```text
OK T-01 3 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2190-inv37-offline-binding/.harness/harness/features/BUG-2190-inv37-offline-binding/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2190-inv37-offline-binding: 1 task(s), 3 anchor(s) resolved, 0 failure(s)
```

## Write receipts and remaining gate

Both plan writes used control-plane plan-merge.py apply --file <absolute feature plan> --proposal - and returned APPLIED. The second replaced only T-01.intent to include the complete unit context slice (H and fpath). Neither output contained APPROVAL-RESET:, so no gh-sync status call was made. Each invocation's automatic check-state --changed hook reported the still-unsigned BRIEF, missing Build-entry receipt, pending plan, unknown historical cycle attribution and untracked feature-set note; these are preserved as pending-intake findings, not a green repository-state claim. Main must sign before implementation; no receipt was manufactured to quiet them.

## Principles applied

- Experience First — omit an unnecessary offline note while keeping actionable local failures and authenticated failure diagnostics; the operator gets a usable tokenless check without a new control or noisy output surface.

## Open questions

None. Main alone owns the pending approvals. Production outcomes remain unverified; their test-first and final evidence belongs to implementation/QA, not this intake.
