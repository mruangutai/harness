# QA re-gate, full pinned contract: FEAT-2297 c2 (fix-c1-validator, mission fix)

Pin `fa6a38009e54f4380daebd59a78629a68de7c1d0`. `git merge-base fa6a3800 origin/main` = `9fd1f6b414ed683cd5f5bcca4ad5fe17c35e0568` (measured; origin/main = primary HEAD, unchanged).

## BLUF

**VERDICT FAIL on the raw gate, with exactly one red.** Unit is green: 65 of 65 files, valid runner receipt. Integration ran 94 of 95 green; the only red is `tests/integration/test-corpus-real-owner.py`, attributed again to the installed owner still on schema_version 2. That is the approved E-OWNER disposition (local check deferred to PR CI, where the owner is the PR checkout at v3). I record it as a red and do not waive it, so no unconditional PASS and no green integration receipt. Everything else the gate asked for holds. CI green and its run ID are a pending ship condition, not unmet acceptance scope.

## Phase 1 (source-blind, from BRIEF and plan)

Expected tests: loader defaults, shapes and each rejection (including non-object root and missing file, with source, key path and rule); every Python reader refuses (integration); upgrade 2 to 3 with preservation, validate-before-replace and diagnosed missing/unparseable source; one fixture builder plus a bypass census; reduction checker negative controls; reader classification audit; unit and integration evidence per SC-09/SC-10. Gaps against that list: G-1 below.

## Identity, layout, candidate versus installed

- Managed pin `pinned-checkout.py` persona `harness-qa`: `git rev-parse HEAD` = pin; `git status --porcelain` empty before runs; `worktree-state.py --verify --checkout` exit 0 (converged).
- The feature worktree's HEAD is the descendant `df62a102`, which differs from the pin only in `feature.json` (re-pin and open run). Receipts are `tested_commit` = `fa6a3800`.
- Prerequisite, not a code change: pin had no `node_modules`; I ran `bun install --frozen-lockfile` (7 packages) before the integration run so `test-typescript-typecheck.py` could run, as in c1.
- Installed control plane = `9fd1f6b4` (schema_version 2, no `harness_config.py`). sha256 first 8, installed/candidate: `merge-gate.py 2af14ddb/bf224f01`, `branch-create-gate.py 68368d49/e9da1f27`, `gh-close-gate.py 89a86f3a/a7c858db`, `artifact_accessors.py 282b0fcc/6ea46097`. `run-unit-tests.py 6bb0b8c3` and `check-integration-shards.py 83b54f93` are byte-identical, so the receipts are from the production runner. Installed hooks that policed this run are the old non-validating copies. Candidate behavior is proven only by tests run from the pin. Python 3.15.2, bun 1.3.14; `HARNESS_AGENT_TYPE` unset for runs (G-07); no other `HARNESS_*` or project-root variable set.

## Matrix and kinds

Tasks are `cross_module` (T-01..T-07, T-10), `docs` (T-08), `config` (T-09). Floors: `cross_module` always `unit` + `integration`; `config` adds `integration` on `touches_config_shape` (tripped: version 3 plus status shape). `matrix_ok: true` means the floor was evaluated and both kinds mapped, not that the suite is green.

| kind | state | command | discovery | result |
|---|---|---|---|---|
| unit | satisfied | `run-unit-tests.py --kind unit --shard 1/1 --manifest <F>/runs/fix-c1-validator/qa/manifest-unit.json` | 65 `tests/unit/test-*.py` | 65/65 exit 0, runner_exit 0 |
| integration | **red** (digest enum has no ran-and-red value; reported as `missing` as in c1) | same, `--kind integration` | 95 `tests/integration/test-*.py` | 94 exit 0, `test-corpus-real-owner.py` exit 1, runner_exit 1 (146.5 s, 8 workers) |

Receipts (runner-written, never edited; `tested_commit` `fa6a3800`): `runs/fix-c1-validator/qa/manifest-unit.json` sha256 `f342e4f7446e…`, `manifest-integration.json` sha256 `6556161a6555…`. `check-integration-shards.evidence_defects` with `discover_expected` at the tested commit: unit `[]`; integration exactly `runner_exit 1` and `test-corpus-real-owner.py returned 1`, no other defect. No receipt repair needed or attempted. The typecheck test inside integration passed this run. Non-gating deliberate prints in unit output (`FAIL BUG-1290 5a/5b/5c`, `ERROR could not resolve scan root`) are mutation-proof lines inside passing files (G-09); graded on exit codes.

### Owner-v2 attribution (E-OWNER), verified

- Failing subtest: `test_check_state_passes_the_corpus_choke_point` with `caller='/Users/molchairuangutai/GitHub/harness'` (installed owner); 8 tests, 1 failure; the linked-caller subtest passed. Message: `VIOLATION .harness/harness.json is invalid: …/GitHub/harness/.harness/harness.json: schema_version: 2 is the previous harness.json shape; run upgrade-config.py … to migrate it to 3`.
- Probes with the pin's `load_harness_json`: pin's own `.harness/harness.json` VALID (schema_version 3); installed owner file REFUSED for schema_version 2; `git show origin/main:.harness/harness.json` schema_version 2; primary HEAD = origin/main = `9fd1f6b4`. Test file byte-identical to the base (`git diff 9fd1f6b4 fa6a3800 --stat` on it is empty).
- No other red in either kind. Green-after-upgrade is NOT demonstrated here; it is the PR-CI condition ([INFERENCE] it passes once the owner is v3). Not waived, test not weakened.

## Repairs since the prior pin (47d2e502), non-feature diff

`git diff 47d2e502 fa6a3800` outside the feature directory touches only `config-schemas/harness.json`, `tests/unit/test-harness-config.py`, `tests/integration/test-harness-config-upgrade.py`. Between measurement ref `8c945a8e` and the pin `fa6a3800`, no file outside the feature directory differs (metadata-only commit).

- Newline closure. Named assertions: `tests/unit/test-harness-config.py:158` (`repo with a trailing newline`) and `:186` (`signed with a trailing newline`), driven through `test_each_broken_rule_is_refused_at_its_key_path`. Author red/green `notes/receipts/fix-c1-red.txt` (12 tests, 2 failures at those two subtests, "ArtifactAccessError not raised") and `fix-c1-green.txt` (12 OK).
- My own reproduction in the pin (disposable; restored; `git status` clean after): (A) schema reverted to 47d2e502: `FAILED (failures=2)`, exactly those two subtests; (B) `not:{pattern:\s}` removed from `github.repo` only: 1 failure, the repo subtest; (C) removed from `decision` only: 1 failure, the signed subtest; restored schema: 12 OK. Each leg has its own test (P-06) and each discriminates.
- Root refusal: `test-harness-config.py` adds an array root `[{"schema_version": 3}]` to the refused-document set (plus pre-existing `[1, 2, 3]` "not a mapping" at `tests/unit/test-artifact-accessors.py:112`). Missing/unparseable upgrade source: `test-harness-config-upgrade.py:107` asserts exit 1, diagnosis ("harness.json" / "cannot read config"), no Traceback, source bytes unchanged, no backup. These bind already-correct behavior and have no natural red; recorded honestly, none demanded. Discrimination of those two is unshown (O-05), not absent.

## Fail-first per automated SC (tiers labelled)

Production under test is unchanged between 47d2e502 and the pin except the schema `not` clauses, and tests for SC-02..SC-10 are unchanged since c1, so the c1 natural reds stand (derived from the diff primitive, O-09; reproductions and counts are in `review-harness-qa-c1.md` §Fail-first, made at an own checkout of 47d2e502 with base production files restored). Tier: natural RED against pre-change production, except SC-05.

| SC | Evidence |
|---|---|
| SC-01 | c1: `test-harness-config.py` vs base `artifact_accessors.py`: 52 failures + 4 errors. Fix-c1 repro this run: 2 reds at the newline subtests (above); author `receipts/fix-c1-red.txt` |
| SC-02 | c1: `test-harness-config-readers.py` vs 23 base reader/gate files: 62 failures + 2 errors |
| SC-03 | c1: `test-harness-config-upgrade.py` vs base `upgrade-config.py`: 4 failures + 1 error. The new missing/unparseable-source assertion has no natural red (above) |
| SC-04 | c1: census vs base writers: exit 1, 5 bypass findings |
| SC-05 | present-state negative controls (not natural pre-fix red): checker's built-in negatives run first every time (undisposed row, stale fail-open, zero delta, unenumerated file). c1 scratch controls: `--base == --review-ref` gives `FAIL Gate A … +0`; receipt minus rows gives `inventory row not disposed`. This run: literal verify exits 0 |
| SC-06 | c1: canonical-reader audit with base readers: exit 2 `PLAN AMENDMENT REQUIRED` |
| SC-09 | c1: gate-policy and factory-config unit reds with base production (`test-gh-board.py`, `test-fleet-product-config.py` stayed green on base: discrimination unshown, O-05) |
| SC-10 | c1: branch-create-gate 25 FAIL, merge-gate 3 FAIL with base gates (`test-gh-close-gate.py`, `test-check-state.py` green on base) |

## SC-05 and T-10 checker, literal verify at the pin

From the pin, exactly the plan's verify block: `python3 .harness/harness/features/FEAT-2297-harness-json-schema/notes/check-config-reduction.py --review-ref HEAD --receipt …/qa-config-reduction.md` gave exit 0, 7 s: `OK base 9fd1f6b414ed review fa6a38009e54 Gate A -583; 152 rows disposed; 67 files assessed`. Measurement (checker rewrote only the block's `review` line): Gate A -583, Gate B +1575, reported total +992, identical to the committed block. Committed record names measurement ref `8c945a8e` (code tip); the pin `fa6a3800` is a metadata-only commit after it (no non-feature path differs), so the committed block is current in content, with the review SHA one metadata-commit behind. I restored the pin's receipt file after the run (`git checkout`; status clean). BRIEF SC-05 literal "negative total delta" versus signed D-06 Gate A: settled, not re-raised.

## Canonical reader audit (outside suite discovery)

`python3 .claude/skills/harness/bin/check-plan-routes.py --canonical-reader-audit` at the pin: `0 unresolved reader site(s) across 101 Python file(s)`, exit 0.

## T-08 change receipt

`notes/changes-config-contract.md` now cites `notes/uat-kaya-migration.md` and states review and authorization were by the plan's advisor under the operator's run-level delegation, not by the operator personally (lines ~49-50). The prior dangling `receipts/t09-kaya.txt` citation is gone from that file (grep). SC-08 judged on the amended criterion per the settled ruling; SC-07 is inspection (other readers).

## Findings

| id | kind | owner | severity | status |
|---|---|---|---|---|
| F-01 | substance: required-kind red, `test-corpus-real-owner.py` fails against installed owner v2 | none bindable; Main (E-OWNER disposition) | high until CI | **pending ship-only CI confirmation.** Ship needs CI green and the CI run ID; verify attribution and no other red there. Not an unmet code criterion |
| G-1 | substance (low, coverage): non-object-root refusal for `harness.json` is asserted for array roots only (`null`, number, string roots not named in a test) | T-01 | low | advisory; behavior held on c1 probe (`JSON document is not a mapping` for `[]`, `null`, `3`, `"x"`); no code defect shown |

No other findings. c1 F-03/F-04 (root, upgrade-source coverage) are closed by named assertions above; c1 newline issue closed with natural red/green; c1 F-05 (stale reduction block) refreshed.

## Assurance limits

Only my own evidence examined the schema repair after the code review round that raised it (O-07); security and UI readers did not re-read it. Red/green receipts under `notes/receipts/` are author-captured and I corroborated them by reproduction only for SC-01 newline; other SCs lean on c1 reproductions at an unchanged production tree. Installed hooks were the old copies. Real-owner test unproven green until CI.

## Principles applied

- Build the Lever: both kinds ran through the production runner with one manifest each (the runner command from DEC-255), no hand edits.
- Verification is the product (rule 7) and O-01: a nonzero required kind is reported red despite verified attribution.
- Never falsify the record (rule 15): integration state not upgraded to satisfied under the disposition.

Cleanup: managed checkout `harness-qa` removed on return (feature, run and persona keyed).
