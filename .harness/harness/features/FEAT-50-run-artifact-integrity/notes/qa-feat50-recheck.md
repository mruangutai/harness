# QA re-check — FEAT-50-run-artifact-integrity — fix-cycle re-review

**Verdict: PASS.** All three prior findings are closed at the actual repository HEAD
`7505b8739fd19a68601a27898d880fc719962712`. No test case name was lost in the delta. All seven
targeted regression scripts ran with substantial, non-zero case counts and zero failures. The
test-matrix floor (all tasks `change_type: bugfix` or `docs`) is satisfied.

## SHA discrepancy — flag, not a code finding

`feature.json`'s `review_sha` field reads `7505b87681c8d8007a2677381313581f61faf1b0`. That object
**does not exist** in this repository (`git cat-file -e` exits 1; `git rev-parse --verify
...^{commit}` exits 1). The actual `HEAD` is `7505b8739fd19a68601a27898d880fc719962712`
("fix: close FEAT-50 review findings" — same subject line the short `git log --oneline` shows for
`7505b87`), which is almost certainly the commit the pinning was meant to name; the two hashes
share only their first 7 hex characters. I reviewed `HEAD` (`7505b873...`) as the pinned commit and
diffed `9f2a0702bda6de929d42506f5aced2496669a2dc..HEAD`, consistent with this cycle's stated review
base. `feature.json`'s `review_sha` is stale/corrupt and should be repinned to the real `HEAD` before
signing — this is a data-integrity defect in the pin record, not a code defect.

## Item 1 — per-script case counts (all exit 0, all real counts)

| script | exit | case-count evidence (self-reported) |
|---|---|---|
| `test-validate-digest.py` | 0 | 69/69 CLI + 1/1 empty-red + 19/19 hook + 24/24 T-09 + 2/2 template + 18/18 reviewer-enum → `ALL PASSED.` |
| `test-check-domain.py` | 0 | 12/12 + 27/27 T-12 + 20/20 fleet + 10/10 `--resolve` + 30/30 post-mode + 16/16 worktree-boundary + 38/38 grant-parity + 8/8 deep-layout + 28/28 T-14 + **10/10 FEAT-50 artifact-integrity** |
| `test-bash-write-guard.py` | 0 | 42/42 + 7/7 T-14 + 29/29 worktree-boundary + 3/3 deep-layout Bash + 20/20 HEAD-move/forced-removal + **6/6 FEAT-50 Bash binding** |
| `test-harness-boundary.py` | 0 | 17 `PASS` lines, ends `ALL PASS` |
| `test-inflight-registry.py` | 0 | `PASS - 111/111 checks passed` |
| `test-run-unit-tests-kinds.py` | 0 | `23 of 23 cases passed` |
| `test-check-state.py` | 0 | 154 `ok -` lines, 0 `FAIL` lines (no self-reported total; counted directly from output) |

No script exits 0 while discovering zero cases — every one ran a real, non-trivial suite.

## Item 2 — test-matrix gate

Every task in `plan.yaml` is `change_type: bugfix` (10 tasks) or `docs` (2, T-06/T-07 for
`DECISIONS.md`/`DECISIONS-INDEX.md`). Per `.harness/harness.json`'s `test_matrix`: `bugfix.always =
[unit]`; `bugfix.when` names a `__bug_class__` kind gated on `match_bug_class`, which this project's
config never resolves to a concrete kind (no `_matrix_provenance` entry for `bugfix`, and no
project-specific bug-class kind exists in `test_kinds`) — treated as not-applicable, floor is `unit`
only. `docs.always = []`.

Both required buckets are exercised, using `run-unit-tests.sh`'s own `UNIT_SCRIPTS`/
`INTEGRATION_SCRIPTS` binding (verified by grep, not inferred):
- **unit**: `test-harness-boundary.py` (binds `harness_boundary.py`, a changed file) — ran, `ALL
  PASS`.
- **integration**: `test-check-domain.py`, `test-bash-write-guard.py`, `test-validate-digest.py`,
  `test-inflight-registry.py`, `test-run-unit-tests-kinds.py`, `test-check-state.py` — all changed
  or change-adjacent files, all ran green.

`matrix_ok: true`. (Full multi-kind `run-unit-tests.sh` was NOT run, per the dispatch's stated
non-goal; the targeted scripts above are the binding evidence.)

## Item 3 — the five red/mutant cases: each genuinely constructs and diverges

All five are present at HEAD, wired into their file's `main()`/runner path (not dead code), and were
observed `ok` in the live runs above.

- **`empty-red`** (`test-validate-digest.py:2923-2985`) — builds a mutant `validate-digest.py` that
  reverts the presence-vs-truthiness branch to `text = d.get(...) or ""`, fires both real and mutant
  over a whitespace-only `last_assistant_message`, asserts `real==2, mutant==0`. Genuine.
- **`feature-checkout-red`** (`test-check-domain.py:2758-2771`) — deletes the
  `feature_checkout_guard(_verdict["rel"], target)` call from a copied `check-domain.sh`, asserts
  `refused==2` (real) vs `muted==0` (mutant), no traceback. Genuine.
- **`digest-clobber-red`** (`test-check-domain.py:2832-2842`) — deletes the whole issue-#1058 guard
  block between its comment anchor and the next `RE_FEATURE_JSON` check, asserts `clobber==2` (real)
  vs `muted==0` (mutant). Genuine.
- **`bash-feature-checkout-red`** (`test-bash-write-guard.py:891-917`) — requires
  `source.count("            feature_checkout_guard(rel, ap)\n") == 2` (both the feature-scoped and
  the (post-fix) shared-outcome call sites) before building the mutant, then deletes both call sites
  and asserts `main==2` (real) vs `muted==0` (mutant). Genuine, and the count-2 precondition is
  itself proof the shared-outcome call now exists.
- **`dec156-worktree-red`** (`test-validate-digest.py:2988-3033`) — reverts
  `check_artifact_file`'s worktree-aware candidate join back to the plain owner-root join, fires both
  over a worktree-resident narrative digest, asserts `real==2, mutant==0`. Genuine.

None of the five is a vacuous/self-comparing assertion; each mutates real source text taken from the
file under test and asserts an observed exit-code divergence.

## Item 4 — case-name diff, `dca2d3d..HEAD`, changed test files only

Only two test files changed between `dca2d3d` and `HEAD`:
`test-bash-write-guard.py` (+156/-…) and `test-check-domain.py` (+279/-…) — both are pure
extract-to-helper-function refactors of the FEAT-50 blocks plus the two source fixes. I staged full
copies of `.claude/skills/harness/bin/` at both `dca2d3d` and `HEAD` in disposable tmp dirs (not the
worktree) and ran each test file against its own-commit source, extracting the full `ok`/`FAIL`
case-name set from each run:

- `test-bash-write-guard.py`: 106 names at `dca2d3d` → 107 at `HEAD`. **0 lost**, **1 added**:
  `bash-feature-checkout-shared` (the new finding-1 regression).
- `test-check-domain.py`: 119 names at `dca2d3d` → 119 at `HEAD`. **0 lost, 0 added** — a pure
  refactor plus a source-only fix (finding 3), with no test surface change.

**No case name present at `dca2d3d` is absent at `HEAD`.**

## Finding closure, verified directly against source (not inferred from the suite alone)

1. **[HIGH, security] shared-outcome checkout binding** — CLOSED. `bash-write-guard.sh:785` now
   calls `feature_checkout_guard(rel, ap)` inside the `outcome == "shared"` branch (verified by
   direct `git diff dca2d3d..HEAD -- bash-write-guard.sh`: the sole change is this one added line).
   `grep -n feature_checkout_guard bash-write-guard.sh` shows exactly two call sites (781 feature-
   scoped, 785 shared), matching what `bash-feature-checkout-red`'s precondition requires.
2. **[HIGH, code quality] `code_grade` FAIL on two aggregators** — CLOSED. Ran
   `code-grade.py --json` directly (bar is 3): `run_feat50_checkout_binding`
   (`test-bash-write-guard.py:932`) now grades **4, PASS** (cyc 1, ABC 16.1, was grade 1: cyc 11 /
   cog 9 / ABC 59.6); `run_feat50_artifact_integrity` (`test-check-domain.py:2857`) now grades **4,
   PASS** (cyc 1, ABC 20.0, was grade 1: cyc 17 / cog 14 / ABC 85.8). Both fixed by extracting the
   FEAT-50 blocks into named helper functions (`_feat50_*`), confirmed in the diff.
3. **[MED, security] digest-clobber OSError-as-absent** — CLOSED.
   `check-domain.sh:1140-1158` (`git diff dca2d3d..HEAD`): `prior` now starts `None`; a bare
   `FileNotFoundError` still sets `prior = ""` (creating a file is still allowed) but any other
   `OSError` leaves `prior is None`, which now emits an explicit `_head(...)` denial ("run digest
   already exists but cannot be read safely; refusing a Write...") instead of silently permitting
   the clobber. `digest-unreadable` (`test-check-domain.py`) exercises exactly this path and passed.

## New issues from the fix itself

None found. The diff between `dca2d3d` and `HEAD` is exactly: the two source one-liner/multi-line
fixes above, plus a behavior-preserving refactor of the two FEAT-50 test aggregators (confirmed via
the 0-lost/0-added case-name diff and the unchanged pass counts for every pre-existing case). SC-14's
decision-record check (`gen-decisions-index.py --stdout | diff - DECISIONS-INDEX.md` empty; `grep -c
"^## DEC-208 heading text"` returns exactly `1`) also passes.

## Coverage gaps

None beyond what the BRIEF itself already discloses (REQ-04 Write-route-only, REQ-03's sibling-
worktree exclusion, SC-11 external-blocker). The `feature.json` `review_sha` mismatch above is new
and should be corrected before signing.
