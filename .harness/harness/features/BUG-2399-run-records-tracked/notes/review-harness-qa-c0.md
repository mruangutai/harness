# QA gate review — BUG-2399 c0 — pin 3835fde4f16d1b34d8711fc8607b5153545bfaec (base 59289ad1)

Run r-20261122-3-validate-validator. **VERDICT: FAIL** — `matrix_ok: false`, `suite: fail`.
One genuine defect (T-03), one environmental failure (not attributable to the diff).

## Matrix
`harness.json` change types: T-01 scaffolding (no floor), T-02 config (`integration` only if `touches_config_shape`; no gate-read config shape changes), T-03 docs (no floor). No `always` kind is required. I added `integration` (tests/integration and the installer/worktree scripts changed) and `unit` (runtime `merge-gitignore.py` changed) as warranted by the diff; the matrix does not require either.

## Runs (pinned checkout at the review sha, `git rev-parse HEAD` = pin, clean; HARNESS_AGENT_TYPE unset; HOME untouched so user-site `jsonschema` imported, no PYTHONUSERBASE needed)
Command per kind: `python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind <kind> --shard 1/1 --manifest <abs>/runs/r-20261122-3-validate-validator/qa/manifest-<kind>.json`. Run once each; no rerun.

| kind | discovered/selected/completed | runner exit | receipt |
|---|---|---|---|
| unit | 65 / 65 / 65 | 0 | `runs/r-20261122-3-validate-validator/qa/manifest-unit.json` (tested_commit = pin) |
| integration | 95 / 95 / 95 (95 tracked `tests/integration/test-*.py` at the pin) | **1** | `.../qa/manifest-integration.json` (runner-written; `runner_exit: 1`, not edited) |

Integration failures (2 of 95 files; every other file exit 0; pool 176.94s):
1. **`test-gen-decisions-index.py` — genuine FAIL, owner T-03.** `FAIL - test_committed_index_is_complete_and_within_budget: 1 row(s) in DECISIONS-INDEX.md exceed the 30-word ruling cap: DEC-257 (39)`. I counted the DEC-257 ruling at the pin: 39 words (`git show 3835fde4:.harness/harness/docs/DECISIONS-INDEX.md`). The build ran `gen-decisions-index.py --stdout` equality and `--kind unit` only, so the cap test in the integration bucket was never exercised; plan T-03's verify runs three suites and does not include it.
2. **`test-typescript-typecheck.py` — environmental.** `no installed compiler at <pin>/node_modules/.bin/tsc: run bun install --frozen-lockfile`. A pin carries no `node_modules`; no TypeScript file is in the diff. Not a BUG-2399 defect and not evidence about it, but the integration runner exit is nonzero, so the kind cannot be reported satisfied from this checkout.
(Unit output contains `FAIL BUG-1290 ...` lines from the intentional mutation proof in test-factory-claim-mutation.py; grade by exit code 0.)

## fail_first (original `notes/qa-red.json`, head 59289ad1, tracked at the pin)
Its sha256 `37c41ab7…c4ab` equals `red_sha256` in `notes/qa-green.json` (original preserved). All three suites exit 1 before production edits with BUG-2399-labelled assertions, semantic (not import errors; stderr empty):
- SC-01: `FAIL bug2399_repository_rules_track_run_records: … ordinary git add left run evidence untracked: ['.harness/acme/features/FEAT-1-fixture/runs/r-1/.run-identity.json', …]` and `bug2399_fresh_install_tracks_run_records` (test-merge-gitignore.py).
- SC-02: `bug2399_check_reports_obsolete_broad_rules`, `bug2399_merge_replaces_broad_rules`, `bug2399_merge_corrects_shipped_rationale_only` (seven BUG-2399 FAILs in that suite).
- SC-03: test-merge-gate.py `merge-distill refuses while the distill run's own records are uncommitted`, `ordinary git add stages the distill records and leaves run UI out`; test-feature-worktree.py `aborted run: remove refuses with exit 4`, `…WOULD DISCARD…`, `…evidence survive byte-identical`.
Green: `qa-green.json` head 9c8559bb, three suites exit 0. I did not re-run those three suites separately; they were inside my integration run and all exited 0 there (the prior observed `case_landed_differs` flake did not recur; not rerun to confirm).
SC-04 is `verify: inspection`.

## Pinned artifacts tracked
At the pin `git cat-file -e` succeeds for BRIEF.md, plan.yaml, qa-red.json, qa-green.json, build-T-01-T-03.md, simplify-build-c0.md and the research note. `git check-ignore --no-index` on the pinned `.gitignore` ignores `runs/r-1/ui/a.png` only (rule `.gitignore:12`) and does not ignore `runs/r-1/qa/manifest-unit.json`. DEC-257 is present in DECISIONS.md and the index and refs DEC-238.

## Deviation judgements
- **PYTHONUSERBASE**: confirmed necessary only for the plan verify as written (`HOME=<tmp>` → `ModuleNotFoundError: jsonschema`, reproduced). Not code. Acceptable, but the plan verify blocks T-01/T-03 are not reproducible verbatim on this host; low, plan text.
- **Interrupted-run fixture**: no ABORTED vocabulary exists (grep of feature-worktree.py, feature-record.py, SPEC finds none). The fixture (`test-feature-worktree.py case_remove_refuses_aborted_run_evidence`) uses the repo's real `.gitignore`, an unclosed `status: in_progress` state.yaml plus partial digest.md, and asserts exit 4, WOULD DISCARD and byte survival. Reasonable; it did not exercise a real aborted flow. Low.
- **Stale role-doc edits outside T-03 files** (`teams/validate.yaml`, `.omp/agents/harness-qa.md`, `.omp/agents/harness-validator-lead.md`, `.harness/README.md`): diffs read — single-statement wording changes ("main force-adds" → "committed … (DEC-257)"), consistent with the policy, no enforcement logic touched. Acceptable; scope deviation is documented.

## Coverage gaps (Phase 1 versus tests)
None for SC-01..03. Residual: SC-03 removal side models an in-progress record, not a real aborted-state producer.

## Findings
- F-1 (defect, T-03, blocking): DEC-257 index ruling is 39 words > 30 cap; `test-gen-decisions-index.py` red; integration runner_exit 1.
- F-2 (environment, no owner): `test-typescript-typecheck.py` needs `node_modules` the pin lacks; integration runner exit nonzero in this checkout.
- F-3 (plan text, T-01/T-03, low): verify blocks require `PYTHONUSERBASE` on this host.

## Principles applied
- Build the Lever: used the production runner and its receipts as the lever; no hand-written scripts, no receipt edits.

No tests, fixtures or source authored.
