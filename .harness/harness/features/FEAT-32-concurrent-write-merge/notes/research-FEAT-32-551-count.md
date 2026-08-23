# #551's occurrence count, settled — EIGHT, and T-13 needs the operator's signature

**Answer: EIGHT.** The plan's `seven` is stale, not deliberate. Occurrence 8 was measured in round 4
and recorded only in `STATE.md` and the lead's own run digest; nothing propagated it into `plan.yaml`
or `BRIEF.md`, and no artifact anywhere states a decision to hold the count at seven.

**Verdict on scope: writing `eight` is a CHANGE to the plan, not covered by T-13's intent. The
operator must sign a corrected T-13 intent.** Reasoning below the enumeration.

All claims verified at `b1281df` (worktree HEAD; `plan.yaml` is dirty but its 5-line working diff
touches no `#551` line — `git diff … | grep 551` is empty).

## Enumeration, per occurrence, with evidence grade

| # | Claim | Evidence | Grade |
|---|---|---|---|
| 1 | FEAT-31 pm's 1002-line plan overwritten by a 191-line one in 63s; three product-lead runs closed with pm in flight | operator comment on issue #551, `2026-08-21T14:25:14Z`, quoting transcript timestamps; `BRIEF.md:16-18` | A |
| 2 | An orchestrator recorded an internally impossible line-count pair — the signature of a mid-write read | same comment; `BRIEF.md:19-24` | A |
| 3 | A lead forced to a terminal verdict about a provably mid-run member, four times in one round | same comment ("per that orchestrator") — no artifact pointer | B |
| 4 | FEAT-31's orchestrator inferred two of three run verdicts from disk; `plan2b` was `BLOCKED` where it wrote `PASS` | same comment; not re-derived by me | B |
| 5 | A lead forced to a terminal digest with its pm in flight | `plan.yaml:197`, `BRIEF.md:24-26`, run dir `2026-08-21-1-product` (its `state.yaml` now reads the corrected `complete`/`PASS`, so the force-close itself is not visible there) | B+ |
| 6 | The orchestrator forced to a stop with its lead in flight | plan/BRIEF enumeration + `STATE.md` history; no artifact independent of the affected tier | B |
| 7 | Occurrence 5's cost: a digest asserting pm's work `files_touched: []` and unrecoverable was COMMITTED as the run's outcome; pm was resumed, returned `PASS` | commit **`148c8c5`** "FEAT-32: the run's verdict is ESCALATE with pm PASS, not BLOCKED" — the correction is in git | A |
| 8 | Round 4: the product lead was force-closed by `SubagentStop` with pm in flight, one run after 7, and `validate-digest.py` then **REJECTED** a return that declined to grade the unobservable child — the mechanism does not merely permit a false verdict, it demands one. pm ran to completion as an orphan and returned `PASS` | `runs/2026-08-21-2-product/digest.md`, open question **Q3**, written by the **lead** about itself — an author independent of `STATE.md`; corroborated by `STATE.md` at `6bb7d82` (the orchestrator) | A− |

**Occurrence 8 does not rest on `STATE.md` prose.** Its primary is the lead's digest Q3, which also
proposed "worth adding to D-09" — a recommendation nobody enacted. That digest is on disk only
(`runs/**` is gitignored, `.gitignore:7`) and sits under the round-2 id because of the run-id minting
defect; that is the expected gap, and it does not weaken the record, it only means the pointer is
un-pushable.

**Not an occurrence: the round-5 episode** (would-be 9). Refuted by
`runs/2026-08-21-01-product/state.yaml` — `status: complete`, `verdict: PASS`, `completed_at: seq-2` —
plus its `digest.md` `VERDICT: PASS`. Drafted as 9 twice and retracted both times.

## Why the plan says seven, and why that is staleness

`STATE.md` at `6bb7d82` records occurrence 8 happening **in the same round** whose amend propagated
occurrence **7** into four sites, one of them T-13's intent item 4. Occurrence 8 was therefore
discovered after the sites it would have to change were already written, and was parked as a
non-blocking `Q6` about **appending a comment to the GitHub issue** — not about the plan. Round 5's
amend carried Q1/Q2/Q5/F-1 and never revisited it. `grep -n "occurrence 8\|eight"` over `plan.yaml`
and `BRIEF.md` returns nothing. Rounds 5's two `STATE.md` revisions both reaffirm "occurrences stand
at 8". No artifact argues for seven.

## New versus covered — this is the decision

**Not covered.** Three reasons, in order of weight:

1. T-13's intent does not merely state a total; it **enumerates** 5, 6 and 7 and pins all three to run
   dir `2026-08-21-1-product`. Occurrence 8 is from a different round and a different dir, so the
   amended text must not extend that pin — this is new sentence-level content, not a numeral swap.
2. Occurrence 8's claim is **strictly stronger** than anything in an approved artifact: the validator
   *demands* the false verdict. A documentor writing that would be originating a substantive claim
   about the enforcement layer from a gitignored file, with no approved wording to carry verbatim.
   The rest of T-13's intent is deliberately supplied verbatim precisely to prevent that.
3. The signed `BRIEF.md:16` reads "**#551, seven measured occurrences**". A DECISIONS entry saying
   eight would contradict the signed brief, and DECISIONS.md is the authority.

T-13's `verify:` asserts only that the tokens `harness_merge.py`, `fcntl.flock`,
`inflight_registry` and `#551` are present — **no gate reads the number**. So a documentor writing
either seven or eight passes. The count is governed by the intent alone, which is why leaving it
unsettled routes the decision to the least-informed tier.

## Recommendation

**Ask the operator to sign a corrected T-13 intent.** Cheapest shape that keeps the documentor from
originating anything:

- replace "Record #551's SEVEN measured occurrences as seven, not four" with the eight form;
- supply occurrence 8's sentence **verbatim** in the intent, including its own run dir and the
  "demands, not merely permits" claim, and leave the `2026-08-21-1-product` pin attached to 5/6/7 only.

Cost of not doing it: DECISIONS.md — the authority, with no propagation checker — permanently records
seven while the feature's own record says eight. That is a falsified number left standing, which is
the exact failure the strike discipline (DEC-188) exists for.

## Open question for the operator, not for me to settle

`BRIEF.md:16`'s "seven measured occurrences" is the second-order inconsistency. Amending it resets the
BRIEF approval for prose — the same trade the operator already declined on SC-14. A defensible middle:
amend T-13 only, and accept the BRIEF's line as an as-of-signature statement. That is the operator's
call, and it should be made in the same breath as the T-13 signature rather than discovered at T-13
time.
