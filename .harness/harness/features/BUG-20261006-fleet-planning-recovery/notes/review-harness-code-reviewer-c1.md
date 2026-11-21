# FAIL — repository binding still leaks through reconciliation LABEL ownership

**T-01 has one high-severity SC-01 omission:** board reconciliation can label an unrelated Harness issue using a Kaya issue number as its ownership proof. This is a remaining consumer in the requested repository-binding cutover, not a request to reopen another feature.

## Stage 1 — specification compliance

- **Substance / high / T-01 / SC-01, D-01.** At pinned `6451153169f469f5bd9d5f3f01bf89b82787b720`, `.claude/skills/harness/bin/board_lifecycle.py:865-866` supplies `_recorded_issue_numbers(root)` to owner-repository LABEL detection. That helper (`:932-949`) unions every feature's parent/source/task numbers without resolving its repository or checking provenance. Given a valid Kaya task #17 and an unrelated Harness #17 closed NOT_PLANNED without `abandoned`, owner-repository `reconcile --apply` selects Harness #17 as recorded (`:978-993`) and sends `issue edit 17 --repo mruangutai/harness --add-label abandoned` (`:1137-1142`). STATUS's migrated binding guard does not guard LABEL. **[INFERENCE: source-traced scenario, not executed.]** Required fix: make LABEL ownership repository/provenance-aware through the shared contract; invalid/unreadable mappings must not broaden mutation authority. Add a cross-repository number-collision regression and a same-repository positive control in the existing lifecycle integration suite.
- **SC-07 inspection passes:** exact-pin `DECISIONS.md:3673-3686` removes the FAIL floor while preserving bounds; `:7182-7214` distinguishes binding/replacement from compatible adoption; `:7929-7940` separates historical refusal from live acceptance. Its index entries DEC-157/191/220/221/237 and existing `references/ledger.md`, `github-mirror.md`, `build-phase.md` agree on these governing contracts. Later fleet/offline/era changes were not attributed to this feature.
- Reviewed BRIEF, D-01..D-04, original research, build receipt and T-01 budget amendment before attribution review. The amendment does not remove SC-01's board-reconciliation obligation. T-03..T-05 receipts and accepted `notes/uat.md` remain operational evidence; SC-08 was not rerun.

## Stage 2 — not cleared

Specification failure prevents an overall quality approval. The requested mechanical risk check ran over the canonical range: `merge-base(origin/main, pin) == pin`; `code-grade.py --base <pin> --head <pin>` reported `PASSING: 0`. Thus canonical `code_grade: n_a`, not a claim that the historical implementation has no complexity. Prior measured grade-2 reasons remain in `notes/build-verification-2026-10-18.md`.

Attribution ground truth: `4a05030d^..4a05030d` (#2177); feature behavior inspected with `git show <pin>:<path>`. No tracked source dirt or canonical-range human commits. No tests, builds, lint, formatter, remote calls or product/canonical-Kaya writes executed. Matrix and fail-first claims remain audited receipts, not new executions or a replacement QA verdict.

## Principles applied

- **Migrate Callers, Then Delete Legacy APIs:** traced the shared binding cutover beyond STATUS and found the still-unmigrated LABEL ownership consumer.

## Open questions

None. Main-session-direct T-01 owns the fix; QA should exercise the collision regression and positive control under the signed verification rulings.
