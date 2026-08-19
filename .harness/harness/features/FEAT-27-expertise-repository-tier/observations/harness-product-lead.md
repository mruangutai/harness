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
- 2026-08-19 (t05-q4-product): the way to check "did the member corrupt a field I forbade it to
  touch" without a shell is to grep the field BEFORE dispatch and again after, and compare the LINE
  NUMBERS, not just the values. `status:` sat at 105/171/356/456/584/667 both times, which proves
  additively-appended and no rewrite above the insertion point — a value-only comparison cannot
  distinguish "untouched" from "rewritten identically with shifted content around it".
- 2026-08-19 (t05-q4-product): a verify's NEGATIVE greps are literal and therefore prove almost
  nothing about intent. T-05's forbidden phrases were already absent at the base commit, while
  SPEC §5.6 carried the same falsehood worded as "Project wins on conflict" and passed green. The
  documentor found it only by reading the whole section, not by running the gate. When a task's
  point is "this claim must not survive anywhere", the gate cannot be the assurance — a full read of
  the file is, and it is the member's read that must be commissioned, not the grep.
- 2026-08-19 (t05-q4-product): two members editing disjoint files in one repo produced a shared
  `git status` that each read as partly its own. pm correctly disclaimed three `pending → done`
  flips in its working diff as the orchestrator's pre-existing uncommitted work. A member cannot
  tell an uncommitted third-party change from its own; when dispatching concurrently, say which
  files are the OTHER member's so the disclaimer is cheap rather than a re-derivation.
- 2026-08-19 (specfix-product): the dispatch offered the member an out — "if it concludes the line
  is already correct, change nothing, an empty result is a real outcome". I checked the premise at
  source first (`inject-expertise.sh:100` and `:104` both `cap_body ... 150`; `SPEC.md:963` gives
  150/150/40) and found it foreclosed, so I encoded "already correct is not an available outcome,
  but overturn me with your own evidence if you disagree" (P-06 + O-04). An unqualified escape
  hatch on a premise the lead can settle in two Reads buys a member spawn that may return nothing.
- 2026-08-19 (specfix-product): before judging a sweep's COMPLETENESS I have to have read the
  surface myself (G-14) — a member's "I found N" is unfalsifiable otherwise. My own read of
  `SPEC.md` found §5.2 (`:807-825`) already correct and consistent (two *kinds*, craft/repository,
  150/40, precedence by specificity), and flagged `:2260` — "Expertise caps are *entry counts*, not
  token counts" — as the one remaining budget claim in the file whose relationship to the enforced
  LINE caps is questionable. Doing that read before the return arrives is what makes the assessment
  a check rather than a restatement.
