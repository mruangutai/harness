# FAIL — T-01 exceeds the mandatory production complexity bar

Reviewed `926383aef86ee505d2909c291ef4ab672b8ea09b..0646be2354b49c46e7a7b0acc5f15eff84cf5d19`; clean tracked working tree; no `[harness:human]` commits. No tests/builds/linters/formatters executed. Ran only the required pinned Python risk grader: exit 1, code_grade **fail**.

## Stage 1 — specification

- SC-01/SC-03 inspection: `.claude/skills/harness/bin/plan_merge/check.py:196-228` delegates exactly `(resolved_plan, findings, root, routes.manifest_root)`, before `_check_all`; each VIOLATION becomes a complete FAIL line and contributes separately to the summary. None exits 5. Existing anchor/trace/route checks remain; shared processor is unchanged.
- SC-02/SC-05: `.omp/extensions/harness-hooks.ts:1224-1232,1331-1335` ties exact context to successful schema revision, preserves refusal priority, and does not disclose it on bash revisions. `tests/unit/omp-hooks.test.ts:1647-1683` binds batch/flat revised inputs to exact context and scout no-note cases. Red hook receipt shows actual missing-note failures.
- SC-04: `tests/integration/test-plan-merge.py:3043-3048,3110-3234` exercises real budget/status/routing rules, valid acceptance, target isolation, duplicate-id refusal and sentinel delegation/root arguments. Red-plan receipt `:374-423` shows real baseline acceptances/missing shared messages, not fixture-load errors; the sentinel correctly observes no processor calls on baseline.
- SC-06: `tests/integration/test-check-skill-weight.py:127-148` executes the actual CLI, parses JSON and checks all required report values plus plain output. `red-skill-weight.txt:16-29` identifies the new regression and missing-json NameError; the green receipt reports eight passing tests. Provenance metadata is incomplete (below).
- No copied rule predicates or new source ownership. Product `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` are absent; none substituted. No build-lead amendments/developer receipt was present among pinned feature artifacts.

## Stage 2 — ranked findings

1. **high · substance · T-01** — `plan_merge/check.py:210`, `cmd_check`: grader reports cyclomatic **4**, cognitive **6**, ABC **20.9**, grade **3**, production bar **4**, driver **ABC**, `SEVERITY: high`. The new orchestration pushes this changed function below the mandatory maintainability gate; the pinned review therefore fails even though inspected behavior is correct. Remedy: simplify the orchestration to meet the bar without weakening ordering, failure counting or delegation.
2. **med · substance · T-01** — `tests/integration/test-plan-merge.py:3123`, `case_2239_check_runs_ci_per_plan_route_gate`: cyclomatic 7, cognitive 6, ABC 29.8, grade 2 (ABC driver), test bar 3. Reason for retaining: one fixture lifecycle deliberately contrasts rejected and accepted plans and target isolation; repetitive assertions/setup drive the score, not deeply nested logic. Advisory only.
3. **med · substance · T-01** — `tests/integration/test-plan-merge.py:3176`, `case_2239_check_delegates_to_the_shared_processor_with_its_roots`: cyclomatic 7, cognitive 6, ABC 33.4, grade 2 (ABC driver), test bar 3. Reason for retaining: one scoped spy and finally block compare Harness/served-root contracts while restoring module/environment state; splitting would obscure shared-state cleanup. Advisory only.
4. **low · form · T-01 / SC-06** — `notes/receipts/red-skill-weight.txt:1` and `green-verify.txt:1`: output-only records omit the full command, exact base/fix subject identity and explicit exit required by SC-06. Their output demonstrates the intended defect, but cannot independently establish the immutable subject. Remedy: append authentic execution provenance from the existing record; do not invent it or replace red with a narrative claim. QA notified; not a code re-gate.

## Open question — unmapped scope

The pinned diff also deletes `BUG-2171-task-structured/backlog-issues.json:1`, removes its operator judgement at `feature.json:189`, and changes `plan.yaml:7` from done to review. No SC/D or T-01 authorizes those foreign-record changes. Operator recommendation: restore those three paths to BASE or explicitly authorize their scope; do not silently bind them to T-01. Lead notified. No source changes made.

## Principles applied

- Delete First: prefer simplifying the existing check orchestration over adding speculative interfaces solely to satisfy a metric; retain the existing shared rule processor as the behavioral authority.

Checks for QA: signed T-01 four-command verify. After any repair, rerun the pinned Python grader; tests alone cannot clear its high finding.
