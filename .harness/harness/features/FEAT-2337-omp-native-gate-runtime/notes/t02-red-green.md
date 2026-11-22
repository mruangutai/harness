# T-02 RED/GREEN — trusted exact-coverage QA receipts replace the #919 rerun

Builder: BuildT02QaReceipt (main-session-direct, DEC-174). Worktree W at HEAD e1aa5837. The seven owned
files are byte-identical at plan base dd04e52a and at the pre-edit HEAD (`git diff --stat dd04e52a HEAD`
touches none of them), so the pre-implementation run below is the plan-base run. Candidate source only:
this proves candidate behavior from W's working tree. It says nothing about the installed control-plane
hook, which still runs the #919 rerun for this feature's own validate (BRIEF Verification gaps).

## Files changed

- `.claude/skills/harness/bin/validate-digest.py`: `_resolve_run_unit_tests_bin`, `RUN_UNIT_TESTS_BIN`,
  `_artifact_holder`, `_claimed_kinds`, `_reverify_suite`, `_RUN_POOL_*`, `_run_pool_file_lines`,
  `_is_failed_file_line`, `_run_pool_mutated_indexes` and `_print_independent_run` are deleted. Nothing
  falls back to them. `_qa_claims_unconditional_pass` is still the trigger. `check_qa_matrix_claim` now
  verifies receipts:
  - Identity is resolved once per call through `_run_identity`, `authorization_root`,
    `_require_own_claim` and the parent's live `harness-validator-lead` claim in the same checkout. The
    run comes from `registered_destination(..., "harness-validator-lead")`. `review_sha` comes from
    `registered_feature` and is reconciled with `harness_review_pin` through `resolve_reviewed_commit`.
  - The only path read is `<registered feature dir>/runs/<run-id>/qa/manifest-<kind>.json`, checked with
    a realpath-equality test plus `authorization_descriptor` (O_NOFOLLOW, regular file only).
  - Each satisfied claimed active unit/integration kind needs its own receipt. An empty or unsupported
    claim is refused.
  - Lineage: `tested_commit` must equal `review_sha` or descend from it (`merge-base --is-ancestor`).
    Every commit in `rev-list review..tested` is checked with
    `diff-tree -r -z -m --root --no-renames --name-only`, and each changed path must start with
    `<feature_rel>/`. Results are cached per (review, tested, feature_rel).
  - Coverage and shape come from check-integration-shards.py `discover_expected` and
    `evidence_defects` (kind=..., shards=1).
  - Every problem refuses with exit 2, one line per problem, followed by
    `python3 <checkout>/.claude/skills/harness/bin/run-unit-tests.py --kind <kind> --shard 1/1 --manifest <run>/qa/manifest-<kind>.json`
    for each failing kind. `_Untrusted` and `_evidence_failures()` count as invalid evidence. Any other
    exception still reaches hook_guard (DEC-100). The module docstring and #919 comments are updated.
- `.claude/skills/harness/bin/check-integration-shards.py`:
  - `integration_paths` is replaced by `expected_paths(names, kind=KIND)`, driven by an `EXPECTED_PATHS`
    map with integration and unit, both top-level only. An unsupported kind raises `ValueError`.
  - `_identity_defects`, `coverage_defects`, `evidence_defects` and `discover_expected` take an optional
    `kind`, which defaults to integration.
  - The CLI, `_parse`, `_report`, the four-shard defaults and the bootstrap prologue (DEC-234) are
    unchanged. `.github/workflows/tests.yml` is untouched.
- `.claude/skills/harness/bin/check_state/feature_record.py`: one comment line now reads "issue #919's
  receipt check fires only on a qa PASS". INV-47 code is untouched.
- Tests: `tests/integration/test-validate-digest.py`, `tests/unit/test-validate-digest-run-pool-lines.py`
  (converted in place), `tests/unit/test-integration-shard-validation.py`,
  `tests/integration/test-integration-shard-aggregation.py`.

## RED: tests first, against the unmodified implementation (= dd04e52a for these files)

Commands, run from W before any production edit:

    python3 tests/unit/test-integration-shard-validation.py        -> exit 1
      FAIL positive_cases ran AttributeError: module 'check_integration_shards' has no attribute 'expected_paths'
      FAIL unit_kind_cases ran TypeError: evidence_defects() got an unexpected keyword argument 'kind'
      2 failed
    python3 tests/unit/test-validate-digest-run-pool-lines.py      -> exit 1
      Ran 7 tests: FAILED (failures=6, errors=7)
      ERROR ... no attribute '_receipt_refusal' / '_repair_command'
      FAIL test_no_pooled_rerun_parser_or_reporter_survives (name='_run_pool_file_lines' | '_print_independent_run' |
           '_reverify_suite' | '_resolve_run_unit_tests_bin' | '_artifact_holder' | '_claimed_kinds')
    python3 tests/integration/test-integration-shard-aggregation.py -> exit 1
      TypeError: discover_expected() got an unexpected keyword argument 'kind'   (kind_seam_cases)
    python3 tests/integration/test-validate-digest.py --only run_feat2337_qa_receipt_cases -> exit 1, 49 FAILING (13/62 ok), 27.4 s
      the failures cover every refusal row: no kinds, unsupported kind, all 16 doc tampers, 3 raw tampers,
      missing/directory/FIFO/symlinked receipt, symlinked qa dir, other-run and foreign-artifact receipts,
      no parent, spoofed parent, non-validator parent, no live claim, disagreeing dispatch pin, no/ended/two
      open validator runs, unpinned and unresolvable review_sha, code change, foreign feature,
      separator-less prefix sibling, change-then-revert, rename into the feature dir, merge bringing code,
      older commit, divergent commit, untracked working-tree test, and:
      FAIL  [feat2337] zero runner invocations across the accepted and refused returns
            | ['--kind unit', '--kind integration', '--kind unit', '--kind integration']
      the ok rows are the controls: exact pin, agreeing pin, unit-only claim, BLOCKED/FAIL/dev reads,
      ledger-only descendant, ledger-only merge, HEAD drift after an exact-pin receipt, both shim positive
      controls
    --only run_bug919_qa_matrix_cases            -> 7 FAILING (disagreement, missing evidence, RED wiring proof,
                                                    SC-02 every red kind, SC-03 no kinds, SC-04 OSError, SC-04 timeout)
    --only run_bug919_resolve_fallback_case      -> FAIL #1185: an ambiguous feature checkout refuses, never substitutes the owner
    --only run_bug919_resolve_by_artifact_case   -> FAIL #1883: an artifact in another worktree of the family lends it no receipts
    --only run_bug2253_cases                     -> 3 FAILING (all three receipt diagnostics)

The final suite was also run against an extracted plan-base bin
(`git archive dd04e52a .claude/skills/harness/bin | tar -x -C $B`, then
`VALIDATE_DIGEST_BIN=$B/.../validate-digest.py`):

- feat2337 had 51 FAIL and 14 ok. The new rows were red too: "a missing claimed receipt refuses the
  PASS" and "a refused PASS keeps QA's own claim for the retry".
- bug919 had 7 FAIL; #1185, #1883 and bug2253 were each red.
- The migrated controls in qa_record_read_failure, qa_brief_authority and unknown/symlinked checkout
  identity crash red there. The base prints "could not independently re-run … NOT verified", so those
  controls fail open.

Positive controls that prove the zero-fallback witness can see a rerun:

- `positive control: the argv shim records a direct runner invocation` → `['--kind unit']`.
- `positive control: the pre-FEAT-2337 validator's rerun is recorded by the shim` runs `git show
  dd04e52a:…/validate-digest.py` in an isolated bin → `['--kind unit', '--kind integration']`.

## GREEN

    bash -o pipefail -c 'timeout 55 bash -o pipefail -c "python3 tests/integration/test-validate-digest.py --only run_feat2337_qa_receipt_cases && python3 tests/unit/test-integration-shard-validation.py && python3 tests/unit/test-validate-digest-run-pool-lines.py"'
      -> exit 0, about 16 s total; 65/65 feat2337 cases passed; ALL PASSED; "0 failed"; "Ran 7 tests … OK"; no FAIL line
    python3 tests/integration/test-validate-digest.py             -> exit 0, ALL PASSED, about 25 s
      (133 CLI, 10 bug919, 65 feat2337, 2 #1185, 2 #1883, 3 bug2253, 27 hook, 26 SC-07, 23 T-09, 81 BUG-1898, …)
    python3 tests/integration/test-integration-shard-aggregation.py -> exit 0, "0 failed"
    Neighbor checks (unchanged files): test-validate-digest-shadows.py 46/46, test-suite-claim-preservation.py 0 failures,
      test-broad-catch-census.py ALL PASS, test-run-unit-tests-shards.py 0 failed.

Grades: `code_grade.grade_source` over the four test files plus the two bin files puts every new or
changed function at 3 or above. Six pre-existing functions grade below 3, and this task does not change
them: run_cli_cases 1, run_t09 1, run_hook_cases 2, shard-unit manifest_set_cases 2, aggregation
manifest_cases 2 and coverage_cases 2. The SC-08 cumulative grader in T-03 is the authority.

## Assertion migrations (old contract replaced, invariant kept)

- #919 agree/disagree/non-PASS/missing-runner/red-wiring (stub plus the removed env seam) became the
  receipt outcomes in `run_bug919_qa_matrix_cases`:
  - A green claimed receipt is accepted.
  - The runner's own red receipt is refused, naming `tests/integration/test-i2.py returned 1` and
    `runner_exit 1`.
  - BLOCKED reads no receipt.
  - A missing receipt now REFUSES. The old assertion was a fail-open "could not independently re-run"
    with exit 0.
  - The wiring mutant (`_bug919_red_mutant`, same anchor) still flips the refusal to acceptance.
- BUG-1756 SC-01 "runs once per kind": only claimed kinds are read, and a unit-only claim needs no
  integration receipt.
- BUG-1756 SC-02 "first failure stops the rerun": every red kind is named.
- BUG-1756 SC-03 "no kinds → one bare run": no kinds is refused, never defaulted.
- BUG-1756 SC-04 "spawn OSError / timeout fail open": the same exceptions raised by git while reading
  receipts now refuse with exit 2 and the repair command, never a traceback.
- #1185 "`feature_root` failure resolves None, no owner substitution": with two worktrees matching the
  feature, the hook refuses ("cannot resolve the feature checkout"). The owner's valid receipts, which
  accept before the ambiguity, are never used.
- #1883 "rerun resolves to the artifact's linked worktree": a digest artifact in another worktree of
  the family (`process-gaps`, holding its own valid receipts) lends none. The feature's own linked
  checkout, the worktree named for it, supplies them and is accepted.
- #2253 buried/echoed/quiet (stubbed pool output) now uses real runner receipts:
  - 23 failing files (one name contains a space) are each named exactly once above `Repair:`, with no
    tail cut.
  - A failing test that prints run_pool-shaped `FAIL`/header lines for `test-ghost.py` adds no name.
  - `runner_exit 1` with all records green is named together with its receipt path.
- `tests/unit/test-validate-digest-run-pool-lines.py` was converted in place. The `FileLines` and
  `Report` classes are kept, and the dead `_run_pool_file_lines`/`_print_independent_run` imports are
  gone. It now covers:
  - all problems in order, duplicates kept, no tail cut;
  - spaces kept verbatim;
  - control characters escaped, so no line can be forged;
  - the refusal layout and the exact repair command;
  - one repair line per kind;
  - a check that the removed seam names are absent.
- Unconditional-QA fixtures in `run_qa_record_read_failure_cases`, `run_registration_decoder_depth_cases`,
  `run_qa_brief_authority_cases`, `run_unknown_checkout_identity_cases` and
  `run_symlinked_checkout_identity_cases` carry no receipts:
  - Their old exit-0 controls and restorations relied on the removed fail-open. They now assert
    `_reaches_receipt_check`: the contract accepted the return, only the receipt check refused it, and
    QA's claim was kept. Lead restorations still assert exit 0 and release.
  - The corrupted cases in those groups, plus `run_qa_ambiguous_checkout_case` and
    `run_qa_unknown_authorization_cases`, now assert `_refused_before_receipts`. That stops their
    exit-2 assertions from passing vacuously on the new receipt refusal.
- Claim release is still covered in feat2337: an accepted PASS releases QA's claim, and a refused one
  keeps it.
- FEAT-2274 site: there was no unavailable emission at the old fail-open site. feat2337 now asserts
  "a receipt refusal is a refusal, never an unavailable outcome" (no `decision: unavailable` line).
- check-integration-shards unit: the `integration_paths` call became `expected_paths(FILTER_NAMES)`,
  and the old filter expectation is kept unchanged. Unit kind cases were added.
- Aggregation CLI: `repository()` gains unit files at three points: the tested commit, a HEAD-only
  commit and the working tree. `kind_seam_cases` covers:
  - unit discovery from the tested commit only;
  - the integration default when no kind is given;
  - unit evidence: exact, HEAD-only, working-tree-only and omitted;
  - the CLI refusing `--kind`;
  - unit manifests refused under the CLI default.

## Behavior note for Main

A qa PASS with `suite: pass`, `matrix_ok: true` and `kinds: []` is now refused even when the feature's
BRIEF is inspection-only. This is the plan's "empty claims refuse" rule. Before, such a return passed
only because the rerun failed open.

QA must also be dispatched by a live `harness-validator-lead` run with exactly one open registered
validator run. A main-session-direct QA dispatch therefore cannot PASS unconditionally until T-03's
guidance routes QA receipts through that run.
