# c2 send-back applied — step f no longer orders a commit

**Done, one field, two spots.** `tasks[T-01].intent` was replaced through
`plan-merge.py amend` (compare-and-swap, `--expect-sha256`); nothing else in
`.harness/harness/features/BUG-285-yaml-loader-pin/plan.yaml` was touched. The file grew 127 → 131
lines, all four inside the two amended spots. Two amends ran: the first applied the wording, the
second corrected one line citation (see "Deviation from the c1 wording" below).

## What step f now says (`plan.yaml:117-124`)

The builder records both transcripts and the exact commands in `notes/qa-<runid>.md` under this
feature's `notes/` directory and **LEAVES that file in place**; it must **NOT run `git commit`** —
the commit pen is the orchestrator's (DEC-153), which stages by explicit pathspec; it **REPORTS the
note's exact path as its DIGEST artifact** so the orchestrator commits it alongside the test change,
because SC-03 is graded with `git show <review_sha>:<that path>` and a note absent from that commit
grades not_met. The tail is unchanged: delete the throwaway script and its tempdir, nothing under
`tests/` or `.claude/` left changed.

## The one-file qualifier (`plan.yaml:49-52`)

"…and do not edit any file other than `tests/integration/test-gh-sync.py` **and your own notes file
under this feature's notes/ directory**." Widened to exactly that file and nothing else.

## Deviation from the c1 wording — one line number

The c1 must_fix cited `team-config.yaml:259` for harness-qa's notes grant. In this **worktree's**
copy that grant sits at line 258 (259 is `review-harness-qa-*.md`). In the **owner** manifest
`/Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml` — the copy
`check-plan-routes.py` reports the hook consults — it is at line 259. The intent therefore cites
**259**, matching the owner manifest. The filename the c1 note suggested, `notes/qa-<runid>.md`, is
correct for the grant `.harness/*/features/*/notes/qa-*.md`, so it was used as written.

## Verified after the write

`safe_load` over the file: top-level keys `approval decisions feature lanes schema source_issues
status tasks` — **no `panel:`**; `approval.status: pending`; **one** task; **four** decisions;
`files: ['tests/integration/test-gh-sync.py']`; `traces: [REQ-01..REQ-04]`; `verify:` still a
literal block loading byte-identically to
`env -u HARNESS_AGENT_TYPE python3 tests/integration/test-gh-sync.py\n`; `intent:` still `|`; the
task's eleven keys are the c1 set. `intent` in the file is byte-equal to the value file that was
applied. No commit was made, no suite was run, HEAD was not moved.

## Advisory — not caused by this change

`check-plan-routes.py <this plan>` prints `OK T-01 granted to harness-backend-dev, harness-dev-ops,
harness-qa` but exits **1**, counting one violation whose only printed line is `DEVIATION ... this
worktree's .harness/team-config.yaml differs from the owner manifest`. That is a worktree/owner
manifest skew, independent of this edit — the plan's routing fields were not touched. Worth the
orchestrator's attention before signature, since a non-zero exit reads as a plan gate failure.
</content>
<parameter name="i">Writing c2 amend note