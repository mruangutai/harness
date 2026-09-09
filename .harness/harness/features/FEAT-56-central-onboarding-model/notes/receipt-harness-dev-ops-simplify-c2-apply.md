# F4 apply — FEAT-56 simplify-c2 — receipt

**Applied F4 exactly as specced**, no drift: `_central_model_marker_cases`, `main()`'s `results`
tuple shape, and the `[-1]` tuple arity all matched my prior spec verbatim (own receipt,
`receipt-harness-dev-ops-simplify-c2-simplification.md` §F4) — no adaptation needed.

## Change

Added `case_central_model_marker_order_regression()` (`tests/integration/test-onboarding-split.py`,
after `_central_model_marker_cases`, before `case_init_no_addrepo_markers`), asserting both
directions on a synthetic marker string: correctly-ordered markers pass the ordering clause, and
reversed markers fail it. Wired into `main()`'s `results` tuple, appended after
`case_cli_probe_strings_absent_from_both_cut_skills()`. Nothing else touched.

## Negative-direction proof (neuter-and-revert)

Neutered `_central_model_marker_cases` line 116 (`ordered = positions == sorted(positions) and
len(set(positions)) == len(positions)` → `ordered = True  # NEUTERED-FOR-PROOF`), ran the file
directly:

- Every other case stayed PASS.
- `FAIL: synthetic ordering regression: reversed markers fail the ordering clause — first-occurrence
  lines (0-indexed) were [2, 1, 0]` — exactly the new case's negative direction, exactly as
  predicted. `EXIT=1`.

Reverted from a pre-neuter backup (`cp` before mutating), `cmp` confirmed byte-identical restore,
re-ran: `EXIT=0`, all 25 cases PASS including both new directions. `git diff` after the full
apply+proof+revert cycle shows only the 17-line addition (see below) — the neuter never landed.

## Suite verification (against the batch baseline)

- `run-unit-tests.sh --kind unit` → **exit 0**. `^FAIL ` lines: exactly the 4 by-design
  `BUG-1290 5a/5b/5c` mutation-proof lines from `test-factory-claim-mutation.py` (that file itself
  PASSES). Matches baseline.
- `run-unit-tests.sh --kind integration` → **exit 1**. `^FAIL ` lines: exactly 6 cases, all in
  `test-check-plan-routes.py`: `case_04_all_granted_exits_0`,
  `case_05_ungranted_declared_main_session_exits_0`, `case_15_deviation_plan_still_exits_0`,
  `case_17_midpattern_wildcard_grant_exits_0`, `case_19d_explicit_path_unaffected_by_the_root_guard`,
  `case_19d2_explicit_path_with_no_tasks_still_exits_0` (plus the file-level aggregate line, not a
  7th case). Matches baseline set name-for-name — no new or missing case.

No repair attempt needed; the apply introduced zero failures outside the baseline.

## `git status --porcelain` (verbatim, post-apply)

```
 M tests/integration/test-onboarding-split.py
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-ai-dev-simplify-c2-altitude.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-backend-dev-simplify-c2-reuse.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-data-engineer-simplify-c2-efficiency.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-dev-ops-simplify-c2-simplification.md
```

The four `??` receipts are siblings' artifacts (SimplifyAltitudeC2b, backend-dev reuse,
data-engineer efficiency, my own prior simplification-pass receipt) — not mine to touch here.
`git diff --stat` confirms the one modified file: `tests/integration/test-onboarding-split.py |
17 +++++++++++++++++, 1 file changed, 17 insertions(+)`. Nothing committed.

```yaml
VERDICT: PASS
DIGEST:
  headline: F4 applied — two-direction ordering-regression case added and wired, negative direction proven live via neuter/revert, baseline failure set unchanged
  change_type: config
  applied: [tests/integration/test-onboarding-split.py]
  suite: pass
  task: none
  test_kinds_written: []
  open_questions: []
  files_touched:
    - tests/integration/test-onboarding-split.py
    - .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-dev-ops-simplify-c2-apply.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-dev-ops-simplify-c2-apply.md
```
