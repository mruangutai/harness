# QA gate c1: FEAT-2398 T-01, same pin 685e861a667efd13e3c9720dffe9dbb847d4207b (run validate-validator)

**VERDICT: FAIL (carried from c0, now with a second blocking defect).** The reviewer's empty-kind CLI bypass is **reproduced**: the candidate CLI exits 0 on a schema-valid QA PASS with `kinds: []` and no trusted feature directory, instead of refusing the missing pin. c0's red integration kind (fixture regression) stands. This is a same-pin evidence sendback; I ran no suites and edited no manifests.

## Identity
- The managed pin directory had been swept. I re-created it with `pinned-checkout.py add --feature FEAT-2398-qa-test-kind-status --run-id validate-validator --persona harness-qa --sha 685e861a...`.
- `git rev-parse HEAD` = 685e861a667efd13e3c9720dffe9dbb847d4207b, `git status --porcelain` empty before and after the probe.
- Probe ran the candidate `.claude/skills/harness/bin/validate-digest.py` from that pin. The installed control-plane hook was not used.
- No `HARNESS_*` variables were visible in the probe's environment.

## Probe (the reviewer's exact scenario)
Input `/tmp/qa2398/empty-kinds.json` (outside the repo, temporary), contract-valid against `digest-schemas/harness-qa.json`:
`{"VERDICT":"PASS","DIGEST":{"headline":"probe: empty kinds","open_questions":[],"files_touched":[],"expertise_update":[],"suite":"pass","failures":0,"coverage_gaps":[],"matrix_ok":true,"fail_first":[{"sc":"SC-01","evidence":"notes/qa.md"}],"kinds":[],"sc_evidence":[{"id":"SC-01","test":"tests/x.py:1"}]},"artifact":"notes/qa.md"}`

| command (cwd `/tmp/qa2398`) | output | exit |
|---|---|---|
| `python3 <pin>/.claude/skills/harness/bin/validate-digest.py harness-qa /tmp/qa2398/empty-kinds.json` | `digest ok` | **0** |
| same, input on stdin | `digest ok` | **0** |

The CLI accepts it. It does not emit the explicit missing-pin refusal that D-01 requires. Cause by reading: `_qa_kinds_errors` (`validate-digest.py:1795-1800`) returns `[]` before `_qa_policy` when `kinds` and the started tasks are both empty, and the CLI supplies no feature directory (`:3206`).

## Carried from c0 (not rerun; immutable receipts)
- suite: fail. matrix_ok: false. `unit` green (65/65, `manifest-unit.json`). `integration` red (95/95 completed, runner exit 1, `manifest-integration.json`).
- Integration red has two causes. (1) T-01-owned fixture regression: `test-harness-config-fixtures.py` reports 8 findings in `_kp_harness_repo` / `_kp_product_repos` (`test-validate-digest.py` lines 7032-7175), 0 at baseline. (2) Environmental: no `node_modules`, so `test-typescript-typecheck.py` lacks `tsc`; needs `bun install --frozen-lockfile` before a CI-equivalent receipt.
- Focused T-01 verify was 52/52 at the pin in c0.

## Fail-first classification
- 39 of 52 cases red against the baseline hook (13/52 pass) is the **natural baseline fail-first** for SC-01/02/03/04 (c0 note and main's `notes/receipts/t01-red.txt`).
- That is not the state of the full matrix: the matrix stays red for the fixture regression plus, separately, the missing `tsc`.
- The empty-kind bypass has **no** red test. The new CLI case supplies a nonempty kind, so the bypass is undetected by the 52 cases.

## Coverage gaps (existing SC-01/SC-04 duties, T-01-owned corrective work)
1. Empty-kind CLI refusal with no trusted feature directory (SC-03/D-01): no test; reproduced above.
2. SC-04 omission of an unresolved/active-null floor kind under **ESCALATE**: untested (BLOCKED/FAIL/PASS only, 7084-7087).
3. `matrix_ok` not varied independently of verdict (`_kp_digest`, 6999-7006): "regardless of matrix_ok" unproven.
4. Q-fixtures: the `_kp_*` harness.json writes must go through `tests/harness_config_support.py`. This is already T-01-owned corrective work in the plan, and needs no human decision.
5. Nonblocking adequacy note: no matrix-only SC-03 pair. PM explains the existing P1 omission case discriminates both tables, so I keep this advisory.

## Checks for the main-session-direct repair (none authored by me)
- `python3 tests/integration/test-validate-digest.py --only run_feat2398_qa_policy_cases` (add a CLI case for kinds=[] with no feature dir; it must refuse and be red at the pin).
- `python3 tests/integration/test-harness-config-fixtures.py` back to 0 findings.
- Fresh fix-run receipts from the fixed tip after `bun install --frozen-lockfile`: `run-unit-tests.py --kind unit` and `--kind integration` with `--manifest .../runs/fix-c<N>-validator/qa/manifest-<kind>.json`, run with `env -u HARNESS_AGENT_TYPE`.

## Open
- Fix T-01: establish the policy (or refuse the missing pin) before the empty-list early return at `validate-digest.py:1795-1800`; add the real CLI regression.
- The installed hook is pre-change; this probe says nothing about it.

## Record-shape correction (no execution)
Digest states follow the immutable receipts: `unit` satisfied (65/65, exit 0); `integration` missing (runner_exit 1, red). Suite failures = 1 (the integration kind); the CLI bypass is a separate finding, not a failed runner script. fail_first and sc_evidence cover SC-01..SC-04 as in c0.
