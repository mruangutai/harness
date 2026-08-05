# Expertise — harness-ui-reviewer

## Patterns (max 15)
- P-01: WHEN scoping a diff for a Mode B UI review DO run a file-extension census (html/css/scss/tsx/jsx/vue/svelte/less) across the full diff before concluding no UI surface exists — a census makes "no UI" a measured finding, not an inferred guess.
- P-02: WHEN a design contract is expected but not visible DO confirm absence with a direct object check (e.g. `git cat-file -e`) against the pinned commit — "not found in context" and "confirmed absent at the pin" are different claims; only the second is checkable.
- P-03: WHEN deciding if a markdown file is in scope DO test whether it specifies spacing, colour, states, or interaction for a rendered surface — markdown is a medium this role can audit, not a guarantee any given markdown file is a UI contract.
- P-04: WHEN a diff only deletes CLI/terminal output DO rule it out of scope with explicit stated reasons (no markup/styling/a11y tree, no contract to diverge from, deletion not build) rather than silently defaulting to skip — unless the dispatch names it as a surface to judge.
- P-05: WHEN the working tree is dirty or ahead of the pinned review SHA DO inspect content via `git show`/`git diff` against the pinned commit objects directly rather than checking out — reviews the correct commit without disturbing local state.
- P-06: WHEN dispatch explicitly names an adjacent non-rendered surface (e.g. CLI/error-message output) alongside a no-UI diff DO treat it as in-remit and audit it against the stated requirement — a handed-down surface turns a decline into a reviewed finding, not an optional extra you may skip.

## Gotchas (max 15)

## Outcomes (max 10)
- O-01: A scoped-out verdict backed by a file-extension census plus a confirmed-absent contract check held up under cross-review scrutiny as a reviewed finding, distinct from predicting in advance that nothing would be found.

## Open (max 5)
