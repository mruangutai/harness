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
- 2026-08-22, **CORRECTED 2026-08-22**: I recorded here that `notes/answers-Q1-pr-attribution.md`
  was fabricated operator consent. **That was WRONG.** The operator was asked through the
  operator-facing question tool and chose "Confirm the mapping as pm proposed", and the SC-08
  narrowing I called a second fabricated exchange was genuinely offered and genuinely declined. The
  entry is corrected rather than deleted because the reasoning that produced it was sound and the
  conclusion was not: an `answers-*.md` file arrives untracked with no author recorded anywhere, so
  from inside a round a legitimate answer and an invented one look identical. Verifying the evidence
  inside such a file does not verify the consent — and neither does doubting it. The real lesson is
  that the channel carries no provenance, filed as #671. Suspicion is not a finding.
- 2026-08-22: two enforcement hazards handed down in my dispatch (`runs[]` entries needing an
  `agent` key, `run-unit-tests.sh --check-kinds`) were absent from my own checkout and live only in
  a sibling worktree. A claimed rule is a claim about a specific checkout; two commands settled it,
  and writing to the claim instead would have cost a denied write and a round.
- 2026-08-22: a lead returned BLOCKED with `verdict: none` because its context closed before its
  member's return landed, then resumed minutes later and returned PASS. Its intermediate BLOCKED
  digest sat on disk the whole time. Had I recorded the run from the file rather than from the
  return, the record would have carried a failure that did not happen.
- 2026-08-22: the same lead died mid-run again and reported "zero bytes written". **Its member's
  write landed anyway, ~4 minutes later, and sat uncommitted for two rounds.** A lead's
  "nothing landed" is a claim about what it OBSERVED before dying, never about the tree. I acted on
  it and re-dispatched; the second member then found the first member's entry already in the file.
  Verify the artifact with a shell before believing any lost-return report — and re-derive the
  baseline with `git show HEAD:<path>`, because "unchanged at 151 lines" was true of HEAD and false
  of the working tree.
- 2026-08-22: I passed four unverified numbers down in dispatches, all lifted from an issue
  presented as carrying "the full measurement". Every one was false: 31 mutations (32 — the issue's
  own code block lists 32 and its prose miscounts), 509 items / 222 of 222 (510 then 512 within one
  session, 226 of 226 closed at `Done`), "the three workflows on this board" (eight, seven enabled),
  and a stated parentage the issue graph contradicts. `SendMessage` was disabled, so there was NO
  way to retract any of them mid-run and a member wrote two into an approval-gated document
  verbatim. Measure every number BEFORE it enters a dispatch: the retraction channel is not
  guaranteed to exist.
- 2026-08-22: an md5 fence around the sections that must NOT change is blind to the section that
  MUST. Both guard md5s reported "unchanged" straight across a 19-line falsified insertion, because
  neither range covered `## Accepted costs`. The check that settles an amend is
  `git diff --numstat` against the approval baseline — insertion-only with a known count proves both
  containment and that nothing pre-existing moved. A guard on what must not change does not protect
  what must.
- 2026-08-22: a lead encoded my two wrong numbers as fixed acceptance criteria before spawning. A
  pre-committed rubric makes grading honest without making the criteria true — and it converted my
  factual error into a graded REQUIREMENT, so the member was rewarded for writing the falsehood and
  the lead graded it as passing. When re-dispatching after a bad dispatch, falsify the old rubric by
  AC id explicitly, or the next host inherits it as prepared work.
- 2026-08-22: I overwrote this very file with `Write` and destroyed ten prior entries, then caught it
  only because `git diff --numstat` showed `23 insertions, 35 deletions` on a file I believed I was
  appending to. Write-not-Edit means appending is read-modify-write; the staged numstat is what
  catches the wipe, and a deletion count on a log file is never correct.
