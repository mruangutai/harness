# Code review — FEAT-16 factory-per-repo-board — `a7c429c..ec195ec`

Overwrites the stray mis-routed note that was here before. That note was not a finding of mine.

Source read at the working tree, which sits two bookkeeping commits past the pin
(`git log --oneline ec195ec..HEAD` → two commits touching only `feature.json` and QA notes;
`git diff --stat ec195ec..HEAD` confirms none of the twelve `bin/` files or three `docs/harness/`
files changed after the pin, so the tree read is byte-identical to `ec195ec` on every path this
review cites).

## BLUF

PASS with one `med` note. Stage 1 spec compliance is clean across all twelve `bin/` files and the
three `docs/harness/` files — every change traces to a task intent, nothing found that no task asked
for, and the T-10 docs now say what the tree does. The one thing worth fixing before this loops again:
`test-factory-claim.py`'s P5 case claims to prove the new `(repo_name, issue_number)` de-duplication
works, but its own comment's premise is false — the assertions it makes pass identically with the
de-dup line deleted, because the candidate loop's `break`-on-first-win already prevents the second
duplicate from being reached in the scenario P5 builds.

## Target 1 — `factory_claim.py`'s de-dup and tie-break (`:271-290`)

**De-dup key `(repo_name, num)` is correct** — `repo_name` comes from `_repo_name_of(it)`, the
item's own `content.repository`, not from which fleet entry issued the query, so two entries
pointing at the same board number collapse their duplicate reads of the same GitHub item into one
candidate. Verified by hand-tracing `same_board_two_repo_fleet` in the test file.

**The explicit `(issue_number, repo_index[repo_name])` tie-break is untested, and that is defensible,
not a gap.** Given how `raw_items` is built (extended per repository in fleet order), a plain
num-only stable sort reproduces the explicit key's order in the single-board, single-issue cases the
suite exercises. It is **not** universally equivalent, though: on a shared board where two different
repositories both surface an issue carrying the *same number* (e.g. `A` and `B` share board 9, the
board holds both `A#7` and `B#7`, and GitHub's item order returns `B#7` before `A#7`), a num-only sort
would pick `B#7` first while the explicit `(num, repo_index)` key deliberately picks `A#7` — the fleet
order is load-bearing there. No test in `same_board_two_repo_fleet`'s family builds that interleave,
and none is required by any SC — the plan's own intent frames this task as "behaviour is unchanged;
what changes is that it is now chosen," which the shipped test suite's scenarios do not contradict.
Flagging for the record, not as a finding: a future test with power here would need two repos on one
board surfacing colliding issue numbers, not two repos each declaring their own distinct issue like
every current fixture does.

**The de-dup itself is undertested — `med`.** `test-factory-claim.py` P5 (`:975-990`) sets up two fleet
entries on the *same* board, both matching item #300, and asserts:
- `issue_view` is called exactly once for #300 ("the duplicate never entered the candidate loop")
- `project_field_set` is called exactly once

Traced against `factory_claim.py`'s candidate loop: the first candidate reaches `create_ref`, which
`Recorder.create_ref` (`test-factory-claim.py:137-143`) returns `True` for by default, so the winner is
set and the loop **`break`s** before the second (duplicate) candidate is ever reached — regardless of
whether the `if key in seen: continue` de-dup line exists at all. I confirmed this by tracing every
branch the second candidate would need to pass through: nothing in P5's fixture (open issue, no
`factory:claimed` label, no assignee, no `feature:` label) causes the loop to skip past the first
candidate, so the `break` fires on iteration one either way. Deleting the de-dup step entirely leaves
every one of P5's assertions passing unchanged.

A test that *would* discriminate needs the first (would-be-deduplicated) candidate to fail cleanly
before `create_ref` — e.g. an issue already carrying `factory:claimed`, or already assigned — so the
loop's `continue` reaches the second duplicate. With de-dup present that second candidate never
exists (one candidate, skipped, loop exhausts, "no claimable work"); without de-dup it would call
`issue_view` a second time. No such case exists in the current suite.

This is not a live-behavior bug: the plan's own T-02 intent says as much — "the duplicate loses the
create_ref race or is skipped by the factory:claimed label, which is a side effect, not a rule" — so
a missing de-dup wastes calls rather than producing a wrong outcome in every path I traced. It is a
test-quality gap against the reviewer's own explicit bar (target 1: "does anything test them?"): P5's
label overclaims what the assertions prove (Expertise P-01/P-12). Not `must_fix` — it doesn't gate —
but worth a follow-up test using a first-candidate-fails-before-create_ref fixture.

## Target 2 — Stage 1 spec compliance, all twelve `bin/` files + BRIEF's 13 SCs + plan's 11 tasks

Read every task's landed diff against its intent text. No divergence found:

- **T-01** (`factory_config.py`): `_validate_board` extraction, per-repo optional board, `board_for`/
  `board_station` delegating through `repo_entry`, `--show` payload contract — all match verbatim.
- **T-02** (`factory_claim.py`): per-repository loop for board reads/station validation, targeted and
  poll modes both scoped per repo, winner rebind at step 6 (already settled by the dispatcher, and I
  independently re-confirmed `winner_board = boards[repo_name]` at `:378`) — matches.
- **T-03** (`factory_decompose.py:325-330`), **T-04** (`factory_land.py:85-96`): both resolve
  `factory_config.board_for(fleet, args.repo)`, both keep the deliberate idiom split (T-03 uses
  `board_station`, T-04 indexes `stations["review"]` directly with the comment explaining why both
  are safe) — matches intent word for word.
- **T-05/T-06/T-11** (integration, check-domain, workspace fixtures): T-06 migrates exactly the four
  named fixtures (`good_repos`, the `nows_root` inline fixture — repaired to a *complete* per-repo
  board as the intent explicitly calls out — `two_base_fleet`, `two_base_fleet_for`), touches no
  assertion/exit-code/case-name, never touches `check-domain.sh` — verified by diff read. T-05 adds
  exactly the two permitted exceptional sites (`(D-config)` payload assertion, the `ready_option`
  reader) plus the one composed case (H) it's the only file that can carry, with an anti-vacuity check
  proving the discriminator has power (`served_number` must actually appear before asserting
  `other_number` does not). T-11 touches nothing but the fixture dict.
- **T-08** (`factory_config.py` final state): top-level `board` now rejected, every `repos[]` entry
  required, `station()` deleted with no remaining caller (`grep -rn "\.station("` over `bin/` returns
  nothing but `board_station`), `--show` conditional removed. Matches.
- **T-09** (`test-no-distribution.py` case5): all three named checks present, called from `main()`
  (a case defined but never called would always pass — confirmed it's wired in).
- **T-07** (`fleet.yaml` + `board2-capture.md`): fleet.yaml carries the per-repo board on
  `mruangutai/kaya-ai` exactly as specified, retains the DEC-174 am.1 comment; the capture file's
  figures (211 items, 118/82/11/0/0/0, the three historic option ids) match what SC-03 and D-07
  require, precondition explicitly reported. Empirically re-ran both unit and integration suites at
  this pin — `run-unit-tests.sh --kind unit` and `--kind integration` both exit 0, confirming SC-08/
  SC-09 still hold.
- **T-10** (docs, target 4 below).
- **SC-10** (inspection): the diff's own file list settles it — `git diff --stat a7c429c..ec195ec`
  (the 38-file stat captured at the top of this review) contains none of `check-domain.sh`,
  `bash-write-guard.sh`, `validate-digest.py` or `check-state.sh`. Holds.
- **SC-07**: I verified this from `board2-capture.md`'s recorded reading, not by re-running
  `gh project field-list` against the live boards myself — same evidence grade the capture itself
  claims (a T-07 precondition read, not a re-measurement this review performed independently).

No scope creep found — every line in the diff traces to a task. No omission found against the eleven
task intents.

## Target 3 — reconstructed RED (T-01, T-02, T-03, and the Q2 factory_config error-message fix)

Read all four receipts in full, not just the disclosure paragraphs. All four followed the same
honest-reconstruction shape: hash the edited production file, swap in the pre-task version via
`git show HEAD:`, run the already-written tests, observe the predicted subset fail (T-01: aborts at
case (25) before cases (26)-(31) ever execute against old code; Q2-c2: predicted exactly case (27b),
observed exactly that), restore, re-verify the hash is unchanged, then run GREEN. This is the honest
form of reconstruction the process note asks for, not a rubber stamp.

The real question per the dispatch — would these tests fail on a wrong *new* implementation, not just
the old one — I checked by reading the assertions directly rather than trusting the labels:

- T-01's cases (25)-(31) assert on concrete return values (`board_for(...)["number"] == 3`, message
  substrings naming the right repository, `board_station` raising on an unknown key) — these are
  genuinely discriminating against a wrong `board_for`/`board_station` implementation, not just a
  presence check.
- T-02's P1-P6 (already the deepest-verified section of this review, see Target 1) assert on the
  recorded gh call *arguments*, not counts — P1-P4 and P6 are all discriminating; P5 is the one
  exception flagged above.
- T-03's new case asserts `project_item_add`/`project_field_set`/`project_field_options` call
  arguments against both boards, including a negative assertion that B's board number never appears —
  discriminating.
- The Q2 fix's reconstruction is the most rigorous of the four: it captures the exact `str(e))` output
  before and after the one-line string edit and shows the substring assertion would have failed on the
  three-field message and passes on the four-field one — as clean a proof as a two-line diff gets.

## Target 4 — T-10 docs record

- `DECISIONS.md` carries `DEC-174 amendment 2` (`grep -c` confirms) and `per repository served`
  (confirms DEC-186 amendment landed, not just its index row) — both read in full; the prose
  accurately restates what the tree now does (per-repo board, rejection of a leftover top-level key,
  kaya-ai paired with board 2, the rename-not-recreate cost story) and does not touch the original
  DEC-174 am.1 or DEC-186 text, consistent with append-never-rewrite.
- `DECISIONS-INDEX.md`: re-ran `gen-decisions-index.py --stdout | diff -q -` against the committed
  file — **exact match**, so the am-span (`am.1-am.2` on DEC-174, `am.1` on DEC-186) is genuinely
  computed, not hand-typed. Both the DEC-174 and DEC-186 rows independently carry the literal phrase
  `per-repository board`.
- `SPEC.md`: the two table rows match the T-10 intent exactly (`board_for`/`board_station` replacing
  `station`, no fleet-level board framing). The diff also touches the onboarding-sentence paragraph
  below the table, which the task intent explicitly restricted against ("nothing else in that file").
  I traced this through the documentor's own receipts: it was raised as an open question in receipt 1
  (the sentence would otherwise be left false — onboarding is no longer "one edit" with just
  `name`+`default_branch`), then explicitly dispatched as a fix in receipt 2, and a follow-up gap in
  the *same* sentence's board-field list at `SPEC.md:415` (missing `owner`) was caught and fixed in
  receipt 3. This is disclosed, tracked scope widening through the normal open-question channel, not
  silent drift — not a finding.

## Not re-raised (per the dispatch's already-settled list)

Step 6 rebind, fail-open sweep, rejection fixtures' own-fleet construction, no shell injection,
SC-11/SC-12 greps, SC-13's BRIEF rationale, D-08's empty-Ready correctness, DEC-186 am. vs strike — all
independently spot-checked in the course of this review and none contradicted.

```yaml
VERDICT: PASS
DIGEST:
  headline: Spec compliance is clean across all eleven tasks; one test (P5, de-dup) doesn't prove what its own comment claims, but nothing gates.
  severity_max: med
  findings: 1
  must_fix: []
  spec_violations: []
  reviewed: "a7c429c..ec195ec06419eb7a2d47ed3eebab5145c346140c"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/features/FEAT-16-factory-per-repo-board/notes/review-harness-code-reviewer-c0.md
```
