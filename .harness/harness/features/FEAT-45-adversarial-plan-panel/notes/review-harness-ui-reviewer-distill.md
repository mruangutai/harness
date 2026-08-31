# UI Reviewer — feature-close distillation — FEAT-45-adversarial-plan-panel

Source material: my own six review artifacts (`review-harness-ui-reviewer-plan-c0.md`,
`review-harness-ui-reviewer-c0.md` through `-c4.md`) plus `handoff-validate.md` and
`ship-review-2026-08-31.md` for cross-cutting context. No observations log existed for this role
this feature (none was written) — the review notes themselves are the material, per dispatch.

## Applied — craft tier (`.harness/expertise/harness-ui-reviewer.md`)

Section counts, before → after:

| Section | Before | After |
|---|---|---|
| Patterns | 15/15 | 15/15 (unchanged) |
| Gotchas | 12/15 | 15/15 |
| Outcomes | 5/10 | 5/10 (unchanged) |
| Open | 0/5 | 0/5 (unchanged) |

Ops applied via `expertise-merge.py apply` (tool output: `ADDED G-13`, `ADDED G-14`, `ADDED G-15`,
all prior ids `PRESERVED`):

```yaml
expertise_update:
  - op: add
    section: Gotchas
    entry: "G-13: WHEN auditing an operator-facing block, error, or withhold message DO check it
      names the concrete remedy action, not only the triggering fact — a message stating only the
      fact is the most common completeness gap in text-only interfaces and tends to persist
      unfixed across many review cycles."
    why: "Derived from my own Mode A/B notes across this feature: the withhold-message gap (F1/M7)
      was filed at c0 (Mode A and Mode B) and reconfirmed unchanged, unfixed, at c1 and c2 — five
      independent measurements of the same completeness-gap shape with no prior Expertise entry
      naming it."
  - op: add
    section: Gotchas
    entry: "G-14: WHEN asserting a negative claim about text output (e.g. \"no truncation
      exists\") DO enumerate the concrete idioms that would produce it and grep each explicitly
      across every file on the path, then report the searched set — an unsupported \"not
      observed\" is not a measured absence."
    why: "Derived from c4: established the truncation-absence claim by grepping eight named
      idioms ([:N], cut -c, .ljust(, .rjust(, .center(, textwrap, ellipsis, ...) across every file
      on the id's path and reporting zero hits, rather than asserting absence from a read-through.
      Generalizes beyond truncation to any negative-existence claim over text output."
  - op: add
    section: Gotchas
    entry: "G-15: WHEN a dispatch's pinned commit hash does not resolve DO check whether a shorter
      unique prefix of it resolves to the expected commit message and position before halting —
      treat a mistyped-but-recoverable pin as the intended object and flag the mismatch as a
      non-blocking open question."
    why: "Derived from c1: the dispatch's 40-char pin did not resolve; its 7-char prefix resolved
      uniquely to the expected commit (message and position matched). Treated as a typo, review
      proceeded, mismatch flagged non-blocking. A durable procedural check for any git-pinned
      review dispatch."
```

## Repository tier (`.harness/harness/expertise/harness-ui-reviewer.md`) — no-op

`Patterns` 1/1, `Gotchas` 0/0, `Outcomes` 0/0, `Open` 0/0 — **unchanged.** This feature's Mode B
census re-confirmed, five separate cycles, the exact repo-wide invariant the existing P-01 already
states (zero rendered-UI-extension hits every time; no `DESIGN.md` for a doctrine-only feature). No
new repo-specific path, file, decision, or invariant surfaced that P-01 does not already cover, so
nothing was added or edited.

## Judged candidates

### Relayed (a) — plan-c0's two Mode A findings (message-states-fact, SC-11 pass/fail gap)
**Split, judged separately:**
- The SC-11 pass/fail-line gap → **REJECTED as duplicate.** Already fully captured by existing
  `P-08` ("a row with correct prose but no enforcing criterion is invisible to gates and is the
  highest-value Mode A finding") — that entry was very likely distilled from this exact finding
  shape already; adding a second entry would be a story, not a sharper rule.
- The block-message-states-fact-not-remedy gap → **ACCEPTED**, added as `G-13`. Not previously
  captured, and independently reconfirmed unfixed across four more cycles this same feature —
  strong evidence of durability.

### Relayed (b) — c4's truncation-absence-by-enumeration methodology
**ACCEPTED**, added as `G-14`. No existing entry captured "prove a negative by enumerating known
idioms and grepping explicitly" as a general technique; the closest entries (`P-01`'s extension
census, `O-01`'s measured-vs-predicted framing) are adjacent but narrower in scope than this one.

### Relayed (c) — c4's generated-HTML provenance check and out-of-remit routing
**REJECTED, both sub-parts, as duplicates:**
- The do-not-edit-footer provenance check on an extension-census HTML hit is **already verbatim**
  in existing `G-11` ("check each for a regeneration/do-not-edit footer before counting it in-scope
  — a generated ship-review or report view is not product UI"). Adding a second entry would not
  sharpen it.
- Routing a real out-of-remit gap (the plan.yaml T-09 self-consistency defect) as a non-blocking
  open question naming the receiving lens, rather than filing it as `must_fix`, is **already
  captured** by existing `O-02` ("name the peer lens that should cover it in your return").

### Self-derived, accepted
- **Pin-hash prefix-typo recovery** (c1) → `G-15`, reasoning above.

### Self-derived, considered and rejected (not added)
- **Three-dot vs. two-dot diff scoping** (used c2/c3 to isolate a branch's own contribution from
  already-reviewed trunk content) — a real, distinct technique, but with `Gotchas` now at cap and
  no existing `Patterns`/`Gotchas` entry judged weak enough to displace, this candidate loses on
  marginal value against the three accepted above. Left to die rather than forced in — distillation
  is the curation step, and a full section with nothing weaker to displace means the candidate does
  not survive, not that the section is broken.
- **Message-grammar/copula drift** (c2, "disposition resolved." vs. house "is …" phrasing) —
  duplicate in substance of existing `P-14` (grep multiple live examples of a convention before
  filing a consistency finding); the c2 case is exactly that check applied, not a new rule.
- **Cross-schema behavioral divergence routed to a peer lens** (c3, INV-32 skip-acceptance vs.
  `_skipped_member_error`'s fable-advisor-only restriction) — duplicate of `O-02`.
- **Verify-fix-closed-by-direct-diff-not-narration**, reconfirmed at c1/c2 for the same M7 finding —
  duplicate of existing `G-01`; this feature's repeated correct application is evidence `G-01` holds
  up, not a new rule.
- **Self-scope-out evidenced by a measured census** (dispatch's own framing note) — duplicate of
  existing `O-01`, which already states this exactly ("a scoped-out verdict rests on a measured
  check... holds up under cross-review scrutiny").

## Evidence a decline held up

Every one of my five Mode B cycles this feature scoped `in_scope` on a measured extension census
(0/41, 0/51, 0/66, 0/71, 5-file delta with one confirmed-generated HTML) rather than an inferred
guess, and c2's `in_scope: false, PASS by measurement, not inference` was never contradicted by a
later cycle or a peer review — consistent with existing `O-01`, no new entry needed.
