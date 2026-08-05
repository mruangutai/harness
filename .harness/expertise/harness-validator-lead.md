# Expertise — harness-validator-lead

## Patterns (max 15)
- P-01: WHEN promoting a member's cited anchor into your digest DO open the file and confirm the
  line yourself — anchors drift by a line or two even in honest reports, and yours is the tier
  where a citation becomes a measurement two tiers up.
- P-02: WHEN ranking advisory findings for a backlog DO order by irreversibility before
  severity — a low-severity defect whose failure cannot be undone outranks a medium that is
  cheaply reversible, and no member can see that axis from inside its own lens.
- P-03: WHEN a coverage gate returns green DO establish how many of the changed units it actually
  bound before reporting it as assurance — a gate can be correct and near-vacuous at once, and
  "the gate is satisfied" is not the claim "the change is tested".
- P-04: WHEN a member reports one stale anchor or one duplicated statement DO grep for the whole
  class before ranking it — one grep decides whether you hold a single bounded line or a systemic
  defect, and that changes the fix cost, not just the severity.

## Gotchas (max 15)
- G-01: WHEN the blocking gate passes and an advisory gate carries the only defect DO headline
  both — which gate blocks says nothing about which gate finds things, and a digest headed by the
  passing gate reads one tier up as clearance.
- G-02: WHEN recording a run metric or a verified fact DO put it in the digest and a one-line step
  note — the run state's top-level allowlist is closed and rejects an invented key even when its
  value is a bare integer, not prose.

## Outcomes (max 10)

## Open (max 5)
- OQ-01: WHEN reporting relay calibration DO split accepted entries by source and report the
  member's own-material share — a member with no observations log can accept most relays honestly
  while every entry in its file still traces to the lead, which an acceptance rate alone hides.
