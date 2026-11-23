# BUG-2399 original plan panel

Scope found the mission proportionate and no actionable findings. Design self-scoped out. The fable-advisor's requested findings block is transcribed below; its external response also supplied a wrapper with differing summaries/persona metadata, which is not substituted for that requested block. Both findings are task-scoped; neither requests a mission downgrade. PM applies them in this run without another reader cycle.

Reader notes: `notes/review-harness-code-reviewer-plan-c0.md`; `notes/review-harness-ui-reviewer-plan-c0.md`. External reader: `agent://Bug2399PlanProduct2.ProductivePartridge` (requested findings preserved here).

```yaml
DIGEST:
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: Pending plan scope and architecture reviewed; mission fits, no findings.
    - reader: should-not-exist
      status: ran
      persona: fable-advisor
      reason: Independent pending-plan critique returned two task-scoped findings.
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: Mode A self-scoped out; no visual UI, DESIGN.md or prototype applicable.
  severity_max: med
  findings:
    - reader: should-not-exist
      summary: 'The parameterized, test-extractable migration program embedded in checkout-upgrade.md (T-01/T-02) is a shipped tool where grilling settled only "document an operator step"; its safety machinery defends against failure modes that are already safe refusals.'
      severity: med
      kind: proportionality
      scope: task
      why: >-
        Grilling settled the upgrade path as "either backfill them into git or document an
        operator step"; the BRIEF/plan escalated that into an executable block inside a
        markdown reference, extracted and run by test-merge-gitignore.py against legacy
        fixtures with five refusal cases, whitespace/metacharacter filenames, NUL manifests
        and hashes stored outside the repository, re-enumeration diffing and disappearance
        detection. Verified the downside of a sloppy operator with a plain documented
        checklist: once the rule narrows, historical evidence is untracked dirt that
        merge-gate.py (:422) and feature-worktree remove GATE 2 refuse — safe halts, not
        data loss; UI and locks stay ignored so cannot be mis-staged; nothing in the plain
        path deletes bytes. The incremental safety of the embedded program over "run
        merge-gitignore, git status, review, git add the run records, commit separately"
        is marginal, while markdown-embedded scripts kept runnable by test extraction are
        a permanent maintenance coupling (doc edit = test break) for a once-per-checkout
        migration. Keep the operator doc and the merger --check regressions; drop the
        extractable-program contract and its dedicated fixture battery, or shrink it to
        asserting the doc's commands compose correctly.
    - reader: should-not-exist
      summary: T-03's notes/changelog.md is a fourth restatement of the tracking policy with no established reader and no precedent.
      severity: low
      kind: substance
      scope: task
      why: >-
        Verified no changelog.md exists under any of the 27 prior feature dirs at the
        control plane, and the plan itself records "the researched tree has no established
        release changelog". Its planned content (ordinary tracking, operator migration,
        distill ordering, ABORTED protection) lands in the same task in the new DEC,
        SPEC 2.5 and references/distillation.md. A policy note nobody's tooling or
        workflow reads is drift surface, not record; the DEC is the record.
```
