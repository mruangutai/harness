# Code review — BUG-2141 — c0

FAIL: T-01 omits part of SC-04's explicitly required integration coverage. The guard itself has no identified correctness defect.

Reviewed `0b17e9bbf7ef4baafa0eb0844ec0edbb753dd86f..423049fe49c122ee2ec790c53cdc6ce19f1ec791`. No human-attributed commits; initial checkout status clean. HEAD subsequently differs from the pin only in feature.json; inspected source bytes remain pinned. No build-lead amendments or dev receipts exist for this main-direct build.

## Stage 1 — specification
- SC-01 inspection: pinned `git show` establishes duties, permitted leads, header authority and no-handoff exemption at `.harness/harness/docs/DECISIONS.md:4509-4520`, with DEC-120 cross-reference at `:2359-2361`. Index diff carries corresponding references and +4/+17 anchor shifts; generator execution belongs to QA.
- SC-02 inspection: pinned `git show` establishes matching short exception pointers at `AGENTS.md:39` and `.omp/commands/harness.md:8-15`; no lifecycle procedure is copied.
- SC-03: real-guard unit assertions cover refusal, diagnostic, unchanged registry and origin/plan controls (`tests/unit/test-lead-start-preflight.py:344-385`). `notes/evidence-T-01.md` records baseline acceptance rather than setup failure; its run claims were not re-executed here.
- SC-04: shared predicate consumption is correct (`.claude/skills/harness/bin/dispatch-guard.py:705`), and prohibited/mixed integration assertions exist, but the remaining named integration controls are absent.

## Finding — med substance, T-01 / SC-04
`tests/integration/test-dispatch-guard.py:679-712` exercises only Main→engineering on all-direct and mixed plans. No integration fixture dispatches Main→product/validator on the qualifying plan, or Main→engineering on team, absent/invalid/empty/missing-mode plans. Existing product cases originate orchestrator; the existing Main case dispatches orchestrator. Those controls exist only in the unit file. [INFERENCE] A refusal broadened to all Main leads, or to nonqualifying plans other than mixed, would leave this integration coverage green despite rejecting valid dispatches. This is an explicit acceptance omission, not a request to expand scope.

Must fix T-01: add real-guard integration controls for SC-04's permitted main leads and shared-policy nonqualifying shapes, with valid run/header setup and claim assertions; preserve existing outcomes.

## Stage 2 — quality
Origin uses the unchanged `omp_main` identity, not prompt text. Registered feature lookup failures fall through to the existing BUG-2110 registered-run refusal; missing/nonqualifying plans keep prior outcomes. The new refusal precedes preflight and both registry mutations (`dispatch-guard.py:714-718`). No second classification policy or compatibility layer was introduced.

Pinned Python risk grading: 9 records PASS; production refusal grade 4, test records grades 3–5; no grade-2 reasons. No tests, builds, linters, formatters or mutants executed by this reader. QA owns final verification.

## Principles applied
- Model the Domain: retained `handoff_policy.exempt_reason` as the single classification owner.
- Delete First: assessed the local guard addition without demanding speculative interfaces or organizational cleanup.

Open questions: none.
