# Answers — FEAT-1821 after the second spent ruling: re-shape T-03 — 2026-09-18

## Finding (Main, at 7ddb2448)
Three fix rounds (c1–c3) each rewrote one 301-line `feat-53.e2e.spec.ts` and it never grew: a single agent, one file, one round cannot carry twelve checks whose T-02 predicates run to ~22 KB, with C3-KEYBOARD alone naming ~15 transitions. The lane itself works — fixture, config, manifest consumption, reporter, all 22 inspection captures, SRC-TOKENS green, exact contrast counts. This is a task-shape defect, not a rework shortfall; a third rework ruling would repeat it.

## Ruling: amend the plan. T-03 is closed as partially delivered; its residual becomes six tasks executed IN PARALLEL, one spec file each, under `client/e2e/`:
- T-08 `geometry.e2e.spec.ts` — C1-HEADER-GEOMETRY, KPI-R1
- T-09 `colour-placement.e2e.spec.ts` — DIR-KPI-IDENTITY, DIR-STATUS-LABEL
- T-10 `keyboard.e2e.spec.ts` — C3-KEYBOARD (alone)
- T-11 `contrast-hatch.e2e.spec.ts` — C3-CONTRAST, C4-HATCH
- T-12 `tables-a11y.e2e.spec.ts` — TBL-DESKTOP, A11Y-AXE
- T-13 reporter fail-closed probes (F4): for each of the seven cases (missing record, duplicate, mismatched title, empty WebP, parser error, reporter error, incomplete accounting) a two-stage proof — ui-reporter.ts emits a failing summary AND `ui_contract.py gate` refuses the bundle.
Rules for T-08..T-12: exact titles from the Checks table (unchanged); every clause in the T-02 predicate text is its own named `test.step`; no early abort (soft expects) so every clause reports; SRC-TOKENS, VIS-DENSITY and VIS-PROTOTYPE stay in the existing spec, which is trimmed to those three. `--list` must still total exactly 23. FEAT-53 production code untouched (SC-03).
Dispatch: one eng run, six frontend-dev/backend-dev members in parallel (T-13 may be backend-dev), then SIMPLIFY, pin, one validate. The rework ruling for the fix loop that follows is a fresh 2 rounds / 90 minutes (rounds=7, minutes=315 cumulative). Cycle ceiling unchanged at 10; if validate fails after those rounds, return awaiting_user.
