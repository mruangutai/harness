# Plan panel c1 — FEAT-2337

All three readers ran independently. No mission proportionality finding; scope explicitly finds this mission proportionate. Six findings below transcribe their structured return findings unchanged. Scope note: notes/review-harness-code-reviewer-plan-c1.md. Design note: notes/review-harness-ui-reviewer-plan-c1.md. Fable's read-only return: agent://Feat2337Plan.SpotlessThrush.NotableVole (its findings are preserved here, not dependent on that transient path).

PM applies both scope notes, the Fable substance correction and task trims. The info agreement preserves necessary migrations/grants, not a new requirement. For benchmark red-first, preserve harness-brief's discriminating-evidence rule using the cheap wiring check rather than expensive separate mutation ceremony. No assertion is weakened: idle-host ratio and nonzero refusal wiring still required. No prototype needed: UI reader found no end-user interaction; operator may override either direction.

```yaml
DIGEST:
  severity_max: med
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: Pending scope and architecture reviewed; two medium findings, mission proportionate.
    - reader: should-not-exist
      status: ran
      persona: fable-advisor
      reason: Independent critique returned one substance correction, two task trims and one agreement.
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: Mode A self-scoped out; no end-user interaction, DESIGN.md or prototype needed.
  findings:
    - kind: substance
      scope: none
      severity: med
      reader: harness-code-reviewer
      summary: Reserve a separate idle-host acceptance benchmark outside pooled regression execution.
      why: "T-01 adds performance assertions to the standing integration script and T-03 runs complete pooled integration, without explicitly separating the final timing measurement. Concurrent workers can invalidate SC-04's otherwise-idle-host evidence or redden a correct implementation. Specify a review-pin --benchmark invocation outside all suites and clarify default timing-threshold execution (plan.yaml:134-135,206; DEC-211)."
    - kind: form
      scope: none
      severity: med
      reader: harness-code-reviewer
      summary: Complete the semantic decisions_affected sweep with governing keep dispositions.
      why: "The eleven rows omit governing DEC-188, DEC-204, DEC-208, DEC-211, DEC-213, DEC-218, DEC-237 and DEC-238. Also consulted DEC-127, DEC-233 and factory-scoped DEC-250; preserve their scoped boundaries as keep rows. Otherwise trusted receipt destination, async lifecycle and evidence-retention authority are absent from the declared completeness record (plan.yaml:54-109; acceptance.md requirement 5; DEC-254)."
    - kind: substance
      scope: task
      severity: med
      reader: should-not-exist
      summary: "Do not ship the fixed-base (dd04e52a) cumulative changed-test self-grading check in the DEFAULT suite; keep it as --feat2337/review-pin evidence for SC-08, or charter a base-agnostic standing gate under its own decision."
      why: "A default-suite gate pinned to this feature's base re-grades every test function changed by any later feature against the >=3 bar 'without new allowlist exemptions' — repo-wide standing policy enacted as a side effect, unrecorded as a decision; diff range grows unboundedly from a frozen SHA and unrelated failures land inside a FEAT-2337-named check. Acceptance mandates only this feature's tests grade >=3; precedent (test-code-grade.py:197,282) gates a named current-file set, not a pinned diff."
    - kind: proportionality
      scope: task
      severity: low
      reader: should-not-exist
      summary: "SC-04's gating serial-execution mutant is near-tautological given the benchmark's own serial-adapter arm; drop mutant-first sequencing, keep at most a cheap nonzero-exit wiring check."
      why: "If parallel <= 0.75 x sequential passes, the serial arm substituted as candidate trivially fails at ratio ~1.0; the mutant only proves assertion wiring fires, yet SC-04 makes it a red-first precondition on a benchmark. [unverified: exact mutant mechanics, benchmark not yet built]"
    - kind: proportionality
      scope: task
      severity: low
      reader: should-not-exist
      summary: "T-02's 'zero fallback runner invocations with a process witness' verifies absence of code the same task deletes; acceptable only as a trivial PATH/argv shim, not bespoke process tracing."
      why: "T-02 deletes _reverify_suite/_resolve_run_unit_tests_bin/RUN_UNIT_TESTS_BIN outright and SC-10 pins an inspection that no rerun implementation remains; a runtime negative-proof on top is machinery without discrimination unless essentially free."
    - kind: substance
      scope: task
      severity: info
      reader: should-not-exist
      summary: "Agreement: narrow QA manifest grant, copied-gate timeout fixtures, and standing-suite/doc migrations are verified necessary — do not trim as PM padding."
      why: "QA currently holds only notes/expertise grants (team-config.yaml:256-276) so receipt writes need the new grant; copied-gate fixtures follow the FEAT-2274 idiom; migrations are mandated by acceptance send-back criteria and standing synchronous-runner assertions would go red on cutover."
```
