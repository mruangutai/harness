# Goal-check — BUG-1699-lifecycle-cards — validate c0

## Boundary and outcome

**FAIL.** This goal-check reviews immutable SHA `ed64ea9cc4ef92e3e54adfa0849a0147230b480b` against merge base `8ef4731e816f08dbc562206134c100b0c034a812` and the signed `BRIEF.md`/approved `plan.yaml`. The current focused behavior tests pass, and pinned inspection finds the intended implementation, but SC-01–SC-14 each require fail-first evidence that the record does not supply. SC-10 additionally lacks an execution-bound proof that plan mutation makes no GitHub network write. SC-15 and SC-16 are met by pinned inspection. Because each perspective carries at least one unmet criterion, none is delivered.

## Perspective grades

- **operator — fail** — carries SC-01, SC-02, SC-03, SC-06, SC-07, SC-08, and SC-09. Pinned shipped behavior and current tests support the intended lifecycle (`notes/review-harness-code-reviewer-c0.md:7`; `notes/review-harness-qa-c0.md:16-22`), but the required fail-first proof is absent for the checkpoint, reset/reapproval, ship, and reconciliation scenarios (`notes/review-harness-qa-c0.md:30-38,45`); the T-01 build receipt proves only a narrower INV-26 red case (`runs/2026-09-16-03-build-eng/digest.md:30-32`).
- **orchestrator — fail** — carries SC-04, SC-05, and SC-10. The pinned diff places Building/Review at the intended boundaries and preserves best-effort local-first projection (`notes/review-harness-code-reviewer-c0.md:8`), while the focused T-02/T-03 checks pass (`notes/review-harness-qa-c0.md:19-20`); however SC-04/SC-05 have no captured pre-fix failure, and SC-10 has neither complete fail-first evidence nor a subject-bound execution test proving that plan mutation performs no network write (`notes/review-harness-qa-c0.md:33-36,39,45,52`).
- **code maintainer — fail** — carries SC-11, SC-12, SC-13, SC-14, SC-15, and SC-16. Pinned inspection confirms the single projection policy, preserved abandonment/closure/hold behavior, exact callers, and current decision authority (`notes/review-harness-code-reviewer-c0.md:9-12`), and the focused T-01/T-04/T-05 checks pass (`notes/review-harness-qa-c0.md:18,21-22`); SC-11–SC-14 nevertheless lack their required per-criterion fail-first record (`notes/review-harness-qa-c0.md:40-45`), while only inspection criteria SC-15 and SC-16 are met.

## Canonical SC status

```yaml
sc_status:
  - id: SC-01
    verdict: not_met
    method: automated
    evidence: "Current checkpoint/projection checks pass, but no captured pre-fix RESUME/open-order failure: notes/review-harness-qa-c0.md:16-22,30,45."
  - id: SC-02
    verdict: not_met
    method: automated
    evidence: "Current Build/Building checks pass, but no captured pre-fix dispatch-order failure: notes/review-harness-qa-c0.md:16-22,31,45."
  - id: SC-03
    verdict: not_met
    method: automated
    evidence: "Current validation/Review checks pass, but no captured pre-fix boundary-order failure: notes/review-harness-qa-c0.md:16-22,32,45."
  - id: SC-04
    verdict: not_met
    method: automated
    evidence: "Current must-fix ordering assertions pass, but no captured pre-fix failure: notes/review-harness-qa-c0.md:20,33,45."
  - id: SC-05
    verdict: not_met
    method: automated
    evidence: "Current returned-fix Review assertions pass, but no captured pre-fix failure: notes/review-harness-qa-c0.md:20,34,45."
  - id: SC-06
    verdict: not_met
    method: automated
    evidence: "Current reset tests pass, but no captured pre-fix atomic-reset/no-side-effect failure: notes/review-harness-qa-c0.md:19-20,35,45."
  - id: SC-07
    verdict: not_met
    method: automated
    evidence: "Current reapproval classification tests pass, but no captured pre-fix failure: notes/review-harness-qa-c0.md:19-20,36,45."
  - id: SC-08
    verdict: not_met
    method: automated
    evidence: "Current all-card Done scenario passes, but no captured pre-fix failure: notes/review-harness-qa-c0.md:18,37,45."
  - id: SC-09
    verdict: not_met
    method: automated
    evidence: "Current reconciliation/idempotence scenarios pass, but no captured pre-fix failure: notes/review-harness-qa-c0.md:21,38,45."
  - id: SC-10
    verdict: not_met
    method: automated
    evidence: "Local-first and continuation scenarios pass, but fail-first evidence is incomplete and no execution-bound test proves plan mutation performs no GitHub write: notes/review-harness-qa-c0.md:39,45,52."
  - id: SC-11
    verdict: not_met
    method: automated
    evidence: "Current six-station/all-card projection checks pass, but no per-SC pre-fix result is captured: notes/review-harness-qa-c0.md:18,40,45."
  - id: SC-12
    verdict: not_met
    method: automated
    evidence: "Current abandonment checks pass, but no captured pre-fix failure: notes/review-harness-qa-c0.md:18,21,41,45."
  - id: SC-13
    verdict: not_met
    method: automated
    evidence: "Current no-direct-close checks pass, but no captured pre-fix failure: notes/review-harness-qa-c0.md:18,42,45."
  - id: SC-14
    verdict: not_met
    method: automated
    evidence: "Current held-child scenarios pass, but no captured pre-fix failure: notes/review-harness-qa-c0.md:18,43,45."
  - id: SC-15
    verdict: met
    method: inspection
    evidence: "Pinned inspection traces one projection through status, INV-26, and reconcile; local reset/resume; and exactly one caller at each checkpoint: notes/review-harness-code-reviewer-c0.md:10."
  - id: SC-16
    verdict: met
    method: inspection
    evidence: "Pinned inspection confirms DEC-138/203/220/224/229 current, DEC-146 preserved, and the generated index accurate: notes/review-harness-code-reviewer-c0.md:11."
```

## Task accounting

| Task | Pinned delivery evidence | Goal-check consequence |
|---|---|---|
| T-01 | The seven signed focused runners pass (`notes/review-harness-qa-c0.md:18`); the build digest records the INV-26 fail-first repair and exact gate (`runs/2026-09-16-03-build-eng/digest.md:9-18,30-32`). | Current behavior is supported, but the one red INV-26 case does not discharge the explicit fail-first conjunct of every T-01-carried automated SC. |
| T-02 | `test-plan-merge.py` passes (`notes/review-harness-qa-c0.md:19`), and pinned inspection confirms local reset/resume (`notes/review-harness-code-reviewer-c0.md:7,10`). | SC-06/SC-07 red evidence is absent; SC-10's no-network clause has no execution-bound test. |
| T-03 | Station-order, adapter, and generated-parity checks pass (`notes/review-harness-qa-c0.md:20`); pinned inspection confirms one ordered caller per boundary (`notes/review-harness-code-reviewer-c0.md:8,10`). | The checkpoint SCs lack the required pre-fix failures; SC-10 retains the no-network coverage gap. |
| T-04 | Reconciliation's focused test passes (`notes/review-harness-qa-c0.md:21`), and pinned inspection confirms all-card, bounded, best-effort repair (`notes/review-harness-code-reviewer-c0.md:7,9`). | SC-09–SC-12 do not have complete per-SC fail-first evidence. |
| T-05 | Forty authority anchors pass and the generated-index diff is empty (`runs/2026-09-16-04-build-product/digest.md:28-30`; `notes/review-harness-qa-c0.md:22`). | SC-15 and SC-16 are met; documentation does not cure the automated evidence gaps in SC-10–SC-14. |

## Build, simplify, and scope accounting

- The engineering and product build digests pass their signed checks (`runs/2026-09-16-03-build-eng/digest.md:1-33`; `runs/2026-09-16-04-build-product/digest.md:1-32`). These are evidence records, not shipped lifecycle behavior.
- The `2026-09-16-05-simplify-eng` BLOCKED verdict was procedural: its digest expressly reports no product blocker and a passing signed T-01 gate (`runs/2026-09-16-05-simplify-eng/digest.md:4-16,31-34,52-56`). Main authorized the narrow read-only digest-contract repair. The successor `2026-09-16-06-simplify-eng` digest is therefore the current build result and passes all four angles (`runs/2026-09-16-06-simplify-eng/digest.md:4-25`).
- The digest-contract changes in `.claude/skills/harness-digest-dev/SKILL.md` and `.claude/skills/harness-handoff/SKILL.md` are an explicitly authorized **scope change**, not T-01–T-05 lifecycle behavior. Feature records, handoffs, receipts, run state, and digests are evidence/process artifacts only.
- The successor simplify result retains SIMP-02 as a non-blocking briefing row and says the earlier active-phase reuse/altitude concern did not reproduce (`runs/2026-09-16-06-simplify-eng/digest.md:29-46`).
- The configured QA matrix still fails on two surfaces outside the signed task set (`notes/review-harness-qa-c0.md:7-14,47-52`). Focused green commands cannot override either those matrix failures or missing fail-first evidence.

## Findings

```yaml
findings:
  - id: QA-01
    kind: substance
    reader: harness-qa
    severity: high
    concrete_failure: "The configured unit command fails because tests/unit/omp-hooks.test.ts:1261 expects null but receives undefined; the implicated feature-record surface is outside T-01..T-05."
    ownership: { classification: scope_change }
    evidence: "notes/review-harness-qa-c0.md:11,49"
  - id: QA-02
    kind: substance
    reader: harness-qa
    severity: high
    concrete_failure: "The configured integration command fails factory case L: a stale-station audit fixture exits 0 with zero findings instead of exit 1 with a STATUS finding."
    ownership: { classification: scope_change }
    evidence: "notes/review-harness-qa-c0.md:12,50"
  - id: QA-03
    kind: form
    reader: harness-qa
    severity: high
    concrete_failure: "The evidence record lacks a non-empty fail-first entry for each automated SC-01..SC-14, so the BRIEF's explicit fail-before-pass conjunct is not discharged."
    ownership: { tasks: [T-01, T-02, T-03, T-04] }
    evidence: "notes/review-harness-qa-c0.md:28-45,51"
  - id: QA-04
    kind: coverage
    reader: harness-qa
    severity: medium
    concrete_failure: "No execution-bound test proves that plan mutation makes zero GitHub network writes, leaving SC-10's hidden-network clause unverified."
    ownership: { tasks: [T-02, T-03] }
    evidence: "notes/review-harness-qa-c0.md:39,52"
  - id: CR-01
    kind: substance
    reader: harness-code-reviewer
    severity: high
    concrete_failure: "gh_board.project grades 3 below the production bar 4, so a future eligibility change must enter an already over-complex projection and can silently omit or over-include cards."
    ownership: { tasks: [T-01] }
    evidence: "notes/review-harness-code-reviewer-c0.md:18"
  - id: CR-02
    kind: substance
    reader: harness-code-reviewer
    severity: high
    concrete_failure: "test-check-state-inv26._inv26_fixture grades 1 below the test bar 3, making a new miss-case setup liable to alter unrelated fixture dimensions without isolating the intended behavior."
    ownership: { tasks: [T-01] }
    evidence: "notes/review-harness-code-reviewer-c0.md:19"
  - id: CR-03
    kind: substance
    reader: harness-code-reviewer
    severity: medium
    concrete_failure: "The lifecycle checkpoint-order test grades 2 because its linear mutant table has high ABC; this is advisory because the setup has little control-flow complexity."
    ownership: { tasks: [T-03] }
    evidence: "notes/review-harness-code-reviewer-c0.md:20"
  - id: SIMP-02
    kind: simplification
    reader: harness-ai-dev
    severity: low
    concrete_failure: "board_lifecycle.py keeps identical STATION and STATUS repair branches, so later changes to arguments, ordering, or error handling can drift between them."
    ownership: { tasks: [T-04] }
    disposition: "non-blocking briefing row in the current successor simplify PASS"
    evidence: "notes/receipt-harness-ai-dev-2026-09-16-06-simplify-eng.md:7-14; runs/2026-09-16-06-simplify-eng/digest.md:24,31-41"
```

## Open questions and touched files

```yaml
open_questions:
  - id: Q1
    question: "The successor simplify run recorded a non-blocking harness-tooling defect in structured yield/report-issue handling; it does not affect the lifecycle outcome, but remains a process issue."
    blocking: false
files_touched:
  - .harness/harness/features/BUG-1699-lifecycle-cards/notes/research-BUG-1699-lifecycle-cards-goalcheck-validate-c0.md
expertise_update: []
```
