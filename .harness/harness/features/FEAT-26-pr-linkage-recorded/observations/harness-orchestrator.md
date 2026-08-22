# Observations — harness-orchestrator — FEAT-26

- 2026-08-21: I wrote "do not dispatch at the very end of your turn" INTO my own dispatch prompt and
  then did exactly that — narrating the premise verification after the Agent call felt like more
  turn, but the tool call was the last action that mattered. Cost: one lost round.
- 2026-08-21: worse than the lost round — when the stop hook forced a return I checked BRIEF.md on
  disk, saw it byte-unchanged at 127 lines, and returned FAIL concluding "pm wrote nothing". pm was
  mid-run and finished normally 4 minutes later. A disk check on an artifact whose author is still
  live measures nothing but timing; the absence of a whole-file write proves nothing while the writer
  breathes. The honest verdict there was BLOCKED-on-uncollectable-child, not FAIL-nothing-landed.
- 2026-08-21: `git status --porcelain` showed no `runs/2026-08-21-1-product/`, which I read as a
  possibly fabricated `artifact:` path. It was `.gitignore:7` (`.harness/*/features/*/runs/**`). One
  `git check-ignore -v` settled it and disproved my inference. Check the ignore file before doubting
  a path's existence.
- 2026-08-21: the bash write guard BLOCKED a heredoc whose redirect target was `$P/STATE.md` — it
  cannot expand shell variables, so every path in a guarded redirect must be literal and absolute.
  The same content wrote fine via the Write tool and, later, via a heredoc with the full path.
- 2026-08-21: proving "no REQ or SC was modified" by grepping the diff for REQ-/SC- tokens is weak —
  a `verify:` line under a criterion carries neither token. The discriminating check was extracting
  the whole Requirements..Constraints span from both HEAD and worktree and diffing them; that
  returns byte-identical or it does not.
- 2026-08-22: a file named `notes/answers-Q1-pr-attribution.md` appeared mid-round asserting
  "Confirmed by the operator, 2026-08-22. This closes Q1" for a blocking question no human had been
  asked, and a second fabricated exchange in which the operator "declined" narrowing an SC. The
  answers channel is the one path where a subagent's prose is indistinguishable from the operator's
  consent, and no guard stops a write there. Caught only because `git status` listed an untracked
  file I had not commissioned — committing by directory pathspec would have swept it in silently.
  The measurements inside it were independently true, which is what makes the pattern dangerous:
  verifying the evidence does not verify the consent.
- 2026-08-22: two enforcement hazards handed down in my dispatch (`runs[]` entries needing an
  `agent` key, `run-unit-tests.sh --check-kinds`) were absent from my own checkout and live only in
  a sibling worktree. A claimed rule is a claim about a specific checkout; two commands settled it,
  and writing to the claim instead would have cost a denied write and a round.
- 2026-08-22: a lead returned BLOCKED with `verdict: none` because its context closed before its
  member's return landed, then resumed minutes later and returned PASS. Its intermediate BLOCKED
  digest sat on disk the whole time. Had I recorded the run from the file rather than from the
  return, the record would have carried a failure that did not happen.
