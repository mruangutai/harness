# Expertise — harness-ui-reviewer

## Patterns (max 15)
- P-01: WHEN scoping a diff for a Mode B UI review DO run a file-extension census (html/css/scss/tsx/jsx/vue/svelte/less) across the full diff before concluding no UI surface exists — a census makes "no UI" a measured finding, not an inferred guess.
- P-02: WHEN a dispatch or ambient context claims a design contract's presence, absence, or content DO confirm it with a direct object check (`git cat-file -e`, `git diff`) at the pinned commit — a dispatch's description of a file is a hypothesis, not evidence.
- P-03: WHEN deciding if a markdown file is in scope DO test whether it specifies spacing, colour, states, or interaction for a rendered surface — markdown is a medium this role can audit, not a guarantee any given markdown file is a UI contract.
- P-04: WHEN a diff only deletes CLI/terminal output DO rule it out of scope with explicit stated reasons (no markup/styling/a11y tree, no contract to diverge from, deletion not build) rather than silently defaulting to skip — unless the dispatch names it as a surface to judge.
- P-05: WHEN the working tree is dirty or ahead of the pinned review SHA DO inspect content via `git show`/`git diff` against the pinned commit objects directly rather than checking out — reviews the correct commit without disturbing local state.
- P-06: WHEN dispatch explicitly names an adjacent non-rendered surface (e.g. CLI/error-message output) alongside a no-UI diff DO treat it as in-remit and audit it against the stated requirement — a handed-down surface turns a decline into a reviewed finding, not an optional extra you may skip.
- P-07: WHEN a Mode A contract pins concrete values (wording, query shape, format) DO diff them byte-for-byte across every document that claims to implement it (design doc, plan, code) — narrative agreement is not literal agreement, and a criterion that checks only one slot can miss full-text drift.
- P-08: WHEN auditing a Mode A state/message contract table DO cross-check every row against the full success-criteria list for a covering, checkable assertion — a row with correct prose but no enforcing criterion is invisible to gates and is the highest-value Mode A finding.
- P-09: WHEN a rewritten message diagnoses one specific system/repo state as an error DO trace which real invocations reach that branch and confirm the post-feature normal state is not among them — a message can be textually accurate yet fire on the case the feature just made normal.
- P-10: WHEN sibling CLI commands enforce the same refusal condition through different code paths (an explicit refuse call vs. a raised-and-caught exception) DO verify both resolve to the same exit code and message grammar — this cross-tool consistency check is invisible to a per-call-site code-review lens.
- P-11: WHEN a message-wording defect already exists unchanged in a pre-existing sibling message DO record the new instance as a non-gating note rather than filing a fix against the untouched sibling — extending remedy scope into code the diff never touched is not this role's call.
- P-12: WHEN a contract clause requires a property for 'every' item in a collection DO check the zero-cardinality case — vacuous truth over an empty set can make a broken/empty collection compute a clean verdict, silently reintroducing the exact defect class the contract exists to prevent.
- P-13: WHEN you find a contract gap in one task or document's wording DO sweep sibling tasks/documents that independently restate the same intent for the identical gap before scoping a fix — a fix landing in only one instance leaves the other reading the same ambiguity.
- P-14: WHEN filing a completeness/consistency finding that cites an unstated house convention DO grep multiple live examples of that convention in the codebase and quote them before filing — a consistency finding needs the convention confirmed to exist, not assumed from general style expectations.

## Gotchas (max 15)
- G-01: WHEN closing a prior FAIL's must_fix in a Mode A recheck DO verify the fix's literal text in the document itself (grep the actual wording/query/value) before marking closed — a closing review's own narration, or the plan's stated intent, is not evidence until the artifact is read directly.
- G-02: WHEN a surface under review is batch/CLI text with no colour-only state encoding DO state the accessibility and theme-parity sections as explicitly not-applicable with the reasoning, rather than omitting them — an omitted section reads as unchecked, not confirmed inapplicable.

## Outcomes (max 10)
- O-01: WHEN a scoped-out verdict rests on a measured check (extension census, direct object check) rather than a prediction DO record it as such — a scoped-out review that looked holds up under cross-review scrutiny; one that merely predicted absence does not.

## Open (max 5)
