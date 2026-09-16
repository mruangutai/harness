# Goal-check — BUG-1725-task-file-overlap — c1

## BLUF

At review SHA `b317f9a54f7f5f6570e0d36b1a46601357a02ec9`, SC-01 is met, but SC-02, SC-03, and SC-04 are not met. The overlap behavior is green and discriminates the pre-fix checker, but SC-02's required exit-code assertion was already green before the fix. The two inspection criteria name `.agents/...` objects that do not exist at the pinned SHA. No tests were run by this goal-check reader; automated evidence is cited from QA's single matrix run and fail-first replay.

## Success-criterion status

| SC | Verdict | Method | Evidence |
|---|---|---|---|
| SC-01 | met | automated | `notes/review-harness-qa-c1.md:34-45,72-74` records the pinned integration case green and the pre-fix checker red on the overlap assertions. The pinned case covers normalized plain, symbol, and quote anchors, one advisory per shared path, single-task repetition, and overlap beside an existing failure at `tests/integration/test-plan-merge.py:2954-3005`. |
| SC-02 | not_met | automated | `notes/review-harness-qa-c1.md:38-47,72-74` records the pinned exit-0 assertion green, but the same assertion green against the pre-fix checker. The criterion requires that assertion to fail before the fix; it does not discriminate the pre-fix state. |
| SC-03 | not_met | inspection | The mandated `git show b317f9a54f7f5f6570e0d36b1a46601357a02ec9:.agents/skills/harness-spec-driven/SKILL.md` exits 128 because the object is absent (`notes/review-harness-qa-c1.md:76-80`; independently corroborated by `notes/review-harness-code-reviewer-c1.md:11-20`). |
| SC-04 | not_met | inspection | The mandated `git show b317f9a54f7f5f6570e0d36b1a46601357a02ec9:.agents/skills/harness/teams/plan.yaml` exits 128 because the object is absent (`notes/review-harness-qa-c1.md:76-80`; independently corroborated by `notes/review-harness-code-reviewer-c1.md:11-20`). |

## Perspective grades

- **operator — partial — SC-01, SC-02:** SC-01 is met, but SC-02's required fail-first proof is absent, so the operator perspective is not fully discharged.
- **code maintainer — fail — SC-03, SC-04:** neither carrying inspection criterion can read its required immutable object at the pinned SHA; this perspective is undischarged.

## Findings

- **GC-01 — high — kind: substance — SC-02:** the exit-0 assertion passes both before and after the overlap implementation. A future reader cannot produce the criterion's required fail-first evidence from this assertion (`notes/review-harness-qa-c1.md:38-47,72-74`).
- **GC-02 — high — kind: substance — SC-03:** the exact immutable `.agents/skills/harness-spec-driven/SKILL.md` object required by the approved criterion is absent at the pin, so the criterion cannot be inspected (`notes/review-harness-qa-c1.md:48,76-80`).
- **GC-03 — high — kind: substance — SC-04:** the exact immutable `.agents/skills/harness/teams/plan.yaml` object required by the approved criterion is absent at the pin, so the criterion cannot be inspected (`notes/review-harness-qa-c1.md:49,76-80`).
- **QA-01 — high — kind: substance — matrix gate:** independently of the perspective grading, the required unit-kind matrix command has a named assertion failure (`notes/review-harness-qa-c1.md:17-29,56-60`).

## Trace coverage

T-01 traces SC-01 through SC-04 (`plan.yaml:26-48`), so no SC is orphaned. The approved BRIEF declares no REQ identifiers. Trace presence does not cure the three unmet criteria.

## Standard handoff

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Only SC-01 is met; SC-02 lacks its required fail-first proof and both pinned inspection paths are absent."
  feasibility: clear
  surface: S
  flags: [verification, immutable-path, qa-matrix]
  recommend: reframe
  tasks: 1
  decisions: 0
  needs_approval: true
  risk: high
  sc_status:
    - { id: SC-01, verdict: met, method: automated, evidence: "notes/review-harness-qa-c1.md:34-45,72-74" }
    - { id: SC-02, verdict: not_met, method: automated, evidence: "notes/review-harness-qa-c1.md:38-47,72-74" }
    - { id: SC-03, verdict: not_met, method: inspection, evidence: "notes/review-harness-qa-c1.md:48,76-80" }
    - { id: SC-04, verdict: not_met, method: inspection, evidence: "notes/review-harness-qa-c1.md:49,76-80" }
  open_questions: []
  files_touched:
    - .harness/harness/features/BUG-1725-task-file-overlap/notes/research-BUG-1725-task-file-overlap-goalcheck-validate-c1.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1725-task-file-overlap/.harness/harness/features/BUG-1725-task-file-overlap/notes/research-BUG-1725-task-file-overlap-goalcheck-validate-c1.md
```
