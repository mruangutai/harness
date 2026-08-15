# Operator answers — a1fix-eng — 2026-08-09

Relayed by the main session. The operator read all five questions and ruled on the four
blocking ones in one pass.

## Q1 — Cycle budget: 12 of 10

**Raise `max_total_cycles` to 12.** The operator accepts your count as honest, including
your decision NOT to charge the lead's second send-back. Write the raise into
`feature.yaml`; DEC-157 requires a per-feature raise to be recorded there as a user
decision, and this note is that decision.

The operator had already asked for 12 earlier in the session, before your segment
returned. The main session did not write it, because you owned the file.

## Q2 — `_validate_stations` is beyond the signed plan

**The run digest stands as the record. Do not amend `plan.yaml`.**

The behaviour ships. You declared it rather than slipping it in, and
`runs/a1fix-eng/digest.md` documents both the addition and the reasoning. That is
sufficient. No D-NN amendment.

## Q3 — The disclosed instruction violation (carried from panel2)

**Accepted. File nothing.**

Panel2's qa agent edited `check-state.sh` in a throwaway worktree, then restored it and
verified the tree clean, and it disclosed this itself. Nothing reached the tree. The
operator accepts the disclosure and closes the question.

## Q4 — `review_sha` is stale at 8bbb246

**Re-pin to a post-fix commit. Re-run nothing.** Your recommendation, taken.

The A1 fix carries the strongest verification evidence in the feature — red proven by
injecting the pre-fix module (17 of 172 failing, including the three that match the live
typo run), then green at 22 test files with 0 failures. The panel already passed the
rest. A second panel would spend budget the operator is raising for the fix itself.

## Q5 — Live re-run against a real repo (not blocking)

**Still open. Do not act on it.** It needs a throwaway repo and a fresh board, which is
the operator's to authorize, and the last one required a `delete_repo` scope refresh to
clean up. The main session raises it at the ship decision, not now.

## Two things the main session owns, so you do not duplicate them

- `bf8f191 [harness:human]` — the `check-state.sh` fixes, committed directly under the
  DEC-174 carve-out while your segment ran. Two crash fixes, four INV-24 defects, and
  INV-15 now imports `validate-digest.py` once instead of forking 103 times. Your
  observation that `check-state.sh` exits 0 with zero violations is that commit's effect.
  Do not touch `check-state.sh` or `test-check-state.py`.
- Issues #203 and #204, both filed and on the board, both blocked on FEAT-10 shipping.
  Neither is your work.
