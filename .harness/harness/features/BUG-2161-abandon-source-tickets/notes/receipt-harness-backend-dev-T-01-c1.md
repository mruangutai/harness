# Receipt — harness-backend-dev — BUG-2161 T-01 (cycle 1)

BLUF: `abandon --close-sources --yes` now disposes plan.yaml sources through the existing planner/executor; unopened and already-abandoned records finalize locally. Signed verify exits 0, no FAIL, 22 s. No intent/files/verify amendment was needed. SC-07 is operator-only post-merge and is NOT claimed.

Commit: the commit carrying this file (`git log -1 --format=%H -- .harness/harness/features/BUG-2161-abandon-source-tickets/notes/receipt-harness-backend-dev-T-01-c1.md`); subject `[harness:t-01]`, same trailer.

## Verify (byte-for-byte as plan.yaml T-01)

```
python3 tests/unit/test-gh-sync-abandon-sources.py && python3 tests/integration/test-gh-sync-abandon.py && python3 tests/integration/test-gh-sync-ship.py
```

Run from PRODUCT root after the change: exit 0, elapsed 22 s (< 60 s), zero `FAIL` lines.

|Runner|Result|
|---|---|
|tests/unit/test-gh-sync-abandon-sources.py|20 PASS, 0 FAIL, `ALL PASSED`|
|tests/integration/test-gh-sync-abandon.py|160 ok, 0 FAIL, `ALL PASSED` (93 pre-existing + 67 new checks; 37 of the new ones were red pre-change, 30 were pre-change-green guards/positive pairs)|
|tests/integration/test-gh-sync-ship.py|78 ok, 0 FAIL, `ALL PASSED` (unchanged)|

Discovery: the two edited/new runners are standalone scripts (no collector); counts above are the printed PASS/ok lines.

## Red-first evidence (captured before any production edit; gh-sync.py unmodified)

Pre-change the CLI does NOT reject `--close-sources` on `abandon`: `main()` leaves unknown flags in argv and ignores them, so every integration failure on the abandon path is SEMANTIC (missing behaviour), not an unsupported-option error. The unit tests call `cmd_abandon(close_sources=...)`/`_abandon_plan(rec, sources)`, so there the unsupported option surfaces as `TypeError`, labelled `UNSUPPORTED-OPTION` in the failure detail.

Unit (re-captured with the final test file against stashed pre-change gh-sync.py, hash-verified restore): 3 PASS / 17 FAIL.
- UNSUPPORTED-OPTION (13): AS-01, AS-04, AS-05, AS-06, AS-07, AS-10, AS-12, AS-14, AS-15, AS-16, AS-17, AS-18 plus AS-02 (planner TypeError).
- SEMANTIC, missing behaviour (4): AS-13 (unopened `--yes` prints `gh-sync: SKIP — no recorded milestone or issues`, no station, no prune), AS-19 (same early skip), AS-03 and AS-08 (planner/board assertions that depend on the missing source plan).
- Pre-change PASS (regression guards, positive pairs): AS-09 (`--yes` without the flag disposes parent and task, touches no source), AS-11, AS-20.

Integration (37 FAIL / 123 ok pre-change), all semantic: two-source disposal (close, backlog-after-close, label, original body-file path, per #51/#52 separately), dry-run source lines, dry-vs-real number list, `[--close-sources --yes]` combo, unopened + plan-only sources + stale mirror, unopened `--yes` (local finalization), unopened dry run, already-abandoned absent/retained runs/, failed close, failed comment+label, and `--close-sources` rejection on ship/reject/open/status/recover-terminal. Pre-change PASS (guards): neither-flag, `--yes`-only and `--close-sources`-only combos, no-sources, #99 stale-mirror untouched.

## Named new cases

Unit (tests/unit/test-gh-sync-abandon-sources.py): AS-01..AS-20 — planner source inclusion and dedupe against parent/task; executor passes the unchanged reason-file argument to every comment; `cmd_abandon` dry run, flag matrix, second active feature citing the same source (only this plan's sources targeted, neither feature's bytes mutated), plan.yaml over stale mirror, unopened, re-entry, failure continuation, reporter honesty, legacy direct-caller signature. No corpus-lookup detector exists or is asserted.

Integration (tests/integration/test-gh-sync-abandon.py, BUG-2161 block): two-source disposal, dry-run (every byte of the feature dir preserved), dry-vs-real list, four flag combinations, no sources, unopened (plan-only sources + stale mirror; bare `--yes`; no sources; dry run), station-before-prune, already-abandoned (no rewrite by bytes + mtime + stdout; absent and retained runs/; no-flag no-op), failed source close, failed source comment and label, `--close-sources` rejection on other subcommands (exit 1, zero gh calls, zero byte change). Existing parent/task disposal and reject cases retained unchanged.

## Architecture change summary (for lead assessment)

Seam unchanged: `_abandon_plan` / `_apply_abandon_plan` / `cmd_abandon` in .claude/skills/harness/bin/gh-sync.py. No new adapter, command, resource or lifetime.
- `main()`: strips boolean `--close-sources`; refused (exit 1, before config load or any gh call) unless `cmd == "abandon"`; threaded to `cmd_abandon(..., close_sources=False)` (false default for direct callers). Usage lines updated (header docstring, die usage).
- `_abandon_plan(rec, sources=())`: sources appended LAST as `source_comment` + `source` entries; a source equal to the parent or a task issue is not planned twice. Dry run and executor walk this one list.
- `cmd_abandon`: sources come from `parse_source_issues(feat_dir)` only when `close_sources`; the unopened-mirror early `skip()` removed; `ensure_labels` only when the plan is non-empty; `_record_station` guarded by `_feature_station(feat_dir) == "abandoned"` (re-entry does not rewrite); `_prune_abandoned_runs` still follows the station. Dry run adds `would record the feature station abandoned` when not already abandoned. Source disposal is never refused for an already-abandoned station.
- `_apply_abandon_plan`: `_ABANDON_COMMENT_TARGET` maps `comment`->parent, `source_comment`->source; `parent` and `source` kinds share `close_and_reseat` (close not_planned, then Backlog, then label).
- `_post_abandon_reason(..., what="parent")` and `_report_abandon_gaps` generalized in place: "reason posted/not posted on {parent|source} #N"; the "no parent recorded — reason not posted" line now prints only when the plan has NO comment target at all (prior-receipt A-2 fold-in).
- Unchanged: gh-close-gate.py (its printed abandon usage line is unchanged), reject, ship, feature.json mirror, plan.yaml, BRIEF, T-02 documents.

## Notes for the lead / reviewer

- Decision (cheap, reversible): sources are planned after the parent close, comment before close per source, mirroring the parent's comment-then-close order. Not fixed by the signed intent.
- Decision: a source number already planned as the parent or a task is skipped to avoid a double comment; not in the signed intent, covered by AS-03.
- Dry run additionally prints one local-only `would record the feature station abandoned` line.
- Control-plane stash list holds 7 pre-existing stashes (not mine); my temporary stash was popped and the gh-sync.py hash verified identical.
- Code-risk grading (`code-grade.py`) was not run: assignment forbade checks beyond red-first runs and the signed verify.
