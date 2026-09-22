# T-05 files-field amendment

```yaml
VERDICT: PASS
DIGEST:
  headline: T-05 now names only the OMP host source and its policy test
  feasibility: clear
  surface: S
  flags: []
  recommend: proceed
  tasks: 1
  decisions: 0
  needs_approval: false
  risk: low
  cycles_used: 0
  sc_status: []
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-1821-ui-verification-lane/plan.yaml
    - .harness/harness/features/FEAT-1821-ui-verification-lane/feature.json
    - .harness/harness/features/FEAT-1821-ui-verification-lane/notes/research-amend-product-t05-anchor.md
  expertise_update: []
  amendments:
    - { task: T-05, field: files, was: [.omp/agents/harness-ui-reviewer.md, .claude/agents/harness-ui-reviewer.md, tests/unit/test-ui-reviewer-policy.py], now: [.omp/agents/harness-ui-reviewer.md, tests/unit/test-ui-reviewer-policy.py], reason: "DEC-233: OMP is the sole host and the generated Claude agent path no longer exists." }
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/research-amend-product-t05-anchor.md
```

## Evidence

- Baseline T-05.files matched the ordered three-path `was` list.
- `record-amendments` emitted `AMENDED T-05.files judgement=amendment` and applied only plan.yaml and feature.json.
- T-05.files is exactly `[.omp/agents/harness-ui-reviewer.md, tests/unit/test-ui-reviewer-policy.py]`; its verify, intent, dependencies, status, traces, and every other field are unchanged.
- The plan byte diff is confined to T-05.files. The approval mapping remains byte-for-byte identical and approved.
- feature.json changed only by one appended `amendment` judgement for `T-05.files` with the DEC-233 reason; cycles and rework state are unchanged.
- The required scoped `plan-merge.py check` exited 0 with 26 resolved anchors and zero failures. Main confirmed 26 is the correct post-amendment total; 27 was the pre-amendment count.
- The unchanged T-05 task verify was intentionally not run.
