# BUG-2565 plan run 2026-11-27-02-plan-product — PASS, plan pending signature

**BLUF:** plan.yaml now exists, built from the run-01 proposal: 6 main-session-direct tasks, 5 plan decisions, and source_issues [2565, 2482]. All three readers ran. pm applied all 8 findings: record-panel recorded 8 PF ids and `plan-merge.py check` exited 0 (34 anchors, 0 failures). The goal-check passed all three perspectives (operator, orchestrator, code maintainer) and confirmed that all six operator constraints hold. Approval is `pending`, with no `approval:` written.

## Steps
- draft (pm) PASS: landed the proposal. T-02's verify was timed at about 21s (bun test 19s, typecheck 2s) at base 104252db (Q-05 answered).
- scope (code-reviewer) FAIL: a valid reader return and not a loop_back. It found 2 high substance, 1 med substance and 1 med form. Note: `notes/review-harness-code-reviewer-plan-c1.md`.
- should-not-exist (fable-advisor) PASS: 1 low proportionality finding (scope task) and 3 info findings. Two of the info findings endorse keeping D-04 and T-06's extra stale sites; it checked both against the worktree. Its findings are in `panel-c1.md`.
- design (ui-reviewer) PASS: scoped itself out because the plan has no user-facing surface.
- apply (pm) PASS: how each finding was handled is in `notes/research-panel-c1-apply.md`. T-01 is now transcript-backed: the parent's `data` is compared with the refused `data`, and an inconclusive result stops the cutover. T-04 uses `typed_equal` and adds an `additionalProperties: 0` fixture. T-02 and T-03 have independent witnesses. A DEC-202 amend row was added. `--check` was removed from T-04's verify but kept in T-03, because SC-07 names it.
- goalcheck (pm) PASS: `notes/research-BUG-2565-digest-frontmatter-contract-goalcheck-plan.md`.

## Lead assessment
- **Prototype gate:** none is required. The plan changes agent tool contracts and docs, not an end-user surface (ui-reviewer in_scope false). Visual-designer was not consulted, so this call is mine and the operator can override it.
- **The high findings were applied without a re-read (O-10).** The team has no re-read step, so the rewritten T-01 intent and verify and the T-04 `typed_equal` and drift-fixture text have not been read by any reader. That includes literal gate commands, for example T-02's `grep -c validatorUnavailableRefusal ... = 0`. I raise this as one blocking signature question.
- No proportionality finding has `scope: mission`, so I make no downgrade recommendation.

## Questions for signature
See DIGEST `open_questions`. Q-S1 is blocking. The others are prune or extend choices: SC-03 wording, org.html stale text, and the test-dispatch-guard case_30 docstring.

## Harness defect carried from run 01
Q-02 is the route from a station-only seed to tasks. It was acknowledged as separate and is not repeated here.

```yaml
VERDICT: FAIL
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2565-digest-frontmatter-contract/.harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-02-plan-product/digest.md
DIGEST:
  headline: The BUG-2565 plan is applied and pending signature, but rolls up FAIL.
    The scope reader failed the draft on 2 high findings. pm applied all 8 findings
    in this run, record-panel and check exit 0, and the goal-check passes all three
    perspectives. The high-finding remediations were never re-read, and that goes
    to signature (Q-S1). No re-plan cycle is needed.
  open_questions:
  - id: Q-S1
    question: 'Two high substance findings were applied without a re-read: T-01 now
      uses transcript-backed refused attempts, compares parent data with refused data,
      and stops the cutover when inconclusive; T-04 now uses typed_equal plus an additionalProperties:
      0 fixture. The rewritten T-01 intent and verify, the T-04 drift text and T-02''s
      literal gate `grep -c validatorUnavailableRefusal tests/unit/omp-hooks.test.ts
      = 0` have not been read by any reader. Recommendation: at signature, read T-01''s
      and T-04''s verify blocks as written (notes/research-panel-c1-apply.md maps
      each change), or order one scope re-read before signing.'
    blocking: true
  - id: Q-S2
    question: 'The code-reviewer advised making SC-03''s ''unchanged'' explicit: the
      host call is not rewritten, and the normalized dispatch-guard input stays its
      own interface. It was outside every recorded finding, so SC-03 is unchanged.
      Should it be amended at signature?'
    blocking: false
  - id: Q-S3
    question: .harness/harness/docs/org.html still says the OMP task hook refuses
      outputSchema/schemaMode and injects the strict schema. No task owns it. Should
      T-06 take it? It is a surviving contradiction outside the operator's named docs.
    blocking: false
  - id: Q-S4
    question: The docstring of tests/integration/test-dispatch-guard.py case_30_schema_controls_are_not_the_guards
      will go stale because it says the hook refuses and injects; the assertion stays
      true. Should T-02 own the one-line comment fix?
    blocking: false
  files_touched:
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/plan.yaml
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/BRIEF.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-plan-proposal.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-panel-c1-apply.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-BUG-2565-digest-frontmatter-contract-goalcheck-plan.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/review-harness-code-reviewer-plan-c1.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/review-harness-ui-reviewer-plan-c1.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/observations/harness-pm.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-02-plan-product/state.yaml
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-02-plan-product/panel-c1.md
  expertise_update: []
  team: plan
  steps_run: 6
  cycles_used: 0
  members:
  - step: draft
    persona: harness-pm
    verdict: PASS
    headline: 'Proposal landed into plan.yaml: 6 tasks, 5 decisions, source_issues
      [2565, 2482], check exit 0; T-02 verify timed at about 21s'
    files_touched:
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/plan.yaml
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-plan-proposal.md
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/observations/harness-pm.md
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Keep the six-task plan; fix the T-01 refusal probe and the T-04 drift
      equality before signature; DEC-202 needs an amend
    files_touched:
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/review-harness-code-reviewer-plan-c1.md
  - step: should-not-exist
    persona: fable-advisor
    verdict: PASS
    headline: Nothing to cut; one low dual-drift-checker redundancy; D-04 and T-06
      extras checked against the worktree as load-bearing
    files_touched: []
  - step: design
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode A scoped out: no user-facing surface'
    files_touched:
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/review-harness-ui-reviewer-plan-c1.md
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: All 8 cycle-1 findings applied; record-panel (8 PF ids) and check exit
      0
    files_touched:
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/plan.yaml
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/BRIEF.md
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-panel-c1-apply.md
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/observations/harness-pm.md
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Operator, orchestrator and code maintainer perspectives all pass; all
      six hard constraints hold; org.html stale text is an advisory gap
    files_touched:
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-BUG-2565-digest-frontmatter-contract-goalcheck-plan.md
  must_fix:
  - 'Before signing, confirm the unread remediation text for the two high scope findings
    (T-01 refusal probe, T-04 typed_equal drift gate): operator read or one scope
    re-read (Q-S1)'
  branch: none
  escalations: []
  adequacy_notes:
  - The FAIL comes only from the scope reader's verdict on the pre-apply draft. All
    8 findings were applied in this run; the panel is recorded and check passes. Approval
    stays pending.
  - The scope FAIL was routed to apply, not to loop_back, so cycles stay at 0.
  - 'Prototype gate: none is required, because the plan changes no end-user surface
    (ui-reviewer in_scope false). Visual-designer was not consulted, so this is the
    lead''s call and the operator can override it.'
  - fable-advisor and the goal-check both judged D-04 and T-06's extra stale sites
    to be load-bearing (Q-03 from run 01). They stay in the plan.
  - No proportionality finding has scope mission, so there is no downgrade recommendation.
  - plan-merge apply printed no APPROVAL-RESET receipt, so gh-sync status was not
    run. The check-state violations it printed (BRIEF unapproved, INV-37 Build receipt)
    are expected at draft.
  sc_status:
  - id: operator
    verdict: pass
    method: inspection
    evidence: SC-01, SC-02 via T-02; SC-09, SC-10 via T-06; SC-11 via T-01 and T-06
  - id: orchestrator
    verdict: pass
    method: inspection
    evidence: SC-03, SC-04 via T-02; SC-05 via T-05 live binding probe
  - id: code maintainer
    verdict: pass
    method: inspection
    evidence: SC-06 via T-04 (typed_equal drift fixtures); SC-07, SC-08 via T-03
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps:
  - org.html stale hook text has no owning task (Q-S3)
  - test-dispatch-guard case_30 docstring will go stale (Q-S4)
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: T-01 can pass without observing a refused yield or detecting its payload
      in the parent result.
    why: 'Applied: T-01 is now transcript-backed, compares parent data with refused
      data, and treats an inconclusive result as stopping the cutover. No reader has
      re-read it (Q-S1).'
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: T-04's proposed Python equality admits type-changing frontmatter drift.
    why: 'Applied: typed_equal plus an additionalProperties: 0 drift fixture. No reader
      has re-read it (Q-S1).'
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: T-02 and T-03 do not yet pin several promised failure behaviors.
    why: 'Applied: six process-end cases, six check-domain witnesses, structured deny,
      literal refusal text, and a case for an items node that is present but untyped.'
  - kind: form
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: T-06 omits DEC-202's affected clause and leaves stale sibling wording
      in the named docs.
    why: "Applied: a DEC-202 amend row was added, the DEC-126/237 schema directory\
      \ reference was fixed, and the SPEC \xA78.3 cutover paragraph is now marked\
      \ historical."
  - kind: proportionality
    scope: task
    severity: low
    reader: should-not-exist
    summary: gen-agent-output.py --check is a second home for the drift check the
      grilling settled into check-omp-port.py alone
    why: 'Trimmed: --check was removed from T-04''s verify; it stays in T-03 as a
      self-test aid because SC-07 names it.'
  - kind: substance
    scope: none
    severity: info
    reader: should-not-exist
    summary: T-01 Run B measures a question (dataless_result_yield_without_hook) whose
      answer changes nothing in the build
    why: 'Applied: T-01''s intent now says Run B documents and does not gate.'
  - kind: substance
    scope: none
    severity: info
    reader: should-not-exist
    summary: 'D-04 should stay: the pass-through it deletes is verifiably broken by
      the frontmatter route'
    why: Endorsement; no change.
  - kind: substance
    scope: none
    severity: info
    reader: should-not-exist
    summary: "T-06's extra sites should stay: SPEC \xA78.3, harness-team SKILL and\
      \ the DEC-100 amend are live stale text, not padding"
    why: Endorsement; no change.
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
