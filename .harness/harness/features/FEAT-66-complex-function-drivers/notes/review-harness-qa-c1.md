# QA matrix gate — FEAT-66, review pin `b635ec5f61ee29bf280c99f5b6182520c99a0487`

```yaml
VERDICT: PASS
DIGEST:
  headline: "T-01's cross_module unit and integration matrix is green at b635ec5f, with both automated SC fail-first requirements credibly discharged."
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit", named_tests: 42 }
    - { kind: integration, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind integration", named_tests: 70 }
  coverage_gaps: []
  sc_evidence:
    - { id: SC-01, test: "plan.yaml:84 inline code_grade assertion; clean-pin-byte-receipts.md:45-56" }
    - { id: SC-02, test: "clean-pin-byte-receipts.md:11-42 (11 owning suites, baseline-to-pin byte comparison with D-09 normalization)" }
  fail_first:
    - { sc: SC-01, evidence: "red-first-receipts.md:30-40; clean-pin-byte-receipts.md:45-56 — the plan-inline assertion exits 1 at baseline 35c39f02 (all three drivers grade 1) and 0 at implementation pin f882dc3e; f882dc3e..b635ec5f changes no production/test bytes." }
    - { sc: SC-02, evidence: "BRIEF.md:18-21 and answers-validate-validator.md:5 approve baseline-vs-pin byte comparison as the fail-first equivalent; clean-pin-byte-receipts.md:11-42 records 11/11 green comparisons and exact D-09 checkout-root-only raw lines, which build-divergences.md:27 records as operator-ruled." }
  open_questions: []
  files_touched: [.harness/harness/features/FEAT-66-complex-function-drivers/notes/review-harness-qa-c1.md]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-66-complex-function-drivers/.harness/harness/features/FEAT-66-complex-function-drivers/notes/review-harness-qa-c1.md
```

## Matrix evidence

T-01 is `cross_module` (`plan.yaml:35-39`), so `.harness/harness.json:174-178` requires both active kinds. The exact-pin detached checkout ran the configured commands with `HARNESS_AGENT_TYPE` unset to prevent the documented environment-sensitive false failure:

| Kind | Command | Discovery | Outcome |
|---|---|---:|---|
| unit | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit` | 42 files | exit 0; pool completed in 23.12s |
| integration | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind integration` | 70 files | exit 0; pool completed in 119.90s |

The runner maps those kinds to `tests/unit/test-*.py` and `tests/integration/test-*.py` (`run-unit-tests.py:89-106,134-160`), and both discovery counts are non-zero.

## Fail-first audit

- **SC-01:** credible natural red/green evidence. The retained receipt identifies the plan-inline grade assertion as the sole lock, records its baseline exit 1 and three grade-1 drivers, and records the green pin run (`red-first-receipts.md:30-40`; `clean-pin-byte-receipts.md:45-56`). The former permanent `tests/unit/test-driver-grades.py` is absent at this pin. History places the temporary red lock at `abe0d43a` before production commits and its removal at `f882dc3e`.
- **SC-02:** no synthetic red is required: the approved BRIEF equivalence governs (`BRIEF.md:18-21`; `answers-validate-validator.md:5`). The receipt compares all 11 named owning suites, including exit status and stdout/stderr hashes; its only three raw changes are checkout-root path lines exactly ledgered and ruled as D-09 (`clean-pin-byte-receipts.md:11-42`; `build-divergences.md:27`).

## Independent c0 re-grade

MF-01, MF-03, MF-04, MF-05, and MF-06 are closed as recorded in the digest. I independently confirmed the D-09 exact-line/ruling evidence, absent second lock, removed stale `validate` exemption, approved SC-02 equivalence, and configured `cross_module` selection. D-02's amended built form is present: `_merge_keys` delegates key-ordered six-list folding to `_fold_merge_rows` (`plan-merge.py:992-1020`), matching the operator ruling (`answers-validate-validator.md:8`). No surviving finding has a concrete failure scenario.
