# FEAT-1714 goal-check — validation cycle 1

## Review identity and evidence bound

Reviewed exactly `33f45262a9346b62a0e81d3a21786ab2b761cf4e..8090ce0b0fd8eb9d12c63df83ef9cb45a7b38125`; every implementation and test citation below names immutable pin `8090ce0b0fd8eb9d12c63df83ef9cb45a7b38125`. The c1 QA artifact became available during grading: it ran the required unit and integration matrices in a detached worktree at the pin, both exit 0 (`notes/review-harness-qa-c1.md:3,9-14`). I did not rerun tests.

## Verdict

**FAIL.** The c0 implementation defects VAL-01/GC-01 and VAL-02/GC-02 are closed at the pin, including the designed first-sync disposition through source tickets. Two automated criteria remain unearned because their regressions are non-discriminating: source-ticket provenance can be deleted without reddening SC-02, and SC-03 does not prove exact final-station order. QA records these as QA-C1-01 and QA-C1-02 (`notes/review-harness-qa-c1.md:16-27,47-57`).

## Perspective grades

- **orchestrator — partial** — The pin supplies the recognised reject return and an executable no-parent first-sync path, but SC-02's required `source_issues` preservation lacks a discriminating automated assertion (`8090ce0b:.claude/skills/harness/SKILL.md:47-69`; `8090ce0b:.claude/skills/harness/bin/gh-sync.py:1886-1919`; `notes/review-harness-qa-c1.md:19,21,31`).
- **operator — partial** — The pinned implementation fails closed and retains the recorded-parent lifecycle, while SC-04 is proven; however SC-03's exact last-mutation clause remains unproven by its automated fixture (`8090ce0b:.claude/skills/harness/bin/gh-sync.py:1873-1884,1921-1967`; `notes/review-harness-qa-c1.md:20,26,32-33`).
- **code maintainer — pass** — The pin has one terminal tuple and the named writers, gates, projections, handoff check, and cleanup classifier consume it without a surviving `TERMINAL_MARKER` (`8090ce0b:.claude/skills/harness/bin/factory_config.py:51`; `8090ce0b:.claude/skills/harness/bin/plan-merge.py:239`; `8090ce0b:.claude/skills/harness/bin/check-domain.py:1320`; `8090ce0b:.claude/skills/harness/bin/check-plan-routes.py:525,545`; `8090ce0b:.claude/skills/harness/bin/check-state.py:105-106`; `8090ce0b:.claude/skills/harness/bin/board_lifecycle.py:528`; `8090ce0b:.claude/skills/harness/bin/gh_board.py:174,240,274`; `8090ce0b:.claude/skills/harness/bin/handoff_done_when.py:277`; `8090ce0b:.claude/skills/harness/bin/worktree_terminal.py:416`).

## Success-criterion outcomes

- **SC-01 — met — automated.** The pinned integration cases accept numeric and `none` successors and refuse wrong kind, zero/negative/boolean successors, empty/oversized/multiline reasons, missing/extra keys, non-zero cycles, and judgement on another status (`8090ce0b:tests/integration/test-validate-digest.py:1404-1443`); the c1 integration matrix passed (`notes/review-harness-qa-c1.md:11-14,30`).
- **SC-02 — not_met — automated.** The pin directly covers first-sync source-ticket comment/backlog behavior, terminal station, drafted-BRIEF byte identity, INV-44 shape, and terminal worktree classification (`8090ce0b:tests/integration/test-gh-sync-abandon.py:711-750`; `8090ce0b:tests/integration/test-check-state-feat59.py:464-521`; `8090ce0b:tests/integration/test-worktree-terminal.py:862-864`). But the plan assertion compares only newly added lines; deleting or rewriting the original `source_issues: [1714]` remains green, so the criterion's provenance-preservation clause is not proven (`notes/review-harness-qa-c1.md:21,25,31,48`).
- **SC-03 — not_met — automated.** The pinned parent-path cases prove dry-run silence, confirmed close/comment/label/backlog/milestone behavior, no sub-issue mutation, and refusal without station after a numeric label failure (`8090ce0b:tests/integration/test-gh-sync-abandon.py:645-709`). Production sequencing runs all remote steps before `_record_station` (`8090ce0b:.claude/skills/harness/bin/gh-sync.py:1932-1967`), but the success fixture observes only final state: moving the station before a later successful remote write would stay green. The exact “records station rejected last” clause therefore lacks discriminating automated evidence (`notes/review-harness-qa-c1.md:20,26,32,49`).
- **SC-04 — met — automated.** The pinned INV-44 cases separately prove the conforming zero-cycle shape and rejection of non-zero cycles, zero/two runs, lead ownership, missing reject judgement, approved plan, signed BRIEF, panel, and combined violations (`8090ce0b:tests/integration/test-check-state-feat59.py:464-521`); the c1 integration matrix passed (`notes/review-harness-qa-c1.md:11-14,33`).
- **SC-05 — met — inspection.** `TERMINAL_STATIONS = ("abandoned", "rejected")` is the sole declaration, no `TERMINAL_MARKER` survives at the pin, and the criterion's writer/gate/projection/handoff/cleanup consumers import that set at the cited locations under the code-maintainer grade.

Overall SC status: **partial — 3 met, 2 not met**.

## c0 finding reconciliation

### VAL-01 (former GC-01) — closed

- id: VAL-01
- severity: high
- kind: substance
- owner task: T-02/T-05
- concrete prior scenario: A legitimate first-run intake had no recorded parent, so c0 refused rejection before the promised pre-lead terminal outcome.
- disposition: closed at the pin. The approved first-sync reading is implemented, not treated as a defect: the orchestrator creates a station-only plan when needed; no parent is expected before `open` at build entry; reject posts the reason on every `plan.yaml.source_issues` ticket and returns each card to backlog without close or label; no parent and no source ticket is refused (`8090ce0b:.claude/skills/harness/SKILL.md:47-69`; `8090ce0b:.claude/skills/harness/bin/gh-sync.py:1886-1919`; `8090ce0b:tests/integration/test-gh-sync-abandon.py:711-763`; `notes/review-harness-qa-c1.md:19`). When a recorded parent exists, `_parent_reject_steps` preserves SC-03's close/comment/numeric-label/backlog lifecycle (`8090ce0b:.claude/skills/harness/bin/gh-sync.py:1873-1884`).

### VAL-02 (former GC-02) — implementation defect closed; verification gap replaced

- id: VAL-02
- severity: high
- kind: substance
- owner task: T-02/T-05
- concrete prior scenario: A required GitHub write failed after partial irreversible progress, yet c0 returned success and could record `rejected`.
- disposition: closed as an implementation defect at the pin. Required writes raise `_RejectHalt`; execution stops at the first failure, reports landed and unrun steps, exits 1, and withholds the numeric station; the `none` caller sees the same non-zero result (`8090ce0b:.claude/skills/harness/bin/gh-sync.py:1838-1870,1921-1967`; `8090ce0b:tests/integration/test-gh-sync-abandon.py:689-709`; `notes/review-harness-qa-c1.md:20`). The remaining test inadequacy is the narrower medium QA-C1-02 below, not retention of the high implementation defect.

## Active findings

### QA-C1-01 — source provenance assertion is one-way

- id: QA-C1-01
- severity: medium
- kind: substance
- owner task: T-02/T-05
- concrete scenario: A future station-write change deletes or rewrites `plan.yaml.source_issues`; `tests/integration/test-gh-sync-abandon.py:742-744` still passes because it checks only lines added after the run, so SC-02 is reported green without proving original provenance survived.
- evidence: `8090ce0b:tests/integration/test-gh-sync-abandon.py:711-746`; `notes/review-harness-qa-c1.md:21,25,48,51`.

### QA-C1-02 — final station order is not discriminated

- id: QA-C1-02
- severity: medium
- kind: substance
- owner task: T-02/T-05
- concrete scenario: A future change records station `rejected` before a later successful remote mutation; the parent and first-sync success fixtures read only final state after the subprocess, so they remain green despite violating SC-03's exact last-mutation guarantee. The same coverage finding also lacks a direct `none`-path required-write failure case.
- evidence: `8090ce0b:tests/integration/test-gh-sync-abandon.py:645-709,711-750`; `notes/review-harness-qa-c1.md:20,26,32,49,52`.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "VAL-01 and VAL-02 are closed in implementation, but non-discriminating SC-02 provenance and SC-03 final-order regressions leave two criteria unmet."
  feasibility: clear
  surface: M
  flags: [workflow-integrity, external-api, provenance, test-coverage]
  recommend: halt
  tasks: 5
  decisions: 2
  needs_approval: false
  risk: med
  sc_status:
    - { id: SC-01, verdict: met, method: automated, evidence: "notes/review-harness-qa-c1.md:11-14,30; 8090ce0b:tests/integration/test-validate-digest.py:1404-1443" }
    - { id: SC-02, verdict: not_met, method: automated, evidence: "notes/review-harness-qa-c1.md:21,25,31,48; QA-C1-01 above" }
    - { id: SC-03, verdict: not_met, method: automated, evidence: "notes/review-harness-qa-c1.md:20,26,32,49; QA-C1-02 above" }
    - { id: SC-04, verdict: met, method: automated, evidence: "notes/review-harness-qa-c1.md:11-14,33; 8090ce0b:tests/integration/test-check-state-feat59.py:464-521" }
    - { id: SC-05, verdict: met, method: inspection, evidence: "8090ce0b:.claude/skills/harness/bin/factory_config.py:51 and pinned shared-set consumers cited above" }
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-1714-reject-verb/notes/research-FEAT-1714-reject-verb-goalcheck-validate-c1.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1714-reject-verb/.harness/harness/features/FEAT-1714-reject-verb/notes/research-FEAT-1714-reject-verb-goalcheck-validate-c1.md
```
