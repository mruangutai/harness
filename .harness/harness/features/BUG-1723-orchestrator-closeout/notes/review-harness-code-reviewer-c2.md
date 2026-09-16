# Code review — BUG-1723-orchestrator-closeout — c2

**FAIL.** At exact pin `972d5c054e6a1dbab811f957ff5d5186a7445f63`, the PM finding is correct: the BUG-1723 addition to DEC-159 says terminal INV-43 is only a note, while the pinned ledger and executable make it a violation at every station. This supersedes this note's initial claim that C1-V01 was closed.

## Stage 1 — spec compliance: FAIL

The complete pinned range is `1a1c1925171803db8ac7f7464560a3767fa902a8..972d5c054e6a1dbab811f957ff5d5186a7445f63`; it has no `[harness:human]` commit.

- **C1-V01 survives — mismatch and scope creep (SC-03/D-02).** The pinned DEC-159 BUG-1723 clause says a retrospective succession is “a violation on a live feature, a note on one at a terminal station” (`972d5c05:.harness/harness/docs/DECISIONS.md:3815-3818`). The pinned ledger instead says it “is a violation at every station, `done` included” (`972d5c05:.claude/skills/harness/references/ledger.md:52-59`), and the executable appends every in-era INV-43 hit to `bad` even for terminal features (`972d5c05:.claude/skills/harness/bin/check-state.py:3058-3064`). The two permanent authorities therefore define opposite terminal behavior.
- **Concrete failure scenario.** A maintainer follows the feature's new DEC-159 clause while changing or diagnosing INV-43 and restores or expects the terminal-note exemption. A retrospective succession on a `done` feature then sails through as advisory even though the approved all-stations ledger/check-state contract requires it to block, reopening the exact phase-seam fail-open this feature closes.
- **Task/scope status.** This is not bound to an approved task file: `.harness/harness/docs/DECISIONS.md` is absent from T-01, T-02, and T-03. The range nevertheless adds the contradictory BUG-1723 mechanism clause there. Correcting DEC-159 (and regenerating its index if required) is a source-scope change requiring operator approval; it must not be silently charged to T-03.
- **Other c1 findings remain closed.** C1-V02's judgement/spend fail-first receipts and C1-V03's public spend-stage wiring evidence remain valid; this reconciliation does not disturb them.
- **SC-04 inspection still passes.** The three specified playbook files present `close-run`, keep `STATE.md`, handoff, and commit separate, and keep quarantine at wake time (`972d5c05:.claude/skills/harness/SKILL.md:79-93`; `972d5c05:.claude/skills/harness/references/build-phase.md:9-12,67-71`; `972d5c05:.claude/skills/harness/references/ledger.md:9-32`). SC-05 remains `deferred_not_yet_verifiable` as approved.

Because stage 1 fails, stage 2 is not entered. The already-run pinned complexity audit is preserved as mechanical evidence: it reported no high record and two justified grade-2 test functions — `case_inv43_chronology` (cyclomatic 6, cognitive 2, ABC 27.2, ABC driver) and `CloseRunTest.test_spend_stage_refusal_through_close_run_names_spend_keeps_earlier_writes` (cyclomatic 1, cognitive 0, ABC 29.5, ABC driver).

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Stage 1 fails at 972d5c05: pinned DEC-159 grants terminal INV-43 a note exemption that the pinned all-stations ledger and executable reject"
  severity_max: high
  findings:
    - { kind: substance, scope: task, severity: high, reader: code-reviewer, task: none, scope_change: true, needs_approval: true, summary: "C1-V01 survives because the new DEC-159 clause contradicts terminal INV-43 enforcement", why: "A maintainer following DEC-159 can restore or expect a terminal-note exemption, causing retrospective succession on done features to sail through instead of blocking; DECISIONS.md belongs to no approved task, so correction requires operator-approved scope expansion." }
    - { kind: substance, scope: task, severity: med, reader: code-reviewer, task: T-02, summary: "case_inv43_chronology is grade 2", why: "Cyclomatic 6, cognitive 2, ABC 27.2 (ABC driver); the cohesive chronology matrix is clearer than assertion helpers." }
    - { kind: substance, scope: task, severity: med, reader: code-reviewer, task: T-01, summary: "public spend-refusal regression is grade 2", why: "Cyclomatic 1, cognitive 0, ABC 29.5 (ABC driver); one linear scenario best exposes stage ordering and retained-state failure." }
  must_fix:
    - "Obtain operator approval to add the DEC-159 authority surface to scope, then make its terminal INV-43 contract agree with the approved all-stations ledger/check-state behavior and update its generated index if required."
  spec_violations:
    - { kind: mismatch, path: .harness/harness/docs/DECISIONS.md, ref: "SC-03/D-02" }
    - { kind: scope_creep, path: .harness/harness/docs/DECISIONS.md, ref: "SC-03/D-02" }
  code_grade: grade_2
  grade_2_reasons:
    - "case_inv43_chronology: cyclomatic 6, cognitive 2, ABC 27.2 (ABC driver); one cohesive chronology boundary/ordering matrix."
    - "CloseRunTest.test_spend_stage_refusal_through_close_run_names_spend_keeps_earlier_writes: cyclomatic 1, cognitive 0, ABC 29.5 (ABC driver); one linear public-path refusal and retained-state scenario."
  reviewed: "1a1c1925171803db8ac7f7464560a3767fa902a8..972d5c054e6a1dbab811f957ff5d5186a7445f63"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Will the operator approve expanding scope to correct the BUG-1723 DEC-159 clause and regenerate DECISIONS-INDEX.md if required?", blocking: true }
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1723-orchestrator-closeout/.harness/harness/features/BUG-1723-orchestrator-closeout/notes/review-harness-code-reviewer-c2.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1723-orchestrator-closeout/.harness/harness/features/BUG-1723-orchestrator-closeout/notes/review-harness-code-reviewer-c2.md
```
