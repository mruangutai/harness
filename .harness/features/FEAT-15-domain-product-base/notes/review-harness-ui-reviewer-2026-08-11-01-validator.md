# FEAT-15 · harness-ui-reviewer · scope decision (SHA e057525)

**Out of scope.** No rendered UI surface in this diff.

1. **File-extension census** (`git diff --stat 8122948..e057525 --name-only`) — zero
   html/css/scss/less/tsx/jsx/vue/svelte files. All 22 changed files are `.sh`, `.py`, `.yaml`,
   `.md`. `check-domain.sh` (241 lines changed) is the only substantive code touched; it's a
   bash-invoked Python PreToolUse hook, no markup or styling.
2. **DESIGN.md** — confirmed absent: `git cat-file -e e057525:.harness/features/FEAT-15-domain-product-base/DESIGN.md`
   fails (does not exist at pinned SHA). Matches BRIEF.md:191-192, "No UAT criterion, deliberately"
   — the feature never claims a design contract, so there is nothing for Mode A to audit.
3. **Stderr messages (`BLOCKED`, `Permitted for you:`, lines ~201, 250, 324, 329, 531, 545, 642-643)**
   — read directly. Scoped OUT of UI-reviewer remit: this is plain-text CLI/terminal output
   consumed by an agent process, not a rendered surface — no markup, no styling, no colour, no
   focus/interaction state, no a11y tree to check contrast or reading order against. It is a
   correctness/wording question (does the message accurately describe PRE vs POST-mode semantics,
   does it match the fleet.yaml schema, etc.), which is harness-code-reviewer's SC-12 content
   check, not this role's. Not duplicated here per dispatch instruction.

No findings, no must_fix, nothing to gate on.
