# SIMPLIFICATION angle — BUG-1309-mirror-build-entry

BLUF: one finding, low-risk, applicable — a byte-identical error string duplicated
across two branches inside `merge-gate.py`'s new `main()`. Everything else read
(the `gh-sync.py` Build-entry recorder, `_build_entry_preflight`, the two
`recover-terminal` helpers, `_open_ensure_labels`, `feature_schema.recovery_command_for`,
the `check-state.sh` INV-37 block, `post-merge-sweep.sh`'s retention branch, the four
hook-registration sites) reads as anchored: every conjunct I traced back to a distinct,
documented reason (`skip()`'s four-clause guard, `_recover_terminal_conflict`'s single
refusal, `recovery_command_for`'s three fail-safe checks), and every `(T-NN, BUG-1309)`
comment matches this file's 51 pre-existing citations of the same style — established
convention, not narration-of-the-diff noise.

## Finding 1 (highest value, and the only one)

- **File · line**: `.claude/skills/harness/bin/merge-gate.py:128` and `:137`
- **Summary**: `main()` prints the exact same f-string (`"merge-gate: could not verify
  this merge - the head branch could not be resolved through gh ({failure}) and the
  local branch {branch} owes no build-entry receipt; allowing it, because GitHub is a
  mirror and never a gate (DEC-138)."`) from two different branches of the same
  function, byte-for-byte identical, verified with `grep -n "could not verify this
  merge"` (two hits, one string).
- **Concrete cost**: this is new code introduced by this diff (`merge-gate.py` is a new
  file in this feature), so the duplication is not inherited debt — it is added by the
  change under review. A future wording edit (this message already went through
  adversarial review once, per DEC-138 framing) has two call sites to update in lockstep;
  the second one, 9 lines further down inside the `entry in {"opened", ...}` branch, is
  the one an editor is likely to miss because it reads like a different case.
- **Alternative**: factor the `if failure: print(...)` pair into one helper, e.g.
  `_allow_unverified(branch, failure)`, called from both the `document is None` branch
  (line ~127) and the `entry in {"opened", "not-applicable", "recovered-terminal"}`
  branch (line ~136), each still followed by its own bare `return`. This does not touch
  `main()`'s branching or its ordered exits — it only removes the second literal copy of
  the string — so it does not reopen the accepted grade-2 reason on `main()` (token
  scanning/orchestration branch count is unchanged; this is a leaf substitution).
- **What it does NOT change**: `tests/integration/test-merge-gate.py`'s T-05 checks
  (`"could not verify" in r.stderr` / `not in reason`, lines 103 and 108) assert a
  substring, not object identity or line count, so they pass unchanged after the
  extraction. No test asserts the two call sites are textually distinct. No `verify:`
  clause depends on the duplication itself. This is the one finding I'd rank for the
  single-fix ceiling: it is mechanical, in code this feature added (not inherited), and
  provably behavior-preserving against the existing test's exact assertions.

## Skipped, not findings

- `gh-sync.py`'s `skip()` four-clause guard (`feat_dir is not None and not
  remote_written and build_entry is not _NO_RECORD and os.path.isfile(...)`) — each
  clause is independently load-bearing per its own docstring paragraph (un-onboarded
  tree, remote-already-written funnel, explicit-silence sentinel); none can be dropped
  without changing which case it degrades.
- `_build_entry_preflight`'s two `entry is None` checks — the second is reachable only
  after the first's stricter (`and not exempt`) condition has already caused an exit via
  `refuse()` (`sys.exit(2)`), so they are sequential states, not a duplicated test of the
  same fact.
- The near-identical "predates the build-entry receipt" notice repeated across
  `gh-sync.py`, `merge-gate.py`, and `post-merge-sweep.sh` — this crosses three files and
  is a shared-authority question (one rule, three homes), which is the ALTITUDE angle's
  territory, not SIMPLIFICATION's.
- `merge-gate.py main()` and `check_state.sh` INV-37 — no conjunct or branch found that
  can be cut without changing a decision; the two accepted grade-2 functions in scope
  (`merge-gate.py main`, plus the case functions named as settled) were not touched
  beyond the one leaf-level string dedup above.
