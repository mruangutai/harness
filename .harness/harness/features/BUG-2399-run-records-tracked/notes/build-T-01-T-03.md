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

## Fix c1 (after validate c0 FAIL, main-session-direct, rework round 1)
- **T-02 grade:** `merge-gitignore.py` `_without_obsolete` now delegates its two predicates (`_is_obsolete`, `_still_in_block`); `_merge` delegates to `_report_check`, `_apply` and `_report_removed`. Behaviour is unchanged and the merger suite gives 14 passed. `code-grade.py --base 59289ad1` shows no production failure.
- **T-01 grade:** the checklist composition test is split into `seed_fleet_checkout`, `stage_reviewed_evidence` and `require_operator_commit`, with the same assertions. Three grade-2 test functions remain, each with the reviewer's accepted reason.
- **T-03 index cap:** the DEC-257 index ruling now fits the 30-word cap. `test-gen-decisions-index.py` has no FAIL.
- **GC-F1 (advisor: AMEND→T-01):** the aborted-run fixture now uses the documented seed status `running` (`references/team-run-state.md:34`). An interrupted-run producer is out of scope, and that gap is accepted: the removal gate reads only git dirt.
- **GC-F2 (advisor: AMEND):** `plan-merge.py amend` records the four doc paths in T-03's files and `feature-worktree.py#_gate_removal` in T-02's, each ledgered as an amendment judgement.
- **QA-Q1 (advisor):** the fix run's QA provisions `bun install --frozen-lockfile` in its pinned checkout and records the command with the receipt. PR CI is not a substitute.
- **Fleet-note check (advisor flag):** `git clone` checks out tracked files only, so a fresh clone holds no ignored historical run files for `merge-gitignore.py .` to expose.
- The terminal three-suite verify was re-run green (`qa-green.json` rewritten), with `qa-red.json` preserved.

## Fix c2 (PR #2427 CI red: instruction-path gate)
I ran the plan's verify commands, the unit suite and check-state before the PR, but not every CI gate. The `checks` job's Instruction-path gate (`check-instruction-paths.py`) refused three unanchored `.harness/…` paths in the new `checkout-upgrade.md` checklist (lines 41 and 49). Those paths name locations in the operator's target checkout, which is neither the control plane nor the feature tree, so neither anchor is correct. The fix rewords them without the `.harness/` prefix ("`runs/*/ui/**` under each feature"; layouts "under the checkout's `.harness` directory"), so the gate reports 0 violations; the meaning is unchanged. Before re-pinning, the remaining CI gates were run locally and all exit 0: plan-route, canonical-reader audit and layout.
