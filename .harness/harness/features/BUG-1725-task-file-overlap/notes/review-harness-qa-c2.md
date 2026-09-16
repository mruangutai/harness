# QA cycle-2 gate — BUG-1725 T-01

Pinned review: `708dcc4c0776136fb0addecbf3d60af3dd56eca6`. This note assesses only that immutable tree in detached worktree `qa-BUG1725-c2-pin`, never later feature `HEAD`.

```yaml
VERDICT: PASS
DIGEST:
  headline: "PASS at 708dcc4c0776136fb0addecbf3d60af3dd56eca6: unit and integration matrix are green, and the amended SC-02 fail-first assertion discriminates."
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit", exit_status: 0, named_tests: 112 }
    - { kind: integration, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind integration", exit_status: 0, named_tests: 1 }
  coverage_gaps: []
  sc_evidence:
    - { id: SC-01, test: "tests/integration/test-plan-merge.py:2978-2985 (case_bug1725_check_names_files_shared_by_tasks)" }
    - { id: SC-02, test: "tests/integration/test-plan-merge.py:2976-2977,3001-3004 (case_bug1725_check_names_files_shared_by_tasks)" }
    - { id: SC-03, test: ".claude/skills/harness-spec-driven/SKILL.md:42-47 at 708dcc4c0776136fb0addecbf3d60af3dd56eca6" }
    - { id: SC-04, test: ".claude/skills/harness/teams/plan.yaml:78-80 at 708dcc4c0776136fb0addecbf3d60af3dd56eca6" }
  fail_first:
    - { sc: SC-01, evidence: "Independent cycle-2 perturbation in detached pin worktree: replaced only plan-merge.py with pre-fix 1a1c1925171803db8ac7f7464560a3767fa902a8, then tests/integration/test-plan-merge.py exited 1 with red overlap-count, normalized-a.py, new_module.py, and overlap-beside-failure assertions; restored pin and confirmed clean path." }
    - { sc: SC-02, evidence: "Independent cycle-2 perturbation above made tests/integration/test-plan-merge.py:3003-3004 red (overlap remains reported beside existing failure), the amended SC-02's fail-first subject. The exit-0 preservation half stayed green as BRIEF.md specifies; it predates the fix and is not credited as fail-first." }
  open_questions: []
  files_touched: [".harness/harness/features/BUG-1725-task-file-overlap/notes/review-harness-qa-c2.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1725-task-file-overlap/.harness/harness/features/BUG-1725-task-file-overlap/notes/review-harness-qa-c2.md
```

## Matrix derivation

T-01 is `bugfix`. Its changed Python checker trips `touches_runtime_code`, requiring unit. Its automated acceptance evidence is the changed integration test, so the scoped integration kind is also required. No other matrix predicate applies. The direct pinned task check exits 0 with four resolved anchors and zero failures.

## Required input and immutable-path remeasurement

The validator digest's three must-fixes are each closed above. The main fix receipt identifies the amended canonical `.claude` paths and SC-02 subject; the fail-first receipt records the same four red assertions. Cycle 2 independently repeated the relevant pre-fix condition rather than accepting either receipt by assertion. The pin's ownership guidance states exclusive file ownership / one-task checklist and assigns whole-tree verify to the last touching task or validate; its scope-reader prompt asks both required shared-file questions and calls the answer a substance finding.
