# Operator ruling after validate c1 FAIL — 2026-11-08

Asked: the signed rework budget (1 round / 45 min) was spent — c0 FAIL fixed, c1 FAIL
(med: oversized shipped issue string crashes INV-24; low: active Unicode-digit claim regressed by the
ASCII-only guard). Options offered: grant one more round (recommended), stop and park, or descope the
SC-03 edge to backlog.

## Ruling

Mike Ruangutai: **Grant 1 more round.** Rework budget raised to 2 rounds / 75 min. Planned fix:
`_inv24_issue_number` returns to `str.isdigit()` semantics and treats `int()`'s ValueError as
unusable (None), with regressions for an oversized shipped parent and an active "٣" collision.
