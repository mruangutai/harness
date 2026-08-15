# Observations — harness-ui-reviewer — FEAT-10

- 2026-08-08: dispatch (harness-handoff skill text) named the artifact path as
  `notes/receipt-harness-ui-reviewer-seg3.md`, but `check-domain.sh`'s enforced grant for this role is
  `notes/review-harness-ui-reviewer-*.md` only — the `receipt-*` naming in harness-handoff's generic
  guidance is not this role's permitted pattern. Wrote to `review-harness-ui-reviewer-seg3.md` instead
  and the guard passed. Worth checking the enforced glob before trusting a dispatch-quoted filename
  when it doesn't match this role's own `review-*` convention.
