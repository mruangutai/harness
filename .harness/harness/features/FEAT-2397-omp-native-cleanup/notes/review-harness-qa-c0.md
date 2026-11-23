# QA gate — FEAT-2397 — run r-20261122-4-validate-validator — pin 53a89eb7

**VERDICT: FAIL.** The unit runner is red on two standing scripts that are green at base 522c94b2: `tests/unit/test-lead-stop-and-wake.py` and `tests/unit/test-no-distribution.py`. They are feature regressions. Integration is green (95/95), typecheck is clean, and the standing Repository-state gate also exits 1 at the pin (see Open). A `PASS` with `suite: pass` is not available.

Policy: repo mruangutai/harness, commit 53a89eb70251d1529dbffd8e50959c4590a032f7, path `.harness/harness.json` (read via `git show`). Matrix rows read at the pin: T-01 cross_module (unit+integration), T-02 config (integration if `touches_config_shape`), T-03/T-04/T-06 scaffolding (T-04 is cross_module), T-05 docs. Resolved states: `unit` active, `integration` active, `typecheck` active, `omp_session_accessor` locally_run, `functional` and `eval` excluded, `component` and `ui` unresolved but no task triggers them.

## Phase 1 (from BRIEF/plan only) and the coverage it implied
- SC-01 context bytes parity vs the frozen baseline, plus four-file outcomes in-process.
- SC-02 one decode, a context object, retry and once-only behaviour.
- SC-03 agent/task inputs, legacy `stop_hook_active` rejected, claim retention, identity arms.
- SC-05 preservation of the root-negative suites.
- SC-06 config pin `perCallModel == "off"`.
- SC-07 native finite `usage.tokens`.
- SC-11 offline probe identity/measurement tables.
- SC-04, SC-08, SC-09, SC-12 inspection; SC-10 uat.
- Phase 1 found no test missing for the SCs; two standing tests that the doctrine/rename work should have kept green went red (below).

## Runner receipts (production commands, managed checkout at the pin, `HARNESS_*` env unset, serial)
Command shape: `run-unit-tests.py --kind <k> --shard 1/1 --manifest <F>/runs/r-20261122-4-validate-validator/qa/manifest-<k>.json`.

| kind | receipt | selected/completed | exit | state |
|---|---|---|---|---|
| unit | `qa/manifest-unit.json` (`tested_commit` is the pin) | 67/67 | **1** | red, two named scripts |
| integration | `qa/manifest-integration.json` | 95/95 | 0 | satisfied |
| typecheck | `bun run typecheck` (tsc --noEmit) | n/a | 0 | satisfied |

Wall times: unit 22.9 s, integration 147.8 s. The unit receipt is the runner's own red file; I did not edit it. Full runner output was captured by the session artifacts (unit `local://214.log`, integration `local://223.log`), not written into `runs/`, because bash redirects into `runs/` are blocked for QA.

### The two unit reds (new, not disclosed)
Both scripts exit 0 at base 522c94b2 (run in a second managed pin, `harness-qa-base`, removed on return). Neither is an environment failure.

1. **`tests/unit/test-lead-stop-and-wake.py`** — `FAIL case_floor_DECISIONS.md: zero once-only occurrences found`.
   - T-05's DEC-127/173/208/233 rewrites removed every `ONCE_RE` phrase ("fires at most once…") from DECISIONS.md.
   - The test's floor requires at least one such occurrence.
   - Owner: T-05 (docs). The test file is outside every task's `files:`, so this is a scope-change open question.
2. **`tests/unit/test-no-distribution.py`** — `FAIL case6_absence_the_env_chain_occurs_nowhere`, 14 occurrences of `HARNESS_PROJECT_DIR` outside `test-*`.
   - Sites: `.github/workflows/tests.yml` (12 lines, from the T-02 renames), `check-plan-routes.py:718`, `check_state/ctx.py:295`, `check_state/worktrees.py:112` (T-05 comments).
   - Baseline carried `CLAUDE_PROJECT_DIR` there, so the test did not match.
   - Owner: T-02 and T-05, with the test file outside the task lists.
   - The T-02/T-05 verify blocks never ran the unit kind, which is why this was missed.

### Environment classification (observed in the runner)
- `tests/unit/test-omp-hooks.py` passed in the runner (18.8 s), and `bun test tests/unit/omp-hooks.test.ts` gave 247 pass / 0 fail with `HARNESS_PROJECT_DIR` unset at the pin.
- This confirms the five FEAT-2225 cases are environment-induced and do not appear when the env is clean.
- Integration `test-check-plan-routes.py` (DEVIATION rows) and the canonical-reader suites passed in this runner. The deliberate team-config DEVIATION is a non-failing output line.
- No baseline-versus-feature attribution is needed for these.

## Fail-first per automated SC (the tier is stated for each)
Baseline for the red runs is bdb1c2f6 (identical production to the spec baseline 9eb07b4f per the T-01 note). Files are under `notes/t01-red-green/`, `notes/t04-red-green/`; each ends with its exit code.

| SC | red evidence | tier / class |
|---|---|---|
| SC-01 | `red-A` (9/46, exit 1) for context-object bytes and drift; `red-B` (37/46) for the subprocess checker versus the in-process one; `red-C` mutants m1–m4 redden the parity rows | natural RED for A and B (semantic, byte output); mutation tier for C parity, as the SC allows |
| SC-02 | `red-D` (7 fail, exit 1): one decode, context carried, retired envelope rejected | natural RED, semantic |
| SC-03 | `red-E` dispatch-guard (174/178: agent/task inputs, no model refusal), `red-H` validate-digest (7 failing, truthy legacy `stop_hook_active`), `red-I` TS yield field, `red-J` gate-runtime (605/606), `red-K` identity (28/30) | natural RED, semantic. Claim retention (case 3/9) is in the final suite; I did not find a baseline red for the claim-retention rows alone |
| SC-05 | preservation by the brief: root-negative suites green at the pin; the `t02` transient check is RED at base and GREEN at the pin | the preservation is not a new red |
| SC-06 | `red-G` (31/35; live pin, absent/on/eval fail) | natural RED, semantic |
| SC-07 | `red-L` (37 fail, 9 pass): the `contextUsageTokens` accessor rows fail as "not a function" (signature-absent); the handler-level `context advisory injection` rows fail because the baseline reads JSONL | mixed; the handler rows are semantic RED |
| SC-11 | `t04 red-baseline-2346a777` (AttributeError for 5 of 6 test functions, signature-absent) plus `red-mutants` (10 mutants each exit 1) | signature-absent natural RED plus mutation proof for the semantics |

## Fresh evidence QA produced
- **SC-04** — I ran the plan T-02 `CHECK` heredoc, extracted from the pinned `plan.yaml`, with `HARNESS_PROJECT_DIR=$PWD` in each checkout. At base 522c94b2 it exits 1 (9 workflow steps FAIL, two guidance lines FAIL, and the five helper readers FAIL, with the two-guidance-lines count row OK). At pin 53a89eb7 it exits 0 with every target OK. The builder's `T-02-red-green.md:55` green was the working tree; this closes that gap for the review pin and base.
- **SC-12 code-grade** — `code-grade.py --base 522c94b2 --head 53a89eb7`: exit 0, 80 functions graded, 0 below bar (78 tests at bar 3, 2 production at bar 4, all passing). The listed files are harness_yaml.py, inject-expertise.py, the test-check-* / test-dispatch-guard / test-inject-expertise / test-validate-digest tests, the probe and its unit test. `validate-digest.py::_pass_through` is not in the tool list; the builder's own `grades-changed-functions.txt` records 4 (`hook_mode` 4).
- **SC-12 corpus** — `git ls-files '.harness/*/features/*/feature.json'` at the pin = **34** (positive). The T-05 receipt recorded 31 before the merge.
- **Cumulative gates after all source changes, run at the pin** — T-05's verify literal:
  - canonical-reader audit: 0 unresolved sites across 101 files.
  - instruction paths: 68 files, 0 violations.
  - layout: clean.
  - feature routes: 0 violations (the DEVIATION rows are the disclosed GC-03 output).
  - **check-state exits 1** — see Open.

## Launcher, candidate versus installed
- Live omp: `/Users/molchairuangutai/.bun/bin/omp`, `omp/19.1.0`, sha256 `dca56436…f5abb` (hash of the resolved binary). The T-06 receipt records the same launcher path and version (no hash was required).
- The T-06 receipt's probe blobs match the pin: `probe-omp-session-accessor.py` `81a28131…` and `probe-session-accessors.ts` `8c3e9153…`, both equal to `git rev-parse` at the pin. The observed tree was 59c3becf; the probe blobs are unchanged to the pin.
- Installed control-plane `harness-hooks.ts` hashes `fab2760e…` and the pin's `eb763b58…`. `validate-digest.py` is installed `7e0feb6d…`, pin `21b3ffd1…`. The control plane is at 522c94b2 and runs the pre-change hook. Candidate behaviour was proven only by the tests run from the pin.

## locally_run kind `omp_session_accessor`
I audited, and did not execute, the committed `notes/research-omp1910-observation.md` at the pin. It records launcher/version, a command, 7/7 PASS with exit 0, a nested child (path-identified) with tokens 6827 / window 500000 / percent 1.3654, a distinct flat main, and the #2194 closure JSON (`CLOSED`). The review pin is stated as "whatever later SHA validate pins", with blob identity as the binding. The receipt is adequate. `tripwire-after-t04.md` is a prior smoke run.

## Other kinds
`functional` and `eval` are excluded (DEC-187). `component` and `ui` are unresolved with no triggering task; they are not required here. `handoff_comprehension` and `issue_types_live` are locally_run with no changed detect surface.

## Coverage gaps and open items
1. **Two red unit scripts** (above): T-05 / T-02 fix, or a scope-change decision, with the test files outside the plan's `files:`.
2. **Repository-state gate (`check-state.py`) exits 1 at the pin.** There are eight INV-26 rows, "plan says done, so the card should read building — the board reads review", for T-01..T-06, parent #2411 and source #2397.
   - The pin's `plan.yaml` carries `status: building` while the feature was moved to review. These look like orchestration-state/board mismatches, not code defects, and they read live board state.
   - The T-05 receipt predates the merge and the status flips. Main must reconcile board and plan state, or rule that this gate is evaluated at ship.
3. SC-03 claim-retention rows have no isolated baseline red in the notes (the baseline red for the surrounding hook cases exists).
4. SC-07 and SC-11 reds are partly signature-absent. Semantic discrimination is carried by the handler rows (SC-07) and the mutants (SC-11).
5. Independence: the fail-first runs for SC-01..SC-11 are the builder's own captured runs. I did not rerun the baseline reds, except SC-04 (and the base runs of the two reds).
6. SC-08/09/10/12 inspection items outside this gate are for PM and the reviewers.

## Principles applied
Verification-rules fail-first gate: green was not accepted without a retained red per automated SC. Two unit reds were not excused as environmental, because both scripts are green at base. "Candidate versus installed": hashes recorded and behaviour claimed only from pin runs.

## Correction (same run, appended; the original text above is retained as first written)
1. **SC-03 gap withdrawn.** Open item 3 above ("no isolated baseline red for the claim-retention rows") was wrong. `notes/t01-red-green/red-H-validate-digest-baseline.txt` has natural reds at line 409 (case 3: invalid truthy legacy `stop_hook_active` still refused), line 412 (correction completes and releases the claim) and line 426 (case 9: live-child truthy refusal). Lines 411 and 428 (claim retention) pass at baseline because the old bypass also retained claims; they are preservation assertions, not changed properties. The coverage gap is removed from the digest. The finding came from PM's reading of that file; I had not read those lines myself.
2. **Code-grade scope.** The "80 functions, 0 below bar" result is the canonical `code-grade.py --base 522c94b2 --head 53a89eb7` report only. It does not claim every SC-12 changed function passes. The code-reviewer's changed-body grading (CR-01/CR-55) found 2 changed tests grading 2, which is below the >=3 bar. SC-12 is therefore not discharged by my grade figure, and that finding stands as the reviewer's record.
3. The FAIL verdict and the runner receipts are unchanged.
