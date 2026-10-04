# Draft ready; anchor, route and trace check passes

BRIEF.md and plan.yaml are pending approval. Seven criteria cover operator outcomes (SC-01–SC-06, T-01) and maintainer documentation (SC-07, T-01/T-02). No UAT is required. T-01 owns test-first adapter work directly under DEC-174; T-02 is the documentor-owned DEC/index task and depends on T-01. Source issues are [1016, 1570]. Approve or amend only after the lead's reader pass; this draft grants no build permission.

## Choices and evidence

- Silent lexical rewriting; absolute, tilde and leading scheme:// entries remain explicit. The exact predicate and blank/default treatment are in BRIEF.md Constraints and T-01 intent; downstream BUG-2003 write/edit URI restrictions remain unchanged.
- Resolver authority remains the ready run's feature identity plus inflight_registry.py#_feature_root_command, backed by harness_boundary.py#worktree_for_feature. The similarly named Python feature_root convenience helper swallows ambiguity; T-01 explicitly rejects using it.
- The authoritative grilling supplied the observed defect and host/tool facts; these were not re-probed. Implementation seams were inspected at registerHarnessHooks, preDomain/postDomain and the existing lifecycle/URI fixtures. Control-plane templates, team routes and live plan-merge help were used, not stale worktree CLI help. Route baseline: af2a958ab06c0d6fc026b363b59fc3147e3982f1.
- unit is active and detects the existing Bun suite via tests/unit/test-omp-hooks.py. TypeScript typecheck has no runner and is disclosed at signature; no new runner or host probe is introduced.

## Required plan-merge evidence

Command (exit 0):

```text
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths
OK T-01 2 anchor(s) resolved
OK T-02 2 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths: 2 task(s), 4 anchor(s) resolved, 0 failure(s)
```

Task-changing apply stdout (exit 0):

```text
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/plan.yaml
```

No APPROVAL-RESET: receipt was emitted; no gh-sync status call was made. Bootstrap supplied pending plan approval; the proposal contained no approval block or panel. The automatic post-write state report noted unsigned BRIEF and missing github.build_entry, plus unrelated legacy state notes: neither a signature nor a build-entry receipt was manufactured. The temporary merge proposal was removed. No builds, tests, lint, formatters, smoke runs or other verification were executed.

## Principles applied

- Redesign From First Principles — operator promises cover the complete tool surface and explicit-target safety together, rather than adding a read-only exception; one adapter task owns both production and tests.
- Experience First — silent correct checkout selection avoids recurring notice noise; ambiguous resolution remains a named refusal. No interactive prototype is needed for this adapter-only contract.

## Open coordination issue

The attempt to request the lead's four separate pre-signature simplify readers through agent://Bug1016Plan.WesternCanid was denied as filesystem agent:/Bug1016Plan.WesternCanid. The required xd://report_issue report was likewise denied as xd:/report_issue. No guard bypass was attempted. The draft/check deliverable is complete; the lead still owns the read-only reader wave, and the host owner should repair this URI-messaging rollout discrepancy.

```yaml
VERDICT: PASS
DIGEST:
  headline: Draft complete; plan anchors, routes and traces pass with approval pending.
  feasibility: clear
  surface: M
  flags: [security, main-session-direct]
  recommend: proceed
  tasks: 2
  decisions: 1
  needs_approval: true
  risk: med
  sc_status: []
  open_questions:
    - id: Q1
      question: Can the host owner restore documented agent:// messaging and xd://report_issue reporting? Both were refused as filesystem targets; the lead must receive the simplify-reader coordination through this artifact instead.
      blocking: false
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/BRIEF.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/plan.yaml
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/observations/harness-pm.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/notes/research-BUG-1016-worktree-relative-paths-draft-plan.md
```
