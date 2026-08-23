# Title backfill report — board 3, mruangutai/harness

Date: 2026-08-23. Board **3**. Run by the operator's hand, main-session direct.

## Outcome

```
renamed: 218; already correct: 0; refused: 0; points spent (approx): 436
```

Exit 0. **Zero errors, zero refusals** across 218 live renames. Every ticket carried a milestone
naming a real feature, so #782's gap did not fire.

## The format, and why byte-identity mattered

Titles now read `<feature-id> — <T-NN> — <title>`, spot-checked live rather than inferred:

```
#26   FEAT-06-team-layer-inv6 — T-01 — Close INV-6's truthy hole and give the placeholder vocabulary one home
#28   FEAT-06-team-layer-inv6 — T-04 — Write `build.yaml` — the eng-squad build team, born valid
#777  FEAT-33-board-lifecycle-native — T-22 — Widen INV-26 to accept a done task whose sub-issue is deliberately still open
```

T-16 changed the title `gh-sync.py open` writes. A backfill differing by one character would have
left two writers in permanent disagreement about the same ticket. T-17 proved them identical by
extracting both f-string bodies and comparing character by character, **including the em-dash byte**
— both U+2014. The live titles above carry that same U+2014.

## Idempotence, measured on live data

A second `retitle` preview after the apply:

```
renamed: 0; already correct: 0; refused: 0; 0 to rename; projected cost 0 GraphQL points
```

**Note what that says and does not say.** `already correct: 0`, not 218 — the renamed titles are
excluded by the *selection regex* before the "already correct" check is reached, because a real
feature id never starts with `T-\d+`. T-17 said exactly this in its receipt rather than presenting
the skip as a live guard, and the live run confirms it. **The re-run is safe; the mechanism is the
regex, not the skip.**

## Derivation checked independently

Each id comes from the ticket's own milestone. Three checked against GitHub directly rather than
trusted from the preview:

| issue | milestone | derived id |
|---|---|---|
| #28 | `FEAT-06-team-layer-inv6` | matches |
| #777 | `FEAT-33-board-lifecycle-native` | matches |
| #772 | `FEAT-33-board-lifecycle-native` | matches |

## One correction to my own reading of the preview

I grepped the preview for refusals and got 8 hits. They were the words *"refuse"* and *"refusal"*
**inside the ticket titles** — #708 "Cut dispatch-guard.sh over to refuse…", #620 "Refuse a governed
agent…". The summary's `refused: 0` was accurate and my matcher was the wrong shape.

That is the same defect this feature has found nine times in other places: a matcher that cannot
distinguish the thing it seeks from prose mentioning it. Recorded because it was mine.

## Cost

436 GraphQL points, 2 per rename, matching T-17's projection of the same figure.
