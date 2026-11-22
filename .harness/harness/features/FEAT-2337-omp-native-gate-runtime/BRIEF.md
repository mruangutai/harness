# BRIEF — FEAT-2337 omp-native gate runtime

## Problem

Every governed Bash call starts five Python gates synchronously and sequentially, costing approximately 180 ms on the measured 2026-11-22 host; an unbounded Python process can freeze OMP's event loop. An unconditional QA PASS also starts another whole-suite run inside validate-digest, duplicating QA's work instead of checking its recorded execution. These are the three operator-confirmed findings in the grilling artifact, not a wider host redesign.

## Done when — by perspective

**operator** — I can keep using OMP while a gate or helper is running, and a hung process cannot hold my session indefinitely. Refusals still protect the same commands, and an unavailable check is visible rather than mistaken for a pass.

**orchestrator** — I spend measurably less time checking a Bash call. QA's recorded suite execution can establish its PASS without another suite execution at return, and an invalid record tells QA exactly how to repair the evidence.

**code maintainer** — I have one receipt-verification implementation shared with CI, migrated standing callers and tests, and current decision and operating guidance instead of conflicting old rules.

**reader** — I can reproduce the claimed outcomes at the review pin, distinguish candidate behavior from the runtime actually validating this feature, and see discriminating failure-first evidence and test grades.

## KPIs

| KPI | Baseline | Target |
|---|---|---|
| Five-gate portion of a Bash call | Approximately 180 ms sequential on 2026-11-22; individual means 28/33/50/27/42 ms at e3e628a4, applicability rechecked at dd04e52a | Paired same-host median parallel duration at most 75% of sequential duration, using identical gates and payloads at review_sha |
| Additional whole-suite executions by candidate validate-digest for an unconditional QA PASS | One per claimed kind at dd04e52a | Zero; validate runner receipts instead |

## Success criteria

- SC-01 (operator): Every runPolicy caller, including registry, expertise injection, digest destination, dispatch, yield, post-write and lifecycle cleanup helpers, awaits asynchronous completion. Tests hold a child open while an event-loop heartbeat advances, and delayed helper answers cannot become an early authorization, release, or successful injection. The single named timeout constant in harness-hooks.ts is 30 seconds, matching HOOK_HANG_BUDGET_S; no harness.json key is introduced. QA demonstrates failing-before behavior first.
  verify: automated evidence: unit
- SC-02 (operator): Real copied gate processes that exceed the budget are killed and settle once; broad gates report visibly unavailable, matching narrow commands are refused, unrelated narrow commands remain allowed, and helpers retain their existing error/empty-output conventions. Startup failures, exit 2, structured deny, signals, malformed output, and a child ignoring graceful termination do not leave a pending hook or orphan process. Test-only shortened clocks live in fixtures, not production options; QA demonstrates failing-before behavior first.
  verify: automated evidence: integration
- SC-03 (operator): All five Bash gates start before any is allowed to finish. Results are combined in the existing declared gate order regardless of completion order: refusal outranks unavailable, all unavailable notices survive, including in refusal reasons, and unrelated commands still invoke every gate. Delayed failures and rejected promises cannot suppress another gate's result. QA demonstrates failing-before behavior first.
  verify: automated evidence: unit
- SC-04 (orchestrator): A dedicated review-pin --benchmark invocation outside all pooled/default/focused suites measures the real five-gate Bash path for ls -la and harness-backend-dev, with 3 warmups followed by 15 alternating sequential/parallel pairs in one Bun process, identical payloads/environment/cwd, and no other suite running on that host. Its parallel median is at most 0.75 times its same-pin sequential median. Evidence records every sample, both medians, ratio, host, Python/Bun versions and source SHA; 180 ms is historical context, not a portable absolute limit. Before accepting the fix, QA records a cheap failing-ratio input to the benchmark's assertion/exit wiring producing a nonzero exit; no serial-execution mutation sequence is required.
  verify: automated evidence: integration
- SC-05 (code maintainer): The shared check-integration-shards discovery and evidence validator can validate full unit and integration receipts without changing its existing integration CLI defaults. Expected top-level test-*.py files come from git at tested_commit, never manifest selections, HEAD or the working tree; exact selected/completed coverage, integer zero exits, kind and shard identity are required. Existing four-shard CI successes and refusals remain covered. QA demonstrates failing-before behavior first.
  verify: automated evidence: unit
- SC-06 (orchestrator): A candidate qa PASS with suite: pass and matrix_ok: true is accepted only with schema-1 runner receipts for every satisfied claimed kind at its validate run's runs/<run-id>/qa/manifest-<kind>.json. tested_commit equals review_sha, or descends from it with every intervening change confined to this feature's own directory; a code change followed by a revert is not ledger-only. Real-runner fixture receipts exercise exact-pin and ledger-only descendants, foreign features, divergent/older commits, malformed JSON, missing/unreadable files, red exits, missing/extra/duplicate files, wrong kinds/shards and unresolvable identities. Every invalid receipt refuses PASS and names the production --kind <kind> --shard 1/1 --manifest command; no fallback suite is launched. Non-PASS and non-QA returns retain their existing trigger behavior. QA demonstrates failing-before behavior first.
  QA can write the receipt through its authored/template manifest grant without gaining access to arbitrary run logs, state or lead digests; wrong-feature/checkout claims and unrelated roles remain refused. These grant assertions also require failing-before evidence.
  verify: automated evidence: integration
- SC-07 (operator): Receipt lookup is bound to the trusted feature, validate run and review pin, not an arbitrary digest artifact or process environment override. Existing wrong-checkout, ambiguous lookup, refusal precedence, all-persona return and claim-release regressions remain covered; migrated #919/#1756/#1883/#2253 cases assert receipt outcomes instead of obsolete subprocess stubs. Refusal diagnostics name all relevant failed/missing files rather than hiding them behind an output tail. QA demonstrates failing-before behavior first.
  verify: automated evidence: integration
- SC-08 (reader): Every new or changed Python test function in this feature grades at least 3, including the self-grading additions, enforced by tests/unit/test-code-grade.py --feat2337 against the immutable feature base and committed review tip with no new allowlist exemptions. This feature-pinned grading runs only in the explicit feature mode, never as a cumulative policy in the default suite. A grade-2 changed-test mutant fails the self-grader; QA records its red-first result. The TypeScript tests are exercised through the existing Python-to-Bun unit wrapper, not claimed as Python-graded.
  verify: automated evidence: unit
- SC-09 (code maintainer): git show <review_sha>:<path> for the task-owned decision docs shows the new receipt decision, the DEC-100 timeout clause rewritten in place, preserved DEC-174/DEC-205/DEC-234 boundaries, and a regenerated decision index with a new ruling tail of at most 30 words. The same pinned reads of task-owned role/verification/team guidance, SPEC.md and README.md describe production receipt commands, force-adding ignored receipts with the run record, refusal repair, and the unchanged CI trust backstop. No #919 full-rerun contract survives on the inventoried changed standing surfaces; historical feature records are not rewritten.
  verify: inspection
- SC-10 (reader): git show <review_sha>:<path> for the changed extension, verifier and tests establishes a clean cutover: no synchronous Python runPolicy execution, obsolete RUN_UNIT_TESTS_BIN seam, suite-rerun implementation or pooled-rerun-only parser remains; the five independent processes and their existing bootstrap/applicability boundaries remain, and the PR CI suite is not removed. The validation evidence explicitly distinguishes pre-existing host enforcement from candidate source behavior.
  verify: inspection

## Verification gaps

- typecheck has cmd: null and unresolved status; SC-01/SC-03/SC-10 do not claim static TypeScript proof. Unit Bun tests via tests/unit/test-omp-hooks.py plus real-process integration tests carry runtime evidence and pinned code review carries migration inspection. Standing issue #2257 owns the runner gap; this feature does not invent a typecheck command.
- component and ui have null unresolved runners but no browser/component interaction surface is changed; functional and eval are excluded under DEC-187. No SC rests on these kinds. Unit and integration are active runnable kinds with matching standing test paths. No UAT criterion or operator-only manual pass is required.
- This feature's own validate run intentionally uses the pre-existing installed/control-plane #919 rerun enforcement, not the new receipt hook. Candidate receipt behavior is proved by unit and real CLI integration tests from review_sha; QA records the host launcher path/version/hash and source pin separately. It must not claim that the installed hook used receipts. Candidate runner receipts are still produced and force-added with the committed validate record, so their contract is inspectable without replacing the live host mid-run. Receipt acceptance alone does not establish committed receipt availability: if main forgets the settled force-add duty, an accepted QA PASS can lack a committed inspectable receipt. Main's existing manual close-time inspection of the run record is the place to notice that omission; receipt acceptance and PR CI do not detect it. This discloses the residual, not a new gate.

## Constraints

- PRODUCT checkout and every implementation edit: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2337-omp-native-gate-runtime. docs/spec.md, docs/decisions.md and docs/architecture.md are absent at dd04e52a. This product's AGENTS.md Project map explicitly names .harness/harness/docs/SPEC.md and DECISIONS.md as its guidance; no architecture document exists. Do not invent missing guidance or silently substitute another product.
- DEC-100 SUPPLIES refusal/unavailable semantics; D-01 adds the killed 30-second timeout in place. Helpers preserve existing conventions. The timeout figure matches BUG-2253, not a shared import or new config key.
- DEC-174 BLOCKS implementation through the enforcement path under change: every task is main-session-direct, including gate tests and associated docs. Planning/review remain allowed.
- DEC-205 BLOCKS amendment appendices and number reuse; DEC-234 BLOCKS replacing the copied bootstrap prologues. Each Bash gate keeps its process and own applicability decision; TypeScript does not skip gates.
- DEC-179/DEC-232 SUPPLY literal lane resolution and symbolic/quoted anchors; DEC-182/DEC-254 SUPPLY controlled YAML writes and decision dispositions; DEC-120 reserves approvals to the operator's main session; DEC-187 supplies the per-project test-kind contract; DEC-202 supplies canonical .claude/skills authored paths with .agents/skills as discovery symlink.
- New D-02 records #919 receipt trust as a new decision, not a false amendment to DEC-209. The runner's existing --shard 1/1 --manifest schema is reused and check-integration-shards.py owns expected-file discovery. CI remains the backstop against fabricated receipts.

## Out of scope

- The suite run in CI on the PR. It stays: it is the backstop the receipt trust model relies on.
- Skipping narrow gates by the extension's applicability classifier (option B), and the one-process gate dispatcher (option C). Both were ruled out above.
- A harness.json budget key for the gate timeout.
- Findings 9–14 and the spike (Features C, D, E and F).

## Approval

status: approved
approved-by: Mike Ruangutai (delegated to fable-advisor)
date: 2026-11-22
