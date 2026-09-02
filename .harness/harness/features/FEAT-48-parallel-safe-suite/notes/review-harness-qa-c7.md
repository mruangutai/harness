# QA panel gate re-run — FEAT-48-parallel-safe-suite — validate c7

Independent re-run of the `test_matrix` gate at `8e7f56dc` (byte-identical to `b86ce66a`). One
`--kind all` invocation, plus the two cheap contract checks. No test, fixture or source was
authored; nothing under `.claude/skills/harness/bin/**`, `.harness/harness.json`, or
`DECISIONS.md` was touched.

```
matrix_ok: true
required_kinds: unit, integration
kinds:
  - kind: unit
    state: satisfied
  - kind: integration
    state: satisfied
  - kind: component
    state: skipped
    reason: "BRIEF `## Verification gaps`: cmd: null, none of component/ui/eval/typecheck detects
      any surface this feature touches (bash and Python gate scripts under
      .claude/skills/harness/bin/, covered by unit and integration, both of which have runners)"
  - kind: ui
    state: skipped
    reason: "same BRIEF quote as component"
  - kind: eval
    state: skipped
    reason: "same BRIEF quote; change_type never resolves to ai_behavior in this diff"
  - kind: typecheck
    state: skipped
    reason: "same BRIEF quote; not present in test_matrix for any change_type in this diff"
```

## Change-type derivation (independent)

`plan.yaml` tasks: T-01 `bugfix`, T-02 `bugfix`, T-03 `logic`, T-04 `cross_module`, T-06
`cross_module`, T-05 `docs`, T-07 `bugfix`/`abandoned` (excluded per dispatch constraint — no
implementation, not graded).

`.harness/harness.json` `test_matrix` rows, read directly:
- `bugfix.always = [unit]`, `bugfix.when = [{kind: __bug_class__, if: match_bug_class}]` — no
  bug-class taxonomy entry fires for this diff, so the `when` clause does not add a kind. Floor:
  `unit`.
- `logic.always = [unit]`.
- `cross_module.always = [unit, integration]`.
- `docs.always = []`.

Union across all six live tasks: **unit + integration**. Both `status: active` in `harness.json`
with real, non-null `cmd`s. `component`, `ui`, `eval`, `typecheck` all carry `cmd: null`; the
BRIEF's own `## Verification gaps` section states the reason and it checks out — none of their
`detect` globs match anything under `.claude/skills/harness/bin/` (the only surface this feature
touches), so soft-skip is correct, not `BLOCKED`.

This matches the segment receipt's derivation (`notes/qa-c7.md` lines 34-41) exactly, independently
re-derived from `plan.yaml` and `harness.json` rather than read off that note.

## My own runner invocations (the only panel member permitted to run it)

1. `env -u HARNESS_AGENT_TYPE bash .claude/skills/harness/bin/run-unit-tests.sh --kind all`
   → **exit 0**. `pool: 8 workers, 63 files, 45.27s wall`.
   - File-level lines: `grep -cE '^PASS [a-zA-Z_.-]+\.py$'` → **69**, `^FAIL ` → **0**, `MUTATED` →
     **0**. The 69-vs-63 gap is the six scripts that print their own summary in addition to the
     runner's line (`test-quarantine.py`, `test-plan-merge.py`, `test-panel-findings.py`,
     `test-observations-merge.py`, `test-feature-worktree.py`, `test-expertise-merge.py`, each
     appearing twice) — this is the already-ruled pre-existing duplication (dispatch item 1),
     confirmed again in this run's own log, not merely trusted from the receipt.
   - `test-suite-independence.py` block: `root /…/FEAT-48-parallel-safe-suite`, `discovered 63`,
     `ok no test mutates a path derived from the live checkout`, `PASS test-suite-independence.py`.
2. `env -u HARNESS_AGENT_TYPE bash .claude/skills/harness/bin/run-unit-tests.sh --check-kinds`
   → **exit 0**, prints `check-kinds: the script arrays and test_kinds.integration.detect agree.`,
   runs no test.
3. `env -u HARNESS_AGENT_TYPE bash .claude/skills/harness/bin/run-unit-tests.sh --kind bogus`
   → **exit 2**, prints `run-unit-tests.sh: unknown kind 'bogus' — use unit, integration or all`.

All three match REQ-06's stated contract and SC-07's literal wording exactly.

## Cross-check against `notes/qa-c7.md` (segment receipt)

**Agree:**
- `matrix_ok: true`, required kinds `unit + integration`, the four soft-skips and their BRIEF-quoted
  reasons — my independent derivation lands on the identical set.
- Exit codes and pool line shape: my `--kind all` run (45.27s) is consistent with the receipt's
  split-run figures (13.72s unit + 44.41s integration ≈ 48.09s combined by the orchestrator's own
  earlier run) and with SC-06's ≤120s bound. Small wall-time variance across separate invocations
  (45.27s here vs 48.09s/48.13s elsewhere) is expected machine noise, not a regression — all clear
  the 120s bound by a wide margin.
- The 69-vs-63 PASS-line duplication: same root cause, same six files, confirmed independently in
  my own log rather than taken on trust.
- Zero `FAIL`, zero `MUTATED` in my run — matches.
- `--check-kinds` and unknown-kind contract: matches exactly (exit 0/2, same message shapes).

**No disagreement.** I did not re-run the assertion-strength probes (`test-suite-independence.py`'s
missing self-red-proof fixtures; `test-run-pool.py`'s missing `__pycache__` leg) — those are
static/mutation-probe findings the segment already substantiated with falsification evidence
(patched `scan_file` returning `[]` producing identical exit-0 output on both a fixture and the
live tree; independent `run_pool.py --mutation-check` probing of all seven vectors). Re-deriving
them would require authoring fixtures or probes, which this gate-only dispatch prohibits — I take
them as already-ruled per the dispatch's own item 3/4, and my runner-level re-run corroborates
their premise (the suite is green, the gap is in what regression-protects it going forward, not in
today's pass/fail state).

## Findings

None new. This re-run corroborates the segment's `matrix_ok: true` and its two carried findings
(HIGH: `test-suite-independence.py` has no shipped self-red-proof; MEDIUM: `test-run-pool.py`
omits the `__pycache__`-exclusion leg) without weakening or amplifying either — both are about
regression protection going forward, not about today's gate state, and today's gate state is
green by two independent runs now (segment's and mine).
