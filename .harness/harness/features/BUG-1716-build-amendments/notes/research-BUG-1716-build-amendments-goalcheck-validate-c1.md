# BUG-1716 build amendments — goal-check validate c1

## Scope

- Review SHA: `f602c7eee7761ce4325accba7a04678794c7ed69`
- Merge base: `33f45262a9346b62a0e81d3a21786ab2b761cf4e`
- Reviewed range: `33f45262a9346b62a0e81d3a21786ab2b761cf4e..f602c7eee7761ce4325accba7a04678794c7ed69`
- Inputs: `BRIEF.md`, `plan.yaml`, `feature.json`, `notes/receipt-main-session-fix-c1.md`, `runs/validate-validator/digest.md`, the c0 PM goal-check note, the complete pinned diff, and the independent c1 QA and code-review notes.

## Verdict

**FAIL.** Six of seven success criteria are met, but SC-02 is not met. The plan is replaced before the ledger write, and `_record_amendments_locked` restores the plan only when the ledger writer raises `harness_merge.MergeRefusal`. Ordinary `OSError` failures exposed by `feature_json_write.write_feature_json` bypass that handler, leaving the amended plan installed without the required ledger judgement. This violates SC-02's atomic mutation outcome and the brief's constraint that every mutation failure leave its target byte-identical.

The gates remain independent: the c1 QA matrix is **PASS**, while the c1 code review and this product goal-check are **FAIL** on the uncovered ordinary-I/O failure path. A passing test suite does not discharge a success criterion contradicted by the pinned implementation.

## Perspective grades

| Perspective | Carrying criteria | Grade | Evidence |
|---|---|---|---|
| End user (engineering lead) | SC-01, SC-06 | pass | Closed amendment schema and eligibility are implemented and covered; BUG-285 fixtures cover apply, validate, and invalid rejection. See `notes/review-harness-qa-c1.md:22,27`. |
| Orchestrator | SC-02 | fail | Non-`MergeRefusal` ledger I/O failure can leave the plan amended without the ledger judgement. See `notes/review-harness-code-reviewer-c1.md:18,43-45`, `plan-merge.py:2239-2259`, and `feature_json_write.py:131-223`. |
| Operator | SC-03, SC-04 | pass | Plan/ledger hashes, INV-40 behavior, exact overrule route, refusal behavior, and ledger-derived rate are implemented and covered. See `notes/review-harness-qa-c1.md:24-25`. |
| Reader (reviewer / QA) | SC-05 | pass | Review contract requires the Stage 1 outcome/decision anchor and repository-derived pinned Stage 2/code-grade evidence. See `notes/review-harness-code-reviewer-c1.md:15,33-35`. |
| Code maintainer | SC-07 | pass | DEC-23/32/157/229/230 and DEC-226 precedent consistently encode the amendment lifecycle and three independent checks. See `notes/review-harness-code-reviewer-c1.md:15,33-35`. |

## Success-criterion grades

| Criterion | Verdict | Method | Evidence |
|---|---|---|---|
| SC-01 | met | automated | `notes/review-harness-qa-c1.md:22`; `tests/integration/test-validate-digest.py:603-651`; `.claude/skills/harness/bin/amendment_contract.py:1-98`; `.omp/agents/harness-eng-lead.md:100-128`. |
| SC-02 | not_met | inspection | `notes/review-harness-code-reviewer-c1.md:18,43-45`; `plan-merge.py:2239-2259`; `feature_json_write.py:131-223`. The rollback catches only `harness_merge.MergeRefusal`; ordinary ledger I/O failures can escape after the plan replacement. |
| SC-03 | met | automated | `notes/review-harness-qa-c1.md:24`; `tests/integration/test-plan-merge.py:3647-3695`; `tests/integration/test-check-state.py:440-496`; `check-state.py:2875-2942`. |
| SC-04 | met | automated | `notes/review-harness-qa-c1.md:25`; `tests/unit/test-feature-record.py:245-288`; `feature-record.py:208-260`; `.claude/skills/harness/references/briefing.md:29-39`. |
| SC-05 | met | inspection | `notes/review-harness-code-reviewer-c1.md:15,33-35`; `.claude/skills/harness-code-review/SKILL.md:34-50`; `validate-digest.py:784-979`. |
| SC-06 | met | automated | `notes/review-harness-qa-c1.md:27`; `tests/integration/test-validate-digest.py:597-604`; `tests/integration/test-plan-merge.py:3711-3725`. |
| SC-07 | met | inspection | `notes/review-harness-code-reviewer-c1.md:15,33-35`; `DECISIONS.md:255-270,360-371,3613-3635,7415-7499`. |

## Prior aggregate findings V-01 through V-08

| Finding | Kind | c1 disposition | Independent reassessment |
|---|---|---|---|
| V-01 | substance | **open** | The new lock-refusal test covers `MergeRefusal`, but the implementation restores the plan only for that exception class. An ordinary `OSError` from the ledger write still leaves a partial commit. See `notes/review-harness-code-reviewer-c1.md:18,43-45`. |
| V-02 | substance | closed | Shared amendment validation is centralized in `amendment_contract.py`; c1 code-grade and source review report no surviving violation. See `notes/review-harness-code-reviewer-c1.md:19,27-35`. |
| V-03 | substance | closed | The relevant validation path was decomposed below the enforced code-grade thresholds. See `notes/review-harness-code-reviewer-c1.md:20,27-35`. |
| V-04 | substance | closed | The relevant record path was decomposed below the enforced code-grade thresholds. See `notes/review-harness-code-reviewer-c1.md:21,27-35`. |
| V-05 | substance | closed | The relevant merge path was decomposed below the enforced code-grade thresholds. See `notes/review-harness-code-reviewer-c1.md:22,27-35`. |
| V-06 | substance | closed | The relevant state-check path was decomposed below the enforced code-grade thresholds. See `notes/review-harness-code-reviewer-c1.md:23,27-35`. |
| V-07 | substance | closed | Remaining graded Python functions pass at the pinned SHA (`PASSING:87`). See `notes/review-harness-code-reviewer-c1.md:24,27-35`. |
| V-08 | substance | closed | The corrective refactors preserve the specified behavior and pass the assigned pinned code-grade check. See `notes/review-harness-code-reviewer-c1.md:25,27-35`. |

## Finding

### GC-c1-01 — ledger I/O errors can bypass amendment rollback

- **kind:** substance
- **severity:** high
- **criterion:** SC-02
- **task:** T-04
- **failure scenario:** `record-amendments` replaces the plan successfully; the subsequent ledger tempfile write, fsync, or `os.replace` raises `OSError`; the handler catches only `harness_merge.MergeRefusal`; the command exits with the amended plan installed but no ledger judgement.
- **required remedy:** make every ledger-write failure after plan replacement restore the original plan bytes while the plan lock remains held, then preserve or translate the original failure without masking rollback failure. Add focused evidence for an ordinary ledger I/O exception, not only lock refusal.
- **evidence:** `plan-merge.py:2239-2259`; `feature_json_write.py:131-223`; `notes/review-harness-code-reviewer-c1.md:18,43-45`.

## Harness digest

```yaml
VERDICT: FAIL
DIGEST:
  headline: "SC-02 fails at f602c7e because ordinary ledger I/O errors bypass rollback and can leave a partial amendment commit."
  feasibility: clear
  surface: L
  flags: [bugfix, task-amendments, atomicity]
  recommend: proceed
  tasks: 9
  decisions: 8
  needs_approval: false
  risk: high
  sc_status:
    - { id: SC-01, verdict: met, method: automated, evidence: "notes/review-harness-qa-c1.md:22; tests/integration/test-validate-digest.py:603-651" }
    - { id: SC-02, verdict: not_met, method: inspection, evidence: "notes/review-harness-code-reviewer-c1.md:18,43-45; plan-merge.py:2239-2259; feature_json_write.py:131-223" }
    - { id: SC-03, verdict: met, method: automated, evidence: "notes/review-harness-qa-c1.md:24; tests/integration/test-plan-merge.py:3647-3695; tests/integration/test-check-state.py:440-496" }
    - { id: SC-04, verdict: met, method: automated, evidence: "notes/review-harness-qa-c1.md:25; tests/unit/test-feature-record.py:245-288" }
    - { id: SC-05, verdict: met, method: inspection, evidence: "notes/review-harness-code-reviewer-c1.md:15,33-35; .claude/skills/harness-code-review/SKILL.md:34-50" }
    - { id: SC-06, verdict: met, method: automated, evidence: "notes/review-harness-qa-c1.md:27; tests/integration/test-validate-digest.py:597-604; tests/integration/test-plan-merge.py:3711-3725" }
    - { id: SC-07, verdict: met, method: inspection, evidence: "notes/review-harness-code-reviewer-c1.md:15,33-35; DECISIONS.md:255-270,360-371,3613-3635,7415-7499" }
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1716-build-amendments/.harness/harness/features/BUG-1716-build-amendments/notes/research-BUG-1716-build-amendments-goalcheck-validate-c1.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1716-build-amendments/.harness/harness/features/BUG-1716-build-amendments/notes/research-BUG-1716-build-amendments-goalcheck-validate-c1.md
```
