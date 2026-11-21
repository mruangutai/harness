# Red-first — validate c1 fix, F2 (T-01 core): verify-receipt checks the COMPLETE destination

Slice owner: MergeGate. Files: `.claude/skills/harness/bin/expertise-merge.py`,
`tests/integration/test-expertise-merge.py`, `tests/unit/test-expertise-ops.py`. Not committed.

Command: `python3 tests/unit/test-expertise-ops.py && python3 tests/integration/test-expertise-merge.py`

## RED — new tests against the unchanged expertise-merge.py (HEAD 8cddd8cd)

- Unit: `FAIL test-expertise-ops.py`, 194 PASS / 1 FAIL — `case_u43_write_chain: completed without raising`
  (`_write_chain` did not exist). Log `/tmp/f2225-f2/red-unit.txt`.
- Integration: `FAIL test-expertise-merge.py`, 358 PASS / 3 FAIL. Log `/tmp/f2225-f2/red-int.txt`:
  - `verify full: receipted P-01 add plus unreceipted deletion of pre-existing G-01 refuses` (the finding's counterexample: verify-receipt exited 0)
  - `verify full: receipted add plus unreceipted edit of another entry refuses`
  - `verify full: unreceipted G-01 deletion BEFORE the receipted add refuses`

The new guard `supersession: replacement verifies its complete destination with no --base (superseded write honoured)` already passed against the old code. Its job is to stop the fix from refusing a legitimate superseded history.

## Fix

`verify_receipt` keeps every earlier check and its exit-code/output contract (exit 0 + same JSON; refusals exit 15 with lines on stdout). After the existing final-effect comparison, `_refuse_unreceipted_content` adds three requirements:
- The file's current sha256 must be the last link of the destination's recorded write chain (`_write_chain`): each step takes the latest unused batch whose `after_sha256` equals the current link, then moves to that batch's `before_sha256`. Superseded batches count as writes because they did land, and a replacement's `after_sha256` is already the authorized reconstruction.
- The chain must pass through a committed state (`_anchor_states`): the destination at `HEAD`, or "absent" when HEAD lacks it. With `--base`, the base blob is also accepted.
- Every active batch of the caller must lie on that chain.

Otherwise it refuses with 15: `UNRECEIPTED CONTENT <rel>: the file (sha256 …) is not the recorded result of its receipted writes onto the committed base`.

No `--base` is required, so validate-digest's existing call (no `--base`, live yield and durable close) gets the full-content check unchanged.

## GREEN

Same command: exit 0. Unit `PASS test-expertise-ops.py` (198 PASS); integration `PASS test-expertise-merge.py` (362 PASS, 0 FAIL). Logs `/tmp/f2225-f2/green-unit.txt`, `/tmp/f2225-f2/green-int.txt`.

## code-grade (path mode)

Every function I touched or added is at or above the bar:
- Production (bar 4): `_recorded_batches` 4, `_chain_step` 5, `_write_chain` 4, `_committed_state` 5, `_anchor_states` 5, `_refuse_unreceipted_content` 4, `verify_receipt` 4.
- Tests (bar 3): `case_verify_complete_destination` 4, `_complete_fixture`/`_verify_full`/`_refuses_unreceipted`/`_check_tamper_after`/`_verifies` 5, `_check_supersession_verification` 4, `case_u43_write_chain` 4, `_write` 5.

The remaining FAIL rows in these files are pre-existing legacy functions I did not touch (`parse_expertise`, `compute_union`, `cmd_apply`, `case_u23`, cases 3/9/13/14/17/19).

## Known boundary

The chain anchors on the committed state. So an unreceipted edit that has already been committed at HEAD is not caught here; the merge-time `replay --check` blob comparison catches it. A file rewritten by a mutating `replay` onto a new main no longer chains to its receipts either. After that, the merge path (`replay --check`, merge-distill) is the verifier.
