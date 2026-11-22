# FEAT-2340 plan — PASS, pending signature

BRIEF.md and plan.yaml define exactly T-01 prevention → T-02 gate refactor. Both execute main-session-direct: guidance resolves NOBODY; gate code follows DEC-174. Plan status is plan and approval pending. PM reports final plan-merge check exit 0 (two tasks, four anchors, zero failures); no integration tests ran in planning.

Six member steps passed; zero send-backs/cycles. Draft established scope; scope and advisor raised six findings, all applied and recorded with original severity/kind; design self-scoped out; goalcheck passed both perspectives and all four SCs for plan coverage only. Panel source: panel-c1.md. Application dispositions: ../../notes/research-FEAT-2340-gate-one-pattern-per-concept-apply-plan.md. Exit intent check: ../../notes/research-FEAT-2340-gate-one-pattern-per-concept-goalcheck-plan.md.

T-01 uses docs and T-02 scaffolding (configured empty floors); semantics-preserving gate refactor adds existing integrations, not nonexistent unit evidence. Runtime remains unmeasured; Main supervises the 55-second aggregate deadline. run_pool.py buffers incomplete suites, so timeout fails verification without recovering their partial output. Multi-cycle canonicalization and diagnostic ordering require pinned-content inspection: cited existing tests do not prove them. This corrects the grilling's coverage claim without changing its requirements.

No end-user interaction or UI surface: prototype gate not applicable, overridable by operator. Product standard docs are absent; AGENTS.md maps existing SPEC/DECISIONS authority. No new implementation document, test changes, approval mutation or gh-sync. Exclusions remain ship backlog, not added tasks. Open questions: none. Main signature and future implementation verification remain required.

```yaml
VERDICT: PASS
DIGEST:
  headline: Two-task plan passes check and intent goalcheck; pending signature, zero
    send-backs.
  open_questions: []
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2340-gate-one-pattern-per-concept/.harness/harness/features/FEAT-2340-gate-one-pattern-per-concept/BRIEF.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2340-gate-one-pattern-per-concept/.harness/harness/features/FEAT-2340-gate-one-pattern-per-concept/plan.yaml
  expertise_update: []
  team: plan
  steps_run: 6
  cycles_used: 0
  members:
  - step: draft
    persona: harness-pm
    verdict: PASS
    headline: Exactly two constrained tasks drafted; check exit 0.
    files_touched:
    - BRIEF.md
    - plan.yaml
  - step: scope
    persona: harness-code-reviewer
    verdict: PASS
    headline: Proportionate mission; three verification/decision findings.
    files_touched: []
  - step: should-not-exist
    persona: fable-advisor
    verdict: PASS
    headline: Three findings on runner reuse, semantic naming and duplicate scope
      instruction.
    files_touched: []
  - step: design
    persona: harness-ui-reviewer
    verdict: PASS
    headline: No UI or interaction; prototype gate inapplicable.
    files_touched: []
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: All six findings applied; panel recorded and check exit 0.
    files_touched:
    - BRIEF.md
    - plan.yaml
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Both perspectives and all four SCs plan-covered.
    files_touched: []
  must_fix: []
  branch: feat/FEAT-2340-gate-one-pattern-per-concept
  escalations: []
  adequacy_notes:
  - Plan status plan / approval.status pending; signature belongs to Main.
  - 'Both tasks main-session-direct: T-01 guidance resolves NOBODY; T-02 follows DEC-174.
    execution_agent records expertise; execution_mode records direct execution.'
  - T-01 docs and T-02 scaffolding have configured empty floors. Behavior-preserving
    refactor adds existing integrations, not nonexistent unit evidence.
  - 'PM authorized plan-merge check exit 0: two tasks, four anchors, zero failures.
    No builds/tests/lint/formatters ran.'
  - 'Six findings resolved during ordinary apply, not send-backs. Advisor''s own reported
    cycle was not a team send-back: cycles_used 0.'
  - Runtime unmeasured. Main supervises 55-second aggregate deadline; timeout fails
    verification and incomplete-suite buffered output is unavailable.
  - 'Source inspection corrected grilling''s coverage claim: multi-cycle canonicalization
    and diagnostic ordering require pinned-content inspection, not claimed existing
    test assertions.'
  - No end-user interaction/UI; prototype gate inapplicable, operator may override.
  - Standard product docs absent; AGENTS maps existing SPEC/DECISIONS authority. No
    approval writes or gh-sync.
  - Non-proportionality findings serialize scope none per validator; advisor original
    task annotations remain in panel-c1.md. Reader reasons for ran entries serialize
    none per validator.
  sc_status:
  - id: SC-01
    verdict: covered
    method: plan inspection
    evidence: T-01 and exit goalcheck code-maintainer perspective.
  - id: SC-02
    verdict: covered
    method: plan inspection
    evidence: T-02 constraints and pinned multi-cycle/diagnostic inspection.
  - id: SC-03
    verdict: covered
    method: plan inspection
    evidence: T-02 existing suites via run_pool.py; baseline/post receipts and supervised
      deadline.
  - id: SC-04
    verdict: covered
    method: plan inspection
    evidence: Exactly T-01 -> T-02, four implementation files and pinned history obligations.
  needs_approval: true
  severity_max: med
  matrix_ok: n/a
  coverage_gaps:
  - Implementation unverified; integration runtime unmeasured.
  - Existing suites do not establish multi-cycle canonicalization or diagnostic ordering;
    pinned inspection explicitly required.
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: scope
    summary: T-02 verification loses timeout receipts and lacks an aggregate deadline.
    why: plan.yaml:95-112 collects pool.map results before printing anything. A suite
      exceeding timeout=50 raises before completed-suite receipts or the timed-out
      suite's captured output are printed; executor shutdown waits for remaining workers.
      Per-suite timeouts do not enforce the promised whole-command under-60-second
      bound. Preserve failure/timeout output and use Main's supervised aggregate deadline;
      no suite timings were measured.
  - kind: form
    scope: none
    severity: med
    reader: scope
    summary: SC-03 claims existing multi-cycle regression coverage that the cited
      suite does not contain.
    why: BRIEF.md SC-03 claims handoff-x-c1-c2.md canonicalization is asserted. test-check-domain-post.py:919-921
      supplies only single-cycle cases to the helper at :933. A wrong multi-cycle
      canonical name is not excluded by this evidence. Preserve the operator's requirement
      and no-test-rewrite constraint, but assign this edge explicitly to pinned-content
      inspection rather than falsely claiming an existing test. Mixed-case exit coverage
      also does not establish legacy-versus-shape diagnostic ordering.
  - kind: form
    scope: none
    severity: low
    reader: scope
    summary: decisions_affected omits keep dispositions for three directly refactored
      contracts.
    why: Independent index and authority searches identified DEC-159 governing handoff
      phase/supersession, DEC-180 governing pre/post shape semantics, and DEC-182
      governing legacy conversion and single-writer denial. T-02 changes their matchers
      or diagnostic label, but plan.yaml:26-56 omits them. Record keep dispositions;
      no planned behavior contradicts these decisions.
  - kind: substance
    scope: none
    severity: med
    reader: should-not-exist
    summary: T-02 verify hand-rolls a parallel suite runner duplicating run_pool.py
      and losing its private-TMPDIR isolation
    why: Second runner spelling drifts in lockstep (angle-reuse.md:10-11's own example)
      and reintroduces temp leakage run_pool.py:61-66 fixed; run_pool.py accepts explicit
      script paths as a drop-in.
  - kind: substance
    scope: none
    severity: med
    reader: should-not-exist
    summary: SHAPE_REFUSAL_LABEL misnames the POST-mode value 'OVER BUDGET (already
      written)', which is not a refusal
    why: check-domain.py:1463-1468 exists because 'BLOCKED states something that did
      not happen' in POST; REFUSAL in the name restores that misstatement in a feature
      whose SC-01 bullet is 'Name constants for what they mean'. Name was not grilling-settled.
  - kind: form
    scope: none
    severity: low
    reader: should-not-exist
    summary: Ship-time backlog-routing sentence duplicated in T-02 intent; BRIEF Out
      of scope already owns it
    why: One rule in two places that can drift (angle-simplification.md:11-13), and
      a T-02 executor can read issue-filing as T-02 work, expanding a deliberately
      one-file task.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2340-gate-one-pattern-per-concept/.harness/harness/features/FEAT-2340-gate-one-pattern-per-concept/runs/r-20261122-1-plan-product/digest.md
```
