# T-03 all-role domains amendment

## Conclusion

The operator ruling is encoded in T-02 and T-03 without broadening the feature, both tasks are `ready`, approval is `pending`, and the required plan check exits `0` with all `145` anchors resolved.

## Authority and represented contract

Authoritative ruling: `.harness/harness/features/BUG-285-canonical-reader/notes/answers-2026-09-15-t03-final-eng.md`.

- T-02 now specifies the existing public `manifest_domains(path, agent=None)` mode. With no explicit agent, its first tuple dynamically aggregates all non-read write-domain globs from every named manifest role, while its second tuple contains shared write-domain globs. Explicit-agent behavior is unchanged. Focused coverage remains in the already-listed `tests/unit/test-artifact-accessors.py` and must prove all named roles, read-only exclusion, shared-glob separation, and unchanged explicit-agent behavior. A second accessor, raw parser, exemption, hard-coded role list, and unrelated scope are forbidden.
- T-03 now requires `harness_boundary.run_dir_grant_globs` to call that existing all-role mode, combine the returned all-role and shared tuples, filter them to run-directory grant globs, and preserve established fail-open behavior on manifest-access failure. Board-lifecycle fixture repairs discovered during T-03 remain T-03 implementation work, with no separate task or scope change.
- The initial check exposed that the pre-existing partial T-03 implementation no longer contained the unchanged `gh_issue_types.py#classify_capability` symbol. On cycle-one send-back, T-03's already-listed path was narrowed through `plan-merge.py apply` to the permitted file-level `.claude/skills/harness/bin/gh_issue_types.py` anchor, preserving ownership of the evolving implementation without guessing a replacement symbol or inspecting production contents.

## Task and approval state

- T-02: `ready`, reopened with `plan-merge.py set-task-station`.
- T-03: `ready`.
- Approval: `pending`, reset by the controlled `plan-merge.py apply` mutation of `T-02.intent` and `T-03.intent`; `reset_reason` is `apply T-02, T-03`. Approval was neither edited nor signed directly.
- Existing verify commands, routes, traces, dependencies, panel history, decisions, lanes, and unrelated tasks were left unchanged. T-03's stale `gh_issue_types.py#classify_capability` anchor was the sole file-list change and is now the file-level `gh_issue_types.py` anchor.

## Plan-check evidence

Required command executed exactly:

    python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-canonical-reader/.harness/harness/features/BUG-285-canonical-reader/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-canonical-reader

Observed final result: exit `0`; `9 task(s), 145 anchor(s) resolved, 0 failure(s)`.

No task verification, tests, formatters, linters, builds, or project-wide validation were run.

## Planning-only scope

This amendment wrote only `.harness/harness/features/BUG-285-canonical-reader/plan.yaml` and this named PM research note. A name-only working-tree check showed pre-existing uncommitted production, test, state, feature, and operator-answer paths alongside the plan; none of their contents was inspected, modified, restored, or staged by this pass. Both temporary plan proposals were deleted after their controlled merges.
