# FEAT-2458 cycle 2 — Code review: PASS

**MF-1 and MF-2 closed.** Only test changes since cycle 1; two non-blocking assertion gaps below. Reviewed `322b12b0..f42393e23d81c840332e2132ce711053caa737ad`. The active feature record agrees with the dispatch pin. The canonical `261fdf72` base adds only feature records. No tracked edits outside feature records.

## Stage 1 — Spec compliance: PASS

- **SC-01/02, D-01/02/03:** exact harness/fleet lookup delegates the verdict to `_landed_classification`; `worktree_terminal.py:213` converts undecodable blobs to unresolved. Eleven local/fleet rows still exercise all named cases against real Git.
- **SC-03/04/05:** `tests/integration/test-post-merge-sweep.py:1254` runs the real sweep against a Git fixture both dry and wet; all eight rows reach `main`. No production or route-inventory changes since `1d8e8446`; `b4536600` touches only the two owned test files.
- **SC-06 (inspection):** `.claude/skills/harness/bin/post-merge-sweep.py:341` (`_sweep_shape_stamps`) calls `classify_feature` at line 361. Only `terminal` reaches unlink. The sweep reads no plan, feature record, BRIEF or station itself.
- **SC-08 (inspection):** `.claude/skills/harness/bin/worktree_terminal.py:7` lists all five public names. `.claude/skills/harness/bin/post-merge-sweep.py:159` uses the shared repo helper; the duplicate and stale surface claim are gone.
- **SC-07:** retired key absent from registry and inventory; shared helper row remains. SC-07/09/10 execution and fail-first evidence belong to QA; no integration suite or changed enforcement path run by this reviewer. Cycle-1 operator advisories are not reopened.

## Stage 2 — Code quality

**MF-1:** `code-grade.py --base 322b12b0 --head f42393e23d81c840332e2132ce711053caa737ad` exited **0**; 17 `RESULT: PASS` records. Canonical base returned the same. The only below-bar records are the two accepted production grade-2 exceptions (`RESULT: FAIL` individually, no high severity):

| Task | Function | Cyclomatic / cognitive / ABC | Grade / bar | Reason |
|---|---|---|---|---|
| T-02 | `post-merge-sweep.py:341` `_sweep_shape_stamps` | 11 / 20 / 24.4 | 2 / 4 | File type, verdict, dry-run and unlink-error guards stay beside the write. |
| T-01 | `worktree_terminal.py:601` `classify_feature` | 10 / 16 / 24.0 | 2 / 4 | Harness precedence and fleet ambiguity remain visible before the shared verdict. |

The split separates fixture setup, dry/wet observations and local/fleet invocation. Row tables hold data, not hidden branching. Both runners consume every returned row; local exceptions become failing rows, and fleet subprocess failure or missing data cannot skip a row into green.

**MF-2:** Isolated probes executed assertion predicates extracted from the pin, not the enforcement code. With unchanged fixture ids, stripping the reason made sweep rows (3)/(7) red; removing the `absent` word but retaining the id made classifier rows (d)/(i) red. Adding `absent` to the undecodable reason made row (8)'s predicate red. Removing all literal id occurrences is necessary for these positives because the reason can echo the id as well as the path. The current negative fixtures' IDs do not contain `absent`, so stripping them cannot erase a real negative-marker failure.

## Findings — non-blocking

- **T-01 · substance · med** — `tests/integration/test-worktree-terminal.py:1106`: the refactored `_feature_row` accepts `('terminal', True)` or `('unresolved', True)` for rows without a required marker (confirmed on (a)/(e)). Cycle 1 required a string; the new `bool(reason)` lets a truthy non-string satisfy the reason contract. Restore the type requirement when touching this assertion.
- **T-02 · substance · low** — `tests/integration/test-post-merge-sweep.py:1206–1216`: the existing substring path match accepts a kept message naming `FEAT-912-stamp-absent-longer` instead of `FEAT-912-stamp-absent` if the reason still says `absent`. Row (8) also accepts a blank reason after `unresolved:`. Both accepted by the isolated probe; neither defeats the corrected missing-`absent` checks. Exact stamp-token and non-empty reason checks would catch these output-only regressions.

## Principles applied

- **Migrate Callers, Then Delete Legacy APIs:** verified the hook uses the shared helper and the deleted reader left no shim or stale registry entry.
- **Model the Domain:** verified the row tables declare the expected classifier outcomes while one assertion helper evaluates them.

Open questions: none.
