# FEAT-2297 plan — acceptance and assessment

The plan must preserve all 13 settled operator decisions and return BRIEF.md and plan.yaml pending for one operator signature.

## Pre-dispatch acceptance

- All implementation tasks use main-session-direct; no engineering-lead dispatch.
- Schema defaults and any required conditional keys are explicit proposed decisions, not unresolved developer guesses.
- Every reader is classified; Python readers use one validated loader, with only the named repair/report carve-outs and advisory TypeScript budget exception.
- One shared valid-config fixture builder replaces the three shared writers and covers inline fixtures.
- Explicit tasks dispose of every REMOVABLE inventory item, rewrite every fail-open test, and prove net affected test-line reduction against a pinned base receipt.
- Unit and integration evidence meet the live feature/runtime/config-shape test-matrix floors without implementing #2293.
- Kaya migration names its actual checkout/process and lands 2-to-3 on kaya main through an operator-approved PR; no delegated ownership fiction.
- Changed reader sites maintain canonical-reader-classification.json.
- Plan check and record-panel must pass; one exit goal-check judges the grilling intent by perspective.

## Prototype decision

No new end-user interaction surface is requested: this is configuration validation, reader migration and refusal diagnostics. A high-fidelity prototype is not required. The design reader independently checks this scope; operator may override either way.

## Final assessment — ESCALATE

BRIEF.md and plan.yaml remain pending: 10 main-session-direct tasks, 8 signature decisions, 10 SCs. Required record-panel and final plan check passed (10 tasks, 101 anchors, zero failures). Three independent readers ran; PM resolved/dismissed seven findings and retained one evidenced scope question. No implementation checks ran.

### Decisions needed

- Operator — OQ-SMOKE: remote smoke main `7f87b403b6dcf1e3379b7a1b6b7a01ff74ed0b04` has object-valued `github.board.stations`, invalid under the target array contract. Migration/removal is excluded. Explicitly accept expected fleet refusal or authorize separate scope; never weaken the loader silently.
- Main — GAP-SIMPLIFY: mandatory four-angle simplify did not run: product host cannot spawn eng personas and available task tools do not expose them. Complete it or resolve the process conflict before signature. Panel/goalcheck are not substitutes.

### Members and durable pointers

- draft / PM PASS: `../../notes/research-config-contract.md` — defaults/API, reader census, 30 removable / 12 behavior / 110 fixture rows, Kaya authority and receipts.
- scope / code-reviewer PASS: `../../notes/review-harness-code-reviewer-plan-c0.md` — local cumulative proof before Kaya; applied.
- should-not-exist / Fable PASS: `panel-c0.md` — seven task findings, no mission finding; smoke consequence remains open.
- design / UI-reviewer PASS: `../../notes/review-harness-ui-reviewer-plan-c0.md` — no interaction surface; no DESIGN/prototype, operator-overridable.
- apply / PM ESCALATE: research note dispositions — no repair allowlist, generated TS fixture, bounded census, feature-only reduction checker, no new changelog. Literal verify blocks corrected through existing writer.
- goalcheck / PM ESCALATE: `../../notes/research-FEAT-2297-harness-json-schema-goalcheck-plan.md` — operator partial pending smoke decision; maintainer/reader pass for plan coverage only; implementation SCs unproven.

Kaya T-09 follows local T-10 evidence, publishes a dedicated PR, requires operator merge authorization and validates remote main. Unit and integration floors, one builder, exhaustive negative test-line delta and #2293 exclusion remain. Main should re-record the panel from final digest including goalcheck. Six steps completed; zero send-backs.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: BRIEF and plan pending; checks pass, but smoke disposition and four-angle
    simplify remain before signature.
  open_questions:
  - id: OQ-SMOKE
    question: Smoke main 7f87b403b6dcf1e3379b7a1b6b7a01ff74ed0b04 has object-valued
      github.board.stations and will fail the new loader/fleet aggregate. Explicitly
      retain expected refusal under the existing exclusion, or authorize separate
      migration/removal scope?
    blocking: true
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2297-harness-json-schema/.harness/harness/features/FEAT-2297-harness-json-schema/BRIEF.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2297-harness-json-schema/.harness/harness/features/FEAT-2297-harness-json-schema/plan.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2297-harness-json-schema/.harness/harness/features/FEAT-2297-harness-json-schema/notes/research-config-contract.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2297-harness-json-schema/.harness/harness/features/FEAT-2297-harness-json-schema/notes/research-FEAT-2297-harness-json-schema-goalcheck-plan.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2297-harness-json-schema/.harness/harness/features/FEAT-2297-harness-json-schema/runs/2026-11-22-01-plan-product/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2297-harness-json-schema/.harness/harness/features/FEAT-2297-harness-json-schema/runs/2026-11-22-01-plan-product/panel-c0.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2297-harness-json-schema/.harness/harness/features/FEAT-2297-harness-json-schema/runs/2026-11-22-01-plan-product/host-findings-c0.md
  expertise_update: []
  team: plan
  steps_run: 6
  cycles_used: 0
  members:
  - step: draft
    persona: harness-pm
    verdict: PASS
    headline: 10 direct tasks, 8 decisions, 10 SCs; initial plan check passed.
    files_touched:
    - BRIEF.md
    - plan.yaml
    - notes/research-config-contract.md
  - step: scope
    persona: harness-code-reviewer
    verdict: PASS
    headline: Outcomes preserved; local proof should precede Kaya landing.
    files_touched: []
  - step: should-not-exist
    persona: fable-advisor
    verdict: PASS
    headline: Seven task findings; no mission downgrade.
    files_touched: []
  - step: design
    persona: harness-ui-reviewer
    verdict: PASS
    headline: No interaction surface; DESIGN/prototype unnecessary, operator-overridable.
    files_touched: []
  - step: apply
    persona: harness-pm
    verdict: ESCALATE
    headline: Seven findings resolved/dismissed; required checks pass; smoke needs
      operator disposition.
    files_touched:
    - BRIEF.md
    - plan.yaml
    - notes/research-config-contract.md
  - step: goalcheck
    persona: harness-pm
    verdict: ESCALATE
    headline: Intent covered; operator partial pending smoke ruling, maintainer/reader
      pass for plan coverage.
    files_touched:
    - notes/research-FEAT-2297-harness-json-schema-goalcheck-plan.md
  must_fix:
  - Resolve OQ-SMOKE before signature without silently changing excluded scope.
  - Main must complete four-angle simplify or resolve its persona/tool authorization
    conflict before signature.
  branch: feat/FEAT-2297-harness-json-schema
  escalations:
  - id: GAP-SIMPLIFY
    raised_by: harness-product-lead
    question: Mandatory simplify requires four eng-persona readers outside this product
      host's allowlist and available task agents; Main must own the pass or resolve
      the process conflict.
    domain: Harness orchestration
    routed_to: Main
    resolution: unresolved; Main messaged; no substitute pass claimed
    decided_by: none
    recorded_as: notes/research-config-contract.md; exit goalcheck; run digest
  adequacy_notes:
  - 'Record-panel and final plan-merge check exited 0: 10 tasks, 101 anchors, zero
    failures. Both deliverables pending.'
  - 'All tasks main-session-direct. One builder, exhaustive inventory dispositions,
    negative net-line receipt and unit/integration floors remain; #2293 excluded.'
  - Kaya T-09 follows local proof, publishes a dedicated PR, requires operator merge
    authorization and validates remote main; no migration performed.
  - No interaction surface; prototype unnecessary, independently confirmed by UI reviewer
    and overridable by operator.
  - Seven findings resolved/dismissed with reasons; smoke remains open. Original severity/kind
    preserved. Substance finding's source task scope is represented as none to satisfy
    digest schema; source panel retains reader wording.
  - No implementation tests/builds/linters/formatters ran. matrix_ok means planned
    evidence floors are covered, not execution success.
  - Main should record-panel from final digest including goalcheck.
  sc_status:
  - id: SC-01
    verdict: not_met
    method: inspection
    evidence: T-01/T-04 plan coverage; implementation pending.
  - id: SC-02
    verdict: not_met
    method: inspection
    evidence: T-03/T-05/T-06 plan coverage; integration pending.
  - id: SC-03
    verdict: not_met
    method: inspection
    evidence: T-01/T-07/T-09 plan coverage; migration pending.
  - id: SC-04
    verdict: not_met
    method: inspection
    evidence: "T-01/T-02/T-04\u2013T-07/T-10 plan coverage; fixture migration pending."
  - id: SC-05
    verdict: not_met
    method: inspection
    evidence: "T-02/T-04\u2013T-07/T-10 plan coverage; reduction not yet measured."
  - id: SC-06
    verdict: not_met
    method: inspection
    evidence: T-03/T-07/T-10 plan coverage; reader evidence pending.
  - id: SC-07
    verdict: not_met
    method: inspection
    evidence: T-08 plan coverage; amendments and pinned inspection pending.
  - id: SC-08
    verdict: not_met
    method: uat
    evidence: T-09 requires actual operator-authorized Kaya main landing; pending.
  - id: SC-09
    verdict: not_met
    method: inspection
    evidence: T-01/T-04/T-10 plan coverage; configured evidence pending.
  - id: SC-10
    verdict: not_met
    method: inspection
    evidence: "T-02/T-03/T-05\u2013T-07/T-10 plan coverage; integration pending."
  needs_approval: true
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - Mandatory four-angle simplify not run; panel/goalcheck are not substitutes.
  - Implementation verification and Kaya UAT are future signed-plan work.
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: T-10 offline cumulative proof unnecessarily waits for the external Kaya
      merge.
    why: 'Resolved: T-10 precedes T-09; SC-08 remains mandatory.'
  - kind: proportionality
    scope: task
    severity: high
    reader: should-not-exist
    summary: T-03's gate_policy repair-command recognizer solves a Bash lockout the
      gates need not create; scope invalid-config denial to each gate's governed command
      shapes instead.
    why: 'Resolved: existing recognizers precede config reads; matched actions refuse,
      no repair allowlist.'
  - kind: substance
    scope: none
    severity: med
    reader: should-not-exist
    summary: No task dispositions harness-factory-smoke's remote config, which fail-closed
      product_config will start validating.
    why: 'Open: remote main stations object violates target array shape. Migration/removal
      excluded; OQ-SMOKE requires operator disposition.'
  - kind: proportionality
    scope: task
    severity: med
    reader: should-not-exist
    summary: T-10's pinned-SHA reduction checker is one-shot release tooling installed
      as a permanent integration test.
    why: 'Resolved: feature-only bounded checker; controls and own lines included
      in reduction count.'
  - kind: proportionality
    scope: task
    severity: low
    reader: should-not-exist
    summary: Routing omp-hooks.test.ts fixtures through the Python builder CLI buys
      nothing the advisory TS reader can feel.
    why: 'Resolved: builder-generated checked-in fixtures plus freshness census; no
      runtime Python dependency.'
  - kind: proportionality
    scope: task
    severity: low
    reader: should-not-exist
    summary: Creating CHANGELOG.md with a single entry invents a third change-record
      convention.
    why: 'Resolved: existing authority and feature change records retained; no new
      changelog.'
  - kind: proportionality
    scope: task
    severity: info
    reader: should-not-exist
    summary: The fixture census's six --scope flags encode this plan's task boundaries
      into permanent machinery.
    why: 'Resolved: optional file bounds and full census replace task partitions.'
  - kind: proportionality
    scope: task
    severity: info
    reader: should-not-exist
    summary: T-09's dependency on T-08 serializes the only human-latency step behind
      the entire test-reduction grind.
    why: 'Early-publication remedy dismissed: local contract proof must precede remote
      mutation. T-09 follows T-10; latency accepted explicitly.'
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2297-harness-json-schema/.harness/harness/features/FEAT-2297-harness-json-schema/runs/2026-11-22-01-plan-product/digest.md
```
