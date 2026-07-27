## Patterns (max 15)
- P-01: This repo has no build system — no package.json, Makefile, or .github/. All automation is Claude Code hooks in .claude/settings.json (SubagentStart / PreToolUse / SubagentStop), which is the only wiring mechanism in use.

## Gotchas (max 15)
- G-01: check-docs.sh runs only as a subprocess of check-state.sh (INV-10, check-state.sh:174), and that call is guarded by `os.access(cd, os.X_OK)` — if check-docs.sh loses its exec bit, INV-10 silently passes instead of failing. Nothing invokes check-state.sh automatically, so both scripts are manual-only.

## Outcomes (max 10)

## Open (max 5)
