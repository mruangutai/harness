# set-lanes exact receipt

Command: `python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py set-lanes --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/plan.yaml --value-file /tmp/kaya-plan-c2-lanes.yaml`

Exit: 0

## stdout (verbatim)
```text
LANES 30 row(s) resolved at e8d868f78a6ec43880598af5c5873f5daa8ba985 -> /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/plan.yaml
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/plan.yaml
```

## stderr (verbatim)
```text
check-state --changed after /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/plan.yaml:
  VIOLATION  .harness/kaya/features/FEAT-01-kaya-platform/BRIEF.md is NOT approved — halt that flow and surface to the user.
  VIOLATION  FEAT-01-kaya-platform: cycles_used=0 but 1 FAIL run(s) recorded — the fix loop is no longer bounded.
  VIOLATION  kaya/features/FEAT-01-kaya-platform/runs/2026-10-05-3-simplify-eng/digest.md: does not satisfy the lead digest contract — a successor reads this file, not the transcript (DEC-156): /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/runs/2026-10-05-3-simplify-eng/digest.md: no fenced YAML block loads to a mapping — the durable record needs a ```yaml block holding VERDICT, DIGEST and artifact after the prose..
  VIOLATION  INV-37 FEAT-01-kaya-platform: github.sync is enabled but feature.json records no github.build_entry, so no Build entry outcome was ever recorded and the board cannot be telling the truth about this feature - run gh-sync.py open /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform.
  note       .harness/kaya/features/FEAT-01-kaya-platform/plan.yaml approval is pending — awaiting the user.
  note       FEAT-01-kaya-platform: run r-20261004-1 is referenced but its dir is absent (pruned, or never created).
  note       FEAT-01-kaya-platform: run 2026-10-04-1-product is referenced but its dir is absent (pruned, or never created).
  note       INV-23 .harness/harness/features/FEAT-02/STATE.md has illegal section(s) ['## Feature', '## Mission', '## Success criteria (binding; pm may refine wording, not weaken)', '## Constraints', '## Log'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md is 170 lines — budget is 120. It holds no history: ## Current is replaced, never appended (DEC-150).
  note       INV-23 .harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md has illegal section(s) ['## Landed', '## Two rulings LANDED, 2026-08-03 — both were mine to raise, neither mine to decide', '## Carried forward', '## Backlog nit — not fixed here', '## Cost'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-43-code-risk-grading/STATE.md is 153 lines — budget is 120. It holds no history: ## Current is replaced, never appended (DEC-150).
  note       INV-23 .harness/harness/features/FEAT-43-code-risk-grading/STATE.md has illegal section(s) ['## Cycle 29 — the origin/main reconciliation and the count-predicate defect', '## Cycle 28 — the crash class, CLOSED', '## Cycle 27 — the CI blocker, and what fixing it uncovered'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-59-proportional-flow/STATE.md has illegal section(s) ['## Open questions', '## Pointers'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
```
