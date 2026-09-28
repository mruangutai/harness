# FEAT-69 — build divergences (SC-02 ledger)

Source: the one clean-pin execution recorded in `notes/clean-pin-byte-receipts.generated.md` (implementation pin `db488aa7c78e392c788bd5839a43ebf4ba562ea1`, baseline `a726bad8f74d23e6c1f07409383bb88d1da8fbcf`). Normalisation: each checkout's absolute root → `<checkout>`, nothing else. Thirteen measurements; twelve identical; the full-table run differs in exactly the five lines of D-02 and D-03 below, quoted verbatim from the committed generated receipt's "exact lines" block (a `+` line is pin-only). D-01 was observed in the FIRST clean-pin execution (20:48:57Z–20:51:18Z, the same pin and baseline, superseded) and had resolved by the committed execution (T-04's verify re-runs the script; 20:52:45Z–20:55:06Z); it is kept here because it was measured, with the ruling that explains why it cannot recur from the split.

## D-01 — a foreign worktree's dirty state changed between the two executions of the FIRST run (environment, not the split; absent from the committed run)

```
-  VIOLATION  INV-29: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/perf-slow-tests is a standing worktree whose terminal status could not be determined — worktree path is not under WORKTREES_SEGMENT. A lookup that FAILED is not an exemption; the worktree is reported rather than passed over. The tree is dirty: `remove` will DECLINE until those changes are committed, landed or discarded. Its path did not resolve to a repository and id, so no removal command can be composed for it.
+  VIOLATION  INV-29: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/perf-slow-tests is a standing worktree whose terminal status could not be determined — worktree path is not under WORKTREES_SEGMENT. A lookup that FAILED is not an exemption; the worktree is reported rather than passed over. Its path did not resolve to a repository and id, so no removal command can be composed for it.
```

Ruling: not the split. INV-29 lists every live git worktree of the repository and reports `The tree is dirty: …` from a `git status --porcelain` in that worktree at run time. `perf-slow-tests` is another session's worktree (not under `.claude/worktrees/harness/`, so its terminal status is unresolvable at baseline and pin alike); between that run's baseline execution and pin execution — about seventy seconds apart — that session committed or discarded its changes, so the dirty clause dropped; by the committed run both sides read the worktree clean and the line is identical. The line is otherwise byte-identical, the INV-29 body moved byte-for-byte into `check_state/worktrees.py`, and `test-check-state-worktrees.py` (identical at baseline and pin) proves the dirty/clean clause on fixture repositories.

## D-02 — FEAT-69's own feature record exists only at the pin (four INV-32 notes)

```
+  note       INV-32: FEAT-69-long-file-check-state-package finding PF-c2128122a0bb540f061d16fb1410fe65 disposition resolved.
+  note       INV-32: FEAT-69-long-file-check-state-package finding PF-340baf59ff3499fe4a22647112179b9a disposition resolved.
+  note       INV-32: FEAT-69-long-file-check-state-package finding PF-8df76c10f1a644c190f4873f2bcb3ccd disposition resolved.
+  note       INV-32: FEAT-69-long-file-check-state-package finding PF-bc67c8325e2128cacd86013cfd559654 disposition resolved.
```

Ruling: not the split. The baseline commit predates the feature directory; the pin carries it, with the plan panel's four findings (all applied by the plan run, marked `resolved` at signature). INV-32 emits one note per resolved finding, as it does for every other feature with a resolved panel finding on both sides of the comparison (e.g. the BUG-1081 lines present in both runs).

## D-03 — FEAT-69's plan run directory is gitignored, so a clean checkout lacks it (one INV-8 note)

```
+  note       FEAT-69-long-file-check-state-package: run plan-product is referenced but its dir is absent (pruned, or never created).
```

Ruling: not the split. `.gitignore:7` excludes `.harness/*/features/*/runs/**`; `feature.json` records the `plan-product` run, so INV-8 notes the absent directory in any clean checkout of any feature with a recorded run — the same note FEAT-68's receipts ledgered for its own record (its D-01 class). The INV-8 body moved byte-for-byte into `check_state/feature_record.py`.

## Not divergences

- `full_table` exit status: 1 → 1 (the repository carries standing INV-29 violations from other sessions' worktrees on both sides; identical apart from D-01).
- `--list`, the nine suites, `feat62_findings`, `consolidation_findings`: identical bytes and exit statuses after the one normalisation (see the generated receipt's table).
- The canonical-reader audit (`--canonical-reader-audit`) is not an SC-02 measurement; its state is recorded in `notes/amendments-1-baseline.md` § 3 (exit 2 with 69 `PLAN AMENDMENT REQUIRED` rows at baseline and pin alike; six rows re-keyed in path only; one `T-05 task files omit` route line added for the re-keyed `station_of` row because the FEAT-61 inventory's route cites files FEAT-61's plan named).
