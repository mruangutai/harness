# Distillation — harness-ui-reviewer — FEAT-11-graphql-field-resolve

**Result: one `replace` op (P-02 widened). No stale entries found. No displacement needed.**

## Source correction (epistemic honesty note)

The dispatch framed this as "you scoped out of this feature's only review," citing
`review-harness-ui-reviewer-c0.md` as the sole source. Directly listing
`.harness/features/FEAT-11-graphql-field-resolve/notes/` shows **four** UI-reviewer notes, not one:
`review-harness-ui-reviewer-plan-product.md` (Mode A, FAIL — 2 must_fix), `review-harness-ui-reviewer-
plan-contract.md` (Mode A, PASS), `review-harness-ui-reviewer-recheck.md` (Mode A, FAIL then a
closure-check PASS), and `review-harness-ui-reviewer-c0.md` (Mode B, PASS, `in_scope: false`). Three
of the four are full Mode A audits against `DESIGN.md`/`BRIEF.md`/`plan.yaml`, all correctly
self-scoping IN under P-06 (dispatch names the operator-facing stderr diagnostic as the surface).
This does not change my ops — the dispatch's relayed C1 candidate and my distillation instructions
were still usable — but it is itself a live instance of exactly the lesson C1 teaches: a dispatch's
characterization of what happened is a hypothesis, not evidence, checkable by a direct listing. Noted
here, not raised as a blocking open_question — it changed no decision in this distillation and the
feature is closed.

## C1 — accepted, as a `replace` widening P-02, not an `add`

**Candidate:** the dispatch described `DESIGN.md`'s change (two struck `<!-- ok-stale -->` markers)
inside the reviewed range; I ran `git diff` on that file directly and confirmed the description before
declining to report it, rather than taking the dispatch's word.

**Judgment:** durable, and sharper as a widening of P-02 than as a new entry. Old P-02 covered only
*absence* ("design contract expected but not visible — confirm absence directly"). The c0 event and
the plan-product/plan-contract/recheck notes above are the same discipline applied to *presence* and
*content* claims — a contract that IS in the diff, with its change characterized by the dispatch (or,
in the recheck case, by a prior review's narration of what got fixed) — confirmed by direct
`git diff`/`git cat-file` rather than accepted. One rule covers both without lengthening past the
original: "presence, absence, or content... claimed by a dispatch or ambient context." A second
`add` entry restating the same discipline for a different object (presence vs. absence) would be the
distillation smell the skill warns against — same root cause, one rule.

**Rejected alternative:** leaving P-02 unchanged and adding a new P-07. Rejected because the two
situations share one root cause (trust nothing about a contract file's state without a direct object
check at the pin) and the section has no pressure to grow — `merge`/`replace` is available and is the
correct-shaped move per the skill's own guidance on redundant entries.

## Stale-entry check — none found

Walked all six existing Patterns against this feature's four UI-review notes:
- P-01 (census) — exercised in c0, held.
- P-02 — widened, not contradicted (see above).
- P-03 (markdown-in-scope test) — exercised: `DESIGN.md`'s Contract 1/2/3 tables were tested and
  found to specify a real message contract (states, wording, negative constraints), confirming the
  test's premise rather than contradicting it.
- P-04 (CLI-output ruled out unless dispatch names it) — exercised in c0 for `factory_gh.py`'s raised
  `GhError`s (ruled OUT, no dispatch naming); exercised in the other three notes for the *same* kind
  of surface, *named* by the dispatch (ruled IN under P-06). Consistent, not contradictory — the two
  outcomes differ exactly on the condition the pattern names.
- P-05 (dirty tree / pinned SHA) — not stressed this feature (tree was clean per plan-contract's
  "read-only, no writes"); no contradiction, no new evidence either way.
- P-06 (dispatch names an adjacent non-rendered surface) — heavily exercised and explicitly cited by
  name in `review-harness-ui-reviewer-plan-product.md` and `-recheck.md`. Held cleanly across three
  separate applications.

No candidate for `drop`.

## Section counts

| Section | Before | After |
|---|---|---|
| Patterns | 6 | 6 |
| Gotchas | 0 | 0 |
| Outcomes | 1 | 1 |
| Open | 0 | 0 |

`check-expertise.sh .harness/expertise/harness-ui-reviewer.md` → `OK` (one prior failure on word
count for the first P-02 draft, 52 words; trimmed to 43 and re-checked clean).

---

## Round 2 — the three withheld Mode A notes (plan-product, plan-contract, recheck)

**Result: two `add` Patterns (P-07, P-08) and one `add` Gotcha (G-01). No `drop`, no displacement —
sections were nowhere near cap.**

Source discipline for this round: read only the three named notes
(`review-harness-ui-reviewer-plan-product.md`, `-plan-contract.md`, `-recheck.md`); did not re-derive
anything from `-c0.md`, which is closed and already distilled above.

### Candidate 1 (offered) — a contract row with no covering success criterion, as a property of the contract

`plan-product`'s FAIL turned on a real, generalizable defect class: `DESIGN.md` Contract 2's rows had
prose (`what`/`value`/`next_step`) for one failure class but no row, and `BRIEF.md` had no success
criterion, for the sibling failure class (non-diagnosable-envelope). Walking every SC against every
contract row was the method that surfaced it, not a vague "is it checkable" gut check.

**Judgment: accept, as `P-08` (add).** The harness's own Mode A instructions already say "is it
checkable" as a heuristic — that part is not new and doesn't earn a slot. What *is* new and durable
is the concrete procedure that operationalizes it: cross-check every contract row against the full SC
list, row by row, rather than reading the SC section once and asking "does this feel covered." Six
spawns from now, doing that walk explicitly (not just eyeballing) is what would have caught this, and
is exactly the kind of repetition rule 13 says to crystallize.

### Candidate 2 (offered) — the recheck's FAIL→closure cycle: evidence vs assertion

The recheck closed both original must_fix items only after checking the *artifact itself*: hand-
checking the rendered `what` string against the forbidden substring, and reading `plan.yaml`'s query
lines directly rather than trusting the plan's own "PART A step 1 now uses `repositoryOwner`" framing.
Then, in its own closure-check section, it applied the same standard to `BRIEF.md`'s SC-05 rewrite —
verifying the exact clause was gone and the replacement text matched `DESIGN.md`'s footnote, not
accepting that a fix had been "made."

**Judgment: accept, as `G-01` (add).** This is materially different from P-02: P-02 governs claims
made *about* a contract file by a dispatch or ambient context. This governs my *own* prior FAIL and
whether I am willing to convert it to PASS — the object of distrust is the closing narration (mine,
the plan's, or a prior review's), not an external claim about file state. The Gotchas section is
empty and this is exactly the shape of hazard that belongs there: nothing currently stops a future
recheck from accepting "I fixed it" language and marking closed without opening the file.

### Candidate 3 (offered) — byte-consistency across three documents for a pinned/frozen text contract

`plan-contract`'s Mode A audit byte-diffed `what`/`next_step` wording across `DESIGN.md`, `plan.yaml`,
and `factory_gh.py`, and separately flagged that `SC-04`/`SC-10` check only the `value` slot, so wording
drift would pass gates undetected. `plan-product`'s finding 2 (the `user(login:)` vs
`repositoryOwner(login:)` query mismatch between `DESIGN.md`'s stated mechanism and `plan.yaml`'s
literal query text) is the same check applied to a different pinned value — a query shape instead of
prose.

**Judgment: accept, merged into `P-07` (add), not two separate entries.** Both are the same underlying
move — diff a contract's pinned concrete value byte-for-byte against every document/artifact that
claims to implement it, because narrative or intent-level agreement is not literal agreement, and a
success criterion checking one slot can miss the rest. Writing this as two entries (one for "wording,"
one for "query shape") would be the instance-listing smell the skill warns against; one rule covers
both objects. Confirmed distinct from `P-06` (which governs whether a non-rendered surface is in
scope at all, not what to check once it is) and from the existing `P-02`/widened (which governs trust
in a dispatch's claim, not cross-document literal-value drift).

### Rejected

Nothing from the three notes was rejected outright — all three offered candidates survived, though
Candidate 3 was merged rather than kept as two entries, and Candidate 1 was narrowed from the generic
"is it checkable" framing (already covered by the base Mode A instructions) to the specific
row-by-row cross-check procedure, which is what's actually new.

### Stale-entry check, round 2

Re-walked all Patterns/Outcomes against the three notes: no contradiction to any of P-01–P-06 or O-01.
`P-06` was exercised a third and fourth time (once per note) and held without qualification each time.

### Section counts

| Section | Before (this round) | After (this round) |
|---|---|---|
| Patterns | 6 | 8 |
| Gotchas | 0 | 1 |
| Outcomes | 1 | 1 |
| Open | 0 | 0 |

`check-expertise.sh .harness/expertise/harness-ui-reviewer.md` → `OK`, single run, no word-count
violations on P-07/P-08/G-01.
