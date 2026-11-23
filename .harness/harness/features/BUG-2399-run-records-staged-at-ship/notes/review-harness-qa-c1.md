# QA gate — BUG-2399 T-01, cycle 1, run 2026-11-23-02-validate-validator

**Verdict: PASS, with advisory coverage gaps (all form/low).** Matrix satisfied, unit receipt recorded, fail-first bound for SC-01 and SC-02.

## Matrix (Phase 1 was done from BRIEF and plan only)
- T-01 `change_type: bugfix`. harness.json: `always: []`; `unit` when `touches_runtime_code` (true: `.claude/skills/harness/bin/prune-run-evidence.py`); `integration` when `fix_confined_to_tests_and_contract_docs` (false: runtime code changed); `__bug_class__` placeholder never fires (repo Expertise G-08). Required: **unit only**.
- unit `cmd` runs `tests/unit/test-*.py`; `tests/unit/test-prune-run-evidence.py` is a member of the 65-file selection (P-14 checked: manifest `completed_files` names it, returncode 0).

## Runner receipt (DEC-255)
- Pin: `.claude/worktrees/.pins/BUG-2399-run-records-staged-at-ship--2026-11-23-02-validate-validator--harness-qa`, HEAD `9db1ba98209df49017e73fae13da56f3e240086c`, clean.
- Command (HARNESS_AGENT_TYPE, CLAUDE_PROJECT_DIR, HARNESS_PROJECT_DIR unset): `python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind unit --shard 1/1 --manifest <feature>/runs/2026-11-23-02-validate-validator/qa/manifest-unit.json`
- Result: exit 0; 65 files, 0 nonzero; manifest `tested_commit` 9db1ba98..., `runner_exit` 0. Full output was kept at `/tmp/qa-b2399-unit.log` (2498 lines; the write guard refused a copy into notes). The prune test block, runner lines 2434-2472: 36 PASS, `all checks passed`, exit 0, 4.13s.
- Installed-vs-candidate: this diff changes `prune-run-evidence.py`, not a gate or hook enforcing this run; the receipt is the candidate's own run.

## Fail-first (natural RED, signature-bearing assertion diffs, not mutation)
Independent check of `notes/red-first-T-01.md`: sha256 of the test file at the pin is `1f896bd0...08bc` and of the pruner at the pin is `4ccdd6bf...b08c`; both equal the red note's. The base pruner blob at 9eb07b4f hashes `3ce3bb40...af9`, equal to the note's red subject. So the red run used exactly the pinned test against the exact base. I did not rerun it, as directed. Each of the 9 named FAILs maps to a new check whose assertion cannot hold at base (the base has no staging or evidence refusal): staged index empty, rc 0 where 2 was expected, no `would stage` lines. stderr was empty and 27 checks passed (25 pre-existing), so the failures are assertion diffs, not import or setup errors. Count is 9 of 11 new checks; the other 2 pass at base vacuously (dry-run immutability, no-ui/no-stray staged) and are paired with presence checks.
- SC-01: `staging_prune` (test:204), `staging_dry_run` (:194), repeat prune, `symlink_staging` (:320).
- SC-02: `evidence_refused` (:239, prune and dry-run, naming two missing paths), `evidence_complete` (:248).

## Claims graded
- No manual force-add text at base: **confirmed** (`git show 9eb07b4f:.omp/commands/harness-ship.md | grep -i 'force\|add -f\|git add'` is empty). SC-03's "manual force-add is removed" therefore removes nothing; the intent (no hand step, auto-staged) is met, the literal text is vacuous (O-04, form).
- Exit 1 on git-add failure versus exit 2 on refusal: true in code (`_stage` returns 1; `_refuse` 2) and docstring. **Untested**, and exit 1 arrives after the UI prune already ran, so it is not atomic.
- Unsafe ids not staged: `_recorded_run_ids` filters empty, `.`, `..` and ids with separators. **Untested**; the fixtures use only plain ids.
- Only top-level run ui excluded: true in code (`current == run_dir and "ui" in dirs`). **Untested**: no fixture holds a nested `ui/` such as `qa/ui/x`. A mutant that excludes any `ui` dir at any depth passes the suite.
- Missing means absent on disk, not hash invalidity: true (`os.path.isfile`). Test removes files only; no case keeps a hash-mismatched file and expects success, or a directory at the path.

## Coverage adequacy
Adequate: dry-run (names, bytes and index byte-identical), nested qa/ survivor beside notes/ (allowlist mutant caught), arbitrary non-UI sentinel, kept and pruned recorded runs, unrecorded stray run, linked run and linked subdirectory, repeat prune, refusal with two missing paths and no file or index change in either mode.
Gaps (advisory, form unless noted): (1) exit-1 git failure; (2) unsafe run ids; (3) nested `ui/` staged; (4) symlinked file skip in `_run_files`; (5) hash-mismatch not refused; (6) a `cycle_evidence` path escaping the feature dir counts as present if the file exists (substance-low, edge).

## Principles applied
None cited beyond harness-verification-rules (matrix, receipts, fail-first, absence pairing).
