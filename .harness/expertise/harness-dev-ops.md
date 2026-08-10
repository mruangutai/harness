# Expertise — harness-dev-ops

## Patterns (max 15)
- P-01: This repo has no build system — no package.json, Makefile, or .github/. All automation is Claude Code hooks in .claude/settings.json (SubagentStart / PreToolUse / SubagentStop), which is the only wiring mechanism in use.
- P-02: WHEN a test runner combines an explicit list with a glob-based drift detector DO keep the two mechanisms separate — collapsing to glob-and-run erases the case that makes a specific exit code reachable and silently disables drift detection.
- P-03: WHEN a domain guard denies a write DO accept the denial as final — never retry through a command shape the guard doesn't parse. A coverage gap is not permission — return the denial and let the tier above route it.

## Gotchas (max 15)
- G-01: Nothing invokes check-state.sh automatically — it is manual-only, so a green session is not evidence it ran. (This gotcha used to also cover check-docs.sh's exec-bit fail-open; that script and INV-10 were struck under DEC-188.)
- G-02: WHEN a verify command relies on `${PIPESTATUS[0]}` DO wrap it in `bash -c '...'` — this Bash tool's default shell is zsh, not bash, where PIPESTATUS silently expands empty and the check passes vacuously instead of failing.
- G-03: WHEN writing verification bash for this repo DO avoid `declare -A` (associative arrays) — this machine's default bash is 3.2.57, which errors `invalid option` on it. See the drift-detector's nested-loop membership check in `.claude/skills/harness/bin/run-unit-tests.sh` for the working pattern.
- G-04: WHEN proving a runner's properties DO check its source and the file's mode, not the transcript — a capture-and-replay wrapper (`out=$(cmd); echo "$out"`) reproduces a byte-identical transcript while voiding downstream verifies, and a missing exec bit yields a failure mode a passing transcript won't show.
- G-05: `.claude/skills/harness/templates/harness.json` is merged additively into `.harness/harness.json` by `.claude/skills/harness/bin/upgrade-config.py`, and copied verbatim on init — editing one without the other creates silent drift on the next upgrade or init.

## Outcomes (max 10)

## Open (max 5)
