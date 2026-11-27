# Plan team digest — FEAT-2516-stamp-sweep-hardening, run 2026-11-26-01-plan-product (cycle 1)

**BLUF: The plan is ready for the operator's signature and stays `pending`. It has 5 tasks, all
main-session-direct; the BRIEF has 3 perspectives and 12 SCs. `plan-merge.py check` exits 0 (16
anchors, 0 failures, no OVERLAP) and `record-panel --cycle 1` exits 0 with 10 findings recorded open.
VERDICT ESCALATE (worst-wins over the scope reader's FAIL on the draft). Every must_fix has an
applied remedy, but no reader re-read the applied text. That, plus D-03's reversal of settled
operator text, needs the operator's ruling at signature. Do not re-panel (DEC-176).**

## Steps
| step | persona | verdict | artifact |
|---|---|---|---|
| draft | harness-pm | PASS | notes/research-stamp-sweep-hardening-plan.md |
| scope | harness-code-reviewer | FAIL (on draft) | notes/review-harness-code-reviewer-plan-c1.md |
| should-not-exist | fable-advisor | PASS, ran | fan-in only (no write grant) |
| design | harness-ui-reviewer | PASS, self-scoped out | notes/review-harness-ui-reviewer-plan-c1.md |
| apply | harness-pm | PASS | plan.yaml / BRIEF.md; dispositions in the research note § C1 |
| goalcheck | harness-pm | PASS | notes/research-FEAT-2516-stamp-sweep-hardening-goalcheck-plan.md |

Reader fan-in: `panel-c1.md` (this dir). Send-back criteria were written before any return:
`criteria.md`. No send-backs were needed, so cycles = 0.

## Findings and dispositions (severity and kind are each reader's own)
| # | reader | kind | sev | summary | disposition |
|---|---|---|---|---|---|
| 1 | scope | substance | high | T-03 fix round attributable without meeting the receipt contract | applied: shared `verify_fix_receipt` with sole_effect, closed key set, 40-hex fix_commit, FAIL-only; writer + INV-7; close-run test. UNREAD |
| 2 | scope | substance | high | T-03 resolves fleet fix commits in the planning repo | applied: `feature_schema.code_repository` (moved from validate-digest `_qa_code_repository`); test where the commit is product-only. UNREAD; widens T-03 into validate-digest.py |
| 3 | scope | substance | med | strict timestamp cutoff can omit a same-second round | applied: rounds counted by INV-40 FAIL/regate ordinal association; legacy fallback kept; SC-11/12 rewritten |
| 4 | scope | substance | med | T-01 duplicate-hit reason names no segment | applied: reason names every hit segment; row (l) asserts both |
| 5 | scope | substance | med | T-02 escape assertions pass if the diagnostic is suppressed | applied: exactly one escaped line per mode; SC-06 rewritten |
| 6 | scope | form | med | omitted DEC-159/221/227/230 | applied: keep rows added |
| 7 | scope | form | low | ledger prose inconsistent; stamp containment overstated | applied |
| 8 | should-not-exist | substance | info | D-03's decline of the runner step is correct; keep it unbuilt | kept: operator signature question (Q-A) |
| 9 | should-not-exist | substance | low | T-04 verify keeps the obsolete self-test flag alive | declined: the operator's destination is "self-test is green"; running the flag is its direct evidence |
| 10 | should-not-exist | form | low | T-03.E test name inverted without a rename | moot: with the association design the test body is unchanged and its name stays true |

record-panel records all ten as `open` by construction. Resolution is set-panel's or the operator's
(`--overrule` at signature), never this tier's.

## Lead assessment
- **Scope reader vs fable on T-03 timing: not a contradiction.** Fable verified the diagnosis
  (should be 1, prints 2). Scope found that the "strictly after" remedy misses a same-second case.
  pm resolved this at the mechanism, which satisfies both readers.
- **Unread remediation (O-10).** Findings 1 and 2 are high. The applied T-03 text now prescribes new
  shared functions and moves a resolver into a second gate file (validate-digest.py, DEC-174). No
  reader has graded that text. The operator signs either knowing it is unread, or after choosing a
  targeted re-read.
- **Goal-check.** operator: PASS. code maintainer: PARTIAL, solely because D-03 is unratified.
  orchestrator: PASS. pm listed six departures from `## Settled`; only D-03 is a reversal, the rest
  are disclosed narrowings. One of those narrowings is real: B-3 row (p) keeps a harness hit
  `terminal` while a fleet tree is unreadable. That is pre-existing short-circuit behaviour, but it
  is narrower than "never decides from the remaining hits".
- **#2519** was already closed by PR #2530. source_issues lists the 8 open issues, so "all nine
  close with this feature" holds only as an end state.
- **No `scope: mission` finding** was raised. Fable explicitly judged the mission scale
  proportionate, so there is no downgrade recommendation.
- **Prototype gate.** The ui-reviewer self-scoped out: there is no user-facing surface, only CLI and
  hook text. Visual-designer is not a plan-team step. My call: no prototype is required. This is
  overridable.

## Harness defects met
- pm's apply return put multi-paragraph prose into `artifact` after the path. validate-digest
  accepted it. A string field meant to hold a path is not checked as a path.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: 'FEAT-2516 plan is signable and still pending: 5 main-session-direct tasks,
    12 SCs, check and record-panel both exit 0. Every scope must_fix has a remedy
    applied, but no reader has re-read the two high T-03 remedies. D-03 reverses settled
    operator text. Both need the operator''s ruling at signature. No re-panel and
    no downgrade.'
  open_questions:
  - id: Q-A
    question: Signature ruling, blocking. D-03 replaces the grilling's settled B-1/B-4
      text 'have the integration runner invoke --canonical-reader-self-test'. In its
      place T-04 adds a CASES-membership guard, since the default run has been a superset
      since FEAT-2489. The flag stays a local entry point that T-04's verify runs.
      Scope and should-not-exist both recommend accepting. Ratify or overrule?
    blocking: true
  - id: Q-B
    question: 'Signature ruling, blocking. Two high scope findings were remediated
      at apply and nobody has re-read the result. The first is ''T-03 can attribute
      a fix round without meeting the receipt contract.'': the fix is a shared verify_fix_receipt
      with sole_effect, a closed key set, a 40-hex fix_commit and a FAIL-only rule.
      The second is ''T-03 resolves fleet fix commits in the central planning repository.'':
      the fix moves validate-digest.py#_qa_code_repository to feature_schema.code_repository.
      Recommendation: sign, and have the validate-phase code-reviewer verify the T-03
      text against these two findings. The other option is a targeted scope re-read
      of T-03 before signature.'
    blocking: true
  - id: Q-C
    question: T-03 now also edits validate-digest.py, a second gate file under DEC-174
      and still main-session-direct, because the code-repository resolver moved there
      instead of being duplicated. Accept the wider task?
    blocking: false
  - id: Q-D
    question: 'Narrowings of settled text to disclose at signature: B-2 tests still
      assert reason substrings for non-absence purposes (rows k, l, n, o). B-3 row
      (p) keeps a harness hit terminal while a fleet tree is unreadable; this is the
      pre-existing short-circuit, but narrower than ''never decides from the remaining
      hits''. B-5 symlinked stamps are skipped silently, not refused. B-6 uses repr
      only for non-printable names. B-9 accepts exactly +1, on FAIL runs only.'
    blocking: false
  - id: Q-E
    question: '#2519 (B-4) was already closed by PR #2530 and is left out of source_issues.
      ''All nine close with this feature'' holds only as an end state. Ship should
      name #2519 as delivered by #2530.'
    blocking: false
  - id: Q-F
    question: Harness defects. (1) validate-digest accepted a pm apply return whose
      `artifact` string held a path followed by several paragraphs of prose; a field
      meant to hold a path is not checked as a path. (2) The team-file fan-in contract
      asks for a scope on fable-advisor's findings and a reason on every reader. The
      lead digest schema refuses scope on non-proportionality findings and a reason
      on ran readers, but panel-c1.md carried both and record-panel accepted it. The
      two contracts disagree.
    blocking: false
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2516-stamp-sweep-hardening/.harness/harness/features/FEAT-2516-stamp-sweep-hardening/BRIEF.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2516-stamp-sweep-hardening/.harness/harness/features/FEAT-2516-stamp-sweep-hardening/plan.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2516-stamp-sweep-hardening/.harness/harness/features/FEAT-2516-stamp-sweep-hardening/notes/research-stamp-sweep-hardening-plan.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2516-stamp-sweep-hardening/.harness/harness/features/FEAT-2516-stamp-sweep-hardening/notes/review-harness-code-reviewer-plan-c1.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2516-stamp-sweep-hardening/.harness/harness/features/FEAT-2516-stamp-sweep-hardening/notes/review-harness-ui-reviewer-plan-c1.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2516-stamp-sweep-hardening/.harness/harness/features/FEAT-2516-stamp-sweep-hardening/notes/research-FEAT-2516-stamp-sweep-hardening-goalcheck-plan.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2516-stamp-sweep-hardening/.harness/harness/features/FEAT-2516-stamp-sweep-hardening/observations/harness-pm.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2516-stamp-sweep-hardening/.harness/harness/features/FEAT-2516-stamp-sweep-hardening/runs/2026-11-26-01-plan-product/panel-c1.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2516-stamp-sweep-hardening/.harness/harness/features/FEAT-2516-stamp-sweep-hardening/runs/2026-11-26-01-plan-product/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2516-stamp-sweep-hardening/.harness/harness/features/FEAT-2516-stamp-sweep-hardening/runs/2026-11-26-01-plan-product/criteria.md
  expertise_update: []
  team: plan
  steps_run: 6
  cycles_used: 0
  members:
  - step: draft
    persona: harness-pm
    verdict: PASS
    headline: BRIEF (3 perspectives, 12 SCs) and a 5-task main-session-direct plan.yaml
      drafted; check exit 0
    files_touched:
    - .harness/harness/features/FEAT-2516-stamp-sweep-hardening/BRIEF.md
    - .harness/harness/features/FEAT-2516-stamp-sweep-hardening/plan.yaml
    - .harness/harness/features/FEAT-2516-stamp-sweep-hardening/notes/research-stamp-sweep-hardening-plan.md
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: The plan lane fits, but on the draft T-03 did not enforce the fix-receipt
      contract or resolve fix commits in the right repository. 5 must_fix.
    files_touched:
    - .harness/harness/features/FEAT-2516-stamp-sweep-hardening/notes/review-harness-code-reviewer-plan-c1.md
  - step: should-not-exist
    persona: fable-advisor
    verdict: PASS
    headline: No task builds anything the operator does not need; D-03's decline was
      verified correct; 3 minor findings, max low
    files_touched: []
  - step: design
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode A out of scope: no user-facing surface'
    files_touched:
    - .harness/harness/features/FEAT-2516-stamp-sweep-hardening/notes/review-harness-ui-reviewer-plan-c1.md
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: All 5 must_fix and both form findings applied; fable findings kept,
      declined or moot; record-panel and check exit 0 (16 anchors, 0 failures, no
      OVERLAP)
    files_touched:
    - .harness/harness/features/FEAT-2516-stamp-sweep-hardening/BRIEF.md
    - .harness/harness/features/FEAT-2516-stamp-sweep-hardening/plan.yaml
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: operator PASS, orchestrator PASS, code maintainer PARTIAL until the
      operator ratifies D-03
    files_touched:
    - .harness/harness/features/FEAT-2516-stamp-sweep-hardening/notes/research-FEAT-2516-stamp-sweep-hardening-goalcheck-plan.md
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - 'Plan approval.status is pending. This run wrote no approval: block. panel: is
    recorded for cycle 1 from panel-c1.md. The orchestrator should re-run record-panel
    from this digest.md so goalcheck is among the readers (INV-32).'
  - 'The scope reader''s FAIL was on the draft. All 5 must_fix were applied at apply,
    so the gating list is now empty. The verdict is still ESCALATE rather than PASS
    for two reasons: worst-wins, and the two high remediations are unread (Q-B).'
  - "All 10 panel findings are recorded open by construction. Dispositions are in\
    \ each finding's why, in digest.md, and in the pm research note \xA7 C1. Resolution\
    \ belongs to the operator at signature (--overrule) or to set-panel."
  - 'Reader context, carried here because the schema closes reason to none for ran
    readers. scope: FAIL on the draft with 5 must_fix. should-not-exist: resolved
    and ran, max low. design: self-scoped out, no user-facing surface. goalcheck:
    operator pass, code maintainer partial, orchestrator pass.'
  - 'Prototype gate: no user-facing surface (ui-reviewer self-scoped out), so the
    lead''s call is that no prototype is required. This is overridable.'
  - 'No scope: mission proportionality finding was raised; fable judged the mission
    proportionate, so no downgrade is recommended.'
  sc_status:
  - id: perspective:operator
    verdict: pass
    method: goalcheck inspection
    evidence: SC-04/05/06 via T-02, T-05 terminal
  - id: perspective:code maintainer
    verdict: partial
    method: goalcheck inspection
    evidence: SC-01..03 via T-01/T-02, SC-07/08 via T-04, SC-09 via T-01..T-05; partial
      only because D-03 is unratified
  - id: perspective:orchestrator
    verdict: pass
    method: goalcheck inspection
    evidence: SC-10/11/12 via T-03, DEC-157 amendment via T-05
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps: []
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: scope
    summary: T-03 can attribute a fix round without meeting the receipt contract.
    why: 'Disposition: applied (shared verify_fix_receipt, sole_effect, closed keys,
      40-hex fix_commit, FAIL-only, close-run test); the applied text is unread.'
  - kind: substance
    scope: none
    severity: high
    reader: scope
    summary: T-03 resolves fleet fix commits in the central planning repository.
    why: 'Disposition: applied (feature_schema.code_repository moved from validate-digest;
      product-only commit test); the applied text is unread and widens T-03.'
  - kind: substance
    scope: none
    severity: med
    reader: scope
    summary: T-03's strict timestamp cutoff can omit a real rework round.
    why: 'Disposition: applied (INV-40 ordinal FAIL/regate association, legacy fallback,
      SC-11/12 rewritten).'
  - kind: substance
    scope: none
    severity: med
    reader: scope
    summary: T-01's duplicate-hit diagnostic does not name either segment.
    why: 'Disposition: applied (the reason names every hit segment; row (l) asserts
      both).'
  - kind: substance
    scope: none
    severity: med
    reader: scope
    summary: T-02's escape assertions pass if the control-name diagnostic is suppressed.
    why: 'Disposition: applied (exactly one escaped line per mode; SC-06 rewritten).'
  - kind: form
    scope: none
    severity: med
    reader: scope
    summary: The draft omits decisions governing close-run, spend, regates and served
      repository separation.
    why: 'Disposition: applied (keep rows for DEC-159, DEC-221, DEC-227, DEC-230).'
  - kind: form
    scope: none
    severity: low
    reader: scope
    summary: The plan leaves ledger prose internally inconsistent and overstates stamp
      containment.
    why: 'Disposition: applied (ledger synopsis, recommended-filename wording, operator
      perspective scoped to stamps).'
  - kind: substance
    scope: none
    severity: info
    reader: should-not-exist
    summary: "Grilling's settled B-1/B-4 item \u2014 'have the integration runner\
      \ invoke --canonical-reader-self-test' \u2014 must stay unbuilt; D-03's decline\
      \ is verified correct and the gate should not push the plan back toward the\
      \ grilling text."
    why: 'Disposition: kept; the operator ratifies at signature (Q-A). The reader''s
      digest tagged it scope task.'
  - kind: substance
    scope: none
    severity: low
    reader: should-not-exist
    summary: "T-04's verify runs `test-check-plan-routes.py --canonical-reader-self-test`,\
      \ keeping alive and exercising a flag whose only remaining caller is that verify\
      \ line \u2014 the very entry point D-03 declares obsolete."
    why: 'Disposition: declined by pm. The operator''s destination is ''self-test
      is green'', and running the flag is its direct evidence.'
  - kind: form
    scope: none
    severity: low
    reader: should-not-exist
    summary: T-03.E rewrites `test_the_window_opens_exactly_at_the_first_validate_start`
      to assert the opposite of its name (a regate AT the window's opening no longer
      counts) without directing a rename.
    why: 'Disposition: moot. Under the association design the test stays unmodified
      and its name stays true.'
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2516-stamp-sweep-hardening/.harness/harness/features/FEAT-2516-stamp-sweep-hardening/runs/2026-11-26-01-plan-product/digest.md
```
