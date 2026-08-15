# Distillation — harness-security-reviewer — FEAT-11-graphql-field-resolve

**Source:** no observations log was written this feature (confirmed absent); the sole source is my
run note, `.harness/features/FEAT-11-graphql-field-resolve/notes/review-harness-security-reviewer-c0.md`.

## Candidates relayed by the lead — decisions

**C1 (reachability-closed vs. structurally-closed) — ACCEPTED, as P-07.**
The durable rule is not "`gh` has magic values" (that's the substance, already covered by P-02);
it's a claim-strength rule: when a tool's own value-parsing can't be verified under the review's
constraints, closing on provenance is legitimate only if the closure is labelled reachability-closed
and the exact provenance assumption that would reopen it is named. Deliberately **excluded** the
`-f`/`-F` flag-semantics guess from the entry — that stayed unverified in my run note and in the
lead's own relay, and an Expertise entry is injected every spawn, so putting an unverified flag
mapping there would launder a guess into a repo fact next feature.

**C2 (data-exposure delta, not absence) — ACCEPTED, as P-08.**
"Compare the changed path against the pre-change path, not against zero" generalizes past this
one rewrap to any exposure audit on a modified path — genuinely new to the file. Dropped the
`factory_gh.py:238-249` line anchor and the fixed-string content per the distill skill's rule that
recipes/line numbers rot with the code; kept only the shape of the comparison.

**C3 (scope-in ruling as a lead-consumable finding) — REJECTED.**
My own role prompt's output schema, injected on every spawn, already states: `n/a = scoped OUT;
nothing in this diff for this role to judge. PASS with n/a is legitimate (DEC-173)`. An Expertise
entry restating the info-vs-n/a distinction fails the six-spawns test not because it's wrong but
because I'm already told this every spawn regardless of Expertise — knowing it from Expertise would
change nothing I do differently. No entry added.

## Staleness check — P-01

**Flagged stale, replaced.** P-01 asserted "the only untrusted-input boundary is the hook payload...
the rest of the repo is Markdown." This feature's diff was a `subprocess` argv + GraphQL
query-document construction surface under `bin/factory_*.py` — my own run note called it "a genuine
injection surface" and audited it as such. The old P-01 would misdirect a future audit away from
that surface entirely.

Replacement is deliberately **no stronger than my own evidence supports**: my run note concluded
`fleet.yaml` is hand-authored operator config (trusted), reachability-closing the `-f`/`@filename`
question rather than finding a live vector. So the new P-01 does NOT claim `fleet.yaml` values are
untrusted input — it only names `bin/factory_*.py` as a second surface to audit (argv + GraphQL
document construction from operator-config values, shells to `gh`), without asserting that surface
is currently exploitable. That is the weakest statement the evidence supports (rule 6).

## Section counts — round 1

| Section | Before | After |
|---|---|---|
| Patterns | 6 | 8 |
| Gotchas | 5 | 5 |
| Outcomes | 0 | 0 |
| Open | 0 | 0 |

No displacement needed — neither section was at cap.

## Verification — round 1

- `wc -l` on the pre-write Expertise file: 55 lines, matched the injected copy in context exactly
  (P-01..P-06, G-01..G-05, two empty sections) — confirmed no truncation before read-modify-write.
- `.claude/skills/harness/bin/check-expertise.sh` on the post-write file: `OK`.

---

## Round 2 — missed source: `review-harness-security-reviewer-plan-contract.md`

**Trigger:** the orchestrator's original source list omitted my plan-time review of the same
feature. That note was not swept in round 1. This round: read only that note, judge whether it
holds a durable rule my file (post-round-1: P-01..P-08, G-01..G-05) does not already carry.

**Orchestrator's stated prior:** the note's digest headline — "static query constant, list-form
argv, no token capture — operator-input surface clean by construction" — reads like the same
conclusion my build-time review later reached, one stage earlier, and if that's all it holds,
`expertise_update: []` is correct.

**Finding: the prior undersells the note.** The digest headline is a summary of the *conclusion*,
not the note's full content. Section 1 (query construction) contains a second paragraph the headline
doesn't carry: the plan's `verify:` block reads `factory_gh._FIELD_QUERY` at import time to confirm
the constant's *shape*, and Part B's over-scope guard regexes the *emitted* `query=` value's shape —
but nothing in the plan asserts the emitted value is *equal* to the reviewed constant. My own note
states the consequence directly: "An implementation could technically build a second,
differently-worded string that still passes the shape checks." That is a gap in assertion strength
(shape-match vs. identity-match), not a restatement of the plan-vs-diff conclusion, and no existing
entry names it:

- P-04 is the nearest and is the *opposite* situation — code exists, run the fixture suite instead
  of trusting a static read. Here nothing has been built; the gap is that the *proposed* check
  (a regex) would not prove the thing even once it runs.
- P-05 is adjacent but its action is severity reclassification against an SC's literal wording, not
  a critique of whether an assertion mechanism has the discriminating power the review is crediting
  it with.
- P-07 is adjacent but its trigger is *third-party, unverifiable* value-parsing (a CLI's own flag
  semantics). This gap is the reviewer's own reasoning about an assertion *within the plan*, fully
  inspectable — no provenance-closure move applies.

**Accepted — added as P-09** (Patterns, no displacement, section was 8/15):
"WHEN a review closes a construction-injection question by citing an assertion on the emitted value
DO check whether it proves equality to the reviewed constant, not merely shape or pattern — a regex
a second, differently-worded string also satisfies establishes nothing about identity."

Deliberately dropped the plan-vs-diff framing from the entry text. My first draft read "at plan time
nothing has run, so an unexecuted shape-only check carries less weight than passing evidence" — that
is a weaker, and wrong, generalization: the gap does not depend on the check being unexecuted. A
shape regex that runs and *passes* at build time still admits a differently-worded string; that is
the actual finding in my note. The corrected wording is the weakest statement my evidence supports
(rule 6) and applies equally to a build-time diff review of the same regex, not only to plan review.

**Considered and rejected, this round:**
- Section 2 (`-f`/`-F` flag-parsing reasoning) — same unverified claim already excluded from P-07 in
  round 1. A second note repeating it is not corroboration; neither note executed anything against
  `gh`'s actual parser. Exclusion holds.
- Section 3 (transport re-raise narrows disclosure vs. `run_gh`'s default) — this is a second
  instance of the exact comparison P-08 already generalizes ("compare against the pre-change path,
  not zero"). Citing a second incident inside P-08 is the distillation smell the skill names
  explicitly; the rule already covers it unchanged.
- Section 4 (predictable `/tmp` log paths, same pattern across three feature plans) — covered by
  G-03's family: a re-admitted, already-legal spelling is not a new shape, here a pre-existing
  shared-tmp convention repeated, not a FEAT-11-specific gap. Runner-up to P-09, but one honest add
  beats two thin ones.
- Section 5 (client-side org-board refusal vs. GitHub's own ACL) — same reasoning as round 1's C3:
  this is baseline role knowledge (a UX/message-routing decision is not itself a security boundary
  unless the plan claims otherwise), not a repo-specific fact worth an injected entry.

## Section counts — round 2

| Section | Before (round 1 end) | After |
|---|---|---|
| Patterns | 8 | 9 |
| Gotchas | 5 | 5 |
| Outcomes | 0 | 0 |
| Open | 0 | 0 |

No displacement — Patterns was 8/15, still under cap at 9/15.

## Verification — round 2

- Pre-write `wc -l` on the on-disk Expertise file: 63 lines, matched the SubagentStart-injected copy
  in context exactly (P-01..P-08, G-01..G-05, two empty sections) — confirmed no drift since round 1
  before read-modify-write.
- `.claude/skills/harness/bin/check-expertise.sh .harness/expertise/harness-security-reviewer.md`
  on the post-write file: `OK`.
- Did not touch `harness-documentor.md` or any other member's Expertise file, per the dispatch's
  explicit heads-up that its G-04 violation is a separate, out-of-scope defect.
