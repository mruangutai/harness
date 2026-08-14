# Distillation — harness-ui-reviewer — FEAT-20-migration-detector

**Sources read:** both self-notes only (no observations log exists for this agent this feature).
- `notes/review-harness-ui-reviewer-plan-c1.md` — Mode A, plan-time. Rich; primary source.
- `notes/review-harness-ui-reviewer-c0.md` — Mode B, build-time scope-out. Confirms P-01/P-02/O-01,
  contributes nothing new (per lead's filter, independently verified by re-reading it).

## Section fill

| Section | Before | After |
|---|---|---|
| Patterns | 11/15 | 14/15 |
| Gotchas | 1/15 | 2/15 |
| Outcomes | 1/10 | 1/10 (one entry replaced, count unchanged) |
| Open | 0/5 | 0/5 (unchanged) |

## Relayed candidates — all three accepted, source: `relay`

**1. Vacuous truth over an empty quantified set (F-4).** Checked against existing P-08 ("row lacks
an enforcing criterion") for overlap first — different failure class: P-08 is a contract row
nothing tests; this is a quantifier-logic flaw where the verdict computation itself is satisfiable
by an empty collection, independent of whether any test covers the row. Kept separate. Added.

**2. Sibling-document sweep after finding a defect (F-1).** Checked against P-07 ("diff pinned
values byte-for-byte") — P-07 is a proactive consistency scan; this is a reactive move triggered by
a defect already found, checking whether the *same gap* recurs in a sibling spec before scoping the
fix. Different trigger, different action. Kept separate. Added.

**3. House-style verification before filing a completeness gap (F-2).** Checked against P-02
(confirm design-contract presence via `git` object check) — P-02 is about a file's
existence/content; this is about confirming a stylistic convention exists via multiple live
examples before citing its absence as a gap. Different claim type. Kept separate. Added.

## Own-artifact addition — source: `own-artifact`

**Explicit accessibility n/a statement** (from the plan-time note's "Accessibility and theme
parity" section, re-derived by re-reading — not on the relay list). Distinct from P-04 (ruling a
whole diff out of scope): this is about a sub-dimension inside an in-scope review. Added — an
omitted section is ambiguous to a downstream reader (unchecked vs. confirmed inapplicable); stating
it explicitly removes the ambiguity.

**O-01 reformatted** (own-artifact, format-only). O-01 was the only Outcomes entry in the tree not
in WHEN/DO shape (checked orchestrator/product-lead/qa/security-reviewer as reference — all
WHEN/DO). Distillation is the legitimate window to curate the file, so this is in-remit now, not
deferred. Same meaning, reshaped.

## Considered and rejected

**Ranking findings by blast radius** (F-1 > F-4 > F-2 > F-3, plan-time note's "Ranking" section).
Not added. One instance of ordinary review-prioritization judgment, not a distinctive reusable
check — closer to generic reviewing wisdom than a UI-review-specific rule. Declined rather than
manufacture a slot-filler.

## Ops applied — verbatim (durable copy; DIGEST below is the receipt)

```yaml
expertise_update:
  - op: add
    section: Patterns
    entry: "WHEN a contract clause requires a property for 'every' item in a collection DO check
      the zero-cardinality case — vacuous truth over an empty set can make a broken/empty
      collection compute a clean verdict, silently reintroducing the exact defect class the
      contract exists to prevent."
    why: "relay: highest-value finding on this feature, promoted by the receiving lead from
      advisory to blocking; distinct quantifier-logic failure class from P-08's missing-criterion
      check."
  - op: add
    section: Patterns
    entry: "WHEN you find a contract gap in one task or document's wording DO sweep sibling
      tasks/documents that independently restate the same intent for the identical gap before
      scoping a fix — a fix landing in only one instance leaves the other reading the same
      ambiguity."
    why: "relay: reactive sweep after finding a defect, distinct from P-07's proactive
      byte-for-byte diff; prevents a fix that closes the gap in only one of several restatements."
  - op: add
    section: Patterns
    entry: "WHEN filing a completeness/consistency finding that cites an unstated house convention
      DO grep multiple live examples of that convention in the codebase and quote them before
      filing — a consistency finding needs the convention confirmed to exist, not assumed from
      general style expectations."
    why: "relay: verified four live call sites before citing the convention as violated, distinct
      from P-02's file-presence check; avoids filing a finding against a convention that isn't
      actually established in the tree."
  - op: add
    section: Gotchas
    entry: "WHEN a surface under review is batch/CLI text with no colour-only state encoding DO
      state the accessibility and theme-parity sections as explicitly not-applicable with the
      reasoning, rather than omitting them — an omitted section reads as unchecked, not confirmed
      inapplicable."
    why: "own-artifact: re-derived from the plan-time note's explicit n/a statement; removes
      ambiguity for a downstream reader who cannot tell 'skipped' from 'checked and inapplicable'."
  - op: replace
    target: O-01
    section: Outcomes
    entry: "WHEN a scoped-out verdict rests on a measured check (extension census, direct object
      check) rather than a prediction DO record it as such — a scoped-out review that looked holds
      up under cross-review scrutiny; one that merely predicted absence does not."
    why: "own-artifact: format-only fix, same meaning as the prior entry, brought into the WHEN/DO
      shape every other sampled Outcomes entry in the tree already uses."
```
