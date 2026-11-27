# BUG-2565 build receipt: main-session-direct (DEC-174)

Every task in this plan is `execution_mode: main-session-direct`. The main session built each one in
the product checkout, on branch `feat/BUG-2565-digest-frontmatter-contract`, and dispatched no
engineering lead. Test-first order applied to the `logic`/`bugfix` tasks: the tests were written
first and observed failing (RED) before the production change. `docs` work is exempt.

| Task | Commit(s) | Verify result |
|---|---|---|
| T-01 probe: does a hook-refused yield reach the parent? | `7c8b99a0` | `probe receipt ok` |
| T-02 fail-closed yield, schema-control refusal removed | `c68f4af7`, type fix after it | bun 240 pass / 0 fail; typecheck PASS; greps 0; dispatch-guard 426/426 |
| T-03 Python projection + generator | `5acda291` | all cases PASS; 16/16 `parity ok` against the 104252db TypeScript loader |
| T-04 generate all 16 agents, `task.structured` off, drift gate | `84e3b617` | `OMP port surface: ok`; 39/39 cases; check-skill-weight exit 0 |
| T-05 live probe of the generated frontmatter | `caccc607` | `binding receipt ok` |
| T-06 docs and decision amendments | `5385422f` | `decisions ok`, exit 0 |
| SIMPLIFY apply | `7995f460` | test-digest-projection PASS; test-check-omp-port 39/39; port gate ok; `gen-agent-output.py --check` ok |

## RED evidence

- **T-02.** Before the hook change, the rewritten `tests/unit/omp-hooks.test.ts` failed 9 tests:
  - the six validator-failure classes (one parameterised test), which expected the D-02 refusal and got a passing yield;
  - the data-less `type: result` yield, which the old hook returned `undefined` for;
  - the six SC-03 dispatch witnesses (`flat-output-only` … `batch-both-scout`), which the old hook refused or revised;
  - the unavailable dispatch-guard case, which expected an unrevised input.
- **T-03.** `digest_projection.py` was first written ahead of its test. That draft was deleted, the
  tests in `tests/unit/test-digest-projection.py` were written, and RED showed 42 failures
  (module absent) before the module was written again.
- **T-04.** Before the gate change:
  - `check-omp-port.py` passed the schema-drift fixture (exit 0, `OMP port surface: ok`);
  - it failed the `task.structured`-absent fixture;
  - `python3 -c 'print({"a": False} == {"a": 0})'` printed `True`, which is why `typed_equal` exists.
- **T-01, T-05.** These are probes, with no production code. Their receipts are
  `research-yield-refusal-probe.md` and `research-frontmatter-binding-probe.md`.
- **T-06.** `docs`, exempt.

## SIMPLIFY pass

The skill's four reader dispatches go to the engineering squad. Under DEC-174 the main session may
not dispatch `harness-eng-lead`, so the main session ran the four angles itself, read-only first,
over the code diff `104252db..5385422f`:

- **reuse.** Finding: the root-relative path `.claude/skills/harness/schemas/digest` was spelled at
  `gen-agent-output.py:56` and `check-omp-port.py:178`. The cost: two spellings to move in
  lockstep, and this directory has moved once before. Applied: `digest_projection.SCHEMA_RELPATH`.
- **simplification.** Empty. `typed_equal` closes a measured bool/int equality hole, and
  `--check` is part of the signed T-03 spec.
- **efficiency.** Empty. `check-omp-port.py` measured 0.2 s and is on no hook path.
- **altitude.** Leave. The validator-unavailable refusal sits in the yield phase, the one home D-02
  names, and the projection sits beside `digest_schema.py`.

## Known residual for validation

The dispatching main-session process loaded the pre-change `harness-hooks.ts` and keeps enforcing
it until omp restarts. That stale-process class is BUG-2566's subject.
