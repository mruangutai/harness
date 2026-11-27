# QA test-matrix gate — FEAT-2452-gh-one-transport, validate c1 (fix pin)

**BLUF: PASS, `matrix_ok: true`.** At `e282689dd01a1a45eb22f08be67b1e2a9b437fb1`, unit 67/67 and integration 95/95 are green, with DEC-255 receipts. All five plan `verify:` blocks exit 0. Every `verify: automated` SC (SC-01..SC-05) has a named test and a red from before the fix. G1 is closed: I reproduced the #13-shaped abandon red myself at `15a240bc`. P1, P2 and P3 are confirmed. P4 is partly refuted: the unit seam still catches a dropped label **attachment**, but not a dropped label **create**. The create is caught only at the integration layer, and that blindness predates this fix (F-1). Two findings, both non-blocking.

- **Run:** `r-20261123-6-validate-validator`.
- **Base:** `b788e9dac342ee112106a3bc5aa7430d4467cbcb`. The fix delta is `64102016..e282689d`, and its code is byte-identical at `15a240bc`: `git diff --stat 64102016 15a240bc -- .claude tests` is empty.
- **Review checkout:** `<control plane>/.claude/worktrees/.pins/FEAT-2452-gh-one-transport--r-20261123-6-validate-validator--harness-qa`. `worktree-state.py --verify` reported `converged`, exit 0. `git status --porcelain` was clean before and after every run.
- **Environment:** every run had `HARNESS_AGENT_TYPE`, `CLAUDE_PROJECT_DIR` and `HARNESS_ROOT` unset. Before the runs I did `bun install --frozen-lockfile` in the pin (exit 0), per the OQ-QA-3 ruling.

## Matrix (policy read at the pin)

- **Policy source:** repository `mruangutai/harness` (unbound Harness feature), commit `e282689dd01a1a45eb22f08be67b1e2a9b437fb1`, blob `.harness/harness.json`, read with `git show`.
- **Required kinds:** T-01..T-04 are `cross_module`, with `always: [unit, integration]`. T-05 is `docs`, with `always: []`. The floor is **unit and integration**. The predicates were resolved over the full feature diff `b788e9da..e282689d` (169 paths), not just the fix delta.

| kind | status at pin | state | evidence |
|---|---|---|---|
| unit | active | **satisfied** | Runner exit 0, 16:38:18–16:38:42Z. 67 discovered, 67 completed, 67 file headers `(exit 0, …)`, 0 nonzero. Receipt `runs/r-20261123-6-validate-validator/qa/manifest-unit.json`: `tested_commit` = pin, `runner_exit` 0, selected 67, completed 67. |
| integration | active | **satisfied** | Runner exit 0, 16:38:42–16:41:22Z, **one run**. 95 discovered, 95 completed, 95 file headers `(exit 0, …)`, 0 nonzero. Receipt `.../qa/manifest-integration.json`: `tested_commit` = pin, `runner_exit` 0, selected 95, completed 95. |
| issue_types_live | locally_run | **locally_run** | The diff touches its detect surface: `tests/manual/probe-issue-types.py`, comments only. The fix delta does not. The recorded run at the pin is `notes/issue-types-live-probe.txt`: `probe-issue-types: CAPABILITY PRESENT mruangutai/harness declares native issue types Bug, Feature, Task`. |
| functional, eval | excluded | not_applicable | No functional or ai_behavior task. |
| typecheck | active | not required | No `.ts` or `.tsx` file in base..head. It ran inside integration anyway (`test-typescript-typecheck.py`, exit 0). |
| component, ui | unresolved | not required | No frontend or feature change type, and no matching path. |

**Runner command:** DEC-255's production command, once per kind, serially:
`python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind <kind> --shard 1/1 --manifest /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-6-validate-validator/qa/manifest-<kind>.json`

**Output:**
- Unit: 2,770 lines; it ends with `pool: 8 workers, 67 files, 24.69s wall`.
- Integration: 8,020 lines; it ends with `ALL PASSED. … pool: 8 workers, 95 files, 159.05s wall`.
- Verdicts come from the runner exit and the per-file `(exit N)` headers, never from a count of `^FAIL` lines.
- The verbatim logs are in host scratch, `/tmp/qa-2452-c2/{unit,integration}.txt`. The logs are too large to transcribe, and QA's only `runs/` grant is the receipts, so the counts above are the durable record.

## Plan `verify:` blocks (verbatim from the pin's plan.yaml, run from the pin)

| task | exit | tail |
|---|---|---|
| T-01 | 0 | `pool: 4 workers, 4 files` — all PASS |
| T-02 | 0 | `pool: 4 workers, 12 files` — all PASS |
| T-03 | 0 | `pool: 3 workers, 4 files` — all PASS |
| T-04 | 0 | `pool: 2 workers, 2 files` — all PASS |
| T-05 | 0 | `PASS policy vocabulary, exit-2 correction, enforcement-ticket readback, live capability receipt and retired-override absence` |

## Predictions

- **P1: confirmed (G1 / SC-05 #13).**
  - **The dev's reds are genuine assertion reds.** In `fix-c1-FixD1_Mirror/01-red-label-create-head.txt` and `05-red-final-tests-at-15a240bc.txt` (gh-sync blob `86ddc86f`), exactly 6 checks fail, with exit 1, and every legacy check is `ok`.
    - The failing values are real behaviour: `rc=0 gh-sync: SKIP — label abandoned could not be created … HTTP 403`, a call log holding only `auth status` and `label create abandoned`, and station `building`.
    - For reject: `rc=0 … parent #40 closed … SKIP`, with no halt report.
    - There is no sentinel hit and no traceback.
  - **My own reproduction matches.** I made a second managed pin at `15a240bc367c…`, restored the two pin test files into it with `git checkout e282689d -- tests/integration/test-gh-sync-abandon.py tests/integration/gh_sync_support.py`, and ran the file. It exited 1, with the same 6 FAIL lines and 180 `ok`. The restore was clean afterwards.
  - **Green at the pin.** In my integration run (lines 5838–5841 and 5880–5882) every `abandon, label create fails` and `reject, label create fails` check is `ok`.
- **P2: confirmed (H2).**
  - `fix-c1-FixD1_Wayfind/01-red-wayfind.txt` has 28 FAIL. All are `case_8b`, `case_10b` or `case_11b`, and 57 pre-existing cases PASS.
  - The reds are semantic, not signature-absent. Examples: `('value', [], '')` for a null blocker payload; `#11 eligible?` printed and `issue view` read for frontier; `has no parent map` or the title read for resolve.
  - I reproduced it independently by running the pin's `test-wayfind.py` with `wayfind` replaced in memory by its `64102016` blob (`/tmp/qa-2452-c2/old_module_driver.py`; the install marker fired). The result was 28 FAIL, all 28 in the new cases, and 57 PASS, exit 1. The control run with the `e282689d` blob gave 85 PASS, exit 0.
- **P3: confirmed (A1).**
  - `02-red-factory-gh.txt` shows `4 of 324 FAILING`: query-char, userinfo, fragment and bare-port authority. `https:///` was already rejected before the fix, so it is a guard.
  - My in-memory reproduction with `factory_gh@64102016` gave the same 4 FAIL, exit 1. With `@e282689d` it gave `324/324`. In the pin's unit run the cases at `test-factory-gh.py` lines 886–890 are `ok`.
- **P4: partly refuted. The seam still discriminates the attachment, but not the create (F-1).** I mutated `tests/unit/test-gh-sync-abandon-sources.py` in memory (`/tmp/qa-2452-c2/p4_driver.py`; no file edited):
  - **Baseline:** ALL PASSED. The seam was reached 14 times.
  - **Seam returns a failure line:** `AS-07` and `AS-17` go red, because no `--add-label` edits are made. A failed create therefore still discriminates abandon's attachment leg, and the None-returning lambda still means success.
  - **gh-sync mutant `label_gap = None`:** abandon never calls `ensure_labels`. The mutant install marker fired, the seam was reached 0 times, and the file stayed **ALL PASSED**. The file has no assertion on the `("labels", …)` event, so dropping the create is invisible to the unit floor.
  - Not vacuous overall, and not a new defect: at base the lambda was identical and also unasserted.
  - The integration `abandon_label_create_failure_case` does catch a dropped create: `the failed create named with its diagnostic` requires the 403 create line.

## Fail-first, per `verify: automated` SC

| SC | covering test (pin) | red before fix | class |
|---|---|---|---|
| SC-01 | `tests/unit/test-gh-cost-log.py:494-` (counter through `launch_gh`); `tests/unit/test-factory-gh.py:2186-2218` (URL parser incl. A1) | `t01-red-green/01-red-test-gh-cost-log.txt` (`unexpected launch`); `t01-red-green/01-red-test-factory-gh.txt` (URL non-ASCII/oversized); `fix-c1-FixD1_Wayfind/02-red-factory-gh.txt` `4 of 324 FAILING`, reproduced by QA | semantic (the c0 note's signature-absent caveat on 13 GhResult cases still stands) |
| SC-02 | `tests/integration/test-gh-sync-open.py:863` `single_override_case` | `t02-red-green/01-red-confinement-open.txt`: `default gh binary was dispatched: 'auth status'` | semantic, natural |
| SC-03 | `tests/unit/test-wayfind.py:305` case_6, `:318` case_7, `:387` case_8b, `:397` case_10b, `:410` case_11b | `t04-red-green/03-red-behaviour.txt` (c0; the M2/M3 mutants closed the sentinel entanglement); `fix-c1-FixD1_Wayfind/01-red-wayfind.txt` 28 FAIL in the new cases, reproduced by QA at `64102016` | semantic |
| SC-04 | `test-gh-sync-open.py:802` `label_failure_case`, `:747` `launch_failure_cases`; `tests/integration/test-board-lifecycle.py:1600-1605`; `tests/integration/test-gh-sync-abandon.py:70` and `:97` (caller policy after a failed create) | `t02-red-green/04-red-behaviour-old-override.txt`; `t02-red-green/03-red-behaviour-test-gh-sync-open.txt`; `t03-red-green/03-red-behaviour-lifecycle.txt`; `fix-c1-FixD1_Mirror/05-red-final-tests-at-15a240bc.txt`, reproduced by QA | semantic. (e) is cut under C5 (ruled) |
| SC-05 URL | `test-gh-sync-open.py:774` `malformed_url_cases`; `tests/integration/test-gh-backlog-issue-types.py:169` CASE I | `t02-red-green/04-red-behaviour-old-override.txt` (`ValueError: invalid literal for int()`) | semantic |
| SC-05 #13 | `tests/integration/test-gh-sync-abandon.py:70` `abandon_label_create_failure_case` (red); `:539-546` close-failure #13 case (guard) | `fix-c1-FixD1_Mirror/05-red-final-tests-at-15a240bc.txt` lines 49–56; QA reproduction `/tmp/qa-2452-c2/repro-abandon-15a240bc.txt` (exit 1, 6 FAILED) | semantic, natural (see F-2 on scope) |

## Regression check on the fix delta

- **Every former SKIP caller moved to `mirror_labels`.** At `64102016`, `ensure_labels` had five call sites: two in `_open_ensure_labels`, one in `_finish_replacement`, one in abandon and one in reject.
  - At the pin the first three are `mirror_labels`, so SKIP/0 is kept.
  - Abandon reports and continues; reject raises `_RejectHalt`.
  - The `open` label guard and existing-label acceptance stay green in my integration run.
- **`ABSENT` is used only by `blockers()` and `parent_of()`.** No other caller of `gh_json_or_absent` exists. `case_7`, where a genuine 404 means absence, is green.
- **The A1 regex still accepts a GHE host with a port** (`t01_issue_number_from_url_accepts`, green).

## Findings

- **F-1 · substance · info · T-02.**
  - **What:** the unit seam `tests/unit/test-gh-sync-abandon-sources.py` cannot see whether abandon's label **create** runs. Mutant `label_gap = None` dropped all 14 seam calls and the file stayed ALL PASSED. The attachment leg does discriminate: AS-07 and AS-17 redden when the seam returns a failure.
  - **Failure scenario:** a refactor that drops `ensure_labels(repo, {"abandoned"})` from `cmd_abandon` passes the unit floor. Abandon would then attach a label the repo may not define, and only `test-gh-sync-abandon.py:70` catches it.
  - **Status:** it predates this feature (the base lambda is identical), so it is not a fix-c1 regression. To close it, assert `("labels", ["abandoned"])` precedes the first `issue edit` in one AS case.
- **F-2 · form · low · T-02 (SC-05 #13 scope).**
  - **What:** G1 is closed by reading a failed label **create** as #13's "a failing abandon API call". That create is a REST call made by abandon, and the red shows later per-item writes and the local station being dropped, so the reading is sound. The literal close-failure #13 case at `:539-546` is still preservation-only, with no red of its own, as in c0.
  - **Failure scenario:** only if SC-05 is read as "the close call specifically" does the gap reopen. The PM goal-check should state which reading it accepts.
- **O-07 disclosure.** The fixes landed after the c0 review. Their red/green has been examined only by the dev and by QA's reproductions here.

## Phase 1 expectations vs tests (coverage_gaps)

From BRIEF and plan, SC-01..SC-05 each needed a unit or integration test with a prior red. All are mapped above. Remaining gaps:
- F-1, unit-layer blindness to the abandon label create;
- the #13 close-failure case has no red of its own (F-2).

## Cleanup

Both managed pins were removed with `pinned-checkout.py remove` on return: `…--harness-qa` and `…-red--harness-qa`.

## Principles applied

- **Build the Lever:** the old-blob reproductions for P2/P3 and the P4 mutants ran through two scripted in-memory drivers (`old_module_driver.py`, `p4_driver.py`) over the pin's own test files. No source or test edits were hand-flipped.
