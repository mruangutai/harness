# Pending patch ready for signature

BRIEF.md and plan.yaml are pending. One T-01 traces all four SCs and routes main-session-direct under DEC-174; no production edits, tests, smoke runs, readers, panel or goal-check were performed. Source issues: [2349]. No new hard-to-reverse design choice or decision disposition is needed.

## Scope and evidence

- Intake: /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-plan-merge-inline-empty-union-2026-11-22.md, Settled; source issue #2349 read via gh. No source-diff reconfirmation was run.
- Inspected union.py _merge_union_key, _aligned_items and _union_key_head, and regression fixture helpers in tests/integration/test-plan-merge.py. Proposal-head selection is confined to empty-base/non-empty-proposal; both keys receive independent red-first cases and decisions: [a] retains explicit exit-5 coverage.
- The literal verify runs the existing integration file and a separate scratch git repository reproduction at .harness/features/FEAT-9-x/plan.yaml. Main must run it after the fix and after merge, setting BUG2349_TOOL_ROOT to the corresponding checkout and retaining both receipts. Tests alone do not settle SC-04.
- Applicable product docs/spec.md, docs/decisions.md and docs/architecture.md do not exist in the assigned worktree (ls reported each missing). There is no invented guidance; settled intake supplies this bounded contract. Missing guidance question: where should future product-level CLI contracts live? Nonblocking for this settled patch.
- Governing control-plane decisions consulted: DEC-174 enforcement carve-out, DEC-182 controlled YAML plan, DEC-225 patch lane. DEC-174 takes precedence over the generic team-route example in the patch reference. The advisor-set conditions were supplied by intake; this draft adds no new advisor ruling.

## Writer and check receipts

Control-plane plan-merge.py apply seeded the absent plan from stdin without an approval mapping and emitted APPLIED. No APPROVAL-RESET: receipt occurred; no remote reset sync was invoked. Its post-write diagnostics reported the intentionally unsigned brief, absent Build-entry receipt and pending approval; these are signature/build-entry prerequisites, not a failed draft check.

Authorized check command:

    python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2349-plan-merge-inline-empty-union/.harness/harness/features/BUG-2349-plan-merge-inline-empty-union/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2349-plan-merge-inline-empty-union

Exact output (exit 0):

    OK T-01 2 anchor(s) resolved
    CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2349-plan-merge-inline-empty-union/.harness/harness/features/BUG-2349-plan-merge-inline-empty-union/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2349-plan-merge-inline-empty-union: 1 task(s), 2 anchor(s) resolved, 0 failure(s)

## Open questions

No blocking scope questions. Main owns signature, Build-entry receipt, implementation execution and both scratch-repro receipts. Product guidance location is a nonblocking documentation gap; no extra patch files are authorized.
