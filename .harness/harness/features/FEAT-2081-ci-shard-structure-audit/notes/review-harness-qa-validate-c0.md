# QA gate — FEAT-2081 at review_sha fc942ec4 (validate c0)

**BLUF: PASS.** Final matrix run once at a clean pinned checkout of `fc942ec4ebb0783f61e9809e3fc329b7f53be3e6`
(`git rev-parse HEAD` = pin, `git status --porcelain` empty): unit exit 0, integration exit 0. Every automated SC
(01/02/03/06/07/08) has fail-first evidence. No QA-side blocker to `uat.md` becoming ready; see "UAT-ready" for the
non-blocking staleness items. SC-04/05 inspection prerequisites below are mine; SC-09/SC-10 are user UAT and not graded.

## Isolation and pin equality
Pinned checkout via `pinned-checkout.py` (`FEAT-2081-ci-shard-structure-audit--validate-c0--harness-qa`), HEAD verified = pin.
Feature worktree HEAD `0a3e9ae6` is the pin plus a `feature.json` pin-only commit (`git diff --stat fc942ec4 HEAD` = that one file).
`check-plan-routes.py` at the pin hashes `608c6446013d6862` = the equivalence note's post-change checker; the file has
changed only in `3cdd3f19` and `d89f9b23` (neither after the proof). Run env: `env -u HARNESS_AGENT_TYPE` (repo G-07).

## Matrix (harness.json test_matrix, resolved against the full merge-base..pin diff)
| task | change_type | required | state | command / receipt |
|---|---|---|---|---|
| T-01 | cross_module | unit + integration | satisfied | below; new `test-runner-unsharded.py` (unit), `test-run-unit-tests-shards.py` + kinds/layout/pool (integration) |
| T-02 | feature | unit + integration | satisfied | `test-integration-shard-validation.py` (unit), `test-integration-shard-aggregation.py` (integration) |
| T-03 | cross_module | unit + integration | satisfied | `test-structure-audit-index.py` (unit), `test-structure-audit-single-pass.py`, `test-checker-structure-locks.py` (integration) |
| T-04 | config | integration only `if touches_config_shape` | n/a trigger; integration satisfied anyway | `test-integration-shard-aggregation.py`; yaml parse exit 0 |
| T-05, T-06 | docs | none | not_applicable | |

`kinds`: unit `run-unit-tests.py --kind unit` → exit 0, **pool: 8 workers, 49 files** (= `ls tests/unit/test-*.py`, 49);
integration `--kind integration` → exit 0, **76 files** (= `ls tests/integration/test-*.py`, 76). All seven T-01/T-02/T-03
verify-listed integration scripts and three unit scripts printed their own `PASS` line in those runs (each exactly once), so the
plan's verify blocks are covered by the full suites; not rerun individually. Non-suite verify items run: canonical-reader audit
`0 unresolved reader site(s) across 97 Python file(s)` (rc 0); `yaml.safe_load(tests.yml)` rc 0. No unexpected `FAIL`/`ERROR` lines
except one expected-negative `ERROR could not resolve scan root` printed by a passing unit test. `functional`/`eval` excluded (DEC-187),
`component`/`ui`/`typecheck` unresolved but outside this Python/workflow diff (BRIEF verification gaps).

## fail_first per automated SC (tier: N = natural red against absent/old code; M = constructed mutation)
- **SC-01 (N)** evidence-T-01: new `test-run-unit-tests-shards.py` vs pre-fix runner → exit 1, 25 FAIL/8 PASS covering independent witnesses:
  completeness exactly-once, LPT-vs-round-robin weighting, equal-weight tie-break, unknown-file inclusion (`default_seconds`), empty shard
  (pool not invoked, empty manifest), 14 malformed-argument cases, manifest completed-vs-selected. Pre-fix passes were the positive controls.
  Post-fix at pin: green in my run.
- **SC-02 (N + M)** evidence-T-02: pre-gate unit `exit 1 cannot load gate`, integration `FileNotFoundError`; per-defect mutation table
  (C-failure/skipped/cancelled/missing/unrecognized/absent, each reddens named checks-/matrix- cases) with the all-success positive control.
  **I re-proved at the pin (post-simplify code):** `value != "success"` → `not in ("success","cancelled")` ⇒ unit exit 1 (4 FAIL: checks/matrix cancelled rejected,
  diagnostics) and integration exit 1 (FAIL checks-result cancelled, "exit 0: PASS integration…").
- **SC-03 (N + M)** evidence-T-02 table: missing manifest, duplicate shard id, extra manifest, foreign commit/kind, within-shard and cross-shard
  duplicate, omitted, unexpected, empty expected suite, selected-without-completion, plus oracle witnesses X-rows (expected from HEAD / working-tree glob /
  selected union each redden the two-commit conflicting-tree fixture). **I re-proved at the pin:** within-shard duplicate threshold `>1`→`>9` ⇒
  unit exit 1 and integration exit 1 ("duplicated within shard 1" diagnostic missing, defect count wrong). Note the defect is still caught by the cross-coverage
  leg (`completed 2 times`), so this mutation is not a sole-detector for exit status; the diagnostic/count assertion is what discriminates (O-05).
- **SC-06 (N, strongest)** `CHECK_PLAN_ROUTES_BIN=<8e0b9e90 checkout> python3 tests/integration/test-structure-audit-single-pass.py` → exit 1, 9 failures
  (in-process consolidation/feat62/broad-catch and CLI: every-node-once, no source re-parsed, overlapping checker sources) vs post exit 0
  (`99 trees, 202781 visits = 202781 node occurrences`; pre: 210 trees, 557328 visits over 432491 nodes, 30442 not-once). Receipts:
  `qa-structure-audit-equivalence.md` ("Red-first receipt"), `evidence-T-03.md`.
- **SC-07 (M, natural red impossible: asserting existing behavior)** evidence-T-01 M1 drop-first-file, M2 destroy attribution (`run_pool.py`), M3 mask failure; unit/integration/no-arg forms each fail.
  **I re-proved M1 and M3 at the pin** (`git apply` in the disposable pin, restored via `git checkout`, `git status --porcelain` empty):
  M1 `*_scripts(patterns)[1:]` ⇒ exit 1, 6 FAIL (attributed + count, unit/integration/no-arg); M3 `run_pool.main([...]) and 0` ⇒ exit 1, 6 FAIL (child failure propagates, per form). M2 rests on the author's receipt (not re-run).
- **SC-08 (M + N)** omitted integration file and masked integration failure = the `--kind integration` rows of M1/M3 (re-proved above); `test-run-pool.py` seam red: `TypeError: main() got an unexpected keyword argument 'completed'` (N, evidence-T-01).
  Existing `test-run-unit-tests-kinds/layout` keep complete-discovery assertions (3- and 2-line additions only).

## Independent defect witnesses and positive controls
SC-06 per-rule violating witnesses = 53-input equivalence table (every structure-lock mutant: station literal, drifted bucket, second loader, module body ×6, reads ×9,
authority ×4, posture ×2, reparse ×2, broad-catch ceilings ×14, package lock ×10); identical old/new findings, order, CLI exit/stdout/stderr, `non_identical=[] suite_failures=[]`.
Positive controls: SC-01 checked-in weights provenance/73→(now re-measured) positive records; SC-02/03 all-success exact-coverage case; SC-06 clean real-tree and clean fixtures
(`findings=0`, exit 0 rows).

## Equivalence-corpus audit (qa-structure-audit-equivalence.md)
- Breadth: 53 inputs = real tree + every `CASES` mutant/fixture from `test-checker-structure-locks.py`, both entry paths (in-process public calls; `--consolidation-audit` CLI), compared byte-for-byte.
- Traversal counts: pre 210 parsed trees / 557328 visits / 30442 nodes visited ≠ once; post 99 trees / 202781 visits / 0.  Embedded programs 2→1 is a tree-count artifact of the fixture, not a gap (both runs audit the same copy).
- History independence: permanent tests never reference 8e0b9e90 or git history; the old checker enters only through the optional `CHECK_PLAN_ROUTES_BIN` env override (grep of the five permanent test files for `8e0b9e90|git log|merge-base|worktree add` returned nothing). The single-pass test does not install `_PARSED`/`_cached_parse` (grep: none).
- Residual: red run predates the final index edit (node total differs by 2, noted by the author); the checker hash at the pin equals the post-final-edit checker the green run used.

## Completion-vs-selection, tested commit vs HEAD/partition (code audit at pin)
`check-integration-shards.py`: coverage counts only `completed_files`; `selected − completed` and `completed − selected` are separate defects; expected set =
`git ls-tree -r -z --full-tree --name-only <--commit>` filtered by `tests/integration/test-[^/]*\.py` fullmatch; never the duration table, selected union, working tree or partition.
Fixtures use a two-commit repo with conflicting HEAD and working tree (evidence-T-02 X-rows). Simplify commit `fc942ec4` touched this gate, the aggregation and shards tests as behavior-preserving refactors
(inline `_defect`, flatten `_record_defects`, shared `git_support`); suite green at pin and my two mutation re-proofs above redden post-simplify code.

## SC-04/SC-05 inspection prerequisites (pinned `git show fc942ec4:.github/workflows/tests.yml`; line = pin)
SC-04: `on.push.branches: [main]` + unfiltered `pull_request` L19-23; `cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}` L28-29; job id `integration` no `name:` L417; `needs: [checks, integration-shards]` L419;
job-level `if: always()` L425; matrix `shard: [1,2,3,4]`, `fail-fast: false` L366-368, all `runs-on: ubuntu-latest`; `Validate shard completeness` `if: always()`, results passed literally via env L444-.
SC-05: Unit suite L106, Validate feature execution state L115, Plan-route gate L165, Canonical-reader audit L227, Instruction-path gate L245, Layout gate L271, Repository-state gate L337 — all in `checks` (no `continue-on-error`), summary/nonempty-discovery bodies intact (diff removes one `run:` = the moved Integration suite step);
`needs.checks.result` must be `success` in the validator, so any gate failure/non-execution blocks `integration`. Reviewer/user still own the sign-off; this is a QA read, not UAT.

## Findings (ranked)
1. **low / test-first / T-03 — no retained fail-first for `tests/unit/test-structure-audit-index.py`** (unit kind of cross_module). evidence-T-03 records 25 PASS only; the red-first is carried by the integration single-pass test. Scenario: an index bug the unit test alone would catch cannot be shown to have reddened it. Remedy: advisory — one mutation/perturbation receipt if the user wants unit-kind discrimination; not gating (SC-06 evidence kind is integration).
2. **low / assurance / T-01,T-02 — mutation tables are author-run on uncommitted trees (ad119cb8/d89f9b23)**. I independently reproduced SC-07 M1/M3 and two gate mutations at the pin; the rest (M2, weighted/tie/unknown-file, ~25 T-02 rows) rest on author receipts, tier M. Remedy: none required; label tier M.
3. **info / UAT draft hygiene / T-06** — line hints and shard-assignment hints in `uat.md` (workflow lines "at 0ebdaef7", `test-onboarding-split`→shard 4) are stale after `98c3438b`/`95ccc992` (precompile step added, weights re-measured). They are labeled non-authoritative and the table has a "line at review_sha" column the reviewer fills.
4. **info / SC-10 L-01** — same-corpus fixed-timing record is pending user execution (not code). T-03 evidence timings (locks 3.05→2.57 s, CLI 0.64→0.36 s) are same-host/interleaved but each side audited its own bin; the uat.md already says so.

No FAIL-grade finding; no stub/dormant path found in the new gate (every validator branch is reached by a CLI case).

## UAT-ready blockers (answer)
Nothing in QA blocks draft `uat.md` → ready. Remaining gate-table rows are procedural: this QA verdict (now available), code-reviewer verdict, SC-04/05 reviewer fill-in, Main's final whole-suite note (my matrix run may be cited but is not Main's own), and `review_sha:` field still blank in the draft (fill with `fc942ec4…`). Refresh stale line hints (finding 3) or let the reviewer overwrite the column. SC-09/SC-10 stay pending the user.

## Assurance bounds
Live CI facts (runs 37324916242/37325307899/37335457819) are given context, not re-observed by me. Edits to `bin/` were refused for harness-qa by check-domain (honored); perturbations used `git apply` in the disposable pin and were restored (`git status --porcelain` empty). Pin removed on return.
