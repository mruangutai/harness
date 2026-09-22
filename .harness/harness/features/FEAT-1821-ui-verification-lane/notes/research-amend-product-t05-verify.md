# T-05 verify-field amendment

```yaml
VERDICT: PASS
DIGEST:
  headline: T-05 verification now runs only the surviving focused policy test
  feasibility: clear
  surface: S
  flags: []
  recommend: proceed
  tasks: 1
  decisions: 0
  needs_approval: false
  risk: low
  sc_status: []
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-1821-ui-verification-lane/plan.yaml
    - .harness/harness/features/FEAT-1821-ui-verification-lane/feature.json
    - .harness/harness/features/FEAT-1821-ui-verification-lane/notes/research-amend-product-t05-verify.md
  expertise_update: []
  amendments:
    - task: T-05
      field: verify
      was: |
        python3 tests/unit/test-ui-reviewer-policy.py && python3 .claude/skills/harness/bin/sync-agent-adapters.py --root . --check
      now: |
        python3 tests/unit/test-ui-reviewer-policy.py
      reason: "DEC-233: sync-agent-adapters.py and the Claude adapter path were deleted; the focused policy test is now T-05's sole verify."
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/research-amend-product-t05-verify.md
```

## Evidence

- Baseline T-05.verify matched the required compound command byte for byte before mutation.
- The sole mutation route was the control-plane `plan-merge.py record-amendments`; it emitted `AMENDED T-05.verify judgement=amendment` and applied only plan.yaml and feature.json.
- T-05.verify is exactly `python3 tests/unit/test-ui-reviewer-policy.py`; files, intent, dependencies, status, traces, and every other task field are unchanged.
- The focused policy test exited 0 with all contract and mutant checks reporting `ok`, followed by `PASS`.
- The scoped plan check exited 0: 13 tasks, 27 anchors resolved, and 0 failures. Its pre-existing T-03/T-08 Playwright config overlap remained advisory.
- Approval remains `approved` with the original operator and 2026-09-18 date.
- feature.json contains one appended `amendment` judgement for `T-05.verify`, attributed to `harness-orchestrator`, with the exact DEC-233 reason.
- Baseline diff inspection found only the already-created `amend-product-t05-verify` PENDING run entry. Post-amendment diff added only the one-line T-05.verify replacement and the seven-line amendment judgement; no unrelated plan, task, approval, feature-state, or ledger field changed.
- This amendment completed with 0 retry cycles.
- No formatter, linter, build, project-wide test, or project-wide validation ran.
