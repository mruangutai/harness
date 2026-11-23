# QA gate c0: FEAT-2398 T-01 at review_sha 685e861a667efd13e3c9720dffe9dbb847d4207b (run validate-validator)

**VERDICT: FAIL.** The required `integration` kind is red at the pin: `tests/integration/test-harness-config-fixtures.py` exits 1 with 8 findings, all in T-01's new fixtures. `unit` is green. The focused T-01 verify is green (52/52). The baseline (9eb07b4f) runs the same script at 0 findings, so T-01 caused the regression.

## Environment
- Pin: `.claude/worktrees/.pins/FEAT-2398-qa-test-kind-status--validate-validator--harness-qa`, HEAD 685e861a, clean.
- Baseline pin: `...--harness-qa-base`, HEAD 9eb07b4f.
- Run with `env -u HARNESS_AGENT_TYPE`.
- The installed control-plane validate-digest.py is pre-change and was not used as evidence. All candidate behaviour here comes from tests run in the pin.
- The pinned `.harness/harness.json` `test_matrix.cross_module` is `always: [unit, integration]` with no `when:`. The matrix floor is therefore unit and integration; `typecheck` is not in the floor.
- Pinned status of both required kinds is `active` with a cmd (`run-unit-tests.py --kind unit` / `--kind integration`).
- Diff 9eb07b4f..685e861a also carries unrelated files (checkout-upgrade.md, gitignore, test-merge-gitignore, and others). They come from commit 04a318d0, "Merge origin/main (BUG-2399)", plus 9a818b46. I did not assess them.

## Receipts (runner-written, DEC-255 command from the pin)
Command: `python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind <k> --shard 1/1 --manifest <F>/runs/validate-validator/qa/manifest-<k>.json`

| kind | tested_commit | discovered | completed | runner_exit | result |
|---|---|---|---|---|---|
| unit | 685e861a | 65 | 65 | 0 | green (`manifest-unit.json`) |
| integration | 685e861a | 95 | 95 | 1 | red (`manifest-integration.json`) |

Integration failures, with each failing script's `returncode` in the manifest:
1. **`test-harness-config-fixtures.py` (rc 1). Genuine regression owned by T-01.**
   - It reports 8 findings: "a harness.json producer that does not reach build_config/write_config", at `test-validate-digest.py` lines 7032, 7041, 7042, 7165, 7167, 7169, 7171 and 7175.
   - Those lines are in `_kp_harness_repo` and `_kp_product_repos`. They write `.harness/harness.json` through `_rx_commit` and `_mx_write` with `json.dumps(build_config(...))` rather than the fixture writer.
   - That contradicts T-01's intent that every config fixture use `tests/harness_config_support.py`.
   - At baseline (pin ...-base), the same script gives `0 finding(s)`.
2. **`test-typescript-typecheck.py` (rc 1). Environmental, not a code defect.**
   - The pin has no `node_modules`, so there is no `tsc`.
   - After `bun install --frozen-lockfile` in my pin, the script passes (diagnostic run only; I did not edit the receipt). Main must note that CI-equivalent receipts need `bun install` first.

I did not re-run the whole integration kind. The manifest stays red and was not edited. A repair to the T-01 fixtures needs a fix run with fresh receipts from the fixed tip.

## Focused command (T-01 verify, verbatim, at pin)
`python3 tests/integration/test-validate-digest.py --only run_feat2398_qa_policy_cases` gives `52/52 feat2398 cases passed. ALL PASSED.` and exit 0. The full-integration run also reports `52/52 feat2398 cases passed`.

## fail_first (own reproduction, natural RED)
- Command: the pinned test file run with `VALIDATE_DIGEST_BIN=<baseline pin>/.claude/skills/harness/bin/validate-digest.py`.
- Result: `13/52 feat2398 cases passed. 39 FAILING.`, exit 1. This matches main's `notes/receipts/t01-red.txt` (13/52 passing, 39 failing).
- Reds are semantic in the SC-01 and SC-02 branches. The baseline hook accepts at exit 0 what must be refused at exit 2 (for example "reported satisfied/not_applicable/missing/locally_run is refused").
- SC-03 reds are mixed. Some are semantic, for example the baseline reading current-tree policy instead of the pin. Others are absent-pin-machinery refusals.
- SC-01: all unresolved and active/null refusal cases, lines 7072-7087.
- SC-02: `locally_run` mismatch (7099) and the Verification gaps pair (7107-7117). Controls at 7093-7104 are green at baseline by design.
- SC-03: Harness cases 7122-7133 and product cases 7190-7213.
- SC-04: `PASS ... floor` (7142), reported unresolved conditional (7147), and the no-kind exemption pair (7149-7153). Omit-allowed controls (7138-7141, 7145) are green at baseline by design.
- Green at the pin: `notes/receipts/t01-green.txt` was recorded over an uncommitted tree. I reproduced green at 685e861a myself.

## Coverage gaps (Phase 1 expectations with no pinned test)
1. SC-04 omission of an unresolved or active/null floor kind is tested under BLOCKED, FAIL and PASS only (7084-7087). ESCALATE omission is untested.
2. `matrix_ok` is never varied independently of the verdict, because `_kp_digest` (6999-7006) derives it from the verdict. "Regardless of matrix_ok" is therefore unproven for FAIL with matrix_ok n/a or true, and BLOCKED with false or true.
3. SC-03 matrix selection:
   - The P1/P2 pins and the `floor_*` pins change statuses and the matrix together; no pair changes only the matrix.
   - A mutant reading statuses from the pin and the matrix from another source (or the reverse) would still redden the P1 omission case (7190). That is [INFERENCE] by reading; I ran no mutation proof.
   - A drift that alters only `always` membership of a kind with identical statuses is not isolated.
4. SC-05 (inspection): only coarse coverage extent assessed. The sweeps in the other test files that rely on the changed docs ran green in the unit and integration runs. I did not read the SKILL, SPEC or DECISIONS prose line by line.

## Fixture-run observation
`unit` and `integration` also passed `test-validate-digest-shadows.py` and `test-harness-config-readers.py` (both named in T-01 files) inside the integration run. Both returned 0.

## Open
- Fix T-01's fixtures (`_kp_*` harness.json writes) to go through the `harness_config_support` writer so `test-harness-config-fixtures.py` returns to 0 findings. Then a fix run with fresh unit and integration receipts, after `bun install --frozen-lockfile` in the checkout.
- Decide whether the coverage gaps for ESCALATE omission and independent `matrix_ok` need tests.
- No INV-25/INV-29 `/private/tmp/ship-BUG-2399` finding was encountered.
