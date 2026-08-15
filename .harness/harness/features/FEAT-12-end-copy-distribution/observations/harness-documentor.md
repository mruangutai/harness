# Observations — harness-documentor — FEAT-12

- 2026-08-10 (T-14 c2): `gen-decisions-index.py` recomputes a row's `refs:` and `[tags]` from the
  decision's body text (`:221-229` refs, `:244-252` tags). Striking a block therefore silently drops
  refs and retags the row — DEC-113 lost `refs: DEC-112` and the `deploy`/`plan` tags because the only
  `DEC-1NN` mention and the deploy vocabulary sat in the deleted fixture/safety blocks. Expect it and
  report it as an effect, not a defect.
- 2026-08-10 (T-14 c2): a `verify:` clause can be green before any edit and stay green after — here
  `grep -q 'harness/teams'` matched a later rename record, never DEC-113. Two independent operator
  confirmations of that blindness preceded this cycle. When a criterion is about a section's body,
  the receipt's section map is the deliverable; the verify is necessary and not sufficient.
- 2026-08-10 (T-14 c2): rewrapping a long line moved the overflow to the next line twice before I
  measured. Run the `awk length` check *after* the last edit, not before it.
