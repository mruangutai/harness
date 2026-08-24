# research — source_issues on FEAT-35's plan.yaml — 2026-08-24

**BLUF.** `source_issues: [751]` is now a top-level key on FEAT-35's plan.yaml, added add-only via
plan-merge (exit 0, diff is `1 insertion, 0 deletions`). The chain the dispatch asked me to
re-derive HELD. **But the edit alone does not make `closes` emit** — `closes` reads the mirror in
feature.json, not plan.yaml, and that mirror is still `[]`. A `gh-sync.py open` re-run is required
before the PR body can be composed.

## Precondition

`grep -n source_issues plan.yaml` before the edit: no match, exit 1. Nothing was overwritten.

## The chain, re-derived from source

- `parse_source_issues(feat_dir)` reads plan.yaml's own top-level `source_issues`
  (`gh-sync.py:332-356`). Absent key -> `[]`, never raises.
- `cmd_open` refreshes the mirror on EVERY run: `rec["source_issues"] = parse_source_issues(...)`
  (`gh-sync.py:705`), persisted by `save_recorded` (`gh-sync.py:784`).
- `cmd_closes` prints one `Closes #<n>` per entry — but reads `load_recorded(feat_dir)`, the
  on-disk mirror, **not** plan.yaml (`gh-sync.py:1054`, and the docstring above it says so
  explicitly: "the on-disk mirror, not plan.yaml, so what is emitted is what was recorded at open
  time").

So with the plan key absent, both the mirror and the emit were empty, and #751 plus #798-#802 would
have survived the merge. FEAT-33 (PR #785) was stranded by exactly this shape; diagnosed as #806.

## The gap this edit does NOT close

`feature.json` `github.source_issues` is `[]` at the time of writing. Running
`gh-sync.py closes .harness/harness/features/FEAT-35-orchestrator-stop-and-wake` right now prints
**nothing**. The plan is the truth; the mirror is stale until `open` runs again. This is by design
per the docstring, not a defect — but it is a required next step that the plan edit does not
perform, and skipping it reproduces FEAT-33's failure with a correct plan.yaml on disk.

## Verification performed

- grep after: `319:source_issues: [751]` — one line.
- `git diff -- plan.yaml`: a single `+source_issues: [751]` appended after the last task.
  `--numstat` = `1  0`. Deletion/modification lines matching `^-[^-]`: **0**, file-wide. The
  `approval:` block (lines 4-7) is byte-unchanged and is not adjacent to the addition.
- Re-loaded with `harness_yaml.load_plan`: parses; `source_issues == [751]`;
  `approval == {status: approved, approved_by: operator, date: 2026-08-23}`; 5 tasks, 9 decisions
  intact.

## Scope held

Only `751`. `#798`-`#802` are the task sub-issues covered by the parent; `#803`-`#806` are residual
findings filed from this feature. None added.

Not committed, not staged, HEAD not moved.
