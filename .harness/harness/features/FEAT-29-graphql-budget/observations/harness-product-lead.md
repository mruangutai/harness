# Observations — harness-product-lead — FEAT-29-graphql-budget

- 2026-08-19: Goal-check dispatch. Routing was unambiguous (goal verification is pm's `consult-when`,
  `team-config.yaml:87`); no second member matched, so no fan-out.

- 2026-08-19: **Four distinct shas across one feature's evidence base.** `measurement-after.md:16`
  = `8c2c24d`; validator panel = `c472a02`; `runs/2026-08-19-10-eng/digest.md:39` records HEAD
  `8c7d7bc`; `feature.json:6` `review_sha` = `4f2e5d0`. The dispatch told me `4f2e5d0` was verified
  equal to the branch tip, which is checkable and probably right — but the *measurements* grading
  SC-01/SC-03/SC-04 were taken two-plus commits earlier, and no artifact I can read bounds what
  moved in between. The simplify run's "zero source bytes" claim covers its own segment only. This
  is the G-07 shape, found by reading run 10's digest rather than the ones the dispatch named.

- 2026-08-19: **Then a FIFTH — `STATE.md:15` pins `review_sha` at `e7104ca`**, "verified equal to the
  branch tip", against `feature.json:6`'s `4f2e5d0`. The validator lead raised this same STATE.md-vs-
  feature.json drift at run 09 (its Q3, "the third run running") and it has drifted again since. The
  durable lesson is not "STATE.md rots" but that **every artifact carrying a sha also carries the
  claim that it equals the branch tip** — so the phrase "verified equal to the tip" is worth exactly
  nothing when read later, and two artifacts can both assert it while disagreeing. A sha claim needs
  the check's date, not the check's conclusion.

- 2026-08-19: **Reading the run dir the dispatch did NOT name is what surfaced it.** The dispatch
  named run 09 (the panel). Run **10** — an eng simplify segment — landed after it and is the reason
  `review_sha` moved past the panel's sha at all. A dispatch that names the evidence set is naming a
  hypothesis about which runs matter, and the newest run is the one most likely to be omitted from
  it, because it did not exist when the framing was written.

- 2026-08-19: G-13 checked and NEGATIVE this time — `runs/2026-08-19-09-validator/` holds exactly
  one `digest.md`, no sibling. Worth recording that the check came back clean, so the habit is not
  read later as always-positive.

- 2026-08-19: **The `SubagentStop` hook forced a digest out of this context while pm was still in
  flight, and the cost of complying is already ON THE RECORD.** `STATE.md:31-33` says three of this
  feature's eleven runs "bought no artifact — two premature lead closes under stop-hook pressure,
  and one duplicate angle". `STATE.md` Q2 and `runs/2026-08-19-10-eng/digest.md:28` (Q4) both name
  it a harness defect: no preloaded rule tells a lead that an in-flight `BLOCKED` is the correct
  response. Mine is the fourth occurrence.
  **What I did about it:** refused to emit a roll-up I did not have, and spent the forced turns on
  assessment prep against files pm was not writing — which is what surfaced the sha findings above.
  A premature close would have discarded pm's in-flight spawn AND filed a verdict with no member
  behind it. pm then returned normally and the run completed as FAIL, so the refusal cost nothing
  and saved a spawn. Leads also hold no `SendMessage`, so I could not fold the sha finding into the
  live dispatch and had to write it to `send-back-criteria.md` instead.

- 2026-08-19: **A cross-squad SC contradiction that was NOT a factual disagreement.** The validator
  lead graded SC-05 `met` at run 09 (after spending a send-back on it); pm graded it `unmet` at run
  11. Both agreed on every fact — the only OFF+failing assertion calls `record()` directly, and no
  test drives OFF + `measured()` + non-zero rc. They differed on whether SC-05's OFF sentence
  inherits the word "wrapped" from its ON sentence. **The tell that it was interpretive, not
  factual, was that neither cited evidence the other lacked.** Worth remembering that a squad
  grading an SC months apart from another squad will produce exactly this, and that the resolution
  is usually to make the ambiguity moot (write the 8-line test) rather than to decide the wording.

- 2026-08-19: **The best finding of the run came from a criterion's ABSENCE clause, not its positive
  clause.** SC-08 required that no surviving document assert `item-list` is cheap. The feature
  corrected the note that caused the incident and left the same rotted 31-point figure standing in
  an approved, shipped brief (`FEAT-11-graphql-field-resolve/BRIEF.md:171-172`). A criterion phrased
  as "no document says X" is the one most likely to be graded from the single file the task named,
  and it is the one where a whole-corpus search actually changes the verdict.

## Run 2026-08-19-12-product — the resume, and the mistake in it

- 2026-08-19: **A member killed mid-run leaves NOTHING on disk.** Run 11's state.yaml recorded pm as
  `in_flight` with the note "artifact lands on disk and is resumable by re-dispatch". That was wrong:
  globbing `notes/*` at resume returned 33 files and no `research-goalcheck-FEAT-29.md`. A member
  writes its artifact at the END of its run. So a lead's in-flight `BLOCKED` preserves the criteria
  and the framing, never the member's partial work, and the re-dispatch is a full re-spend of that
  spawn. State the assumption correctly in the resume note so the next reader does not plan around a
  partial that cannot exist.

- 2026-08-19: **THE MISTAKE OF THIS RUN — I read the live member's artifact mid-write and treated a
  complete-LOOKING document as final.** While pm was still in flight I read
  `notes/research-goalcheck-FEAT-29.md`, found 98 lines ending in a closing `## Open questions`
  section, **re-read the tail to "confirm stability", got a byte-identical result**, and wrote a full
  team digest from it. The artifact was still being revised. pm's actual return graded **8 of 10 met,
  not 7**: SC-05 moved `unmet — unproven` to `met`, and SC-09's evidence changed from the weak "cites
  no cost figure" to the far sharper "`git show 4f2e5d0:CLAUDE.md` carries NO rule at all — the
  deliverable is uncommitted". Two open questions I had never seen appeared.
  **Every structural cue I used was misleading**: a closing section, an unchanged re-read, internal
  consistency, and six citations that all verified at source. A mid-write artifact is not a draft that
  only grows — it can be rewritten in place, so "it looks finished and did not change between two
  reads" is worth nothing. **The only valid signal that a member is done is the member's RETURN.**
  This is the mirror image of the error the operator warned me about: they had been wrong about an
  absence, I was wrong about a presence.

- 2026-08-19: **The waste was not the reading — it was the digest written from it.** Reading pm's
  EVIDENCE BASE while waiting was cheap and paid for itself: it let me verify six citations at source
  and reach SC-05 = `met` by an independent structural route (`gh_cost_log.py:157-159` is
  `yield m; return` with no `finally`, and `record()` re-guards at `:112`, so the untested combination
  cannot fail while the code is correct — corroborated by mutation 3 in
  `receipt-harness-backend-dev-T-03-c3.md:69-83`, where deleting the guard left the write absent and
  reddened only the call-count assertions). pm reached the same verdict by the literal-text route.
  Two independent routes to one verdict is the strongest assessment this tier can produce (P-07).
  The rule to keep is narrow: **while a member is live, read its INPUTS freely, never its OUTPUT.**

- 2026-08-19: **I nearly filed an ABSENCE claim from the wrong document.** SC-08 names "the 2026-08-10
  grilling note". `.harness/notes/` holds **two** notes carrying that date —
  `grilling-board-read-lookups-2026-08-10.md` and `grilling-graphql-cost-2026-08-10.md`. I grepped the
  first, found no `490-506`, no `608` and no condition, and was one step from reporting SC-08's first
  clause unmet. The correction is complete and exemplary in the *second* file (`:14-22`, `:61-65`,
  `:87-95`). G-14 says read the source document before asserting an absence; the sharper form is that
  **a descriptive reference to a document is not an identifier** — disambiguate by TOPIC against the
  directory listing first, because two files sharing a date is enough to make a correctly-executed
  search return a wrong answer.

- 2026-08-19: **The observations log lost writes to a concurrent context.** My resume entries were
  written, then overwritten by another product-lead context's version of this file, which had no way
  to see them. The log is `Write`-not-`Edit`, so appending is read-modify-write and two contexts
  racing means last-writer-wins with silent loss. Re-read immediately before every write to this file,
  and expect to merge rather than append.
