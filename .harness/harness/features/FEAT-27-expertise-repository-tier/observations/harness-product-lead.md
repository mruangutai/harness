# Observations — harness-product-lead — FEAT-27-expertise-repository-tier

- 2026-08-19: E1 judgment segment. I handed pm a *proposed* ruling on gap (a) (split: committed at
  REQ-05, un-operationalized at SC-06) and told it to test that reading rather than inherit it. It
  confirmed the split but on a stronger anchor than mine: T-02 intent 1b (`plan.yaml:240-241`) offers
  "nullglob semantics **or** an `[ -r "$f" ]` guard" as equally conforming, and `nullglob` gives zero
  unreadable-file protection — so a conforming implementation could lack the property entirely. My
  footing was SC-06's scoping clause, which is disputable prose; pm's is a disjunction in the signed
  plan, which is structural. Adopted pm's route as the record (P-07). The lesson: when I pre-argue a
  ruling, the instruction "test this against the source, do not inherit it" is what buys the better
  anchor — a deferential member would have returned my own reasoning back to me.
- 2026-08-19: the `[ -r ]` guard is double-covered for its *specified* duty and uncovered for its
  *unspecified* one. `inject-expertise.sh:75-77`'s segment filter independently rejects an unexpanded
  glob word (it carries a literal `*`), which is why qa's guard-removal mutant survived all 18 cases.
  The comment at `:63-65` states the guard exists for the non-matching-glob case — i.e. the code's own
  comment describes only the duty that is redundant, and is silent on the one that is load-bearing.
  A guard whose stated rationale is the covered half is a shape worth recognising: mutation survival
  there means "masked by a sibling guard", not "dead code".
- 2026-08-19: dispatch-guard blocked my first spawn because I passed `model: opus` — model pins are
  org design (DEC-152/155) and a lead may never pass one, even to a member whose own frontmatter
  carries that model. Cost one blocked call, no spawn. Re-dispatched identically without the
  parameter and it ran. Never put `model:` in an Agent call from this tier.
- 2026-08-19: "delaying the ship" was a null cost in this escalation and I corrected it in the
  dispatch before pm reasoned from it. T-01/T-04/T-05/T-06 were unbuilt (`plan.yaml`, three
  `main-session-direct` and pending with the operator), so the feature could not ship regardless, and
  BOTH options — author T-07, or backlog — required an operator signature. The real variable was
  *when* the signature is asked for, not *whether*. Check what actually gates the ship before letting
  a member cost out "now vs later"; an inherited cost frame produces a confidently wrong trade-off.
