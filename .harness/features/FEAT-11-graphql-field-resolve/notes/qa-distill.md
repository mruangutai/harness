# QA distillation — FEAT-11-graphql-field-resolve

Cold pass over `notes/qa-c0.md` (blocking matrix gate) and `notes/review-harness-qa-c0.md`
(gate-only re-run at pinned `review_sha 2ea9af3`) — no observations log existed for this agent this
feature, so these two run notes are the source per the dispatch.

## Section counts

| Section | Before | After |
|---|---|---|
| Patterns | 7 | 9 |
| Gotchas | 3 | 4 |
| Outcomes | 2 | 2 |
| Open | 0 | 0 |

No displacement — no section was at cap.

## Relayed candidates — verdicts

**C1 — accepted.** Added `P-08`. My own two gate notes both scored SC-11 "distinct from org and
board-absent" without checking whether *both* named distinctions had their own comparison — pm's
goal-check caught what my gate missed (`unknown_exc` vs `board_exc` never directly compared). This
is a real, repeatable blind spot in how I read multi-clause SCs: I confirm the area has a passing
assertion and stop, rather than mapping each named clause to its own check. Generalizes past this
feature — kept as a rule about inequality not being transitive, not as an instance.

**C2 — accepted.** Added `P-09`. My own MF-1 review note is the positive case of this rule (ran the
mutant, discovered the vacuity was real for one message and not the other) and the relayed
candidate is the same lesson from the other side (eng-lead's MF-1 dispatch generalized from one
message to a sibling by reading rather than running). Worth keeping as its own entry rather than
folding into P-07 — P-07 is about asserting content over presence; P-09 is specifically about the
*method* for judging vacuity (run it, don't eyeball the string), which is the distinction that
actually would have prevented the over-broad claim.

**C3 — accepted.** Added `G-04`. Directly matches my own two run notes: the prior gate's Q1 flagged
that the matrix was bound only via the task's local `verify:`, and this run's own step explicitly
ran `run-unit-tests.sh --kind integration` as the standing bucket command, separate from task
verify, and reported the real 97/97 count. That distinction (task verify vs. kind command) is not
yet in Expertise as its own rule — P-04's denominator framing is adjacent but doesn't say to run
the second command. Kept as a Gotcha since it's a concrete "do this specific extra step," not a
general judgment rule.

## Stale-entry check

Reviewed all 7 existing Patterns, 3 Gotchas, 2 Outcomes against this feature's evidence. **None are
stale.** P-04 (denominator framing) and P-07 (assert content not presence) both got reinforced, not
contradicted, by this feature's findings (see C1/C2 above) — they remain correct as stated, and the
new entries are additions covering gaps those two didn't reach, not replacements.

## Harness defect noted, not distilled

`review-harness-qa-c0.md` records a `bash-write-guard.sh` false-positive on `cp ... 2>/dev/null`
(redirect target misread as a `cp` destination). That was already correctly routed as an
`open_question` in that run's DIGEST, not into Expertise — a workaround entry here would outlive
the fix. Not re-raised in this distillation; it belongs to whoever reads that run's DIGEST, not to
this cold pass.

## Round 2 — one missed source: `notes/review-harness-qa-plan-contract.md`

Scope: this one note only, judged against the file as round 1 left it (9 Patterns, 4 Gotchas, 2
Outcomes, 0 Open). Not re-deriving anything from `qa-c0.md`/`review-harness-qa-c0.md`.

**Candidate — accepted. Added `P-10`.** The note's Q1(a) finding: `git diff --quiet HEAD -- <files>`
is vacuous once the build agent commits before running verify, because `HEAD` moves to include the
commit and the comparison becomes self-referential (empirically demonstrated in a disposable scratch
repo: post-commit `git diff --quiet HEAD` exits 0, `git diff --quiet <pre-edit-sha>` exits 1).

Judged against the flagged candidate `P-09` (run a substring/mutation probe rather than reading
message text): **kept separate, not a `replace`.** P-09's WHEN is "judging whether an assertion is
vacuous" via message wording, and its DO is "run a probe instead of reading text." This note's
finding is a different WHEN (a `git diff`-against-`HEAD` verify clause specifically) and a different
DO (check commit-before-verify ordering; diff the pinned SHA, not HEAD) — the actionable step is not
"run it instead of reading it," it's "diff against a different baseline entirely." Folding it into
P-09 would either widen P-09 past its own single mechanism or produce a `merge` result describing two
unrelated failure modes under one WHEN, which is the instance-list smell the distill skill warns
against. Both are true and independently useful: P-09 for wording-based vacuity, P-10 for
baseline-timing vacuity. Generalizes past this feature — any `git diff --quiet HEAD`-style
freeze-verification clause in any plan is exposed to the same ordering bug, independent of what
files or wording it names.

No displacement — Patterns was 9/15, now 10/15; nothing else changed.

### Section counts

| Section | Before (round 2 start) | After |
|---|---|---|
| Patterns | 9 | 10 |
| Gotchas | 4 | 4 |
| Outcomes | 2 | 2 |
| Open | 0 | 0 |

`check-expertise.sh .harness/expertise/harness-qa.md` — OK.
