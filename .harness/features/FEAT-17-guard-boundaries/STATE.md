# STATE

## Current

- feature: FEAT-17-guard-boundaries
- branch: feat/FEAT-17-guard-boundaries
- status: Building
- review_sha: 2e02cfc
- run: .harness/features/FEAT-17-guard-boundaries/runs/2026-08-12-08-goalcheck-product/digest.md

GOAL-CHECK RUN. All seven tasks are done and committed; the four gates are green. EIGHT of ten
success criteria are met. The feature is NOT ready for Review — two criteria are outstanding and
neither is mine to close.

SC-07 is NOT MET, and the gap is a missing TEST, not a broken guard. SC-07 requires an allow into
<root>/.claude/worktrees/wt/.harness/allowed/x.txt reached FROM OUTSIDE that worktree, through
DEC-143's prefix stripping. Verified at source: in both suites `legit` is only ever used as the
SESSION ROOT — test-check-domain.py:1547 and test-bash-write-guard.py:372 both call _fire(legit, …),
and SC-06's mutation case pins the root inside it too. From inside, no prefix stripping happens, so
the mechanism SC-07 names is exercised by nothing. pm probed both routes directly and both exit 0,
so the guard is correct and one test per route is owed. No plan task ever instructed this test.

SC-07's OTHER clause IS met, confirmed by my own diff of 52ee5db..HEAD rather than by anyone's note:
no pre-existing expected exit code changed VALUE in either test file. The single removed
expected-code line is the (rel, want) loop in test-bash-write-guard.py's run_t14 block, where a
pair was ADDED — src/main.py, 2 — while
both pre-existing pairs kept 0 and 2, which is exactly what T-03's intent instructed.

SC-09 is ruled SUPERSEDED by pm and needs the operator's decision. Both halves, neither absorbing
the other: the LETTER fails — notes/worktree-list-before.md and -after.md do not exist and
`git log --all` shows neither was ever committed on any branch, and SC-09's paired negative was
destroyed by the FEAT-13 close-out. The INTENT holds — T-06's verify clause runs verbatim at exit 0:
no out-of-place worktree remains, archive/worktree-r6 preserves 52d8334 which is not an ancestor of
main, and the receipt names LATE, the tag and the word sweep. NOTHING WAS MANUFACTURED, which was
the binding instruction.

THE OWED SC-07 WORK IS NOT DISPATCHABLE BY ME. Both test files are `lane: main-session-direct` in
plan.yaml's lanes block, DEC-174 carve-out, because they co-change with the guards they assert
against in the same diff a human reads. So there is no fix cycle to route to a lead, and
cycles_used stays 6 of 10 — no rework was re-dispatched. Runs 8 of 20.

## Open Questions

- Q1 BLOCKING. SC-09 cannot be met as written. Accept `superseded` on the record, or amend the SC to
  cite notes/worktree-removal-receipt-2026-08-12.md? The signed BRIEF still names two files that
  never existed. pm left the prose standing, correctly — editing a signed artifact is a
  re-signature, not a record correction. Operator's call.
- Q2 SC-07's owed test is main-session-direct under DEC-174 and therefore the operator's to execute,
  not mine to dispatch. Add on each route a case with the session root at <root> writing to
  <root>/.claude/worktrees/wt/.harness/allowed/x.txt, expecting exit 0.
- Q3 Backlog: both guard suites sit in run-unit-tests.sh INTEGRATION_SCRIPTS despite matching the
  unit glob, so --kind unit never runs them.
- Q4 Backlog: bash-write-guard.sh resolves RELATIVE operands against the harness root rather than
  the agent cwd. Untriaged.
- Q5 plan.yaml's T-07 intent cites check-domain.sh line 676; verified rotten, the gate is at line
  534. DEC-193 quotes the condition not the integer, so the shipped doc is unaffected. pm's to fix.

ANSWERED and struck: INV-25 severity — remains a FAILURE, not a warning (operator, 2026-08-11).
