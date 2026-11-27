# FEAT-2458 cycle 1 — code review: FAIL

Pinned implementation: `322b12b0..9b5b6a7a05c3dc8aa382699e33477d2f0397281c`. Canonical grading/attribution base: `261fdf726428bd8325fbd3d4beccad23b67e83cc`; the difference between bases is feature records only. No tracked edits outside feature records. No open questions.

## Stage 1 — FAIL

- **SC-06 PASS (inspection)** — `.claude/skills/harness/bin/post-merge-sweep.py:341`, `_sweep_shape_stamps`: line 361 calls `worktree_terminal.classify_feature`; only `terminal` reaches unlink. The sweep reads no `plan.yaml`, `feature.json`, `BRIEF.md` or station itself. The plain stamp, empty suffix, symlinks and non-regular entries skip classification. Dry run does not unlink.
- **SC-08 PASS (inspection)** — `.claude/skills/harness/bin/worktree_terminal.py:7` names `CLASSES`, `classify`, `classify_all`, `classify_feature` and `repo_arg_for_segment`. `.claude/skills/harness/bin/post-merge-sweep.py:159` uses the shared helper; the duplicate and its stale public-surface claim are gone.
- **SC-07 static PASS** — `.claude/skills/harness/bin/check-plan-routes.py:970` and `tests/integration/canonical-reader-classification.json` no longer contain `post-merge-sweep.py::_repo_arg_for_segment::load_fleet#1`; the shared helper's inventory row remains (`:2108`).
- The normal SC-01–05 paths are present: exact harness/fleet matching, one `_landed_classification` call, and the decode catch limited to the single `cat-file` call (`worktree_terminal.py:213`, `:621–640`). Prefix-only ids do not borrow a verdict. An unresolved branch or a failed harness `ls-tree` returns unresolved before deletion. SC-07/09/10 runtime and fail-first evidence were not rerun here; build notes concern the same implementation (no code or tests changed after `1d8e8446`).

**Spec findings (substance):**

1. **T-01 · med · D-01/D-03** — `worktree_terminal.py:143–149,625–634` treats an unreadable fleet declaration as an empty fleet. If a registered fleet feature is landed at `done` but local `fleet.yaml` is unreadable, its stamp is kept with an *absent* reason rather than a fleet lookup failure. Likewise, a failed fleet tree read is silently skipped: with one visible done match and a second exact hit in the unreadable segment, the sweep sees a unique `terminal` result and removes the stamp without establishing uniqueness. Distinguish a missing segment directory from an actual read failure; do not report absence or uniqueness on incomplete lookup.
2. **T-01 · med · SC-01** — `worktree_terminal.py:479–482,637–639`: a landed plan with `status: absent` returns `unresolved`, but interpolation places `absent` in its reason even though the feature exists. A corrupt landed record whose id contains `absent` has the same problem. Preserve the shared terminal rule while keeping the absence marker exclusive to a confirmed miss.
3. **T-02 · med · SC-05** — `tests/integration/test-post-merge-sweep.py:1216–1220,1235–1242`: the wet/dry check for `absent` can pass on the stamp filename alone. The shipped predicate accepted `…FEAT-912-stamp-absent — unresolved: lookup failed` in an isolated string check. Assert `absent` in the reason, separately from the filename and one-line check.

## Stage 2 — qualitative review not opened after Stage 1 failed

The required pinned mechanical grade is **fail** (`code-grade.py` exit 1):

| Task | Function | Cyclomatic / cognitive / ABC | Finding |
|---|---|---|---|
| T-02 | `tests/integration/test-post-merge-sweep.py:1162` `case_shape_stamps` | 20 / 21 / 74.0 | substance · high: ABC drives grade 1, below test bar 3 |
| T-01 | `tests/integration/test-worktree-terminal.py:1106` `case_classify_feature` | 4 / 3 / 45.7 | substance · high: ABC drives grade 1, below test bar 3 |
| T-02 | `.claude/skills/harness/bin/post-merge-sweep.py:341` `_sweep_shape_stamps` | 11 / 20 / 24.4 | substance · med: grade 2 (cyclomatic/cognitive). Non-blocking: explicit file-type, outcome, dry-run and unlink-error guards keep the deletion preconditions visible beside the write. |
| T-01 | `.claude/skills/harness/bin/worktree_terminal.py:601` `classify_feature` | 10 / 16 / 24.0 | substance · med: grade 2 (cognitive). Non-blocking: the exact-id resolution branches keep harness precedence and fleet ambiguity ahead of the shared predicate. |

Split the grade-1 fixture setup and assertions into cohesive pieces while keeping the real Git and dry/wet coverage. No implementation files changed; no hook or integration suite executed in this review.
