# BRIEF — FEAT-2081-ci-shard-structure-audit

## Problem

The operator waits on an increasingly throughput-bound CI integration suite: the sampled main runs grew from 38–71 seconds in August to 131–226 seconds in October. After PR #2078, run 37264903064 still spent 170 seconds in integration. The structure audits in `check-plan-routes.py` (feat62, consolidation, broad-catch) repeat AST traversal per rule; their callers are `tests/integration/test-checker-structure-locks.py` and the `--consolidation-audit` CLI (real `check-state.py` does not invoke them), and the supplied pre-#2078 profile of that test counted 17 million node visits. Adding tests increases this recurring wait even when individual tests get faster. Source: issue #2081 and the main session's measured intake.

## Done when — by perspective

**operator** — I wait less for complete integration coverage, without exchanging safety for speed. The required check rejects failed, skipped, cancelled, or incomplete work, reaches a conclusion when its dependencies finish, and still covers every gate I rely on today.

**code maintainer** — I can add integration test files without silently losing coverage, identify which files ran where, and reduce repeated structure-audit work without changing its findings or the unsharded suite's behavior.

## Success criteria

- SC-01 (code maintainer): `run-unit-tests.py --shard i/n` partitions the selected suite deterministically using duration weights and prints each shard's selected file list. Across all shards, every discovered integration file appears exactly once, including a newly added file without duration history; invalid shard arguments fail explicitly. QA demonstrates red-first discrimination for partition completeness, duration weighting, and argument handling.
  verify: automated        evidence: integration
- SC-02 (operator): The aggregation rejects every non-success shard conclusion, including failure, skipped, cancelled, and missing results; only all-success results with complete manifests can pass. QA demonstrates each rejection independently, red-first, alongside an all-success positive control.
  verify: automated        evidence: integration
- SC-03 (operator): Manifest validation compares against independently discovered `tests/integration/test-*.py` files at the tested commit, not against the partition's own output. Omitted files, duplicate files within or between shards, unexpected files, and missing manifests each fail; exact coverage passes. QA demonstrates red-first rejection of each defect.
  verify: automated        evidence: integration
- SC-04 (operator): Reading `git show <review_sha>:.github/workflows/tests.yml`, the reviewer confirms parallel integration matrix jobs on ubuntu-latest and one required-context aggregation job emitting exactly `integration`, with job-level `if: always()`. Once dependencies terminate, their failed, skipped, or cancelled conclusions do not skip the aggregator. Existing trigger asymmetry and the prohibition on cancel-in-progress on main remain intact.
  verify: inspection
- SC-05 (operator): Reading `git show <review_sha>:.github/workflows/tests.yml`, the reviewer traces each current gate individually into the required check's success condition: Unit suite, Validate feature execution state, Plan-route gate, Canonical-reader audit, Instruction-path gate, Layout gate, and Repository-state gate. Any failure or non-execution prevents success; existing nonempty-discovery and summary checks remain effective. Unit may run in a separate parallel job only if the aggregation requires its success.
  verify: inspection
- SC-06 (code maintainer): For the feat62, consolidation, and broad-catch structure audits, each file's AST is traversed once and dispatched to all applicable rules. Instrumented integration assertions show the reduced traversal count through both existing entry paths (`test-checker-structure-locks.py`'s in-process calls and the `check-plan-routes.py --consolidation-audit` CLI), and fail against the pre-change repeated traversal. Clean and violating fixtures preserve the baseline findings, ordering, exit status, stdout, and stderr; each rule has an independent violating witness.
  verify: automated        evidence: integration
- SC-07 (code maintainer): Unsharded unit execution preserves its discovery, attributed output, and failure propagation; regression assertions fail first against a targeted mutation of the touched runner behavior, rather than claiming an already-green suite as new proof.
  verify: automated        evidence: unit
- SC-08 (code maintainer): Unsharded integration execution preserves complete discovery and failure propagation, and existing structure-audit regressions pass alongside SC-06's differential evidence. QA demonstrates red-first discrimination for the touched integration runner behavior.
  verify: automated        evidence: integration
- SC-09 (operator): On a throwaway PR, the user independently breaks one test in one shard and omits one test file from every shard. For each case, the required `integration` check completes with failure, not success or indefinite pending. Restoring complete passing execution produces success. Record tested commit SHAs and Actions run URLs for each case. (A cancelled shard result is covered by SC-02's automated rejection; see OQ-02.)
  verify: uat
- SC-10 (operator): The user observes parallel shards in an actual passing Actions run and compares recorded integration critical-path time, including setup and aggregation, with the supplied 170-second run baseline. A controlled same-host, same-corpus comparison records lower structure-audit wall time for both `test-checker-structure-locks.py` and the `check-plan-routes.py --consolidation-audit` CLI, with commit pins and traversal counts. The thresholds settled in OQ-01 below apply.
  verify: uat

## Verification gaps

- Unit and integration have active non-null runners in harness.json; their detect globs cover the Python test surfaces. No applicable null-runner kind carries an SC. Functional and eval are excluded under DEC-187; unresolved component, ui, and typecheck kinds do not cover this Python/workflow change, and credentialled locally_run probes are not changed.
- Local automated evidence cannot establish GitHub's real scheduling, cancellation conclusions, required-context identity, or runner timing. SC-04/SC-05 inspect the pinned workflow; SC-09/SC-10 require the user and live Actions evidence before ship. This is not proof against deletion of the workflow that hosts the checks (DEC-183).

## Constraints

- Mission: plan. The brief-only intake authored no plan.yaml or implementation.
- DEC-174 BLOCKS execution of changes to run-unit-tests.py, run_pool.py, check-plan-routes.py, tests.yml, and gate tests through the enforcement path being changed. Plan the work here; implementation and explicit verification must be main-session-direct in this feature worktree.
- DEC-183 BLOCKS moving the plan-route protection outside the required `integration` context or claiming a self-hosted workflow guard protects its own deletion. It SUPPLIES the existing required-context contract; preserve it through aggregation, with human inspection of the workflow diff.
- DEC-211 SUPPLIES the attributed worker pool, complete selection, and suite-independence contract; sharding must preserve these. It BLOCKS change-based selection and shared-checkout test mutation.
- Settled implementation bounds: duration-weighted `--shard i/n`, printed shard file lists, parallel GitHub Actions integration matrix on ubuntu-latest, and fail-closed exact manifest coverage. The public repository uses free standard runners. Branch-protection settings remain the repository admin's responsibility, not a code change.
- OQ-01 — performance target, SETTLED at signature (recommendation adopted): start with four shards and require integration critical-path wall time below 100 seconds in three consecutive passing ubuntu-latest runs, recording all three rather than selecting the fastest. The supplied 45–70 second estimate is inference, not a guarantee. Structure-audit wall time must show a lower median across three controlled runs for each of the two existing entry paths (`test-checker-structure-locks.py` and the `--consolidation-audit` CLI), supported by SC-06's exact traversal reduction.
- OQ-02 — cancellation boundary, SETTLED at signature, AMENDED 2026-10-05 by the user: the guarantee is a failed conclusion when any shard concludes other than success, including cancelled, and main's no-cancellation policy is preserved. GitHub offers no per-job cancel in its UI or REST API (only whole-run cancel), so a live shard-only cancellation cannot be produced; the user dropped that live SC-09 case and relies on SC-02's automated proof that a `cancelled` shard result is rejected. Whole-workflow cancellation or supersession of an old PR run remains out of scope; no claim is made that `always()` survives cancellation of the entire workflow.
- OQ-03 — structure-audit entry paths, SETTLED by the user: the original brief claimed real `check-state.py` runs these audits; at 8e0b9e90 it does not (it delegates only to `check_state.runner.main`). The brief is corrected to the two existing entry paths. Wiring the audits into check-state is not part of this feature.

## Out of scope

- Migrating to pytest — rejected: large rewrite, process-spawn cost unchanged.
- Change-based test selection — rejected: miss risk in a heavily cross-wired repository.
- Moving heavy tests to nightly — deferred until sharding and less work prove insufficient.
- Reducing the BUG-1898 per-persona loop — the user chose to leave it.
- Paid larger runners — alternative noted, not chosen.
- Wiring the feat62 / consolidation / broad-catch audits into `check-state.py` — the user chose to correct the brief instead (OQ-03); it would add new reporting scope and change check-state output.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-10-04
