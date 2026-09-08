# Stated intent — BUG-1480

**This is the operator's stated intent, recorded verbatim from the dispatch that opened this
feature.** There was no grilling or wayfinding session: the defect arrived fully diagnosed as
backlog row B-1 on the BUG-201 ship briefing
(`.claude/worktrees/harness/BUG-201-depends-on-integrity/.harness/harness/features/BUG-201-depends-on-integrity/notes/ship-review-2026-09-07-ship.md`),
and the operator's decision was about *how it lands*, not about what it is.

## What the operator asked for

> Implement and ship the prerequisite B-1: worktree handoff-note validation must resolve
> authorities relative to the feature's checkout rather than main checkout.

## The binding decision

> Fable advisor requires this as a standalone minimal BUG flow off `origin/main`, with its own PR,
> before reconciling BUG-1290 and merging BUG-201. No cherry-pick into BUG-201.

## The defect, as stated to the factory

> In `check-domain.sh`, the handoff_done_when path takes a checkout-relative path from
> `harness_boundary.checkout_relative` but discards the returned checkout root and passes the main
> root to `handoff_done_when.problems`, so worktree-only feature artifacts are unseen. Fix should
> carry `_ck[0]` into that call. Add a worktree-feature regression in `test-check-domain.py`.

## The constraints

> Create required issue/feature artifacts and worktree according to Harness BUG flow; use TDD; run
> only required focused verification plus QA/review/ship lifecycle. No formatters, linters, or
> unrelated project-wide suites. Treat fable-advisor as binding for non-external questions.

## The acceptance

> Merged PR on origin/main, issue closed, board Done, and B-1 verification/review records present.
> Return authoritative evidence or an external blocker.

## What is therefore OUT of scope, stated so a reviewer can hold the line

- Any other `_norm` caller, and any change to `_norm`'s own return contract.
- BUG-1290's five record violations, and the BUG-201 rebase — both named by the operator as
  separate, later work.
- Any broadening of the handoff validator's own rules (grammar, caps, satisfaction semantics).
- `bash-write-guard.sh`, which asks a different question against the same boundary module.
