# Architecture/plan re-review — BUG-1081 code-grade enforcement (revision 2)

Scope: re-read of `BRIEF.md`/`plan.yaml` after Main applied fixes for the findings in
`review-harness-code-reviewer-planreview.md`. This supersedes that artifact's verdict; the original
is left unmodified as the record of what the first draft looked like.

## Verdict

**PASS.** severity_max: low. All three substantive findings from the first pass are resolved. One
low-severity residual worth pinning explicitly before/during T-02 execution; not blocking.

## Findings resolved

- **F1 (was high) — dead verify commands.** T-03's verify is now a self-contained inline check
  (asserts `validate-digest.py`, `code_grade`, `n_a`, `grade_2` are present in
  `harness-code-review/SKILL.md`) — no more reference to the DEC-188-deleted `check-docs.sh`. T-04's
  verify now uses `gen-decisions-index.py`'s own documented mechanism (write in place, then
  `--stdout | diff` against the committed index) — no more nonexistent `--check` flag.
- **F2 (was med) — deletion-only Python file vs. `n_a`.** D-04 now states explicitly: "`n_a` is
  reserved for a canonical range with no changed Python path. A deletion-only Python range is
  `pass`, because a Python path changed but no head-side function exists to gate." T-02's fixture
  list now names "deletion-only pass" explicitly, closing the ambiguity between the two "did Python
  change" mechanisms the first draft left unpinned.
- **F3 (was med) — ambiguous checkout root for the classification seam / `test_kinds` lookup.**
  Resolved, and strengthened past what was asked. T-02 now states explicitly: "Resolve the
  repository root from the feature directory selected by the existing artifact/registry binding, not
  from validate-digest.py's installed location or ambient cwd, and pass that root to `gated_set()`."
  T-01 goes further and removes the filesystem read from the seam's interface entirely — "the seam
  receives the parsed active `test_kinds` policy explicitly; it never discovers configuration from
  ambient cwd" — a cleaner fix (dependency injection at the seam boundary) than the one recommended.
- **F4 (was low) — self-grading qualname list.** Not named explicitly, but implicitly addressed: T-01
  now assigns bar/precedence assertions to `test-code-grade.py` and CLI-behavior assertions to
  `test-code-grade-cli.py` by rule ("Put direct bar and precedence assertions in
  test-code-grade.py... preserve the CLI's text, JSON, severity, exit-status, and sorting behavior in
  test-code-grade-cli.py"), which is the same separation that makes the original narrow qualname
  check's function-relocation risk moot. CR-01's whole-file self-grading sweep (`test-code-grade.py`)
  remains the backstop either way.
- **F5 (was low, cosmetic) — DEC-207 double-guard clarity.** Not addressed, and not re-raised: the
  existing `_pending_plan_review_error` rejection already holds regardless, so this remains a
  clarity-only note, not a finding.

## One residual (low, non-blocking)

T-01's "both the CLI and validator load the configuration they already own and pass that policy in"
does not say *where* the validator's `test_kinds` load comes from. Two readings are both consistent
with the sentence as written:
1. Re-derive `test_kinds` from the same feature-directory-derived root T-02 already names for
   `review_sha`/`gated_set()` — closes F3 completely.
2. Reuse the existing `review_config_path()`/`load_policy()` path — still installed-location-based
   (`harness_boundary.resolve_root`) — which would reopen F3 for the `test_kinds` config specifically,
   even though the git-range computation itself is now correctly scoped to the feature's checkout.

**Recommendation:** add one clause to T-02's intent naming that `test_kinds` is read from the same
feature-directory-derived root as `review_sha`, not from `review_config_path()`. Not blocking — the
plan's own explicit root instruction for `gated_set()` makes reading (1) the far more likely
implementation, and this is exactly the kind of thing code review (stage 2, this same persona) can
catch on the actual diff if it goes the other way.

## No new issues found

The expanded D-05/SC-11 scope (fail-closed default-branch/merge-base/degenerate-range handling now
applies to every graded value, not only `n_a`), the added mutation-proof requirements in T-01/T-02,
and the enlarged fixture list introduce no new correctness or scope-creep concerns on inspection —
each traces to REQ-01..REQ-06 or the two peer reviewers' own findings (mutation evidence, `--hook`
exit-code coverage for the primary bypass fixture, not only the crash fixture).
