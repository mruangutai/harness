# Observations - harness-pm

- 2026-08-29: FEAT-44 planning. `bun test <relative/path/to.test.ts>` treats the argument as a
  NAME FILTER, not a path: it printed "12 files were searched", ran 0 tests and exited 1. Three
  verify blocks I had drafted were therefore red for the wrong reason. The `./` prefix makes it a
  path (`bun test ./.claude/skills/harness/bin/omp-hooks.test.ts` → 24 pass / 0 fail). Positive
  control before trusting any bun-based verify.
- 2026-08-29: FEAT-44 dispatch said `test-orchestrator-playbook.py:62-65` asserts `context-watch.py`
  is PRESENT in SKILL.md. Read at source: `:62-67` asserts a wording regex is present AND that
  `context-watch.py` is ABSENT. The deletion does not break that guard; the SKILL.md rewrite breaks
  its other half. Re-reading changed which half the task had to touch.
- 2026-08-29: `run-unit-tests.sh --check-kinds` only flags an INTEGRATION_SCRIPTS name missing from
  `harness.json` integration `detect`, and a UNIT_SCRIPTS name present in it. A STALE detect entry
  naming a deleted file is invisible to it, so a deletion task needs its own grep over harness.json.
- 2026-08-29: full `run-unit-tests.sh` measured ~170s at 7ebfc9e, past the 60s a `verify:` may
  spend. Budget-honest plans put the full-suite claim on the qa gate and keep `--check-kinds`
  (0.15s) plus targeted greps in the task verify.
- 2026-08-29: `plan-merge.py apply` REFUSES (exit 8) a proposal carrying an `approval:` mapping when
  the base plan does not exist, so a first-spawn proposal must omit the block entirely — while
  `check-state.sh:159-161` flags a `plan.yaml` with no `approval:` block as bad. Every brand-new
  plan.yaml is therefore BAD until the main session inserts the pending block.
- 2026-08-29: FEAT-44 T-01 item 5 specified a state the code cannot reach — a post-domain block reason composed with the task-gated advisory. postDomain returns [] for any toolName that is not write/edit/bash (harness-hooks.ts:272), so a task result never carries a block reason. The BRIEF's own composition paragraph asserted the same impossible state and had been through a validator panel and an eng-lead architecture review without either catching it: a composition claim about two gates is only checkable by intersecting their predicates, which prose review does not do. Worth doing at plan time whenever a task asserts "X and Y co-occur" across two independently gated paths.
