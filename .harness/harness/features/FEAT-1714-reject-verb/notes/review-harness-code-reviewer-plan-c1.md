# Code review — FEAT-1714 plan c1

## Conclusion

FAIL. The brief matches the grilling artifact, all five SCs are live and traced, and the task graph is topological. One cutover omission makes the drafted plan internally unexecutable: T-03 deletes `factory_config.TERMINAL_MARKER`, but the plan never assigns migration of all existing `gh-sync.py` consumers of that name.

## Stage 1 — spec compliance

### F-01 — high · substance · terminal-vocabulary cutover leaves `gh-sync.py` on the deleted interface

`plan.yaml:67-96,98-128` assigns `gh-sync.py` to T-02, but T-02 only specifies the new reject command plus migration of handoff, card projection, and lifecycle auditing. T-03 then requires deletion of `TERMINAL_MARKER` while its file list and migration list omit `gh-sync.py`. The current module references the singular name at `.claude/skills/harness/bin/gh-sync.py:137,343,953,985,1150,1557,1713,1799` (among other prose sites).

Failure scenario: implement T-02 and T-03 exactly as written; when T-03 removes `factory_config.TERMINAL_MARKER`, importing or invoking `gh-sync.py` evaluates `STATION_VALUES` against a missing attribute and fails before either `reject` or the existing lifecycle commands can run. T-03's verify block does not run the gh-sync regression test, so the predecessor's once-green verification is invalidated without a task-local detector.

This violates D-01 and SC-05's clean shared-vocabulary cutover. Make one task explicitly migrate every generic terminal-state use in `gh-sync.py` to `TERMINAL_STATIONS` while retaining abandoned-only behavior as abandoned-specific, and run the gh-sync regression after the deletion.

## Stage 1 clearance

- No orphan SCs: SC-01..SC-05 each trace to at least one implementation task.
- No nonexistent traced SCs.
- Dependencies are acyclic and topological: T-01 → T-02 → T-03 → T-04 → T-05, with T-04 also correctly depending on T-01.
- The BRIEF preserves the grilling destination, settled decisions, constraints, and out-of-scope boundaries.

## Stage 2 — architecture

Subject to F-01, the proposed `TERMINAL_STATIONS` module is a deep shared vocabulary at the existing `factory_config` seam: one small interface governs many writers and readers, improving locality and avoiding respelled terminal sets. No speculative adapter is introduced. The `gh-sync.py reject` command reuses the existing GitHub lifecycle adapter and `_close_and_reseat` ordering rather than creating a parallel seam.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "The plan is correctly scoped and topological, but deletes TERMINAL_MARKER without assigning migration or post-deletion verification of gh-sync.py's live consumers."
  severity_max: high
  findings:
    - kind: substance
      scope: task
      severity: high
      reader: code-reviewer
      summary: "T-03 deletes TERMINAL_MARKER while gh-sync.py retains live references not assigned to any migration task."
      why: "Implementing the tasks literally makes gh-sync.py fail at import before reject or existing lifecycle commands can run, and T-03 does not rerun the gh-sync regression after deletion."
  must_fix:
    - "Assign migration of every generic gh-sync.py TERMINAL_MARKER consumer to TERMINAL_STATIONS, preserve abandoned-only branches as specific behavior, and verify gh-sync after the singular constant is deleted."
  spec_violations:
    - kind: omission
      path: plan.yaml
      ref: D-01
  code_grade: n_a
  reviewed: "plan:/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1714-reject-verb/.harness/harness/features/FEAT-1714-reject-verb/plan.yaml"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1714-reject-verb/.harness/harness/features/FEAT-1714-reject-verb/notes/review-harness-code-reviewer-plan-c1.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1714-reject-verb/.harness/harness/features/FEAT-1714-reject-verb/notes/review-harness-code-reviewer-plan-c1.md
```
