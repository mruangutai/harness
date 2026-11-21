# BUG-2241 patch intake

Acceptance for this run: PM delivers BRIEF.md (≤120 lines, every patch-lane section, approval pending) and plan.yaml (plan/1, pending approval, exactly T-01, execution_mode team, one eventual SKILL.md target, every SC traced, source issue 2241, ≤50 task machine-field lines). The rule must require execution-fresh or parameterized ids for state-creating verify recipes and explain why literal single-use ids prevent validation reruns. No detection gate or BUG-2171 recipe change.

Before accepting: PM supplies execution persona domain-resolution evidence, configured change_type rationale, planned skill word delta and budget evidence, and exit-zero outputs for plan-merge check and check-plan-routes from the assigned worktree. Send back missing or contradictory artifacts or failed required gates; an unbounded fix/new interface is a mission-label escalation. No panel, readers, goal-check, build, feature.json writes, or skill edits in this intake. Prototype gate: not applicable—guidance-only text adds no end-user interaction; user may override.

## Assessment

Pending artifacts pass both requested intake gates. Team execution cannot be claimed: the resolver returns NOBODY. PM used the assignment's expressly permitted main-session-direct fallback, without inventing an execution_agent. Preserve PM's ESCALATE under worst-wins; the orchestrator can resolve the packaging exception from the existing user instruction, without changing scope or grants. This remains a bounded patch, not a plan mission.

- PM member: ESCALATE; BRIEF.md is 47 lines, all sections present. plan.yaml is plan/1, exactly T-01, SC-01/02/03 traced, source_issues [2241], pending approval, 13 task machine-field lines. One eventual skill target; no implementation.
- Domain evidence: PM's check-domain.py --resolve on the absolute tracked .claude/skills/harness-spec-driven/SKILL.md path printed NOBODY, exit 0. Lead inspected PRODUCT .harness/harness/docs/SPEC.md:1095-1099 and the control-plane resolver interface:164-269: rule skills have no squad writer. execution_agent: none; execution_mode: main-session-direct, not team. Ordinary signature is still required.
- change_type: docs, because this is guidance-only text with no runtime/enforcement change; configured docs floor is empty. Supplemental content assertion remains mandatory. Proposed rule adds 44 words (1137→1181); PM preload 5001→5045, universal unchanged 1476, below advisory 5500/1900 thresholds.
- PM gate outputs, both from assigned worktree after artifacts landed: plan-merge.py check exited 0, “1 task(s), 1 anchor(s) resolved, 0 failure(s)”; check-plan-routes.py with the explicit plan path exited 0, “OK T-01: declared main-session-direct (.agents/skills/harness-spec-driven/SKILL.md ungranted)” and “0 violation(s) across 1 plan(s)”. Exact invocations and outputs: notes/research-verify-id.md, Pending artifacts and intake gates. Lead did not rerun them.
- No readers, panel, goal-check, UAT, build, source changes or feature.json writes. Implementation SCs remain not_met; intake gates do not prove the future rule exists. cycles_used: 0.
- Separate nonblocking defect: check-skill-weight.py --json raised NameError; plain interface passed. Lead inspected control-plane script:20-23,141-146 (json.dumps with no json import). No repair in scope.

Member handoff: notes/research-verify-id.md. Open routing discrepancy: literal team acceptance cannot hold under existing grants; use the already-authorized fallback at signature. Open question for Harness owner: whether to track the unrelated --json defect separately.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: Pending intake artifacts pass both gates; NOBODY requires the permitted
    main-session-direct fallback instead of team execution.
  open_questions:
  - id: OQ-02
    question: Should the Harness owner track the unrelated check-skill-weight.py --json
      NameError separately? Plain-output measurement succeeded.
    blocking: false
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2241-smoke-run-id/.harness/harness/features/BUG-2241-smoke-run-id/BRIEF.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2241-smoke-run-id/.harness/harness/features/BUG-2241-smoke-run-id/plan.yaml
  expertise_update: []
  team: patch
  steps_run: 1
  cycles_used: 0
  members:
  - step: intake
    persona: harness-pm
    verdict: ESCALATE
    headline: Pending BRIEF and one-task plan pass both intake gates; requested team
      routing conflicts with NOBODY grant.
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2241-smoke-run-id/.harness/harness/features/BUG-2241-smoke-run-id/BRIEF.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2241-smoke-run-id/.harness/harness/features/BUG-2241-smoke-run-id/plan.yaml
  must_fix: []
  branch: none
  escalations:
  - id: E-01
    raised_by: harness-pm
    question: Requested team execution cannot name a granted execution_agent for this
      rule skill.
    domain: routing
    routed_to: harness-orchestrator
    resolution: The assignment explicitly permits main-session-direct when no squad
      persona holds the target. Resolver output NOBODY establishes that condition;
      pending T-01 uses this fallback. Preserve this exception at signature rather
      than fabricate a grant. Member ESCALATE preserved under worst-wins.
    decided_by: harness-product-lead applying the assignment's conditional fallback
    recorded_as: plan.yaml tasks[T-01].execution_mode and runs/2026-11-21-01-plan-product/digest.md
  adequacy_notes:
  - BRIEF is 47 lines with every required section and approval pending. plan/1 has
    exactly T-01, pending approval, every SC traced, source_issues [2241], one eventual
    SKILL.md target, and 13 task machine-field lines.
  - 'execution_agent: none. PM ran control-plane check-domain.py --resolve on the
    absolute tracked .claude/skills/harness-spec-driven/SKILL.md path: stdout NOBODY,
    exit 0. Lead confirmed PRODUCT SPEC section 6 explicitly forbids squad rule-skill
    grants; no team owner can honestly be selected.'
  - 'change_type: docs, because this is guidance text only, not runtime logic or enforcement.
    Configured required-test floor is empty; the proposed content assertion remains
    mandatory supplemental evidence.'
  - "Proposed rule adds 44 words: skill 1137\u21921181, PM preload 5001\u21925045,\
    \ universal unchanged 1476; advisory budgets 5500/1900. Plain check-skill-weight\
    \ inspection exited 0 without violations; projections are not post-implementation\
    \ measurements."
  - 'PM ran plan-merge.py check with the assigned plan and worktree root: exit 0,
    ''1 task(s), 1 anchor(s) resolved, 0 failure(s)''. PM ran check-plan-routes.py
    from the assigned worktree with the explicit plan path: exit 0, ''OK T-01: declared
    main-session-direct (.agents/skills/harness-spec-driven/SKILL.md ungranted)''
    and ''0 violation(s) across 1 plan(s)''. Exact invocations/output are in notes/research-verify-id.md.
    Lead did not rerun gates.'
  - 'No implementation, skill edits, feature.json writes, readers, panel, goal-check
    or UAT occurred. Prototype not applicable: guidance-only text introduces no end-user
    interaction; operator may override.'
  - The bounded guidance fix remains a patch. The routing exception does not introduce
    a new interface or justify expanding to a plan mission. Both artifacts await ordinary
    signature.
  sc_status:
  - id: SC-01
    verdict: not_met
    method: automated
    evidence: Pending T-01 specifies the complete-rule assertion and baseline red/review-pin
      green evidence; the source change and QA receipts do not yet exist.
  - id: SC-02
    verdict: not_met
    method: inspection
    evidence: Pending T-01 specifies pinned inspection of the rule's clarity and coverage;
      implementation has not begun.
  - id: SC-03
    verdict: not_met
    method: inspection
    evidence: Pending T-01 specifies the one-file diff and actual word/preload receipts;
      intake records baseline measurements and projections only.
  needs_approval: true
  severity_max: med
  matrix_ok: none
  coverage_gaps:
  - Intake gates validate the pending plan, not the unimplemented guidance rule or
    future QA evidence.
  findings: []
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2241-smoke-run-id/.harness/harness/features/BUG-2241-smoke-run-id/runs/2026-11-21-01-plan-product/digest.md
```
