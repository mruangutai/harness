# QA gate review — BUG-2399 c2 — pin 54c702c7af73568249d51c07771c7727b6003b1f (prior accepted c1 pin ec95d8fb)

Run r-20261122-5-validate-validator. **VERDICT: PASS** — `matrix_ok: true`, `suite: pass`.
Both claimed kinds ran once at the pin and exited 0. No rerun.

## Delta verified, not assumed
`git diff ec95d8fb 54c702c7 --name-only` outside the feature directory = exactly one file, `.claude/skills/harness/references/checkout-upgrade.md` (three path rewordings: the run-UI rule named as `runs/*/ui/**` under each feature; the two layouts named under the checkout's `.harness` directory without a `.harness/` prefix). No script, test or config changed since c1, so the c1 production behavior stands.

## Matrix
Plan change types: T-01 scaffolding, T-02 config (no gate-read shape change), T-03 docs. No `always` kind required. I claim `unit` and `integration` as in c0/c1 (merger, installer, worktree scripts and integration tests are in the full feature diff, P-13).

## Runs
Managed pin, `git rev-parse HEAD` = pin, status clean. `HARNESS_AGENT_TYPE` unset via `env -u`. Inherited env: `GIT_EDITOR/GIT_PAGER/GIT_SEQUENCE_EDITOR/GIT_TERMINAL_PROMPT` only.
Provisioning (QA-Q1): `bun install --frozen-lockfile` in the pin first → `+ @types/bun@1.4.5`, `+ typescript@7.0.2`, 7 packages, exit 0; `node_modules/.bin/tsc` present.
Command: `python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind <kind> --shard 1/1 --manifest <feature>/runs/r-20261122-5-validate-validator/qa/manifest-<kind>.json`.

| kind | selected / completed | runner_exit | tested_commit | wall |
|---|---|---|---|---|
| unit | 65 / 65 | 0 | 54c702c7… (pin) | 56.95s |
| integration | 95 / 95 | 0 | 54c702c7… (pin) | 244.58s |

Receipts are the runner's own files (keys `tested_commit, kind, schema, selected_files, completed_files, runner_exit`), unedited. Counts equal c1 (65, 95). Integration output: zero `^FAIL` lines. Unit output carries the intentional `FAIL BUG-1290` mutation lines; graded by exit code (G-09). Runner PASS lines include `test-merge-gitignore.py`, `test-merge-gate.py`, `test-feature-worktree.py`, `test-gen-decisions-index.py`, `test-typescript-typecheck.py`. Full runner output kept transiently at `/tmp/qa2399-c2-{unit,integration}.out`; slowest integration: test-harness-config-fixtures 151.7s, test-plan-decision-dispositions 106.7s, test-merge-gate 94.2s.

## fail_first (semantic red, preserved from c1; unchanged files)
`git show 54c702c7:<feature>/notes/qa-red.json` sha256 `37c41ab7…c4ab` equals `red_sha256` in the tracked `qa-green.json` (original red receipt preserved byte-for-byte). Red head 59289ad1: test-merge-gitignore, test-merge-gate, test-feature-worktree each exit 1 with BUG-2399 assertion FAIL lines (not import errors). Green receipt head 71a2ac7f: all three exit 0. Current-pin execution of all three suites: this run, exit 0 (the suites and the shipped scripts are byte-identical to c1's pin; only the markdown differs).
Named cases (cited from c1, files unchanged since): SC-01 `bug2399_repository_rules_track_run_records`, `bug2399_fresh_install_tracks_run_records`; SC-02 `bug2399_check_reports_obsolete_broad_rules`, `bug2399_merge_replaces_broad_rules`, `bug2399_merge_corrects_shipped_rationale_only`, `bug2399_line_endings_preserved`, `bug2399_operator_checklist_commands_compose`; SC-03 merge-gate "merge-distill refuses while the distill run's own records are uncommitted" and the feature-worktree aborted-run exit-4 / WOULD DISCARD / byte-identical cases.

## Delta note
The operator-checklist compose test drives the commands directly and does not parse `checkout-upgrade.md` (plan T-01), so the rewording cannot affect it; its pin-run pass is the evidence. Whether the reworded prose is accurate and passes `check-instruction-paths.py` is not part of my gate (code-reviewer/CI); I did not run that gate.

## Coverage gaps (Phase 1)
None for SC-01..03. SC-04 is `verify: inspection` (PM).

## Findings
None. Residual from c1 unchanged: SC-03 removal side uses a hand-built `running` run record (advisor-accepted).

## Principles applied
- Build the Lever: production runner and its own receipts are the evidence; no hand-written harness, no edited receipt.
No tests, fixtures or source authored. Pin removed on return.
