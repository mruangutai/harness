# Expertise — harness-ui-reviewer
## Patterns (max 15)
- P-01: WHEN reviewing any diff in this repo DO expect zero rendered UI by default — harness is files-only, no build step (CLAUDE.md); confirmed via extension census on multiple diffs (0 html/css/scss/tsx/jsx/vue/svelte/less hits). Scope reduces to markdown DESIGN.md contracts (rare) and adjacent CLI/hook-emitted text surfaces.
- P-02: WHEN a file-extension census hits an .html file under a feature's notes/ directory in this repo DO check it for a do-not-edit/regenerate footer before counting it in-scope — this repo generates ship-review reports there, which are not authored product UI.
## Gotchas (max 15)
## Outcomes (max 10)
## Open (max 5)
