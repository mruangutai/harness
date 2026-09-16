# Code review — BUG-1723-orchestrator-closeout — c0

**FAIL.** Reviewed pinned range `1a1c1925171803db8ac7f7464560a3767fa902a8..e23646776b1cf1d1833ca0b7cab5da12272eba7b` (merge-base of `origin/main`; no `[harness:human]` commits). Stage 1 failed; per protocol stage 2 did not run.

## Stage 1 — spec compliance

1. **High · substance · T-02 · mismatch (SC-03/D-02).** `.claude/skills/harness/bin/check-state.py:3058-3067` changes terminal-feature INV-43 hits from `bad` to `warn`. If succession is recorded after the first later-phase run and the feature later reaches `done`, `check-state.py` exits clean instead of reporting T-02's required violation. The terminal-note test at `tests/integration/test-check-state-feat59.py:437-463` codifies the mismatch.
2. **Med · substance · T-01 · omission (SC-02).** `tests/unit/test-feature-record.py:228-258` covers digest and station refusals but never makes judgement or spend refuse. A regression that continues after either late-stage refusal remains green, so SC-02's “each refusal case” fail-first/no-later-stage evidence is incomplete.

SC-04 inspection passes at `.claude/skills/harness/SKILL.md:79-93`, `.claude/skills/harness/references/build-phase.md:9-12,67-71`, and `.claude/skills/harness/references/ledger.md:9-32,52-57`. SC-05 is deferred by design, not unmet.

## Code grade

The canonical grader reported 21 passing symbols and `grade_2` for `tests/integration/test-check-state-feat59.py:396 case_inv43_chronology`: cyclomatic 6, cognitive 2, ABC 27.2, driver ABC, test bar 3. The receipt at `.harness/harness/features/BUG-1723-orchestrator-closeout/notes/receipt-main-session-T-02-fail-first.md:19-21` adequately names the function and metrics and explains that its cohesive after/before/equal/two-handoff matrix would otherwise split into a one-assertion helper without added meaning.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "T-02 lets terminal retrospective succession sail through, and T-01 omits required late-stage refusal evidence"
  severity_max: high
  findings:
    - { kind: substance, scope: task, severity: high, reader: code-reviewer, task: T-02, summary: "INV-43 becomes non-gating after terminal status", why: "A postdated succession on a later-terminal feature is warned rather than failed, so check-state exits clean." }
    - { kind: substance, scope: task, severity: med, reader: code-reviewer, task: T-01, summary: "SC-02 lacks judgement/spend refusal evidence", why: "Continuing after either late-stage refusal would remain green." }
  must_fix:
    - "T-02: remove the terminal-state downgrade and replace the terminal-note expectation."
    - "T-01: add focused fail-first-derived judgement and spend refusal cases."
  spec_violations:
    - { kind: mismatch, path: .claude/skills/harness/bin/check-state.py, ref: D-02 }
    - { kind: omission, path: tests/unit/test-feature-record.py, ref: SC-02 }
  code_grade: grade_2
  grade_2_reasons:
    - "case_inv43_chronology: cyclomatic 6, cognitive 2, ABC 27.2 (ABC driver); one cohesive chronology boundary/ordering matrix, and splitting the ordering assertion would add a meaningless helper."
  reviewed: "1a1c1925171803db8ac7f7464560a3767fa902a8..e23646776b1cf1d1833ca0b7cab5da12272eba7b"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1723-orchestrator-closeout/.harness/harness/features/BUG-1723-orchestrator-closeout/notes/review-harness-code-reviewer-c0.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1723-orchestrator-closeout/.harness/harness/features/BUG-1723-orchestrator-closeout/notes/review-harness-code-reviewer-c0.md
```
