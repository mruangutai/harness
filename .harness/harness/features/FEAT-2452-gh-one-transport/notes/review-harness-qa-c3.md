# QA test-matrix gate — FEAT-2452-gh-one-transport, validate c2 (fix-c2 pin)

**BLUF: PASS, `matrix_ok: true`.** At `caeebc7cb24b7205bb5d5ad5191cd6541fc3519a`, unit 67/67 and integration 95/95 are green, with DEC-255 receipts. All five plan `verify:` blocks exit 0. I reproduced the fix-c2 reds myself in a managed checkout at `3465716a`:
- `test-wayfind.py`: 115 FAIL / 123 PASS, exit 1. All 50 new input classes are red and every control is green.
- `test-factory-gh.py`: 17 of 345 FAILING, exit 1.

These match the builder's counts exactly. The M1 input classes the prior must_fix named are each covered and were each red. The EMU owner accept case discriminates: a mutant using the builder's narrower owner class reddens it. The fix delta touches no enforcement file. There are two non-blocking advisories (A-1, A-2).

- **Run:** `r-20261123-7-validate-validator`.
- **Base:** `b788e9dac342ee112106a3bc5aa7430d4467cbcb`. The fix delta is `3465716a..caeebc7c`, and its code paths are only `factory_gh.py`, `wayfind.py`, `github-mirror.md`, `tests/unit/test-factory-gh.py` and `tests/unit/test-wayfind.py`.
- **Checkouts (managed, `pinned-checkout.py`):**
  - `.pins/FEAT-2452-gh-one-transport--r-20261123-7-validate-validator--harness-qa` @ `caeebc7c`.
  - `.pins/…--r-20261123-7-validate-validator-red--harness-qa` @ `3465716afc164e155658adc99b0929684d5a447e`.
  - `worktree-state.py --verify` reported `converged` (exit 0) for both. `git status --porcelain` was clean before and after every run, and after restoring the red pin.
- **Environment:** every run had `HARNESS_AGENT_TYPE`, `CLAUDE_PROJECT_DIR` and `HARNESS_ROOT` unset. I ran `bun install --frozen-lockfile` in the pin first (exit 0), per OQ-QA-3.

## Matrix (policy read at the pin)

- **Policy source:** repository `mruangutai/harness` (unbound Harness feature), commit `caeebc7cb24b7205bb5d5ad5191cd6541fc3519a`, blob `.harness/harness.json`, read with `git show`.
- **Required kinds:** T-01..T-04 are `cross_module`, with `always: [unit, integration]`. T-05 is `docs`, with `always: []`. The floor is **unit and integration**.
- **Diff object:** I resolved the predicates over the full feature diff `b788e9da..caeebc7c`: 201 paths, 30 of them outside the feature directory. It has 0 `.ts`/`.tsx` paths and no component, e2e, eval or functional paths.

| kind | status at pin | state | evidence |
|---|---|---|---|
| unit | active | **satisfied** | Runner exit 0, 17:01:01–17:01:26Z. 67 discovered, 67 file headers `(exit 0, …)`, 0 nonzero. `test-factory-gh.py` 345/345 and `test-wayfind.py` PASS. Receipt `runs/r-20261123-7-validate-validator/qa/manifest-unit.json`: `tested_commit` caeebc7c…, `runner_exit` 0, selected 67, completed 67. |
| integration | active | **satisfied** | Runner exit 0, 17:01:31–17:04:01Z, **one run**, after unit finished. 95 discovered, 95 headers `(exit 0, …)`, 0 nonzero, `ALL PASSED.` Receipt `…/qa/manifest-integration.json`: `tested_commit` caeebc7c…, `runner_exit` 0, selected 95, completed 95. |
| issue_types_live | locally_run | **locally_run** | The full diff touches `tests/manual/probe-issue-types.py` (comments only); the fix delta does not. Recorded run at the pin: `notes/issue-types-live-probe.txt` reads `probe-issue-types: CAPABILITY PRESENT mruangutai/harness declares native issue types Bug, Feature, Task`. |
| functional, eval | excluded (DEC-187) | not_applicable | No functional or ai_behavior task. |
| typecheck | active | not required | 0 `.ts`/`.tsx` paths in base..head. |
| component, ui | unresolved | not required | No frontend or feature change type, and no matching path. |

**Runner command (DEC-255), once per kind, serially:**
`python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind <kind> --shard 1/1 --manifest /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-7-validate-validator/qa/manifest-<kind>.json`

**Output:**
- Unit: 2,944 lines, ending `pool: 8 workers, 67 files, 24.30s wall`.
- Integration: 8,020 lines, ending `ALL PASSED. … pool: 8 workers, 95 files, 150.13s wall`.
- Verdicts come from the runner exit and the per-file `^----- … (exit N, …)` headers, never from a `^FAIL` count.
- The verbatim logs are in host scratch, `/tmp/qa-2452-c3/{unit,integration}.txt`. They are too large to transcribe, and QA's only `runs/` grant is the receipts, so the counts above are the durable record.

## Plan `verify:` blocks (verbatim from the pin's plan.yaml, extracted with yaml and run from the pin)

| task | exit | tail |
|---|---|---|
| T-01 | 0 | `pool: 4 workers, 4 files, 9.95s wall` |
| T-02 | 0 | `pool: 4 workers, 12 files, 50.73s wall` |
| T-03 | 0 | `pool: 3 workers, 4 files, 18.06s wall` |
| T-04 | 0 | `pool: 2 workers, 2 files, 11.05s wall` |
| T-05 | 0 | `PASS policy vocabulary, exit-2 correction, enforcement-ticket readback, live capability receipt and retired-override absence` |

## Focus 1: independent red reproduction at 3465716a

**Method.** In the red pin (`3465716a`, production code untouched) I ran `git checkout caeebc7c -- tests/unit/test-wayfind.py tests/unit/test-factory-gh.py` and confirmed the two files diff-equal to caeebc7c. I ran each file once, then restored them with `git checkout 3465716a -- …`; porcelain was empty afterwards. Logs: `/tmp/qa-2452-c3/red-{wayfind,factory-gh}-3465716a.txt`.

**`test-wayfind.py` at 3465716a: exit 1, 115 FAIL, 123 PASS.**
- **Where the reds are.** 7 are in `case_8c`, 94 in `case_10c` and 14 in `case_11c`. None is in a pre-existing case.
- **Every new input class is red.** I grouped the new checks by input class: all 50 classes (`case_8c` 7, `case_10c` blockers 7 / subs 10 / views 17, `case_11c` title 5 / body 4) have at least one red. No new class is a guard.
- **The reds are semantic, not signature-absent.** Examples:
  - `case_8c_blockers_item_no_state_raises_gh_error ('value', [{}], '')`.
  - `case_10c_frontier_blockers_state_unknown_exit_1 ('value', 0, '#11\t?\teligible?\n')`.
  - `case_10c_frontier_blockers_state_int_typed_diagnostic ('raise', AttributeError("'int' object has no attribute 'lower'"), '')`.
  - `case_10c_frontier_assignees_missing|null_*`: `#11 eligible?` was printed.
  - `case_10c_frontier_assignees_string|object_*`: `(frontier empty)`, so the value was read as claimed.
- **The controls are green at 3465716a:**
  - `case_8c_blockers_open_closed_any_case_valid` and `case_8c_blockers_empty_list_valid`;
  - all seven `case_10d_*` (closed_blockers, empty_blockers, blockers_404, open_blocker, claimed, closed_ticket, no_subs);
  - `case_7_blockers_404_is_absence` and `case_7_parent_404_is_absence`.

  At caeebc7c the same file passes in full in the unit run.

**`test-factory-gh.py` at 3465716a: exit 1, `17 of 345 FAILING`.**
- **Reds:**
  - owner `?`, `#`, `.`, `%2F` and `@`;
  - repo `?`, `#`, `.` and `..`;
  - `a..b`, `a.-b` and `a-.b`;
  - ports 65536, 99999, 0, 0443 and 100000.
- **Guards, already `ok` before the fix:** leading host dot, trailing host dot, leading host hyphen and empty port.
- **Accept case:** `t01_issue_number_from_url_accepts` (EMU `jdoe_acme` included) is `ok` at 3465716a, because the old owner segment was `[^/\s]+`. It is a guard there, so see the mutant below.
- **At caeebc7c:** 345/345.

## Focus 3: adequacy against the prior must_fix

| M1 input class (prior must_fix) | test at the pin | red at 3465716a |
|---|---|---|
| blocker `[{}]` | `case_8c_blockers_item_no_state`, `case_10c_frontier_blockers_item_no_state` | yes (value `[{}]`; `#11 eligible?`) |
| blocker `[{"state":"unknown"}]` | `case_8c/10c_…state_unknown` | yes |
| blocker `[{"state":1}]` | `case_8c/10c_…state_int` | yes (untyped AttributeError) |
| assignees missing, null, string, object | `case_10c_frontier_assignees_{missing,null,string,object}` | yes, all four |
| valid `[]` and confirmed 404 kept | `case_8c_blockers_empty_list_valid`, `case_10d_frontier_blockers_404`, `case_7_*` | green at both |
| EMU owner accept (`_`) | `tests/unit/test-factory-gh.py` `t01_issue_number_from_url_accepts` (`https://ghe.acme.com/jdoe_acme/r/issues/11`) | guard. **Mutant:** owner class narrowed to the builder's `[A-Za-z0-9-]+` turns the accepts case red, `1 of 345 FAILING`, exit 1 |

I also ran a second mutant, deleting the repo `(?!\.\.?/)` lookahead. It reddens exactly the two dot-segment rejects (`2 of 345`). Both mutants and the unmutated control (345/345, exit 0) went through the in-memory driver `/tmp/qa-2452-c3/url_mutant_driver.py`. The driver prints an install marker and edits no file.

**The fix note's audit table, field by field.** Every decision field it lists has at least one refusal test:
- sub_issues: container, state, number;
- blockers: container (c1 `case_8b`) and state;
- ticket view: object, assignees, labels, number (missing, other, string, bool), title;
- parent_of number (c1 `case_8b`/`case_11b`);
- resolve title (null, list, missing, null, int);
- gist body (null, missing, null, int).

Two weaker spots remain:
- **A-1 · substance · info · T-04 (`tests/unit/test-wayfind.py`).** The frontier view's `title` is refused only when it is missing or null (`title_missing`, `title_null`). No case gives it a non-null non-string (for example `5`). Resolve's title does have `title_int`.
  - **Failure scenario:** a regression that weakens frontier's `title=_string` to `title=lambda t: t is not None` stays green. `{"title": 5}` would then be advertised as a ticket.
- **A-2 · substance · low · T-04 (`wayfind.py` `cmd_map`, `tests/unit/test-wayfind.py`).** `cmd_map` now goes through the validated `sub_issues` (wayfind.py:302). A `null` sub-issue payload, which used to tally as 0 tickets, now exits 1 typed. `test-wayfind.py` has no `map` command case at all, so neither the old nor the new map behaviour is pinned.
  - **Failure scenario:** a later edit that restores `or []` for the map path silently prints "0 tickets" for an unreadable map, and no test reddens.
  - The fix note says the map view is "display only, outside frontier/resolve", so this is outside the audit's stated scope. It is an advisory, not a must_fix.

## Enforcement re-confirmation (C4)

- `git diff --name-only 3465716a caeebc7c` outside the feature directory lists 5 paths: `factory_gh.py`, `wayfind.py`, `github-mirror.md` and two unit test files.
- None matches `branch-create-gate|merge-gate|check_state|check-state|ctx|hooks/|validate-digest|check-domain|bash-write-guard`.
- The `GH_BIN` holders (`branch-create-gate.py`, `merge-gate.py`) are not in the fix delta or the full diff.
- **Zero enforcement files changed.**

## Fail-first, per `verify: automated` SC

| SC | covering test (pin) | red before fix | class |
|---|---|---|---|
| SC-01 | `tests/unit/test-gh-cost-log.py:494-` (counter through `launch_gh`); `tests/unit/test-factory-gh.py` `t01_issue_number_from_url_rejects` (URL parser, incl. B1/B3) | `t01-red-green/01-red-test-gh-cost-log.txt`; `t01-red-green/01-red-test-factory-gh.txt`; `fix-c2-FixD2_Frontier/02-red-factory-gh.txt` 17/345, **reproduced by QA at 3465716a this run** | semantic |
| SC-02 | `tests/integration/test-gh-sync-open.py:863` `single_override_case` | `t02-red-green/01-red-confinement-open.txt` (`default gh binary was dispatched: 'auth status'`) | semantic, natural |
| SC-03 | `tests/unit/test-wayfind.py` case_6/7/8b/10b/11b plus the new `case_8c_blocker_state_must_be_open_or_closed`, `case_10c_frontier_refuses_unusable_decision_fields`, `case_11c_resolve_refuses_unusable_title_and_body` | `t04-red-green/03-red-behaviour.txt` (c0); `fix-c1-FixD1_Wayfind/01-red-wayfind.txt` (c1, QA-reproduced); `fix-c2-FixD2_Frontier/01-red-wayfind.txt` 115 FAIL, **reproduced by QA at 3465716a this run** | semantic |
| SC-04 | `test-gh-sync-open.py:802` `label_failure_case`, `:747` `launch_failure_cases`; `tests/integration/test-board-lifecycle.py:1600-1605`; `tests/integration/test-gh-sync-abandon.py:70`/`:97` | `t02-red-green/04-red-behaviour-old-override.txt`; `t02-red-green/03-red-behaviour-test-gh-sync-open.txt`; `t03-red-green/03-red-behaviour-lifecycle.txt`; `fix-c1-FixD1_Mirror/05-red-final-tests-at-15a240bc.txt` (QA-reproduced c1) | semantic; (e) cut under C5 (ruled) |
| SC-05 URL | `test-gh-sync-open.py:774` `malformed_url_cases`; `tests/integration/test-gh-backlog-issue-types.py:169` CASE I | `t02-red-green/04-red-behaviour-old-override.txt` (`ValueError: invalid literal for int()`) | semantic |
| SC-05 #13 | `tests/integration/test-gh-sync-abandon.py:70` `abandon_label_create_failure_case` | `fix-c1-FixD1_Mirror/05-red-final-tests-at-15a240bc.txt` (QA-reproduced c1). Literal discharge accepted under OQ-GC2-1; the per-item close-failure red was never observed | semantic, natural |

The fix delta leaves SC-02/04/05 test and production files untouched, so their c0/c1 fail-first evidence carries forward. Their tests are green in this run's integration receipt.

## Phase 1 expectations vs tests (coverage_gaps)

Every M1 class the prior must_fix named has a test that was red before the fix. The open gaps are A-1 (frontier non-string title) and A-2 (no `map` command test). The carried items, B4 (unit seam labels event) and OQ-GC2-1 (per-item close red never observed), are already ruled for backlog or ship.

## O-07 disclosure

Fix c2 landed after the c1 review. Its red/green has been examined only by the builder and by QA's reproductions here.

## Cleanup

Both managed pins are removed with `pinned-checkout.py remove` on return (`…--harness-qa`, `…-red--harness-qa`).

## Principles applied

- **Build the Lever:** the B1/EMU discrimination ran through one scripted in-memory mutant driver over the pin's own test file. The red reproduction ran the pin's tests against the parent's production code by a scripted checkout and restore, not by hand-flipping any source.
