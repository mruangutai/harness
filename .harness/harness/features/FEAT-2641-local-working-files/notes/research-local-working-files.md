# Research — FEAT-2641 local working files (pm, plan-product, at e2bffca0)

BLUF: nine main-session-direct tasks (DEC-174) remove every CI reader of notes/runs/observations,
add one cleanup routine with four callers, and strike DEC-257. Every grilling "Not yet specified"
item is resolved as a plan decision (D-03..D-08); three consequences go to the operator (OQ-01..03).

## Measured (worktree e2bffca0; control plane 0b5aa6e4)
- Tracked working files: 2,750 — harness 1,739 notes / 744 runs / 45 observations; kaya 215 / 6 / 1
  (`git ls-tree -r e2bffca0`). `.harness/notes/` has none tracked.
- check-state rows reading notes/runs/handoffs: INV-7 (evidence part), 8, 12, 15, 16, 17, 18, 36,
  43, 46, 47, 51, INV-40(c) (`check_state/table.py` INVARIANTS). INV-37 reads only feature.json.
- `seam_era_start` is read only by INV-43 (`check_state/ctx.py`); kept declared (D-09).
- `feature-worktree.py remove` GATE 2 uses `git status --porcelain`, which omits ignored files, and
  `git worktree remove` deletes ignored files silently — so without D-08 an ignored notes/ dies with
  the tree. The post-merge sweep removes a worktree once the station-done record lands
  (`post-merge-sweep.py`, `worktree_terminal.classify`), before distill.
- No skip-distill path exists anywhere (rg over .claude, .omp, DECISIONS.md) — D-05 adds
  `feature-worktree.py clean`, refused below a terminal station.
- `gh-sync.py ship` runs in the main checkout or a plain clone (it refuses worktree paths), where an
  untracked `notes/handoff-validate.md` never exists; D-07 reads the validator PASS from feature.json.
- merge-distill replays from `--root` (the live worktree) and checks `git status --porcelain --
  .harness`, which ignores ignored files; the only receipt git read is `pr_receipt_paths`'s
  `git ls-tree` base exclusion (`expertise-merge.py`), dead once receipts are never committed.
- DECISIONS.md has no `notes|runs|observations/...:<line>` anchors, so `check-decision-anchors.py`
  is unaffected by untracking.
- `git rm --sparse` exists (git 2.54); the feature worktree is sparse, so T-01 uses it. Not executed:
  bash-write-guard refused a scratch-repo experiment.
- Product docs: `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` are absent in this
  checkout (docs/ holds PRINCIPLES.md and invalid-states-audit.html).

## Grilling "Not yet specified" → resolution
| Item | Resolution |
|---|---|
| Receipt replay state | D-04: receipts local; replay reads local notes; already-applied = merged main + cleanup deletion |
| Evidence references into notes | D-03: write-time checks kept; recorded path+sha is provenance only |
| Uses needing a committed home | D-03: none; feature.json/plan.yaml already hold the decisions |
| Worktree removal vs working files | D-08: remove refuses while untracked working files remain |
| Distill run identity | D-04: feature.json runs[] (committed) + local run dirs read at runtime |
| Project-note ownership | D-06: feature.json `project_notes` via `feature-record.py project-note` |

## Gate states between tasks (P-07)
CI sees only the PR head. Locally, check-state reads disk, so T-01's untracking changes no row's
input; T-02 removes rows before T-04 deletes `run_evidence_problems`; T-03's GATE 2b ignores
tracked files, so sweep fixtures that commit notes stay green until T-05 rewrites them; registries
(canonical-reader classification, shard durations) are reconciled once, in T-09.

## Open
- OQ-01 ship precondition replacement (D-07) vs plain deletion; OQ-02 pending distills of shipped
  features (BUG-2451, FEAT-2557, BUG-2565, BUG-2566, FEAT-2581 show no distill commit in the last
  60 commits of origin/main); OQ-03 in-flight branches still tracking working files.
- `notes/research-FEAT-2641-plan-proposal.md` is the proposal file `plan-merge.py apply` read;
  plan.yaml is the record.
