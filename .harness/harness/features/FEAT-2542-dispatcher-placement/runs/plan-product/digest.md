# FEAT-2542 plan-product — team digest (cycle 1)

**BLUF.** BRIEF.md and plan.yaml are drafted, panelled, applied and `pending` for signature. The plan carries the grilling's rulings Q1–Q5 faithfully: two tasks (T-01 dispatch-guard + tests, T-02 DEC-258), both `main-session-direct`; SC-01..SC-05 by class with LEAVE lists; no DEC-100/DEC-253 amendment (8 `keep` rows). SC-characterization was discharged before signature: 98 measured rows at base 2e7a2c77 (59 change, 39 same) in `notes/research-FEAT-2542-dispatcher-placement-characterization.md`. Team VERDICT is FAIL by worst-wins (scope, design and goalcheck returned FAIL) — the findings were applied in-run, but no reader re-read the remediations, so the operator rules on that at signature.

## Members
- draft (pm) PASS — BRIEF, plan, probe note; `plan-merge.py check`: "2 task(s), 5 anchor(s) resolved, 0 failure(s)"; no APPROVAL-RESET, no gh-sync.
- scope (code-reviewer) FAIL — 2 high + 2 med substance, 1 low form. Note `notes/review-harness-code-reviewer-plan-c1.md`.
- should-not-exist (fable-advisor) PASS — ran; 1 proportionality/task low, 1 substance low. Findings only in `panel-c1.md`.
- design (ui-reviewer) FAIL — in scope on operator-facing denial text (no visual UI); 3 med substance on remedy wording. Note `notes/review-harness-ui-reviewer-plan-c1.md`.
- apply (pm) PASS, sent back once — 9/10 resolved (T-01/T-02), PF-0017 open; record-panel and check exit 0 per pm. Send-back (goalcheck GC-1) added `c38/distill/foreign-tree-root`; check exit 0.
- goalcheck (pm) FAIL — all 4 perspectives met; grilling test-matrix check partial (missing product→code-reviewer foreign-tree-root shape). Discharged by the send-back after grading; lead-verified by grep (plan.yaml T-01 row `c38/distill/foreign-tree-root`). The goal-check note itself is unchanged and records the partial as graded.

## Findings and dispositions (panel-c1.md; plan.yaml `panel:`)
| PF | Reader | Sev/kind | Disposition |
|---|---|---|---|
| PF-309f… baseline failure set unproducible | code-reviewer | high/substance | resolved T-01 (one row inventory, predicted_red = observed_red) |
| PF-5bd4… tested checkout not final pin | code-reviewer | high/substance | resolved T-01/T-02 (tested_sha recorded, DEC-number step 0 stop-and-report) |
| PF-8833… exemption vs preflight disagree | code-reviewer | med/substance | resolved T-01 (single dispatch-local placement answer; no reorder) |
| PF-ffad… ambiguity remedy registry | code-reviewer | med/substance | resolved T-01 (same defect as PF-83a8) |
| PF-6cb0… complete decision rows | code-reviewer | low/form | resolved T-02 (DEC-204, DEC-214 keep rows) |
| PF-83a8… ambiguous-claim remedy | ui-reviewer | med/substance | resolved T-01 |
| PF-c356… OSError remedy assumes path | ui-reviewer | med/substance | resolved T-01 |
| PF-88cf… persona-mismatch remedy | ui-reviewer | med/substance | resolved T-01 |
| PF-658a… redundant matrix rows | should-not-exist | low/proportionality task | resolved T-01 (trimmed instances, classes kept) |
| PF-0017… id-less-lead pass-through pinned | should-not-exist | low/substance | **open** — tied to signer OQ-1 |

No `scope: mission` finding; no downgrade recommended. No reader dissent on mission proportionality.

## Prototype gate
visual-designer is not a plan-team step and was not dispatched. Lead call (overridable either way): no high-fidelity prototype required — the only user-facing surface is CLI denial text, which ui-reviewer judged in Mode A and whose remedies T-01 now specifies.

## Adequacy
- `c38/distill/foreign-tree-root` base outcome is code-read, not measured (pm OQ-A1); T-01 Step 2's predicted=observed equality settles it at build.
- Cycles: 1 send-back (apply). Run dir: `runs/plan-product/`; send-back criteria pre-written at `sendback-criteria.md`.

```yaml
VERDICT: FAIL
DIGEST:
  headline: FEAT-2542 plan is signable and pending. The grilling's Q1-Q5 are carried,
    SC-characterization is discharged by 98 measured base rows, and 9 of 10 panel
    findings were applied. The run is FAIL by worst-wins because no reader re-read
    the 2 high and 5 med fixes, so the signer must rule on that.
  team: plan
  steps_run: 7
  cycles_used: 1
  members:
  - step: draft
    persona: harness-pm
    verdict: PASS
    headline: 'BRIEF and plan.yaml drafted with T-01 and T-02 (main-session-direct),
      SC-01..SC-05 by class, DEC-258; probe has 98 rows: 59 change, 39 stay the same'
    files_touched:
    - .harness/harness/features/FEAT-2542-dispatcher-placement/BRIEF.md
    - .harness/harness/features/FEAT-2542-dispatcher-placement/plan.yaml
    - .harness/harness/features/FEAT-2542-dispatcher-placement/notes/research-FEAT-2542-dispatcher-placement-characterization.md
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Keep the bundled plan. Fix the fail-first matrix, final-pin proof, split
      route decision and ambiguity remedy (2 high, 2 med substance, 1 low form)
    files_touched:
    - .harness/harness/features/FEAT-2542-dispatcher-placement/notes/review-harness-code-reviewer-plan-c1.md
  - step: should-not-exist
    persona: fable-advisor
    verdict: PASS
    headline: Plan matches operator intent; trim redundant matrix rows; the id-less-lead
      pass-through should not be pinned
    files_touched: []
  - step: design
    persona: harness-ui-reviewer
    verdict: FAIL
    headline: The operator-facing lineage refusals lack an actionable remedy in three
      cases; no visual UI is affected
    files_touched:
    - .harness/harness/features/FEAT-2542-dispatcher-placement/notes/review-harness-ui-reviewer-plan-c1.md
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: 9 of 10 findings resolved in T-01/T-02 and PF-0017 left open; record-panel
      and check exit 0. One send-back added c38/distill/foreign-tree-root
    files_touched:
    - .harness/harness/features/FEAT-2542-dispatcher-placement/plan.yaml
    - .harness/harness/features/FEAT-2542-dispatcher-placement/BRIEF.md
    - .harness/harness/features/FEAT-2542-dispatcher-placement/notes/research-FEAT-2542-dispatcher-placement-characterization.md
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: 'All 4 perspectives are met. The test-matrix check was partial: the
      product->code-reviewer row lacked the foreign-tree-root shape. The apply send-back
      fixed it after grading'
    files_touched:
    - .harness/harness/features/FEAT-2542-dispatcher-placement/notes/research-FEAT-2542-dispatcher-placement-goalcheck-plan.md
  must_fix: []
  files_touched:
  - .harness/harness/features/FEAT-2542-dispatcher-placement/BRIEF.md
  - .harness/harness/features/FEAT-2542-dispatcher-placement/plan.yaml
  - .harness/harness/features/FEAT-2542-dispatcher-placement/notes/research-FEAT-2542-dispatcher-placement-characterization.md
  - .harness/harness/features/FEAT-2542-dispatcher-placement/notes/research-FEAT-2542-dispatcher-placement-goalcheck-plan.md
  - .harness/harness/features/FEAT-2542-dispatcher-placement/notes/review-harness-code-reviewer-plan-c1.md
  - .harness/harness/features/FEAT-2542-dispatcher-placement/notes/review-harness-ui-reviewer-plan-c1.md
  - .harness/harness/features/FEAT-2542-dispatcher-placement/observations/harness-pm.md
  - .harness/harness/features/FEAT-2542-dispatcher-placement/runs/plan-product/state.yaml
  - .harness/harness/features/FEAT-2542-dispatcher-placement/runs/plan-product/panel-c1.md
  - .harness/harness/features/FEAT-2542-dispatcher-placement/runs/plan-product/sendback-criteria.md
  branch: none
  open_questions:
  - id: SQ-1
    question: 'PF-309f and PF-5bd4 (high substance, code-reviewer) and five med substance
      findings were resolved at apply without any reader re-reading the fixes; the
      team has no re-read step. Recommendation: accept them as applied at signature
      (the remedies are in T-01/T-02 and T-01 Step 2 enforces predicted_red = observed_red
      at build). The alternative is a cycle-2 scope/design re-read in a new run dir.
      Which?'
    blocking: true
  - id: SQ-2
    question: 'OQ-1 / PF-0017 (open, low): should the guard also refuse a governed-lead
      payload that has no harness_agent_id? The grilling keeps that path unchanged.
      pm recommends keeping it and keeps case 41''s lead-no-id rows as asserted SC-02
      LEAVE rows. fable-advisor dissents: it says either refuse now or leave the row
      unasserted. Your ruling decides PF-0017 (overrule or amend).'
    blocking: false
  - id: SQ-3
    question: No on-disk fixture at base 2e7a2c77 can reach the escaped UnreadableRegistry/OSError
      state. SC-02 grades it through a fault-injected copied bin tree. Is that acceptable
      evidence? pm recommends yes.
    blocking: false
  - id: SQ-4
    question: The rework budget of 2 rounds / 90 min is recorded only as a proposal
      (BRIEF Constraints). Please rule on it with --rework at signature.
    blocking: false
  - id: SQ-5
    question: 'Collision rule: if DEC-258 is already taken on origin/main or HEAD
      when T-01 Step 0 or T-02 runs, the task stops and reports, and renumbering becomes
      an operator-ruled plan amendment. Do you confirm that rule?'
    blocking: false
  - id: SQ-6
    question: The c38/distill/foreign-tree-root base outcome (exit 2, cause red) comes
      from reading the code. The probe did not measure it. Will you accept T-01 Step
      2's build-time predicted=observed equality as its characterization?
    blocking: false
  - id: SQ-7
    question: 'T-01''s files anchor #case_33_every_child_of_a_bound_distill_run_carries_the_mission
      names a function the task does not edit, because the new rows went into case
      38. Should it be retargeted to case 38 / the test file, or left as is?'
    blocking: false
  - id: SQ-8
    question: The Harness checkout ships no docs/spec.md, docs/decisions.md or docs/architecture.md,
      so the tasks cite .harness/harness/docs/DECISIONS.md. Should Harness carry those
      product documents? This is out of scope for this feature.
    blocking: false
  escalations: []
  expertise_update: []
  adequacy_notes:
  - 'plan-merge.py check (draft): ''2 task(s), 5 anchor(s) resolved, 0 failure(s)''.
    pm reported exit 0 after apply and after the send-back, but not the verbatim line.'
  - 'No APPROVAL-RESET receipt appeared, so no gh-sync call was made. plan.yaml approval.status
    is pending, and BRIEF ## Approval reads status: pending.'
  - 'All readers ran, none skipped: scope FAIL (high), should-not-exist PASS (low;
    findings only in runs/plan-product/panel-c1.md), design FAIL (med, Mode A in scope
    on denial text), goalcheck FAIL (test-matrix partial, discharged by the apply
    send-back).'
  - The goal-check note records the test-matrix check as partial, as graded before
    the send-back. The send-back discharged it, and the lead verified that T-01 carries
    c38/distill/foreign-tree-root. The goal-check was not re-run, so the note is left
    honest.
  - 'Prototype gate, lead call (overridable either way): no high-fidelity prototype
    is required. The only user-facing surface is CLI denial text, which ui-reviewer
    judged in Mode A. visual-designer is not a plan-team step.'
  - 'No scope: mission proportionality finding was raised, so no downgrade is recommended.'
  sc_status:
  - id: SC-03
    verdict: partial
    method: inspection
    evidence: 'The pre-signature clause is met: notes/research-FEAT-2542-dispatcher-placement-characterization.md
      has 98 measured rows at base 2e7a2c77, one per placement state and route class.
      The build-time base-vs-pin repeat is pending T-01.'
  - id: SC-01
    verdict: not_met
    method: automated
    evidence: pending T-01 build
  - id: SC-02
    verdict: not_met
    method: automated
    evidence: pending T-01 build
  - id: SC-04
    verdict: not_met
    method: inspection
    evidence: pending T-02 (DEC-258)
  - id: SC-05
    verdict: not_met
    method: inspection
    evidence: source_issues [2542, 2532] recorded; issues close at ship
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps: []
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: T-01 demands a baseline failure set the planned cases cannot produce.
    why: resolved T-01 (PF-309f48cdcedbf909ab82e5498efcb731); no reader re-read, see
      SQ-1
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: The T-01 checkout being tested is not the final review pin.
    why: resolved T-01 (PF-5bd4c7e2d9c22bd3f8bedaf1f044a322); no reader re-read, see
      SQ-1
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: The scope-reader exemption and its enforcing preflight can disagree on
      registered distill state.
    why: resolved T-01 with a single dispatch-local placement answer, no preflight
      reorder (PF-8833220de88a57f753f4013b0eff3664)
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: The proposed ambiguity remedy does not select the surplus claim's registry.
    why: resolved T-01 (PF-ffad756dce4ea37a6c2e5c1fa63b40b9); same defect as ui-reviewer
      PF-83a8
  - kind: form
    scope: none
    severity: low
    reader: code-reviewer
    summary: Complete the affected-decision rows without amending DEC-100 or DEC-253.
    why: 'resolved T-02: DEC-204 and DEC-214 keep rows added (PF-6cb02861164d00358b884fde7388983d)'
  - kind: substance
    scope: none
    severity: med
    reader: ui-reviewer
    summary: "The ambiguous-claim remedy does not identify how to target the surplus\
      \ claim\u2019s registry."
    why: resolved T-01 (PF-83a8ba7961f1073e49b1fbb9f9ea97ca)
  - kind: substance
    scope: none
    severity: med
    reader: ui-reviewer
    summary: The registry-error remedy assumes an escaped OSError names a file.
    why: resolved T-01 (PF-c356bbe7ce38cc31328914a874668f07)
  - kind: substance
    scope: none
    severity: med
    reader: ui-reviewer
    summary: The persona-mismatch remedy stops at inspection.
    why: resolved T-01 (PF-88cfa7473ff8f72ec654c4f353dc9400)
  - kind: proportionality
    scope: task
    severity: low
    reader: should-not-exist
    summary: Case 38/39/41 matrices re-assert one causally identical branch across
      ~90 redundant rows
    why: 'resolved T-01: redundant instances trimmed and every class member kept (PF-658a0cb4a7eb0306c85fedc3290e4e6a)'
  - kind: substance
    scope: none
    severity: low
    reader: should-not-exist
    summary: Case 41's id-less-lead rows pin a lenient pass-through the plan itself
      calls host-unreachable
    why: 'open (PF-0017166a75cb353dd551d85bd7d61a78): refusing now would contradict
      the grilling''s scope; signer rules via SQ-2'
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/features/FEAT-2542-dispatcher-placement/runs/plan-product/digest.md
```
