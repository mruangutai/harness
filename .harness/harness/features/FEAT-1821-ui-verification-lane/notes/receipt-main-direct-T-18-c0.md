# Receipt — T-18 (main-session-direct): FEAT-53 RED bundle rebuilt with replayable traces — 2026-09-19

Command: `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=FEAT-1821-initial-red npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui` at e94bc953 → nonzero (22 failed / 1 passed), as SC-03 requires on the unchanged FEAT-53 bundle.
Bundle: results.json, 41 WebPs, 8 traces (C3-KEYBOARD, TBL-DESKTOP, VIS-PROTOTYPE, A11Y-AXE × desktop-1440/1920; 144 KB–3.3 MB each). No FEAT-53 production or dist edit.
Independent gate: `ui_contract.py gate … --changed client/src/tiles.tsx` → FAIL with predicate and inspection-setup reasons only; 0 structural, 0 trace, 0 title reasons.
Replay verified by Main: C3-KEYBOARD--desktop-1440.zip carries 15 recorded actions (navigation, networkidle, "overview has seven KPI tile links", "overview has seven KPI InfoDisclosure triggers", Tab, "overview Tab order stop 1: activeElement / outline width / outline offset") and a 9-frame screencast. Open with `npx playwright show-trace .harness/harness/features/FEAT-53-metrics-dashboard/runs/FEAT-1821-initial-red/ui/traces/C3-KEYBOARD--desktop-1440.zip`.
