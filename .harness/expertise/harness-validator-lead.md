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
- P-05: WHEN relaying candidates into a member's distillation DO carry only cross-member and
  lead-tier findings — a member independently derives everything its own note already holds
  before it reads the relay, so recalling that back contributes nothing and wastes half the
  relay.
- P-06: WHEN two reviewers each return PASS on adjacent mechanisms DO check each one's mechanism
  against the criteria the other verified — the gating defect lives in the union of the scopes,
  and no member is positioned to call it from inside its own lens.
- P-07: WHEN dispatching a review panel DO hand the file set down explicitly rather than let each
  reviewer self-scope — self-chosen scopes leave the seams between them uncovered, and the seam
  is where the gating defect sits.

## Gotchas (max 15)
- G-01: WHEN the blocking gate passes and an advisory gate carries the only defect DO headline
  both — which gate blocks says nothing about which gate finds things, and a digest headed by the
  passing gate reads one tier up as clearance.
- G-02: WHEN recording a run metric or a verified fact DO put it in the digest and a one-line step
  note — the run state's top-level allowlist is closed and rejects an invented key even when its
  value is a bare integer, not prose.
- G-03: WHEN every gate returns green DO establish which routes actually reach each gate and
  whether each fixture can fail — logic can be correct while reachability is wrong, and neither
  is visible to anyone reading the gate's own code.

## Outcomes (max 10)

## Open (max 5)
- OQ-01: WHEN judging relay quality DO record each member's accept/reject split, not merely that
  ops came back — a member accepting every relayed candidate and a member rejecting one with a
  stated reason are not yet distinguishable as good relay versus weak filtering.
