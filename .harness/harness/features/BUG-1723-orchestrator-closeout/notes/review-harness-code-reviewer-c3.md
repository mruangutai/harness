# Code review — BUG-1723-orchestrator-closeout — c3

**PASS.** Both review stages pass for the exact complete feature range `1a1c1925171803db8ac7f7464560a3767fa902a8..6999227750f68b3ec9c8f77a3ae4f281310742a9`; the range contains no `[harness:human]` commit.

Relay instruction, verbatim: `DECISIONS.md/-INDEX.md are now on T-03's declared files: (amended and re-signed); DEC-159's clause matches ledger.md and check-state.py (all-stations INV-43). INV-43 lines for BUG-1723 itself and BUG-285-canonical-reader in check-state output are the specified census.`

## Stage 1 — spec compliance: PASS

Every executable and playbook change traces to T-01/SC-01–02, T-02/SC-03/D-02, or T-03/SC-04. The c3 amendment is also in scope: T-03 now declares `.harness/harness/docs/DECISIONS.md` and `DECISIONS-INDEX.md` (`plan.yaml:166-185`), and the approved plan was re-signed on 2026-09-16. The generated index matches `gen-decisions-index.py --stdout` byte-for-byte.

The former C1-V01 is closed. DEC-159 says retrospective succession is “a violation at every station, `done` included” and unreadable chronology is CANNOT VERIFY (`DECISIONS.md:3815-3820`). That matches the ledger's all-stations contract (`references/ledger.md:51-59`) and the executable, which appends every in-era INV-43 hit to `bad` without a station exemption (`check-state.py:3023-3064`).

The specified census is correct from the pinned records and INV-43's ordered matching rule. BUG-1723 has `handoff-plan.md` at seq-1, first later run `validate-validator` at 05:21:45, and its first succession at 05:39:33: one INV-43 line. BUG-285 has qualifying handoffs at seq-3, seq-26 and seq-27: the seq-3 succession precedes run 4, while seq-26/27 successions at 18:53:25 and 20:17:42 postdate runs 27/28 at 17:00:04 and 18:07:42: two INV-43 lines for that feature. Its seq-28 handoff has no later run and is correctly outside the census.

SC-04 inspection passes: the orchestrator skill presents one `close-run`, its stage order and named first refusal, then keeps `STATE.md`, handoff and commit separate and quarantine wake-only (`.claude/skills/harness/SKILL.md:79-96`); build-phase repeats the separate-write/wake rule and phase-seam order (`references/build-phase.md:8-12,67-71`); ledger does the same under Runs and Judgements (`references/ledger.md:9-32,51-59`). SC-05 remains the approved post-shipment UAT and is not presently due.

Prior findings: C1-V01 is closed by the aligned, declared and re-signed DEC-159/index change; C1-V02 remains closed by the distinct judgement/public-spend fail-first receipts; C1-V03 remains closed by the public `cmd_close_run` spend refusal exercise. QA c2's verifier question is answered by the documented Python invocation error and does not alter the exact-pin review contract.

## Stage 2 — code quality: PASS with grade-2 notes

Fail-open review found no surviving defect. `close-run` validates shape and the recorded persona before mutation, executes digest → run-end → optional station → optional judgement → spend, propagates the first authority's nonzero exit and diagnostics, and never enters later stages after refusal (`feature-record.py:340-416`). INV-43 refuses unreadable instants, compares aware instants, and routes every in-era hit to the violation list including terminal features (`check-state.py:2857-2870,3023-3064`).

The pinned complexity audit has no high record. Two test functions are grade 2 and non-gating: `case_inv43_chronology` (cyclomatic 6, cognitive 2, ABC 27.2; ABC driver) is one cohesive chronology/order matrix; `CloseRunTest.test_spend_stage_refusal_through_close_run_names_spend_keeps_earlier_writes` (cyclomatic 1, cognitive 0, ABC 29.5; ABC driver) is one linear public-path refusal/retained-state scenario.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Both stages pass at 69992277: T-03 declares the re-signed decision surfaces, DEC-159 matches all-stations INV-43, and the specified two-feature census is exact"
  severity_max: med
  findings:
    - { kind: substance, scope: task, severity: med, reader: code-reviewer, task: T-02, summary: "case_inv43_chronology is grade 2", why: "Cyclomatic 6, cognitive 2, ABC 27.2 (ABC driver); one cohesive chronology and ordered-handoff matrix is clearer than splitting its observable cases." }
    - { kind: substance, scope: task, severity: med, reader: code-reviewer, task: T-01, summary: "public spend-refusal regression is grade 2", why: "Cyclomatic 1, cognitive 0, ABC 29.5 (ABC driver); one linear public-path refusal and retained-state scenario keeps the stage-order contract visible." }
  must_fix: []
  spec_violations: []
  code_grade: grade_2
  grade_2_reasons:
    - "case_inv43_chronology: cyclomatic 6, cognitive 2, ABC 27.2 (ABC driver); cohesive chronology/order matrix."
    - "CloseRunTest.test_spend_stage_refusal_through_close_run_names_spend_keeps_earlier_writes: cyclomatic 1, cognitive 0, ABC 29.5 (ABC driver); linear public-path refusal and retained-state scenario."
  reviewed: "1a1c1925171803db8ac7f7464560a3767fa902a8..6999227750f68b3ec9c8f77a3ae4f281310742a9"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1723-orchestrator-closeout/.harness/harness/features/BUG-1723-orchestrator-closeout/notes/review-harness-code-reviewer-c3.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1723-orchestrator-closeout/.harness/harness/features/BUG-1723-orchestrator-closeout/notes/review-harness-code-reviewer-c3.md
```
