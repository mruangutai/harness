# Expertise — harness-dev-ops

## Patterns (max 15)
- P-02: WHEN a test runner combines an explicit list with a glob-based drift detector DO keep the two mechanisms separate — collapsing to glob-and-run erases the case that makes a specific exit code reachable and silently disables drift detection.
- P-03: WHEN a domain guard denies a write DO accept the denial as final — never retry through a command shape the guard doesn't parse. A coverage gap is not permission — return the denial and let the tier above route it.
- P-04: WHEN a CI step's `run:` body can't be exercised until it lands on a runner DO extract it into a standalone script and execute it against the real tool's live output locally first — untestable-until-merged is a gap to close, not accept.
- P-05: WHEN capturing a git status snapshot as verification evidence DO record it unfiltered rather than trimmed to what the dispatch pre-warned about — an unexpected modified-not-untracked file is exactly what an unfiltered capture catches and a filtered one would silently miss.
- P-06: WHEN verifying in a shared working tree DO re-check git status at the end and diff it against the opening snapshot — a verification window spans real time other agents can write into, so the tree is read at two points, not one, and the run should say so.
- P-07: WHEN a dispatch names a gate as a risk without stating whether it currently passes DO run that gate standalone and report the result explicitly — a risk left unmeasured in the record reads later as unknown status, not as verified green.
- P-08: WHEN a verify clause asserts only that old required text is ABSENT DO also assert the new required content is literally PRESENT, mirroring any correct positive-check instance already in the same file — a negative-only clause passes unconditionally on an emptied or deleted field.
- P-09: WHEN judging near-identical blocks for dead-code deletion DO locate the exception by an adjacent comment, never by line number (deletions shift lines below), and prove no case is lost via the ordered SET of ok-line texts before/after — a bare count hides a case lost behind a coincidental addition.
- P-10: WHEN a dispatch quotes a verify command inline DO independently re-extract it from its source config and byte-diff it against the quoted copy before running — this decouples acceptance evidence from the dispatcher's transcription, keeping it attributable to the source, not the relay.

## Gotchas (max 15)
- G-01: Nothing invokes check-state.sh automatically — it is manual-only, so a green session is not evidence it ran. (This gotcha used to also cover check-docs.sh's exec-bit fail-open; that script and INV-10 were struck under DEC-188.)
- G-02: WHEN a verify command relies on `${PIPESTATUS[0]}` DO wrap it in `bash -c '...'` — this Bash tool's default shell is zsh, not bash, where PIPESTATUS silently expands empty and the check passes vacuously instead of failing.
- G-03: WHEN writing verification bash for this repo DO avoid `declare -A` (associative arrays) — this machine's default bash is 3.2.57, which errors `invalid option` on it. See the drift-detector's nested-loop membership check in `.claude/skills/harness/bin/run-unit-tests.sh` for the working pattern.
- G-04: WHEN proving a runner's properties DO check its source and the file's mode, not the transcript — a capture-and-replay wrapper (`out=$(cmd); echo "$out"`) reproduces a byte-identical transcript while voiding downstream verifies, and a missing exec bit yields a failure mode a passing transcript won't show.
- G-05: `.claude/skills/harness/templates/harness.json` is merged additively into `.harness/harness.json` by `.claude/skills/harness/bin/upgrade-config.py`, and copied verbatim on init — editing one without the other creates silent drift on the next upgrade or init.
- G-06: WHEN wrapping a CLI tool that has more than two meaningful exit codes DO pass its exit code through (`exit "$rc"`) rather than normalizing to 0/1 — normalizing silently drops a real outcome (e.g. cannot-verify) at that call site.
- G-07: WHEN leaving an adjacent pre-existing comment or config untouched because it's out of scope DO byte-check it before and after rather than assume, and write any nearby new comment only on grounds you personally verified — not by copying its phrasing.
- G-08: WHEN a verify script inspects `git show --name-only` output for a renamed path DO expect only the destination path — the source path never appears there; use `--name-status` instead when the old path itself must be matched.
- G-09: WHEN a verify clause collapses whitespace with `awk`/`gsub` to match a literal prose phrase DO test it against fixtures with inline markup (bold, code span, blockquote prefix) landing inside the phrase — those break contiguity and false-RED even though the visible text matches.
- G-10: WHEN judging whether a script's outcome can gate on its exit code DO run it and inspect the exit code directly — some audit/lint tools print findings to stdout while always exiting 0, and reading for `sys.exit()` in source is not a substitute for measuring.
- G-11: WHEN a three-dot diff (`A...HEAD`) audits which files changed DO first check whether HEAD has moved from the base commit — an empty three-dot diff means 'no changes' and 'nothing committed yet' identically, and only a working-tree diff distinguishes the two.
- G-12: WHEN reporting a wall-clock timing as verification evidence DO capture and report its exit code alongside it, and an ok-count for every suite measured — a duration number alone cannot distinguish a fast success from a fast failure.

## Outcomes (max 10)

## Open (max 5)
