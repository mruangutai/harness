# PM distillation receipt

The `harness-pm` observation log is absent. Distillation requires no substitute: no replacement log was searched for or created, and assessment was limited to the three relayed candidates.

## Sources and judgments

1. Source: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/runs/plan-product/digest.md`
   - Candidate: a task activated `test:ui` before the later producer task created the script and runner.
   - Judgment: rejected. The six-spawns lesson is already captured by repository Pattern P-03: producer/consumer ordering belongs in `depends_on`, because prose and task order are invisible to the scheduler. A second rule would duplicate the same action and failure mode.
   - Layer considered: repository, because the durable mechanism is this repository's `teams/build.yaml` dependency scheduling.
2. Source: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/runs/amend-product-traces-product/digest.md`
   - Candidate: separate the main-session-direct gitignore evidence boundary from frontend-executable work and make each task's proof behavioral.
   - Judgment: rejected. The lane split is already a mandatory planning rule for work requiring two execution routes, while the behavioral-proof half duplicates existing craft Patterns P-01, P-08, and P-13. It would not change a later spawn's action beyond rules already injected.
   - Layer considered: craft for task decomposition and proof quality; the gitignore instance is repository detail and does not justify a second entry.
3. Source: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/runs/plan-product/digest.md`
   - Candidate: restore the omitted pending Approval section before goalcheck and signature.
   - Judgment: rejected. The PM brief procedure already requires the template's Approval section with `status: pending`, and repository Pattern P-07 already records pending-approval bootstrap behavior. This incident is compliance with existing procedure, not a new six-spawns rule.
   - Layer considered: craft; the rule would apply in any repository, but is already authoritative in the PM procedure.

Accepted entries by source: none.

## Counts

| Layer | Section | Before | After |
|---|---|---:|---:|
| Craft | Patterns | 12 | 12 |
| Craft | Gotchas | 15 | 15 |
| Craft | Outcomes | 1 | 1 |
| Craft | Open | 0 | 0 |
| Repository | Patterns | 15 | 15 |
| Repository | Gotchas | 15 | 15 |
| Repository | Outcomes | 10 | 10 |
| Repository | Open | 0 | 0 |

Exact Expertise ops: `[]`

Changed Expertise files: `[]`

## Squad-wide Expertise checker

Exact command:

```text
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-expertise.py /Users/molchairuangutai/GitHub/harness/.harness/expertise/
```

Exact result: exit 0. Stdout:

```text
OK   /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-ai-dev.md
OK   /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-backend-dev.md
OK   /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-code-reviewer.md
OK   /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-data-engineer.md
OK   /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-dev-ops.md
OK   /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-documentor.md
OK   /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-eng-lead.md
OK   /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-frontend-dev.md
OK   /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-orchestrator.md
OK   /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-pm.md
ADVISORY /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-pm.md:3: P-01 names '.harness/' — repository-layer candidate; rule on it (issue 340)
OK   /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-product-lead.md
OK   /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-qa.md
OK   /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-security-reviewer.md
ADVISORY /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-security-reviewer.md:19: G-01 names 'DEC-100' — repository-layer candidate; rule on it (issue 340)
OK   /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-ui-reviewer.md
OK   /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-validator-lead.md
OK   /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-visual-designer.md
```

No build, formatter, linter, test, feature validation, project-wide suite, or other checker ran. `suite: n/a`; `matrix_ok: n/a`; `reviewed: none`; `code_grade: n_a`.
