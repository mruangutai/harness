# QA gate — BUG-2187 T-01 @ pin edd9098c (run 2026-11-21-03-validate-validator, cycle 2)

BLUF: **ESCALATE, suite fail.** Every T-01/SC-bound check is green at the pin (verify exit 0; unit kind exit 0; bound integration
files green inside the pooled kind) and base-red is reproduced for SC-01/02/03. But the required pooled `--kind integration`
runner exited **1**: `tests/integration/test-validate-digest.py` (exit 1, 51.24s) died on two uncaught
`subprocess.TimeoutExpired` (hard 3s `_t09_fire(..., timeout=3)` at test-validate-digest.py:1060 via :3059 and :3026/3462) while
host load average was ~125. That file and validate-digest.py are not in base..pin. Not rerun (instruction). Per O-01 not graded PASS.
Source untouched; files_touched [].

## Phase 1 (BRIEF + plan only)
Expected: (SC-01 integration) station-only silent, serialization-only silent, nested/other status STALE, task-nested STALE, five silences
+ placeholder, changed-then-restored; unloadable/legacy byte fallback. (SC-02 unit) pin-review default HEAD, ref->full id, noncommit/unresolved
refused no-write REFUSED, APPLIED output, only review_sha changes, shared writer, both docs name the verb, seam order. (SC-03 unit)
direct-fix regate, multiple, start-equality, earlier/non-regate, replace-not-sum, legacy fallback, no validate, cycles_used. No Phase 1 gap
remains unbound (see coverage).

## Production equivalence
`git diff 1b35414b edd9098c -- .claude` from PRODUCT: **empty** (`--quiet` exit 0, 0 names). Cycle-1 production claim confirmed. HEAD 16087b6a
differs from the pin only in feature.json/plan.yaml, so all executions ran in managed pins (pinned-checkout.py, personas harness-qa-c2 and
harness-qa-c2-base, both removed). Env: `env -u HARNESS_AGENT_TYPE`, only CLAUDECODE/OMPCODE exported.
Delta 1b35414b..edd9098c tests: +inv33.h/i/j (integration), +3 unit (naive stamp, field preservation, writer destination).

## Matrix
change_type bugfix: unit `when touches_runtime_code` = TRUE (full diff changes bin/*.py; P-13 measured against 5bd9efd4..pin); integration
`when fix_confined_to_tests_and_contract_docs` = false (production changed), but integration carries SC-01 so it is required by the BRIEF.
`__bug_class__` unresolved placeholder (repo G-08). harness.json identical in product and control plane.

## Executions at the pin (mine)
| command | exit | wall | observed |
|---|---|---|---|
| exact T-01 verify `python3 tests/integration/test-check-state-records.py && python3 tests/unit/test-feature-record.py` | 0 | **67s** | integration 53 `ok -`, 0 FAIL; unit `Ran 131 tests OK` (21.7s); stderr = tests' own expected REFUSED/validator noise. Exceeds the plan's under-60s intent by 7s, under heavy host load (uptime later: load avg 125.67/71.73/37.46); c0 measured 52.6s. Reported honestly, no assertion dropped |
| `code-grade.py --base 5bd9efd4 --head edd9098c` | 0 | - | PASSING: 40, all RESULT: PASS, none grade 1 or 2 (lowest 4; _without_stations feature_record.py:66 cyc 7 ABC 9.8; _inv33_changed_since test-check-state-records.py:529 cog 8 ABC 15.7). Answered to reviewer by IRC |
| `run-unit-tests.py --kind unit` | 0 | 29s | 61 files, includes test-feature-record.py PASS. Its 'FAIL BUG-1290 5a/5b/5c' lines are test-factory-claim-mutation.py's deliberate mutation-proof prints (repo G-09), runner exit 0 |
| `run-unit-tests.py --kind integration` | **1** | 214s | 87 files, pool 8 workers. test-check-state-records.py PASS (48.9s), test-checker-structure-locks.py PASS, test-gh-sync-open.py PASS (125s, its own ALL PASSED). Failing file: **tests/integration/test-validate-digest.py exit 1, summary `2 FAILING.` / `FAIL test-validate-digest.py`** |
Full output of the unit then integration runner (8271 lines, command, env) is retained at local://54.log (spill) and was not copyable
into notes (bash-write-guard, DEC-151); the failing block is lines 7604-8110. The first red is a hard 3s subprocess timeout wrapped in
the test's own harness, i.e. timing under load, not an assertion diff. [INFERENCE] load-induced: pooled run was 214s vs 120s in
cycle 1 and this checkout's host showed load 125. Not proven; no rerun was made per instruction. Prior cycle's red file was
unrecoverable; this identifies one candidate file, not that it was the same red.

## Base-red (own reproduction, immutable base 5bd9efd4, production byte-identical to pin's pre-fix; tests overlaid from edd9098c)
`git diff 5bd9efd4 -- .claude` is the fix only; overlay of 3 test files, both scripts run once.
- Integration exit 1: `FAIL (inv33.e)`, `FAIL (inv33.f)`; ok at base (safety assertions, allowed): inv33.g/h/i/j.
- Unit exit 1, `Ran 131 FAILED (failures=9)`, all AssertionError, no import/collection error:
  SC-02 PinReviewTest: omitted_sha (`0 != 2`), ref_or_short (`0 != 2`), non_commit_or_unresolved, every_other_field (`0 != 2`, argparse
  invalid choice 'pin-review'), guidance (`'pin-review' not found in {'run-start','close-run'} : build-phase.md`);
  SC-03 SpendTest: direct_fix (`1 != 0`), every_regate (`2 != 0`), window_opens_exactly (`1 != 0`), replace_never_add (`1 != 2`).
  Natural-RED tier, semantic (real defect output: STALE for station-only; argparse refusal of absent verb; undercounted rounds).
  Shared-writer destination test and naive-stamp test are green at base (verb absent / guard pre-existing): discrimination for them
  rests on the mutants below, not on base-red (O-05).

## Mutant receipts (receipts/fix-cycle1.txt + /tmp/bug2187_mutants.py), inspected not rerun
Anchors match current source (feature-record.py:611-613, :673-675; check_state/feature_record.py:66-90). Each of the seven kills is
specific: wipes-judgements and bumps-cycles_used are caught by test_every_other_field (full-document equality, tests:1297); bypass-writer by the
stray-destination test (:1310, schema-writer refuses outside `.harness/*/features/*/`); tz guard by naive-stamp test (:1256);
task-nested-status by inv33.h (:521); non-plan.yaml-as-None and unloadable-as-None by inv33.j (:579, two different unloadable texts and a
changed legacy PLAN.md). inv33.i has a changed-plan control proving the harness reports before four silences are asserted (:547). The receipt's
"four full green sequential runner executions" cannot be corroborated against this run's red; it is a claim, and this run is the stronger datum.

## SC audit
| SC | bound test | fail_first |
|---|---|---|
| SC-01 | tests/integration/test-check-state-records.py:496 inv33.e, :505 inv33.f; boundaries :513 g, :521 h, :547 i, :579 j | base-red above (inv33.e/f) |
| SC-02 | tests/unit/test-feature-record.py:1284, :1291, :1297, :1310, :1322, :1332 | base-red above (5 fail) |
| SC-03 | tests/unit/test-feature-record.py:1231, :1234, :1238, :1245 (+ :1249, :1253, :1256 safety) | base-red above (4 fail) |

## Findings (none new against the diff)
| # | kind | severity | location | note |
|---|---|---|---|---|
| 1 | substance | high | tests/integration/test-validate-digest.py:1060 (via :3026, :3059, :3462) | required integration kind red at the pin: uncaught TimeoutExpired at hard 3s. Outside the diff; gate cannot pass until a clean run is recorded |
| 2 | form | low | plan.yaml T-01 verify | literal verify 67s > 60s intent under load; unmeasured on a quiet host |
| 3 | form | low | notes/ | full runner log not copyable to notes by QA; retained at local://54.log only |

## Coverage gaps
Phase 1: none unbound. Pre-existing: lock contention and nonexistent `--file` for pin-review untested; guidance test checks verb presence,
not flags. Reader execution limitation: reviewers could not run checks; every execution above is mine, once, sequential.

## Principles applied
Build the Lever: reused the sanctioned runner/pins and the receipt's mutant script as the rerunnable artifact rather than hand mutation.
