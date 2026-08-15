# Operator ratification — SC-12, 2026-08-15

**Ruling: the SC-12 deviation is RATIFIED — four commits, not two — CONDITIONAL on the
post-cluster commits containing no logic change, only code hygiene.**

The operator's words: "ratify. provided the logic has not changed, only code hygiene."

What the condition covers, stated precisely:
- `d033b9d` (the cluster) and `5afa7e3` (T-01) are the two commits SC-12 contemplated; the
  atomicity purpose — no landed commit shows a half-moved tree — is met by construction.
- `b1d3925` changes TEST logic only (case 20 compares against the real gate instead of a
  hand-written mirror); no production behaviour changes. The strengthening of a test is
  within the condition's spirit: the thing being shipped behaves identically.
- `4a98cc4` is comment-truth and lifecycle hygiene; the one code reshape (gh-sync's walk-up
  loop) must be semantics-identical — resolves the same root from both old- and new-depth
  feature dirs and falls back identically for un-onboarded trees.

**The condition's verification is delegated to the validator panel's confirmation pass**
(in flight at this writing, pinned at 4a98cc4, explicitly tasked with proving the walk-up
refactor changed no semantics and re-running the SC-10 mutation pair). If that pass finds
any logic change in b1d3925 or 4a98cc4, this ratification does NOT attach and the finding
comes back to the operator.

With the condition confirmed, SC-12 is closed as met-in-purpose, deviation ratified, and
FEAT-21 stands at 14 of 14.
