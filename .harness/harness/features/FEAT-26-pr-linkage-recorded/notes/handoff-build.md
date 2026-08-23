# FEAT-26 build seam — eight tasks landed, the panel found three, all closed

## Next
Nothing on the build. The remaining arc is pm's goal-check against the signed success
criteria, then the PR, CI and merge. Two things must ride into the PR body:
- **`gh-sync.py closes <feature-dir>` now emits `Closes #492`.** Paste it. Without it this
  feature's own PR does not close the ticket it exists to fix.
- `feature.json` records `pr` after the merge via `gh-sync.py record-pr`, which `ship` runs.

## Trust
- **Every task's own `verify` printed `VERIFY-OK`.** Full suite `--kind all`: **45 PASS, 0
  FAIL**, run with the claim registry empty because #741 makes that suite report false
  failures while agents are in flight.
- **The qa classification was settled before the gate ran and it was nearly a hole.**
  `touches_db_or_external` is YES for this diff — T-03 shells out to `gh pr list`. Judged on
  T-04 alone the honest answer is NO, because making no external call is exactly what
  `closes` does. A `unit`-only gate runs neither `test-gh-sync.py` nor `test-check-state.py`,
  which is the whole evidence for T-02 through T-05. See `notes/qa-classification-ruling.md`.
- Panel: code FAIL, qa PASS, security PASS, ui PASS. All three must-fixes are closed.
- The four PR numbers measurement cannot derive were measured anyway, by PR **title**. Seven
  more were checked the same way before writing.

## Dead ends
- **A verify can pass because it cannot fail, and this one fooled the main session.** T-07's
  clause grepped for a sentence that wraps across two lines. `grep` matches within a line, so
  no line ever contained it: green whether or not the correction was made. The main session
  ran it, got `VERIFY-OK`, and reported T-07 done with the false sentence still on the page.
  **The general rule, from pm: only an ABSENCE assertion turns a wrap into a false green.**
  Presence assertions break loud. Grade pattern span against matcher unit, and note which way
  the failure points.
- **`plan.yaml` was pinned at a decision number that had been taken.** T-08 demanded
  `## DEC-197`; it has been taken since 2026-08-22 and DEC-198/199 landed after signature.
  The entry is DEC-200. Re-derive a number, never inherit one.
- **The mirror is not refreshed by `ship`.** FEAT-26's own `source_issues` was absent because
  `open` last ran before T-02 existed. `closes` printed nothing. Re-running `open` at Review
  fixed it — idempotent, every recorded id skipped.
- **Do not classify the test matrix task by task.** See above; it is the diff that counts.

## Working set
- `.claude/skills/harness/bin/gh-sync.py` — `_record_pr` (exactly-one rule, never overwrites),
  `cmd_closes` (renders, never posts), `source_issues` mirroring.
- `.claude/skills/harness/bin/check-state.sh` — INV-28, and its six cases in
  `test-check-state.py`.
- `.claude/skills/harness/bin/feature-schema.json` — `pr` and `github.source_issues`.
- `.harness/harness/docs/DECISIONS.md` — DEC-200, and its regenerated index row.

## Log
- Five agents died on a 600s no-progress watchdog before this build completed. The cause is
  upstream: **children of a subagent are always async and completion notifications never
  reach a subagent parent** (anthropics/claude-code#75043), so an orchestrator has no legal
  way to wait. The build was finished by the main session sequencing leads directly.
- **DEC-186's scope question is OPEN and is the operator's**: `record-pr`'s
  `gh pr list --state merged` read is none of DEC-186's four closed purposes. Both readings
  are recorded in DEC-200. Either the bound widens to five or DEC-186 says the mirror is out
  of its scope.
