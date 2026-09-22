# Research — FEAT-61-control-plane-consolidation

Feature: FEAT-61-control-plane-consolidation
Baseline: 066638e8acf68b47e74637006a01c8823cff939c

## Fixed scope

The grilling artifact is authoritative. Wave 1 consolidates five copied gate dependencies: station lifecycle classification, the feature checkout predicate, strict JSON parsing, run-state schema navigation, and repo-local script loading. It also removes the unread gate policy surface, adds exactly two regression locks, and documents the accepted five-file bootstrap duplication. Waves 2 and 3, message improvements, the broader sys.path prologue set, a bin-wide dead-symbol sweep, and grader expansion remain out of scope.

DEC-174 fixes execution: the main session performs every eventual source, test, config, and doctrine change directly. Harness supplies this plan, its review panel, and goal-check only.

## Fog resolved from repository and corpus evidence

1. A rejected task completes review. The station table classifies done, abandoned, and rejected as finished, and plan-merge.py _review_complete uses the strict shared is_finished predicate. DEC-203 says terminal task stations have no board column and no executable work; FEAT-1714 added rejected after the local done/abandoned set was written. Retaining the smaller set would be chronology drift rather than a distinct lifecycle rule.
2. A terminal task does not by itself prove that work started. plan-merge.py _work_started remains a named historical predicate over building, review, and done. Abandoned may occur before execution, and rejected occurs at intake; neither establishes passage through Building. The plan requires explicit tests for both exclusions and records the one-off reason beside the predicate.
3. The live plan.yaml corpus at the baseline contains only the declared station vocabulary or an omitted task status that the plan reader defaults to ready. No live plan depends on permissive False from is_active or is_finished for an empty or unknown station. The implementation task must keep a corpus sweep plus explicit empty/unknown fail-first cases.

## Consolidation seams

- factory_config.py owns one ordered row table. Rows are name, has_board_column, and lifecycle bucket. The exact rows derive MANDATED_STATIONS, TERMINAL_STATIONS, ACTIVE_STATIONS, and FINISHED_STATIONS without a second literal set. Values remain strings.
- artifact_accessors.py owns one strict_json_loads primitive and one run-step-contract accessor. Callers keep their existing domain-specific exception wording while sharing JSON duplicate/non-finite rejection and the nested run-state-schema navigation.
- harness_boundary.py owns feature_artifact_checkout_mismatch and load_repo_module. The former returns the common checkout finding while check-domain.py and bash-write-guard.py keep their different refusal channels and absorbing failure posture. The latter has explicit pre-exec sys.modules registration for the dataclass loader and otherwise propagates loader failures to each caller's existing catch.
- gate_policy.py retains only review policy loading and evaluation. qa_gate, uat, merge, SUITE_OUTCOMES, QaResult, and evaluate_qa leave code, live configuration, template configuration, example configuration, and tests together.

## Regression and record

The two lock-ins are semantic AST checks: feature-station literals outside factory_config.py, discriminated from task-status sets; and a second spec_from_file_location call for a repo-local bin path. Each check needs a live-tree pass and a mutation that reddens it.

branch-create-gate.py, gh-close-gate.py, merge-gate.py, plan-sign-gate.py, and run-unit-tests.py retain their bootstrap prologues. Each receives a comment naming the other four. A new decision records that none can import a shared helper before it establishes the trusted bin path. The glossary gains the lifecycle bucket meanings.

The open GitHub backlog at the baseline contains no ticket that this feature implements, so source_issues remains empty.
