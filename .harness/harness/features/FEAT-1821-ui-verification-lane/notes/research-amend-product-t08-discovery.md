# T-08 discovery files-field amendment

```yaml
VERDICT: PASS
DIGEST:
  headline: T-08 owns the minimum Playwright discovery expansion required for the split browser specs
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
    - .harness/harness/features/FEAT-1821-ui-verification-lane/notes/research-amend-product-t08-discovery.md
  expertise_update: []
  amendments:
    - task: T-08
      field: files
      was:
        - .claude/skills/harness/bin/dashboard/client/feat-53.e2e.spec.ts
        - .claude/skills/harness/bin/dashboard/client/e2e/geometry.e2e.spec.ts
      now:
        - .claude/skills/harness/bin/dashboard/client/feat-53.e2e.spec.ts
        - .claude/skills/harness/bin/dashboard/client/e2e/geometry.e2e.spec.ts
        - .claude/skills/harness/bin/dashboard/client/playwright.config.ts
      reason: "Main's operator ruling: the split requires discovery of the new e2e files; T-08 is integration owner and may only expand testMatch to discover the root feat-53.e2e.spec.ts plus e2e/*.e2e.spec.ts."
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/research-amend-product-t08-discovery.md
```

## Evidence

- Baseline T-08.files matched the required ordered two-path `was` list.
- `record-amendments` emitted `AMENDED T-08.files judgement=amendment` and applied only plan.yaml and feature.json.
- T-08.files now preserves the two baseline paths in order and appends `.claude/skills/harness/bin/dashboard/client/playwright.config.ts`.
- The plan with the T-08.files block removed retained SHA-256 `a3a86022dfe8aea677d238add49afac24ab7c6c44267f1fe5db7d9cbec23aebb`, proving the byte diff is confined to that field. T-08 intent, verify, dependencies, traces, status, and all unrelated plan fields are byte-identical.
- The approval mapping retained SHA-256 `8a4d924507af56c6610a6b49ac7dd977bba6bb7fd343996c4c1bf37b1ec5940f` and remains `approved`.
- feature.json's canonical content excluding `judgements` retained SHA-256 `068748c603f026841df34e1ecf7056a34208cf6c778f6e9a929705afc0882330`; its ledger count advanced from 11 to 12 with one appended `T-08.files` amendment judgement carrying Main's reason.
- BRIEF.md retained SHA-256 `ed8edce8d3b1fed8c9c6e30e968f9277f2e4b026128dfd2dc89a1e3affe5dd2d`, so BRIEF and success criteria are unchanged.
- The scoped `plan-merge.py check` exited 0: 13 tasks, 27 anchors resolved, and 0 failures. It reported the intended T-03/T-08 Playwright config ownership overlap without gating.
- The unchanged T-08 verify was intentionally not run for this plan-only amendment; no formatter, linter, test, build, or broad validation ran.
