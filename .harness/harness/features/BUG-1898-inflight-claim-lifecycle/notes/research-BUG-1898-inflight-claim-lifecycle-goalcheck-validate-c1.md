# BUG-1898 goal-check — validate c1

## BLUF

**FAIL for panel readiness** at pinned SHA `81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e`. The canonical range is `a4d72e7fc91d0cf7a568d9e2a5225465a422170e..81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e` (35 paths), with focused c1 comparison `84c3a6cbe74c7c27337d4372a68be60fca834118..81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e` (11 paths). F-01 is closed and every non-operator criterion, SC-02 through SC-06 plus SC-08, is discharged. F-QA-01 remains high because the new suite-preservation wrapper passes without placing its sentinels in any registry exercised by the child suite, and its fixed sentinel identity is unsafe under concurrent invocation. SC-07 remains a separate pending operator-only live OMP merge gate; it is not a panel failure and no receipt is claimed.

The focused executable/test change is limited to `.claude/skills/harness/bin/validate-digest.py`, `tests/integration/test-validate-digest.py`, and new `tests/integration/test-suite-claim-preservation.py`; the other focused paths are feature state and c0 records. The checkout's enforcement, test, decision, index, checklist, and live-probe surfaces match the pinned SHA.

## Perspective grades — exactly one line each

- **partial — operator** — SC-01 is partial because direct exact-release proof passes but the suite-preservation wrapper is non-discriminating; SC-07 is independently pending the operator's live OMP receipt.
- **pass — orchestrator** — SC-02, SC-04, and SC-06 are met by the 98-case hook run and the 81 exact-release checks, including exact held-child refusal, recovery, and unreadable-registry handling.
- **pass — code maintainer** — SC-03 and SC-05 are met by the 161 registry checks, 88 dispatch-guard cases, and the 30-case port check that rejects the wrong lifecycle bus.
- **pass — reader** — SC-08 is met by pinned DEC-100/DEC-204 current truth, a clean generated index, and the exact manual cutover and non-gating post-merge follow-up in the ship checklist.

## Success-criterion adjudication

| SC | Verdict | Method | Pinned evidence |
|---|---|---|---|
| SC-01 | partial | automated | `test-validate-digest.py` passes 81/81 BUG-1898 exact-release checks, including every governed persona and occurrence 1 (`tests/integration/test-validate-digest.py:5712-5760`). The new wrapper reports 3 PASS, but its sentinels live at checkout `ROOT` while child hook calls set `HARNESS_PROJECT_DIR` to temporary roots (`test-suite-claim-preservation.py:33-69`; `test-validate-digest.py:1733-1753`), so the suite clause lacks discriminating proof. |
| SC-02 | met | automated | T-01/T-02 targeted verifies pass: registry 161/161, dispatch guard 88/88, and hook 98/98 with 272 expectations; the c1 focused diff leaves these surfaces unchanged from the accepted pin. |
| SC-03 | met | automated | Registry and dispatch verifies pass 161/161 and 88/88; canonical feature-root, one-PM, multi-flight non-PM, exact-id recovery, unreadable refusal, and DEC-100 pass-through cases remain unchanged in c1. |
| SC-04 | met | automated | Hook verify passes 98/98; actual-id reordered results, never-started receipt rollback, repeated/lineage ids, and exact settlement surfaces are unchanged in c1. |
| SC-05 | met | automated | Port verify passes 30/30, including a marker-bearing `pi.on` mutant that fails and the pinned `pi.events` registration that passes. |
| SC-06 | met | automated | Validator verify passes 81/81. `validate-digest.py:2306-2345` strict-reads own and child claims before release; `test-validate-digest.py:5850-5877` proves unreadable parent PASS refusal, BLOCKED escape, leaf behavior, and byte preservation, while readable held-child/recovery paths remain exact. |
| SC-07 | not_met | uat | Pinned `notes/live-omp-probe.md:3` says no live run is recorded. The exact T-04 dry-run started nothing and reported NOT READY only because this validation panel's live claims are present. This operator-only merge gate remains pending, not failed. |
| SC-08 | met | inspection | Pinned DEC-204 states run-start exact ids, id-keyed task/lifecycle settlement through `pi.events`, receipt-only rollback, canonical-root exact release, and parent-yield refusal (`DECISIONS.md:6361-6438`). DEC-100's guard-crash rule remains distinct from child self-refusal; T-05's generator/diff exits 0; `ship-checklist.md:13-115` provides per-registry enumeration, exact per-row cutover, and non-gating post-merge follow-up. |

## Prior-finding re-adjudication

- **F-01 — closed** — `kind: substance`; `severity: high`; `reader: harness-code-reviewer`; `owner task: T-03`; original scenario: an unreadable canonical registry let a dispatch-capable parent yield while a child might remain live. The pin now strict-reads before any release, refuses non-BLOCKED dispatcher returns, permits BLOCKED as the repair escape, preserves the unreadable bytes, and passes all corresponding checks. This makes SC-06 and the implementation side of SC-08 current-truth compliant.
- **F-QA-01 — retained** — `kind: substance`; `severity: high`; `reader: harness-qa + harness-pm`; `owner task: T-03/T-04`; concrete failure scenario: a validator regression releases an unrelated row in the temporary hook registry actually exercised by `test-validate-digest.py`, while the wrapper's checkout-root sentinel remains untouched and all three wrapper assertions pass. Separately, two workers can invoke the wrapper together: the second creates non-PM rows, hits the fixed-feature one-PM refusal before `main()` enters `try/finally`, raises while dereferencing the refused entry, and strands the rows already created. The measured serial 3/3 PASS proves the happy path, not either contract boundary.

Repairing F-QA-01 needs no new approval: isolate each invocation and place the sentinel in the registry the child suite actually exercises, with a red proof that mutating that registry fails. This remains inside approved SC-01 and T-03/T-04.

## Verification receipts

- T-01 exact verify: `python3 tests/integration/test-inflight-registry.py && python3 tests/integration/test-dispatch-guard.py` — exit 0; 161/161 and 88/88.
- T-02 exact verify: `bun test tests/unit/omp-hooks.test.ts && python3 tests/integration/test-check-omp-port.py` — exit 0; 98/98, 272 expectations, then 30/30.
- T-03 exact verify: `python3 tests/integration/test-validate-digest.py` — exit 0; 81/81 BUG-1898 exact-release checks; `ALL PASSED`.
- Focused suite wrapper: `python3 tests/integration/test-suite-claim-preservation.py` — exit 0; 3 PASS, 0 failures. The green run is non-discriminating for the reasons above.
- T-04 exact verify: `python3 tests/manual/probe-inflight-claim-lifecycle.py --dry-run && python3 tests/integration/test-run-unit-tests-kinds.py` — exit 1 at the dry-run's expected active-panel-claims prerequisite, so the `&&` second command did not execute. Run separately, `test-run-unit-tests-kinds.py` passes 8/8. No live process or scenario ran, and this is not an SC-07 receipt.
- T-05 exact verify: `python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md` — exit 0, no diff.

## Gate separation

- **Panel readiness:** FAIL on open high F-QA-01 and partial SC-01.
- **Non-operator criteria:** all met: SC-02, SC-03, SC-04, SC-05, SC-06, SC-08.
- **Operator merge gate:** SC-07 pending; the operator must still produce the live OMP PASS after panel repair. Pending is not a panel failure.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "At 81dbd81d, F-01 is closed and all non-operator criteria pass, but F-QA-01 remains high because the suite-preservation wrapper is non-discriminating; SC-07 is separately pending operator execution."
  feasibility: clear
  surface: L
  flags: [coverage-gap, test-isolation, exact-identity, lifecycle, operator-merge-gate]
  recommend: proceed
  tasks: 5
  decisions: 7
  needs_approval: false
  risk: high
  sc_status:
    - { id: SC-01, verdict: partial, method: automated, evidence: "81/81 direct checks pass; suite wrapper 3/3 is non-discriminating because sentinels and exercised hook registries differ" }
    - { id: SC-02, verdict: met, method: automated, evidence: "T-01/T-02 exit 0; 161/161 registry, 88/88 dispatch, 98/98 hook" }
    - { id: SC-03, verdict: met, method: automated, evidence: "T-01 exit 0; canonical root, one-PM, legal non-PM multi-flight, recovery and pass-through covered" }
    - { id: SC-04, verdict: met, method: automated, evidence: "T-02 exit 0; 98/98 hook cases" }
    - { id: SC-05, verdict: met, method: automated, evidence: "T-02 exit 0; 30/30 port cases including wrong-bus mutant" }
    - { id: SC-06, verdict: met, method: automated, evidence: "T-03 exit 0; 81/81 exact-release checks including unreadable-registry parent hold" }
    - { id: SC-07, verdict: not_met, method: uat, evidence: "notes/live-omp-probe.md:3 — no live receipt; pending operator gate, not panel failure" }
    - { id: SC-08, verdict: met, method: inspection, evidence: "pinned DEC-100/DEC-204/index/checklist; T-05 exit 0" }
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle/.harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/research-BUG-1898-inflight-claim-lifecycle-goalcheck-validate-c1.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle/.harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/research-BUG-1898-inflight-claim-lifecycle-goalcheck-validate-c1.md
```
