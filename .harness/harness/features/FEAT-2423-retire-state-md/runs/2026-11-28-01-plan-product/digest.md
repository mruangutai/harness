# FEAT-2423 plan run — 2026-11-28-01-plan-product

**BLUF.** BRIEF.md and plan.yaml (7 tasks, all `main-session-direct`) are drafted, panelled and goal-checked, both `pending`. The only blocker is Q-05, which is environmental and is Main's call: this sparse worktree (FEAT-1559) holds no other feature directory. As a result, `plan-merge.py check --root <worktree>` fails on exactly the 40 STATE.md deletion anchors in T-06/T-07. The same check against the main checkout resolves 78/78 with exit 0. Main should widen the sparse checkout over those 40 directories and re-run the check. After that, run `record-panel --digest <this file>` once, per plan-phase.md.

## Artifacts
- BRIEF: `.harness/harness/features/FEAT-2423-retire-state-md/BRIEF.md` (SC-01..SC-10)
- Plan: `.harness/harness/features/FEAT-2423-retire-state-md/plan.yaml` (T-01..T-07; panel recorded c1, 9/9 resolved)
- Reader fan-in: `runs/2026-11-28-01-plan-product/panel-c1.md`
- Scope review: `notes/review-harness-code-reviewer-plan-c1.md`; design review: `notes/review-harness-ui-reviewer-plan-c1.md`
- Goal-check: `notes/research-FEAT-2423-retire-state-md-goalcheck-plan.md` (original grades, then `## Remediation applied`)
- Research: `notes/research-retire-state-md.md`

## Panel outcome
- scope (code-reviewer): FAIL with 3 high and 3 med substance findings and 1 low task-proportionality finding. All 7 are resolved by pm at apply (T-01, T-02, T-03, T-04, T-05, T-07). Under the DEC-123 carve-out this ranks as PASS. The reader found the mission proportionate.
- should-not-exist (fable-advisor): ran. Its one low task-proportionality finding was resolved: SC-06's case is folded into `test-check-domain-post.py` (T-02). The reader found the plan right-sized.
- design (ui-reviewer): in scope through org.html. Its one med finding was resolved: T-04's table now names plan.yaml, feature.json and the digest.
- No `scope: mission` finding was raised, so there is no downgrade recommendation. No severity was lowered.
- goalcheck: graded FAIL on GC-01, because live INV-2/INV-5 prose survived in check_state and tests. I confirmed this at source; it is wider than reported (plan.py lines in 6 places). I sent it back to apply once. T-01 now names 25 mentions in 9 files, and its verify turns red on any survivor. After that, the code-maintainer perspective and the no-orphan constraint pass. The operator and code-maintainer perspectives are otherwise partial only on items that are open questions (GC-02, GC-03).

## Lead assessment
- The three high remedies were applied without a re-read, and each is a literal verify command: the T-01 catalogue rows[-8], rename witness and INV grep; the T-05 Amended-by scope; the T-06/T-07 `set -e -o pipefail` sweep. The signer grades substance, not whether the shell runs. That is why LEAD-01 is a blocking signature question.
- Prototype gate: visual-designer is not in the plan team. My call is that no prototype is needed, because no end-user interaction exists. The only rendered surface is static reference text in org.html. This call can be overridden in either direction.
- Cycles: 1 send-back (apply, after goalcheck). There were no reader loop-backs.

```yaml
VERDICT: ESCALATE
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2423-retire-state-md/.harness/harness/features/FEAT-2423-retire-state-md/runs/2026-11-28-01-plan-product/digest.md
DIGEST:
  headline: 'FEAT-2423 BRIEF and 7-task plan.yaml are pending. All 9 panel findings
    and goal-check GC-01 are resolved. The only blocker is environmental: the worktree''s
    sparse checkout must be widened over the 40 STATE.md dirs so check --root <worktree>
    passes. Against main it passes 78/78.'
  team: plan
  steps_run: 7
  cycles_used: 1
  members:
  - step: draft
    persona: harness-pm
    verdict: ESCALATE
    headline: BRIEF SC-01..SC-10 and plan T-01..T-07 drafted, all main-session-direct;
      the worktree check fails only on 40 sparse deletion anchors (Q-05)
    files_touched:
    - .harness/harness/features/FEAT-2423-retire-state-md/BRIEF.md
    - .harness/harness/features/FEAT-2423-retire-state-md/plan.yaml
    - .harness/harness/features/FEAT-2423-retire-state-md/notes/research-retire-state-md.md
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Mission is proportionate; 3 high gate defects in T-01, T-05 and T-06/T-07,
      plus 3 med and 1 low; all were resolved at apply (DEC-123 carve-out)
    files_touched:
    - .harness/harness/features/FEAT-2423-retire-state-md/notes/review-harness-code-reviewer-plan-c1.md
  - step: should-not-exist
    persona: fable-advisor
    verdict: PASS
    headline: Plan is right-sized; one low finding to fold T-02's new test file into
      the existing check-domain suite, resolved
    files_touched: []
  - step: design
    persona: harness-ui-reviewer
    verdict: PASS
    headline: In scope via org.html; T-04 should name the live records in place of
      the removed pointer, resolved
    files_touched:
    - .harness/harness/features/FEAT-2423-retire-state-md/notes/review-harness-ui-reviewer-plan-c1.md
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: 9/9 findings resolved; record-panel and set-panel exit 0; check exits
      0 on the main root and exit 1 on the worktree, only for the 40 sparse anchors
    files_touched:
    - .harness/harness/features/FEAT-2423-retire-state-md/BRIEF.md
    - .harness/harness/features/FEAT-2423-retire-state-md/plan.yaml
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: 'Plan delivers the intent except GC-01: live INV-5 prose survives in
      check_state/plan.py and its tests with no verify to catch it'
    files_touched:
    - .harness/harness/features/FEAT-2423-retire-state-md/notes/research-FEAT-2423-retire-state-md-goalcheck-plan.md
  - step: apply-r1
    persona: harness-pm
    verdict: PASS
    headline: 'GC-01 closed: T-01 names all 25 live INV-2/INV-5 mentions in 9 files
      and its verify turns red on any survivor; the goal-check note is re-graded'
    files_touched:
    - .harness/harness/features/FEAT-2423-retire-state-md/plan.yaml
    - .harness/harness/features/FEAT-2423-retire-state-md/notes/research-FEAT-2423-retire-state-md-goalcheck-plan.md
  must_fix: []
  files_touched:
  - .harness/harness/features/FEAT-2423-retire-state-md/BRIEF.md
  - .harness/harness/features/FEAT-2423-retire-state-md/plan.yaml
  - .harness/harness/features/FEAT-2423-retire-state-md/notes/research-retire-state-md.md
  - .harness/harness/features/FEAT-2423-retire-state-md/notes/review-harness-code-reviewer-plan-c1.md
  - .harness/harness/features/FEAT-2423-retire-state-md/notes/review-harness-ui-reviewer-plan-c1.md
  - .harness/harness/features/FEAT-2423-retire-state-md/notes/research-FEAT-2423-retire-state-md-goalcheck-plan.md
  - .harness/harness/features/FEAT-2423-retire-state-md/runs/2026-11-28-01-plan-product/state.yaml
  - .harness/harness/features/FEAT-2423-retire-state-md/runs/2026-11-28-01-plan-product/panel-c1.md
  - .harness/harness/features/FEAT-2423-retire-state-md/runs/2026-11-28-01-plan-product/criteria.md
  branch: none
  open_questions:
  - id: Q-05
    question: 'Main: plan-merge.py check --root <worktree> exits 1, and all 40 failures
      are T-06/T-07 STATE.md deletion anchors outside the sparse cone (FEAT-1559).
      Run with --root /Users/molchairuangutai/GitHub/harness it exits 0 with 78/78.
      Recommendation: run `git -C <worktree> sparse-checkout add` over the 40 feature
      directories listed in T-06/T-07 files:, re-run check, then record-panel --digest
      on this run''s digest.md. Dropping the deletions would orphan SC-01. Harness
      gap: no plan can own another feature''s file while check reads only the sparse
      disk.'
    blocking: true
  - id: LEAD-01
    question: 'Operator at signature: three high scope findings were remedied at apply
      and no reader re-read them. Each remedy is a literal verify command: T-01''s
      catalogue rows[-8], rename witness and INV-2/5 grep; T-05''s Amended-by ban,
      scoped to DEC-129/150; and the T-06/T-07 `set -e -o pipefail` deletion sweep.
      T-01''s new grep has only been observed red at base; its green path was never
      observed. Recommendation: sign, and have the executing main session confirm
      each verify block runs green on the landed tree before review_sha is pinned.'
    blocking: true
  - id: Q-01
    question: 'When does the build start relative to FEAT-2643, which edits check_state/ctx.py,
      plan.py and feature_record.py in other symbols? Recommendation: start after
      FEAT-2643 merges, rebasing first.'
    blocking: false
  - id: Q-02
    question: 'FEAT-2641, FEAT-2688 and BUG-2524 each keep a STATE.md in their worktree.
      Recommendation: this feature merges first, and each of them runs git rm on its
      copy before it merges. No re-add gate is added, so review is the only catch.'
    blocking: false
  - id: Q-03
    question: 'Should the 40th tracked copy, .harness/kaya/features/FEAT-01-kaya-platform/STATE.md,
      be deleted? The grilling scoped served trees out, but the constraint says no
      STATE.md under any feature dir. Recommendation: delete it in T-07, as drafted.
      If you keep it, T-07 states how to amend its files and verify.'
    blocking: false
  - id: Q-04
    question: 'Expertise entries harness-validator-lead G-01 and harness-code-reviewer
      G-05 still name STATE.md, and DEC-145/253 bar build tasks from editing them.
      Recommendation: this feature''s distillation recommends drop to each. Decide
      whether that drop is a ship condition (goalcheck GC-02).'
    blocking: false
  - id: Q-06
    question: 'SC-03 allows exactly two test functions to name the file: case_stray_status_file_is_inert
      (test-check-state-table.py, SC-05) and run_retired_status_file_is_ungated (test-check-domain-post.py,
      SC-06). This relaxes the constraint that no test mentions it. Recommendation:
      accept, because proving the gates ignore a stray file needs a fixture by that
      name.'
    blocking: false
  - id: GC-03
    question: 'The plan keeps dated mentions as historical record under DEC-205: DEC-121/160/173/180/182
      narrative, shipped runs/notes/plans and BUILD.md. This narrows the grilling
      Destination''s ''no decision or feature directory mentions the file''. Recommendation:
      acknowledge the narrowing. Optionally add a decisions_affected keep row for
      DEC-182''s dated INV-3/4/5 narrative.'
    blocking: false
  - id: Q-07
    question: 'Possible harness defect, reported twice by pm: plan-merge.py apply
      given an empty stdin proposal printed APPLIED and exited 0 with no change. Recommendation:
      file an issue so apply refuses an empty or no-op proposal.'
    blocking: false
  escalations: []
  expertise_update: []
  adequacy_notes:
  - The draft returned ESCALATE only for Q-05, which is environmental. I checked the
    draft against send-back criteria written before dispatch (criteria.md) and ran
    the reader wave on the unchanged text, because Main was waiting on this run and
    the plan text does not depend on the sparse cone.
  - The goal-check ran once, as the team requires. Its FAIL was GC-01 only, which
    I confirmed at source (check_state/plan.py carries INV-5 in 6 places). One send-back
    to apply closed it, and the note records both the original grades and a Remediation
    applied section.
  - 'Prototype gate: visual-designer is not a plan-team step. My call is that no prototype
    is needed, because there is no end-user interaction; the only rendered surface
    is static reference text in org.html. This can be overridden in either direction.'
  - 'No scope: mission finding was raised, so there is no downgrade recommendation.
    No reader severity was lowered.'
  sc_status:
  - id: SC-01..SC-10
    verdict: not_met
    method: inspection
    evidence: 'plan stage: each SC is traced by at least one of T-01..T-07; goal-check
      grades perspectives orchestrator and reader as pass, operator and code-maintainer
      as partial only on open questions GC-02/GC-03 (notes/research-FEAT-2423-retire-state-md-goalcheck-plan.md)'
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps:
  - T-01's new INV-2/5 verify block has been observed red at base (25 hits); its green
    path is not yet observed (pm Q-GC01-green)
  findings:
  - reader: scope
    severity: high
    kind: substance
    scope: none
    summary: T-01 breaks the existing catalogue assertion and weakens the rename witness
    why: INV-44 moves from rows[-6] to rows[-8]; renaming BRIEF away leaves inv_1
      silent. Resolved by T-01.
    exposure:
      trigger: routine
      vs_today: regression
      control: harness
  - reader: scope
    severity: high
    kind: substance
    scope: none
    summary: T-05 rejects existing DEC-182 wording its intent does not change
    why: Amended-by ban across DEC-182 refuses three existing headings. Resolved by
      T-05 (ban limited to DEC-129/150).
    exposure:
      trigger: routine
      vs_today: regression
      control: harness
  - reader: scope
    severity: high
    kind: substance
    scope: none
    summary: T-06/T-07 verification can exit zero with a tracked STATE.md still present
    why: Failed absence checks did not stop the block and a git error read as an empty
      list. Resolved by T-07 (set -e -o pipefail, bound assertions).
    exposure:
      trigger: routine
      vs_today: regression
      control: harness
  - reader: scope
    severity: med
    kind: substance
    scope: none
    summary: T-05 omits active DEC-180 clauses and incompletely updates DEC-181 and
      DEC-199
    why: Live INV-23 parity and budget claims survived. Resolved by T-05 (amend rows
      added).
    exposure:
      trigger: plausible
      vs_today: regression
      control: harness
  - reader: scope
    severity: med
    kind: substance
    scope: none
    summary: T-03/T-04 under-specify the digest read at first entry and wake
    why: A fresh feature has no accepted digest. Resolved by T-03 and SC-02/SC-10
      wording.
    exposure:
      trigger: plausible
      vs_today: regression
      control: harness
  - reader: scope
    severity: med
    kind: substance
    scope: none
    summary: T-03 runs the wake suite before T-05 changes both files it tests
    why: test-lead-stop-and-wake.py binds DECISIONS.md and its index. Resolved by
      moving the suite to T-05.
    exposure:
      trigger: plausible
      vs_today: regression
      control: harness
  - reader: scope
    severity: low
    kind: proportionality
    scope: task
    summary: T-02 needlessly rewrites the subject of a historical measurement
    why: The eeabc59 reproduction measured a 204-line status file. Resolved by T-02
      trim.
    exposure:
      trigger: routine
      vs_today: regression
      control: harness
  - reader: should-not-exist
    severity: low
    kind: proportionality
    scope: task
    summary: T-02's new dedicated file tests/unit/test-check-domain-state-retired.py
      should be cases in the existing check-domain integration suites, not a new pseudo-unit
      file
    why: House precedent places retirement-inertness cases in the subject's existing
      suite. Resolved by T-02 (case moved into test-check-domain-post.py; SC-06 evidence
      integration).
    exposure:
      trigger: routine
      vs_today: no_worse
      control: harness
  - reader: design
    severity: med
    kind: substance
    scope: none
    summary: T-04 removes the org reference table's only explicit state and open-question
      pointer without naming the live records.
    why: A reader resuming a feature would lose the pointer. Resolved by T-04 (rows
      name plan.yaml, feature.json, digest).
    exposure:
      trigger: plausible
      vs_today: regression
      control: harness
  readers:
  - reader: scope
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: should-not-exist
    status: ran
    persona: fable-advisor
    reason: none
  - reader: design
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
```
