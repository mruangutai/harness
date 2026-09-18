# UI review — FEAT-1821 plan c0

The planned Checks table is not yet a buildable verification contract. It establishes a sound dark-only, baseline-opt-in evidence model, but it does not pin the exact titles it makes contractual and leaves measurable interaction/focus behavior plus the evidence composition for qualitative review underspecified.

```yaml
VERDICT: FAIL
DIGEST:
  headline: The evidence lane is well bounded, but its Checks-table contract omits exact titles and sufficient interaction/state evidence.
  mode: A
  in_scope: true
  severity_max: high
  findings:
    - reader: design
      summary: "The plan names check ids but never carries the exact Playwright title strings that DESIGN.md and the specs must share."
      severity: med
      kind: substance
      scope: task
      why: "T-02 asks the visual designer to invent one exact title per row while T-03 independently makes byte-exact title matching a gate; without the literal titles in the plan, two implementers can make locally reasonable but incompatible choices and the reviewer cannot verify plan-to-contract fidelity."
    - reader: design
      summary: "C3-KEYBOARD does not explicitly automate focus preservation across state changes, routes, and disclosure close."
      severity: high
      kind: substance
      scope: task
      why: "FEAT-53 DESIGN.md C-3 clauses 2a-3 separately require route-title focus, keyboard-versus-pointer restoration, retained focus after filters/layout changes, Back restoration, and popover restoration; T-03 promises only Tab order and focus-visible, so a surface may pass while losing focus during the interaction defects this lane is intended to measure."
    - reader: design
      summary: "The two inspection rows do not prescribe which routes, states, or interactions their screenshots must expose."
      severity: high
      kind: substance
      scope: task
      why: "One full-page screenshot per row/project can satisfy results accounting while showing only `/`; it need not expose KPI drill, work detail, popover, horizontal table overflow, unavailable/error states, or the approved prototype's interaction outcomes, leaving Mode B with formally complete but substantively insufficient evidence and no permitted ad-hoc browser probe."
    - reader: design
      summary: "The automated row set collapses broad contracts without defining each row's observable predicates."
      severity: med
      kind: substance
      scope: task
      why: "Labels such as TBL-DESKTOP, C4-HATCH, A11Y-AXE, and SRC-TOKENS do not state whether they cover the full named DESIGN clauses or only the examples in T-03; this makes the automatable-versus-inspection boundary non-measurable and can silently leave overflow, sticky-column, real-table/text-equivalent, and colour-not-alone requirements unchecked."
  must_fix:
    - "Put every literal spec title beside its id in the plan (or another single pre-build authority) and require DESIGN.md/specs to copy it exactly."
    - "Expand the automated contract into explicit predicates for C-3 focus transitions/restoration and state which broad DESIGN clauses each check includes or excludes."
    - "Define an evidence manifest for inspection rows: route, fixture state, interaction/setup, viewport, and required screenshot(s), sufficient to compare all intended surfaces with DESIGN.md and the prototype."
  states_unspecified:
    - "keyboard- versus pointer-opened control dismissal and restored focus"
    - "filter/layout result settlement with focus retained"
    - "in-app route transition, fresh load, and browser Back focus"
    - "InfoDisclosure open and close evidence"
    - "KPI drill and work-detail qualitative screenshots"
    - "filtered zero, unavailable/error, overflow, and long-content evidence"
  contract_violations: []
  a11y:
    - "Focus preservation and modality-sensitive focus visibility are specified by FEAT-53 DESIGN.md but are not unambiguously assigned to executable assertions."
    - "Axe coverage cannot substitute for the omitted route/state focus transitions or the contract's visible text equivalents."
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-ui-reviewer-plan-c0.md
```

Confirmed strengths: dark-only scope is consistent with FEAT-53 C-3; screenshots are required for every listed row in both projects; missing evidence fails; and pixel-baseline gating is explicitly opt-in and unused by FEAT-53. Rendered-size/layout remains unverified at plan review and must be judged from the specified post-build evidence.
