# Plan panel fan-in — FEAT-2423, cycle 2

Targeted re-panel per operator ruling LEAD-01 (notes/answers-2026-11-28-plan-c1.md). One reader ran; two are recorded skipped with host reasons. Every finding is transcribed at its reader's own severity, kind and exposure (no PF- ids). No severity was lowered: no finding is contrived + no_worse + non-adversary.
- scope: notes/review-harness-code-reviewer-plan-c2.md (VERDICT FAIL; 2 high + 2 med substance). It found the c1 high remedies now discriminate (T-01 rows[-8]/rename witness/INV grep, T-05 Amended-by scope, T-06/T-07 sweep probed red and green) and kept the Plan mission.
- should-not-exist: not dispatched. The c1 rulings narrow scope (org.html deleted not rewritten, two test cases removed) and add no build task (SC-11 rides distillation), so no ruling changes scope materially; the dispatch authorised this reader only on a material scope change.
- design: self-scoped out. Its only c1 surface was org.html, which T-04 now deletes; the plan touches no user-facing surface.

No `scope: mission` finding exists; no downgrade recommendation.

```yaml
DIGEST:
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: returned FAIL carrying 4 findings; note at notes/review-harness-code-reviewer-plan-c2.md
    - reader: should-not-exist
      status: skipped
      persona: fable-advisor
      reason: host skip; c1 rulings narrow scope and add no build task, so no material scope change warrants the reader (dispatch authorised it only on one)
    - reader: design
      status: skipped
      persona: harness-ui-reviewer
      reason: self-scoped out; org.html, its only c1 surface, is deleted in T-04 and no user-facing surface remains
  findings:
    - reader: scope
      severity: high
      kind: substance
      summary: SC-03 and T-07 exempt live executable fixtures despite the operator's Q-06 ruling.
      exposure: {trigger: routine, vs_today: no_worse, control: harness}
      why: "The claims and route tests install and execute the prior-check-domain and prior-check-plan-routes fixtures (test-check-domain-claims.py:19,27-34; test-check-plan-routes.py:1454-1471). Both name the retired file, and the explicit prior-* pathspec excludes both from the terminal sweep (BRIEF.md:36; plan.yaml:795-798). This is active test data, not an archived note."
    - reader: scope
      severity: high
      kind: substance
      summary: The latest non-PENDING run is not necessarily the latest accepted digest (D-01, SC-10).
      exposure: {trigger: plausible, vs_today: regression, control: harness}
      why: "T-04 requires an accepted digest, but the playbook selects the newest non-PENDING row and T-05/D-01/DEC-129 say latest run digest. A refused return is stamped BLOCKED without an accepted digest (feature_record/runs.py:262-264,463-479,577-583; DEC-156), so the selector can hide older accepted questions or read a rejected record. BUG-2169's tracked ledger ends in this state."
    - reader: scope
      severity: med
      kind: substance
      summary: T-02's new SC-06 witness can pass on the wrong denial or miss an indented stale routing line.
      exposure: {trigger: plausible, vs_today: regression, control: harness}
      why: "A handoff missing required sections exits 2 even with its line cap disabled; exit 2 alone does not bind either budget. The hook indents Routing: lines, so a raw startswith filter can miss a second stale line (plan.yaml:488-489; check-domain.py:1600,2305-2335). The feature.json exact-line assertion does distinguish the old routing."
    - reader: scope
      severity: med
      kind: substance
      summary: T-01's numeric-range grep does not implement its range claim.
      exposure: {trigger: plausible, vs_today: regression, control: harness}
      why: "With the exact two retirement rows, adding INV-1..100 still gives exit 0 though it spans both retirees; INV-3..4 raises a false hit though it spans neither (probed against plan.yaml:421). The catalogue assertions independently cover SC-04."
  severity_max: high
```
