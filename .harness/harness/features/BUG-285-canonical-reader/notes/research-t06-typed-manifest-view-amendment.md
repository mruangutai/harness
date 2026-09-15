# T-06 typed manifest view amendment

## Conclusion

The engineering recommendation resolves both T-06 check-domain raw-manifest consumers through one opt-in typed view on the existing public manifest_domains function. The semantic accessor extension and focused unit coverage belong to reopened T-02; the two consumer cutovers, classification remedies, and integration proof remain in building T-06; T-07 remains the unchanged mechanical relocation task.

## Architecture source

Source: .harness/harness/features/BUG-285-canonical-reader/runs/2026-09-15-t06-contract-eng/digest.md, dated by its run path 2026-09-15-t06-contract-eng. The digest recommends the runtime signature manifest_domains(path, agent=None, *, view=False), immutable ManifestRoleDomains and ManifestDomainsView records for view=True, strict single-read YAML behavior, and consumer-owned policy and exception handling.

## Live-plan preconditions

Before mutation, T-02 and T-06 verify strings matched the dispatch verbatim. Neither verify field was changed. T-02 was done, T-06 was building, T-07 was ready, and approval was approved. The complete T-07 task block was read before mutation for the unchanged-byte comparison.

## Legal mutations and receipts

Only control-plane plan-merge.py legal verbs changed plan.yaml:

1. apply with a narrow stdin proposal naming only T-02.intent, T-06.files, and T-06.intent.
   - REPLACED T-02.intent
   - REPLACED T-06.files
   - REPLACED T-06.intent
   - APPROVAL-RESET: the plan was approved and its task set or a task field changed; approval.status is pending until the main session signs again
   - APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-canonical-reader/.harness/harness/features/BUG-285-canonical-reader/plan.yaml
2. set-task-station with --task T-02 --station ready.
   - STATION T-02 -> ready
   - APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-canonical-reader/.harness/harness/features/BUG-285-canonical-reader/plan.yaml

## Result and scope boundaries

Post-mutation reads establish approval.status pending, T-02 ready, T-06 building, and T-07 ready. The complete post-mutation T-07 task block matches the pre-mutation block byte-for-byte. T-06 files contains tests/integration/canonical-reader-classification.json exactly once, inserted after canonical-reader-enforcement-baselines.json, while all prior entries retain their relative order. The two exact check-domain classification row identifiers each occur once in the plan and are jointly assigned in T-06 intent to artifact_accessors.manifest_domains(..., view=True), with module consumption mapped to roles and shared_write_globs and approval consumption mapped to main_session_present and main_session_writes. The already-canonical manifest_domains row remains assigned to T-07.

No BRIEF, panel, decision, lane, approval field, other task field, production file, test file, or staging state was inspected or changed. No second accessor, raw mapping, exemption, callback or query abstraction, general manifest model, or accessor-owned policy or approval grammar was introduced into the plan contract. No task verify command, test, formatter, linter, build, or project-wide validation was run.

## Plan check evidence

The sole validation command was the required control-plane plan-merge.py check against the feature worktree. It exited 0 and reported:

- T-01: 3 anchors resolved
- T-02: 13 anchors resolved
- T-03: 39 anchors resolved
- T-04: 22 anchors resolved
- T-05: 21 anchors resolved
- T-06: 28 anchors resolved
- T-07: 18 anchors resolved
- T-08: 2 anchors resolved
- T-09: 1 anchor resolved
- Total: 9 tasks, 147 anchors resolved, 0 failures
