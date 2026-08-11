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
- P-09: WHEN sibling CLI commands enforce the same refusal condition through different code paths (an explicit refuse call vs. a raised-and-caught exception) DO verify both resolve to the same exit code and message grammar — this cross-tool consistency check is invisible to a per-call-site code-review lens.
- P-10: WHEN a message-wording defect already exists unchanged in a pre-existing sibling message DO record the new instance as a non-gating note rather than filing a fix against the untouched sibling — extending remedy scope into code the diff never touched is not this role's call.

## Gotchas (max 15)
- G-01: WHEN closing a prior FAIL's must_fix in a Mode A recheck DO verify the fix's literal text in the document itself (grep the actual wording/query/value) before marking closed — a closing review's own narration, or the plan's stated intent, is not evidence until the artifact is read directly.

## Outcomes (max 10)
- O-01: A scoped-out verdict backed by a file-extension census plus a confirmed-absent contract check held up under cross-review scrutiny as a reviewed finding, distinct from predicting in advance that nothing would be found.

## Open (max 5)
