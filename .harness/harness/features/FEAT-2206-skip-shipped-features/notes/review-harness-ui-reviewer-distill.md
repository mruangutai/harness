# PASS — no new UI Expertise rule earns displacement

Accepted **0**, rejected **1** relay candidate; exact host-application JSON ops: `[]`. Neither Expertise target was changed. No diff reviewed; no product suite, rendering, tests, grader, build, lint, formatter, or expertise checker run. Host/main owns final directory checking.

## Independent derivation, before relay

Read `review-harness-ui-reviewer-c0.md`, `-c2.md`, `-c3.md`, and `-c5.md` in this notes directory first. Their measured changed-object counts grow 20 → 42 → 51 → 62 without introducing visual surfaces. Three durable lessons already have coverage:
- Re-measure and classify the exact pinned range, including Markdown/schema/CLI objects rather than relying on extensions: craft P-01/P-02/P-03/P-05 and O-03/O-05.
- No visual surface means accessibility/theme/focus/layout are not applicable, not visually passed: craft G-02/G-15.
- Route CLI behavior and behavioral-closure claims to code/QA instead of certifying them through a visual scope-out: craft O-02. Explicit adjacent-surface assignments remain covered by P-06/O-06; this feature does not justify a blanket CLI exclusion.

These are covered observations, not additional accepted/rejected relay proposals.

## Relay disposition

**Rejected UI candidate 1 — already covered, no stronger rule.** `runs/distill-validator/candidates.md:18-19` relays lead acceptance of measured scope-outs with bounded assurance. Source: `runs/validate-c3-validator/digest.md:10,49-53,102` credits the measured zero-surface census; `notes/ship-review-validate-c3-validator.md:31` records UI scope-out. The original c0/c2/c3/c5 notes explicitly reserve CLI correctness for functional reviewers and deny visual approval. Craft P-01, O-02/O-03/O-05, and G-15 already encode the actionable discriminator and assurance boundary. Repeating this case adds no stronger instruction and displaces nothing at full craft caps. No new repository-specific invariant is established.

## Measured counts and application targets

Counts freshly measured from section headers and entry IDs in the assigned feature tree, not inferred solely from injected Expertise. Order: **Patterns / Gotchas / Outcomes / Open**.

| Layer and exact target relative to feature-tree root | Before | Projected after |
|---|---|---|
| Craft: `.harness/expertise/harness-ui-reviewer.md` | 15 / 15 / 10 / 0 | 15 / 15 / 10 / 0 |
| Repository: `.harness/harness/expertise/harness-ui-reviewer.md` | 4 / 0 / 0 / 0 | 4 / 0 / 0 / 0 |

Exact ops for both targets: `[]`. No entries appended, merged, replaced, or dropped. No harness defect identified for escalation. Open questions: none. This is feature-close distillation only, not a fresh source or rendered-UI review.
