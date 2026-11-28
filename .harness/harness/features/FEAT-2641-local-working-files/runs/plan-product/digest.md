# plan-product — FEAT-2641-local-working-files — team digest

**BLUF: ESCALATE.** BRIEF.md and plan.yaml are drafted, both `pending`, and plan-merge.py check exits 0 (pm's report). The plan has 9 tasks, all main-session-direct under DEC-174, and 10 decisions; it strikes DEC-257 and amends the other affected decisions. All three readers ran. Apply resolved 11 of the 12 panel findings. The one still open is an info-severity agreement from should-not-exist, which does not gate. No reader raised a `scope: mission` proportionality finding, and fable-advisor judged the plan lane proportionate. In-run send-backs: 0.

The run escalates because the operator must rule at signature, not because more planning is needed:
1. **OQ-02 (blocking).** Raised by pm and code-reviewer: protect the working files of shipped-but-undistilled features before the untracking pull removes them from disk.
2. **LEAD-01 (blocking).** Apply remediated six high substance findings and added D-10 (the landing route). This team has no re-read step, so no reader has seen the applied text of T-03, T-05, T-06, T-07 and T-09, including the literal commands in T-09's landing step and T-05's refusal message.
3. **Non-blocking departures from the grilling's Settled lines:**
   - D-07 replaces ship's handoff-validate refusal; the grilling asked for deletion. Raised as OQ-01 and GC-02.
   - On reject-none and declined distill, the caller runs cleanup instead of the station-setting command doing it. Raised as GC-01.

## Per member
| step | persona | verdict | headline | artifact |
|---|---|---|---|---|
| draft | harness-pm | PASS | 16 SCs, 9 tasks, 9 decisions; check exit 0; OQ-01..05 | BRIEF.md, plan.yaml, notes/research-local-working-files.md, notes/research-FEAT-2641-plan-proposal.md |
| scope | harness-code-reviewer | FAIL (draft) | 5 high + 1 med substance, 1 low form: terminal cleanup ordering, distill staging, project-note deletion bounds, ignore-rule cutover, decision clauses | notes/review-harness-code-reviewer-plan-c1.md |
| should-not-exist | fable-advisor | PASS | Nothing should not be built. 1 low task-proportionality finding (GATE 2b output), 1 info form finding (fixture), 1 info agreement | inline; transcribed in panel-c1.md |
| design | harness-ui-reviewer | FAIL (draft) | Reject-none deletes files before the station is written (high). Cleanup-failure reporting is unspecified (med) | notes/review-harness-ui-reviewer-plan-c1.md |
| apply | harness-pm | PASS | 11/12 findings resolved_by tasks; D-10 added; record-panel and check exit 0 | plan.yaml, BRIEF.md |
| goalcheck | harness-pm | PASS | operator partial; code maintainer met; orchestrator met | notes/research-FEAT-2641-local-working-files-goalcheck-plan.md |

## Lead assessment
- **The reader FAILs graded the draft, not the applied plan.** Both were valid returns, so `on_fail` (which covers only an invalid reader return) did not fire. Their findings went to apply.
- **Same defect, two readers.** The code-reviewer and the ui-reviewer both reported the reject-none ordering defect. The panel keeps both, because a finding's identity is its reader plus its summary. One change to T-05 resolved both.
- **The panel in plan.yaml records three readers.** This digest adds `goalcheck`, so the orchestrator should re-record the panel from it (INV-32).
- **Why ESCALATE.** Two members returned FAIL, and worst-wins collation puts ESCALATE above FAIL. The open item is a decision for the operator, not a fix this team could make. The orchestrator may route the run to signature as a pending plan.
- **Possible harness defect (OQ-05).** bash-write-guard refused a scratch git repo under /tmp as a governed kaya write. This goes to the harness owner.

Reader fan-in: runs/plan-product/panel-c1.md. Send-back criteria were written before the first return: runs/plan-product/criteria.md.

```yaml
VERDICT: ESCALATE
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2641-local-working-files/.harness/harness/features/FEAT-2641-local-working-files/runs/plan-product/digest.md
DIGEST:
  headline: FEAT-2641 BRIEF and plan are both pending and plan-merge check passes,
    with 11 of 12 panel findings resolved. The operator must rule at signature on
    OQ-02 (protect the working files of undistilled features) and on whether the high-finding
    remediations, which no reader has seen, need a re-read.
  team: plan
  steps_run: 6
  cycles_used: 0
  members:
  - step: draft
    persona: harness-pm
    verdict: PASS
    headline: 16 SCs, 9 tasks all main-session-direct, 9 decisions; DEC-257 struck,
      others amended; check exit 0
    files_touched:
    - .harness/harness/features/FEAT-2641-local-working-files/BRIEF.md
    - .harness/harness/features/FEAT-2641-local-working-files/plan.yaml
    - .harness/harness/features/FEAT-2641-local-working-files/notes/research-local-working-files.md
    - .harness/harness/features/FEAT-2641-local-working-files/notes/research-FEAT-2641-plan-proposal.md
    - .harness/harness/features/FEAT-2641-local-working-files/observations/harness-pm.md
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: 'Draft: fix terminal cleanup ordering, distill staging, project-note
      deletion bounds, ignore-rule cutover, decision clauses'
    files_touched:
    - .harness/harness/features/FEAT-2641-local-working-files/notes/review-harness-code-reviewer-plan-c1.md
  - step: should-not-exist
    persona: fable-advisor
    verdict: PASS
    headline: 'Nothing here should not be built. Remaining findings: one low task-proportionality,
      one info form, one info agreement'
    files_touched: []
  - step: design
    persona: harness-ui-reviewer
    verdict: FAIL
    headline: 'Draft: reject-none deletes working files before the terminal station
      is written; cleanup-failure reporting unspecified'
    files_touched:
    - .harness/harness/features/FEAT-2641-local-working-files/notes/review-harness-ui-reviewer-plan-c1.md
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: 11 of 12 findings resolved by named tasks; D-10 landing route added;
      record-panel and check exit 0
    files_touched:
    - .harness/harness/features/FEAT-2641-local-working-files/plan.yaml
    - .harness/harness/features/FEAT-2641-local-working-files/BRIEF.md
    - .harness/harness/features/FEAT-2641-local-working-files/observations/harness-pm.md
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: 'Operator perspective partial: the terminal-verb cleanup departure and
      D-07 are not on the record. Code maintainer and orchestrator perspectives met'
    files_touched:
    - .harness/harness/features/FEAT-2641-local-working-files/notes/research-FEAT-2641-local-working-files-goalcheck-plan.md
  must_fix: []
  files_touched:
  - .harness/harness/features/FEAT-2641-local-working-files/BRIEF.md
  - .harness/harness/features/FEAT-2641-local-working-files/plan.yaml
  - .harness/harness/features/FEAT-2641-local-working-files/notes/research-local-working-files.md
  - .harness/harness/features/FEAT-2641-local-working-files/notes/research-FEAT-2641-plan-proposal.md
  - .harness/harness/features/FEAT-2641-local-working-files/notes/review-harness-code-reviewer-plan-c1.md
  - .harness/harness/features/FEAT-2641-local-working-files/notes/review-harness-ui-reviewer-plan-c1.md
  - .harness/harness/features/FEAT-2641-local-working-files/notes/research-FEAT-2641-local-working-files-goalcheck-plan.md
  - .harness/harness/features/FEAT-2641-local-working-files/observations/harness-pm.md
  - .harness/harness/features/FEAT-2641-local-working-files/runs/plan-product/state.yaml
  - .harness/harness/features/FEAT-2641-local-working-files/runs/plan-product/panel-c1.md
  - .harness/harness/features/FEAT-2641-local-working-files/runs/plan-product/criteria.md
  branch: feat/FEAT-2641-local-working-files
  open_questions:
  - id: OQ-02
    question: 'Raised by pm and code-reviewer. Pulling FEAT-2641''s untracking commit
      deletes untracked working files from each checkout''s disk. That includes those
      of shipped-but-undistilled features: BUG-2451, FEAT-2557, BUG-2565, BUG-2566
      and FEAT-2581. How should these files be preserved? Recommendation: before FEAT-2641
      merges, finish or explicitly decline each of those distills. Where that is not
      possible, snapshot the feature''s notes/, runs/ and observations/ outside the
      repository. Never rewrite history.'
    blocking: true
  - id: LEAD-01
    question: 'Apply remediated six high substance findings and added D-10 (the landing
      route): PF-731dc8d4, PF-30e2e530, PF-5c090d3a, PF-104ac367, PF-3f271400 and
      PF-a6ec2bbc. The plan team has no re-read step, so no reader has seen the applied
      text of T-03, T-05, T-06, T-07 and T-09. That includes the literal commands
      in T-09''s landing step and T-05''s refusal message. Recommendation: commission
      one scope re-read of those five tasks before signing. The alternative is to
      sign while explicitly accepting that the text is unread.'
    blocking: true
  - id: OQ-01
    question: 'Raised by pm; goalcheck GC-02 asks that it go to the operator. D-07
      replaces gh-sync ship''s notes/handoff-validate.md refusal with a feature.json
      precondition that a validator validate or fix run recorded PASS. The grilling
      asked for plain deletion, but deletion would reopen BUG-1129. This departure
      appears in neither BRIEF.md nor plan.yaml. Recommendation: keep D-07. Strike
      it at signature if you want the plain deletion.'
    blocking: false
  - id: GC-01
    question: 'The grilling says the command that sets the terminal station cleans
      up. On reject --superseded-by none and on a declined distill, the plan instead
      has the caller run feature-worktree.py clean as a documented follow-up, so the
      evidence survives if the station write is refused. Alternative: set-feature-station
      calls cleanup when it writes rejected. Recommendation from pm''s applied plan:
      accept the documented follow-up.'
    blocking: false
  - id: OQ-03
    question: 'An in-flight branch that still tracks its working files will turn the
      guard test red when it merges main. Should these branches use the documented
      repair (git rm -r --cached --sparse, recorded in references/checkout-upgrade.md
      through T-07), or must each untrack before FEAT-2641 lands? Recommendation:
      accept the documented repair.'
    blocking: false
  - id: OQ-04
    question: 'This feature''s own grilling and facts notes in .harness/notes/ can
      be recorded in project_notes only after T-04 adds feature-record.py project-note.
      Recommendation: the build records both paths immediately after T-04 lands, so
      distill cleanup removes them.'
    blocking: false
  - id: OQ-05
    question: Possible harness defect for the harness owner, reported by pm. bash-write-guard
      refused a throwaway git experiment in a mktemp directory under /tmp, treating
      it as a governed kaya product write ('mismatched runtime repository binding
      for kaya'). A scratch repo outside every checkout should not be guarded.
    blocking: false
  escalations: []
  expertise_update: []
  adequacy_notes:
  - Both reader FAILs (scope, design) graded the draft. Their findings were applied,
    and 11 of 12 are recorded resolved_by a task. The only open finding is an info-severity
    agreement from should-not-exist, which does not gate. Worst-wins collation over
    FAIL members combined with a blocking operator question gives ESCALATE; the plan
    itself is pending and can be signed once the operator rules.
  - The panel recorded in plan.yaml lists scope, should-not-exist and design. This
    digest's readers also include goalcheck; the orchestrator should re-record the
    panel from runs/plan-product/digest.md so INV-32 sees goalcheck.
  - 'No scope: mission proportionality finding was raised, so there is no downgrade
    recommendation; fable-advisor judged the plan lane proportionate.'
  - 'The prototype gate does not apply: there is no visual-designer step, and design
    self-scoped to CLI reject/abandon states, with no end-user UI and no prototype
    required. The user can override this either way.'
  - Every task is main-session-direct under DEC-174. D-10 names the landing route
    as one PR, with CI and the operator's ordinary hooked merge as the live gates.
  sc_status:
  - id: operator
    verdict: partial
    method: inspection
    evidence: goalcheck note; grilling's terminal-verb cleanup line vs T-05/T-07 caller-runs-clean;
      D-07 not on record (GC-01, GC-02/OQ-01)
  - id: code maintainer
    verdict: met
    method: inspection
    evidence: SC-04 T-02, SC-14 T-05/T-07/T-09, SC-15 T-08, D-05 single routine
  - id: orchestrator
    verdict: met
    method: inspection
    evidence: SC-05 T-05, SC-10 T-06, SC-11 T-04, SC-12/13 T-04/T-09, SC-16 T-07
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps: []
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: T-05/T-07 deletes evidence before terminal state on reject with no successor.
    why: Station write left to caller for successor none; cleanup first loses evidence
      if that write refuses. Resolved by T-05.
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: T-03/T-06/T-07 cannot reliably clean after ship or distill.
    why: Station read from the retained worktree plan; declined-distill, retry and
      zero-change distill paths unreachable. Resolved by T-03.
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: T-03's project-note cleanup can delete unclaimed files.
    why: A project_notes path naming a directory or behind a symlinked parent removes
      unclaimed files. Resolved by T-03.
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: T-06/T-07 does not stage D-04's durable distill ledger.
    why: Dirty feature.json makes merge-gate refuse before receipt replay. Resolved
      by T-07.
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: T-01 changes T-03/T-06 fixture semantics before their gates are migrated;
      first landing and registry timing are unstated.
    why: Intermediate trees hit old gates; isolated verification is not live enforcement.
      Resolved by T-09 (D-10).
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: T-08 misses live clauses in affected decisions.
    why: DEC-46, DEC-150 and DEC-191 still prescribe committed run history; some amendments
      leave obsolete clauses live. Resolved by T-08.
  - kind: form
    scope: none
    severity: low
    reader: code-reviewer
    summary: T-07's negative grep matches its own required documentation.
    why: Verify rejects text the intent requires. Resolved by T-07.
  - kind: substance
    scope: none
    severity: high
    reader: ui-reviewer
    summary: T-05 deletes local working files before writing the terminal station
      on reject --superseded-by none.
    why: SC-06 requires the station to be recorded before deletion; files are gone
      if the caller's write refuses. Resolved by T-05.
  - kind: substance
    scope: none
    severity: med
    reader: ui-reviewer
    summary: T-05 does not specify what abandon or reject reports when the terminal
      operation succeeds but local cleanup fails.
    why: Operator may retry the remote operation instead of only the cleanup. Resolved
      by T-05.
  - kind: proportionality
    scope: task
    severity: low
    reader: should-not-exist
    summary: GATE 2b's per-file "WOULD DISCARD WORKING FILE" listing turns every post-merge
      sweep into a wall of output for shipped-but-undistilled features
    why: Buries the actionable clean command; dirs plus file count suffice. Trimmed
      in T-03.
  - kind: form
    scope: none
    severity: info
    reader: should-not-exist
    summary: T-06's induced-cleanup-failure integration fixture ("a directory the
      process cannot remove") is environment-dependent and should be a unit-level
      fake instead
    why: Unremovable directories do not exist for root. Resolved by T-06.
  - kind: substance
    scope: none
    severity: info
    reader: should-not-exist
    summary: Everything of substance traces to an operator ruling or a grilling "Not
      yet specified" item; no task builds a thing the user does not need, and no task
      is obsoleted by another
    why: Stated agreement so the panel does not re-litigate it; still open, non-gating.
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
