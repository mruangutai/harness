# T-02 — executable FEAT-53 Checks contract

## Conclusion

PASS. The executable Checks contract is published under `## Checks` in `.harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md`. It contains the 12 signed tuples, executable predicates including the complete C-3 keyboard transition contract, and 22 unique per-project inspection evidence rows. The same task command failed before the edit and emitted `harness-ui-manifest/1` with exit 0 after it.

## Plan cross-check

The approved `plan.yaml` entry is `T-02`, title `Publish the executable FEAT-53 Checks contract`, status `building`, file `.harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md`, dependency `[T-01]`, and traces `[SC-05, SC-09]`. Its intent and verify command match the dispatch verbatim. No T-03, production dashboard, or plan file was changed.

## Exact fail/pass evidence

Executed from the FEAT-1821 worktree before editing and once again after editing:

```sh
python3 .claude/skills/harness/bin/ui_contract.py check --design .harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md --require-predicates --require-inspection-evidence \
  --expect 'C1-HEADER-GEOMETRY|shared header geometry matches DESIGN|shared-header|automated-each-project|desktop-1440,desktop-1920' \
  --expect 'KPI-R1|overview KPI grid is 4 plus 3|overview-kpis|automated-each-project|desktop-1440,desktop-1920' \
  --expect 'DIR-KPI-IDENTITY|KPI identity hues stay on identity marks|all-routes|automated-each-project|desktop-1440,desktop-1920' \
  --expect 'DIR-STATUS-LABEL|status hue stays on attention labels|overview-attention|automated-each-project|desktop-1440,desktop-1920' \
  --expect 'C3-KEYBOARD|keyboard focus transitions and restoration match DESIGN|all-routes|automated-each-project|desktop-1440,desktop-1920' \
  --expect 'C3-CONTRAST|dark tokens meet DESIGN contrast floors|all-routes|automated-each-project|desktop-1440,desktop-1920' \
  --expect 'C4-HATCH|unavailable hatch uses 45 degree 1 pixel 6 pixel stops|all-routes|automated-each-project|desktop-1440,desktop-1920' \
  --expect 'TBL-DESKTOP|desktop tables contain overflow and keep ID sticky|work-and-kpi-tables|automated-each-project|desktop-1440,desktop-1920' \
  --expect 'SRC-TOKENS|component source uses only theme tokens|client-source|automated-once|desktop-1440' \
  --expect 'A11Y-AXE|routes pass axe and expose non-colour equivalents|all-routes|automated-each-project|desktop-1440,desktop-1920' \
  --expect 'VIS-DENSITY|dense hierarchy and qualitative states match DESIGN|all-routes|inspection-each-project|desktop-1440,desktop-1920' \
  --expect 'VIS-PROTOTYPE|rendered routes and interactions match approved prototype|all-routes|inspection-each-project|desktop-1440,desktop-1920'
```

- Pre-edit: exit 1; salient output: `REFUSED: .harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md: no \`## Checks\` section`.
- Post-edit: exit 0; salient output: normalized JSON with schema `harness-ui-manifest/1`, all 12 expected check IDs, `SRC-TOKENS` applicable only to `desktop-1440`, the other 11 checks applicable as signed, and all 22 inspection evidence objects.

No formatter, linter, build, project-wide test, broad validation, or T-03 command was run.

## Contract pointers

- Method meanings, mandatory screenshots, and the 12 predicates: FEAT-53 `DESIGN.md` → `## Checks`.
- Exact focus order, active-element transitions, pointer/keyboard outline distinctions, Back restoration, and InfoDisclosure restoration: `C3-KEYBOARD` in the Checks table.
- Seven `VIS-DENSITY` plus four `VIS-PROTOTYPE` entries for each desktop project: FEAT-53 `DESIGN.md` → `## Checks` → `### Inspection evidence`.
- Approved comparison source: FEAT-53 `DESIGN.md` → `## The prototype gate` and `.harness/harness/features/FEAT-53-metrics-dashboard/notes/prototypes/FEAT-53/`.

## Files touched

- `.harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md`
- `.harness/harness/features/FEAT-1821-ui-verification-lane/notes/prototypes/build-product-t02.md`

## Open questions

None.
