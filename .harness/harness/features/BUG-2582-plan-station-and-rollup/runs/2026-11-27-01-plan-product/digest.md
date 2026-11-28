# BUG-2582 plan run 2026-11-27-01-plan-product — team digest

**BLUF: the plan is ready for signature (pending): 5 main-session-direct tasks, 11 SCs, 4 decisions, `plan-merge.py check` exit 0, all six reader findings applied and recorded `resolved`. The team VERDICT is FAIL only because DEC-123's worst-member roll-up forces it over the two readers' findings-carrying FAILs. That is defect 2 of this same feature, and the plan fixes it.**

## Members
| step | persona | verdict | artifact |
|---|---|---|---|
| draft | harness-pm | PASS | BRIEF.md, plan.yaml, notes/research-plan-station-and-rollup.md |
| scope | harness-code-reviewer | FAIL (5 findings) | notes/review-harness-code-reviewer-plan-c1.md |
| should-not-exist | fable-advisor | FAIL (1 finding, inline) | runs/2026-11-27-01-plan-product/panel-c1.md |
| design | harness-ui-reviewer | PASS (self-scoped out) | notes/review-harness-ui-reviewer-plan-c1.md |
| apply | harness-pm | PASS | notes/research-plan-c1-apply.md |
| goalcheck | harness-pm | PASS (3/3 perspectives pass) | notes/research-BUG-2582-plan-station-and-rollup-goalcheck-plan.md |

## Assessment
- **Both readers independently confirmed OQ-1.** `record-panel` writes every finding `open` (`plan_merge/panel.py` `_digest_finding`), and the shipped apply prompt never calls `set-panel`. Without a change to the team file, the defect-2 carve-out would have no trigger. The lead ruled to plan it in as T-05 (DEC-228 amend). This widens the operator's listed surfaces; it crosses none of the out-of-scope items. The operator may strike T-05 at signature.
- **pm overturned scope finding 1 with primary evidence, and the lead accepts it.** INV-34's remedy says the stub is "written through plan-merge.py apply" (`check_state/plan.py` `inv_34`), and `_seed_new_plan` seeds `approval: pending` on that creation. So `dispatch-guard.py` `_plan_preflight` admits the prescribed stub, and the lead had verified only the hand-written shape. D-04 makes no guard change, and T-04 witnesses the start→convert path end to end. The lead's verification and pm's measurement differed because they tested different stub routes; pm's is the route the remedy prescribes.
- **Decisions:** DEC-123, DEC-254 and DEC-228 are amended rather than replaced by new decisions. DEC-174, DEC-229 and DEC-191 are kept. FEAT-41's loader pair stays byte-identical, and T-01's verify asserts this.
- **Not re-read:** apply resolved four high findings and no reader re-read the result. Per O-10 this goes to the operator as one blocking signature question.
- Send-back criteria (`sendback-criteria.md`, written before the draft returned): all seven were met, so nothing was sent back. Cycles used: 0.

```yaml
VERDICT: FAIL
DIGEST:
  headline: 'BUG-2582 plan is ready for signature: 5 main-session-direct tasks, 11
    SCs, check exit 0, all 6 reader findings applied and resolved. VERDICT is FAIL
    only because DEC-123 forces worst-member over two findings-carrying reader FAILs,
    which is defect 2 itself. Do not loop back.'
  team: plan
  steps_run: 6
  cycles_used: 0
  members:
  - step: draft
    persona: harness-pm
    verdict: PASS
    headline: 'BRIEF with 9 SCs and a 3-task plan drafted; check exit 0; OQ-1: apply
      never marks findings resolved'
    files_touched:
    - .harness/harness/features/BUG-2582-plan-station-and-rollup/BRIEF.md
    - .harness/harness/features/BUG-2582-plan-station-and-rollup/plan.yaml
    - .harness/harness/features/BUG-2582-plan-station-and-rollup/notes/research-plan-station-and-rollup.md
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: '5 findings: INV-34 stub start, T-02 member binding, resolved-record
      identity, red-first discrimination, T-03 docs form'
    files_touched: []
  - step: should-not-exist
    persona: fable-advisor
    verdict: FAIL
    headline: T-02 would ship without a trigger unless the plan team's apply runs
      set-panel
    files_touched: []
  - step: design
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Self-scoped out: no user-facing surface'
    files_touched: []
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: All 6 findings applied and set resolved; T-04 witness and T-05 team-file
      apply step added; INV-34 stub start measured admissible (D-04, no guard change)
    files_touched:
    - .harness/harness/features/BUG-2582-plan-station-and-rollup/plan.yaml
    - .harness/harness/features/BUG-2582-plan-station-and-rollup/BRIEF.md
    - .harness/harness/features/BUG-2582-plan-station-and-rollup/notes/research-plan-c1-apply.md
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Operator, orchestrator and code maintainer perspectives pass at plan
      time; T-05 crosses no out-of-scope item
    files_touched:
    - .harness/harness/features/BUG-2582-plan-station-and-rollup/notes/research-BUG-2582-plan-station-and-rollup-goalcheck-plan.md
  must_fix: []
  files_touched:
  - .harness/harness/features/BUG-2582-plan-station-and-rollup/BRIEF.md
  - .harness/harness/features/BUG-2582-plan-station-and-rollup/plan.yaml
  - .harness/harness/features/BUG-2582-plan-station-and-rollup/notes/research-plan-station-and-rollup.md
  - .harness/harness/features/BUG-2582-plan-station-and-rollup/notes/research-plan-c1-apply.md
  - .harness/harness/features/BUG-2582-plan-station-and-rollup/notes/research-BUG-2582-plan-station-and-rollup-goalcheck-plan.md
  - .harness/harness/features/BUG-2582-plan-station-and-rollup/runs/2026-11-27-01-plan-product/state.yaml
  - .harness/harness/features/BUG-2582-plan-station-and-rollup/runs/2026-11-27-01-plan-product/panel-c1.md
  - .harness/harness/features/BUG-2582-plan-station-and-rollup/runs/2026-11-27-01-plan-product/sendback-criteria.md
  expertise_update: []
  branch: feat/BUG-2582-plan-station-and-rollup
  escalations: []
  adequacy_notes:
  - 'The team VERDICT FAIL is the forced DEC-123 worst-member roll-up over the scope
    and should-not-exist readers. Both returned FAIL to carry findings, and all six
    of those findings are recorded disposition: resolved in plan.yaml panel.findings.
    The plan is pending signature and needs no other cycle. This is the exact defect
    T-02 and T-05 fix.'
  - pm's apply overturned scope finding 1 with primary evidence, and the lead accepts
    it. INV-34's remedy prescribes a stub 'written through plan-merge.py apply' (check_state/plan.py
    inv_34). _seed_new_plan seeds approval pending on that creation, so dispatch-guard
    _plan_preflight admits it. The lead's own check had used a hand-written stub,
    which is refused. D-04 records no guard change, and T-04 witnesses the start-then-convert
    path.
  - 'Decision record: DEC-123, DEC-254 and DEC-228 are amended, not replaced by new
    decisions. DEC-174, DEC-229 and DEC-191 are kept. FEAT-41''s loader pair stays
    byte-identical, and T-01''s verify asserts this.'
  - 'Prototype gate: not applicable. The design reader self-scoped out, and there
    is no end-user interaction.'
  - 'Correction for the record: the lead''s prose fan-in (panel-c1.md) transcribed
    scope and fable findings without a scope key, which is correct because none is
    a proportionality finding. No reader raised a scope: mission finding, so there
    is no downgrade recommendation.'
  sc_status:
  - id: SC-01
    verdict: not_met
    method: automated
    evidence: plan-time; carried by T-01
  - id: SC-02
    verdict: not_met
    method: automated
    evidence: plan-time; carried by T-01
  - id: SC-03
    verdict: not_met
    method: automated
    evidence: plan-time; carried by T-01
  - id: SC-04
    verdict: not_met
    method: inspection
    evidence: plan-time; carried by T-01
  - id: SC-05
    verdict: not_met
    method: automated
    evidence: plan-time; carried by T-02
  - id: SC-06
    verdict: not_met
    method: automated
    evidence: plan-time; carried by T-02
  - id: SC-07
    verdict: not_met
    method: automated
    evidence: plan-time; carried by T-02
  - id: SC-08
    verdict: not_met
    method: inspection
    evidence: plan-time; carried by T-03 and T-05
  - id: SC-09
    verdict: not_met
    method: automated
    evidence: plan-time; carried by T-01 and T-02 verify
  - id: SC-10
    verdict: not_met
    method: automated
    evidence: plan-time; carried by T-04
  - id: SC-11
    verdict: not_met
    method: automated
    evidence: plan-time; carried by T-05 and T-02
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps: []
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: T-01 fixes the writer but leaves the ordinary plan start blocked.
    why: 'Resolved at apply by measurement: the prescribed apply-written stub carries
      approval pending and is admitted. T-04 witnesses it; D-04.'
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: T-02 keys rank relief by step, not by the exact FAIL member.
    why: 'Resolved at apply: relief keyed by member index, and a duplicated reader
      step is denied.'
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: T-02 does not prove the corresponding on-disk finding is resolved.
    why: 'Resolved at apply: each recomputed PF id must match exactly one row, with
      the same reader and an exact resolved disposition.'
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: T-01/T-02 baseline substitutions are viable, but named failures do not
      prove the intended baseline behavior.
    why: 'Resolved at apply: the named reds now carry the refusal code and the diagnostic
      text.'
  - kind: form
    scope: none
    severity: low
    reader: code-reviewer
    summary: T-03 leaves an unqualified worst-wins statement and understates carve-out
      conditions in summary docs.
    why: Fixed in place at apply.
  - kind: substance
    scope: none
    severity: high
    reader: should-not-exist
    summary: "T-02's carve-out ships without its only trigger \u2014 no shipped step\
      \ ever writes disposition: resolved \u2014 so do not build it in this shape:\
      \ either put the one-line set-panel requirement in teams/plan.yaml apply (with\
      \ DEC-228 flipped to amend and a lanes row for the team file) in this feature,\
      \ or defer T-02 and its T-03 doc amendments together (OQ-1: answer yes)"
    why: Resolved at apply by T-05 (the team file's apply step runs set-panel) and
      the DEC-228 amend.
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
  open_questions:
  - id: OQ-1
    question: 'Signature, one batched ruling (lead recommends accept all three). (a)
      pm''s apply marked 4 high reader findings resolved, and no reader re-read the
      applied T-01, T-02 and T-04 text. Accept pm''s resolution, or request a re-read?
      (b) T-05 is planned in: the plan team''s teams/plan.yaml apply step runs set-panel
      after record-panel, and DEC-228 is amended. This goes beyond the surfaces you
      listed, because Destination 2 has no trigger without it. Keep it, or strike
      T-05, SC-11 and the DEC-228 row together? (c) D-04 makes no dispatch-guard change.
      Only the apply-written INV-34 stub can start a plan, and a hand-written stub
      stays refused as at base. Accept?'
    blocking: true
  - id: OQ-2
    question: Should the build also qualify validate-digest.py's unchanged header
      comment ('the top verdict must be the WORST member verdict')? Advisory.
    blocking: false
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2582-plan-station-and-rollup/.harness/harness/features/BUG-2582-plan-station-and-rollup/runs/2026-11-27-01-plan-product/digest.md
```
