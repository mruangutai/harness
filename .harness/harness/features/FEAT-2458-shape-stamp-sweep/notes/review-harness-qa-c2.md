# QA gate — FEAT-2458-shape-stamp-sweep — validate cycle 2

**BLUF: PASS. matrix_ok is true, and unit and integration are satisfied, with runner receipts at
f42393e2. MF-2 is closed: my own mutants turn every absent-marker assertion red, on both layers,
independent of the fixture ids. Under the same mutants the cycle-1 tests stay green, so the fix is
what discriminates. MF-1 is closed for the tests: code-grade exits 0, and every test function in
the diff is at or above bar 3. The PASS-name sets of the feature's test files are identical to
cycle 1. Both verify blocks exit 0. There are two low advisory findings and no must-fix.**

- Run: 2026-11-24-02-validate-validator, cycle 2. Persona harness-qa.
- Tested commit: `f42393e23d81c840332e2132ce711053caa737ad`, which is the feature.json `review_sha`.
- Managed pin: `.claude/worktrees/.pins/FEAT-2458-shape-stamp-sweep--2026-11-24-02-validate-validator--harness-qa`.
  - `git rev-parse HEAD` returned the pin SHA.
  - `worktree-state.py --verify` reported `converged` (rc 0).
  - I ran `bun install --frozen-lockfile` first.
  - Afterwards, `git status --porcelain` was empty and `git diff --quiet <pin>` was clean.
- Policy blob: repository harness, commit f42393e23d81c840332e2132ce711053caa737ad, path
  `.harness/harness.json`, read with `git show`.

## Matrix

- Both tasks are `change_type: cross_module`, so the matrix requires `always = [unit, integration]`.
- There are no `when:` clauses.
- Nothing else is required:
  - `typecheck` is not in the cross_module floor, and the diff touches no `.ts` file.
  - `component` and `ui` are unresolved but not required, because the diff touches no `.tsx`, story or e2e file.
  - No locally_run kind's `detect` (`tests/manual/probe-*.py`) is touched.

|kind|state|command (DEC-255 production runner, from the pin, `env -u HARNESS_AGENT_TYPE`)|files|result|
|---|---|---|---|---|
|unit|satisfied|`python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind unit --shard 1/1 --manifest <run>/qa/manifest-unit.json`|68 selected|rc 0, `runner_exit 0`, `pool: 8 workers, 68 files, 29.94s wall`|
|integration|satisfied|`… --kind integration --shard 1/1 --manifest <run>/qa/manifest-integration.json`|95 selected|rc 0, `ALL PASSED.`, `pool: 8 workers, 95 files, 227.03s wall`|

**Receipts.** Each receipt is the runner's own file and was not edited. Both record
`tested_commit: f42393e2…`.

|receipt|sha256|
|---|---|
|`runs/2026-11-24-02-validate-validator/qa/manifest-unit.json`|`d1cf46b6…b466f`|
|`runs/2026-11-24-02-validate-validator/qa/manifest-integration.json`|`dbeb6228…b40f`|

**Feature scripts in the receipts.** All of these print `PASS <file>` with exit 0:
- integration: test-worktree-terminal.py, test-post-merge-sweep.py, test-check-plan-routes.py and test-checker-structure-locks.py.
- unit: test-broad-catch-census.py and test-no-distribution.py.

**FAIL-token lines that are not failures** (my expertise notes G-09 and G-08):
- The `FAIL`/`ERROR` lines in the unit log come from test-factory-claim-mutation.py's own BUG-1290 mutation proof.
- The others come from test-suite-independence.py.
- Both files exit 0. No file in either log exited non-zero.

**Full output, kept outside the repo.** QA's grant under `runs/` covers only receipts, so the logs
stay in /tmp:
- `/tmp/feat2458-c2-{unit,integration}.log`
- `/tmp/feat2458-c2-verify-T-0{1,2}.log`
- `/tmp/feat2458-c2-mutants.log`
- `/tmp/feat2458-c2-red.log`

## Plan verify blocks (verbatim from plan.yaml at the pin, `env -u HARNESS_AGENT_TYPE sh -c`, at the pin)

- **T-01 verify: rc 0.**
  - 215 PASS lines and 0 FAIL lines.
  - 11 of the PASS lines are `classify_feature` rows.
  - The AST check passed.
- **T-02 verify: rc 0.**
  - 427 PASS lines and 0 FAIL lines.
  - 19 of the PASS lines are feature rows: 8 `stamps` and 11 `classify_feature`.
  - The audit summary reads `0 unresolved reader site(s) across 101 Python file(s)`.
  - All the greps passed.
- **PASS-line totals versus cycle 1.**
  - Cycle 1 recorded 433 PASS lines for T-02; this cycle has 427. The 6-line gap is not in the
    feature's test files.
  - The per-file PASS-name sets at 9b5b6a7a and at f42393e2 are byte-identical:
    - post-merge-sweep: 79
    - check-plan-routes: 103
    - worktree-terminal: 70
  - [INFERENCE] The gap is live-tree-dependent output in the remaining scripts:
    - At the pin, test-no-distribution.py prints 30.
    - I measured 9b5b6a7a only in a scratch tree that is not a git checkout, and there it cannot run (rc 1 at both SHAs).

## Phase 1 (from BRIEF and plan only)

These tests were expected:
- SC-01: one classify_feature row per klass and per reason contract. The absent marker must be
  bound independently of the ids.
- SC-02: fleet rows, and exact-id rows for both harness and fleet.
- SC-01: an undecodable row.
- SC-03, SC-04 and SC-05: a 5-stamp sweep fixture with:
  - real-run deletion of the done stamp only;
  - byte-intact kept stamps;
  - a dry run that deletes nothing and names the done stamp;
  - exactly one unresolved line per kept stamp, with absent or not absent, bound to the reason;
  - no line for the building stamp.
- SC-07: a routes and registry guard.
- SC-09 and SC-10: the regression suites stay green.

Every expectation has a test. The only gap is SC-07's named file, which is OQ-1 and stays LEAVE.

## fail_first, per automated SC

I retook the natural RED at this pin because both test files were rewritten (my expertise note G-06).
- Driver: `/tmp/feat2458-c2-red.py`.
- Each scratch tree is a `git archive` of f42393e2 with only the named production blobs swapped
  for 322b12b0.

|SC|Test (pin)|Red evidence|Tier|
|---|---|---|---|
|SC-01|`tests/integration/test-worktree-terminal.py:1123` `_LOCAL_FEATURE_ROWS` (a)–(f), (i), (k), via `case_classify_feature_local` :1154 and `_feature_row` :1106|Pin tests with base production: rc 1, 59 PASS, **11 FAIL**: every classify_feature row, (a)–(k). This matches cycle 1. Semantic mutants on the pin: T1 (absent wording removed) reds (d) and (i); T2 (unresolved reasons say absent) reds (e), (f) and (k).|natural RED (signature-absent) + semantic mutants|
|SC-02|same file `_FLEET_FEATURE_ROWS` :1168 (g), (h), (j), via `case_classify_feature_fleet` :1206|With base production, (g), (h) and (j) FAIL. For the semantic tier, cycle 1's M1 and M10 still apply, because worktree_terminal.py is unchanged since 9b5b6a7a.|signature-absent + carried semantic|
|SC-03|`tests/integration/test-post-merge-sweep.py:1231` `_shape_stamp_wet_rows` rows (4)–(8), via `case_shape_stamps` :1254|Pin tests with the base post-merge-sweep.py, using either base or T-01 worktree_terminal.py: rc 1, 74 PASS, **5 FAIL**: rows (2), (3), (4), (7) and (8). The deletion row (4) is red.|natural semantic RED|
|SC-04|same, `_shape_stamp_dry_rows` rows (1), (2)|Row (2) is naturally red at base. Row (1)'s dry-run guard is carried from cycle 1's M5, because sweep production is unchanged since 9b5b6a7a.|natural + carried mutant|
|SC-05|same, rows (3), (6), (7), (8); `_one_kept_line` :1213|Rows (3), (7) and (8) are naturally red at base. My MF-2 mutants are in the next section: (3) and (7) red on reason drop; (8) reds on a spurious absent.|natural + mutants|
|SC-07|`tests/integration/test-check-plan-routes.py` (named)|This was carried from cycle 1, unchanged: the named test is never red, and `--canonical-reader-audit` reds both mutants. Production and this test file are byte-unchanged 9b5b6a7a→f42393e2. This is OQ-1 (LEAVE). No new evidence.|carried; audit-command red|
|SC-09|pre-existing cases in the four integration files|Regression guard. There is no defect to redden, so fail-first is N/A. Green in the integration receipt and in both verify runs.|N/A|
|SC-10|test-broad-catch-census.py, test-no-distribution.py|Regression guard, so fail-first is N/A. Green in the unit receipt.|N/A|

## MF-2 — mutant results (my own)

- **Driver:** `/tmp/feat2458-c2-mutants.py`.
- **Scratch tree:** `/tmp/feat2458-c2-mut`, a `git archive` of the pin. Production was never edited
  in a repository checkout (DEC-153; my expertise note G-06).
- **Restore proof:** after each mutant the driver asserted that the scratch sources are
  byte-identical to the pin blobs.
- **Pin intact:** the pin's `git status --porcelain` is empty, and `git diff --quiet f42393e2` is
  clean.
- **Pin blob hashes:** the sha256 of `post-merge-sweep.py` and `worktree_terminal.py` equals that of
  `git show f42393e2:<path>`:
  - post-merge-sweep.py: `158523a2…d721`
  - worktree_terminal.py: `abe81763…1c9e`

|mutant|sweep rows red|terminal rows red|
|---|---|---|
|baseline (pin)|none|none|
|S1: sweep kept line drops `: {reason}`|(3), (7)|—|
|S2: sweep kept line replaces `absent`→`missing` in reason|(3), (7)|—|
|T1: classify_feature absent reason → `is not on …`|(3), (7)|(d), (i)|
|S1+T1 together|(3), (7)|(d), (i)|
|S3: sweep appends ` absent` to every kept line|(8)|—|
|T2: every `_landed_classification` unresolved reason gets ` (absent)`|(8)|(e), (f), (k)|
|**CONTROL: cycle-1 tests + S1**|**none (green)**|none|
|**CONTROL: cycle-1 tests + T1**|**none (green)**|(d) only; **(i) green**|

Conclusions:
- Every positive absent assertion reddens when the reason stops saying absent:
  - sweep (3) and (7);
  - terminal (d) and (i).
- Every negative not-absent assertion reddens when the reason wrongly says absent:
  - sweep (8);
  - terminal (e), (f) and (k).
- Each of these holds independently of the fixture ids FEAT-912-stamp-absent and
  FEAT-920-prefix-absent.
- The controls reproduce the cycle-1 vacuity, so the id-stripping in `_stamp_lines` and
  `_feature_row` is the discriminator.

Row (8) correctly stays green under S1/S2. SC-05 asks only that the 909 line carry unresolved
and not absent, and dropping the reason leaves both true. Its not-absent leg is bound by S3 and T2.

**No absent-marker assertion stays green, so MF-2 is closed.**

## MF-1 — grade

`code-grade.py --base 322b12b0 --head f42393e2`, run from the pin, exits 0 with `RESULT: PASS`
and `PASSING: 17`.

Every test function in the diff is at or above bar 3:

|grade|functions|
|---|---|
|3|`main` (terminal)|
|4|`case_shape_stamps`, `_one_kept_line`, `_shape_stamp_wet_rows`, `_feature_row`, `case_classify_feature_local`, `case_classify_feature_fleet`, both `_commit_bad_utf8_feature`, `_shape_stamp_fixture`|
|5|the remaining helpers|

The two production functions, `_sweep_shape_stamps` and `classify_feature`, are grade 2 against
bar 4. That is the settled cycle-1 dismissal with recorded reasons (LEAVE); there is no new evidence.

## Row-set preservation (cycle 1 → pin)

**Sweep test.** Rows (1)–(8) and both `_assert_resolved_root_in_fixture` SAFETY rows are present
with the same names.
- The fixture is unchanged, now factored into `_shape_stamp_fixture`:
  - same ids, statuses and bytes;
  - FEAT-909 is written by `_commit_bad_utf8_feature`.
- Both runs are still exercised against the real-git fixture: the real `--dry-run`, then the real
  run (`case_shape_stamps` :1254).

**Terminal test.** Rows (a)–(k) are present with the same ids, klass and markers:
- local rows in `_LOCAL_FEATURE_ROWS`;
- fleet rows (g), (h) and (j) in `_FLEET_FEATURE_ROWS`, still run through the fleet subprocess.

**PASS-name sets match.** Sorted PASS-name sets at 9b5b6a7a and at f42393e2 are identical for
test-post-merge-sweep.py (79), test-worktree-terminal.py (70) and test-check-plan-routes.py (103).

**Weakenings found.** Both are advisory:
- **A-1 · substance · low · T-02** (`tests/integration/test-post-merge-sweep.py`).
  - What changed: row (7)'s never-removed clause is narrower.
    - Cycle 1 rejected any line in either run that contains `FEAT-912` with `would remove` or `removed`.
    - The pin checks `removed` / `would remove` only on the single stamp-naming line per run, through `_one_kept_line` in rows (3) and (7).
  - Failure scenario: a sweep that prints a removal line naming FEAT-912 without the `.shape-sweep-stamp.` path.
  - Why the risk is low: any extra stamp-naming line breaks the count-equals-1 check, and any actual
    deletion breaks `_stamp_intact`, so I found no realistic escaping mutant.
- **A-2 · substance · low · T-01** (`tests/integration/test-worktree-terminal.py:1106`).
  - What changed: `_feature_row` tests `bool(reason)`, where cycle 1 tested `isinstance(reason, str) and reason != ""`.
  - Failure scenario: a non-str truthy reason, such as `("terminal", 1)`, now passes the rows that
    have no `must` markers: (a), (c), (g), (h) and (j). SC-01 requires a non-empty reason, which
    implies a str.
  - I established this by reading the code, not by a mutant. No production path returns a non-str reason.

## Principles applied
- Build the Lever: I used one scripted mutant driver, including the cycle-1 controls, and one scripted
  red driver over scratch extractions, instead of hand edits.

## Open questions
- none new. OQ-1 through OQ-4 are unchanged and carried.
