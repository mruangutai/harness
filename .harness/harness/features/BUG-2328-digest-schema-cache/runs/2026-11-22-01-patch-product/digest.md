# BUG-2328 patch intake

Acceptance before dispatch: BRIEF.md (at most 120 lines) and plan.yaml both pending; exactly T-01, main-session-direct with DEC-174 reason and lanes table; both named files owned, all settled tests specified including fail-first at dd04e52a and both identity-to-content updates; cache comments updated; all grilling exclusions preserved. No readers, panel or goal-check; no prototype required because this changes schema-data freshness only and adds no end-user interaction (operator may override).

The PM must report plan-merge check, ordinary route check and canonical-reader audit with their exit statuses. Missing artifacts, missing scope/test requirements, non-pending approval or a nonzero required gate fail acceptance. No implementation tests run during intake.

## Conclusion — pending patch ready for signature

BRIEF.md and plan.yaml are pending; main owns the next signature. PM PASS accepted: exactly T-01, main-session-direct under DEC-174, lanes table, both supplied implementation files, all three settled test requirements and every grilling exclusion. The task stays below DEC-182's machine-field bound. No implementation changed.

## Member

- **patch-intake · harness-pm · PASS** — bounded brief and direct task ready; all three required gates exited 0. Receipt: ../../notes/research-digest-schema-cache.md. Deliverables: ../../BRIEF.md and ../../plan.yaml.

## Gate evidence and assessment

PM's durable receipt records `plan-merge.py check --file PLAN --root ROOT` (1 task, 2 anchors, 0 failures), `check-plan-routes.py PLAN` (0 violations), and standalone `check-plan-routes.py --canonical-reader-audit` (0 unresolved sites across 100 Python files), each exit 0. Canonical audit is repository-wide and accepts no plan selector. Interface discovery `--help` exited 2; source established valid invocation before the successful gates.

Acceptance confirms pending approvals, fail-first at dd04e52a with preserved red/green evidence required during build, both identity-to-content updates and distinct-copy preservation, cache-comment update, and unchanged per-loader/Python/host behavior. No readers, panel or goal-check run applies to patch. No prototype required: schema-data freshness introduces no end-user interaction; operator may override.

Existing #2257 null-typecheck and #2329 generic Bun-discovery gaps are disclosed, not repaired or claimed passing. Direct Bun verification is required during build. No implementation tests, builds, linters or formatters ran during intake. SCs remain ungraded until implementation validation.

## Open questions

None. Needs approval: true. Main signs both pending artifacts and owns subsequent direct execution. Zero send-backs.

```yaml
VERDICT: PASS
DIGEST:
  headline: Pending patch brief and one-task direct plan ready for signature; all
    three required intake gates exited 0.
  open_questions: []
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2328-digest-schema-cache/.harness/harness/features/BUG-2328-digest-schema-cache/BRIEF.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2328-digest-schema-cache/.harness/harness/features/BUG-2328-digest-schema-cache/plan.yaml
  expertise_update: []
  team: patch
  steps_run: 1
  cycles_used: 0
  members:
  - step: patch-intake
    persona: harness-pm
    verdict: PASS
    headline: Pending bounded patch artifacts satisfy settled cache-removal scope;
      plan check and both route gates exited 0.
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2328-digest-schema-cache/.harness/harness/features/BUG-2328-digest-schema-cache/BRIEF.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2328-digest-schema-cache/.harness/harness/features/BUG-2328-digest-schema-cache/plan.yaml
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - Exactly T-01, main-session-direct citing DEC-174, lanes table and both requested
    implementation files; task below DEC-182 machine-field bound.
  - All three settled tests, behavioral red at dd04e52a and green after, cache-comment
    updates and grilling exclusions are specified; implementation remains unmodified.
  - PM receipt records plan-merge check exit 0, ordinary route check exit 0 and standalone
    canonical-reader audit exit 0; canonical audit is repository-wide, not plan-scoped.
  - No readers, panel or goal-check run for patch. No prototype required because schema-data
    freshness adds no end-user interaction; operator may override.
  - 'Both approvals remain pending for main-session signature; no implementation tests
    ran. Existing #2257 typecheck and #2329 Bun-discovery gaps are disclosed; direct
    Bun verification is required during build.'
  sc_status: []
  needs_approval: true
  severity_max: none
  matrix_ok: none
  coverage_gaps: []
  findings: []
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2328-digest-schema-cache/.harness/harness/features/BUG-2328-digest-schema-cache/runs/2026-11-22-01-patch-product/digest.md
```
