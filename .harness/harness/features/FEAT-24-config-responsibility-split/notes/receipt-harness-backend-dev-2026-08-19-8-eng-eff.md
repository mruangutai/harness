# EFFICIENCY receipt — harness-backend-dev — FEAT-24 run 2026-08-19-8-eng

## HEAD check

`git rev-parse HEAD` = `3396b5e2bc7b9501c714fce23967adc8de6d74b6` — matches the dispatched
target. No mismatch.

## Findings

**None.** Every concrete concern named in the dispatch was checked and came back negative,
with measurement attached (below), not inferred from the call graph.

## What was measured

1. **check-state.sh session-entry path — no new network I/O.** `git diff ada8e99..3396b5e --
   check-state.sh` (lines ~1097–1284, the INV-26 block) shows `_gb.load_board(root)` still
   reads the LOCAL `root/.harness/harness.json` (`gh_board.py:44`, `os.path.join(root,
   ".harness", "harness.json")`) — it never routes through `factory_config.product_config`'s
   remote read. The diff only wraps the existing call in try/except for the new `FleetError`
   raise-on-unusable-board behavior (T-04) and renames the `_EXPECT` literals to read from the
   board mapping. The pre-existing `gh auth status` / `board_stations` calls inside
   `if _inv26_board:` are unchanged lines, gated exactly as before behind
   `github.sync is True and repo`. No new network read landed on this gate.

2. **`gh_board.py` import-time I/O — matches the documented "one `os.access` probe" claim,
   verified, not trusted.** Monkeypatched `subprocess.run` and `socket.socket.connect` to raise
   on any call, then `import gh_board` (which pulls in `factory_config` at module level):
   import completed with **zero** subprocess or socket calls. Import wall time ≈28ms, which is
   interpreter/module-load overhead, not I/O.

3. **`product_config`'s per-`(repo_name, ref)` memo — exercised empirically.** Monkeypatched
   `factory_gh.file_at_ref` with a call-counting stub and called `factory_config.product_config`
   three times for the same `(repo, ref)`: exactly **1** simulated network call, confirming the
   memo behaves as D-03/D-06 describe. Grepped every caller of `board_for`/`product_config`
   outside tests (`factory_land.py`, `factory_claim.py`, `factory_decompose.py`): each is a
   one-shot CLI invocation touching one repo; `factory_decompose.py` calls `board_for` once
   (line 329) and `board_station` again for the same repo (line 399) inside one process, which
   is exactly the memo paying off a real second call — not a new cost. No loop was found calling
   either function per-issue or per-task.

4. **`board-station.py` / `gh-sync.py` still use the local-read `gh_board.load_board`,
   never the remote `board_for`/`product_config` path** — grepped both files; only
   `factory_land.py`, `factory_claim.py`, `factory_decompose.py` import `factory_config` for the
   remote board. So the per-write-guard / per-sync-run hot paths carry no new remote read either.

5. **`factory_gh.file_at_ref` stays GET-only** (`factory_gh.py:439`, no `-X`, no `-f`) — the
   `-f` flags in the same file are on the GraphQL query calls (lines 237–238, 337–339), where
   POST is the correct method for `gh api graphql`, not the "`-f` silently forces POST on a
   REST GET" defect class named in the dispatch. No live defect of that shape found in the
   touched surface.

6. **The fake-`gh` blind spot the dispatch flagged (line-wrapped base64) is already covered.**
   `test-factory-gh.py:962-978` builds a fixture that line-wraps base64 at 60 chars with
   embedded newlines (GitHub's real shape) and asserts `file_at_ref` decodes it — this is not a
   gap left open by this diff.

## Suite

`bash .claude/skills/harness/bin/run-unit-tests.sh --kind all` — rc=0, zero `FAIL` lines,
wall-clock ≈78s (`1:18.36 total` per `time`). This full-suite run is a deliberate boundary-step
run (this is the last build step before `review_sha` pins), not waste — consistent with the
dispatch's framing, not flagged.

## Not re-litigated

D-01–D-10, the plan-surface F-1–F-9 findings, and anything in `DECISIONS.md`/
`DECISIONS-INDEX.md` — out of scope per the dispatch.

```yaml
VERDICT: PASS
DIGEST:
  headline: "EFFICIENCY angle on FEAT-24 diff ada8e99..3396b5e — empty return, every flagged concern measured negative"
  tests_added: 0
  suite: pass
  task: none
  blocked_on: none
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-24-config-responsibility-split/notes/receipt-harness-backend-dev-2026-08-19-8-eng-eff.md
```
