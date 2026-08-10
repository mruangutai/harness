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
- P-04: WHEN a defect class is named anywhere in a feature — by a member or by you — DO sweep the
  surface for further instances before closing the next gate on it; your own earlier finding is
  the one nobody thinks to re-sweep.
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
- G-04: WHEN your own finding names N instances DO run the discriminating test on each one
  separately — a vacuity claim is a substring claim, and reading the first message then
  generalising to its siblings produces a remedy that is half unwarranted.
- G-05: WHEN relaying a member's own prior work into its distillation DO list its notes directory
  yourself rather than trusting the dispatch's account of how many times it ran — a missed run is
  a lesson lost permanently, since Expertise is written once per feature.
- G-06: WHEN a member's role field carries a placeholder you would not have chosen DO check the
  digest validator's per-persona table before recording a convention mismatch — a scoped-out
  reviewer's `n/a` is the sanctioned spelling there, not drift.

## Outcomes (max 10)
- O-01: WHEN dispatching a review panel DO name the already-ruled items in the prompt —
  pre-briefing suppressed every re-discovery without suppressing new probing, so it buys back
  reviewer attention at no cost to independence.
- O-02: WHEN judging relay quality DO require each member to record rejections with reasons — a
  member rejecting a candidate as already covered by a preloaded rule is filtering, and a round
  with zero rejections anywhere is the signal to distrust.

## Open (max 5)
