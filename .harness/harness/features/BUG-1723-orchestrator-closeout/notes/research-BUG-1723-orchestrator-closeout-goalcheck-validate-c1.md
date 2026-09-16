# BUG-1723 goal-check — validate c1

## Conclusion

FAIL at pinned review SHA `c700a71e5f513a483f33e495cd3aa559cdd2ee78`. SC-01, SC-03, and SC-04 are met; SC-02 remains partial because its new judgement/spend refusal arms lack the required pre-change fail-first evidence and the spend case bypasses the public `close-run` composition it is meant to defend. SC-05 is deliberately deferred until the first complete plan mission after shipment, not unmet. The V-01 runtime correction and V-03 producer binding work, and the required matrix is green, but `ledger.md` still states the removed terminal-note rule.

## Authority and scope

- Reviewed SHA: `c700a71e5f513a483f33e495cd3aa559cdd2ee78`; range: `1a1c1925171803db8ac7f7464560a3767fa902a8..c700a71e5f513a483f33e495cd3aa559cdd2ee78`. No evidence was taken from a later `HEAD`.
- `BRIEF.md` and `plan.yaml` are approved. The findings fit approved T-01/T-03 surfaces, so `needs_approval: false`.
- QA ran the scoped commands at the pin: direct T-01 passed 48 tests, direct T-02 passed all cases, unit passed 40 files, and integration passed 72 files (`notes/review-harness-qa-c1.md:28-38`).
- The INV-43 violations emitted for BUG-1723-orchestrator-closeout and BUG-285-canonical-reader are the expected honest census produced by the V-01 fix, not regressions (`notes/receipt-main-session-fix-c1.md:3`; `notes/review-harness-qa-c1.md:38`).

## Perspective grades — exactly one line per declared perspective

- **pass — orchestrator** — SC-01 and SC-04 are met: the pinned command closes a run in one public invocation and the three pinned playbook files keep `STATE.md`, handoff, and commit separate while leaving quarantine at wake time.
- **pass — operator** — SC-03 is met: INV-43 now violates for retrospective succession at both `review` and `done`, stays silent at earlier/equal timestamps, and fails closed on unusable chronology; SC-05 remains deliberately deferred until the first complete post-shipment plan mission and therefore does not downgrade this perspective.
- **partial — code maintainer** — SC-02 is partial: the judgement refusal is behaviorally exercised, but neither new late-stage arm has the required pre-change fail-first receipt and the spend refusal test calls private `_stage` rather than proving the public composition's spend-stage binding; the permanent ledger also contradicts the corrected terminal behavior.

## Success-criterion status

- **SC-01 — met (automated).** `c700a71:tests/unit/test-feature-record.py#CloseRunTest` covers one-line spend success, paired task/station plus judgement, exact `n_a`, digest/argument/run refusal, and retained earlier writes. The original six cases are red against the pre-change command (`notes/receipt-main-session-T-01-fail-first.md:6-16`), and QA records 48 passing direct tests at the pin (`notes/review-harness-qa-c1.md:15,30-33`).
- **SC-02 — partial (automated).** The pinned judgement test drives `close-run` and checks the named refusal, nonzero schema exit, retained run-end, absent judgement, and no spend summary (`c700a71:tests/unit/test-feature-record.py:259-271`). The pinned spend test calls `_stage("spend", ...)` directly (`c700a71:tests/unit/test-feature-record.py:273-291`), so changing `_close_run_stages` to name the actual tuple `summary` would leave that test and success tests green while a public refusal reports the wrong stage. In addition, the sole fail-first receipt predates and does not name either new test arm (`notes/review-harness-qa-c1.md:18-21,40-44`).
- **SC-03 — met (automated).** `c700a71:tests/integration/test-check-state-feat59.py#case_inv43_chronology`, `#case_inv43_unreadable`, and `#case_inv43_scope` cover after/before/equal ordering, multiple handoffs, unreadable fields, and both `done` and `review`; `check-state.py:3056-3064` sends every in-era hit to violations. The retrospective and unreadable cases were red before INV-43 (`notes/receipt-main-session-T-02-fail-first.md:6-17`), and QA records the pinned cases passing (`notes/review-harness-qa-c1.md:17,30-38`).
- **SC-04 — met (inspection).** At `c700a71`, `.claude/skills/harness/SKILL.md` under `Adjust and record`, `.claude/skills/harness/references/build-phase.md` under the opening close rule and `The seam out of this phase`, and `.claude/skills/harness/references/ledger.md` under `Runs` present one `close-run`, first-refusal handling, separate `STATE.md`/handoff/commit writes, and wake-time quarantine. The required T-03 inspection passes (`notes/review-harness-qa-c1.md:34`).
- **SC-05 — deferred / not yet verifiable by design (uat).** Per `BRIEF.md:25-30`, evidence is collected only from the first complete plan mission after shipment: exported orchestrator OMP JSONL must show at most eight model calls per dispatch, median `.message.usage` context below 100,000 tokens, and zero retrospective succession judgements. That mission has not occurred; this is deliberately deferred evidence, not an unmet outcome.

## Findings and must-fix

- **GC-C1-01 — kind: substance; severity: high; task: T-03.** `c700a71:.claude/skills/harness/references/ledger.md:52-57` still says terminal INV-43 is a note while `check-state.py:3056-3064` and the terminal tests now make it a violation. Concrete failure scenario: an orchestrator reads the shipped ledger, expects a terminal retrospective succession to leave `check-state` clean, but the executable exits nonzero; the V-01 terminal-note expectation was not replaced across its operator authority. **Must fix:** change the ledger's terminal guidance to match the approved all-stations violation contract.
- **GC-C1-02 — kind: substance; severity: med; task: T-01.** The c1 judgement and spend tests are absent from `receipt-main-session-T-01-fail-first.md:6-13`, so SC-02's each-refusal-case fail-first clause remains unproven. Concrete failure scenario: the new assertions pass now, but the record cannot establish that either test distinguishes the pre-change command rather than merely documenting already-green behavior. **Must fix:** capture both named c1 refusal cases failing against the pre-change command, then passing at the review pin.
- **GC-C1-03 — kind: substance; severity: med; task: T-01.** The spend-refusal test invokes private `_stage("spend", ...)` instead of the public `close-run` stage plan. Concrete failure scenario: `_close_run_stages` labels its spend tuple `summary`; successful close-out still prints spend and the private test still passes, but a real spend refusal says `REFUSED at stage summary`, violating SC-02's named-first-stage contract. **Must fix:** route an injected spend-authority refusal through `close-run`, or otherwise assert the actual public stage plan and required `spend` name discriminatingly.

Prior V-03 is closed: step 6 names recorded `code_grade: n_a`, the producer test binds the heading by stable lead words, and the pinned integration matrix passes. No finding is raised for the expected BUG-1723/BUG-285 INV-43 census.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Orchestrator and operator pass, but code maintainer remains partial: SC-02 evidence is incomplete and the shipped ledger contradicts terminal INV-43 behavior."
  feasibility: clear
  surface: M
  flags: [regression-evidence, documentation-contract]
  recommend: proceed
  tasks: 3
  decisions: 2
  needs_approval: false
  risk: med
  sc_status:
    - { id: SC-01, verdict: met, method: automated, evidence: "notes/review-harness-qa-c1.md:15,30-33; notes/receipt-main-session-T-01-fail-first.md:6-16" }
    - { id: SC-02, verdict: partial, method: automated, evidence: "c700a71:tests/unit/test-feature-record.py:259-291; notes/review-harness-qa-c1.md:18-21,40-44; notes/review-harness-code-reviewer-c1.md:7-12" }
    - { id: SC-03, verdict: met, method: automated, evidence: "notes/review-harness-qa-c1.md:17,30-38; notes/receipt-main-session-T-02-fail-first.md:6-17" }
    - { id: SC-04, verdict: met, method: inspection, evidence: "c700a71:.claude/skills/harness/SKILL.md#Adjust and record; c700a71:.claude/skills/harness/references/build-phase.md#The seam out of this phase; c700a71:.claude/skills/harness/references/ledger.md#Runs" }
    - { id: SC-05, verdict: deferred_not_yet_verifiable, method: uat, evidence: "BRIEF.md:25-30 — first complete plan mission after shipment has not occurred" }
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1723-orchestrator-closeout/.harness/harness/features/BUG-1723-orchestrator-closeout/notes/research-BUG-1723-orchestrator-closeout-goalcheck-validate-c1.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1723-orchestrator-closeout/.harness/harness/features/BUG-1723-orchestrator-closeout/notes/research-BUG-1723-orchestrator-closeout-goalcheck-validate-c1.md
```
