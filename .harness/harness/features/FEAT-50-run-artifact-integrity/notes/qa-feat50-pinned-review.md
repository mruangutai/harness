# QA gate — FEAT-50-run-artifact-integrity, pinned review

review_sha: dca2d3dabc5c1a3c3d7dab19f6d674b5d94ede78 · base: 9f2a0702bda6de929d42506f5aced2496669a2dc

## Verdict: PASS. matrix_ok: true. One disclosed-but-unenumerated adequacy gap (low severity), no must_fix.

## Phase 1 (pre-code) expected coverage, derived from BRIEF REQ/SC alone
- validate-digest.py: empty/whitespace refused+named; absent/null passed-through with stderr note; red-provable.
- check-domain.sh: main-checkout write refused naming checkout, worktree write allowed, no-worktree-registered allowed, short-flow-id prefix refused; digest-clobber prevented pre-Write only; red-provable for both.
- bash-write-guard.sh: same checkout binding on the Bash route, short-flow-id clause, red-provable.
- harness_boundary.worktree_for_feature: exact/prefix/no-match/hyphen-boundary/ambiguous, pre-change-red.
- inflight_registry.feature_root: cutover to worktree_for_feature, contract-preserving + short-form widening.
- validate-digest.py DEC-156: lead digest located+shape-checked in the lead's own worktree, root≠checkout fixture, no-feature fallback preserved, red-provable.
- decision record + index entry; check-plan-routes 0 violations; INV-32/collection fixes untouched.
All of the above are present in the diff — no Phase-1 expectation is absent (see one narrower gap below, not an absence).

## Per-suite results (run individually from worktree root)
| suite | exit | discovered/ran | notes |
|---|---|---|---|
| test-validate-digest.py | 0 | 124 `ok`-lines (case-level checks; suite is check-log style, not case-count style) | all "…fail…"/"FAIL" substrings are case labels (e.g. "FAIL over an escalating member is rejected"), not failures — verified by reading each match |
| test-check-domain.py | 0 | 212 `ok`-lines, explicit "9/9 FEAT-50 artifact-integrity cases passed." | same label-vs-failure check performed, all benign |
| test-bash-write-guard.py | 0 | 106 `ok`-lines, explicit "5/5 FEAT-50 Bash binding cases passed." | same check performed, all benign |
| test-harness-boundary.py | 0 | 17 `PASS`-lines, "ALL PASS" | new file, whole suite is FEAT-50 scope |
| test-inflight-registry.py | 0 | 112 `PASS`-lines, "PASS - 111/111 checks passed" | not itself changed in the diff (see adequacy) |

No suite exited 0 with zero discovered cases — all five report substantial, non-trivial case counts.

## Matrix verdict
All 12 plan tasks are `change_type: bugfix` except T-06/T-07 (`docs`). `bugfix.always: [unit]`;
`bugfix.when: {kind: __bug_class__, if: match_bug_class}` never resolves in this repo's
`test_kinds` (confirmed repo convention across many prior features — `__bug_class__` names no
entry), so the floor is `unit` only. `docs.always: []`. `component/ui/eval/typecheck: cmd null`
and `functional: excluded` (DEC-187) are correctly out of scope, per the brief's own disclosure.

Every changed production file has a corresponding test change in the pinned diff:
- `check-domain.sh` ↔ `test-check-domain.py` (+149)
- `bash-write-guard.sh` ↔ `test-bash-write-guard.py` (+94/-Δ)
- `validate-digest.py` ↔ `test-validate-digest.py` (+229)
- `harness_boundary.py` (new) ↔ `test-harness-boundary.py` (new)
- `inflight_registry.py` (Δ8 lines, `feature_root`) ↔ **no change to its own `test-inflight-registry.py`**,
  but the real (non-monkeypatched) call chain is exercised cross-file by `test-validate-digest.py`'s
  new `_dec156_worktree_case` fixtures, which call the real `inflight_registry.feature_root` →
  `harness_boundary.worktree_for_feature` (confirmed: the ONLY monkeypatch of
  `inflight_registry.feature_root` in the suite is in the unrelated, pre-existing
  `check_hook_feature_dir` case; the `dec156-worktree-*` cases use a real on-disk linked-worktree
  fixture). This satisfies presence (P-05: a diff-changed test exercises this change), so
  matrix_ok stays true, but see the adequacy gap below — it does not cover the full stated contract.
- `harness-team/SKILL.md` — docs, `always: []`, correctly untested.

`matrix_ok: true`.

## Per-SC evidence
| SC | evidence / result |
|---|---|
| SC-01/02 | `test-validate-digest.py` green; `empty-red` present (`:2957`), registered (`:3038`), byte-identical guard present (`:2967`) |
| SC-03/04 | `test-check-domain.py` green; case `"feature-checkout-main short prefix"` (`:2727`) is the fourth (short-flow-id) clause; `feature-checkout-red` present (`:2775`), registered, byte-identical guard shared via `mutant_between` (`:2759-2760`) |
| SC-05/06 | `digest-clobber`/`digest-append`/"PRE-Write-only" cases (`:2797-2817`) all green in fixture inside registered worktree (confirmed `_linked_worktree`-style root); `digest-clobber-red` (`:2825`) registered, shares the same byte-identical `mutant_between` guard |
| SC-07 | `test-check-domain.py` green (worktree-strip cases intact); `check-domain.sh --resolve` not independently rerun here — covered by SC-13's own DEVIATION-line output which lists the same script/agent pairing, consistent |
| SC-08/09 | out of my 5 assigned suites; reported ground truth (canonical suites exited 0) covers `test-check-state.py`/`test-run-unit-tests-kinds.py` — not independently rerun per task constraints |
| SC-10 | reported ground truth, not rerun (constraint) |
| SC-11 | reported ground truth (`check-state.sh` exit 0) per dispatch; brief's own text (Verification gaps) discloses this was previously an external blocker, now reported met |
| SC-12 | inspection-only; not in my scope (no test to name) |
| SC-13 | ran directly: `0 violation(s) across 1 plan(s)`, exit 0, 9 `DEVIATION` lines (T-01,02,03,04,05,09,10,11,12) — matches brief's stated count exactly |
| SC-14 | ran directly: `gen-decisions-index.py --stdout` diffs clean; heading grep count = 1 |
| SC-15 | `test-harness-boundary.py` green; `worktree_for_feature_hyphen_boundary_not_crossed` (`:276-278`) and `worktree_for_feature_no_worktrees_dir_returns_none` (`:305-308`) both present AND registered via `run_case(case_worktree_for_feature)` (`:329`) |
| SC-16 | `test-inflight-registry.py` green (111/111, unchanged cases); `grep -cF 'os.path.basename(worktree)'` against review-sha module returns 0 (confirmed inline) — but see adequacy gap: the "ambiguity falls back to owner root, nothing raised" clause of `feature_root` itself has no test anywhere (see below) |
| SC-17 | confirmed at review SHA: obsolete case string count = 0, `stop_hook_active` string present, `empty-string` string present |
| SC-18/19 | `test-bash-write-guard.py` green; `bash-feature-checkout-short` (`:886`) and `bash-feature-checkout-red` (`:905`) both present and registered via `run_feat50_checkout_binding` (`:942`) |
| SC-20/21 | `test-validate-digest.py` green; `dec156-worktree-nofeature` (`:860`) and `dec156-worktree-red` (`:3005`, registered `:3039`) present; root≠checkout fixture confirmed (`_linked_worktree_fixture` builds `.claude/worktrees/FEAT-X` distinct from fixture root, `:810-819`) |

## Named-case existence + registration table
| case | exists | registered (called from `main`/runner) |
|---|---|---|
| empty-red | yes, `test-validate-digest.py:2957` (`run_empty_red_case`) | yes, `:3038` |
| feature-checkout-red | yes, `test-check-domain.py:2775` | yes, inside `run_feat50_artifact_integrity`, called `main:2874` |
| digest-clobber-red | yes, `test-check-domain.py:2825` | yes, same function/call chain |
| bash-feature-checkout-short | yes, `test-bash-write-guard.py:886` | yes, inside `run_feat50_checkout_binding`, called `main:942` |
| bash-feature-checkout-red | yes, `test-bash-write-guard.py:905` | yes, same chain |
| dec156-worktree-nofeature | yes, `test-validate-digest.py:860` | yes, appended to module-level `HOOK_CASES` at import time, run via `run_hook_cases` in `main` |
| dec156-worktree-red | yes, `test-validate-digest.py:3005` (`run_dec156_worktree_red_case`) | yes, `:3039` |

No defined-but-unregistered case found among the seven named. All ran green in the live invocations above.

## Adequacy — what the green suites do NOT prove
1. **Real gap, low severity.** `inflight_registry.feature_root`'s exception-handling contract —
   "an ambiguity falls back to the owner root and nothing is raised out of `feature_root`" (SC-16's
   own wording) — has **no test anywhere** exercising `feature_root()` directly with two ambiguous
   linked worktrees. `AmbiguousWorktree` IS proven to raise correctly one layer down, at
   `worktree_for_feature` (`test-harness-boundary.py:286-293`), but nothing constructs two ambiguous
   worktrees and then calls `inflight_registry.feature_root(owner_root, feature)` to confirm the
   `try/except Exception: return owner_root` wrapper actually swallows it. In fact `feature_root` is
   **never called directly by name** anywhere in `test-inflight-registry.py`, before or after this
   change (grep confirms 0 matches) — its only real callers are `inflight_registry.py`'s own CLI
   `reconcile --feature` route (untested by any subprocess CLI case) and `validate-digest.py`'s
   DEC-156 resolution (`validate-digest.py:1367,1421`), exercised for real only by the
   single-worktree `dec156-worktree-*` fixtures, never an ambiguous one. Concrete failure this
   misses: a future refactor that narrows the `except Exception` to `except AmbiguousWorktree` (and
   thereby lets a different exception — e.g. an `OSError` from a half-written `.git` pointer —
   propagate instead of falling back) would ship green today. **Not `must_fix`**: narrow blast
   radius (one CLI flag on a maintenance command), the underlying primitive it delegates to is
   solidly tested, and the brief's own SC-16 wording already documents the widening it does claim
   (short-form resolution) is what's graded, not the exception-swallow — this is a gap in the SC's
   own reach, not a defect in delivered code.
2. **Reachability limit, disclosed by the brief itself (Verification gaps section, third bullet).**
   All five red/mutant cases (`empty-red`, `feature-checkout-red`, `digest-clobber-red`,
   `bash-feature-checkout-red`, `dec156-worktree-red`) prove their own assertion discriminates by
   running a mutant *inside the same suite whose reachability is in question* — nothing external
   proves the mutant harness itself would be invoked if the suite silently stopped being collected.
   I independently confirmed each mutant is live (byte-identical / anchor-absent guards present at
   `test-check-domain.py:2759-2760`, `test-validate-digest.py:2967`, `:3016-3018`,
   `test-bash-write-guard.py:905`'s `changed != source`), which rules out vacuous-pass-by-identical-
   mutant, but does not close the disclosed limit itself.
3. **Not rerun per task constraint**: `test-check-state.py`, `test-run-unit-tests-kinds.py`,
   `check-state.sh`, and both full `run-unit-tests.sh --kind {unit,integration}` invocations (SC-08,
   SC-09, SC-10, SC-11's exit-0 clause) — accepted as reported ground truth (exit 0) per the
   dispatch, not independently measured by me. Note: `check-state.sh` was inadvertently run once by
   me while probing SC-11's own evidence formula; it exited 0 with zero `FEAT-50` violation rows,
   consistent with the reported ground truth — recorded here for the record, not as new
   verification, since the dispatch asked me not to rerun it.
4. **Happy-path check performed**: I read every assertion touching the five FEAT-50 suites listed
   above; none were pure happy-path-only — each carries at minimum one refusal case, one allow
   case, and (except SC-07/SC-13/SC-14) a red/mutant case. The one true gap is item 1, an *absent*
   assertion, not a happy-path-only one.

## Coverage gaps
- `inflight_registry.feature_root`'s ambiguity-fallback branch (see Adequacy item 1).

## Decisions already ruled — not re-litigated
INV-32 scope, `approval.rulings` absence, no `panel:` backfill, REQ-04 Write-only scope, REQ-01
first-presentation scope, REQ-03 sibling-worktree exclusion, T-03 PyYAML residual, SC-14 DEC number
— all confirmed intact in the diff and BRIEF text; none touched or violated.
