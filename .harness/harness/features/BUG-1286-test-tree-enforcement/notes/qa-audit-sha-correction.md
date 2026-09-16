# QA — Audit SHA Correction (BUG-1286 T-04)

**BLUF: PASS.** Line 3's orphaned provenance SHA `5f76d6b1…` was replaced with its post-rebase twin
`4b343d8083d94d97477d3f2ebd7b848e83f01871` — the ancestor confirmation, subject match, and
`--against` re-measurement all held, both T-04 verify runs exit 0 pre- and post-edit, the fence
count is unchanged (2/2), and the diff touches exactly one line in exactly one file.

## Diff (one changed line, one file)

```
-BLUF: at commit 5f76d6b139c9cd5fc3cc7d4011f063335210cb8e, ...
+BLUF: at commit 4b343d8083d94d97477d3f2ebd7b848e83f01871, ...
```
(full diff run: `git diff -- .../notes/qa-tree-audit.md`; only the `@@ -1,6 +1,6 @@` hunk, one `-`/`+` pair.)

## Fence count

`grep -c '^```' <note>` — **before: 2, after: 2** (opening line 7, closing line 94; unchanged).

## Three required confirmations (all performed by me, pre-edit)

1. **Ancestry.** `git merge-base --is-ancestor 4b343d8083d94d97477d3f2ebd7b848e83f01871 9adbce6b` →
   `exit=0`.
2. **Subject match.** `git show -s --oneline 4b343d8083d94d97477d3f2ebd7b848e83f01871` →
   `4b343d80 BUG-1286: add the tree-audit census subcommand [harness:t-03]`. The orphan object is
   still reachable (not pruned) and shows the identical subject:
   `5f76d6b1 BUG-1286: add the tree-audit census subcommand [harness:t-03]`.
3. **Measurement holds at the new SHA.**
   `python3 tests/manual/suite-census.py tree-audit --ref 4b343d8083d94d97477d3f2ebd7b848e83f01871 --against .../qa-tree-audit.md`
   → exit 0, full row list printed (TOTAL 85 OUTSIDE 9 VIOLATIONS 0), **no MISSING or EXTRA row**.

## T-04 verify clause — run verbatim, both refs, before AND after the edit

Clause cross-checked against `plan.yaml` T-04 (line 998) — identical to the dispatch string.
Captured status is via `$?` immediately after the compound `out=$(...) && printf ... | grep -q ...`
command — `grep -q` is the last element in the chain, so this is its exit status, which is also the
overall chain's status since nothing follows it:

| When | `--ref` | captured exit |
|---|---|---|
| before edit | `HEAD` | 0 |
| before edit | `4b343d80…` | 0 |
| after edit | `HEAD` | 0 |
| after edit | `4b343d80…` | 0 |

## `git status --porcelain` (captured right after the edit, before writing this artifact)

```
 M .harness/harness/features/BUG-1286-test-tree-enforcement/feature.json
 M .harness/harness/features/BUG-1286-test-tree-enforcement/notes/qa-tree-audit.md
?? .harness/harness/features/BUG-1286-test-tree-enforcement/notes/answers-2026-09-05-budget-c11.md
```

Only `qa-tree-audit.md` is my change. `feature.json` (modified) and
`answers-2026-09-05-budget-c11.md` (untracked) were both present before I touched anything —
pre-existing state from prior seeding, not written by this run. This artifact
(`qa-audit-sha-correction.md`) and my observations log are additional untracked files this run adds
under `notes/`/`observations/`; they postdate the porcelain capture above so they don't appear in it.
HEAD unchanged: `b86498a0`. Nothing staged, nothing committed.

## `.claude/skills/harness/bin/suite_layout.py` / `tests/unit/test-suite-layout.py`

Not opened, not touched — concurrent engineering run owns these; irrelevant to this task.
