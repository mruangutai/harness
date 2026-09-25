# BUG-1898 goal-check — validate c1

## Scope and verdict

**FAIL** at pinned SHA `81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e` over the exact canonical range `a4d72e7fc91d0cf7a568d9e2a5225465a422170e..81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e` (35 paths, 3,889 insertions, 554 deletions), emphasizing c1 delta `84c3a6cbe74c7c27337d4372a68be60fca834118..81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e` (11 paths, 483 insertions, 18 deletions). F-01 is closed, but F-QA-01 remains high: the new suite wrapper is green only without discriminating the checkout-root sentinel, and concurrent invocations fail before cleanup. SC-07 remains the expected `pending_operator_gate`; its absent live receipt is not this failure.

The c1 executable/test delta is confined to `.claude/skills/harness/bin/validate-digest.py`, `tests/integration/test-validate-digest.py`, and new `tests/integration/test-suite-claim-preservation.py`; the other eight paths are feature state and c0 validation records. Current-pin source and tests were read directly; the worktree copies of the enforcement, test, decision, index, and checklist surfaces have no diff from the pin.

## Perspective grades — exactly one line per declared perspective

- **partial — operator** — SC-01 is partial: direct exact-release preservation passes, but its required suite-plus-sentinel proof remains non-discriminating and non-reentrant; SC-07 is separately `pending_operator_gate` (`tests/integration/test-suite-claim-preservation.py:22-23,43-73`; `tests/integration/test-validate-digest.py:1733-1753,5664-5729`; `notes/live-omp-probe.md:1-43`).
- **pass — orchestrator** — SC-02, SC-04, and SC-06 are met: the c1 unit receipt is 98 pass / 0 fail, and the validator is `ALL PASSED` with 81/81 BUG-1898 checks including unreadable-registry parent refusal, BLOCKED escape, exact preservation, and settled-child recovery (`notes/review-harness-qa-c1.md:9-14,27,31-38`; `tests/integration/test-validate-digest.py:5815-5877`).
- **pass — code maintainer** — SC-03 and SC-05 remain met: c1 did not change the canonical resolver, registry, hook, or port-check surfaces; the current unit/validator receipts are green and the retained wrong-bus mutant proves `pi.events` (`notes/review-harness-qa-c0.md:25,27`; `notes/review-harness-qa-c1.md:9-15,31-38`).
- **pass — reader** — SC-08 is met at the pin: DEC-100 retains guard-crash pass-through plus child self-refusal, DEC-204 states exact run-start identity, canonical-root exact release, id-keyed settlement, `pi.events`, and held-child refusal, its generated index is byte-current, and the checklist requires per-row exact cutover while making the first post-merge cycle non-gating (`.harness/harness/docs/DECISIONS.md:1373-1377,6361-6399,6418-6438,6476-6495`; `.harness/harness/docs/DECISIONS-INDEX.md:204`; `notes/ship-checklist.md:13-115`).

## Success-criterion status

| SC | Verdict | Method | Current-pin evidence |
|---|---|---|---|
| SC-01 | partial | automated | Direct missing-identity, occurrence-1, canonical-root, and exact-release cases pass in the measured 81/81 validator run. The wrapper's serialized run was 3 PASS, but it seeds the checkout registry while the invoked suite fires BUG-1898 hook cases only against fresh `_t09_root()` directories via `HARNESS_PROJECT_DIR`; it therefore cannot redden on a regression confined to the hook roots. Its fixed sentinel feature/ids also caused two measured parallel invocations to exit 1 before `finally`. (`notes/review-harness-qa-c1.md:19-25,31-33`; `tests/integration/test-suite-claim-preservation.py:22-23,43-73`; `tests/integration/test-validate-digest.py:1733-1753,5664-5729`.) |
| SC-02 | met | automated | `bun test tests/unit/omp-hooks.test.ts` measured 98 pass, 0 fail, 272 expectations; retained red-first evidence covers bind, reclaim, refusal, BLOCKED-only yield, and exact settlement (`notes/review-harness-qa-c1.md:9-12,31-34`; `notes/review-harness-qa-c0.md:24`). |
| SC-03 | met | automated | Canonical feature-root/run-start, one-PM, non-PM multiflight, unreadable refusal, and DEC-100 pass-through evidence remains unchanged from c0; c1 validator is green (`notes/review-harness-qa-c0.md:25`; `notes/review-harness-qa-c1.md:12,35`). |
| SC-04 | met | automated | The same 98/98 unit run covers actual result ids, reordered mixed batches, repeated/lineage ids, never-started receipt rollback, and settlement; red-first receipt retained (`notes/review-harness-qa-c1.md:11,36`; `notes/review-harness-qa-c0.md:26`). |
| SC-05 | met | automated | No c1 change touched the hook or port checker; the retained wrong-`pi.on` mutant fails while the pin's `pi.events` form passes (`notes/review-harness-qa-c0.md:27`; `.harness/harness/docs/DECISIONS.md:6423-6428,6487-6492`). |
| SC-06 | met | automated | Independent `python3 tests/integration/test-validate-digest.py` exited 0 with `ALL PASSED` and 81/81 BUG-1898 checks. The new unreadable-registry case refuses parent PASS, permits the BLOCKED escape, leaves corrupt bytes unchanged, and source strict-reads before any release (`.claude/skills/harness/bin/validate-digest.py:2290-2342`; `tests/integration/test-validate-digest.py:5850-5877`; `notes/review-harness-qa-c1.md:27`). |
| SC-07 | pending_operator_gate | uat | `notes/live-omp-probe.md:1-43` records no live run and explicitly says dry-run is not evidence. This remains the sole expected operator-run merge gate after validation findings close; it was not run and is not a panel failure. |
| SC-08 | met | inspection | Pinned DEC-100/DEC-204/index/checklist inspection passes, and `python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md` exited 0. DEC-204 current truth is preserved at source as cited above. |

## Prior finding dispositions

- **F-01 — closed.** `kind: substance`; `scope: task`; `severity: high`; `reader: code-reviewer`; `owner task: T-03`. Original scenario: a dispatch-capable parent yields while its canonical registry is unreadable and a child may remain live. Current source strict-reads `live_claims` before release and `_unreadable_registry` refuses a non-BLOCKED lead/orchestrator return without writing; the measured validator suite proves refusal, BLOCKED escape, leaf behavior, and byte preservation (`validate-digest.py:2290-2342`; `test-validate-digest.py:5850-5877`; 81/81 and `ALL PASSED`).
- **F-QA-01 — retained.** `kind: substance`; `scope: task`; `severity: high`; `reader: harness-qa + harness-pm`; `owner task: T-03/T-04`. Concrete executable failure scenario: worker A runs `python3 tests/integration/test-suite-claim-preservation.py` and holds fixed `BUG-1898-suite-sentinel` rows; worker B runs the same command, reaches the one-PM refusal, dereferences `None` at `entry["claim_id"]`, exits 1 before entering `finally`, and leaves its already-created non-PM rows. Even serialized, a validator regression that releases claims in the hook's actual root is not discriminated because the wrapper seeds the checkout root while all invoked BUG-1898 hook subprocesses set fresh throwaway `HARNESS_PROJECT_DIR` roots. The panel measured both the parallel exit-1 path and a later serialized 3-PASS run; no faithful baseline/mutant red exists (`notes/review-harness-qa-c1.md:19-25,40-42`).

No approval is needed: repairing the test isolation and making its sentinel share the exercised hook registry are within the already approved SC-01 and T-03/T-04 scope.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "F-01 closes at 81dbd81d, but operator remains partial and F-QA-01 stays high because the suite-preservation wrapper neither discriminates the exercised registry nor survives concurrent invocation; SC-07 is separately pending operator execution."
  feasibility: clear
  surface: L
  flags: [coverage-gap, test-isolation, exact-identity, lifecycle, operator-merge-gate]
  recommend: proceed
  tasks: 5
  decisions: 7
  needs_approval: false
  risk: high
  sc_status:
    - { id: SC-01, verdict: partial, method: automated, evidence: "Direct 81/81 preservation cases pass, but the wrapper uses disconnected throwaway hook roots and concurrent invocations exit 1 — notes/review-harness-qa-c1.md:19-25" }
    - { id: SC-02, verdict: met, method: automated, evidence: "98 pass / 0 fail unit receipt — notes/review-harness-qa-c1.md:9-12,31-34" }
    - { id: SC-03, verdict: met, method: automated, evidence: "notes/review-harness-qa-c0.md:25; notes/review-harness-qa-c1.md:12,35" }
    - { id: SC-04, verdict: met, method: automated, evidence: "98 pass / 0 fail unit receipt — notes/review-harness-qa-c1.md:11,36" }
    - { id: SC-05, verdict: met, method: automated, evidence: "notes/review-harness-qa-c0.md:27; pinned DEC-204 pi.events truth" }
    - { id: SC-06, verdict: met, method: automated, evidence: "81/81 BUG-1898 validator checks including unreadable parent refusal — notes/review-harness-qa-c1.md:12,27,38" }
    - { id: SC-07, verdict: pending_operator_gate, method: uat, evidence: "notes/live-omp-probe.md:1-43 — no live receipt; expected operator merge gate, not a panel failure" }
    - { id: SC-08, verdict: met, method: inspection, evidence: "Pinned DEC-100/DEC-204/index/checklist; generated-index diff exit 0" }
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle/.harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/research-BUG-1898-inflight-claim-lifecycle-goalcheck-validate-c1.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle/.harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/research-BUG-1898-inflight-claim-lifecycle-goalcheck-validate-c1.md
```
