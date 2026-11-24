# Goal-check — FEAT-2458-shape-stamp-sweep — validate cycle 1

**Verdict: PASS.** Both perspectives are discharged. SC-01..SC-05 and SC-07..SC-10 are met by
tests I ran at review_sha, and SC-06 is met by inspection. Each `decisions_affected` keep row
and D-01..D-03 is honoured. I raise no findings.

Pin: review_sha `9b5b6a7a05c3dc8aa382699e33477d2f0397281c`, diff `322b12b0..9b5b6a7a`. The
worktree HEAD is `1bc2d516`. `git diff --stat 9b5b6a7a -- .claude tests` is empty, so I could
run the suites in the worktree and they still test the pinned code. Every run cleared
HARNESS_AGENT_TYPE (`env -u`).

## Perspectives

- **operator — pass.** Carried by SC-03, SC-04 and SC-05. In the `case_shape_stamps` fixture
  (`tests/integration/test-post-merge-sweep.py`), a real run deletes only the `done` feature's
  stamp. The plain, live, never-landed-prefix and non-UTF-8 stamps all keep their bytes. A dry
  run deletes nothing and prints `would remove` for the done stamp. Each unresolved stamp gets
  exactly one line per run that gives the reason (absent vs not absent), and the live stamp
  never appears in the output. Code: `post-merge-sweep.py#_sweep_shape_stamps`.
- **code maintainer — pass.** Carried by SC-01, SC-02 and SC-06..SC-10. There is now one public
  predicate, `worktree_terminal.py#classify_feature`, and it is built on
  `_landed_classification`, the same landed rule INV-29 uses through `classify`. The hook's
  `_repo_arg_for_segment` is gone: the hook now calls `worktree_terminal.repo_arg_for_segment`,
  and the registry key and inventory row were removed with it. Nothing in the hook reads
  plan.yaml, feature.json, BRIEF.md or a station name inside the stamp step.

## sc_status

| SC | verdict | method | evidence |
|---|---|---|---|
| SC-01 | met | automated | test-worktree-terminal.py `case_classify_feature` rows (a)(b)(c)(d)(e)(f)(i)(k) pass at pin. Fail-first: the current test file run against 322b12b0's worktree_terminal.py shows all 11 rows FAIL |
| SC-02 | met | automated | same case, rows (g)(h)(j) (fleet fixture via `_write_fleet`; (j) has the longer harness id at building) pass |
| SC-03 | met | automated | test-post-merge-sweep.py `case_shape_stamps` rows (4)(5)(6)(7)(8) pass. Fail-first: run against 322b12b0's post-merge-sweep.py, (2)(3)(4)(7)(8) FAIL |
| SC-04 | met | automated | rows (1)(2) pass |
| SC-05 | met | automated | rows (3)(7) (absent: once, unresolved+absent, dry and real), (8) (non-UTF-8: once per run, not absent) and (6) (live never named) pass |
| SC-06 | met | inspection | `git show 9b5b6a7a:.claude/skills/harness/bin/post-merge-sweep.py` `_sweep_shape_stamps`: `listdir`/`isfile`/`islink`, `classify_feature`, `os.remove` only. It decides on `klass` alone (the code-reviewer owns the formal citation) |
| SC-07 | met | automated | the key is absent from check-plan-routes.py and the row from canonical-reader-classification.json (`grep -c` = 0 for both); test-check-plan-routes.py exits 0, no FAIL line; `--canonical-reader-audit` exits 0 |
| SC-08 | met | inspection | at the pin, the worktree_terminal.py module docstring names CLASSES, classify, classify_all, classify_feature and repo_arg_for_segment. The hook's "only CLASSES and classify" docstring was deleted (`grep CLASSES` finds nothing in the hook) |
| SC-09 | met | automated | test-worktree-terminal, test-post-merge-sweep, test-check-plan-routes and test-checker-structure-locks exit 0. A grep for `FAIL` matched only test names inside `PASS:` lines |
| SC-10 | met | automated | unit test-broad-catch-census and test-no-distribution exit 0 |

## Decision dispositions (DECISIONS.md at the pin; untouched by the diff)

These are all `keep` rows. Per Mode 2 they are not graded, but the dispatch asked whether each
is honoured, so each row below answers that.

- **DEC-174** (`DECISIONS.md` heading at line 4479) — honoured. Both tasks are main-session-direct, so no hosted dev built anything.
- **DEC-180** (line 4945, "The window survives only as the first-run bound") — honoured. check-domain.py is not in the diff, so stamp write and read are unchanged.
- **DEC-238** (line 8169) — honoured. The stamp step comes after `_sweep_prototype_node_modules` and respects `DRY_RUN`. The pin and node_modules functions are unchanged.
- **DEC-221** (line 7378) — honoured. `classify_feature` runs `git ls-tree` on the control plane's own `.harness/<segment>/features` and reads no product repository. Preflight is unchanged.
- **DEC-191** (line 5550) — honoured. The station comes from the landed plan.yaml through `_landed_plan_classification`. feature.json is read only to check it is present and parseable.
- **DEC-252** (line 8337) — honoured. The only change to the landed reader turns a UnicodeDecodeError into `(None, "unparseable")`.
- **D-01** — honoured. The function returns one of three results, and only the absent reason contains "absent".
- **D-02** — honoured. A stamp is deleted only when `klass == "terminal"`, only in the post-merge sweep, and feature-worktree.py is not in the diff.
- **D-03** — honoured. Matching is by exact `in names`: harness first, then each fleet segment. There are no `_match_landed_id`, `_planning_segment` or `_resolve_landed` calls, and rows (i) and (j) pin this behaviour.

## Not measured

- I did not run a mutant that only deletes the UnicodeDecodeError catch. bash-write-guard
  refused the temporary rewrite of the bin file (correctly, under my domain), so I did not try
  another route. qa owns that fail-first proof.
- The probe tree `/var/folders/.../gc2458-7wv0puj7` is a scratch export outside the repo and was left in place.
- The real main checkout's stamp population is a post-merge operational check under the BRIEF's Verification gaps. It is not graded here.
