# FEAT-2397 T-01: red/green evidence

Baseline for red runs: `bdb1c2f68c63bdc7a2b8ba2203db72da80a2abe0`, the merge of origin/main. The spec
text names 9eb07b4f. Main ruled that bdb1c2f6 is the baseline: the production files are identical to it.

The baseline tree was exported read-only with `git archive bdb1c2f6 | tar -x -C /tmp/feat2397-base`,
and node_modules was symlinked into it. For each red run, the changed test file was copied into that
tree and run there. Green runs ran in the worktree. Raw outputs are in `t01-red-green/`, and the last
line of each file is its exit code.

| Step | Change | RED (baseline) | GREEN |
|---|---|---|---|
| A | inject-expertise `_emit` returns a single `{"context": ...}` object | red-A-inject-expertise-baseline.txt (9/46, exit 1) | (see C) |
| B | in-process drift check via `harness_boundary.load_repo_module` | red-B-inject-expertise-subprocess-checker.txt (tree = baseline + A; 37/46, exit 1) | green-inject-expertise.txt (46/46, exit 0) |
| C | single-pass `_capped_body` (parity with a frozen baseline) | red-C-capped-body-mutants.txt: mutants m1-m4 each fail the parity rows (exit 1) | green-inject-expertise.txt |
| D | TS: one decode in classifyPolicyRun, `PolicyResult.context` carried through, before_agent_start uses it with no fallback | red-D-ts-expertise-transport-baseline.txt (7 fail, exit 1) | green-D-ts-expertise-transport.txt (12 pass, exit 0) |
| E | dispatch-guard #10+#11 as one atomic edit | red-E-dispatch-guard-baseline.txt (174/178, exit 1) | green-E-dispatch-guard.txt (178/178, exit 0) |
| F | TS: taskModelOverride deleted, model forwarded untouched | red-F-ts-per-call-model-baseline.txt (2 fail, exit 1) | green-F-ts-per-call-model.txt (exit 0) |
| G | `.omp/config.yml` `task.perCallModel: "off"` plus SC-06 regression | red-G-omp-port-perCallModel-baseline.txt (31/35, exit 1) | green-G-omp-port-perCallModel.txt (35/35, exit 0) |
| H | validate-digest `_pass_through` no longer honours stop_hook_active | red-H-validate-digest-baseline.txt (7 failing, exit 1) | green-H-validate-digest.txt (ALL PASSED, exit 0) |
| I | TS yield adapter stops sending stop_hook_active | red-I-ts-yield-legacy-field-baseline.txt (exit 1) | green-I-ts-yield-legacy-field.txt (exit 0) |
| J | gate-runtime: false-field fixtures removed; per-call model row turned into a parity check | red-J-gate-runtime-baseline.txt (605/606, exit 1) | green-J-gate-runtime.txt (606/606, exit 0) |
| K | harness_yaml CLAUDE_CODE_* identity arms deleted; fire_noyaml identity now in the payload | red-K-domain-grant-identity-baseline.txt (28/30, exit 1) | green-K-domain-grant-identity.txt (30/30, exit 0) |
| L | #12: `contextUsageTokens(ctx)` reads `ctx.getContextUsage().tokens` (finite number only) inside the same orchestrator-only `task` tool_result trigger. The JSONL tail reader, `resolveSessionFile`, the inert/accessor notices, their types/constants and `contextNoticeEmitted` are deleted, along with the now-unused fs imports. Tests are table-driven: invalid values, below/equal/above, custom and default thresholds via a copied extension root, wrong agent/Main/non-task, repeated wakes, preserved content and absent isError, retry after a failure, and the post-domain gate after a throw | red-L-ts-context-usage-baseline.txt (37 fail, 9 pass, exit 1) | green-L-ts-context-usage.txt (46 pass, exit 0) |
| M | test-dispatch-guard.py: `case_f2274_unavailable_outcome`, `case_12_claim_lands_in_declared_worktree`, `case_31_repository_binding_read_from_the_feature_worktree` and `main` split into helpers/tables (`CASES` plus `_report`). Every assertion is kept | n/a (test-only refactor, grade-driven) | green-M-dispatch-guard-splits.txt (178/178, exit 0) |

The historical `*.fixture.jsonl` files and the frozen `prior-*.fixture` files are untouched. They no longer feed any test.

## Grades
`grades-changed-functions.txt` covers every changed or new function graded against bdb1c2f6 with `code_grade`. 0 are below bar: tests are at ≥3, and production is at ≥4. The four split functions now grade f2274 4, case_12 4, case_31 5 and main 5.

## Verify
- `verify-literal.txt`: T-01's verify block run verbatim from the worktree. It exits 0 with a 60 s wall time.
  - The 7 integration scripts all exit 0, with no `^FAIL` lines.
  - omp-native-gate-runtime takes 41.5 s under the 7-way pool, inside the 45 s per-script timeout.
  - `bun test tests/unit/omp-hooks.test.ts`: 247 pass, 0 fail.
  - `bun run typecheck`: clean.
- `verify-timings.txt`: a second pool run measured each script.
  - inject 3.7 s, dispatch-guard 16.9 s, validate-digest 38.5 s, gate-runtime 40.8 s.
  - domain-grant 16.5 s, instruction-paths 0.9 s, omp-port 8.3 s.
- `verify-canonical-reader-audit.txt`: 0 unresolved reader sites across 101 files.
- `verify-instruction-paths.txt`: 68 files scanned, 0 violations.
- `verify-code-grade.txt` was the first run. It exited 1 with one failure from the "self-grading allowlist has no stale entries" check: `test-validate-digest.py:run_t09 allowlisted grade is stale: expected 1, got 4`.
- `verify-code-grade-after-allowlist.txt` is the run after the deviation below. It shows `PASS test-code-grade` and exit 0.

## Deviation: out-of-list edit to tests/unit/test-code-grade.py (authorized)
- **Trigger:** T-01's intent mandates the split: "Every new/changed Python test function must grade >=3 ... split large existing grade-2 tests rather than inheriting their exemption." Splitting `run_t09` in `tests/integration/test-validate-digest.py` into `_t09_*` scenarios raised its grade from **1 to 4**.
- **Failing check:** the CR-01 "self-grading allowlist has no stale entries" check in `tests/unit/test-code-grade.py` then failed with `run_t09 allowlisted grade is stale: expected 1, got 4`. By that file's own rule, an exemption must not outlive the record it excused.
- **Edit:** exactly one line was deleted, `("test-validate-digest.py", "run_t09"): 1,`, from `SELF_GRADING_ALLOWLIST`. It was not re-pinned, and no other edit was made to the file.
- **Authorization:** the file is outside `tasks[0].files`. Main authorized the edit through a delegated ruling (fable-advisor AdvisorC7Allowlist, option A) as a recorded deviation, with no plan amendment.

## Out of list, left alone
- `tests/integration/check_domain_support.py` `_env` still sets `CLAUDE_PROJECT_DIR`.
