# Code review — BUG-1723-orchestrator-closeout — c1

**FAIL.** Reviewed pinned range `1a1c1925171803db8ac7f7464560a3767fa902a8..c700a71e5f513a483f33e495cd3aa559cdd2ee78` (merge-base of `origin/main`; no `[harness:human]` commits). Stage 1 still has one T-01 evidence omission, so stage 2 did not run.

## Stage 1 — spec compliance

V-01 is fixed: `.claude/skills/harness/bin/check-state.py:3056-3064` now sends every in-era INV-43 hit to `bad`, including terminal features, and `tests/integration/test-check-state-feat59.py:437-463` discriminates `done` and `review` violations. The named BUG-1723 and BUG-285 INV-43 reports are the required honest census, not regressions.

V-03 is fixed: `.claude/skills/harness/SKILL.md:87-92` explicitly names the recorded `code_grade: n_a` field, while `tests/integration/test-check-state-plans.py:554-557` binds the producer check to step 6 by its stable lead words and checks that field within the step.

1. **Med · substance · T-01 · omission (SC-02; V-02 incomplete).** `tests/unit/test-feature-record.py:273-294` calls the private `_stage("spend", ...)` directly rather than invoking `close-run`, so it proves the generic subprocess wrapper but not that the public composition wires the spend refusal under the required stage name. If `_close_run_stages` changes the actual tuple to `("summary", spend_argv, None)`, the success test still prints spend, the new refusal test still passes, but a real spend read refusal is reported as `REFUSED at stage summary` rather than naming `spend`. Bind the injected failure through `close-run` (or otherwise assert the actual stage plan) so the named-first-stage contract is discriminating. This is owned by T-01; no plan upgrade is recommended.

SC-04 inspection passes: `.claude/skills/harness/SKILL.md:79-93`, `.claude/skills/harness/references/build-phase.md:9-12,67-71`, and `.claude/skills/harness/references/ledger.md:9-32,52-57` present `close-run`, preserve the three separate writes, and retain wake-time quarantine. SC-05 remains deliberately deferred to UAT.

## Stage 2 — code quality

Not run because stage 1 failed. The pinned-range mechanical Python grader was still run as the required audit claim: 23 symbols pass and `tests/integration/test-check-state-feat59.py:396 case_inv43_chronology` remains grade 2 (cyclomatic 6, cognitive 2, ABC 27.2; ABC driver; test bar 3). The existing rationale remains adequate: the function is one cohesive after/before/equal/two-handoff chronology matrix, and splitting it would add a one-assertion helper without reducing conceptual load.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "V-01 and V-03 are fixed, but V-02 still bypasses close-run and cannot detect a misnamed spend refusal stage"
  severity_max: med
  findings:
    - { kind: substance, scope: task, severity: med, reader: code-reviewer, task: T-01, summary: "Spend-refusal evidence bypasses the public close-run composition", why: "If the actual spend tuple is renamed to summary, success and the private _stage test remain green while a spend refusal names the wrong first failing stage." }
  must_fix:
    - "T-01: make the spend-refusal case exercise or discriminatingly bind the actual close-run spend-stage wiring, including the required stage name."
  spec_violations:
    - { kind: omission, path: tests/unit/test-feature-record.py, ref: SC-02 }
  code_grade: grade_2
  grade_2_reasons:
    - "case_inv43_chronology: cyclomatic 6, cognitive 2, ABC 27.2 (ABC driver); one cohesive chronology boundary/ordering matrix, and splitting it would add a meaningless one-assertion helper."
  reviewed: "1a1c1925171803db8ac7f7464560a3767fa902a8..c700a71e5f513a483f33e495cd3aa559cdd2ee78"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1723-orchestrator-closeout/.harness/harness/features/BUG-1723-orchestrator-closeout/notes/review-harness-code-reviewer-c1.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1723-orchestrator-closeout/.harness/harness/features/BUG-1723-orchestrator-closeout/notes/review-harness-code-reviewer-c1.md
```
