# Patch intake — FEAT-71

BLUF: The bounded removal/refactor is ready for operator signature: both artifacts are pending; one all-direct T-01 traces all five SCs. No implementation or product verification ran.

## Artifacts and merge evidence

- Brief: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-71-corpus-independence/.harness/harness/features/FEAT-71-corpus-independence/BRIEF.md — 49 lines (wc -l), all required sections, Approval pending. Operator and code maintainer perspectives; two automated SCs (unit/integration), three pinned-content inspections; no UAT requirement.
- Plan: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-71-corpus-independence/.harness/harness/features/FEAT-71-corpus-independence/plan.yaml — plan-merge.py apply exited 0 and printed APPLIED for this exact path; writer seeded approval pending. No APPROVAL-RESET receipt, therefore no remote sync.
- Authorized plan-merge.py check --file <above plan> --root /Users/molchairuangutai/GitHub/harness exited 0: OK T-01 20 anchor(s) resolved; CHECK reported 1 task, 20 anchors, 0 failures. Tool-generated changed-state feedback correctly reports unsigned BRIEF and absent build_entry; these are signature-stage prerequisites, not claimed green merge gates.

## Scope and guidance

- Binding evidence: /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-corpus-independence-2026-11-07.md, Settled/Facts/Out of scope, observed baseline c4e8bbc8. Inventory reused, not re-derived. Four survivors include this new intake.
- Contracts consulted: control-plane patch-lane.md, artifact-paths.md, plan/BRIEF templates; BUG-2141 plan shape; DEC-174 and DEC-225 entries, decision index; product CLAUDE.md, AGENTS.md Project map and SPEC index. Root resolver returned the assigned feature worktree; routing SHA is c4e8bbc87e858bb2a0320efd766c7036cbcebb8b.
- Product docs/spec.md, docs/decisions.md, docs/architecture.md are absent. AGENTS.md explicitly maps specification/decision authority to .harness/harness/docs/SPEC.md and DECISIONS.md, with BUILD.md for sequencing; no architecture substitute is invented. This is an existing-guidance disclosure, not an unresolved scope choice.
- cross_module is the configured schema vocabulary for this removal/refactor (unit + integration floor); no feature label or new public gate. Existing plan_anchors.py supports bounded glob path anchors; these cover the inventory-defined bulk deletion/record surfaces while intent explicitly prohibits unrelated changes. All source/config/skill/test/doc/expertise/record/corpus surfaces are declared main-session-direct. Main builds directly, never harness-eng-lead.

## Precise terminal merge acceptance

T-01.verify is an executable literal shell block: clone committed HEAD with --no-local/--no-hardlinks into canonical /private/tmp, require real .git directory, canonical path, matching SHA and exact survivor set; run check-state.py, validate-feature-json.py, check-decision-anchors.py, check-plan-routes.py and full run-unit-tests.py --kind all, then compare regenerated decisions index. All must exit zero with no FAIL assertions. Output is retained as notes/merge-<pin>.log; pipefail preserves failure. Task intent also requires per-command exits, baseline/new-test fail-first evidence and final green receipts. No linked owner corpus, reduced suite, assertion suppression or /tmp-symlink waiver is accepted. Review content with git show at the same review_sha; separately receipt deletion of authorized untracked records. Full suite execution belongs to main, not this intake.

## Open questions

None. Approval is still required; new public interface or unbounded diff would require escalation, not implementation under this patch.
