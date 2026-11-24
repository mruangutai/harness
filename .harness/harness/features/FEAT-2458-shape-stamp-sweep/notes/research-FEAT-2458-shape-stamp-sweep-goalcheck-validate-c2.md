# Goal-check — FEAT-2458-shape-stamp-sweep — validate cycle 2

**Verdict: PASS.** Both declared perspectives (operator, code maintainer) are discharged.
SC-01..SC-10 are all met at the pin. The absent clause of SC-01 and SC-05, which cycle 1 accepted
on behaviour only, now has discriminating test evidence: a mutant that drops only the absent
wording reddens the rows that carry it. No decision disposition is violated. I raise no findings.

Pin: review_sha `f42393e23d81c840332e2132ce711053caa737ad` (FD/feature.json `review_sha`, at both
HEAD and the working tree). Diff `322b12b0..f42393e2`. Production code is byte-identical to cycle
1's pin: `git diff --stat 9b5b6a7a f42393e2 -- .claude` is empty. The only code change is
fix-round commit b4536600, which touches two test files, and
`git diff --stat b4536600 f42393e2 -- .claude tests` is empty. Worktree HEAD is `87d88716`, and
`git diff --stat f42393e2 HEAD -- .claude tests` is empty, so the suites I ran in the worktree
test the pinned code. Every run had HARNESS_AGENT_TYPE cleared (`env -u`). I ran the mutants in
a scratch export of the pin (`git archive f42393e2` into `/tmp/gc2458c2-Zcev`, outside the repo)
and restored it after each one.

## Perspectives

- **operator — pass.** Carried by SC-03, SC-04 and SC-05.
  - In `test-post-merge-sweep.py` `case_shape_stamps` (`_shape_stamp_dry_rows`,
    `_shape_stamp_wet_rows`), the real run deletes only the done stamp. The plain, live,
    never-landed-prefix and non-UTF-8 stamps all keep their bytes.
  - The dry run deletes nothing and prints `would remove` for the done stamp.
  - Each unresolved stamp gets exactly one line per run, and the line carries its reason. The
    absent marker is now proven to discriminate (see below), and the live stamp is never named.
- **code maintainer — pass.** Carried by SC-01, SC-02 and SC-06..SC-10.
  - There is one public predicate, `worktree_terminal.py#classify_feature`, built on
    `_landed_classification`.
  - The hook's `_repo_arg_for_segment` is gone. The hook calls
    `worktree_terminal.repo_arg_for_segment`, and the registry key and inventory row were
    removed with it.
  - The stamp step decides from `klass` alone.
  - `code-grade.py --base 322b12b0 --head f42393e2` exits 0 with `RESULT: PASS` and `PASSING: 17`,
    so MF-1 is closed at the pin itself, not only at the tip.

## Was the absent clause discriminating? (cycle 1: met on behaviour only)

It is now. The repair is in the tests: `_stamp_lines` and `_feature_row` remove the feature id
before matching a marker. No fixture id was renamed: FEAT-912-stamp-absent and
FEAT-920-prefix-absent are still in use. Each mutant changes one branch at a time.

- **Mutant A** drops `{reason}` from the sweep's kept line in `post-merge-sweep.py`.
  - Pin tests: sweep rows (3) and (7) FAIL. Row (8) stays green, which is correct because its
    contract is "not absent". Every terminal row stays green.
  - The same mutant run against cycle 1's test file (`9b5b6a7a`): all 8 stamp rows PASS. This
    confirms the MF-2 premise at the old pin and shows the repair is real.
- **Mutant B** changes only `classify_feature`'s absent reason from `is absent from` to
  `is missing from`.
  - The worktree-path reason at `worktree_terminal.py`, which has the same wording, is untouched.
  - Terminal rows (d) and (i) FAIL. Sweep rows (3) and (7) FAIL independently, so the marker is
    graded at both seams.
- **Fail-first, re-run with the pin's test files against 322b12b0's production files:**
  - All 11 `classify_feature` rows FAIL.
  - Stamp rows (2), (3), (4), (7) and (8) FAIL, so the SC-03 deletion assertion (4) is red first.
  - Rows (1), (5) and (6) PASS, as expected: with no sweep step, nothing changes on disk.

## sc_status

| SC | verdict | method | evidence |
|---|---|---|---|
| SC-01 | met | automated | test-worktree-terminal.py `case_classify_feature_local` rows (a)(b)(c)(d)(e)(f)(i)(k) PASS at pin. Fail-first: all FAIL against 322b12b0's worktree_terminal.py. Absent clause: Mutant B reddens (d)(i) |
| SC-02 | met | automated | `case_classify_feature_fleet` rows (g)(h)(j) PASS (fleet fixture, (j) has the longer harness id at building) |
| SC-03 | met | automated | `case_shape_stamps` rows (4)(5)(6)(7)(8) PASS. (4) FAILs against 322b12b0's post-merge-sweep.py |
| SC-04 | met | automated | rows (1)(2) PASS |
| SC-05 | met | automated | rows (3)(7) (absent once, dry and real), (8) (non-UTF-8 once per run, not absent) and (6) (live never named) PASS. Absent clause: Mutant A and Mutant B each redden (3)(7) |
| SC-06 | met | inspection | `git show f42393e2:.claude/skills/harness/bin/post-merge-sweep.py` `_sweep_shape_stamps`: it uses listdir/isfile/islink, then `classify_feature`, then `os.remove`, and decides on `klass` only. It is unchanged since cycle 1. The formal citation belongs to code-reviewer |
| SC-07 | met | automated | the key and the row are absent at the pin (diff hunks in check-plan-routes.py and canonical-reader-classification.json). test-check-plan-routes.py rc=0 with 0 `^FAIL` lines, and `--canonical-reader-audit` rc=0 (OQ-1 carried) |
| SC-08 | met | inspection | the pinned worktree_terminal.py module docstring names CLASSES, classify, classify_all, classify_feature and repo_arg_for_segment. The hook's "only CLASSES and classify" docstring was deleted together with the helper |
| SC-09 | met | automated | test-worktree-terminal, test-post-merge-sweep, test-check-plan-routes and test-checker-structure-locks: each rc=0, with 0 lines starting `FAIL` |
| SC-10 | met | automated | unit test-broad-catch-census and test-no-distribution: each rc=0, with 0 `^FAIL` lines |

## Decision dispositions

DECISIONS.md is not in the diff (`git diff --stat 322b12b0 f42393e2 -- .harness/harness/docs` is
empty). Every `decisions_affected` row is `keep`, so per Mode 2 none is graded and no amend or
strike row exists. The table below is an advisory honour check against
`git show f42393e2:.harness/harness/docs/DECISIONS.md`.

| Row | Pinned anchor | Honoured |
|---|---|---|
| DEC-174 keep | heading at line 4479 | yes: both tasks main-session-direct, and the fix round is a `[harness:human]` commit |
| DEC-180 keep | line 4945 "The window survives only as the first-run bound" | yes: check-domain.py is not in the diff |
| DEC-238 keep | line 8169 "removes pins older than a day" | yes: the stamp step follows the node_modules step, honours DRY_RUN, and the pin and node_modules functions are unchanged |
| DEC-221 keep | line 7378 "Nothing else is installed into a product repository" | yes: only the control plane's own `.harness/<segment>/features` is read via `git ls-tree` |
| DEC-191 keep | line 5550 "A feature's station belongs only to `plan.yaml`" | yes: the station comes through `_landed_classification` |
| DEC-252 keep | line 8337 "Three comparisons still read shipped records, as data only." | yes: the only reader change maps UnicodeDecodeError to `(None, "unparseable")` |
| D-01 | plan.yaml decisions | yes: three results, and only the absent reason says absent (Mutant B shows the tests pin it) |
| D-02 | plan.yaml decisions | yes: a stamp is deleted only on `klass == "terminal"`, in the post-merge sweep. feature-worktree.py is not in the diff |
| D-03 | plan.yaml decisions | yes: exact `in names` matching, harness first and then each fleet segment. There are no `_match_landed_id`, `_planning_segment` or `_resolve_landed` calls, and rows (i)(j) pin this |
| Q-01..Q-05 | notes/approval-decision-2026-11-23.md | yes: `not_terminal` spelling (Q-01); `removed` / `would remove` per-stamp lines (Q-02); D-03 walk (Q-03); UnicodeDecodeError catch in `_landed_blob_text` (Q-04); exact-id match for PF-9ad7c484, tested by rows (i), (j) and stamp (7) (Q-05) |

## Carried, not re-raised

OQ-1..OQ-4 and the cycle-1 advisory dismissals are unchanged. I have no new evidence that alters
the severity of any of them.

## Principles applied

- Expertise P-06 / O-01 (craft): I closed MF-2 by re-measuring its premise. Mutant A is green on
  cycle 1's tests and red on the pin's tests. Each mutant changes one branch only, never one
  mutant per side.
- Expertise O-07 (craft): for fail-first, the earlier commit's production files serve as a free
  mutant.

## Not measured

- I did not re-run the mutant that deletes the UnicodeDecodeError catch. Row (k) and row (8) pass;
  qa owns that proof.
- I left the scratch export `/tmp/gc2458c2-Zcev` and the `/tmp/gc2458c2-*` logs in place. Both
  are outside the repo.
