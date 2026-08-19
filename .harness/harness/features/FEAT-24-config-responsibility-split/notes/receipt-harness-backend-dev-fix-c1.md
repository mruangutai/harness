# FIX-C1 receipt — harness-backend-dev

## Fix 1 — factory_gh.file_at_ref: query form, not `-f`

`.claude/skills/harness/bin/factory_gh.py:439` changed from

    argv = ["api", f"repos/{repo}/contents/{path}", "-f", f"ref={ref}", "--jq", ".content"]

to

    argv = ["api", f"repos/{repo}/contents/{path}?ref={ref}", "--jq", ".content"]

No other line in `file_at_ref` (429-463) touched. The docstring at 429-437 already said "ref as a
query parameter" — that sentence was false against the shipped `-f` argv and is now true; no text
edit was needed there.

`.claude/skills/harness/bin/test-factory-gh.py`, case `file_at_ref: hits the contents path with the
ref` (was two clauses, now four — both original clauses kept verbatim, two added):
  (a) ref rides in the SAME argv element as the contents path, WITH the `?` — `any("repos/o/r/contents/path/to/file.txt" in a and "?ref=main" in a for a in calls[0]["argv"])`.
      (Tightened once more after review: an earlier draft checked `"ref=main"` without the `?`,
      which a malformed argv like `.../file.txtref=main` would still satisfy.)
  (b) `"-f" not in calls[0]["argv"]`
Ok-line text unchanged: `file_at_ref: hits the contents path with the ref`.

### Reddening proof — Fix 1
- Recorded sha256 of `factory_gh.py` before mutating: `0ccddbb140f834207ad5a26167c49e20e1cf8e66409bbd31cd5dfb4912d50014`.
- Mutation: reverted line 439 to the shipped `-f` form.
- Ran `python3 .claude/skills/harness/bin/test-factory-gh.py`. Verbatim FAIL line:
  `FAIL  file_at_ref: hits the contents path with the ref`
- `grep -E "^FAIL"` on the full run showed exactly that one line — no other case reddened.
- Restored the query form; sha256 after restore matches the recorded hash exactly
  (`0ccddbb140f834207ad5a26167c49e20e1cf8e66409bbd31cd5dfb4912d50014`) — byte-identical.
- Re-ran the suite (with the final, `?`-tightened clause): `162/162 checks passed`, and the full
  T-01 verify block (all five `has` checks plus the FAIL-grep and `rc=0` check) passed as
  `T-01 GREEN`.

`run_gh` call sites at 237-240, 337-340 (graphql), 472 (`-X POST`), 486 (`-X DELETE`) left
untouched, per the dispatch's instruction. Confirmed with `grep -n '"-f"' factory_gh.py`: the only
`-f`-carrying call sites remaining are 237-240, 337-339 (graphql) and 472 (`-X POST`); line 486
(`delete_ref`) carries no `-f` at all. `file_at_ref` (439) is the only one that changed.

## Fix 2 — F-5: remote-fails-with-checkout-present case

`.claude/skills/harness/bin/factory_config.py` — UNCHANGED except for the reddening mutation,
which was reverted; final diff against HEAD is empty (`git diff --stat` shows no hunks for this
file). Confirmed by sha256: before mutating `ff0fc89ca2cd3b38a3e8917d36cd70b15045e84e89f54bf49518dce73361cb1a`, mutated,
reverted, after-restore hash matches exactly.

New case added to `.claude/skills/harness/bin/test-factory-config.py`, inserted between the
existing "(iii) never falls back to a checkout" case (513-526) and the "(iv) memoisation" case
(528+). Ok-line text (new, not colliding with any existing string):

    product_config never falls back to a checkout on disk when the remote read fails

Fixture: a fresh `tempfile.TemporaryDirectory()` pair (fleet dir + workspace root) not reused from
any earlier case; `_repo = "mruangutai/harness"`. A checkout is written to
`workspace_path(fleet, _repo)/.harness/harness.json` carrying `board_dict(777333)` — `777333` does
not appear anywhere else in the file (checked via `grep -n "board_dict("`, which lists only 2, 3,
9 elsewhere). `factory_gh.file_at_ref` is stubbed via `patched_file_at_ref` to append to a
`_stub_calls` list and then raise `GhError`. Assertion: `FleetError` raised (`_raised`), the stub
was actually invoked (`len(_stub_calls) >= 1` — this is what rules out "never called because a
prior case already cached the read"), and `"777333" not in _msg`. `got` is set to `None` on the
raise branch and printed in the failure detail alongside `_msg` and `_stub_calls`.

Memo-cache concern (point 1 of the dispatch): `check()`'s own docstring/comment
(test-factory-config.py:39-46) states it calls `fc.clear_product_config_memo()` as its FIRST
statement, so the PREVIOUS case's `check()` call already emptied the memo before this case's body
runs — confirmed by reading that block. The new case also uses a repo/ref combination
(`mruangutai/harness` @ the fleet's default `default_branch`) that, even if memoised by an earlier
case, would have been cleared by that earlier case's own `check()` call. `len(_stub_calls) >= 1`
is the empirical proof the stub fired regardless of the reasoning above.

### Reddening proof — Fix 2
- Mutation (applied to `factory_config.py`'s `product_config`, in the `except factory_gh.GhError`
  branch): if `os.path.join(workspace_path(fleet, repo_name), _PRODUCT_CONFIG_PATH)` exists on
  disk, read and return it instead of raising; only raise `FleetError` when no such file exists.
- Ran `python3 .claude/skills/harness/bin/test-factory-config.py`. Verbatim FAIL line:
  `FAIL  product_config never falls back to a checkout on disk when the remote read fails`
- Result line: `1 of 79 FAILING.` — exactly one case reddened, confirming the mutation's shape is
  correct per the dispatch's constraint #4.
- Cases that did NOT change: all 78 others, including
  "product_config reads the remote at default_branch with no checkout on disk" (case (i), nothing
  to fall back to — stayed green) and "product_config never falls back to a checkout" (case (iii),
  succeeding remote — stayed green, since the mutation only engages on the exception branch).
- Restored `factory_config.py`; sha256 after restore matches the recorded pre-mutation hash exactly.
- Re-ran the suite: `79/79 checks passed.`

## Full-suite red set (`.claude/skills/harness/bin/run-unit-tests.sh`, run from the worktree)

The runner itself exits 1 when any file fails (confirmed by reading its tail: `if [ "$failures"
-gt 0 ]; then exit 1; fi`), and the run's own captured exit code was `exit=1` — not 0. That is
expected given the reds below; it does not indicate a run that failed to execute.

Every FAIL line in the run, with the file it belongs to (the runner prints each file's own
`PASS test-X.py` / `FAIL test-X.py` header AFTER that file's case lines, so a block's file is
identified by the header that follows it — confirmed against `run-unit-tests.sh`'s loop, which
prints the header once per script after running it):

**test-no-distribution.py** (pre-cleared, operator's):
- `FAIL every_repo_declares_its_own_board repos entries with an invalid or missing board: ['mruangutai/kaya-ai']`
- `FAIL kaya_ai_is_paired_with_board_2 board 2 is the kaya-ai board — ...`

**test-check-state.py** — 7 case failures:
- `FAIL - case (a): INV-21 note appears when parent is unrecorded`
- `FAIL - (v.1) a mis-columned card is a VIOLATION naming feature, task, plan status and column found`
- `FAIL - (v.4) tasks in flight with an EMPTY issues map is a violation`
- `FAIL - (v.5) a recorded issue absent from the board is CANNOT VERIFY, not a clean pass`
- `FAIL - (v.6) the parent card disagreeing with the derivation is a violation`
- `FAIL - (v.8) a mis-columned done card is reported even when the plan derives NO parent station`
- `FAIL - (v.12) the same fixture with an EMPTY factory.issues still fires — the exemption keys on recorded issues, not the block`

**Flagging, not filing under "expected":** the dispatch's pre-clearance names `check-state.sh` (the
gate *script*) as red by design pending T-05's `derive_station()` arity fix. `run-unit-tests.sh`
never runs `check-state.sh` — it runs `test-check-state.py`, a different file, and the dispatch
does not name that file. I checked whether my two changed files could be the cause:
`grep -n "factory_gh\|factory_config\|file_at_ref\|product_config" test-check-state.py` returns
only two hits — a comment about `FACTORY_GH` (unrelated function/module names, not a call) and one
fixture line writing an unrelated `"nothing relevant\n"` string into a
`.claude/skills/harness/bin/factory_config.py` key of a fake-file dict. Neither is a call into
`file_at_ref` or `product_config`, so my changes cannot be the cause. This reads as the same
`derive_station()`-arity gap the dispatch names for `check-state.sh`, surfacing through its test
file too, but I did not verify that against a pre-fix baseline and am not asserting it as
pre-cleared. Raised as a non-blocking `open_question` below for the operator to confirm.

No other `FAIL` line appears anywhere in the run — confirmed with a widened
`grep -inE "fail|error|traceback|not ok"` pass over the full log; the only other hits are an
intentional fixture string in `test-factory-decompose.py` ("RuntimeError: boom, kill before any
edge" — a mock error message a test injects on purpose, not a failed assertion) and PyYAML
installation-comment lines. `test-factory-gh.py` (162/162), `test-factory-config.py` (79/79) and
every other file in the run report full passes. Re-ran the whole suite a second time after the
clause-(a) tightening; the red set was byte-identical both times.

## Decisions / refusals

- Did not touch `factory_config.py`'s production code beyond the reddening mutation, which was
  reverted — the dispatch is explicit the implementation is already correct.
- Did not add a new named case for Fix 1 — tightened the existing `file_at_ref: hits the contents
  path with the ref` case in place, as instructed (T-01's verify greps that exact ok-line, and a
  new case would be invisible to it).
- Did not touch `run_gh` call sites at 237-240, 337-340, 472, 486.
- No assertion was deleted or weakened in either file.

## Open question
- Q1 (non-blocking): the dispatch pre-clears `check-state.sh` red-by-design pending T-05, but
  `run-unit-tests.sh` runs `test-check-state.py` (a different file) and that file shows 7 case
  failures. My changed files are not referenced by any of those cases (grep evidence above), so
  they are not caused by this fix cycle. Is `test-check-state.py`'s red the same pre-cleared
  `derive_station()`-arity gap as `check-state.sh`, or a fourth, separately-tracked red?

## Files touched
- `.claude/skills/harness/bin/factory_gh.py`
- `.claude/skills/harness/bin/test-factory-gh.py`
- `.claude/skills/harness/bin/test-factory-config.py`
