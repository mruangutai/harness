# Answers — FEAT-53 resume after FEAT-1821 (operator, 2026-09-22)

## Ruling: resume; the FEAT-1821 lane is FEAT-53's acceptance signal.
FEAT-1821 merged into feat/FEAT-53 at bdd9afae. The record `runs/FEAT-1821-initial-red/ui/` (22 RED / 1 green at bundle e94bc953, 41 WebPs, 8 traces) is the baseline FEAT-53 must turn green: C1-HEADER-GEOMETRY, KPI-R1, DIR-KPI-IDENTITY, DIR-STATUS-LABEL, C3-KEYBOARD, C3-CONTRAST, C4-HATCH, TBL-DESKTOP, A11Y-AXE at both projects, plus the four inspection setups (VIS-DENSITY, VIS-PROTOTYPE) that currently cannot complete. These are the defects the operator saw by eye on 2026-09-17 (UAT round 2) — now machine-named.

## Plan amendment (pm applies; approval resets; Main re-signs)
- T-32 (frontend-dev): make the committed client bundle satisfy every automated Checks row. Files: client/src/**, client/dist/**. verify: `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=<run> npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui` exits 0 AND `ui_contract.py gate` reports PASS with the bundle committed under runs/<run>/ui/. Work is driven by the failing predicates and the trace filmstrips, spec by spec: geometry → colour placement → contrast/hatch → tables/axe → keyboard. No assertion, predicate, Checks row or DESIGN text may be weakened; if a predicate is wrong, that is a DESIGN amendment routed to visual-designer, never a spec edit by frontend-dev.
- Amend SC-26/SC-27/SC-28 (the UI SCs whose verify is `uat`) to add `evidence: ui` — automated by the lane — with UAT retained as the final operator gate. SC-02 (setup from clean checkout) stays uat.
- Validate must include the ui kind: qa runs the lane and the gate; ui-reviewer grades the new bundle and opens all 8 traces (Mode B, T-17 rule).

## Budget
Cycles 45 → 50 (5 for this lane; FEAT-53 has consumed 40 across 43+ runs and this is a fix-to-green pass with a deterministic oracle). Rework for the fix loop after T-32: 3 rounds / 135 min added to the standing ruling. Cap for T-32 itself: 2 eng rounds; if the lane is not green by then, return awaiting_user with the remaining red list — do not loop.

## Also on resume (orchestrator ledger)
Record the four unrecorded amendments INV-40 names (T-02, T-20, T-24, T-25) via record-amendments, re-pin review_sha to the tip before any reader, and repair the 2026-09-16-02-eng digest shape. The lane's scratch run dirs land under this feature's runs/; name them in returns for Main to remove (B-1, #1872).
