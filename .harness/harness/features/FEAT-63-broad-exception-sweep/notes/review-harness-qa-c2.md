# FEAT-63 QA pinned matrix gate — c2

**PASS — re-return at immutable review SHA `e43c1a93c415ebb5215d28bc627a13119b95b84a`.** Fix round 3 moves jsonschema's contract-defect type to `feature_schema.SCHEMA_ERRORS`, removing the second guarded `import jsonschema` that made the earlier independent integration runner fail. Both required `cross_module` kinds and every c2 verify command exited 0 in a detached worktree at this pin.

## c2 history

The original c2 return at `687cc78f98004aaa79e1485717490d83fd67a859` was **BLOCKED**: its independent integration runner exited 1 on `tests/integration/test-harness-yaml.py::test_exactly_one_guarded_import_in_the_tree`, caused by `check-state.py`'s guarded `import jsonschema`. `notes/build-divergences.md` fix round 3 records the fix and the new pin. This re-return replaces that unreconciled result with independently measured receipts at `e43c1a93`.

## Phase 1 coverage expectation

Before source access, BRIEF and T-02/T-03 required the eight checker receipt suites (SC-01); cache/silent-path integration behavior (SC-02); typed repository-load and process-control behavior plus checker integration (SC-03); AST census, per-file ceilings, and syntax mutants (SC-04); both shared-JSON-loader reparse mutants (SC-05); and rationale inspection (SC-06). `cross_module` requires both `unit` and `integration`.

## Re-return receipts

All commands below ran from detached worktree `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/qa63` at `e43c1a93c415ebb5215d28bc627a13119b95b84a`; the requested `/tmp/qa63` destination was denied by the repository worktree guard, which requires `.claude/worktrees/`.

| exact command | exit | verbatim final observed lines |
|---|---:|---|
| `.agents/skills/harness/bin/run-unit-tests.py --kind unit` | 0 | `pool: 8 workers, 42 files, 9.44s wall`<br>`slowest: test-feature-record.py 9.23s, test-code-grade.py 2.19s, test-suite-independence.py 1.85s` |
| `.agents/skills/harness/bin/run-unit-tests.py --kind integration` | 0 | `pool: 8 workers, 69 files, 111.79s wall`<br>`slowest: test-check-plan-routes.py 70.22s, test-plan-merge.py 62.15s, test-validate-digest.py 30.06s` |
| `python3 tests/integration/test-check-state.py` | 0 | `3/3 T-07 undeclared step key cases passed.`<br>`ALL PASSED` |
| `python3 tests/integration/test-check-state-entry.py` | 0 | `ok - FEAT-63: gh auth status is probed exactly once per run (probes: 1; INV-30 still fired: True)`<br>`ok - exit code unchanged by INV-21 (a: 1, b: 1)` |
| `python3 tests/integration/test-check-state-plans.py` | 0 | `ok - case (63.a) an unimportable feature_schema is INV-23 CANNOT RUN naming the failure`<br>`ok - case (63.b) the 300-line fallback is gone — nothing is graded against a guessed budget` |
| `python3 tests/integration/test-check-state-handoff.py` | 0 | `ok - FEAT-54 unsafe target grammar remains enforced`<br>`ok - FEAT-54 unsafe approval grammar remains enforced` |
| `python3 tests/integration/test-check-state-worktrees.py` | 0 | `ok - INV-31 is SILENT when the hook is installed and executable` |
| `python3 tests/integration/test-check-state-inv26.py` | 0 | `ok - (w.1) an Abandoned feature's unapproved BRIEF raises NOTHING`<br>`ok - (w.2) the same fixture at status Plan IS reported` |
| `python3 tests/integration/test-check-state-records.py` | 0 | `ok - case (inv33.d) a pin that resolves but holds no plan at that path is silent, at a NON-TERMINAL station` |
| `python3 tests/integration/test-check-state-feat59.py` | 0 | `ok - case (63.a) an unimportable feature_schema is INV-23 CANNOT RUN naming the failure`<br>`ok - case (63.b) the 300-line fallback is gone — nothing is graded against a guessed budget` |
| `python3 tests/integration/test-check-state-table.py` | 0 | `ok - a repo-scoped row that loops features sees ALL of them without --feature (INV-24 undeclared-repo finding x2)`<br>`ALL PASSED` |
| `python3 tests/integration/test-check-plan-routes.py` | 0 | `PASS feat63_census_allowance_never_transfers_between_files`<br>`PASS feat63_census_unlisted_script_has_a_zero_ceiling`<br>`ALL PASS` |
| `python3 tests/unit/test-harness-boundary.py` | 0 | `PASS run_dir_slug_ok_empty_globs_is_false`<br>`PASS run_dir_forms_synthetic_exact`<br>`ALL PASS` |
| `python3 .agents/skills/harness/bin/check-plan-routes.py --consolidation-audit` | 0 | `0 consolidation finding(s) under bin/` |
| `python3 .agents/skills/harness/bin/code-grade.py --base 804d68b8 --head e43c1a93c415ebb5215d28bc627a13119b95b84a` | 0 | `RESULT: PASS`<br>`PASSING: 37` |

## Second re-return matrix recheck

After the gate reported an independent nonzero matrix result, I recreated the detached worktree at the same immutable pin and reran the exact unprefixed matrix commands. Both exited 0:

| exact command | exit | verbatim final observed lines |
|---|---:|---|
| `.agents/skills/harness/bin/run-unit-tests.py --kind unit` | 0 | `pool: 8 workers, 42 files, 9.35s wall`<br>`slowest: test-feature-record.py 9.14s, test-code-grade.py 2.19s, test-suite-independence.py 1.84s` |
| `.agents/skills/harness/bin/run-unit-tests.py --kind integration` | 0 | `pool: 8 workers, 69 files, 95.91s wall`<br>`slowest: test-check-plan-routes.py 54.36s, test-plan-merge.py 53.54s, test-validate-digest.py 26.88s` |

## Verifier-conflict resolution

The verifier failure was `tests/integration/test-feature-worktree.py`, a new `fix/process-gaps` test outside the immutable pin. Its local `git clone` hardlink shortcut raced under the parallel runner. Commit `b4b2b291` changes that fixture to `--no-local`; Main reports both process-gaps runners now exit 0 (69 integration files and 42 unit files). The pinned `e43c1a93` receipts above remain the c2 evidence.

## Matrix and evidence

| task | required kinds | unit evidence | integration evidence | assessment |
|---|---|---|---|---|
| T-02 | unit, integration | `tests/unit/test-harness-boundary.py:554-569,572-599` exercises typed repo-module load/call behavior, causes, process control, and restoration. | Eight `test-check-state*.py` receipt suites, including `tests/integration/test-check-state-feat59.py:1027-1043`. | satisfied |
| T-03 | unit, integration | `tests/unit/test-broad-catch-census.py:48-80` exercises exact broad-catch counting, parse failure, and ceilings. | `tests/integration/test-check-plan-routes.py:2741-2802` exercises both JSON-reparse and broad-catch mutants. | satisfied |

`notes/red-first-receipts.md:10-27,47-50` supplies fail-first evidence for automated SC-01 through SC-05. SC-06 remains inspection evidence at `notes/review-harness-code-reviewer-c1.md:14-24`.

```yaml
VERDICT: PASS
DIGEST:
  headline: "The e43c1a93 re-return passes both cross-module matrix kinds and every c2 verification command."
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.py --kind unit", named_tests: 42 }
    - { kind: integration, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.py --kind integration", named_tests: 69 }
  coverage_gaps: []
  sc_evidence:
    - { id: SC-01, test: "tests/integration/test-check-state-feat59.py:1027-1043" }
    - { id: SC-02, test: "tests/integration/test-check-state-entry.py:683-710" }
    - { id: SC-03, test: "tests/unit/test-harness-boundary.py:518-599" }
    - { id: SC-04, test: "tests/unit/test-broad-catch-census.py:48-80; tests/integration/test-check-plan-routes.py:2766-2802" }
    - { id: SC-05, test: "tests/integration/test-check-plan-routes.py:2741-2752" }
    - { id: SC-06, test: "notes/review-harness-code-reviewer-c1.md:14-24" }
  fail_first:
    - { sc: SC-01, evidence: "notes/red-first-receipts.md:13-15" }
    - { sc: SC-02, evidence: "notes/red-first-receipts.md:10-11" }
    - { sc: SC-03, evidence: "notes/red-first-receipts.md:17-18" }
    - { sc: SC-04, evidence: "notes/red-first-receipts.md:20-27,47-50" }
    - { sc: SC-05, evidence: "notes/red-first-receipts.md:20-22" }
  open_questions: []
  files_touched: [".harness/harness/features/FEAT-63-broad-exception-sweep/notes/review-harness-qa-c2.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/process-gaps/.harness/harness/features/FEAT-63-broad-exception-sweep/notes/review-harness-qa-c2.md
```
