# T-02 RED/GREEN — tests/integration/test-harness-constraints.py

## RED — final test against a `git archive 1e0b0149` export (.omp, bin, tests) → exit 1

```
FAIL  the rule file .omp/rules/harness-constraints.md exists
      /private/tmp/feat2274-t02-base-Ky6G/.omp/rules/harness-constraints.md
FAIL  frontmatter agents is exactly ['harness-*']
      None
FAIL  frontmatter alwaysApply is exactly true
      None
ok    no project-wide sticky .omp/RULES.md was created (main keeps AGENTS.md only)
FAIL  content group 1 worktree-only work, one feature per worktree, absolute reads of other features
      missing ['.claude/worktrees/', 'only its own feature directory', 'absolute path']
FAIL  content group 2 decision discipline: search the index, open governing entries, struck decisions
      missing ['decisions-index.md', 'decisions.md', 'struck']
FAIL  content group 3 check command-verifiable claims before writing them
      missing ['command-verifiable', 'before writing']
FAIL  content group 4 no shell wait loops or self-supervision of children
      missing ['wait loop', 'supervis', 'sleep']
FAIL  content group 5 DEC-174: never execute changes through the enforcement path being changed
      missing ['dec-174', 'hooks, validators', 'gate scripts', 'enforcement path']
ok    exclusion: the obsolete GSD bullet is not carried
ok    exclusion: the commit-time check-state step is not carried
FAIL  harness-product-lead: escalation guidance present
      missing ['escalate it to the orchestrator', 'routes it to the owning lead', 'reached through its lead', 'omp refuses']
FAIL  harness-eng-lead: escalation guidance present
      missing ['escalate it to the orchestrator', 'routes it to the owning lead', 'reached through its lead', 'omp refuses']
FAIL  harness-validator-lead: escalation guidance present
      missing ['escalate it to the orchestrator', 'routes it to the owning lead', 'reached through its lead', 'omp refuses']

3 passed, 11 failed
```

The three passes are the no-RULES.md control and the two exclusions, which hold vacuously while no rule exists.

## GREEN — worktree → exit 0 in 0.06s

```
ok    the rule file .omp/rules/harness-constraints.md exists
ok    frontmatter agents is exactly ['harness-*']
ok    frontmatter alwaysApply is exactly true
ok    no project-wide sticky .omp/RULES.md was created (main keeps AGENTS.md only)
ok    content group 1 worktree-only work, one feature per worktree, absolute reads of other features
ok    content group 2 decision discipline: search the index, open governing entries, struck decisions
ok    content group 3 check command-verifiable claims before writing them
ok    content group 4 no shell wait loops or self-supervision of children
ok    content group 5 DEC-174: never execute changes through the enforcement path being changed
ok    exclusion: the obsolete GSD bullet is not carried
ok    exclusion: the commit-time check-state step is not carried
ok    harness-product-lead: escalation guidance present
ok    harness-eng-lead: escalation guidance present
ok    harness-validator-lead: escalation guidance present

14 passed, 0 failed
```

Spawns frontmatter of all three leads compared against 1e0b0149: unchanged (diff of the frontmatter block, empty).

Native delivery rests on omp's documented contract (omp://rulebook-matching-pipeline.md steps 3 and 5 and the `agents` field; omp://context-files.md on AGENTS.md exclusion); no live rule-loader session was run.
