# FEAT-53 T-32 frontend cycle 3 receipt

## Final generation

- `npm --prefix .claude/skills/harness/bin/dashboard/client run build && HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=2026-09-22-t32-round2-eng npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui`
  - build passed; lane result: **7 passed, 16 failed**.
- Independent command: `python3 .claude/skills/harness/bin/ui_contract.py gate ...`
  - **UI GATE: FAIL**.
- The required pre-clear of the final `ui/` directory was attempted but blocked by the harness write guard because the generated run path is outside the agent's registered write domain. The lane still generated/updated `results.json` and 29 nonempty WebP files.

## Proven predicate blockers

1. **DIR-KPI-IDENTITY**: predicate excludes only `[data-kpi-identity-mark=N]`, then flags every required descendant identity mark (dot, accent, sparkline, end dot, Shape B marks, column dot). This contradicts DESIGN’s required placement list.
2. **DIR-STATUS-LABEL**: DESIGN pins both `kpi-4` and `status-over-budget` to `#F58BC2`; predicate forbids that computed colour on any selector other than one mutually exclusive target.

## Remaining reachable failures in the final inventory

- KPI-R1 unequal tile-link widths at both desktop widths despite a stretch/min-width correction attempt.
- TBL-DESKTOP and C3-KEYBOARD time out at 30 seconds.
- A11Y-AXE reports serious colour-contrast failures for neutral status counts and several required status-label tokens, then times out.
- VIS-DENSITY times out after its first screenshot; VIS-PROTOTYPE has strict `FEAT-53` link ambiguity and disclosure-focus failures.
- Final bundle contains **29 WebPs** and **0 trace ZIPs** (the traces directory is absent); gate therefore reports missing traces and incomplete visual evidence.

## Repaired and post-fix verified

- Imported `createRoot` and moved root token probing to rendered body: C3 contrast passed at both desktop widths.
- Corrected unavailable hatch: C4 hatch passed at both desktop widths.

## Principles applied

- **Attack the Premise** — proved the rendering/root-token cause rather than adding speculative theme overrides.
- **Experience First** — exercised actual overview/KPI/work routes and browser-rendered contrast/hatch treatment.
