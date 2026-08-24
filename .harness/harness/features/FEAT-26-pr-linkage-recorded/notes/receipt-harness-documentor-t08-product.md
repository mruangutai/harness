# Receipt — harness-documentor — T-08 (FEAT-26) — run t08-product

## BLUF
DEC-200 is appended at `.harness/harness/docs/DECISIONS.md:6568` and its index row is
generated at the tail of `DECISIONS-INDEX.md`. T-08's verify passes and prints
`VERIFY-OK`. The DEC-186 scope question is recorded as OPEN with both readings and
neither settled. Nothing committed; the diff is purely additive (57 lines to
`DECISIONS.md`, 1 row to the index, `git diff --stat`).

## Verify — literal output
Run verbatim from the dispatch, cross-checked against `plan.yaml`'s own T-08 `verify:`
(identical, including the ten `DEC-200` occurrences pm corrected from `DEC-197`):

```
ok DEC-200 row and anchor agree
VERIFY-OK
```

## Generator agreement
`gen-decisions-index.py --stdout` matched the committed `DECISIONS-INDEX.md` byte for
byte BEFORE my change (`diff` empty), so no pre-existing drift was absorbed. The row was
appended with a placeholder anchor and the generator run in place; the re-check after
the write is again `IDENTICAL`. Anchor, tags and refs are all generated:
`@6568 [state,github,approval,plan] refs: DEC-138 DEC-153 DEC-186 DEC-196`.

## The row's ruling — exactly 30 words after ` :: `
Counted with `len(r.split())`, at the cap, not under it. Two earlier drafts were 33 and
28 words; the 33-word one was cut, the 28-word one restored "a feature's pull request
number" because a row whose subject is "the number" cannot serve as an open-or-skip filter.

## What the entry rules, and what it deliberately does not
- The rule (ship-time derivation from the recorded branch, exactly-one-merged, never
  overwritten) plus one clause of why for each, per DEC-158. The implementation is not
  restated — no function names, no code.
- **DEC-138's guarantee survives because of the DESTINATION, not the direction.** Stated
  as the ruling, with `gh-sync.py`'s contradicting docstring named as the thing a reader
  hits first, and amendment 6's own words quoted. `gh-sync.py` was NOT edited.
- **DEC-186's bound is recorded as an OPEN QUESTION**, both readings given with their
  in-entry anchors (the bound's "factory tools" grant plus the `**Scope.**` clause on one
  side; amendment 2's rejection of re-categorisation on the other), closing with
  "nothing in this entry turns on the answer". Neither branch is phrased as settled.

## Facts re-derived rather than transcribed
- Eleven `"pr":` insertions across eleven `feature.json` files (`git diff -U0`), and four
  of them (FEAT-01..FEAT-04, numbers 4/4/15/15) share or lack a resolvable branch — which
  is what "four operator-confirmed from the titles" refers to.
- `feat/harness-native-foundation` carrying two merged pull requests (15 and 4) is
  confirmed in `_record_pr`'s docstring and by FEAT-02/FEAT-03 holding those numbers.
- The new invariant is **INV-28** at warn level (`git diff` of `check-state.sh`), gated on
  `github.sync` like INV-21. The plan's intent said "warn following INV-21's reason"; the
  number is INV-28, and the entry says so.
- DEC-153 does keep "merge/PR/deploy user-gated" (`DECISIONS.md:3717` entry body), which
  is the support for "the opening seat is the user's".

## Open questions
- Q1 (blocking, operator's): DEC-186 either widens to a fifth purpose or states the mirror
  is out of its scope. Recorded as open in DEC-200; raised in my DIGEST too.
- Q2 (non-blocking): `gh-sync.py:21-23`'s module docstring asserts the script "never reads
  GitHub state back into harness state", which `record-pr` now contradicts read literally.
  Out of my scope by dispatch; DEC-200 disarms it in prose only.

---

# Cycle 2 — the over-claim is weakened (run t08-product, cycle 2)

## BLUF
The write-only paragraph no longer claims the guarantee was "**always**" about the
destination. It now says the destination test is what governs THIS read, then names
DEC-138 **amendment 7**'s refused read (`DECISIONS.md:4359-4362`) as the case a pure
destination test does not cover, and separates the two on *discovery vs. a fact only
GitHub holds*. Amendment 6's quotation is kept verbatim. Verify prints `VERIFY-OK`;
the generator now agrees byte for byte. Nothing committed.

## I accepted the dispatch's distinction — because amendment 7 states it itself
The distinction is not mine to invent: amendment 7 gives its own reason in the same
sentence that invokes write-only — "idempotency comes from local receipts, so a discovery
path would be a second, contradictory source of truth". That reason does not reach the
merged pull request number:
- `open` **creates or adopts** the parent and records the number at that moment, so a
  GitHub lookup would compete with a receipt already on disk.
- The harness never opens the pull request (DEC-153), so it holds **no receipt** of that
  number. GitHub is the only holder; the recorded branch is the query's *input*, not the
  thing re-derived; and the write is once-only, never overwritten.

So the entry now carries the narrow claim — *this destination **and** no competing local
source* — and explicitly disclaims that write-only was only ever about destinations. The
DEC-186 open question was left untouched and unsettled; I did not widen it, because this
tension has a textual resolution inside DEC-138 and does not need the operator.

## The index row DID change, in both halves
- **Generated half:** the committed row read `[state,github,approval,plan]`; the generator
  emits `[github,state,approval,plan]`. Tag order is derived from the entry's prose, so my
  edit flipped it. Synced to the generator's output — `gen-decisions-index.py --stdout |
  diff -` is now empty (`GENERATOR-AGREES-BYTE-FOR-BYTE`). The `@6568` anchor is unchanged;
  every added line is below the heading.
- **Ruling half:** was inaccurate after the revision — "DEC-138's write-only guarantee is
  about the destination, not the direction" is the same over-claim in miniature. Replaced
  with "DEC-138 write-only holds by destination AND no local receipt". **29 words** after
  ` :: ` (`len(...split())`), one under the 30 cap.

## Verify — literal output, run verbatim from plan.yaml T-08
```
ok DEC-200 row and anchor agree
VERIFY-OK
```

## Open questions carried forward
- Q1 (blocking, operator's) — unchanged: DEC-186 either widens to a fifth purpose or
  declares the mirror out of scope. Still OPEN in the entry.
- Q2 (non-blocking) — unchanged: `gh-sync.py:21-23`'s docstring still asserts the script
  never reads GitHub state back. Out of scope by dispatch.
- Q3 (non-blocking, NEW) — **the DEC-200 heading still carries the universal form** it
  did in cycle 1: "the write-only guarantee is about the DESTINATION, never the
  direction" (`DECISIONS.md:6568`). The body now qualifies that two paragraphs down, so a
  reader who stops at the title takes away the claim amendment 7 falsifies. My dispatch
  scoped me to the paragraph and to nothing else, so I flagged rather than edited; the
  heading is also the anchor every citation and the index row point at.

---

# Cycle 3 — the heading now states the ruling its body carries (run t08-product, cycle 3)

## BLUF
Q3 is closed. One line changed — the DEC-200 heading. It now reads:

```
## DEC-200 — The pull request number is derived at ship time from the recorded branch, and write-only survives on the destination AND on the absence of a competing local receipt
```

The first clause is unchanged (accurate). The second no longer asserts the universal
("about the DESTINATION, never the direction") that the body's amendment-7 paragraph
explicitly disclaims; it states the conjunction the body actually rules. 177 characters,
inside the neighbours' range (DEC-197 119, DEC-198 130, DEC-199 181). No body text
changed — cycle 2's paragraphs are byte-identical.

## The index row did NOT change — in either half
- **Generated half:** `gen-decisions-index.py --stdout | diff - DECISIONS-INDEX.md` is
  **empty** after the heading edit. Tag order held at `[github,state,approval,plan]`, and
  the `@6568` anchor is unchanged because the edit replaced a line rather than adding one.
- **Ruling half:** left **byte-identical**. "DEC-138 write-only holds by destination AND
  no local receipt" is exactly what the new heading now says, so it was already accurate;
  re-counted at **29 words** after ` :: ` (`len(r.split())`), one under the 30 cap.

`GENERATOR-AGREES-BYTE-FOR-BYTE`.

## Verify — literal output, run verbatim from plan.yaml T-08
```
ok DEC-200 row and anchor agree
VERIFY-OK
```
The `@6568` anchor still lands on the heading — the verify's own
`lines[n-1].startswith("## DEC-200 ")` assertion is what proves it, and `grep -n
'^## DEC-200 '` independently returns 6568.

## Scope
`git diff -U0 --stat` for `.harness/harness/docs/`: `DECISIONS-INDEX.md` 1 insertion,
`DECISIONS.md` 70 insertions — the whole entry as one added block, no other file in the
docs tree touched. `plan.yaml`, `gh-sync.py`, `check-state.sh` and every `SKILL.md`
untouched. Nothing committed.

## Open questions carried forward
- Q1 (blocking, operator's) — unchanged and deliberately unsettled: DEC-186 either widens
  to a fifth purpose or declares the mirror out of its scope.
- Q2 (non-blocking) — unchanged: `gh-sync.py:21-23`'s docstring still asserts the script
  never reads GitHub state back into harness state. Out of scope by dispatch.
- Q3 — **CLOSED by this cycle.** The heading no longer contradicts the body.
