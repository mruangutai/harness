# Main-session receipt — historical refused-return annotation, 2026-10-07

- Operator ruling (this session): backfill the refused marker so the pre-#2131 refused closure satisfies the INV-15 contract merged in #2131 (`37cfcfd4`).
- After merging origin/main (`2b1851f1`), `check-state.py --feature FEAT-2037-product-document-guidance` reported INV-15 on `runs/simplify-eng/digest.md`: the run had been closed with `close-run --refused-return` (STATE.md, Q-03) before `return_disposition` existed.
- Canonical route, no hand edit: `feature-record.py close-run --id simplify-eng --verdict BLOCKED --cycles-used 0 --refused-return`. The inverted digest stage confirmed that the digest does not validate. The entry kept `ended_at` 2026-10-05T05:24:50+00:00, tokens 46313 and cycles_used 0, and gained `return_disposition: refused`.
- `preflight-eng` was not flagged and was left unchanged.
- The board card read Done, which disagrees with the plan's `review` station (INV-26). Reconciled with `gh-sync.py status <feature-dir> review` (#2037, #2072, #2073 -> review).
- Post-state: `check-state.py --feature FEAT-2037-product-document-guidance` exit 0 (notes only).
