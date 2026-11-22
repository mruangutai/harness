# QA gate — FEAT-2297 c1 (validate-validator)

Reviewed pin: `47d2e50243ad7fb080e13ef48115756d7d3b7c61` (clean managed checkout, `pinned-checkout.py`, persona `harness-qa`).
Diff base `git merge-base 47d2e502 origin/main` = `9fd1f6b414ed683cd5f5bcca4ad5fe17c35e0568`.

## BLUF

**VERDICT FAIL.** Unit kind is green with a valid runner receipt. Integration kind is NOT satisfied: one named
red, `tests/integration/test-corpus-real-owner.py` (95 files discovered, 94 exit 0, 1 exit 1). Attribution to the
un-upgraded real owner checkout is verified (below), but a nonzero required-kind exit cannot be graded satisfied and
DEC-255 refuses an unconditional PASS against it. Fail-first is shown for every automated SC (01-06, 09, 10), by my own
reproductions where possible. SC-08 is text-unmet (see F-02). Everything else the gate asked for is clean.

## Phase 1 (source-blind) expected coverage, from BRIEF + plan only

SC-01 unit: absent-key defaults; v3 shapes; each present-invalid, unknown non-prose key, status-less kind, v2 (with upgrade
instruction), duplicate keys, non-finite JSON, **non-object root**, **missing file**; source/key-path/rule in errors.
SC-02 integration: every Python reader + remote product_config refuses; check-state reports; sync-off/null-board unchanged.
SC-03 integration: 2->3 migration, status inference, preservation, validate-before-atomic-replace, original kept on
failure, **missing/unparseable source diagnosed not fabricated**, live + template configs validate.
SC-04: one builder, census with bypass detection, budget-fixture freshness. SC-05: checker fails on undisposed row /
stale fail-open / nonnegative Gate A. SC-06: reader inventory + non-config route cases. SC-09: unit evidence for loader,
strict non-config reads, board normalization, review evaluation, TS advisory fallback. SC-10: cross-process contract
integration plus preserved unrelated semantics, no condition evaluator.
Gaps against this list: F-03, F-04 below.

## Matrix (control-plane `harness.json` at the pin, schema 3)

Every plan task is `cross_module` (T-01..T-07, T-10), `docs` (T-08) or `config` (T-09). Floors: `cross_module` always
`unit`+`integration` (feature/runtime floor, DEC-217); `config` adds `integration` when `touches_config_shape`
(schema_version 3 + status shape change: trips, DEC-212); `docs` none. Both kinds are `active` with runnable `cmd`.
`typecheck` is also `active` (`bun run typecheck`) in the merged tree, contrary to the BRIEF's "cmd null" gap line (BRIEF
text predates the main merge); not in any floor, and `test-typescript-typecheck.py` is inside the integration kind.
`matrix_ok: true` (floor evaluated, both kinds mapped); kind states below.

| kind | state | command (from pin) | discovery | result |
|---|---|---|---|---|
| unit | satisfied | `python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind unit --shard 1/1 --manifest <abs runs/validate-validator/qa>/manifest-unit.json` | 65 `tests/unit/test-*.py` | 65/65 exit 0, runner_exit 0 |
| integration | NOT satisfied (digest enum `missing`: no enum value fits a ran-and-red kind) | same, `--kind integration` | 95 `tests/integration/test-*.py` | 94 exit 0, `test-corpus-real-owner.py` exit 1, runner_exit 1 |

Receipts: `runs/validate-validator/qa/manifest-unit.json` (sha256 `8ee4741c…`), `manifest-integration.json` (sha256
`80ae74c4…`); both `tested_commit` 47d2e502, written by the runner, never edited. Validated with
`check-integration-shards.evidence_defects` at the pin: unit `[]`; integration `runner_exit 1` +
`test-corpus-real-owner.py returned 1`. Runner env: `HARNESS_AGENT_TYPE` unset (G-07); no other HARNESS_*/PYTHONPATH set.
Run 1 of integration also failed `test-typescript-typecheck.py` (pin had no `node_modules`: "run bun install
--frozen-lockfile"). I supplied the prerequisite (`bun install --frozen-lockfile`, 7 packages), confirmed that test PASSES
alone, then re-ran the integration kind once more; the manifest on disk is run 2 (146 s, one red). Run 1 is evidence
only, not a receipt. Non-gating prints in unit output (`FAIL BUG-1290 5a/5b/5c`, `ERROR could not resolve scan root`) are
deliberate mutation-proof lines inside passing files (G-09); graded on exit codes.

### Known failure `test-corpus-real-owner.py` — attribution verified, not accepted

- Failing subtest is `caller='/Users/molchairuangutai/GitHub/harness'` (the host owner); the linked caller (the pin)
  passed in the same file. Message: `VIOLATION .harness/harness.json is invalid: /Users/…/GitHub/harness/.harness/harness.json: schema_version: 2 is the previous harness.json shape; run upgrade-config.py`.
- Probe: owner `HEAD` = `origin/main` = `9fd1f6b4`; `git show origin/main:.harness/harness.json | jq .schema_version` = 2.
  The candidate's own `.harness/harness.json` is 3 and loads valid (probe).
- Mechanism: the test runs the candidate's check-state against the owner; the candidate now refuses a v2 config. The
  host owner is not upgraded until this feature lands. [INFERENCE] it goes green once main carries v3; not demonstrated here.
- This is still a required-kind red. Attribution does not make it satisfied (O-01).

## Candidate versus installed

Installed control plane = `9fd1f6b4`, schema_version 2, no `harness_config.py`. sha256 (first 12) installed vs candidate:
`merge-gate.py 2af14ddb/bf224f01`, `branch-create-gate.py 68368d49/e9da1f27`, `gh-close-gate.py 89a86f3a/a7c858db`,
`artifact_accessors.py 282b0fcc/6ea46097`. `run-unit-tests.py 6bb0b8c3` and `check-integration-shards.py 83b54f93` are
byte-identical, so the receipts come from the production runner. Python 3.15.2, bun 1.3.14. Candidate gate behavior is
proven only by tests run from the pin; the installed hooks that policed this run are the old non-validating copies.

## Fail-first, per automated SC (own reproductions at immutable SHAs)

Method: second managed checkout at 47d2e502, then `git checkout 9fd1f6b4 -- <production file>` for the production under
test, leaving the pin's tests and contract in place (a mixed tree; red type recorded; removed on return). Authors'
self-captured natural reds are `notes/receipts/*-red.txt` (tracked at the pin, 25 files); I treat those as secondary.

| SC | Evidence (tier: natural-RED against pre-change production) | Result |
|---|---|---|
| SC-01 | `python3 tests/unit/test-harness-config.py` with base `artifact_accessors.py` | 12 tests, 52 failures + 4 errors; assertion reds on refusal/default rows (2 errors are missing-`max_total_runs`/import of the new module, not vacuous) |
| SC-02 | `tests/integration/test-harness-config-readers.py` with 23 base reader/gate files | 12 tests, 62 failures + 2 errors, 0 import errors (reader refusal x41, gate block x15, remote/overrides) |
| SC-03 | `tests/integration/test-harness-config-upgrade.py` with base `upgrade-config.py` | 5 tests, 4 failures + 1 error (config-only, check, idempotent, invalid-candidate) |
| SC-04 | census `test-harness-config-fixtures.py check_state_support.py f58_sparse_fixture.py gh_sync_support.py` with base support writers | exit 1, 5 findings, each `raw-write`/`mapping-entry`/`remote-payload` bypass; matches author `t02-census-red.txt` |
| SC-05 | checker negative controls on scratch receipts: `--base == --review-ref` -> `FAIL Gate A … net +0`; receipt minus the `test-gh-board.py` rows -> `inventory row not disposed` (2 rows), exit 1 (tier: negative control, present-state; not a natural pre-fix red) | discriminates |
| SC-06 | `check-plan-routes.py --canonical-reader-audit` with base readers + pin classification | exit 2, `CLASSIFICATION … PLAN AMENDMENT REQUIRED` rows (wrong route); on the pin: `0 unresolved reader site(s) across 101 Python file(s)`, exit 0. The audit is a CI step in `tests.yml:242`, not part of the unit/integration kinds |
| SC-09 | SC-01 red above (loader) + `test-gate-policy.py` (review evaluation: `FAIL removed gate keys are refused`) and `test-factory-config.py` (board normalization, 4 FAIL) with base `gate_policy.py`/`factory_config.py` | red. `test-gh-board.py` and `test-fleet-product-config.py` stayed green on base (kept/relocated cases, no new-behavior red shown for them; O-05: discrimination unshown, not absent) |
| SC-10 | readers red above + `test-branch-create-gate.py` (25 FAIL) and `test-merge-gate.py` (3 FAIL) with base gates | red. `test-gh-close-gate.py` and `test-check-state.py` stayed green on base (valid-config/preserved cases; refusal for them is carried by the readers suite red) |

Checker proper (offline, scratch receipt, `--review-ref 47d2e502 --receipt <scratch copy>`): exit 0,
`OK base 9fd1f6b414ed review 47d2e50243ad Gate A -583; 152 rows disposed; 67 files assessed`. Reported total
(both populations) +974; Gate B new files +1557. That is the signed D-06 amendment's Gate A, settled; BRIEF SC-05's literal
"negative total delta" differs, recorded here, not re-raised.

## Findings

| id | kind | severity | owner | scenario |
|---|---|---|---|---|
| F-01 | required-kind-red | high | none bindable (host owner not upgraded; merge ordering) | `test-corpus-real-owner.py` fails when the validator runs from a host whose owner `harness.json` is v2; blocks an unconditional PASS receipt. Needs lead/main routing: rerun after the owner carries v3, or an explicit signed disposition. No weakening of the test was made or is proposed here |
| F-02 | spec-conformance (text-unmet, intent-met) | high | T-09 | SC-08 literally says "I review … and authorize". `uat-kaya-migration.md` records kaya#29 merged `b9dec8df` on **advisor** authorization under standing delegation and itself says it does not claim operator review. The BRIEF Verification gaps say SC-08 "requires the operator personally". The landing (v3, explicit statuses, null cmds still unresolved, read back valid) satisfies the intent; it does not discharge the operator-personal wording. Migration landing is not authorization. Route to the operator for explicit acceptance or ratification; I do not substitute |
| F-03 | coverage-gap | low | T-01 | SC-01 names non-object roots; no named test asserts a non-mapping `harness.json` root refusal (`[]`, `null`, `3`, `"x"` are refused with `JSON document is not a mapping` by my probe on the pin, so behavior holds, untested) |
| F-04 | coverage-gap | low | T-01 | SC-03 requires missing/unparseable source to stay a diagnosed repair problem with no fabricated file. No test asserts it. Probe on the pin: missing -> exit 1 "not initialised", unparseable -> exit 1 "cannot read config", no file created |
| F-05 | stale-evidence | low | T-10 | committed `qa-config-reduction.md` measurement block names review `1b904355` / base `837e7096`, not 47d2e502 / 9fd1f6b4. The checker reproduces OK at the pin; main must refresh the block before the committed record is cited as the pinned receipt |

Not findings (settled by caller): D-06 Gate A/B, INV-13 retirement, deferred #2393. SC-07 is `inspection` (other readers).
Prior local `notes/receipts/t10-matrix-*.txt` were treated as unverified prior evidence; my own receipts replace them.

## Principles applied

- Build the Lever: `/tmp/qa-c1/run.sh` ran both kinds through the production runner with one manifest each.
- Verification is the product (rule 7) / O-01: a nonzero required kind is reported red, not satisfied, though attributed.

Cleanup: both managed checkouts (`harness-qa`, `harness-qa-red`) removed on return.

## Clarification (lead request): probes and canonical kinds

Probes at pin 47d2e502 (fresh managed checkout, removed; builder-valid base, one field corrupted; no suite rerun):

| input | measured |
|---|---|
| `github.repo = "acme/repo\n"` | ACCEPTED, stored as `'acme/repo\n'` (control `"acme/repo"` accepted) |
| excluded kind `signed = "DEC-187\n"` | ACCEPTED (control `"DEC-187"` accepted) |

Both trailing-newline values pass the loader, so the code-reviewer's reading (schema `$` permits a trailing LF) is confirmed.
Neither is tested; I make no severity claim on them (not an SC-bound requirement; BRIEF requires only "no whitespace" for repo).

Canonical kinds for F-01..F-05 (severities unchanged): F-01 substance (high); F-02 substance (high); F-03 substance (low,
missing test for a stated criterion); F-04 substance (low, same); F-05 form (low, stale record text). The earlier labels
(required-kind-red, spec-conformance, coverage-gap, stale-evidence) were descriptive, not canonical.
