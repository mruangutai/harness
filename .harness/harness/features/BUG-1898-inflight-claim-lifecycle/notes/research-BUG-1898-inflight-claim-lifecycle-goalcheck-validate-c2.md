# BUG-1898 goal-check — validate c2

## BLUF

**FAIL for panel readiness** at exact pin `4942950a83c1895d85922f7cd9e9cfd41e28daf8`. The configured unit and integration matrix is green, F-02 closes at production grade, and current strict-read ordering keeps F-01 closed. SC-02 through SC-06 and SC-08 are met. SC-01 remains partial because the permanent wrapper accepts any nonzero mutant-suite exit with any one `FAIL  [bug1898]` line and discards the evidence needed to distinguish the intended exact-release red from an unrelated failure in the relocated validator. F-QA-01 therefore remains high. SC-07 is separately `pending_operator_gate`, not a panel failure; no live receipt is claimed.

## Provenance and scope

- Reviewed pin: `4942950a83c1895d85922f7cd9e9cfd41e28daf8`.
- Canonical merge-base measured with `git merge-base origin/main <pin>`: `a4d72e7fc91d0cf7a568d9e2a5225465a422170e`.
- Whole range: `a4d72e7fc91d0cf7a568d9e2a5225465a422170e..4942950a83c1895d85922f7cd9e9cfd41e28daf8`; 41 changed paths.
- Focused c2 delta: `81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e..4942950a83c1895d85922f7cd9e9cfd41e28daf8`; 10 changed paths. Its executable changes are `.claude/skills/harness/bin/validate-digest.py` and `tests/integration/test-suite-claim-preservation.py`; the other eight paths are feature state and c1 validation records.
- The assigned worktree had advanced to `24d04e2045d5e22bab745e499b600db63db3a542`, so all source, test, decision, checklist, and live-receipt claims were read by exact pinned object or exact pinned diff rather than inferred from worktree HEAD.
- I ran no tests, formatter, linter, or project-wide suite. Automated evidence below is collected from `notes/review-harness-qa-c2.md`; pinned inspection and diff review were performed directly.

## Perspective grades — exactly one line each

- **partial — operator** — SC-01 is partial because the permanent mutant oracle does not attribute its red result to the intended exact-release behavior; SC-07 is independently `pending_operator_gate`.
- **pass — orchestrator** — SC-02, SC-04, and SC-06 are met by the passing unit/integration matrix and current exact run-start, result-id, held-child, settlement, and recovery assertions.
- **pass — code maintainer** — SC-03 and SC-05 are met by the passing integration matrix; F-02 closes because every c2 production function clears the configured production grade while preserving one canonical-root, id-keyed lifecycle.
- **pass — reader** — SC-08 is met by pinned DEC-100/DEC-204/index/checklist inspection, which also states truthfully that the live receipt remains pending.

## Success-criterion adjudication

| SC | Status | Method | Current pinned evidence |
|---|---|---|---|
| SC-01 | partial | automated | QA's integration kind passed 70/70 and the wrapper's green arm passed: it ran the real validator suite and kept every PID-qualified governed-persona sentinel byte-identical (`notes/review-harness-qa-c2.md:12-24`). The mutation arm really redirects the suite through a copied validator whose `release` ignores `agent_id`, but its permanent oracle is only `code != 0 and reddened`, where `reddened` is any line beginning `FAIL  [bug1898]` (`test-suite-claim-preservation.py:100-111`). It neither binds the red to named exact-release assertions nor retains/rejects unrelated relocated-validator failures, so the exact-discrimination clause remains unproved. |
| SC-02 | met | automated | QA's unit kind passed 42/42; the carrying exact claim/bind-before-write, wake/reclaim, cause/retryability hold, BLOCKED-only yield, and settlement cases remain at `tests/unit/omp-hooks.test.ts:1875-2001` (`notes/review-harness-qa-c2.md:12-16,38`). |
| SC-03 | met | automated | QA's integration kind passed 70/70; canonical feature-root, run-start API, one-PM, legal non-PM concurrency, unreadable refusal, and DEC-100 pass-through cases remain at `tests/integration/test-inflight-registry.py:1238-1410` (`notes/review-harness-qa-c2.md:39`). |
| SC-04 | met | automated | QA's unit kind passed 42/42; actual result-row ids, reordered mixed results, repeated/lineage ids, receipt rollback, and settlement cases remain at `tests/unit/omp-hooks.test.ts:2003-2113` (`notes/review-harness-qa-c2.md:40`). |
| SC-05 | met | automated | QA's integration kind passed 70/70, including the semantic port case that rejects the marker on the wrong bus and accepts `pi.events` at `tests/integration/test-check-omp-port.py:194-214` (`notes/review-harness-qa-c2.md:41`). |
| SC-06 | met | automated | QA's integration kind passed 70/70. At the pin, `_settle_in` strict-reads own and child claims before child refusal and before `_release_own`; the exact held-child, recovery, unreadable-parent, BLOCKED escape, leaf, and byte-preservation cases remain at `tests/integration/test-validate-digest.py:5769-5877` (`notes/review-harness-qa-c2.md:31,42`). |
| SC-07 | pending_operator_gate | uat | Pinned `notes/live-omp-probe.md` states that no live run is recorded. QA did not run the locally-run kind (`notes/review-harness-qa-c2.md:16,44`). This is the required credentialled operator merge gate, not a panel failure, and no live receipt is fabricated. |
| SC-08 | met | inspection | Pinned DEC-100 preserves dispatch-guard crash pass-through and child self-refusal (`DECISIONS.md:1373-1377`); DEC-204 records exact run-start identity, canonical-root/id-keyed settlement, `pi.events`, receipt-only rollback, held-parent refusal, and exact recovery (`DECISIONS.md:6361-6438`); the generated index names that current truth (`DECISIONS-INDEX.md`, DEC-204); `notes/ship-checklist.md` requires enumerate/classify/exact-release/re-enumerate cutover and makes the first post-merge feature follow-up non-gating. |

## Prior-finding dispositions

- **F-01 — closed, no regression.** `kind: substance`; `severity: high`; `reader: harness-code-reviewer`; `owned task: T-03`. Concrete failure scenario: an unreadable canonical registry lets a dispatch-capable parent return success while a child may remain live, or a release rewrite destroys unreadable bytes. At c2, `_settle_in` catches either strict own/child read failure before any release, routes a non-BLOCKED dispatcher return to refusal, and reaches `_release_own` only after readable state and no held child. QA's current integration matrix includes the corresponding parent, BLOCKED, leaf, and byte-preservation cases (`notes/review-harness-qa-c2.md:31,42`).
- **F-02 — closed.** `kind: substance`; `severity: high`; `reader: harness-code-reviewer + harness-qa`; `owned task: T-03`. Concrete failure scenario: concentrated branch ordering in `_registry_errand` falls below the production grade and makes a future release-before-refusal regression plausible. The c2 extraction leaves `_registry_errand` grade 4, `_settle_in` grade 5, and `_release_own` grade 5; the whole-range grader reports 127 passing changed functions with no blocking or grade-2 record (`notes/review-harness-code-reviewer-c2.md:20-30`). The source still has one strict-read → held-child gate → exact release path.
- **F-QA-01 — active.** `kind: substance`; `severity: high`; `reader: harness-qa + harness-pm`; `owned task: T-03/T-04`. Concrete failure scenario: the copied validator suite exits nonzero for an unrelated relocation/configuration regression and emits one incidental `FAIL  [bug1898]` assertion while the intended persona-release signature is absent or different; `code != 0 and reddened` still marks the mutation leg healthy, and the wrapper discards the child output on success, so reviewers cannot attribute the red to exact release. The c2 wrapper fixes prior concurrency collisions with PID-qualified feature/runtime identity and does reject a crash with no BUG-1898 line, but it does not bind acceptance to named exact-release failures or exclude/retain unrelated failures (`notes/review-harness-qa-c2.md:20-30`). F-QA-01 therefore is not closed by a generic nonzero-plus-prefix oracle.

## Gate separation

- **Validation panel:** FAIL on active high F-QA-01 and partial SC-01.
- **Other automated and inspection outcomes:** SC-02 through SC-06 and SC-08 are met; F-01 and F-02 are closed.
- **Operator merge gate:** SC-07 is `pending_operator_gate`. It must be run after panel repair; its absence is not counted as a panel finding.

## Scratch-worktree disposition

No scratch worktree was created. The assigned feature worktree remains in place; only this required goal-check artifact was written.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "F-01 and F-02 are closed at 4942950a, but F-QA-01 remains high because the permanent mutant oracle does not attribute its red to exact-release behavior; SC-07 is separately pending_operator_gate."
  feasibility: clear
  surface: L
  flags: [coverage-gap, mutation-oracle, exact-identity, lifecycle, operator-merge-gate]
  recommend: proceed
  tasks: 5
  decisions: 7
  needs_approval: false
  risk: high
  sc_status:
    - { id: SC-01, verdict: partial, method: automated, evidence: "QA integration 70/70 and green preservation pass; mutant acceptance is only nonzero plus any FAIL [bug1898] prefix" }
    - { id: SC-02, verdict: met, method: automated, evidence: "QA unit 42/42; exact run-start, reclaim, held-run and settlement cases" }
    - { id: SC-03, verdict: met, method: automated, evidence: "QA integration 70/70; canonical root, one-PM, legal non-PM concurrency, unreadable refusal and DEC-100 cases" }
    - { id: SC-04, verdict: met, method: automated, evidence: "QA unit 42/42; actual-id reordered result, receipt rollback, repeated and lineage-id cases" }
    - { id: SC-05, verdict: met, method: automated, evidence: "QA integration 70/70; wrong-bus mutant rejected and pi.events accepted" }
    - { id: SC-06, verdict: met, method: automated, evidence: "QA integration 70/70; exact held-child/recovery and unreadable-registry no-write cases" }
    - { id: SC-07, verdict: pending_operator_gate, method: uat, evidence: "Pinned live-omp-probe.md records no live run; no receipt fabricated and absence is not a panel failure" }
    - { id: SC-08, verdict: met, method: inspection, evidence: "Pinned DEC-100, DEC-204, generated index and ship checklist match current lifecycle and cutover truth" }
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle/.harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/research-BUG-1898-inflight-claim-lifecycle-goalcheck-validate-c2.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle/.harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/research-BUG-1898-inflight-claim-lifecycle-goalcheck-validate-c2.md
```
