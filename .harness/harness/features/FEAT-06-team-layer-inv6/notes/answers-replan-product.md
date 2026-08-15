# User answers — FEAT-06 re-plan gate, run `replan-product` — 2026-08-04

Taken by the main session from the user directly. Three questions answered. One overrides the
orchestrator's recommendation.

## D-08 (Q8, BLOCKING) — pm's recommendation ACCEPTED. QA runs in BOTH places.

The user chose **"two jobs, one persona"** as pm framed it:

- an **orchestrator-sequenced qa SEGMENT** during the build that writes and runs the tests
  (`SPEC.md:1978`, T-11), and
- a **gate-only qa PANEL step** that re-runs the matrix over the pinned SHA and authors nothing
  (`SPEC.md:1980`, issue #8, T-02).

The argument that settled it, reproduced so pm does not re-derive it: standalone review is a real
dispatch path, nothing else runs the matrix on it, and the build-only alternative therefore closes
#24's hole while opening the identical one in the standalone path.

**Cost accepted explicitly:** qa is spawned twice in a full ship.

**THE PLAN DOES NOT SHIFT.** This is the recommended branch, so the flip-delta is not taken:
T-02, SC-04, T-07(1) and T-08 stand exactly as written. Do not apply the alternative.

## Q10 (budget) — RAISED to $160. +$40 authorised.

`max_cost_usd` moves from 120 to **160**. Update `feature.yaml`.

The user's reasoning: the exposure named in the return is the review-and-loop-back tail, and that
tail is what took every prior feature past its signed number (1.2x, 3.0x, 2.7x, 2.0x). The raise
makes the overrun authorised rather than merely reported — DEC-134 means cost never stops work, so
an unraised budget would just have produced the same spend with a worse record of it.

Carry the honest accounting forward: 44.81 measured plus the never-measured segment-1 band, i.e.
**57–90 of 160**, not pm's stale 31–64.

## Q9 (eng architecture review) — USER OVERRODE THE RECOMMENDATION. Run the FULL review, BEFORE signature.

The orchestrator recommended a scoped delta after signature, estimated 10–19. **The user chose a
full architecture review of the rewritten PLAN, run before they sign.**

The staleness objection the recommendation rested on does not apply: D-08 came back as the
recommended branch, so the PLAN does not shift underneath the reviewer. The reason a delta was
cheaper was that a full review might be invalidated by a flip — and there is no flip.

Standing instruction: **the user signs a plan an architect has already passed end to end.** The
first PLAN's review returned six blocking findings; this one is a rewrite of that plan and has had
no architecture review at all.

Scope it as a real review, not a delta: the re-scope and its D-NN decisions, the 15 SCs, retired
T-03, added T-10/T-11, the qa two-places shape now that D-08 is settled, and confirmation the six
EMF remedies were applied as eng-lead specified.

## Two text defects — pm's to fix, NOT the main session's

Both verified at source by the main session. The main session's write grant is
`team-config.yaml:18` — the `## Approval` blocks only, not the prose — so these are routed here
rather than hand-edited:

1. **`BRIEF.md:11`** says "**Five** things in the harness are a definition or a check that appears
   to exist but does nothing" above **six** numbered rows (`grep -c '^[0-9]\. '` returns 6, and row
   6 is the two team files failing `yaml.safe_load`). Either the count becomes six or row 6 is
   folded into another row — pm's call, but the file must not ship self-contradicting on its own
   opening claim, which is this feature's whole subject.
2. **`PLAN.md:687`** says the flip-delta touches "T-02, SC-04 and T-07(1) **only**" — it also
   touches T-08, as `PLAN.md:173` and T-08's own intent block both state. Now that D-08 is settled
   on the recommended branch the flip-delta is moot in practice, but the sentence is wrong on the
   record and the orchestrator already verified the correction.

## Verified independently by the main session (do not re-derive)

- **SC-14 is falsifiable and currently red.** `grep -c -i 'test_matrix' .claude/skills/harness/SKILL.md`
  returns **0** at `635ef14`, as does `qa`. This is the criterion `review.yaml` alone cannot
  satisfy, and it is what makes the #24 fix assertable rather than assumed.
- **The 15 SCs are present** (SC-01 through SC-15, confirmed by id sweep) and `closes_issues` reads
  `#8 #9 #16 #24`.
