# FEAT-2225 — pending plan complete; raw reader FAIL preserved

**BRIEF and plan are pending for signature.** PM applied all four reader findings; record-panel and final plan check passed (4 tasks, 40 anchors, zero failures/overlaps). Goalcheck ran once against the grilling and passed operator, orchestrator and code-maintainer perspectives. No implementation, build, tests or signature occurred. The team verdict retains scope's historical FAIL under the mandatory worst-wins rule, not an assertion that its finding remains open.

## Per-member assessment

- **draft / harness-pm — PASS:** by-perspective BRIEF, six SCs, four dependency-ordered tasks and three concrete design decisions; initial 42-anchor check passed. Evidence: notes/research-member-expertise-writes.md.
- **scope / harness-code-reviewer — FAIL:** one high substance omission: internal merge-distill must retain existing owner/binding/mirror provenance. Accepted after checking worktree DEC-220. Now resolved by T-04/D-03; raw reader judgment remains unchanged. Evidence: notes/review-harness-code-reviewer-plan-c1.md; notes/research-member-expertise-apply.md.
- **should-not-exist / fable-advisor — PASS:** three task-proportionality findings (med/low/low), all trimmed by apply: new file-tool guard denial, receipt write-ahead journal, duplicate all-16 E2E exercises. All-16 actual capability and exhaustive configuration checks remain. Full reader findings: panel-c1.md. Reader explicitly supplied PASS after its findings-only response.
- **design / harness-ui-reviewer — PASS:** self-scoped out; no visual surface, DESIGN or prototype needed. Operator can override in either direction. Evidence: notes/review-harness-ui-reviewer-plan-c1.md.
- **apply / harness-pm — PASS:** four findings marked resolved in plan panel, mirror predicate reused, original-member replay supersession/recovery specified, 40 paths re-resolved, pending metadata preserved. Evidence: notes/research-member-expertise-apply.md.
- **goalcheck / harness-pm — PASS:** stated intent fully covered; all six shipped-outcome SCs remain not_met because implementation does not exist. Evidence: notes/research-FEAT-2225-member-expertise-writes-goalcheck-plan.md.

## Signature boundary

No scope: mission proportionality finding exists; scope explicitly found the mission proportionate. No downgrade recommendation and no proportionality re-cycle. No unresolved product question. Null TypeScript typecheck and the credentialled pre-ship handoff_comprehension probe are disclosed in BRIEF Verification gaps. DEC-174/ungranted changes are separated from squad work as T-03/T-04 main-session-direct; #2229 and the queue remain excluded.

Parent actions: re-record the final team digest into panel cycle 1 to include goalcheck; retain existing resolved dispositions. Reconcile the registered run id r-20261121-1-plan-product with assigned directory runs/plan-product (automatic check-state reports absent/orphan mapping); this lead does not own feature.json. Unsigned/missing Build-entry mirror diagnostics remain expected before signature, not green check-state evidence. The raw scope FAIL versus successfully applied plan reporting tension was reported to the orchestrator; no second reader run or fabricated PASS was used.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Pending plan complete and validated; all findings resolved, but worst-wins\
    \ preserves the draft scope reader\u2019s FAIL."
  team: plan
  steps_run: 6
  cycles_used: 0
  members:
  - step: draft
    persona: harness-pm
    verdict: PASS
    headline: Pending BRIEF and four-task plan drafted and validated.
    files_touched:
    - BRIEF.md
    - plan.yaml
    - notes/research-member-expertise-writes.md
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Draft merge-distill omitted existing mirror-provenance enforcement;
      apply subsequently resolved it.
    files_touched: []
  - step: should-not-exist
    persona: fable-advisor
    verdict: PASS
    headline: Three advisory task-proportionality findings; all trimmed during apply.
    files_touched: []
  - step: design
    persona: harness-ui-reviewer
    verdict: PASS
    headline: No visual surface; DESIGN and prototype gates are inapplicable absent
      operator override.
    files_touched: []
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: All four findings resolved; panel recording and 40-anchor plan check
      passed.
    files_touched:
    - BRIEF.md
    - plan.yaml
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Applied plan delivers stated intent across all three perspectives; implementation
      remains unproven.
    files_touched:
    - notes/research-FEAT-2225-member-expertise-writes-goalcheck-plan.md
  must_fix: []
  files_touched:
  - BRIEF.md
  - plan.yaml
  - notes/research-member-expertise-writes.md
  - notes/research-member-expertise-apply.md
  - notes/research-FEAT-2225-member-expertise-writes-goalcheck-plan.md
  - runs/plan-product/state.yaml
  - runs/plan-product/assessment-contract.md
  - runs/plan-product/scope-assessment-c1.md
  - runs/plan-product/panel-c1.md
  branch: feat/FEAT-2225-member-expertise-writes
  open_questions: []
  escalations:
  - id: RUN-01
    raised_by: harness-product-lead
    question: Reconcile registered run r-20261121-1-plan-product with assigned runs/plan-product;
      automatic check-state reports an absent/orphan directory mapping.
    domain: run-registration
    routed_to: harness-orchestrator
    resolution: none
    decided_by: none
    recorded_as: runs/plan-product/digest.md
  expertise_update: []
  adequacy_notes:
  - All paths above are relative to the assigned feature directory.
  - BRIEF Approval and plan approval.status remain pending; source_issues is [2225],
    status is plan. Nobody signed.
  - 'Required record-panel and final plan check exited 0: four tasks, 40 anchors,
    zero failures or overlaps. Every planned file route was resolved.'
  - "All four findings have resolved dispositions. FAIL preserves the scope reader\u2019\
    s historical verdict under mandatory worst-wins; it does not identify unfinished\
    \ plan work."
  - No mission-proportionality finding exists. Scope explicitly found the mission
    proportionate; no downgrade or proportionality re-cycle occurred.
  - Goalcheck ran once against the grilling. No implementation tests, builds, lint
    or formatting ran.
  - No prototype is required for this internal nonvisual change; operator may override
    either way.
  - Orchestrator must record the final digest into panel cycle 1 to add goalcheck
    while retaining resolved dispositions.
  sc_status:
  - id: SC-01
    verdict: not_met
    method: automated
    evidence: Complete planned coverage; implementation evidence absent.
  - id: SC-02
    verdict: not_met
    method: automated
    evidence: Complete planned coverage; implementation evidence absent.
  - id: SC-03
    verdict: not_met
    method: automated
    evidence: Complete planned coverage; implementation evidence absent.
  - id: SC-04
    verdict: not_met
    method: automated
    evidence: Replay and original-member recovery specified; implementation evidence
      absent.
  - id: SC-05
    verdict: not_met
    method: automated
    evidence: Serialized merge and existing mirror predicates specified; implementation
      evidence absent.
  - id: SC-06
    verdict: not_met
    method: inspection
    evidence: Documentation and decision changes specified; pinned implementation
      inspection absent.
  needs_approval: true
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - Configured TypeScript typecheck remains unresolved/null; no static verification
    is claimed.
  - Credentialled handoff_comprehension probe is scheduled before ship, not exercised
    during planning.
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: T-04 omits existing mirror-receipt enforcement from merge-distill.
    why: plan.yaml:210-211 preserves mirror checks only for ordinary merges. A replay-valid
      distill with missing, wrong-repository or recovery-required build-entry evidence
      could merge through the new executor, contrary to DEC-220:7182-7198. Internal
      gh subprocess execution receives no separate host Bash gate.
  - reader: should-not-exist
    summary: T-04's check-domain file-tool Expertise write denial exceeds the grilling's
      settled guard scope and functionally deadens the own-file grants the operator
      explicitly kept
    severity: med
    kind: proportionality
    scope: task
    why: The proposed direct file-tool denial adds an enforcement surface beyond the
      settled shell loophole and functionally denies retained grants. Receipt/file
      verification and replay equality already prevent unreceipted changes from landing.
  - reader: should-not-exist
    summary: T-01's receipt write-ahead journal and interrupted-receipt detection
      guard a single-writer file against a failure mode already caught downstream
    severity: low
    kind: proportionality
    scope: task
    why: 'Per-runtime sequential receipt writes do not require an additional journal:
      atomic persistence and downstream receipt/file mismatch refusals provide the
      required integrity without extra recovery machinery.'
  - reader: should-not-exist
    summary: SC-01/T-04's 16-persona individual end-to-end apply exercises duplicate
      one closure code path sixteen times where per-persona variance is config
    severity: low
    kind: proportionality
    scope: task
    why: Exhaustive persona configuration assertions plus capability-class behavioral
      representatives distinguish the relevant boundaries without sixteen duplicate
      end-to-end runs and their recurring runtime and maintenance cost.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2225-member-expertise-writes/.harness/harness/features/FEAT-2225-member-expertise-writes/runs/plan-product/digest.md
```
