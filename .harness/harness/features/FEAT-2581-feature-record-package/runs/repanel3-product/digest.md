# repanel3-product: plan re-panel, cycle 4 (FEAT-2581)

**Verdict: FAIL.** The rewrite closed all four cycle-3 findings, and the one re-read raised 7 new substance findings (6 med, 1 low) and 1 low form finding. Per PL-11 (a) and the dispatch, none of them was applied. Each one is left for the operator to rule on at signature. approval.status is still pending, panel cycle 4 is recorded, and `plan-merge.py check` exited 0.

## What closed
I re-derived each closure from the readers' own notes.

| id | reader | pointer (worktree) |
|---|---|---|
| PF-96cdf9f1 (strict decode) | scope | plan.yaml T-03.verify `cz`, :396+ |
| PF-3882d444 (derived d02# fields) | scope | plan.yaml T-03.verify TB/`sg`/`SO`, `bd==BODY` |
| PF-cf9cf710 (SC-08 `divergence:` records) | scope | plan.yaml T-03.verify record-set equality; BRIEF.md:47 |
| PF-a37e5b40 (readable account) | design | plan.yaml:409, 416–418, 449 |

## Open for the signature (all are recorded in plan.yaml `panel:`)
New in cycle 4. Every finding is the reader's own, unchanged.

| id | sev | kind | reader | summary | pointer |
|---|---|---|---|---|---|
| PF-15af8306 | med | substance | scope | T-03 reports SAME when a one-summary file's non-marker stdout changes | plan.yaml:412–413, 439; BRIEF.md:51, 61–65 |
| PF-40325938 | med | substance | scope | A suite record's claimed file is not bound to its argv or checkout cwd | plan.yaml:407, 410–413, 437 |
| PF-db2ae14a | med | substance | scope | Replacing the checkout root before JUnit parsing can invalidate valid Bun evidence | plan.yaml:408, 411–412, 439 |
| PF-5f54f524 | low | substance | scope | test_change compares text-translated patches, not exact bytes | plan.yaml:399, 419, 445 |
| PF-eec01ba2 | med | substance | design | test_change diff not byte-exact for line-ending changes | plan.yaml:399, 419; BRIEF.md:47 |
| PF-2528cfa8 | med | substance | design | The account can obscure whitespace-only and long binary changes | plan.yaml:409, 418, 449; BRIEF.md:47, 107–108 |
| PF-a688e503 | med | substance | design | The BRIEF understates what the new suite records retain (argv, cwd, raw JUnit XML) | BRIEF.md:119–122; plan.yaml:407, 433, 437, 439 |
| PF-42a75f8f | low | form | scope | Stale "only file/id" wording in T-01 and the BRIEF beside the D-01 exception (OQ-C4-1) | plan.yaml:350, 352–353; BRIEF.md:97, 108–112 |

Carried open findings, which pm did not touch: PF-7999938a (high, D-02 authorization; PL-01 rules it accepted at signature), PF-d35d903d (med) and PF-502d3541 (low), the bun-leg pair that PL-04 keeps.

## Assessment
- **PF-5f54f524 and PF-eec01ba2 are one defect reported by two readers.** Scope rated it low and design rated it med. I recorded both entries with their own severities and changed neither. Rule them together.
- **Five of the seven new substance findings fall on the `suite` record kind that pm added this cycle**: PF-15af8306, PF-40325938, PF-db2ae14a, PF-a688e503, and partly PF-2528cfa8. pm added it to make "every disclosed field derived" hold one boundary past the four findings (OQ-C4-2). The added surface brought in a fresh set of narrower findings. This is the same per-mechanism pattern PL-11 (a) tried to end: keying on invariants closed the four findings, but the derivation machinery is itself new attack surface. **Recommendation for the signature:** rule the seven together, as accept-as-disclosed or as a bounded build-time amendment of T-03. Another plan-time re-read round will not converge.
- **No reader raised a proportionality finding.** should-not-exist was not dispatched: PL-11 (a) names only the scope and design readers. It did not run, and it is not recorded as finding nothing.
- **The prototype gate does not apply.** No reader judged the feature to need end-user interaction. The operator-facing surface is text only (design, Mode A).
- **Goal-check was not re-run.** pm appended a dated addendum (goalcheck-plan.md:315-348) because grade-bearing text changed in apply1.

## pm open questions carried to the operator (non-blocking)
- **OQ-C4-1:** T-01's stale "only file and id" clause. It is the same issue as PF-42a75f8f. T-01 was a non-goal in this run.
- **OQ-C4-2:** the suite records grow notes/measurements/*.jsonl.gz beyond what PL-09 accepted, and the size is unmeasured. The question is whether to re-confirm PL-09 or set a ceiling. The scope reader raised the same question.
- **OQ-C4-3:** T-03's fixed table TB pins 11 (file, symbol) pairs. Should T-01 state that these stay in place?

## Command record (pm record step, verbatim exits)
- `record-panel --cycle 4` exited 0. It ADDED 8 findings and printed `PANEL cycle 4 … APPLIED`.
- `set-panel` exited 0. It resolved exactly PF-96cdf9f1, PF-3882d444, PF-cf9cf710 and PF-a37e5b40, each with resolved_by T-03.
- `check` exited 0: `3 task(s), 14 anchor(s) resolved, 0 failure(s)`.
- The check-state hook also printed VIOLATION lines on each write, none of which gates this step:
  - the BRIEF is unsigned;
  - INV-29 names the FEAT-2557 worktree;
  - INV-37 reports no Build-entry receipt, which is expected at Plan.

Full output: pm's return artifact. The record is in `runs/repanel3-product/state.yaml`, step `record`.

```yaml
VERDICT: FAIL
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/runs/repanel3-product/digest.md
DIGEST:
  headline: 'FAIL: the T-03 invariant rewrite closed all four cycle-3 findings (PF-96cdf9f1,
    PF-3882d444, PF-cf9cf710, PF-a37e5b40), but the one re-read raised 7 new substance
    findings (6 med, 1 low) and 1 low form finding, and 5 of them fall on the new
    suite record kind. None was applied; all go to the signature. approval.status
    is pending, panel cycle 4 is recorded, and check exited 0.'
  team: plan
  steps_run: 4
  cycles_used: 0
  branch: none
  members:
  - step: apply1
    persona: harness-pm
    verdict: PASS
    headline: Rewrote T-03 verify and intent around the four invariants, adding a
      new suite record kind to derive case_set, baseline_failing and FAIL lines. Applied
      PL-03 to D-01.because, and applied PL-01/03/05/09/10 to the BRIEF SC-08, gaps
      and disclosure. approval is pending; 3 open questions, none blocking.
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/plan.yaml
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/BRIEF.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/notes/research-feature-record-package.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/notes/research-FEAT-2581-feature-record-package-goalcheck-plan.md
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: 'Closes PF-96cdf9f1, PF-3882d444 and PF-cf9cf710. The new suite verifier
      can miss required evidence or reject valid JUnit: 3 med and 1 low substance
      findings, plus 1 low form finding.'
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/notes/review-harness-code-reviewer-plan-c4.md
  - step: design
    persona: harness-ui-reviewer
    verdict: FAIL
    headline: "Closes PF-a37e5b40 (plan.yaml:409, 416\u2013418, 449). 3 new med substance\
      \ defects on the disclosure surface: whitespace and binary readability, byte\
      \ exactness of test_change, and a BRIEF understatement of the suite records."
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/notes/review-harness-ui-reviewer-plan-c4.md
  - step: should-not-exist
    persona: fable-advisor
    status: skipped
    reason: 'Not dispatched this cycle: the operator''s ruling PL-11 (a) names the
      scope and design readers only. It did not run, so it found nothing.'
  - step: record
    persona: harness-pm
    verdict: PASS
    headline: record-panel --cycle 4 (exit 0, ADDED 8), set-panel resolved exactly
      the 4 reader-closed findings (exit 0), check found 3 tasks, 14 anchors and 0
      failures (exit 0). approval is pending.
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/plan.yaml
  must_fix:
  - "PF-15af8306 (med, scope): T-03 reports SAME when a one-summary file's non-marker\
    \ stdout changes. Pointer: plan.yaml:412\u2013413, 439; BRIEF.md:51, 61\u2013\
    65."
  - "PF-40325938 (med, scope): a suite record's claimed file is not bound to its argv\
    \ or checkout cwd. Pointer: plan.yaml:407, 410\u2013413, 437."
  - "PF-db2ae14a (med, scope): replacing the checkout root before JUnit parsing can\
    \ invalidate valid Bun evidence. Pointer: plan.yaml:408, 411\u2013412, 439."
  - 'PF-eec01ba2 (med, design) and PF-5f54f524 (low, scope), one defect reported twice:
    test_change compares patches read with text=True, so they are not byte-exact.
    Pointer: plan.yaml:399, 419, 445; BRIEF.md:47.'
  - "PF-2528cfa8 (med, design): the account can obscure whitespace-only and long binary\
    \ changes. Pointer: plan.yaml:409, 418, 449; BRIEF.md:47, 107\u2013108."
  - "PF-a688e503 (med, design): the BRIEF understates what the suite records retain\
    \ (argv, cwd, raw JUnit XML). Pointer: BRIEF.md:119\u2013122; plan.yaml:407, 433,\
    \ 437, 439."
  escalations: []
  open_questions:
  - id: OQ-SIG-C4
    question: 'At signature, rule the 8 open cycle-4 findings, PF-15af8306, PF-40325938,
      PF-db2ae14a, PF-5f54f524, PF-eec01ba2, PF-2528cfa8, PF-a688e503 and PF-42a75f8f
      (form), together with the 3 carried findings PF-7999938a (high, authorized at
      signature per PL-01), PF-d35d903d and PF-502d3541. The lead''s recommendation:
      rule the 7 substance findings together, as accept-as-disclosed or as a bounded
      build-time amendment of T-03. Five of them sit on the suite derivation added
      this cycle, so another plan-time re-read round will not converge.'
    blocking: true
  - id: OQ-C4-1
    question: "Should T-01's stale 'only file and id' clause (plan.yaml:350, 352\u2013\
      353) and the matching BRIEF wording (BRIEF.md:97, 108\u2013112) be reworded\
      \ to match D-01/PL-03? This is the same issue as PF-42a75f8f, and T-01 was a\
      \ non-goal in this run."
    blocking: false
  - id: OQ-C4-2
    question: "The new suite records grow notes/measurements/*.jsonl.gz beyond the\
      \ PL-09 proposal. They add argv, cwd and raw JUnit XML per side, and the size\
      \ is unmeasured. Re-confirm PL-09, or set a ceiling? Disclosed at BRIEF.md:119\u2013\
      122, which PF-a688e503 says understates it."
    blocking: false
  - id: OQ-C4-3
    question: T-03's fixed table TB pins 11 (file, symbol) pairs, and a T-01 rename
      would make T-03 fail closed. Should T-01 state that those symbols stay at their
      paths?
    blocking: false
  adequacy_notes:
  - 'Severities are the readers'' own: the same text=True defect is low (scope, PF-5f54f524)
    and med (design, PF-eec01ba2), and both are recorded unchanged.'
  - The check-state hook printed VIOLATION lines on each write (BRIEF unsigned; INV-29
    on the FEAT-2557 worktree; INV-37 no Build-entry receipt at Plan). None gates
    the plan step, and all three commands exited 0.
  - The goal-check was not re-run. pm appended a dated addendum at notes/research-FEAT-2581-feature-record-package-goalcheck-plan.md:315-348
    because grade-bearing text changed.
  - 'Prototype gate: not required. The design reader judged the surface text-only
    (Mode A), and no end-user interaction is involved.'
  sc_status:
  - id: PF-96cdf9f1
    verdict: closed
    method: plan reader (scope), one read
    evidence: notes/review-harness-code-reviewer-plan-c4.md; plan.yaml T-03.verify
      cz strict decode :396+; set-panel resolved_by T-03
  - id: PF-3882d444
    verdict: closed
    method: plan reader (scope), one read
    evidence: notes/review-harness-code-reviewer-plan-c4.md; T-03.verify TB/sg/SO,
      bd==BODY; set-panel resolved_by T-03
  - id: PF-cf9cf710
    verdict: closed
    method: plan reader (scope), one read
    evidence: 'notes/review-harness-code-reviewer-plan-c4.md; divergence: record-set
      equality; BRIEF.md:47; set-panel resolved_by T-03'
  - id: PF-a37e5b40
    verdict: closed
    method: plan reader (design), one read
    evidence: "notes/review-harness-ui-reviewer-plan-c4.md; plan.yaml:409, 416\u2013\
      418, 449; set-panel resolved_by T-03"
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps:
  - should-not-exist (fable-advisor) did not read the cycle-4 text, including the
    new suite record kind, because PL-11 (a) excluded it.
  findings:
  - reader: scope
    kind: substance
    scope: none
    severity: med
    summary: T-03 reports SAME when a one-summary file's non-marker stdout changes.
    why: "PF-15af8306. Worktree plan.yaml:412\u2013413, 439 compares whole stdout\
      \ only for unnamed files, contrary to BRIEF.md:51, 61\u201365. Open, not applied."
  - reader: scope
    kind: substance
    scope: none
    severity: med
    summary: A suite record's claimed file is not bound to its argv or checkout cwd.
    why: "PF-40325938. Worktree plan.yaml:407, 410\u2013413, 437 never consumes argv\
      \ or cwd. Open, not applied."
  - reader: scope
    kind: substance
    scope: none
    severity: med
    summary: Replacing the checkout root before JUnit parsing can invalidate otherwise
      valid Bun evidence.
    why: "PF-db2ae14a. Worktree plan.yaml:408, 411\u2013412, 439. Open, not applied."
  - reader: scope
    kind: substance
    scope: none
    severity: low
    summary: The new test_change check compares text-translated patches, not exact
      patch bytes.
    why: PF-5f54f524. Worktree plan.yaml:399, 419, 445; BRIEF.md:47. Same defect as
      PF-eec01ba2. Open, not applied.
  - reader: scope
    kind: form
    scope: none
    severity: low
    summary: 'OQ-C4-1: T-01 and the BRIEF retain stale only-language beside the explicit
      D-01 exception.'
    why: "PF-42a75f8f. Worktree plan.yaml:350, 352\u2013353; BRIEF.md:97, 108\u2013\
      112. Left unfixed because its T-01 half is a non-goal of this run. Open."
  - reader: design
    kind: substance
    scope: none
    severity: med
    summary: The mandatory account can obscure whitespace-only and long binary changes.
    why: "PF-2528cfa8. plan.yaml:409, 418, 449; BRIEF.md:47, 107\u2013108. Open, not\
      \ applied."
  - reader: design
    kind: substance
    scope: none
    severity: med
    summary: The newly verified test_change diff is not byte-exact for line-ending
      changes.
    why: PF-eec01ba2. plan.yaml:399, 419; BRIEF.md:47. Open, not applied.
  - reader: design
    kind: substance
    scope: none
    severity: med
    summary: The BRIEF discloses growth beyond PL-09 but understates what the new
      suite records retain.
    why: "PF-a688e503. BRIEF.md:119\u2013122; plan.yaml:407, 433, 437, 439. Open,\
      \ not applied."
  readers:
  - reader: scope
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: should-not-exist
    status: skipped
    persona: fable-advisor
    reason: 'status skipped: not dispatched this cycle because the operator''s ruling
      PL-11 (a) names the scope and design readers only.'
  - reader: design
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/plan.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/BRIEF.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/notes/research-feature-record-package.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/notes/research-FEAT-2581-feature-record-package-goalcheck-plan.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/notes/review-harness-code-reviewer-plan-c4.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/notes/review-harness-ui-reviewer-plan-c4.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/runs/repanel3-product/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/runs/repanel3-product/panel-c4.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/runs/repanel3-product/apply1-changes.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/runs/repanel3-product/acceptance-criteria.md
  expertise_update: []
```
