# Fix c1 — FEAT-1559 (validate c1 FAIL at 0e8301a5) — main-session-direct (DEC-174)

The lead's must-fix list is in `runs/validate-validator/digest.md`. Every finding cites a
main-session-direct task, so the main session fixes it. No delegated dev owns any of them.

## Must-fix, in the lead's order

1. **SC-04 discovery gap (T-03): `check-plan-routes.py` walked whatever was present.**
   - **Fix.** The completeness check moved out of `population` into one seam,
     `feature_corpus.require_landed(root)`. It compares the names the landed root tracks against
     the names it reaches, and raises with N of M and the sorted missing names. `population` and
     `discover_plans` both call it now; discovery calls it after the layout refusal and before
     the walk. It exits 2 with a restore remedy. Explicit-path runs are unchanged, because they
     never call `discover_plans`.
   - **New tests** in `tests/integration/test-feature-corpus.py` `Discovery`:
     - one owner directory removed while the others remain, from a sparse worktree: exit 2,
       "reaches 3 of 4 tracked feature directories; missing: harness/FEAT-2-beta", and no walk
       ran;
     - the same in a full clone: exit 2, naming the missing directory;
     - the normal-discovery case now also asserts it does not exit 2.
   - **Red.** With `check-plan-routes.py` at HEAD and everything else fixed, both new cases fail
     with `0 != 2`: the survivors were route-checked and exited 0.
   - **Fixture.** `test-check-plan-routes.py` `_owner_branch` now `git init`s its owner. It
     faked a linked worktree whose owner was not a repository. The new check correctly refused
     it ("not a git repository"), as `population` already would. An owner checkout is always a
     repository, and an unborn one tracks nothing, so case 27 still tests only manifest
     routing.
2. **`board_lifecycle._feature_dirs` cutover was unbound (T-03).**
   - **New tests** in `test-feature-corpus.py` `BoardStatus`, which calls
     `_status_findings`:
     - a landed feature, present only at the owner and carrying an active schema-valid plan, is
       compared against its cards from the sparse worktree (wrong card → finding; right card →
       none);
     - a broken layout yields exactly one "feature cards cannot be audited" finding.
   - **Mutants.** Going back to a local `glob` of the checkout fails the first test. Dropping
     the layout refusal fails the second. The file was restored byte-identical after each.
3. **`check-decision-anchors` routing and exit 2 were unbound (T-03).**
   - **New tests** in `test-feature-corpus.py` `DecisionAnchors`. From a sparse worktree, an
     anchor at `BUG-3-gamma/notes/deep/history.md:1` (a basename with a single candidate, absent
     locally) passes (`examined 1 anchor(s), 0 failed`). With the owner manifest moved away,
     the same run exits 2 with "cannot check".
   - **Mutant.** Going back to a local `count_lines(candidate)` fails both tests (exit 1, "line
     past end of file").
4. **Grade failures (T-01, T-03, T-05).** The nine functions now meet their bar. Each one was
   split by extracting helpers, with no behaviour change:

   | Function | Before | After | Extracted |
   |---|---|---|---|
   | `feature_corpus.reached_feature_dirs` | 3 | 5 | `_listdir`, `_segment_dirs` |
   | `feature_corpus.population` | 3 | 4 | `_local_entries`, `_landed_root` |
   | `feature_corpus.identity` | 3 | 4 | `_pin_identity`, `_branch_id` |
   | `feature_corpus.claiming_segments` | 3 | 5 | `_disk_segments`, plus reuse of `expected_feature_dirs` |
   | `feature_corpus.derive_cone` | 3 | 5 | `_maximal_outside_features` |
   | `worktree-state.render` | 3 | 4 | `_finding_lines`, `_outcome` |
   | `check-instruction-paths._classify` | 3 | 5 | one helper per anchor |
   | `test-corpus-non-regression.manifest_findings` | 1 | 4 | `_header_findings`, plus one check per outcome behind `OUTCOME_CHECKS` |
   | `test-feature-corpus-census.glob_names` | 1 | 5 | `_module_aliases`, `_function_aliases` |

   The extractions sit next to their callers. The existing tests that cover them pass unchanged:
   `test-worktree-state*`, `test-feature-corpus*`, `test-check-instruction-paths` and
   `test-corpus-non-regression`. That includes the planted-inconsistency mutants for
   `manifest_findings`.

## Other reported items

- **QA L-1 (receipt counts).** The receipt's 54/86 were counts of `^PASS test-` lines, not
  files; the runner counted 52/80. The figures are corrected by an erratum appended to
  `notes/non-regression-receipt.md`. The original lines are left in place.
- **QA G-1 (`derive_cone` maximal clause).** Not fixed; the lead called it advisory. Listing a
  nested directory beside its parent changes no materialised file in cone mode, so a test would
  pin an implementation preference.
- **QA G-4 (`check-domain` own-checkout sweep skip).** Not fixed: the evidence is
  inconclusive. A single pool-only red could not be reproduced in isolation, and it stays
  recorded as an assurance limit.
- **Grade-2 functions.** The twelve keep the written reasons in the code review. Three of them
  shrank here.

## Verification

The canonical-reader audit reports "0 unresolved reader site(s) across 99 Python file(s)".
`test-feature-corpus.py` runs 24 tests, OK. `test-check-plan-routes.py` reports no failures,
with case 27a/b/c passing. Full-suite, grading and check-state results at the fix tip are in
STATE.md and in the commit that records this receipt.
