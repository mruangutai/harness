# Receipt — harness-documentor — FEAT-38 T-28 (run t28-t29-product)

**BLUF: done, verify exit code `0`.** DEC-205 rule 2 (executable claims) is deleted, the three
sentences that counted the checks now count one, the DECISIONS-INDEX ruling is hand-repaired, and the
generator is idempotent over that hand-written ruling (second `--stdout` diff empty). No blocking
findings; `must_fix: []`.

## The three repaired sentences, verbatim as they now read

Heading (`.harness/harness/docs/DECISIONS.md`, DEC-205 block line 1):

> `## DEC-205 — This file states current truth: no amendments, supersession is deletion, and one mechanical check guards it`

Enumeration intro (block line 33):

> `**One mechanical check guards this file, and only one.**`

Closing clause (block line 50, end of the "considered and refused" paragraph):

> `the one that is in is the mechanical one.`

The full closing sentence now reads: "Neither becomes cheap merely because the one check above is
open rather than closed — that openness is exactly why the one that is in is the mechanical one."
Em dash with surrounding spaces, the entry's own style, retained. M3 and M4 refusals untouched.

**The closing paragraph was re-wrapped, deliberately.** The clause the verify asserts with `grep -qF`
straddled a physical line break in the original wrap ("...exactly why the / two that are in..."), so
a prose-only substitution would have left the asserted phrase unmatchable. The wrap point moved to
put `the one that is in is the mechanical one` entirely on one line. No other prose changed.

## Item 1 is byte-identical — how established

`git diff -U1` for DECISIONS.md contains exactly four hunks. The hunk covering the enumeration is
`@@ -6264,9 +6264,2 @@`: its only `-` lines are the seven lines of item 2, and item 1's lines appear
as unchanged context with no `+`/`-` inside them. `git diff --numstat` totals `4 11` — 4 insertions
(one heading, one intro, two re-wrapped closing lines) and 11 deletions (the same 4, plus the 7 lines
of item 2). Any touch inside item 1 would have raised both counts. Item 1 keeps its number `1`.

**No numbered item 2 survives:** `grep -cE '^[0-9]+\. '` over the DEC-205 block returns `1`, and the
verify's `^2\. ` clause found nothing.

## Second `--stdout` diff: PASS

`python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - DECISIONS-INDEX.md`
produced no output, exit `0`. The half-generated contract stated in the dispatch holds: the ruling
right of ` :: ` survived regeneration verbatim. New ruling (25 words, inside the 30-word cap asserted
at `.claude/skills/harness/bin/test-gen-decisions-index.py:430-432`):

> `This file states current truth: no amendments, supersession is deletion, deleted numbers are never reused, and one mechanical check — anchor rot — guards it.`

Contains `one mechanical check`; contains no `claim` substring.

## git diff --numstat (both files)

```
57	57	.harness/harness/docs/DECISIONS-INDEX.md
4	11	.harness/harness/docs/DECISIONS.md
```

**The 57/57 is expected and is not scope creep.** The index at HEAD was stale by design — T-27 was
told not to regenerate, so every `@<line>` anchor from DEC-145 down still carried pre-T-27 offsets.
This task owns the only regeneration, so it absorbs T-27's anchor shift as well as its own. All 57
changed rows differ only left of ` :: ` (anchor offsets, plus recomputed tag sets on DEC-145,
DEC-181 and DEC-205); no ruling other than DEC-205's changed. Tag recomputation is a generated-side
effect of shortened entry bodies, not a generator defect, and was not hand-corrected.

## Extra checks run (scoped to my two files)

- `test-gen-decisions-index.py`: all cases `ok`, exit `0`. Named explicitly because the index's
  length and word budgets are asserted only there, never in the index itself.
- Vocabulary sweep for the deleted mechanism across both files
  (`claim:|executable claim|checkable claim|marker whose body|double-colon`): one hit,
  `DECISIONS.md:1790` — "remaining guardrail claim: serialization, the qa gate, and the dirty-tree
  halt", unrelated prose in another entry, coincidental colon. Left alone.
- Count sweep (`two mechanical|two checks|both checks|second check`) across both files: no hits.

## No positive guidance added

The deletion is a deletion. No replacement rule about what an entry does instead of carrying a
checkable claim, and nothing describes the mechanism as superseded.

## Scope note on what the verify does and does not prove

Every clause of the verify is a literal, a count or a placement assertion, and the block was run
against the committed baseline first (exit `1`, "stale check count survives"), so its green is
attributable to this edit. What no clause tests is that the surviving prose still reads coherently
with rule 2 gone — that rests on my reading of the block, reported here.

## Open questions

None blocking. Whether the operator wants any positive replacement guidance in DEC-205 remains
theirs to answer and would only widen this edit; not raised as new.
