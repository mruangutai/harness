# Receipt — T-05 — delete six struck entries, repoint their in-docs citations

**PASS.** The six entries are deleted, all nine amendments went with them, every in-docs citation is
repointed as a rewrite rather than an id swap, and DEC-90 is untouched. Verify block: **baseline exit
`1`** (first assertion, `kept DEC-103`), **final exit `0`**.

## The six deletions

Each cut exactly heading-through-(next-heading minus 1), which reproduces the local seam shape
because the trailing rule and blank belong to the deleted span.

| Entry | Cut | Seam left behind |
|---|---|---|
| DEC-103 + DEC-104 | one cut, 1605–1627 | no `---` at these seams; text/blank/heading, as before |
| DEC-137 | 3129–3207 (incl. its own amendment) | `---`-carrying seam preserved |
| DEC-186 | 5660–5826 (incl. three sub-sections) | normalised a stray double blank to one |
| DEC-192 | 6089–6140 | text/blank/heading |
| DEC-196 | 6495–6734 (incl. four bold-inline amendments) | text/blank/heading |

**A seam-shape assumption in the intent did not hold.** Only ~50 of ~200 inter-entry boundaries carry
a `---`; DEC-103/104 had none. Anchoring on content and cutting to next-heading-minus-1 handled both
shapes without a special case.

### The DEC-137/DEC-138 seam, verbatim

A block was removed from inside DEC-138's span, so this boundary is quoted as required
(`DECISIONS.md:3103-3108`):

```
two historical sentences.

---

## DEC-138 — GitHub Issues integration: asymmetric truth, orchestrator-executed, full loop (task 24)
```

Identical to DEC-136's own head seam, the shape every `---`-carrying boundary has. The second seam,
where `### DEC-137 amendment 2` was cut from inside DEC-138, is the same shape at
`DECISIONS.md:3196-3201`.

## The nine amendments, enumerated

| # | Amendment | Belonged to | Where it physically sat |
|---|---|---|---|
| 1 | `### DEC-137 amendment — authorship is enforced by glob, and the refresh respects it` | DEC-137 | inside DEC-137's span |
| 2 | `### DEC-137 amendment 2 — the human view: map.html, derived and never authored` | DEC-137 | **inside DEC-138's span** (orig. 3299–3312) — found there, removed there, in a separate cut from DEC-137's own span |
| 3 | `### DEC-186 amendment 1 (2026-08-12) — one board per repository served…` | DEC-186 | inside DEC-186's span |
| 4 | `### DEC-186 amendment 2 (2026-08-23) — the read-back bound widens to FOUR…` | DEC-186 | inside DEC-186's span |
| 5 | `### DEC-186 amendment 3 (2026-08-23) — the read-back bound widens to FIVE…` | DEC-186 | inside DEC-186's span |
| 6 | `**Amendment 1 (2026-08-18) — the harness's own board now declares its stations**` | DEC-196 | inside DEC-196's span |
| 7 | `**Amendment 2 (2026-08-18) — the heading's third clause is struck**` | DEC-196 | inside DEC-196's span |
| 8 | `**Amendment 3 (2026-08-23) — the `plan` station is declared…**` | DEC-196 | inside DEC-196's span |
| 9 | `**Amendment 4 (2026-08-23) — the station lifecycle is event driven…**` | DEC-196 | inside DEC-196's span |

None folded. Sweep for all nine heading forms returns empty (rc=1).

## Per-id account: where each id's citations went

**More than half the hits self-resolved.** Of ~60 grep hits, 20 sat outside every deleted span and
needed rewriting; the rest were inside one of the six (DEC-196's span alone held six citations of
DEC-186 and DEC-192). Spans were computed first, then each hit classified.

### DEC-103 → rule stated directly, no citation
Three live sites, all citing it as the founding case of the propagation defect. DEC-188 is the named
successor but it *is* the entry doing the striking — citing it for its own predecessor's content
would be circular — so each names the thing instead of the number:
- `DEC-188` body: "the propagation checker and the invariant that enforced it are struck"; "the
  checker was built in the first place because…".
- `DEC-109`: "the propagation checker's own founding case".
- `DEC-111`: "the checker's founding case".

### DEC-104 → rule stated directly, no citation
- `DEC-111`: "the marker registry's own fence fix" — a faithful paraphrase of the id, asserting
  nothing the sentence did not already assert.
- `SPEC.md:45`: "That ruling came from an entry since struck under DEC-188 on unrelated grounds."
- **No content lost.** INV-10's number retirement, which only DEC-104 recorded in docs, is carried
  authoritatively in code at `check-state.sh:1785-1789` ("Do NOT reuse \"INV-10\"").

### DEC-137 → rule stated directly, no citation. **The plan's successor does not carry the claim.**
The plan named DEC-162, "whose glossary half carries it". It carries the *glossary*, not the map-tier
removal — DEC-162 still describes the map as **live** (`.harness/codebase/glossary.md` at
`DECISIONS.md:4131`, "a mapped codebase" at `:4139`, "the codebase map" at `:4151`, `:4158`, `:4162`).
Citing it would have pointed three sentences at an entry that contradicts them. Per the lead's
amplification 1, the rule is stated with no citation:
- `DEC-145` MOOTED note: "removed when the codebase map tier itself was removed".
- `DEC-149` am. 1: "the map tier was removed after 35 features never built one".
- `DEC-158` am. 1: "with the codebase map tier, itself removed after 35 features never built a map".
- `BUILD.md:204` (row 17): the row named a retired task as its "first act" — now "**The map step this
  row used to name is gone** — task 23 is retired".
- `BUILD.md:208` (row 23): cites **DEC-188** for the striking (which DEC-188 genuinely carries) and
  preserves the surviving fact: "The glossary survived at `.harness/glossary.md`."

### DEC-186 → successor DEC-203 cited where it carries the claim
DEC-203 item 5 genuinely carries the read-back bound forward at seven purposes and keeps the
approval-block ban, so it is cited by substance. Inside DEC-203's own body the ids became descriptions
("the superseded bound"), because an entry cannot cite entries deleted in the same act:
- `DEC-203` §5 / §"fourth purpose": the precedent for widening by naming a second caller now points at
  **the fifth purpose in its own list**, verified to bound its read to `record-pr` and `ship`.
- `DEC-203`: "one board **per repository served**" — rule stated directly, citation dropped.
- `DEC-200`: rewritten to "**DEC-203 carries it as the fifth of seven named purposes**", quoting the
  purpose, and keeping the two-readings history without dangling ids.
- `DEC-203` lineage: "DEC-200, which cites the superseded read-back bound".

### DEC-192 → successor DEC-203 cited
DEC-203 item 6 carries the single `status` field, its six case-sensitive values, the absent `blocked`
and both collapses — verified before citing.
- `SPEC.md:1875`: "**There is NO `phase` field…** (DEC-203 item 6)".
- `DEC-203` §6: "carried forward unchanged in substance".

### DEC-196 → successor DEC-203 cited; one falsified claim corrected
- `DEC-203`: "Replaces three earlier entries, struck under DEC-188… and since deleted from this
  record"; "reverses the superseded station table"; "the superseded created-versus-adopted gate".
- `DEC-138` am. 8: "That reasoning belonged to the superseded station-lifecycle amendment".
- **`DEC-200:6960` was not merely dangling — it was false.** It read "no source ticket is ever closed
  by the harness, per DEC-196". DEC-203 reverses exactly that: it moves every recorded card,
  `source_issues` included, to `Done` at ship, and GitHub closes it. Rewritten to state the current
  behaviour and cite DEC-203.
- **A wordless dangling pointer, invisible to any id grep:** `DEC-138` am. 8 read "Every other row of
  amendment 4's table", pointing at a table deleted with DEC-196. Repointed to the live recorded copy,
  `.claude/skills/harness/references/github-mirror.md` §"Who writes each station — one writer per
  column" (heading verified to exist).

## Content that leaves the live tree (recorded so it is not lost)

DEC-203, DEC-188 and `github-mirror.md` carry the rules forward, but three items had no live home and
survive only in history at `git show 7ebfc9e:.harness/harness/docs/DECISIONS.md`:
- **DEC-186's `D-12`** — the two named duplications (two independent issue writers sharing one
  T-NN map; `feature.yaml` as a local idempotence key) recorded as work a later increment owns.
- **DEC-186's claim-as-git-ref rationale** and its stated residual risk (serialisation of concurrent
  ref creates is inferred, never measured). The mechanism itself is live in `factory_claim.py`.
- **DEC-137's "number is retired, not reused"** note. No live citation of DEC-137 now remains, so
  nothing depends on it.

## Verification

- Verify block, cross-checked against `plan.yaml`'s own `verify:` for T-05 (identical): **baseline
  `1`, final `0`**.
- Generator exits **1** with **exactly seven ORPHAN lines and no other stderr** — the six ids plus
  DEC-140 (T-04's, permitted). `DECISIONS-INDEX.md` never touched and absent from `git status`.
- `## DEC-90 — STRUCK 2026-08-21` present with its strike record; the string `DEC-90` does not appear
  anywhere in my diff.
- Dangling-citation sweep across all three files: only `DEC-161`, pre-existing in DEC-188's narrative
  ("the natural host, DEC-161, had already been deleted") where naming a deleted entry is the point.
- Modified: the three doc files only. `STATE.md` and `plan.yaml` were already modified at spawn and I
  did not touch them. HEAD unmoved at `57a3bf3`; nothing committed. MAIN checkout
  `git status --porcelain --untracked-files=no` empty.

## Open questions

- **Q1 (non-blocking).** DEC-162 describes the codebase map tier as live in five places
  (`DECISIONS.md:4131,4139,4151,4158,4162`) although the tier was removed. DEC-137's strike record
  flagged this as "with the map precondition dropped", and that record is now gone. Out of T-05's
  scope — DEC-162 is not one of the six and is a dated record — but it is now the only place in
  DECISIONS.md that describes the map as current, so a reader meeting it first is misled.
