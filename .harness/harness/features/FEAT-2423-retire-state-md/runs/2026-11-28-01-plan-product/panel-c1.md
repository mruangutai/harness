# Plan panel fan-in — FEAT-2423, cycle 1

Three readers ran; every finding is transcribed at its reader's own severity, kind and exposure (no PF- ids; record-panel computes identity). No severity was lowered: no finding is contrived + no_worse + non-adversary.
- scope: notes/review-harness-code-reviewer-plan-c1.md (VERDICT FAIL; 3 high substance carry its must_fix: T-01 catalogue/rename witness, T-05 DEC-182 wording ban, T-06/T-07 sweep exit propagation). It found the plan mission proportionate.
- should-not-exist: fable-advisor returned inline (no write grant); one low task-scope proportionality finding, full `why` below. It found the plan right-sized for mission plan (no mission-scope objection).
- design: notes/review-harness-ui-reviewer-plan-c1.md (in scope via org.html; PASS; one med substance finding on T-04).

No `scope: mission` finding exists; no downgrade recommendation.

```yaml
DIGEST:
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: returned FAIL carrying 7 findings; note at notes/review-harness-code-reviewer-plan-c1.md
    - reader: should-not-exist
      status: ran
      persona: fable-advisor
      reason: resolved and returned one finding inline
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: in scope (T-04 org.html); PASS with one finding; note at notes/review-harness-ui-reviewer-plan-c1.md
  findings:
    - reader: scope
      severity: high
      kind: substance
      summary: T-01 breaks the existing catalogue assertion and weakens the rename witness
      exposure: {trigger: routine, vs_today: regression, control: harness}
      why: "Two new retired rows move INV-44 from rows[-6] to rows[-8] in test-check-state-table.py:104-115. Renaming BRIEF away leaves inv_1 silent even when the source path is never counted dirty; test-check-state-table.py:207-210 and feature_record.py:9-19."
    - reader: scope
      severity: high
      kind: substance
      summary: T-05 rejects existing DEC-182 wording its intent does not change
      exposure: {trigger: routine, vs_today: regression, control: harness}
      why: "The planned verifier bans Amended by across DEC-182, which already has three such headings, while the task rewrites only two other fragments. Restrict the whole-entry wording ban to DEC-129 and DEC-150 as required by SC-09."
    - reader: scope
      severity: high
      kind: substance
      summary: T-06/T-07 verification can exit zero with a tracked STATE.md still present
      exposure: {trigger: routine, vs_today: regression, control: harness}
      why: "A failed absence check does not stop the block; the final positive control can exit zero. The listing substitution also conflates a Git error with an empty list. Bind each assertion, cover the final test inventory, and make the expected inventory follow the Q-03 ruling."
    - reader: scope
      severity: med
      kind: substance
      summary: T-05 omits active DEC-180 clauses and incompletely updates DEC-181 and DEC-199
      exposure: {trigger: plausible, vs_today: regression, control: harness}
      why: "The live INV-23 parity and duplicated budget claims survive after one scope is removed; DEC-181 retains its backstop count and DEC-199 would present source-era evidence claims as current despite DEC-257. Amend the narrowed live claims and preserve genuinely dated evidence."
    - reader: scope
      severity: med
      kind: substance
      summary: T-03/T-04 under-specify the digest read at first entry and wake
      exposure: {trigger: plausible, vs_today: regression, control: harness}
      why: "A fresh feature has no accepted digest; a wake can still have a PENDING row and no confirmed artifact. Distinguish absence from no questions, use the confirmed digest and only handed answers paths, and name the digest authority in SPEC sections 10 and 15 as well as 2."
    - reader: scope
      severity: med
      kind: substance
      summary: T-03 runs the wake suite before T-05 changes both files it tests
      exposure: {trigger: plausible, vs_today: regression, control: harness}
      why: "test-lead-stop-and-wake.py binds DECISIONS.md and its index, including DEC-201's lead/end-turn condition. An edit that drops that condition can pass T-05's verify with only a pre-change suite receipt. Move the suite to T-05."
    - reader: scope
      severity: low
      kind: proportionality
      scope: task
      summary: T-02 needlessly rewrites the subject of a historical measurement
      exposure: {trigger: routine, vs_today: regression, control: harness}
      why: "The eeabc59 reproduction in check-domain.py measured a 204-line status file, not feature.json. Retain the normalization rationale and delete obsolete details instead of changing the measured input."
    - reader: should-not-exist
      severity: low
      kind: proportionality
      scope: task
      summary: T-02's new dedicated file tests/unit/test-check-domain-state-retired.py should be cases in the existing check-domain integration suites, not a new pseudo-unit file
      exposure: {trigger: routine, vs_today: no_worse, control: harness}
      why: "House precedent puts retirement-inertness cases inside the existing suite of the subject under test (test-harness-yaml.py:471, test-gen-decisions-index.py:595, test-check-state-shipped.py:282); check-domain fixture machinery already exists in tests/integration/check_domain_support.py and test-check-domain-post.py. A separate permanent file duplicates scaffolding, adds a forever-file every SC-03 sweep must exempt by name, and labels an integration-grade test evidence: unit (SC-06)."
    - reader: design
      severity: med
      kind: substance
      summary: T-04 removes the org reference table's only explicit state and open-question pointer without naming the live records.
      exposure: {trigger: plausible, vs_today: regression, control: harness}
      why: "Applying plan.yaml T-04 literally leaves org.html:305-311 naming PLAN.md and no current location for station or open questions. A reader using the table to resume a feature loses the pointer though the SC-10 absence check passes. The existing rows can name the records from D-01, with an inspection to confirm the mapping (DEC-169)."
  severity_max: high
```
