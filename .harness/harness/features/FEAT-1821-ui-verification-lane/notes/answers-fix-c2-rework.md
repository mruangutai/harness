# Answers — FEAT-1821 T-03 after the spent rework ruling — 2026-09-18

## Operator-observed at 4326b6eb
Main ran the lane itself: `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard npm run test:ui` → 23 tests, 22 RED, 1 green (SRC-TOKENS). The reds are the divergences the operator found by eye in FEAT-53 (header geometry, 4+3 grid, identity hues, status labels, keyboard, contrast, hatch, tables, axe). All VIS-DENSITY / VIS-PROTOTYPE WebPs captured at both projects. The lane works; the open items are completeness, not function.

## Ruling: rework extended by 2 rounds / 90 minutes, scoped to T03-F1, T03-F2, T03-F4 only.
Total ruling becomes rounds=5, minutes=225. Nothing else may be opened in those rounds. F1: every clause of the seven objective predicates T-02 pinned, asserted individually (no representative subsets). F2: the full C3 graph clause by clause, with no early abort hiding downstream checks — use test.step or soft assertions so every clause reports. F4: producer-side fail-closed proof — a unit/integration probe per case (missing, duplicate, mismatched title, empty WebP, parser error, reporter error, incomplete accounting) showing ui-reporter.ts emits a failing summary and the T-01 gate refuses it. Pin review_sha BEFORE every reader dispatch.
