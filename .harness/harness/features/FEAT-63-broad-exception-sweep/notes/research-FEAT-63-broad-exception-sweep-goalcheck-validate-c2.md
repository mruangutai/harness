# FEAT-63 final goal-check — validate c2

Immutable review SHA: `687cc78f98004aaa79e1485717490d83fd67a859`

## Verdict

**BLOCKED.** The BRIEF goal is satisfied: all three approved perspectives and all six success criteria are met at the immutable review SHA, and QA-C1-01 is closed. Final validation cannot pass because an independent full unit-kind run exited 1 after discovering 69 files, while three direct executions of the same assigned command discovered 42 files and exited 0; the independent receipt omitted the failing case (`notes/review-harness-qa-c2.md:3,13,41`).

## Perspective outcomes

- **operator — met:** SC-01 and SC-02 are met; the eight checker suites pass at the pin, the only accepted receipt additions are D-1 and D-2, INV-23 is CANNOT RUN rather than a 300-cycle guess, environmental failures remain quiet, and the one-probe cache behavior is exercised (`notes/review-harness-qa-c2.md:13-25,37`).
- **code maintainer — met:** SC-03 and SC-04 are met; repository loading and calls expose the typed boundary without swallowing process control, `check-state.py` has no broad catch, and the single AST census has both unit-kind function coverage and integration mutants for its per-file ceilings (`notes/review-harness-qa-c2.md:24-25,32-35`).
- **reader — met:** SC-05 and SC-06 are met; both shared JSON loaders are locked against invariant reparsing, and the five silence rationales remain byte-identical and adjacent at the pin (`notes/review-harness-qa-c2.md:23,39`; `notes/review-harness-code-reviewer-c1.md:14-24`).

## Success-criterion outcomes

| SC | status | method | evidence at `687cc78f98004aaa79e1485717490d83fd67a859` |
|---|---|---|---|
| SC-01 | met | automated | QA c2 records all eight `test-check-state*.py` suites at exit 0 (`notes/review-harness-qa-c2.md:14-23`). `tests/integration/test-check-state-feat59.py#case_feat63_inv23_import_boundary` proves INV-23 CANNOT RUN and rejects the 300 fallback. Receipt reconciliation admits only D-1/D-2 (`notes/review-harness-qa-c2.md:37`). |
| SC-02 | met | automated | `tests/integration/test-check-state-entry.py#case_feat63_gh_auth_probed_once` observes one authentication probe while INV-30 still fires (`notes/review-harness-qa-c2.md:15`). `check-state.py#Ctx.spawn`, `Ctx.gh_ok`, and `Ctx.git_top` provide the narrowed/cached boundary. The previously accepted bootstrap disclosure remains unchanged: eleven post-bootstrap calls use `Ctx.spawn`; the pre-`Ctx` root probe remains direct (`notes/build-divergences.md:82-85`). |
| SC-03 | met | automated | QA c2 records the boundary unit suite green (`notes/review-harness-qa-c2.md:24`). `tests/unit/test-harness-boundary.py#case_load_repo_module_failures` covers structured/chained causes, registration restoration, by-path/by-name load, the disclosed call boundary, success, and unchanged process-control propagation; the live consolidation audit is clean (`notes/review-harness-qa-c2.md:24-25`). |
| SC-04 | met | automated | `tests/unit/test-broad-catch-census.py:48-80` directly covers both broad syntaxes, nesting, clean/parse-failing files, frozen and zero ceilings, reductions, increases, and unlisted files. `tests/integration/test-check-plan-routes.py:2766-2802` covers checker syntax and per-file mutants. The task-specific test, integration suite, and live zero-finding audit are green (`notes/review-harness-qa-c2.md:13,23,25,33`); the unreconciled full unit-kind exit is an overall gate blocker, not evidence of a failed SC-04 assertion. |
| SC-05 | met | automated | `check-plan-routes.py#_SHARED_SOURCE_LOADERS` includes `load_feature_json` and `load_harness_json`; `tests/integration/test-check-plan-routes.py#case_feat63_reparse_lock_covers_both_json_loaders` proves each isolated reparse produces its own finding. QA records the suite green (`notes/review-harness-qa-c2.md:23,33`). |
| SC-06 | met | inspection | The c1 five-site comparison proves exact baseline bytes and adjacency at `check-state.py` for the GitHub, INV-26, INV-30, INV-24, and era-config rationales (`notes/review-harness-code-reviewer-c1.md:14-24`). The only product/test delta from c1 to this pin is the new census unit file, so that source inspection remains applicable. |

## QA-C1-01 and the product goal

QA-C1-01 was a repository test-matrix gate failure, not a failed BRIEF outcome: c1 already had behavior-level evidence sufficient to grade SC-01 through SC-06 met, but T-02 and T-03 had not each demonstrated the configured `cross_module` floor of unit plus integration. That distinction does not excuse the gate; an open QA-C1-01 would still make final validation fail even with every SC met.

At c2 the gap is closed on the tasks' declared files:

- T-02 declares `tests/unit/test-harness-boundary.py#case_load_repo_module_failures`; its by-name-load and `call_repo_module` cases directly exercise T-02 behavior at `tests/unit/test-harness-boundary.py:554-599`, while the eight declared integration suites cover the checker behavior.
- T-03 declares `tests/unit/test-broad-catch-census.py`; its direct census/ceiling cases are at `:48-80`, while `tests/integration/test-check-plan-routes.py:2741-2802` supplies the shared-loader and whole-tree mutant evidence.

The task-specific unit and integration evidence passes at the review SHA, so QA-C1-01 is **closed** without changing or weakening any success-criterion verdict (`notes/review-harness-qa-c2.md:28-35`). The contradictory full unit-kind receipt is separate: it blocks the overall validation verdict until its failing case and 69-file discovery environment are known.

## Receipt ledger reconciliation

`notes/red-first-receipts.md:10-27` retains RED evidence for SC-01 through SC-05, `:33-41` retains the original GREEN evidence, and `:47-50` adds the fix-round-2 T-03 unit RED/GREEN receipt. Against `notes/build-divergences.md:73-78`, only D-1's INV-23 CANNOT RUN case lines and D-2's one-probe entry line are accepted additions. QA c2 observed no deletion, alteration, skip, missing row, or other unruled difference across the eight suites (`notes/review-harness-qa-c2.md:37`).

## Findings

- findings: `[]` — the independent failure is unclassifiable without its failing case, so it is an open question rather than a fabricated finding.
- must_fix: preserve and provide the independent unit run's complete output and invocation environment, identify the failing test, and route that failure to its source owner.
- open_questions: `[{ id: Q1, question: "Why did the independent unit runner discover 69 files and exit 1 when three direct exact-command runs discovered 42 files and exited 0?", blocking: true, recommendation: "Preserve the complete output and invocation environment, identify the failing test, then assign it to its source owner." }]`

```yaml
VERDICT: BLOCKED
DIGEST:
  headline: All three perspectives and all six success criteria are met and QA-C1-01 is closed at 687cc78f, but an unreconciled independent full unit-kind exit 1 blocks final validation.
  feasibility: blocked
  surface: M
  flags: [cross-module, baseline-comparison, fail-first, matrix-closure, unreconciled-suite]
  recommend: halt
  tasks: 3
  decisions: 4
  needs_approval: false
  risk: med
  sc_status:
    - { id: SC-01, verdict: met, method: automated, evidence: "notes/review-harness-qa-c2.md:14-23,37; tests/integration/test-check-state-feat59.py:1027-1043" }
    - { id: SC-02, verdict: met, method: automated, evidence: "notes/review-harness-qa-c2.md:15; tests/integration/test-check-state-entry.py:683-710" }
    - { id: SC-03, verdict: met, method: automated, evidence: "notes/review-harness-qa-c2.md:24-25; tests/unit/test-harness-boundary.py:518-599" }
    - { id: SC-04, verdict: met, method: automated, evidence: "notes/review-harness-qa-c2.md:13,23,25,33; tests/unit/test-broad-catch-census.py:48-80; tests/integration/test-check-plan-routes.py:2766-2802" }
    - { id: SC-05, verdict: met, method: automated, evidence: "notes/review-harness-qa-c2.md:23,33; tests/integration/test-check-plan-routes.py:2741-2752" }
    - { id: SC-06, verdict: met, method: inspection, evidence: "notes/review-harness-code-reviewer-c1.md:14-24; notes/review-harness-qa-c2.md:39" }
  open_questions:
    - { id: Q1, question: "Why did the independent unit runner discover 69 files and exit 1 when three direct exact-command runs discovered 42 files and exited 0?", blocking: true }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-63-broad-exception-sweep/.harness/harness/features/FEAT-63-broad-exception-sweep/notes/research-FEAT-63-broad-exception-sweep-goalcheck-validate-c2.md
```
