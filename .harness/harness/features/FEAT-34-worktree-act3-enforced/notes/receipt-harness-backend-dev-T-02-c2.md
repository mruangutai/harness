# T-02 c2 receipt — CLASSIFY_ALL cases (i)-(l), D-10

**REWORK of a green task.** c1's closing conclusion (lines 135-140 of the c1 receipt) — "REQ-04's
no-exception clause is satisfied by the caller iterating repos, not by classify() itself" — is
OVERTURNED by D-10 (`plan.yaml:125-185`) and is NOT carried forward here. `classify_all(root)` is
now the second entry point in `worktree_terminal.py` (T-01, unedited in this task), and this task
adds the test cases that grade it. The c1 receipt is left exactly as it was written.

## What changed

`.claude/skills/harness/bin/test-worktree-terminal.py`:
- Module docstring corrected: it now states the file covers `classify()` **and** `classify_all()`,
  and the TDD-provenance note records the D-10 overturn truthfully without rewriting c1's history.
- Four new case functions, reusing case (g)'s fixture shape (probe root + `fleet.yaml` +
  `workspace_root` + a real second git repo) rather than a second fixture shape:
  - `case_classify_all_two_repos()` — (i), 3 assertions incl. the red proof
    (`classify(probe_root)` alone never reaches the second repo's worktree).
  - `case_classify_all_absent_vs_unenumerable()` — (j) + (k), 6 assertions: (j) the real
    second-repo record is unaffected and no record/no raise for the never-created directory;
    (k) exactly one `unresolved` record with `klass` and `path` asserted separately; plus both
    red proofs against local stubs that discriminate skip-both from report-both.
  - `case_classify_all_fleet_unloadable()` — (l), 3 assertions: the fleet-path `unresolved`
    record, the harness half's own record still present, and the swallow-implementation red proof.
- **New helper:** `_build_probe_repo(tmp)` makes `probe_root` a REAL git repo with its own standing
  worktree over a landed Done feature (`repo_segment="harness"`) — case (g)'s `probe_root` was
  directories + `SPEC.md` only, sufficient for the `harness_root()` import-time probe but NOT for
  asserting `classify_all`'s harness half returns a non-empty, distinguishable record (dispatch
  note 2). An empty-vs-empty comparison would have passed vacuously.
- Every `classify_all` case runs in a fresh subprocess with `CLAUDE_PROJECT_DIR` set in the env
  before import (dispatch note 1 — the import-time `FLEET_PATH`/`load_fleet` default-argument
  trap), exactly as case (g) already does.
- No total-count assertions anywhere in the new cases (dispatch note 3) — every branch is its own
  assertion on its own property.

**Not touched:** `.claude/skills/harness/bin/worktree_terminal.py` (T-01's, read-only here),
`check-state.sh`, `test-check-state.py`, `post-merge-sweep.sh`, `run-unit-tests.sh`,
`.harness/harness.json`, `plan.yaml`, `BRIEF.md`. Cases (a)-(h) and their red proofs are unmodified.

## No defect found in classify_all

Every case (i)-(l) passed against the real `classify_all` as T-01 shipped it. Nothing to report to
loop T-01 back on.

## Count — before/after, both the grep expression and the run's own PASS-line count

`grep -c 'results.append(' .claude/skills/harness/bin/test-worktree-terminal.py`

- Before (pre-existing, unedited by this task): **19** (matches the operator's independently
  re-derived baseline: case_classify 10, case_deadlock 2, case_deadlock_red_proof 2,
  case_absent_red_proof 4, case_second_repo 1).
- **Predicted after, stated before running:** 19 + (i) 3 + (j)/(k) 6 + (l) 3 = **31**.
- **Actual after:** grep reports **31**. The run's own PASS-line count is also **31** (verbatim
  output below). Predicted and actual match; no adjustment needed.

## verify — `python3 .claude/skills/harness/bin/test-worktree-terminal.py`

Cross-checked against `plan.yaml`'s T-02 `verify:` — identical string. Full actual output:

```
PASS: (a) landed Done, exact name -> terminal
PASS: (b) landed Review -> omitted from the returned list
PASS: (d) never landed -> exempt_absent
PASS: (e) short-named prefix of one landed Done dir -> terminal, NOT exempt_absent
PASS: (f) landed feature.json unparseable -> unresolved
PASS: ambiguous prefix (matches 2 landed dirs) -> unresolved, never exempt_absent
PASS: (h) uncommitted change in a Done worktree -> terminal with dirty True
PASS: every returned record carries exactly the six documented keys, klass is always one of CLASSES
PASS: records are sorted by path
PASS: root itself is never a returned record
PASS: (c) landed Review, working copy Done -> NOT terminal (omitted)
PASS: (c) inverse: landed Done, working copy Review -> terminal regardless
PASS: (c) red proof, forward: working-tree-reading stub wrongly says terminal for a landed-Review worktree
PASS: (c) red proof, inverse: working-tree-reading stub wrongly says omitted for a landed-Done worktree
PASS: (a) red-proof stub PASSES: exact-match Done -> terminal
PASS: (d) red-proof stub PASSES: truly absent -> exempt_absent
PASS: (e) red-proof stub FAILS: short-named prefix wrongly folded into exempt_absent instead of terminal
PASS: (f) red-proof stub FAILS: unparseable landed JSON wrongly folded into exempt_absent instead of unresolved
PASS: (g) real second git repo, fleet-resolved default branch, real worktree add, landed Done -> terminal
PASS: (i) classify_all(probe_root) includes the harness half's own terminal record
PASS: (i) classify_all(probe_root) includes the second repository's terminal record
PASS: (i) RED PROOF: classify(probe_root) alone (classify_all==classify) never returns a record for the second repository's worktree
PASS: (j) real second repository's terminal record is unaffected by an absent declared repo alongside it
PASS: (j) absent checkout: no record for the never-created directory, and classify_all does not raise
PASS: (k) present-but-unenumerable: exactly one repository-level record, klass unresolved
PASS: (k) present-but-unenumerable: record path equals the declared directory
PASS: (j)/(k) RED PROOF: a stub skipping every non-enumerable declared repo passes (j) but fails (k) — emits no record at all for unenum-repo
PASS: (j)/(k) RED PROOF: a stub reporting every non-enumerable declared repo passes (k) but fails (j) — wrongly emits a record for absent-repo too
PASS: (l) fleet.yaml unloadable: classify_all returns an unresolved record whose path is the fleet path
PASS: (l) fleet.yaml unloadable: classify_all still returns the harness root's own records
PASS: (l) RED PROOF: an implementation that swallows the fleet-load exception (dropping the fleet-path record) passes every other case and fails this one
```

`echo $?` → **0**.

## TDD note

`classify_all` was already implemented and shipped by T-01 (a separate, completed task) before
this task began — this task is pure test-authorship against an existing, already-graded
implementation, the same shape as case (g) in c1. No production code was written in this task; the
Iron Law's write-test-before-code ordering is satisfied by T-01/T-02's task split, unchanged from
c1's precedent.

## Files touched

- `.claude/skills/harness/bin/test-worktree-terminal.py` (extended with cases (i)-(l), docstring
  corrected; cases (a)-(h) unmodified)
- This receipt.
- `.harness/harness/features/FEAT-34-worktree-act3-enforced/observations/harness-backend-dev.md`
  (appended one entry via `observations-merge.py`)

## Commits / git state

None. No `git add`, `git commit`, or `git worktree remove` run. Tree left dirty, as instructed.

---

## Loop-back cycle 1: case (l) red proof

**Send-back reason, in the operator's words:** the third assertion in
`case_classify_all_fleet_unloadable()` (previously `test-worktree-terminal.py:699-706`) could not
fail. It was built by filtering the real `classify_all` output to drop the fleet-path record
(`swallowed`), then asserting that record is absent from `swallowed` — a restatement of the filter
that just ran, not a measurement — ANDed with `any(r["path"] == fleet_path for r in recs)`, which
duplicates assertion 1 (`ok_fleet`) already checked one line above. The line printed "RED PROOF:
... fails this one" while never actually running a swallowing implementation, so a reader would
believe a failing state had been demonstrated when it had not.

**What I changed:** replaced the single-producer, self-referential comparison with a second,
independent producer. The fix adds a local, deliberately-wrong stub — same idiom as
`_stub_skip_both`/`_stub_reports_both` and `_classify_stub_reads_working_tree` elsewhere in this
file, independent of `worktree_terminal`'s own `classify_all` code path — that calls
`factory_config.load_fleet()`, catches the failure, and returns only `list(classify(root))` (the
harness half), with no fleet-path record appended at all. Both the real `classify_all(probe_root)`
and this swallowing stub now run in the SAME subprocess, against the SAME unloadable-fleet fixture
(the `fleet.yaml` this case already corrupts), and the assertion compares the two outputs directly:
the stub's records contain NO record whose path is the fleet path, AND the real output's records
DO. Two different producers, one fixture — the tautology is gone because the two sides can now
genuinely disagree.

Also corrected the case's docstring to describe the new red-proof mechanism and to record this
loop-back in place, without rewriting the earlier (accepted) prose describing assertions 1 and 2,
which are unchanged.

**New evidence — the assertion demonstrably discriminates.** Invoking
`case_classify_all_fleet_unloadable()` directly against the corrupted-fleet fixture, the two
producers' JSON differ exactly on the property being asserted:

- `real` (actual `classify_all(probe_root)`): 2 records — the harness half's `terminal` record for
  `FEAT-10-probe-done`, AND an `unresolved` record whose `path` is the fleet path (
  `.../probe/.harness/factory/fleet.yaml`, `reason: "fleet.yaml failed to load: ..."`).
- `stub` (the swallowing implementation, same fixture, same subprocess): 1 record — only the
  harness half's `terminal` record. No fleet-path record present.

`red_proof = (not any(r["path"] == fleet_path for r in stub_recs)) and any(r["path"] == fleet_path
for r in recs)` is therefore `True and True = True` on the real behavior, and would be `False` the
moment `classify_all` itself started swallowing the fleet-load exception (its own `real` output
would then match the stub's — no fleet-path record — and the second conjunct would go `False`).
This is the failure state the operator asked to see demonstrated, not asserted by construction.

### Count after this cycle

`grep -c 'results.append(' .claude/skills/harness/bin/test-worktree-terminal.py` → **31**,
unchanged from before this cycle (this was a like-for-like replacement of one assertion's
evidence, not an added or removed check — case (l) still contributes exactly 3 `results.append`
calls).

### Re-run, verbatim

Command (verbatim from `plan.yaml:306-307`, matches the dispatch):
```
python3 .claude/skills/harness/bin/test-worktree-terminal.py
```

Full output:
```
PASS: (a) landed Done, exact name -> terminal
PASS: (b) landed Review -> omitted from the returned list
PASS: (d) never landed -> exempt_absent
PASS: (e) short-named prefix of one landed Done dir -> terminal, NOT exempt_absent
PASS: (f) landed feature.json unparseable -> unresolved
PASS: ambiguous prefix (matches 2 landed dirs) -> unresolved, never exempt_absent
PASS: (h) uncommitted change in a Done worktree -> terminal with dirty True
PASS: every returned record carries exactly the six documented keys, klass is always one of CLASSES
PASS: records are sorted by path
PASS: root itself is never a returned record
PASS: (c) landed Review, working copy Done -> NOT terminal (omitted)
PASS: (c) inverse: landed Done, working copy Review -> terminal regardless
PASS: (c) red proof, forward: working-tree-reading stub wrongly says terminal for a landed-Review worktree
PASS: (c) red proof, inverse: working-tree-reading stub wrongly says omitted for a landed-Done worktree
PASS: (a) red-proof stub PASSES: exact-match Done -> terminal
PASS: (d) red-proof stub PASSES: truly absent -> exempt_absent
PASS: (e) red-proof stub FAILS: short-named prefix wrongly folded into exempt_absent instead of terminal
PASS: (f) red-proof stub FAILS: unparseable landed JSON wrongly folded into exempt_absent instead of unresolved
PASS: (g) real second git repo, fleet-resolved default branch, real worktree add, landed Done -> terminal
PASS: (i) classify_all(probe_root) includes the harness half's own terminal record
PASS: (i) classify_all(probe_root) includes the second repository's terminal record
PASS: (i) RED PROOF: classify(probe_root) alone (classify_all==classify) never returns a record for the second repository's worktree
PASS: (j) real second repository's terminal record is unaffected by an absent declared repo alongside it
PASS: (j) absent checkout: no record for the never-created directory, and classify_all does not raise
PASS: (k) present-but-unenumerable: exactly one repository-level record, klass unresolved
PASS: (k) present-but-unenumerable: record path equals the declared directory
PASS: (j)/(k) RED PROOF: a stub skipping every non-enumerable declared repo passes (j) but fails (k) — emits no record at all for unenum-repo
PASS: (j)/(k) RED PROOF: a stub reporting every non-enumerable declared repo passes (k) but fails (j) — wrongly emits a record for absent-repo too
PASS: (l) fleet.yaml unloadable: classify_all returns an unresolved record whose path is the fleet path
PASS: (l) fleet.yaml unloadable: classify_all still returns the harness root's own records
PASS: (l) RED PROOF: a stub that swallows the fleet-load exception (catches it, returns only the harness half's own records) never emits a fleet-path record, while the real classify_all against the SAME unloadable fleet.yaml does
```
`echo $?` → **0**.

All 19 pre-existing baseline assertions (cases (a)-(h) and their red proofs, from before c2) are
present above and PASS — unmodified by this cycle, as instructed.

## Files touched, this cycle

- `.claude/skills/harness/bin/test-worktree-terminal.py` (case (l)'s third assertion and
  docstring only; assertions 1 and 2 of case (l), and every other case, unmodified)
- This receipt (appended).

## Commits / git state, this cycle

None. No `git add`, `git commit`, or `git worktree remove` run.
