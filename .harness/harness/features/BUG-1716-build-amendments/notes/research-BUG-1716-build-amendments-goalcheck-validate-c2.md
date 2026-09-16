# BUG-1716 build amendments — goal-check validate c2

## Scope and conclusion

- Review SHA: `e348b40d5bba915a6131be37de728947da990deb`
- Complete reviewed range: `33f45262a9346b62a0e81d3a21786ab2b761cf4e..e348b40d5bba915a6131be37de728947da990deb`
- Inputs: pinned `BRIEF.md`, `plan.yaml`, `feature.json`, and `STATE.md`; `notes/receipt-main-session-fix-c2.md`; all four c1 reader notes; the c1 PM goal-check; `runs/fix-c1-validator/digest.md`; the complete pinned implementation and tests; and the independent c2 QA, code, security, and UI notes.

**PASS.** All five declared perspectives pass and SC-01 through SC-07 are met at the exact pin. The only c1 blocking class, V-01, is closed. I independently inspected the Git objects rather than inheriting the receipt: `_record_amendments_locked` now handles both `MergeRefusal` and every other exception from the post-splice ledger write while the plan lock is held, `_restore_plan` either restores the captured bytes or emits a distinct actionable restore-failure line, and the retained `PermissionError` case asserts both files byte-identical. QA independently executed that case at the pin; code review independently inspected the same path and the complete diff.

## Perspective grades

| Perspective | Carrying criteria | Grade | Evidence |
|---|---|---|---|
| End user (engineering lead) | SC-01, SC-06 | pass | The closed five-key shape, three eligibility conditions, same-run route, and blocking fallback are present at `.omp/agents/harness-eng-lead.md:100-128`; the three BUG-285 specimens are accepted and applied at `tests/integration/test-validate-digest.py:597-651` and `tests/integration/test-plan-merge.py:3699-3730`. |
| Orchestrator | SC-02 | pass | One command splices only named fields, ledgers each entry, preserves approval, and needs no product/task re-dispatch (`plan-merge.py:2075-2305`; `.claude/skills/harness/SKILL.md:128-135`). The former ordinary-I/O gap is closed by `plan-merge.py:2239-2271` and its executed regression at `test-plan-merge.py:3933-3958`. |
| Operator | SC-03, SC-04 | pass | Signing hashes each task deterministically, INV-40 names unledgered changes and their remedy, exact-timestamp overrule mutates one live amendment, and the briefing derives the rate from the ledger (`plan-merge.py:2031-2069`; `check-state.py:2904-2942`; `feature-record.py:208-260`; `briefing.md:30-39`). |
| Reader (reviewer / QA) | SC-05 | pass | Stage 1 uses amendments only as a departure map and anchors on BRIEF plus decisions; Stage 2 and code-grade recompute from the pinned diff (`harness-code-review/SKILL.md:34-50`; `notes/review-harness-code-reviewer-c2.md:9-15,38-40`). |
| Code maintainer | SC-07 | pass | The scripts share one amendment contract and the cited decisions consistently define authority, approval survival, run-not-cycle accounting, the six-kind ledger, DEC-226 precedent, and the three independent checks (`amendment_contract.py:1-98`; `DECISIONS.md:255-270,360-371,3613-3635,7415-7499`). |

## Success-criterion grades

| Criterion | Verdict | Method | Evidence |
|---|---|---|---|
| SC-01 | met | automated | QA PASS at `notes/review-harness-qa-c2.md:20-29`; exercised contract at `tests/integration/test-validate-digest.py:603-651`; direct pinned inspection of `.omp/agents/harness-eng-lead.md:100-128` and `amendment_contract.py:16-98`. |
| SC-02 | met | automated | QA PASS at `notes/review-harness-qa-c2.md:16-29`; exact splice/isolation/ledger/refusal cases at `tests/integration/test-plan-merge.py:3711-3840,3909-3958`; direct pinned inspection of the all-exception rollback and loud restore path at `plan-merge.py:2239-2271`. |
| SC-03 | met | automated | QA PASS at `notes/review-harness-qa-c2.md:20-29`; deterministic hashes at `tests/integration/test-plan-merge.py:3647-3695`; INV-40 detection, remedy, and matching-amendment silence at `tests/integration/test-check-state-feat59.py:440-496`. |
| SC-04 | met | automated | QA PASS at `notes/review-harness-qa-c2.md:20-29`; exact selection and byte-identical refusals at `tests/unit/test-feature-record.py:245-288`; ledger-derived `overruled/total` and `0/0` at `.claude/skills/harness/references/briefing.md:30-39`. |
| SC-05 | met | inspection | Independent code-review PASS at `notes/review-harness-code-reviewer-c2.md:9-15,38-40`; direct pinned contract at `.claude/skills/harness-code-review/SKILL.md:34-50` and repository-derived code-grade enforcement at `validate-digest.py:781-979`. |
| SC-06 | met | inspection | Independent code-review inspection at `notes/review-harness-code-reviewer-c2.md:9-13`; direct pinned fixtures contain and apply all three exact recommendations at `tests/integration/test-validate-digest.py:597-604` and `tests/integration/test-plan-merge.py:3699-3730`. |
| SC-07 | met | inspection | Independent code-review inspection at `notes/review-harness-code-reviewer-c2.md:9-15`; direct pinned authority at `.harness/harness/docs/DECISIONS.md:255-270,360-371,3613-3635,7415-7499`. |

## V-01 remeasurement

At `plan-merge.py:2256-2271`, the plan bytes are captured and replaced under the plan lock; a ledger `MergeRefusal` and every other `BaseException` both call `_restore_plan` before leaving that lock. At `plan-merge.py:2239-2247`, restoration success explicitly reports byte-for-byte recovery, while an `OSError` during restoration explicitly says the plan could not be restored, identifies the unjudged amendment state, and directs restoration from Git.

At `tests/integration/test-plan-merge.py:3933-3958`, mode `000` on `feature.json.lock` causes `PermissionError` after the plan splice. The case asserts a nonzero diagnostic naming the exception with no traceback, the restore message, and equality of both original byte strings. QA reports that this arm executed and passed at the pin (`notes/review-harness-qa-c2.md:16-18`); code review independently confirms reverting to the former narrow catch makes the case expose a traceback and changed plan (`notes/review-harness-code-reviewer-c2.md:19-23`). V-01 is closed. V-02 through V-08 remain closed.

## Nonblocking reader advisories considered

These are not new PM findings and do not falsify the approved SC wording, but they remain in the independent security record:

- **kind:** substance; **severity:** med; **owning task:** T-05. **Scenario:** after one legitimate amendment judgement names a task, a writer with an existing governed plan-write route can later alter another signed field on that task without a new INV-40 warning because coverage is task-level. Evidence: `notes/review-harness-security-reviewer-c2.md:14,37`.
- **kind:** substance; **severity:** med; **owning task:** T-04. **Scenario:** a writer with an existing governed mutation route can alter an approved legacy plan lacking `signed_task_hashes`; approval survives while INV-40 skips the absent mapping. Evidence: `notes/review-harness-security-reviewer-c2.md:15,38`.

Both require pre-existing governed repository-write capability, add no privilege, and are outside the signed-hash behavior SC-03 states. Security therefore returns PASS with `must_fix: []` (`notes/review-harness-security-reviewer-c2.md:25-39`). UI independently finds no rendered surface (`notes/review-harness-ui-reviewer-c2.md:3-11`).

## Harness digest

```yaml
VERDICT: PASS
DIGEST:
  headline: "All five perspectives and SC-01 through SC-07 pass at e348b40d; V-01 is closed by locked all-exception rollback with executed ordinary-I/O byte-identity proof."
  feasibility: clear
  surface: L
  flags: [bugfix, task-amendments, atomicity]
  recommend: proceed
  tasks: 9
  decisions: 8
  needs_approval: false
  risk: med
  sc_status:
    - { id: SC-01, verdict: met, method: automated, evidence: "notes/review-harness-qa-c2.md:20-29; tests/integration/test-validate-digest.py:603-651" }
    - { id: SC-02, verdict: met, method: automated, evidence: "notes/review-harness-qa-c2.md:16-29; plan-merge.py:2239-2271; tests/integration/test-plan-merge.py:3711-3840,3909-3958" }
    - { id: SC-03, verdict: met, method: automated, evidence: "notes/review-harness-qa-c2.md:20-29; tests/integration/test-plan-merge.py:3647-3695; tests/integration/test-check-state-feat59.py:440-496" }
    - { id: SC-04, verdict: met, method: automated, evidence: "notes/review-harness-qa-c2.md:20-29; tests/unit/test-feature-record.py:245-288" }
    - { id: SC-05, verdict: met, method: inspection, evidence: "notes/review-harness-code-reviewer-c2.md:9-15,38-40; .claude/skills/harness-code-review/SKILL.md:34-50" }
    - { id: SC-06, verdict: met, method: inspection, evidence: "notes/review-harness-code-reviewer-c2.md:9-13; tests/integration/test-validate-digest.py:597-604; tests/integration/test-plan-merge.py:3699-3730" }
    - { id: SC-07, verdict: met, method: inspection, evidence: "notes/review-harness-code-reviewer-c2.md:9-15; .harness/harness/docs/DECISIONS.md:255-270,360-371,3613-3635,7415-7499" }
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1716-build-amendments/.harness/harness/features/BUG-1716-build-amendments/notes/research-BUG-1716-build-amendments-goalcheck-validate-c2.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1716-build-amendments/.harness/harness/features/BUG-1716-build-amendments/notes/research-BUG-1716-build-amendments-goalcheck-validate-c2.md
```
