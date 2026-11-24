# FEAT-2458 shape-stamp sweep — ship review

**Recommendation: ship.** Validation passed at `f42393e2` on its second cycle, after one fix round
of the two you granted. All five readers pass, both perspectives pass the goal-check, and the
must-fix list is empty. Nothing blocks the merge; the merge is yours.

No report round was spawned. This briefing is assembled from the three digests on disk, all under
`.harness/harness/features/FEAT-2458-shape-stamp-sweep/`:

- `runs/2026-11-23-01-plan-product/digest.md` (plan, FAIL)
- `runs/2026-11-24-01-validate-validator/digest.md` (validate cycle 1, FAIL)
- `runs/2026-11-24-02-validate-validator/digest.md` (validate cycle 2, PASS)

The build has no digest: both tasks and the fix round were main-session-direct (DEC-174), recorded
in `notes/simplify-pass.md` and `notes/handoff-build.md`.

## Definition of done, graded

Grades are pm's goal-check in validate cycle 2
(`notes/research-FEAT-2458-shape-stamp-sweep-goalcheck-validate-c2.md`).

| Perspective (as signed) | Verdict | SCs | Evidence |
|---|---|---|---|
| **operator** — After a merge, the stamp of every feature that is finished on the default branch is gone, and nothing else is touched: the shared stamp, a live feature's stamp and any stamp whose feature cannot be classified all stay. Each stamp kept because it could not be classified is named once, with the reason, and a dry run shows me what would go without deleting anything. | met | SC-03, SC-04, SC-05 | `tests/integration/test-post-merge-sweep.py` shape-stamp rows (1)-(8), real-git dry run and real run; rows (2)(3)(4)(7)(8) fail against base `322b12b0`; qa's mutants redden the absent-reason rows (3)(7)(8) |
| **code maintainer** — The post-merge hook and the INV-29 gate decide "is this feature finished on the default branch" through one public predicate, and I find no second copy of that rule, nor of the repository-argument helper, in the hook. | met | SC-01, SC-02, SC-06..SC-10 | `tests/integration/test-worktree-terminal.py` rows (a)-(k), 11 rows fail against base; `post-merge-sweep.py:341` decides only on `classify_feature`'s class; `worktree_terminal.py:7` docstring; unit 68 files and integration 95 files green in the run's `qa/` receipts |

All ten success criteria are met. The six kept decisions (DEC-174, 180, 238, 221, 191, 252), D-01
to D-03 and your signature answers Q-01 to Q-05 are honoured.

## What happened, by phase

- **Plan** (product lead, FAIL, 0 cycles). BRIEF and a two-task plan were produced. The run failed
  only because a high panel finding (prefix match could delete an absent feature's stamp) was
  applied without being re-read. You settled it at signature (Q-05, exact-id match).
- **Build** (main session, DEC-174). T-01 `35f67a65` adds `worktree_terminal.classify_feature`.
  T-02 `1d8e8446` makes the post-merge sweep remove finished features' stamps and retires the
  duplicate `_repo_arg_for_segment`. The simplify pass found nothing.
- **Validate cycle 1** (validator lead, FAIL at `9b5b6a7a`). The behaviour passed. Two test-only
  items failed it: two new test cases were complexity grade 1 (MF-1), and the `absent` marker was
  asserted vacuously because the fixture ids contain the word (MF-2).
- **Fix round 1** (main session, `b4536600`, tests only). The cases were split into row tables and
  helpers, and marker checks now strip the feature id before matching.
- **Validate cycle 2** (validator lead, PASS at `f42393e2`). Both items are closed by execution.
  Two readers ran `code-grade.py` independently and got exit 0. qa built its own mutants, saw the
  absent rows go red, and restored byte-for-byte. Production files are byte-identical to cycle 1.

## Open questions

None blocks the ship. The four carried from cycle 1 are backlog rows B-1 to B-4 below. One
harness defect surfaced in this run and is row B-9.

## Escalations

None.

## Spend and ledger

- 3 runs of a 20-run budget; 59 wall-clock minutes; 393,240 tokens.
- Rework window: 29 of the 90 minutes you granted. One fix round of two was used.
- `feature-record.py spend` prints `rework_rounds: 2`. Only one fix round took place; I did not
  trace how the figure is derived, and the ledger holds two `regate` entries (the plan FAIL and
  the validate FAIL).
- `cycles_used` reads 0 of 10 although one fix round ran. See B-9.
- 7 judgements recorded: 1 mission, 3 continue, 2 regate, 1 succession.

## Amendments

The build amended no signed task text.

| at | decision | reason | overruled |
|---|---|---|---|
| none | | | |

overrule rate: 0/0

## UAT

Not required. The BRIEF declares no `verify: uat` criterion.

## Proposed backlog

Strike any row by ID. Unstruck rows become backlog issues on ship acceptance.

| ID | Nature | Finding | Source |
|---|---|---|---|
| B-1 | chore | SC-07's named T-07 case runs only under `--canonical-reader-self-test`, which no runner invokes; the real guard is `--canonical-reader-audit`. Re-point the evidence at the audit, or move the case into `CASES`. | OQ-1, qa c1 |
| B-2 | enhancement | The absence marker is the substring `absent`, which can collide with a feature id or a station named `absent`. Tighten it to a phrase. This rewords signed SC-01 and D-01. | OQ-2, code c1 |
| B-3 | enhancement | `classify_feature` skips a fleet segment whose tree cannot be read, as signed T-01 intent (d) prescribes, so an unreadable tree reads the same as a missing one. Tell them apart. This amends the signed intent. | OQ-3, code c1 |
| B-4 | bug | Harness defect: `tests/integration/test-check-plan-routes.py --canonical-reader-self-test` has 2 failures at base `322b12b0` and at the pin, and no runner invokes it. | OQ-4, qa c1 |
| B-5 | bug | A symlinked `.harness` parent can redirect the sweep's unlink outside the main checkout. It needs local write access, and the worst case is another checkout's stamp deleted, which DEC-180 prices at zero. | security c1, med |
| B-6 | bug | A newline or control character in a stamp's file name can forge a diagnostic line. It needs a local writer. | security c1, low |
| B-7 | chore | Test precision in the fix round: `_feature_row` accepts a truthy non-string reason (cycle 1 required a string); the kept-line check accepts a longer stamp token and a blank row-(8) reason; row (7) checks only the one stamp-naming line. | code and qa c2, med/low |
| B-8 | chore | The multi-segment-hit branch of `classify_feature` and the sweep's symlink-skip branch have no test. No SC requires either. | qa c1 |
| B-9 | bug | Harness defect: a fix round done main-session-direct has no route into `cycles_used`. `run-end --cycles-used 1` on the FAIL run is refused (`cycles_used disagrees with authentic digest evidence`) because the lead's digest reports 0 send-backs, so the hard cycle bound never sees the round. | this run |

Also on record, not proposed as rows: `_sweep_shape_stamps` and `classify_feature` are complexity
grade 2 in production, and the code reviewer recorded written reasons for both in cycle 1.

## Before the merge

Validation ran on this host's interpreter, not in CI. The branch was 0 commits behind
`origin/main` when cycle 2 started.
