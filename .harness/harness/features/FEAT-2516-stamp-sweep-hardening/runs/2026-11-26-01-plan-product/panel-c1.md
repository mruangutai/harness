# Panel fan-in — FEAT-2516 plan, cycle 1 (run 2026-11-26-01-plan-product)

Three readers ran over the same draft (BRIEF.md, plan.yaml, grilling artifact). Severities and kinds
are each reader's own, transcribed unchanged; no PF ids assigned here (record-panel computes them).

- scope (harness-code-reviewer): FAIL, severity_max high — notes/review-harness-code-reviewer-plan-c1.md
- should-not-exist (fable-advisor): ran, max low — findings transcribed from its returned fenced block
  (it has no write grant); scope for its substance/form findings taken from its own digest.
- design (harness-ui-reviewer): self-scoped out (no user-facing surface), PASS, no findings —
  notes/review-harness-ui-reviewer-plan-c1.md

No `scope: mission` proportionality finding was raised; fable-advisor explicitly did not flag mission
scale (operator settled one feature at grilling).

```yaml
DIGEST:
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: "plan scope + architecture read; VERDICT FAIL, 5 must_fix (T-03 x3, T-01, T-02)"
    - reader: should-not-exist
      status: ran
      persona: fable-advisor
      reason: "resolved and ran; 3 findings, max low"
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: "Mode A self-scoped out: plan touches no user-facing surface; PASS, no findings"
  findings:
    - reader: scope
      kind: substance
      severity: high
      summary: "T-03 can attribute a fix round without meeting the receipt contract."
      why: "verify_evidence_ref counts matching subjects, so multiple main-session-fix effects for different runs are accepted independently. The proposed writer does not restrict the route to a closed FAIL, and INV-7 does not validate the fix_commit field's shape. Exercise a successful composed close as well as run-end."
    - reader: scope
      kind: substance
      severity: high
      summary: "T-03 resolves fleet fix commits in the central planning repository."
      why: "feature-worktree.py#targets places the ledger in Harness while the fix lands in the product repository. Resolving from feature.json's directory refuses a valid product-only commit."
    - reader: scope
      kind: substance
      severity: med
      summary: "T-03's strict timestamp cutoff can omit a real rework round."
      why: "now_iso truncates to seconds; a successor opened in the same second as the first validate run can re-gate that run's FAIL yet be excluded. Use the existing ordered FAIL/regate association for identifiable records and preserve the legacy fallback."
    - reader: scope
      kind: substance
      severity: med
      summary: "T-01's duplicate-hit diagnostic does not name either segment."
      why: "The task retains the count-only reason and checks only '2 segments'; SC-02 names both conflicting segments. The baseline no-hit row is unresolved with an absence reason, not absent."
    - reader: scope
      kind: substance
      severity: med
      summary: "T-02's escape assertions pass if the control-name diagnostic is suppressed."
      why: "The test checks every matching line but requires none. Require exactly one positively identified escaped diagnostic per mode."
    - reader: scope
      kind: form
      severity: med
      summary: "The draft omits decisions governing close-run, spend, regates and served repository separation."
      why: "Add keep dispositions for DEC-159, DEC-227, DEC-230 and DEC-221. DEC-157 is correctly amended, not struck."
    - reader: scope
      kind: form
      severity: low
      summary: "The plan leaves ledger prose internally inconsistent and overstates stamp containment."
      why: "T-03 appends prose beside the unconditional equality statement and omits the new close-run options from the example. T-05 calls the note filename a convention while D-02 reads as requiring it. Limit BRIEF's deletion guarantee to stamps if sibling sweeps remain unchanged."
    - reader: should-not-exist
      kind: substance
      scope: task
      severity: info
      summary: "Grilling's settled B-1/B-4 item — 'have the integration runner invoke --canonical-reader-self-test' — must stay unbuilt; D-03's decline is verified correct and the gate should not push the plan back toward the grilling text."
      why: "CASES already contains *CANONICAL_READER_CASES (test-check-plan-routes.py:2461); a runner step passing the flag would run every canonical-reader case twice per CI run for zero added detection."
    - reader: should-not-exist
      kind: substance
      scope: task
      severity: low
      summary: "T-04's verify runs `test-check-plan-routes.py --canonical-reader-self-test`, keeping alive and exercising a flag whose only remaining caller is that verify line — the very entry point D-03 declares obsolete."
      why: "Verifying a caller-less entry point signals support and invites the rejected CI step back; SC-07's guard plus the default run already prove the superset."
    - reader: should-not-exist
      kind: form
      scope: task
      severity: low
      summary: "T-03.E rewrites `test_the_window_opens_exactly_at_the_first_validate_start` to assert the opposite of its name (a regate AT the window's opening no longer counts) without directing a rename."
      why: "The name asserts inclusive-at-open while the body asserts strictly-after; the next rework_rounds debugger reads the name as the contract and mis-fixes."
```
