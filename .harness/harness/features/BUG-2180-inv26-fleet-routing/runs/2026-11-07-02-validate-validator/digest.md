# BUG-2180 validation — FAIL

**Pin `556a23ffea8dafcf5110e80fe25a42ee2542ff2b`: routing behavior satisfies SC-01–SC-04, but mandatory test-complexity and change-specific unit-coverage gates fail.** All five readers ran; no source/test edits. `severity_max: high`, `matrix_ok: false`, `cycles_used: 1` (QA evidence-assessment sendback, not a code-fix round).

## One ranked must-fix list

1. **R1 — substance / high / T-01 / code-reviewer:** new `case_x` at `tests/integration/test-check-state-inv26.py:712` is grade 1 (cyclomatic 48, cognitive 38, ABC 124.9), below test bar 3. Split its independent scenarios coherently without weakening any assertion. Reviewer measured pinned grader exit 1; mandatory high finding, not style. Evidence: `notes/review-harness-code-reviewer-c0.md`, stage 2.
2. **R2 — substance / high / T-01 / validator-lead, QA evidence:** required unit-kind coverage is missing for changed INV-26 runtime logic. The 57-file unit suite is green but none exercises this change; integration evidence cannot replace the unit floor. Add a discriminating direct unit test, not a ceremonial duplicate. Lead severity reflects a mandatory matrix gate; QA calls the gap blocking. Evidence: `notes/review-harness-qa-c1.md`; product DEC-217 (`.harness/harness/docs/DECISIONS.md:7044–7068`) and verification presence rule. **Scope dependency:** a `tests/unit/` path is outside T-01's signed two-file list; obtain scope approval before adding it. DEC-174 keeps remediation main-session-direct, never a delegated gate-code author.

Fix R1 within existing ownership; resolve R2 scope before unit-test authoring; re-pin and revalidate the resulting code. No production defect, security finding, or UI obligation was identified. No duplicate findings were raised.

## Evidence and reconciliation

- QA final **FAIL**: c1 explicitly retracts c0's incorrect “unrelated green unit kind satisfies floor” claim; c0 remains preserved. Integration: 84 files exit 0. Unit: 57 files exit 0 but zero change-specific unit tests. Literal T-01 verify: 37 ok, zero FAIL, 5.97s. Natural base red: 31 existing controls pass, x.1–x.6 fail semantically; per-SC fail-first in `notes/review-harness-qa-c0.md`. QA also measured both reviewed code files identical to build seam `554f219e`.
- SC-01 **pass**: x.1–x.4 own-binding/overlap/owner-off routing; SC-02 **pass**: retained 31 controls plus x.4 mixed routing; SC-03 **pass**: x.5 attributed GhError plus healthy comparison; SC-04 **pass**: x.6 broken binding, no fallback, healthy comparison. These are behavioral statuses, not ship clearance.
- PM **PASS**, `notes/research-BUG-2180-inv26-fleet-routing-goalcheck-validate-c0.md`: both perspectives/SCs were partial solely awaiting independent QA; collected c0 evidence discharges that dependency. Matrix and complexity remain separate blockers.
- Security **PASS**, `notes/review-harness-security-reviewer-c0.md`: routing/diagnostic trust boundaries inspected, no exploitable regression. UI **PASS, not in scope**, `notes/review-harness-ui-reviewer-c0.md`: measured 12-path full census, CLI/test/feature records only, no visual assurance claimed.
- BoardError-only branch coverage is an **assessed nonblocking assurance qualification, no required action**, per QA c1: same handler is exercised via GhError, and SC-03 does not demand another exception case. Live Kaya smoke remains builder evidence, not independently repeated by this panel. Missing product guidance paths introduced no unresolved bounded behavior question.

## Open question

**Q1 (blocking, sent to Main):** authorize extending T-01's file scope for the required discriminating `tests/unit/` coverage, or route the scope decision to the operator. Validation does not authorize that amendment itself.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "556a23ff: SC-01\u2013SC-04 pass behaviorally; mandatory complexity and\
    \ unit-coverage gates fail."
  team: validate
  steps_run: 5
  cycles_used: 1
  members:
  - step: qa
    persona: harness-qa
    verdict: FAIL
    headline: Required change-specific unit coverage is missing; integration passes.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: New case_x fails mandatory complexity grading.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: No exploitable security regression identified.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Measured pinned census confirms no UI changes.
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Both perspectives covered; pending behavioral evidence subsequently
      supplied by QA.
    files_touched: []
  must_fix:
  - 'T-01: split case_x into coherent scenarios while preserving assertions; grade
    1 is below the mandatory test-code bar.'
  - 'T-01: obtain file-scope approval and add discriminating unit-kind coverage of
    changed INV-26 logic.'
  severity_max: high
  matrix_ok: false
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer
    summary: 'T-01: new case_x fails mandatory complexity grading.'
    why: 'tests/integration/test-check-state-inv26.py:712 measures cyclomatic 48,
      cognitive 38, ABC 124.9: grade 1 versus test bar 3.'
  - kind: substance
    scope: none
    severity: high
    reader: validator-lead
    summary: 'T-01: required change-specific unit coverage is absent.'
    why: QA c1 confirms no unit-kind test exercises changed INV-26 logic. DEC-217
      retains the runtime-code unit floor; unrelated green tests cannot satisfy presence.
  sc_status:
  - id: SC-01
    verdict: pass
    method: automated
    evidence: "QA c0: x.1\u2013x.4 fail at base and pass at pin."
  - id: SC-02
    verdict: pass
    method: automated
    evidence: 'QA c0: 31 retained controls pass; mixed-routing x.4 fails at base and
      passes at pin.'
  - id: SC-03
    verdict: pass
    method: automated
    evidence: 'QA c0: GhError/healthy-feature case x.5 fails at base and passes at
      pin.'
  - id: SC-04
    verdict: pass
    method: automated
    evidence: 'QA c0: broken-binding/no-fallback case x.6 fails at base and passes
      at pin.'
  coverage_gaps:
  - Zero change-specific unit tests despite 57 green unit files; integration's 84
    green files do not replace this floor.
  adequacy_notes:
  - 'Literal verify: 37 ok, zero FAIL, 5.97 seconds. QA confirmed reviewed code equals
    build seam 554f219e.'
  - QA c1 retracts c0's unit-satisfied claim; one assessment sendback accounts for
    cycles_used.
  - 'Separate BoardError coverage is nonblocking: GhError exercises the shared handler;
    acceptance was not widened.'
  - Remediation remains main-session-direct under DEC-174.
  readers:
  - reader: qa
    status: ran
    persona: harness-qa
    reason: none
  - reader: code
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: security
    status: ran
    persona: harness-security-reviewer
    reason: none
  - reader: ui
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
  open_questions:
  - id: Q1
    question: Authorize extending T-01's signed file scope for required discriminating
      tests/unit coverage, or route that scope decision to the operator?
    blocking: true
  needs_approval: true
  files_touched: []
  branch: none
  escalations: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2180-inv26-fleet-routing/.harness/harness/features/BUG-2180-inv26-fleet-routing/runs/2026-11-07-02-validate-validator/digest.md
```
