# QA gate review — BUG-2399 c1 — pin ec95d8fb6167cfe199c4a30d4b20860d852c48f0 (base 59289ad1)

Run r-20261122-4-validate-validator. **VERDICT: PASS** — `matrix_ok: true`, `suite: pass`.
Both claimed kinds ran once at the pin and exited 0. No rerun.

## Matrix
Plan change types: T-01 scaffolding, T-02 config (no gate-read config shape change), T-03 docs. Matrix requires no `always` kind. I claim `unit` and `integration` as warranted by the diff (merger, installer and worktree scripts and the integration tests changed), as in c0.

## Runs
Checkout: managed pin, `git rev-parse HEAD` = pin, status clean. `HARNESS_AGENT_TYPE` unset via `env -u`. Inherited env had `GIT_EDITOR/GIT_PAGER/GIT_SEQUENCE_EDITOR/GIT_TERMINAL_PROMPT` only (no repo-root variables).
Provisioning (QA-Q1): `bun install --frozen-lockfile` in the pin → `+ typescript@7.0.2`, 7 packages, exit 0; `node_modules/.bin/tsc` present.
Command per kind: `python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind <kind> --shard 1/1 --manifest <feature>/runs/r-20261122-4-validate-validator/qa/manifest-<kind>.json`.

| kind | selected / completed | runner exit | tested_commit | wall |
|---|---|---|---|---|
| unit | 65 / 65 | 0 | ec95d8fb… (pin) | 24.4s |
| integration | 95 / 95 | 0 | ec95d8fb… (pin) | 282.5s |

Receipts are the runner's own files, unedited. 95 = tracked `tests/integration/test-*.py` at the pin. Unit output carries the intentional `FAIL BUG-1290` mutation-proof lines; I graded by exit code. Integration output has zero `FAIL` lines.
Output kept at `/tmp/qa2399-c1-{unit,int}.out` (transient). The runner PASS lines include `test-gen-decisions-index.py` (index cap, was the c0 defect F-1: now green), `test-typescript-typecheck.py` (c0 environmental F-2: now green after provisioning), `test-merge-gitignore.py`, `test-merge-gate.py`, `test-feature-worktree.py`.

## c0 findings, at this pin
- F-1 DEC-257 index ruling 39 words > 30: closed. The pinned cap test (`tests/integration/test-gen-decisions-index.py:438`, `word_count > 30`) passed at the pin.
- F-2 tsc missing: closed by provisioning, not by dropping the test.
- F-3 plan verify needs `PYTHONUSERBASE`: unchanged, plan text, low (not re-measured).

## fail_first (semantic red, preserved)
Original `notes/qa-red.json` at the pin: sha256 `37c41ab7…c4ab` equals `red_sha256` in the pinned `qa-green.json` (original preserved byte-for-byte). Red head 59289ad1, six production hashes recorded; all three suites exit 1 with BUG-2399 assertion FAIL lines (not import errors, empty stderr). The tracked `qa-green.json` records head 71a2ac7f, three suites exit 0.
Current-pin named cases (all passed in my integration run, test files read at ec95d8fb):
- SC-01: `bug2399_repository_rules_track_run_records`, `bug2399_fresh_install_tracks_run_records` (red: "ordinary git add left run evidence untracked: …").
- SC-02: `bug2399_check_reports_obsolete_broad_rules`, `bug2399_merge_replaces_broad_rules`, `bug2399_merge_corrects_shipped_rationale_only`, `bug2399_line_endings_preserved`, `bug2399_operator_checklist_commands_compose` (the latter two exist at the pin and passed; whether each was in the red set is not separable from the 7 recorded merge-gitignore FAILs, which I did not enumerate per name).
- SC-03: `test-merge-gate.py` "merge-distill refuses while the distill run's own records are uncommitted", "ordinary git add stages the distill records…", "the same distill merges once, at the new head…"; `test-feature-worktree.py` "aborted run: remove refuses with exit 4", "…WOULD DISCARD…", "…survive byte-identical".

## Fix-c1 delta judgements
- `71a2ac7f..ec95d8fb` changes `test-feature-worktree.py` by one line (fixture `status: in_progress` → `status: running`, line 1051). The pinned `qa-green.json` (head 71a2ac7f) therefore did not execute that line. My c1 integration run is the current-pin execution: the three aborted-run cases pass. The red receipt predates the fixture edit; the assertions it reddened (exit 4, WOULD DISCARD, byte survival) are unchanged, and the status value is not what they key on (removal reads git dirt). Rank: natural RED (receipt) for the behavior, current-pin GREEN from this run.
- Residual (accepted by advisor): no interrupted-run producer; the fixture is a hand-written `running` record.
- Not confirmed by me: the three c0 grade-2 test reasons and the high-grade splits (code-reviewer scope); I ran no `code-grade.py`.

## Coverage gaps (Phase 1)
None for SC-01..03. SC-04 is `verify: inspection` (PM).

## Findings
None blocking. Residual noted: SC-03 removal side uses a hand-built unclosed run state.

## Principles applied
- Build the Lever: production runner and its receipts are the evidence; no hand-written harness, no edited receipt.
No tests, fixtures or source authored. Pin removed on return.
