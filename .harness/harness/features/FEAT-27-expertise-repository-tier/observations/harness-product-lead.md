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
- 2026-08-19 (goalcheck-product): the dispatch named the qa gate as the thing to verify
  independently, but did NOT say qa had graded a different commit. qa's digest headline (`:6`) and
  every `sc_status` evidence string say `252fa72`; the commit under grade was `9b929de`. That is a
  stronger objection than "same method twice" — two readers at different commits are not measuring
  the same object at all, so an inherited `met` describes a tree nobody is shipping. The habit worth
  keeping: when a dispatch tells me to verify a prior gate independently, grep that gate's own
  artifact for the SHA it graded before dispatching, because the framing "verify it independently"
  quietly presumes both parties looked at one tree.
- 2026-08-19 (goalcheck-product): `SendMessage` is unavailable at the lead tier — I tried to relay
  the commit-mismatch to an in-flight pm and the tool errored as disabled for the session including
  subagents. `runs/qa-final-validator/digest.md:131` records the same absence independently, so this
  is not a one-off. The operational consequence: a lead cannot course-correct a member mid-flight at
  all, so anything discovered after dispatch has to become a written acceptance criterion (P-05) and
  then a fresh dispatch. Writing send-back criteria before the return is not merely good hygiene
  here — it is the ONLY channel a lead has once a spawn is away.
- 2026-08-19 (goalcheck-product): my turn was ended by the stop hook while the member was still in
  flight, and the digest contract still had to be satisfied. The right return was `BLOCKED` with
  `sc_status: []` — the honest value — plus `state.yaml` carrying `dispatched_at` with
  `completed_at: none`, which is exactly the checkpoint-before-dispatch rule paying off: the run is
  recoverable rather than undecidable, and nobody downstream can mistake an ungraded run for a
  passing one. The temptation to fill `sc_status` from qa's eleven was real and would have been the
  worst available act, because it would have laundered a stale measurement into a fresh-looking grade.
- 2026-08-19 (goalcheck-product): the commit-mismatch I could not relay turned out to be moot, and
  the reason is worth keeping. pm hit the same staleness class from a different direction on its
  own: its first SC-03 pass FAILED on `documentor/P-02` because it had built anchors from entry text
  at `ada8e99`, and the craft files had been re-distilled between `ada8e99` and the move commit. It
  rebuilt all thirty-two anchors from `532806c`'s own removed lines. A member that anchors to the
  commit which PERFORMED the change is immune to the staleness I was worrying about upstream of it —
  so when the worry is "which tree was this measured against", the fix to ask for is not a diff
  range, it is "derive your anchors from the change's own commit".
- 2026-08-19 (goalcheck-product): a member's evidence method can be simultaneously the right fix and
  a new blind spot, and the pairing is what to look for at this tier. pm anchored SC-03 on BODY text
  — correct, and the fix for its own earlier anchoring failure — which made it structurally unable
  to see that entry IDs are renumbered in the destination (craft documentor leaves gaps at exactly
  P-02/P-10/G-03/G-04/G-05, while the repository file renumbers them P-01/P-02/G-01/G-02/G-03). I
  found it by reading the destination file directly rather than by re-running pm's check. When a
  member reports fixing an evidence method mid-run, ask what the NEW method cannot distinguish; the
  answer is usually one dimension of the thing it deliberately stopped comparing.
