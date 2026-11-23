# QA test-matrix gate — FEAT-2452-gh-one-transport, validate cycle 1

**BLUF: PASS, `matrix_ok: true`.** At `64102016cba259b96fcf7761b3f31ec685a65a8c` both required kinds are green, with receipts: unit 67/67 and integration 95/95. All five plan `verify:` blocks exit 0. Each automated SC (SC-01..SC-05) has a named test and red evidence from before the fix. Two qualifications go up as non-blocking findings:

- **(F-1)** The #13 abandon half of SC-05 has no red. It is a guard over behaviour that already held, so SC-05's literal "abandon assertions failing first" is not met.
- **(F-2)** The SC-03 reds are tangled with the offline sentinel, so each case's discrimination was shown by QA's own mutants, not by the natural red.

Run: `r-20261123-5-validate-validator`. Base: `b788e9dac342ee112106a3bc5aa7430d4467cbcb`. Review checkout: `<control plane>/.claude/worktrees/.pins/FEAT-2452-gh-one-transport--r-20261123-5-validate-validator--harness-qa`. `worktree-state --verify` reported `converged`, exit 0. The checkout is not under `$TMPDIR`, so #2442 does not apply: test-factory-config.py exited 0.

## Matrix (policy read at the pin)

- **Policy source:** repository `mruangutai/harness` (unbound Harness feature), commit `64102016cba259b96fcf7761b3f31ec685a65a8c`, blob `.harness/harness.json`, read with `git show`.
- **change_type:** T-01..T-04 are `cross_module`, with `always: [unit, integration]`. T-05 is `docs`, with `always: []`.
- **Required floor:** unit and integration.

| kind | status at pin | state | evidence |
|---|---|---|---|
| unit | active | **satisfied** | exit 0. 67 files discovered and 67 completed, every file exit 0. Receipt `runs/r-20261123-5-validate-validator/qa/manifest-unit.json` (`tested_commit` = pin, `runner_exit` 0, selected 67, completed 67). |
| integration | active | **satisfied** | exit 0. 95 files discovered and 95 completed, every file exit 0. Receipt `.../qa/manifest-integration.json` (`tested_commit` = pin, `runner_exit` 0, selected 95, completed 95). |
| issue_types_live | locally_run | **locally_run** | The diff touches its detect surface (`tests/manual/probe-issue-types.py`, comments only). The recorded run is `notes/issue-types-live-probe.txt` at the pin: `CAPABILITY PRESENT mruangutai/harness …`. |
| functional, eval | excluded (DEC-187) | not_applicable | No `functional`, `eval` or `ai_behavior` task. |
| typecheck | active | not required | The diff contains no `.ts`/`.tsx` file. It ran inside integration anyway: `test-typescript-typecheck.py` exit 0. |
| component, ui | unresolved | not required | No frontend or feature change type, and no `.tsx` in the diff. |

**Runner commands.** Each ran from the review checkout with `HARNESS_AGENT_TYPE` unset, using DEC-255's production command:
`python3 <checkout>/.claude/skills/harness/bin/run-unit-tests.py --kind <kind> --shard 1/1 --manifest <feature tree>/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-5-validate-validator/qa/manifest-<kind>.json`

**Integration ran twice, and the record says why.** The first integration run (16:10:16–16:13:05Z) exited 1 with one red file. It was `test-typescript-typecheck.py`: `FAIL no installed compiler at <checkout>/node_modules/.bin/tsc: run bun install --frozen-lockfile`. That was a missing prerequisite in a fresh checkout. It was not an assertion against this diff, and no test fixture for it was involved. QA supplied the prerequisite with `bun install --frozen-lockfile` in the checkout (exit 0; `git status --porcelain` stayed clean, because node_modules is ignored). The production command was then rerun once (16:13:22–16:16:08Z) and exited 0, 95/95. That rerun overwrote the receipt. The red first run is recorded here, never hidden. Unit ran once: 16:09:51–16:10:16Z, exit 0.

Verdicts come from runner exit and per-file `(exit N)` headers, never from a count of `^FAIL` lines. The full verbatim output stays in the session tool artifacts: about 10.7k lines for unit plus the first integration run, and 8.0k lines for the rerun. The bash write guard refuses a redirect into `notes/`, and the logs are too large to transcribe. Per-file verdicts: unit 67×`exit 0`. Integration run 1: 94×`exit 0` and 1×`exit 1` (typecheck, toolchain). Integration run 2: 95×`exit 0`.

## Plan task `verify:` blocks, verbatim at the pin

| task | exit | result |
|---|---|---|
| T-01 | 0 | 4 files, 4 PASS (factory-gh, gh-cost-log, inv26-routing, inv26) |
| T-02 | 0 | 12 files, 12 PASS |
| T-03 | 0 | 4 files, 4 PASS |
| T-04 | 0 | 2 files, 2 PASS (47 wayfind cases) |
| T-05 | 0 | `PASS policy vocabulary, exit-2 correction, enforcement-ticket readback, live capability receipt and retired-override absence` |

## Fail-first, per automated SC

Each red is classified as one of two kinds:
- **semantic:** a real assertion failed against the named behaviour;
- **signature-absent:** the red is a missing name, which proves no behaviour.

| SC | covering test (pin) | red before fix | class |
|---|---|---|---|
| SC-01 | `tests/unit/test-gh-cost-log.py:529` (counter through launch_gh); `tests/unit/test-factory-gh.py` T-01 cases, incl. create_issue non-ASCII/oversized | `t01-red-green/01-red-test-gh-cost-log.txt`: `FAIL T-01 counter uses launch_gh … AssertionError: unexpected launch` (old `_read_counter` spawned its own subprocess). `01-red-test-factory-gh.txt`: `FAIL T-01 create_issue non-ASCII digits URL … returned` and `oversized … ValueError` | **semantic** for counter routing and URL parsing. 13 of the 15 factory-gh reds are **signature-absent** (`AttributeError: … no attribute 'try_gh'/'GhResult'/'launch_gh'`), so the GhResult/try_gh contract cases prove only presence. Routing of the callers is proven by SC-02's red. |
| SC-02 | `tests/integration/test-gh-sync-open.py:863` `single_override_case` via `gh_sync_support.run` → `offline_gh_env` | `t02-red-green/01-red-confinement-open.txt`: `AssertionError: default gh binary was dispatched: 'auth status'`, empty transcript, no cost lines. Board: `t03-red-green/02-red-confinement-test-board-lifecycle.txt`. Wayfind: `t04-red-green/02-red-confinement.txt` | **semantic, natural** |
| SC-03 | `tests/unit/test-wayfind.py:305` case_6 (401/403/500/network/exit1-no-marker/misleading-404/status0-malformed-with-404/launch), `:318` case_7, `:339` case_9, `:352` case_10, `:363` case_11, `:393-407` case_12/12b/12c, case_5 gist stdin | `t04-red-green/03-red-behaviour.txt`: `FAIL case_6_blockers_401_raises_gh_error ('value', [], '')` and so on for all 16 blocker/parent cases | **semantic but confinement-entangled (F-2).** The old code ignored FACTORY_GH, so every case reached the exit-97 sentinel, not its own fixture. The red proves only that the old code swallowed any failure. |
| SC-04 (c) mirror | `test-gh-sync-open.py:802` `label_failure_case` | `t02-red-green/04-red-behaviour-old-override.txt:52`: `FAIL failed first label create: SKIP, exit 0, and no dependent issue create`, with issue creates after the failed label. The red-only GH_SYNC_GH override got the old code past the sentinel. | **semantic** |
| SC-04 (c) lifecycle | `tests/integration/test-board-lifecycle.py:1600-1605` reconcile LABEL (nonzero / launch failure) | `t03-red-green/03-red-behaviour-lifecycle.txt`: `FAIL reconcile LABEL (nonzero create): both findings survive, exit 1 — rc=0`, label attached after failure | **semantic** |
| SC-04 (d) | `test-gh-sync-open.py:747` `launch_failure_cases` | `t02-red-green/03-red-behaviour-test-gh-sync-open.txt`: `code=None raised=FileNotFoundError(2, …)` for gh and gh_try | **semantic** |
| SC-04 (e) | cut (C5) | No test exists, and none is required. No orphan narrowing test: the pin has no 401/no-lookup milestone case, and `gh-sync.py:1245-1262` keeps lookup-on-any-failure. | SC-04 provides for the cut. **Text-unmet:** SC-04's sentence "looks up … only when … 422 and already exists" is false at the pin. Disclosure #1 and SC-04's own cut clause cover it. The lead or PM should confirm the ship record carries the cut. |
| SC-05 URL | `test-gh-sync-open.py:774` `malformed_url_cases`; `tests/integration/test-gh-backlog-issue-types.py:169-181` CASE I | `04-red-behaviour-old-override.txt`: `ValueError: invalid literal for int() with base 10: 'created'` traceback (parent and task); CASE I `… 'issues'` | **semantic** |
| SC-05 #13 abandon | `tests/integration/test-gh-sync-abandon.py:448-465` | **none.** `t02-red-green/05-red-abandon-old-override.txt` is green on the old code. | **No red (F-1).** |

## Adequacy checks requested

- **SC-02 caller-level single override: present, and it discriminates.**
  - `gh_sync_support.run` (`:215-225`) builds the env with `offline_gh_env`, which strips every `GH_*`, sets only FACTORY_GH and puts a sentinel `gh` first on PATH. The sentinel exits 97 and makes no network call.
  - The real `gh-sync.py open` runs as a subprocess.
  - `assert_sentinel_unused` raises on any default-binary dispatch.
  - The case asserts that every fake-transcript operation is bracketed by the counter, and that there is one gh-cost line per operation.
  - Its natural red on the old code is the sentinel hit `'auth status'`. Any default-binary dispatch therefore fails the test without reaching GitHub, before and after the fix.
- **SC-03 cases:**
  - Status-zero malformed JSON with `(HTTP 404)` in stderr: `READ_FAILURES["status0_malformed_with_404"]` (`test-wayfind.py:300`), for both blockers and parent.
  - Non-404 failures: 401, 403, 500, network, exit 1 without the marker, misleading 404 text, and launch failure, each for blockers and parent.
  - QA ran in-process mutants at the pin. They replace `wf.gh_json_or_absent` in memory; no source was edited.
    - **M2**, which drops `status != 0`, reddens exactly the 2 status0 cases.
    - **M3**, which drops the `(HTTP 404)` marker leg, reddens 12 cases: all non-404 nonzero cases except launch.
    - The baseline stays at 0 FAIL.
  - Each leg of the absence predicate therefore has its own discriminating case.
- **SC-04:** the (c) and (d) reds are listed above. The (e) cut is reflected, and no orphan test is left.

## Findings

- **F-1 · substance · low · T-02** (`tests/integration/test-gh-sync-abandon.py`).
  - SC-05 says "QA demonstrates the new URL/abandon assertions failing first". The #13 assertions passed on the old code (`05-red-abandon-old-override.txt`), so no red exists.
  - QA's perturbation proof of gh-sync's abandon loop was refused. `check-domain` denies a QA edit to `.claude/skills/**`, even inside its own review checkout. Abandon runs as a subprocess, so an in-memory mutant is not possible.
  - Discrimination is **unshown, not disproven** (O-05).
  - **Failure scenario:** a later edit that makes `_close_and_reseat`'s failure path `return` *after* stopping the loop would be caught by the "later item writes" check (it asserts writes to #42, #40 and milestone 7). Whether that check actually discriminates is unproven.
  - **Intent:** #13's continue-policy is preserved and asserted. **Text:** unmet. This routes up as an open question, not as a gate failure: the URL half of SC-05 has semantic red.
- **F-2 · form · info · T-04.** The SC-03 natural reds were all reached through the sentinel, not through each case's own fixture (`t04-red-green.md` § Deviations admits this). The red alone does not prove the status-0 or misleading-404 discrimination. QA's M2/M3 mutants (above) close that gap at the pin.
- **F-3 · substance · info · no task (host).** In a fresh review checkout, integration's `test-typescript-typecheck.py` needs `bun install --frozen-lockfile` before the production runner goes green. This is not a FEAT-2452 defect. Recorded so the next validator doesn't read the red as a regression.

## Phase 1 expectations vs tests (coverage_gaps)

Every Phase-1 expectation derived from BRIEF and plan maps to a test above. The only gap is the #13 abandon discrimination (F-1).

## Principles applied

- **Build the Lever:** the per-case discrimination proofs for SC-03 were run as one scripted in-memory mutant driver over the test module's own case functions, not as hand-flipped edits.
