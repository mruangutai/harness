# qa-c1 — FEAT-25-claim-feature-root

## BLUF

PASS. All three task `verify:` blocks GREEN, both required gate kinds (`unit`, `integration`)
satisfied for FEAT-25's own tests, matrix floor met, SC-08 both clauses clean, SC-07 set-diff
shows zero deletions/weakenings and exactly the one authorised rename. The blocking gate command
(`run-unit-tests.sh --kind integration`) is GREEN at the graded commit `8d7b273` in a clean
worktree (`test-gen-decisions-index.py` PASS there); its exit 1 in the **working tree** is
uncommitted `DECISIONS.md` drift outside the graded diff and outside qa's writable domain — not a
FEAT-25 defect.

## Phase 1 (pre-code) expected coverage, from BRIEF+plan only

- Unpatched-default pin for `FEATURES_ROOT` (equality + isdir), proven red pre-fix.
- End-to-end claim run over the migrated path, no monkeypatch (integration).
- Two distinct diagnostics: absent-root vs. plan-loaded-no-task, each naming the tried path where
  applicable.
- Stream discipline: new diagnostics on stderr only, stdout carries only the JSON payload.
- Layout detector recognizing `factory_claim.py` as a features-surface reader, CLEAN verdict with
  real evidence.
- No regression to existing suites; only the one authorised rename.
- Diff-scope discipline (six files only, forbidden set absent).

Phase 2 (post-code) coverage matches this list closely — no gap found beyond what's noted below.

## Step 0 — commit vs. tree

- `git rev-parse HEAD` = `8d7b273636cfec7fe1cc3d740f70c9153d170b84`, branch
  `feat/FEAT-25-claim-feature-root` — matches dispatch.
- `git diff --name-only d1ffd7f...HEAD` = exactly the six declared files (no more, no less):
  `factory_claim.py`, `layout_fixtures.py`, `layout_migration.py`, `test-factory-claim.py`,
  `test-factory-integration.py`, `test-layout-migration.py`.
- `git diff --stat HEAD -- <six files>` is empty — the working tree is byte-identical to HEAD for
  all six. **The suite measured the graded commit, not merely a tree.**
- `git status --porcelain` shows five modified held-dirt files (`harness-{eng,product,validator}-lead.md`,
  `DECISIONS.md`, `SPEC.md`) plus untracked FEAT-26/FEAT-27 dirs — none of these are among the six,
  none touched by me.

## Step 1 — matrix reading (confirmed, not overturned)

Bug class = path-resolution defect. SC-03 declares `evidence: integration`.
`test-factory-integration.py` is in `test_kinds.integration.detect` AND in `run-unit-tests.sh`'s
`INTEGRATION_SCRIPTS`, and is **absent** from the `--kind unit` run's script list (confirmed —
grepped the full unit-run transcript, it never appears). So under `--kind unit` alone SC-03's
declared evidence never executes. `match_bug_class` → `integration`, required. Union across
T-01(bugfix)/T-02(bugfix)/T-03(logic) = `{unit, integration}`.

Gate commands:
- `run-unit-tests.sh --kind unit` → exit 0. `test-factory-claim.py` PASS (120/120),
  `test-layout-migration.py` PASS incl. `case 22` (41/41 `ok   - ` lines).
- `run-unit-tests.sh --kind integration` → **exit 1**. `test-factory-integration.py` itself PASS
  (106/106). The nonzero exit is `test-gen-decisions-index.py`'s
  `test_committed_index_matches_a_fresh_regeneration`, which fails because the working tree's
  `.harness/harness/docs/DECISIONS.md` (held dirt, uncommitted, explicitly not mine to touch)
  disagrees with a fresh regeneration over DEC-196's `refs:`. **Verified orthogonal**:
  `git diff --stat d1ffd7f...HEAD -- .harness/harness/docs/DECISIONS.md` is empty — this file is
  not part of the graded diff at all, it's pure working-tree drift. Reproduced standalone
  (`python3 test-gen-decisions-index.py`) with the same failure, confirming it is real and
  reproducible, not a fluke of the combined run.

**matrix_ok: true** for FEAT-25's own required kinds — `unit` satisfied, `integration` satisfied.
**Resolved, not left open**: re-ran `run-unit-tests.sh --kind integration` in a clean detached
worktree at `8d7b273` (the graded commit) — **exit 0**, every script including
`test-gen-decisions-index.py` PASS. This proves the working-tree exit 1 is solely a property of
uncommitted `DECISIONS.md` drift (held dirt), not of the commit SC-08 grades. Reported as a
non-blocking `open_question` so whoever owns that edit regenerates the index before the next
person runs the gate over the dirty tree and gets confused by the same exit code.

Kinds not required by `bugfix`/`logic` (BRIEF's "Verification gaps" + DEC-187): `functional` is
`excluded` project-wide; `component`, `ui`, `eval` are simply not in either change type's `always`
list and no criterion invokes them — not applicable, not soft-skipped from a failure.

## Task verify blocks — all three GREEN

Ran each verbatim from `plan.yaml`:
- T-01: `T-01 GREEN` (claim 120/120 ≥116 required, integration 106/106 ≥106 required).
- T-02: `T-02 GREEN` (claim 120/120 ≥120 required).
- T-03: `T-03 GREEN` (layout 41/41 ≥41 required, `test-check-state.py` green — shared stub fixture
  undisturbed).

## Step 2 — the seven judgments

**(1) matrix_ok** — see above. `true`. `unit`: satisfied. `integration`: satisfied (required test
green; unrelated held-dirt failure in a different script, out of FEAT-25's diff).

**(2) Non-vacuity.** All 11 new/renamed ok-line texts (2 T-01 pins, 4 T-02 B5-ter cases, 1 T-02
rename, 2 T-01 integration cases already existing, 1 T-03 case) confirmed **actually emitted**,
exact literal match, via live re-derivation (not quoted from the digest). Confirmed the two
prefixes matter: `"ok    $1"` (T-01/T-02, 4 spaces) vs `"ok   - $1"` (T-03, 3-space-dash) — cross-
testing each literal against the wrong prefix correctly fails. Perturbed 7 representative literals
by one character each; all correctly failed to match (proof each clause CAN fail).
Counts re-derived myself, merged stream: claim=120, integration=106, layout=41 — against baselines
114/106/40 re-derived independently at `d1ffd7f` (via a disposable worktree for the layout suite,
since its "real root" scan needs to sit inside an actual repo checkout; removed after use, `git
worktree list` confirms clean).

**(3) Stream discipline.** Merged (`2>&1`) vs stdout-only (`2>/dev/null`) ok-line counts are
identical for all three suites (120/120, 106/106, 41/41) — no case is counting a stream it
shouldn't. Read the actual assertion code: `run_main()` in `test-factory-claim.py` uses
`contextlib.redirect_stdout(out)` / `redirect_stderr(err)` as **two separate** `io.StringIO()`
captures (lines 399-402), and the B5-ter cases assert `absent_root in err` / `out == ""` against
those separate captures — genuine stream discrimination, not a merged-stream substring check. Same
pattern in T-02's inline python verify (`redirect_stdout(out), redirect_stderr(io.StringIO())`
then `assert out.getvalue() == ""`). This is the opposite shape of the FEAT-24 defect.

**(4) SC-07 set diff** (own script, `diffnames.py` in scratch, comparing `check(...)` literal
names old vs. new):
- `test-factory-claim.py`: **REMOVED 1** — `"(X) sc13b fixture: exactly seven skip lines fired
  (fixture didn't silently short-circuit)"` (the one authorised rename). **ADDED 7** — the T-01
  pair, the T-02 B5-ter quadruple, and the renamed case's new name (`"...exactly eight skip
  lines..."`). Net: exactly what the plan enumerates, nothing else.
- `test-factory-integration.py`: REMOVED 0, ADDED 0 — matches plan (only internal fixture paths
  moved, no new/removed cases).
- `test-layout-migration.py`: REMOVED 0, ADDED 1 (`case 22`) — matches plan.
- Caveat: the extraction regex undercounts by a fixed 6 in both old and new files (one
  f-string-named `check()` inside a loop at line 595, `(R3 {label})`, not statically capturable) —
  confirmed this loop is byte-identical between old and new via direct `diff`, so it doesn't affect
  the delta. Set diff is conclusive, not inconclusive.

**(5) SC-06.** Confirmed via direct introspection (`layout_migration.scan(REPO_ROOT)`), not the
rendered summary line alone: `features` `SurfaceReport` has `evidence={'migrated'}` (non-empty) and
`readers=[..., ('.claude/skills/harness/bin/factory_claim.py', 'migrated'), ...]` — 5 readers
total, `factory_claim.py` enumerated among them with the `migrated` tag. Not an empty-scan CLEAN.

**(6) Red-first claims — empirically re-derived against the `d1ffd7f` copy, without mutating the
main tree** (ran against a `git show`'d snapshot in scratch):
- T-01 pair: pre-fix `FEATURES_ROOT` != migrated join (equality False) and doesn't exist as
  observed from that context (isdir False) — both red pre-fix, both green post-fix (already
  observed in the passing suite run). **The isdir case alone is weak**: it would pass against ANY
  wrong constant that happens to resolve to an existing directory (e.g. accidentally pointing at
  `.harness/harness/docs`); only the **pair** (equality + isdir) discriminates. This matches the
  dispatch's own framing exactly.
- T-02 first two B5-ter cases: re-ran `_blocker_gate` + `_blocker_reason_text` against the pre-fix
  module. Pre-fix, gate = `('edge_i', 'T-01')` (no path-carrying branch exists at all), and the
  resulting text is `"...its title yields no matching plan task (edge (i), lost task
  identity)"` — so `absent_root in text` = **False** (red) and `"no matching plan task" not in
  text` = **False** (red), i.e. both of the first two B5-ter assertions are genuinely red
  pre-fix and green post-fix. Discriminating, not vacuous.

**(7) Coverage per SC** (file:case, can-fail confirmed):
- SC-01: `test-factory-claim.py` — `"the unpatched FEATURES_ROOT default is the migrated harness
  features tree"` + `"...names a directory that exists"` (module scope, lines ~53-58, before any
  patch at line 389). Can fail: yes (shown above).
- SC-02: proven by my own live re-derivation against the `d1ffd7f` snapshot (§6) — both pin cases
  red pre-fix, green post-fix.
- SC-03: `test-factory-integration.py` — `"(F) claim: claimed the T-1 issue (unblocked
  candidate)"`. Confirmed **no monkeypatch of `claim.FEATURES_ROOT`** anywhere in the file (grep);
  the fixture plants the plan at `<root>/.harness/harness/features/<feat>` under an `env`-set
  `CLAUDE_PROJECT_DIR`-equivalent, letting the module's own import-time resolution find it. Can
  fail: yes.
- SC-04: `test-factory-claim.py` — the four B5-ter cases + T-02's inline python
  `_blocker_gate`/`_blocker_reason_text` asserts. Can fail: yes.
- SC-05: `test-factory-claim.py` — `"(B5-ter) absent features root: nothing claimed, zero mutating
  calls, stdout empty"` + T-02 inline `assert out.getvalue() == ""`. Can fail: yes, genuine stream
  separation (§3).
- SC-06: `test-layout-migration.py` — `"case 22: real root's harness/features surface is CLEAN
  with migrated evidence"` + T-03's inline `READER_TABLE`/`STUB` asserts. Can fail: yes (§5).
- SC-07: set-diff evidence above, plus the three count floors (114/106/40) re-derived
  independently. Can fail: yes — a real deletion shows in the REMOVED set.
- SC-08 (inspection, not automated): both clauses checked directly against `git diff --name-only
  d1ffd7f...HEAD` — (a) all six paths ⊆ union of T-01/T-02/T-03 `files:` (exact set match); (b)
  each of the five forbidden files individually absent from the diffed path list, `load_board`
  absent from every added line across all six files (`grep` exit 1). All six verdicts clean,
  individually checked.

## Residuals, not findings

- `test-factory-claim.py:997` and `:1003` still say "seven"/"seven skip reasons" where the fixture
  now holds eight (confirmed present, matches the dispatch's own note). Assertions are
  behaviourally correct (`range(901, 909)`, `len(reasons)` computed dynamically) — labels only.
  Left untouched per instruction.

## Held-dirt failure — resolved as non-blocking, reported for routing

`test-gen-decisions-index.py::test_committed_index_matches_a_fresh_regeneration` fails on the
**working tree** because `.harness/harness/docs/DECISIONS.md` (held dirt, uncommitted, outside
qa's domain) disagrees with a fresh regeneration on DEC-196's `refs:` list. Confirmed via
`git diff --stat d1ffd7f...HEAD -- .harness/harness/docs/DECISIONS.md` (empty) that this file is
not part of FEAT-25's graded diff. **Confirmed at the graded commit**: `git worktree add --detach
.claude/worktrees/qa-head 8d7b273`, ran `run-unit-tests.sh --kind integration` there — exit 0,
`test-gen-decisions-index.py` PASS, `test-factory-integration.py` PASS; worktree removed after
(`git worktree list` shows only the main checkout). The blocking gate is green on the commit it is
supposed to grade. The orchestrator should not route this to FEAT-25 remediation — it needs
whoever owns the `DECISIONS.md` edit (or a regeneration of the index) to resolve, unrelated to this
feature, and non-blocking to FEAT-25's ship decision.
