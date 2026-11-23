# Build — BUG-2399 T-01..T-03 — main-session-direct (DEC-174) — 2026-11-22

## Receipts
- **T-01 red:** `notes/qa-red.json`, taken at `59289ad1` before any production edit. All three suites exit 1, and every FAIL is a BUG-2399 assertion (7 in merge-gitignore, 2 in merge-gate, 3 in feature-worktree). Every pre-existing case passed.
- **T-02:** the main zero-inventory recheck is recorded in the research note (`9eb07b4f`, `selected 0`, exit 0). The focused `test-merge-gitignore.py` gives 14 passed, 0 failed.
- **T-03 green:** `notes/qa-green.json`, all three suites exit 0 with no FAIL line, and the `qa-red.json` hash is preserved. `gen-decisions-index.py --stdout` equals the index. `run-unit-tests.py --kind unit` exits 0 (65 files). `check-state.py` exits 0.

## Deviations (for review)
1. **Verify environment.** Both plan verify scripts set `HOME` to a temp dir to isolate git config, which also hides the user-site `jsonschema` that the suites need since DEC-256. That makes `test-merge-gate.py` crash at import rather than in a BUG-2399 assertion. I ran each verify unchanged, with `PYTHONUSERBASE=$(python3 -m site --user-base)` exported, so `jsonschema` resolves while git stays isolated. The verify text was not amended.
2. **Aborted run shape.** No `ABORTED` status exists in the run-state vocabulary. The regression models an aborted run as what one actually leaves behind: `state.yaml` with `status: in_progress` and a partial `digest.md`, never closed or committed.
3. **Stale statements outside the T-03 file list.** I corrected them so the record stops teaching the old rule:
   - `teams/validate.yaml:40`, `.omp/agents/harness-qa.md:67` and `.omp/agents/harness-validator-lead.md:85-86` said "main force-adds the receipts";
   - `.harness/README.md:33-34` said runs/** is ephemeral scratch that must be ignored.
   Each is a one-line wording change citing DEC-257.
4. **Advisor observation 1, folded into T-02.** I corrected the comment at `feature-worktree.py:341-344` (it claimed `.gitignore:7` ignores `runs/**`); the code is unchanged. Per observation 2, `prune-run-evidence.py` is untouched.
5. **Panel record.** `plan-merge.py record-panel` was re-run from the plan digest so that the `goalcheck` reader is recorded (INV-32). Reader reasons are now the digest's `none`, and both findings were carried.

## Observed flake (not caused by this change: the code path is untouched)
The first run of the T-03 verify failed in the pre-existing `case_landed_differs` (`test-feature-worktree.py`): `git commit` reported `invalid object … for .harness/harness/features/FEAT-97/BRIEF.md`. The suite alone passed twice, and the full T-03 verify then passed three times in a row. The failure is in fixture git plumbing under three concurrent suites, not in the BUG-2399 cases.

## Fleet note
`references/checkout-prereqs.md` still runs `merge-gitignore.py .` unreviewed on a fresh clone. That is safe, because a fresh clone carries no ignored historical files. Existing checkouts go through the new checklist in `checkout-upgrade.md`.
