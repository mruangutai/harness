# FEAT-63 QA pinned matrix gate — c2

**BLOCKED — immutable review SHA `687cc78f98004aaa79e1485717490d83fd67a859`.** QA-C1-01 evidence is present, but the independent gate reports an exit-1 unit-suite execution while three direct executions of the exact assigned command exited 0. The failure cause is absent from the provided tail, so the gate cannot be passed honestly.

## Phase 1 coverage expectation

Before source access, BRIEF and T-02/T-03 required: the eight checker receipt suites (SC-01); cache/silent-path integration behavior (SC-02); typed repository-load and process-control behavior plus checker integration (SC-03); AST census, per-file ceilings, and syntax mutants (SC-04); both shared-JSON-loader reparse mutants (SC-05); and rationale inspection (SC-06). `cross_module` requires `unit` and `integration` independently for each task (`.harness/harness.json:174-178`).

## Scoped command receipts

| exact command | exit | sufficient observed output |
|---|---:|---|
| `.claude/skills/harness/bin/run-unit-tests.py --kind unit` | local exit 0; independent exit 1 | direct final re-run: `test-broad-catch-census.py`: `ALL PASS`; `test-harness-boundary.py`: `ALL PASS`; runner: `pool: 8 workers, 42 files, 9.46s wall`. Independent receipt reported `pool: 8 workers, 69 files, 90.66s wall` and exit 1 without the failing case. |
| `python3 tests/integration/test-check-state.py` | 0 | `3/3 T-07 undeclared step key cases passed.`; `ALL PASSED` |
| `python3 tests/integration/test-check-state-entry.py` | 0 | `ok - FEAT-63: gh auth status is probed exactly once per run (probes: 1; INV-30 still fired: True)` |
| `python3 tests/integration/test-check-state-plans.py` | 0 | all named plan/record checks reported `ok`, including feature-json parse and INV-24 boundary cases |
| `python3 tests/integration/test-check-state-handoff.py` | 0 | all named INV-17 and handoff-shape cases reported `ok` |
| `python3 tests/integration/test-check-state-worktrees.py` | 0 | all named worktree, INV-27, INV-29, and INV-31 cases reported `ok` |
| `python3 tests/integration/test-check-state-inv26.py` | 0 | all named board/INV-26 cases reported `ok` |
| `python3 tests/integration/test-check-state-records.py` | 0 | all named record, budget, INV-23, INV-35, and approval cases reported `ok` |
| `python3 tests/integration/test-check-state-feat59.py` | 0 | `ok - case (63.a) an unimportable feature_schema is INV-23 CANNOT RUN naming the failure`; `ok - case (63.b) the 300-line fallback is gone — nothing is graded against a guessed budget` |
| `python3 tests/integration/test-check-state-table.py` | 0 | `ALL PASSED` |
| `python3 tests/integration/test-check-plan-routes.py` | 0 | all FEAT-63 reparse/census mutants reported `PASS`; `ALL PASS` |
| `python3 tests/unit/test-harness-boundary.py` | 0 | typed load/call error, chained cause, registration restoration, and process-control assertions reported `PASS`; `ALL PASS` |
| `python3 .claude/skills/harness/bin/check-plan-routes.py --consolidation-audit` | 0 | `0 consolidation finding(s) under bin/` |
| `python3 .claude/skills/harness/bin/code-grade.py --base 804d68b8 --head 687cc78f98004aaa79e1485717490d83fd67a859` | 0 | `PASSING: 37` |

## Matrix, evidence, and receipt reconciliation

| task | required kinds | unit evidence | integration evidence | assessment |
|---|---|---|---|---|
| T-02 | unit, integration | `tests/unit/test-harness-boundary.py:554-569,572-599` exercises by-name load and `call_repo_module`, including typed failure/cause, process-control propagation, and successful result. This is a declared T-02 file and behavior-bearing coverage of its added sibling boundary. | Eight declared `test-check-state*.py` suites, notably `tests/integration/test-check-state-feat59.py:1027-1043` for INV-23 CANNOT RUN/no-300 behavior. | satisfied |
| T-03 | unit, integration | `tests/unit/test-broad-catch-census.py:48-80` directly exercises exact broad-catch counting, parse failure, zero/frozen ceilings, above/below behavior, and unlisted-file zero ceiling. | `tests/integration/test-check-plan-routes.py:2741-2802` isolates both JSON-reparse mutants and broad-catch syntax/per-file mutants. | satisfied |

The new census unit suite closes T-03. The existing boundary case closes T-02 because its declared T-02 target includes the `call_repo_module` behavior it directly invokes; it is not credited merely by label or shared file membership. QA-C1-01 is therefore closed.

`notes/red-first-receipts.md:10-27` supplies RED-at-`804d68b8` evidence for SC-01 through SC-05; `:33-41` supplies the original GREEN receipts; `:47-50` supplies the c2 T-03 unit RED (`_broad_catch_count` absent) and GREEN (`ALL PASS`). Reconciliation with `notes/build-divergences.md:73-78` is clean: only D-1's INV-23 CANNOT RUN case lines and D-2's added one-probe entry line are accepted; no other receipt change is recorded or observed in the eight scoped suite runs.

SC-06 remains inspection evidence: the c1 five-site byte/adjacency ledger in `notes/review-harness-code-reviewer-c1.md:14-24` remains applicable; the c2 product/test content is pinned by the caller at `687cc78f98004aaa79e1485717490d83fd67a859`.

Findings: none classifiable from the independent receipt. Must-fix: establish and provide the failing test/cause for the independent `unit` execution; its different 69-file discovery set prevents reconciliation with the direct 42-file runs. Open question Q1 (blocking): why did the independent runner discover 69 files and exit 1 when the same command locally discovered 42 and exited 0? Recommendation: preserve its complete output and invocation environment, then assign the resulting test failure to its source owner.

```yaml
VERDICT: BLOCKED
DIGEST:
  headline: "QA-C1-01's evidence is present, but an unreconciled independent unit-suite exit 1 blocks a PASS."
  suite: fail
  failures: 1
  matrix_ok: true
  kinds:
    - { kind: unit, state: failed, cmd: ".claude/skills/harness/bin/run-unit-tests.py --kind unit", named_tests: 42 }
    - { kind: integration, state: satisfied, cmd: "python3 tests/integration/test-check-state.py; python3 tests/integration/test-check-state-entry.py; python3 tests/integration/test-check-state-plans.py; python3 tests/integration/test-check-state-handoff.py; python3 tests/integration/test-check-state-worktrees.py; python3 tests/integration/test-check-state-inv26.py; python3 tests/integration/test-check-state-records.py; python3 tests/integration/test-check-state-feat59.py; python3 tests/integration/test-check-state-table.py; python3 tests/integration/test-check-plan-routes.py", named_tests: 10 }
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
    - { sc: SC-04, evidence: "notes/red-first-receipts.md:20-27" }
    - { sc: SC-05, evidence: "notes/red-first-receipts.md:20-22" }
  open_questions:
    - { id: Q1, question: "Why did the independent unit runner discover 69 files and exit 1 when three direct exact-command runs discovered 42 files and exited 0?", blocking: true }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-63-broad-exception-sweep/.harness/harness/features/FEAT-63-broad-exception-sweep/notes/review-harness-qa-c2.md
```
