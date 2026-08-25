# Observations - harness-pm

- 2026-08-25: FEAT-40 — a PreToolUse:Bash hook is handed only tool_input.command (branch-create-gate.sh:47), so a gate cannot see gh calls a python script makes through subprocess. The source ticket's "environment marker gh-sync.py sets" could never have reached the gate; the correct answer was an unconditional refusal. Check the interception boundary before planning an exemption mechanism.
- 2026-08-25: FEAT-40 — the source ticket asserted #728 has no children; gh api repos/mruangutai/harness/issues/728/sub_issues returned 13. The false premise would have made the acceptance test exercise the trivial path instead of the open-child skip. Re-derive an acceptance target's own shape even when the operator states it.
- 2026-08-25: send-back c1. plan-merge.py is ADD-ONLY — it refuses (exit 7) when a proposal carries
  an existing id with different values, so folding review findings into shipped tasks has to be done
  with direct edits; the merge tool only helps for NEW D-NN/T-NN. Used it for D-10/D-11 only.
- 2026-08-25: FEAT-40's plan.yaml was written without the template's `approval:` skeleton, and
  check-state.sh reports that as a VIOLATION ("has no approval: block — cannot tell if the goal is
  signed"), distinct from the "approval is pending" note the other live plans get. pm cannot fix it:
  the mapping is the main session's and plan-merge refuses to write it. Instantiating from the
  template rather than composing the file by hand is what prevents this.
- 2026-08-25: two reviewers cited board_lifecycle.py:120 for audit's exit 4; the real site is
  cmd_audit at :906-914 and :120 is docstring prose describing reconcile. A line anchor into a file
  with a 200-line module docstring lands in the narration, not the code.
- 2026-08-25: FEAT-40 — five task verifies opened with `run-unit-tests.sh --kind all` while six unit
  scripts were already red at cc84b29 through no act of the feature; the runner cannot select scripts
  (:24-40), so the tasks were unmarkable. Remedy: a baseline set of tolerated FAIL names plus a
  per-task `PASS <owned script>` clause (D-12, T-11). The clause that matters is the owned-script one.
- 2026-08-25: FEAT-40 — T-09 verify grepped three files for absence; one of the three (harness-init/SKILL.md)
  had ZERO matches at cc84b29, so the task part that only ADDS to that file passed unconditionally.
  The intent said "all three strings are present in these files" — true of the set, false per file.
- 2026-08-25: test-check-state.py takes tens of minutes when more than one copy runs in the same tree;
  each fork of check-state.sh scans the whole repo. Never run two suites concurrently in one worktree.
- 2026-08-25 (FEAT-40): a dispatch enumerated three sites for a numeral defect; the set was four, and the miss was in plan.yaml's approval-gated decisions: block (D-07). Enumerated sites are a hypothesis about where a defect class lives. Grep the class across both artifacts before returning, and report the hit list with a disposition per hit.
