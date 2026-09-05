# STATE

## Current

- feature: BUG-1286-test-tree-enforcement
- run: .harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-26-product/state.yaml
- squad: none
- status: awaiting-user

The operator's third ruling, "Match actual discovery", is applied: the guard-covers-discovery
contract is re-based on `code_grade._is_test_path`'s full-relative-path `fnmatch` semantics over
every running kind, REQ-09 keeps its full breadth, F-01 is fixed rather than overruled (normalized
literal prefix, `..` rejected outright), and T-01 case 11 survives repaired with a behavioural half,
a hygiene half and a positive control that selects its subject from the live config. The cycle-7
goal-check found two gaps — a control pinned to today's `detect`, and an undisclosed three-kind
activation blast radius — and both were closed. The cycle-8 panel PASSED at `severity_max: med`,
four findings, nothing high, critical or unrated, so nothing needs operator risk-acceptance.
BRIEF carries 9 REQ and 19 SC over eleven acceptance criteria; plan.yaml carries 6 decisions and 5
tasks at station `plan`. Both approvals remain `pending`. check-state reports one violation for this
feature, the expected unsigned BRIEF.

## Open Questions

- The Advisor consultation the operator directed is answered and recorded in plan.yaml's `panel:`.
  Its three parts: (a) pm's impossibility claim justifying the hygiene half's sufficient-condition
  substitution is FALSE as stated, falsified independently by both readers; (b) the substitution is
  nonetheless SOUND and was forced; (c) one escaping class is named and currently UNDISCLOSED in the
  plan — extension-position wildcard cores of shape `**/test_*.p?` certify guard-covered while
  counting `.harness/test_evil.pw`, an extension the vocabulary refuses nowhere.
- Four panel findings, all `disposition: open`, entering the operator's batched signature review:
  PF-5f9440b904a275b9a85e79ad14696f63 (med) the extension-position escaping class;
  PF-2e5117c5af28b52e4ae49fe9f8a35da0 (med) the guard-covered-bucket non-emptiness clause as a
  live-config occupancy pin; PF-e41c5dbf8071553d1dee17b0fa53c831 (low) and
  PF-e6721a307394caf409dba6ea04b901b0 (low), the overstated impossibility sentence at both sites.
  The panel's own assessment is that all four are fixable in ONE edit to T-01 case 11 plus SC-19.
- The two readers CONTRADICT on the bucket clause; the lead resolved it on evidence grounds in the
  simulating reader's favour and carried both ratings. Third consecutive cycle in which a clause
  pinning the live config's shape was flagged.
- `len(runs)` is 24 against an informational `max_total_runs` of 20. Raising the budget is a user
  decision and has not been made; the value stands at 20.
