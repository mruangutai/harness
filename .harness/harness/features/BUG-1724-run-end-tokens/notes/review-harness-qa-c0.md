# QA gate — BUG-1724-run-end-tokens

BLUF: FAIL. The sole required `unit` kind passed at immutable review SHA `77dbda525d1bede96071076e5b07cef40f3fbc06`, and the focused tests bind the requested token behaviors, but no durable fail-first evidence exists for any automated success criterion.

## Phase 1 expectations

- SC-01: a host-task-result test must prove non-negative integer aggregation once per task call, exactly one stamp before spend, bare `run-end` preservation, and measured spend/advisory use.
- SC-02: no host figure (including compatibility behavior) must cause no stamp and bare close to record `null`.
- SC-03: normal completion must use bare `run-end`, several results must aggregate once, and explicit `run-end --tokens N` must remain an override.
- SC-04: `stamp-tokens` must write only to exactly one `started_at`/unended run and refuse no-open/multiple-open input with exit 2, byte preservation, and state/id diagnostics.

## Pinned diff and matrix

- Baseline: `c280792f2719145a1a41fb3df12075fdb3eebd40`; reviewed SHA: `77dbda525d1bede96071076e5b07cef40f3fbc06`.
- Changed task-owned paths: `.omp/extensions/harness-hooks.ts`, `.claude/skills/harness/bin/feature-record.py`, `.claude/skills/harness/SKILL.md`, `tests/unit/omp-hooks.test.ts`, and `tests/unit/test-feature-record.py`. `tests/unit/test-omp-hooks.py` is task-owned but unchanged.
- T-01 is `bugfix`; its runtime-code delta fires `bugfix.when[touches_runtime_code] -> unit`. The tests-and-contract-docs-only integration predicate is false. No other matrix kind is required.
- Approved bounded command only: `python3 tests/unit/test-feature-record.py && python3 tests/unit/test-omp-hooks.py` — exit 0. Python: 45 tests OK. Bun: 74 pass, 0 fail, 155 expectations.

## Evidence binding

- SC-01: `tests/unit/omp-hooks.test.ts:1237` aggregates `135888 + 68447`, checks persisted `204335`, exactly one `stamp-tokens`, and stamp-before-`spend`; `tests/unit/test-feature-record.py:148` proves bare `run-end` preserves the stamp; `tests/unit/omp-hooks.test.ts:1104` exercises measured SPEND output.
- SC-02: `tests/unit/omp-hooks.test.ts:1251` verifies no stamp when results lack tokens and bare close records `null`; `:1264` rejects string, negative, and fractional figures.
- SC-03: `tests/unit/test-feature-record.py:185` verifies explicit `run-end --tokens 42`; `tests/unit/omp-hooks.test.ts:1237` verifies several results sum once; `.claude/skills/harness/SKILL.md:79` specifies bare normal close.
- SC-04: `tests/unit/test-feature-record.py:148` verifies sole-open write; `:161` and `:168` verify exit 2, diagnostics, and byte preservation for no-open and multi-open state.

## Finding

- reader: `harness-qa`; severity: `substantive`; kind: `substance`; task: `T-01`. Failure scenario: implementation and focused cases landed together in `d68506cfbdc5ae320eb49ad7bd4be73babf146bb`, while feature notes contain no pre-fix red receipt. A test never observed failing against the defect may not discriminate the stated regression; SC-01 through SC-04 therefore lack required fail-first proof.


```yaml
VERDICT: FAIL
DIGEST:
  headline: "The required unit gate is green, but all four automated SCs lack durable fail-first evidence, so T-01 cannot pass QA."
  review_sha: "77dbda525d1bede96071076e5b07cef40f3fbc06"
  suite: pass
  failures: 0
  matrix_ok: false
  kinds:
    - { kind: unit, state: satisfied, cmd: "python3 tests/unit/test-feature-record.py && python3 tests/unit/test-omp-hooks.py", named_tests: 119, exit: 0 }
    - { kind: integration, state: not_applicable, reason: "bugfix integration predicate fix_confined_to_tests_and_contract_docs is false; runtime code changed" }
  coverage_gaps:
    - "SC-01 fail-first receipt/red capture is absent"
    - "SC-02 fail-first receipt/red capture is absent"
    - "SC-03 fail-first receipt/red capture is absent"
    - "SC-04 fail-first receipt/red capture is absent"
  sc_evidence:
    - { id: SC-01, test: "tests/unit/omp-hooks.test.ts:1237; tests/unit/test-feature-record.py:148; tests/unit/omp-hooks.test.ts:1104" }
    - { id: SC-02, test: "tests/unit/omp-hooks.test.ts:1251; tests/unit/omp-hooks.test.ts:1264" }
    - { id: SC-03, test: "tests/unit/omp-hooks.test.ts:1237; tests/unit/test-feature-record.py:185; .claude/skills/harness/SKILL.md:79" }
    - { id: SC-04, test: "tests/unit/test-feature-record.py:148; tests/unit/test-feature-record.py:161; tests/unit/test-feature-record.py:168" }
  fail_first:
    - { sc: SC-01, evidence: "MISSING: no durable receipt or captured pre-fix red execution at the pinned review surface" }
    - { sc: SC-02, evidence: "MISSING: no durable receipt or captured pre-fix red execution at the pinned review surface" }
    - { sc: SC-03, evidence: "MISSING: no durable receipt or captured pre-fix red execution at the pinned review surface" }
    - { sc: SC-04, evidence: "MISSING: no durable receipt or captured pre-fix red execution at the pinned review surface" }
  open_questions: []
  files_touched: [".harness/harness/features/BUG-1724-run-end-tokens/notes/review-harness-qa-c0.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1724-run-end-tokens/.harness/harness/features/BUG-1724-run-end-tokens/notes/review-harness-qa-c0.md
```
