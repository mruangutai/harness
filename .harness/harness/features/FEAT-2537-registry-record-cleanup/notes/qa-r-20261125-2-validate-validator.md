# QA gate — FEAT-2537 T-01, run r-20261125-2-validate-validator, cycle 1

**BLUF: PASS.** Required kinds (unit, integration, from `cross_module`) are satisfied at the pin with clean runner receipts;
typecheck is green too. T-01's verify block exits 0 verbatim. Fail-first evidence exists for SC-01 (natural red on base,
plus a mutant red) and SC-02 (natural red with the base module swapped in). Every main-session claim reproduced. One
adequacy gap with a surviving mutant (F-1, low) and two form notes. **No behaviour delta outside the signer's ruled class.**

Note path: the dispatch named `notes/review-harness-qa-c1.md`, but qa owns `notes/qa-*.md` (artifact-paths.md), so this
note is written here.

## Policy at the pin
- Repo: harness (the feature is unbound, so this repository). Commit `8ae96bea9dd8eb0f412c654158cbb3050322cfff`.
  Policy blob: `git show 8ae96bea…:.harness/harness.json`.
- T-01 `change_type: cross_module` gives `always: [unit, integration]`. `typecheck` is active, and its detect `**/*.ts`
  matches `harness-hooks.ts`, so it is added as warranted. `omp_session_accessor` (locally_run) is not owed, because
  session-file resolution is untouched.
- Merge-base: `git merge-base main HEAD` = `a24eacee718898c4512379de1fe87b9611a7df43`, and `main` is still at a24eacee.
- Checkout: `pinned-checkout.py` pin `.pins/FEAT-2537…--harness-qa`. `worktree-state.py --verify` exited 0
  ("converged"). `bun install --frozen-lockfile` was run in the pin.

## Runs
Every run was on the host interpreter (Python 3.15.2, darwin arm64), **not CI**: there is no PR, so the CI route never
ran. Each command ran with `env -u PYTHONUNBUFFERED -u NO_COLOR -u FORCE_COLOR -u HARNESS_AGENT_TYPE TERM=xterm-256color`
and `HARNESS_PROJECT_DIR=<pin>` for the gates.

| Kind / gate | Command | Exit | Summary |
|---|---|---|---|
| unit | `python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind unit --shard 1/1 --manifest <run>/qa/manifest-unit.json` | 0 | `pool: 8 workers, 68 files, 24.20s wall` |
| integration | same, `--kind integration` | 0 | `pool: 8 workers, 95 files, 157.49s wall` |
| typecheck | `bun run typecheck` | 0 | `tsc --noEmit -p tsconfig.json` |
| canonical-reader audit | `check-plan-routes.py --canonical-reader-audit`, CI regex | 0 | `0 unresolved reader site(s) across 103 Python file(s)` (scanned=103) |
| consolidation audit | `check-plan-routes.py --consolidation-audit` | 0 | `0 consolidation finding(s) under bin/` |
| plan-route gate | `check-plan-routes.py` | 0 | `0 violation(s) across 2 plan(s)`; `examined 40 feature dir(s)` |
| instruction-path gate | `check-instruction-paths.py` | 0 | `scanned 68 file(s), 0 violation(s)` |
| layout gate | `layout_migration.py .` | 0 | `layout: 2 surface(s) clean, 0 mixed, 0 cannot-verify`; examined 40/1/7 |
| validate-feature-json | `validate-feature-json.py` | 0 | 40 file(s) |
| repository-state gate | `check-state.py` (the `git config core.hooksPath` step was skipped because it writes shared config) | **1 at pin** | two INV-26 rows for FEAT-2537 (see F-3). **0 at the feature tip 2a0904e8** |

- **Receipts** (`runs/r-20261125-2-validate-validator/qa/`):
  - `manifest-unit.json`: sha256 `4b47bdf3…c842`, tested_commit 8ae96bea, runner_exit 0, 68/68/68.
  - `manifest-integration.json`: sha256 `1cbda061…4ba6`, tested_commit 8ae96bea, runner_exit 0, 95/95/95.
  - Checked with `check-integration-shards.discover_expected` and `evidence_defects`, using validate-digest.py:2807's call
    shape: **0 defects** for both.
- **Bare `^FAIL` tokens in the unit log**: there are 4 `FAIL  BUG-1290 5a/5b/5c` lines, all inside
  test-factory-claim-mutation.py (exit 0). They are its deliberate mutation-proof output, not failures.
- **Main-session claims, all reproduced:**

  | Claim | Measured |
  |---|---|
  | test-inflight-registry 183/183 | `PASS - 183/183 checks passed` |
  | test-validate-digest | `ALL PASSED.` |
  | test-lead-start-return | `60 of 60 cases passed` |
  | test-lead-start-preflight | `61 of 61 cases passed` |
  | omp-hooks.test.ts | `247 pass / 0 fail` |
  | canonical-reader audit 0/103 | 0 / 103 |
  | consolidation audit | 0 |
  | typecheck | 0 |

## T-01 verify block
I extracted it from the pinned plan.yaml with yaml, piped it to `bash -s` in the pin, and it printed **VERBATIM_EXIT=0**.
The test file printed 183/183. The explicit immutables diff `a24eacee..8ae96bea` over the 4 immutable files exited 0.

## Fail-first

### SC-01 (natural red)
| Tree | `git grep -n live_children -- .claude/skills/harness/bin .omp/extensions` | Positive control `parent_agent_id=agent_id` in validate-digest.py |
|---|---|---|
| base a24eacee | **exit 0**, match `inflight_registry.py:543:def live_children(...)` | matches |
| pin 8ae96bea | exit 1 | matches, at `validate-digest.py:2914` |

- Cases 2b/2c are gone (grep exit 1).
- Case 29 asserts `live_claim(root, "harness-qa", …)` gives `claim is None and expired == 1`.

### SC-01 (mutant)
- **Mutant:** `/tmp/feat2537-mutant` holds the pinned module with `_omp_claim_live`'s `return int(recorded) == int(current)`
  changed to `return True`, beside a full copy of the pinned bin/.
- **Run:** `INFLIGHT_REGISTRY_DIR=/tmp/feat2537-mutant python3 <pin>/tests/integration/test-inflight-registry.py` exited 1,
  `3/183`:
  - **`FAIL - case25: a stranded child no longer holds its parent`**
  - case22 ×2
- **Case 25's other assertions stayed green under the mutant:** binds, live child holds, no other parent.
- **One-factor control:** the unmutated candidate copy in the same scratch layout exits 0 at 183/183.

### SC-02 (natural red)
- **Run:** `INFLIGHT_REGISTRY_DIR=/tmp/feat2537-base` (the a24eacee module, sha256 `caac8af5…`, beside the pinned bin/)
  against the pinned test file exited 1, `5/183`.
- **Red, exactly the receipt's 5 v1 assertions:**
  - persona-map strict
  - persona-map writer `(None, 1)`
  - persona-map warning
  - `{}` strict
  - `{}` warning
- **Green:** all 20 writer-producible controls, and both "empty v2 file" assertions. The candidate copy is 183/183.
- **The whole file ran on base.** All 183 checks executed; the pinned file no longer references `live_children`.
  - Rewritten cases 25 and 29 are green on base: they drive `live_claims` and `live_claim`, which did not change.
  - So they do not discriminate the deletion. The grep does.
- **Difference from t01-red-receipt.md:** that receipt totals 191 checks because it ran an intermediate test file that
  still had 2b/2c and the old case 25. The case-18 lines are identical.

## Behaviour-delta probe
`/tmp/feat2537-probe.py` ran 27 registry shapes × {strict `live_claims`, writer `live_claim`} and compared the base module
with the candidate on return or raise, stderr and file bytes.

- **SAME on base and candidate:**
  - missing, empty, whitespace, `{`
  - `[]`, `[claim]`, `null`, `1`, `"x"`, `true`
  - v2 empty, v2 live, v2+extra key
  - `{"schema_version": 2.0, "claims": []}`: v2 on both
- **DIFF, all inside the ruled class** ("every non-v2 object refused by strict readers, folded-with-warning by writers"):
  - `{}`, v1 map, `{"persona": []}`, `{"claims": []}`: strict `[]` becomes raise; the writer gains the warning, or the
    1→0 flip for the v1 map.
  - `{"schema_version":1}`, `{sv:2}`, `{sv:2,claims:"x"}`, `{sv:"2"}`, `{sv:true}`, `{"a":"x"}`: the writer gains the
    warning only.
  - v1 map holding a *live omp* claim, and schema-less `{"claims":[live]}`: base read the live claim (strict `['c1']`,
    writer kept it on disk); the candidate refuses it, or folds it and drops it from disk.
    - These are D-01's "folded to empty". Neither shape is writer-producible: v1 predates `runtime`.
    - I record them as in-class, not as a new delta. The ruling named only the expired-count flip, so the signer may want
      them noted.
- No other on-disk reader of the registry exists: a grep of bin/ and .omp/extensions finds no other `inflight-claims` /
  `_parse` / `_known_shape` reader.

## Findings
- **F-1 (substance, low, T-01). A surviving mutant leaves a non-v2 shape reading as "no claims".**
  - **Mutant:** `/tmp/feat2537-mutant2` defaults a missing `schema_version` to 2 in both `_known_shape` and `_parse`
    (`raw.get("schema_version", SCHEMA_VERSION)`).
  - **Result:** the pinned file passes **183/183** (exit 0), while a strict read of `{"claims": []}` returns `[]`.
  - **Scenario:** a regression that accepts version-less documents passes every test and re-opens DEC-218's
    "cannot read = no claims" hole for that shape. It violates D-01's "every non-v2 object refused".
  - **Untested non-v2 shapes:**
    - `{"claims": [...]}` without a version
    - `{"schema_version": 1}`
    - `{"schema_version": 2}` with no claims
    - `{"schema_version": 2, "claims": "x"}`
    - a v1 map with an empty list
    - scalar JSON (`null`, `1`)
  - Of these, only the version-less form currently has a surviving mutant. Case 37 covers sv=99, `[]` and `{`.
- **F-2 (form, low, T-01). Case 18 compares file state as parsed JSON (`_file_after` → `json.loads`), not bytes.**
  - SC-02 says "file bytes". For the v2 control, the writer rewrites compact JSON as indent=2 and sort_keys, and the test
    cannot see that.
  - My probe measured the bytes identical on base and candidate, so there is no defect today. Only the assertion is
    weaker than the text.
  - The v1 inputs also never assert that the file is unchanged after the *strict* read. Case 36 covers read-only only for v2.
- **F-3 (form, info, not T-01). check-state INV-26 exits 1 at the pin.**
  - It reports "plan projects building — the board reads review" for #2540 and #2537.
  - INV-26 reads the live GitHub board, and the pin predates the `2a0904e8` station-review commit. At the feature tip,
    which changes only the feature directory, check-state exits 0.
  - The cause is a live-board/pin-time artifact, not the diff. CI on the PR runs at the tip.

## Test-first audit
The case-18 rewrite and the code landed together in 8764b820. The red-before was recorded in that commit's
`t01-red-receipt.md`, and I reproduced it independently. Ledger commit d1777a89 precedes the code commit.

## Principles applied
- **Build the Lever:** I used a 27-shape scripted base-versus-candidate probe instead of reasoning about shapes one by
  one. It found the in-class live-claim fold and F-1's untested shapes.

Ephemeral evidence: the logs are `/tmp/feat2537-{qa-unit,qa-integration,base-run,mutant-run,mutant2-run,cand-run}.log`.
The excerpts above are the durable record.
