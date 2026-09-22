# Ruling — T-32 round 5: stop teaching to the test (operator, 2026-09-22)

## What Main found in the tree (client/src/work-view.tsx)
- `AccessibleSelector`: hides the real Astryx Selector trigger (`aria-hidden`, `tabIndex=-1`, `disabled`) and overlays a fake read-only `<input role="combobox">` so that `toHaveValue('needs-you')` can pass.
- A `sessionStorage('workStatusFocus')` hand-off plus inline `!important` outline overrides to defeat the focus ring after an attention-card click.
- The Kanban/Table control is a Button labelled "Kanban" whose `aria-pressed` means "Table".
These satisfy locators while degrading the real accessibility DESIGN asks for. They are rejected.

## Rulings
1. **Predicate defect → T-36 (harness-dev-ops, keyboard.e2e.spec.ts only).** DESIGN §680 says the Status filter's selected value is *announced*; `toHaveValue` is meaningless on a button-backed combobox (Astryx Selector is the DESIGN-mandated control). Replace that one assertion with: the focused `combobox` named Status has an accessible name/text that includes the selected option label ("Needs You"), and the polite live region contains the announcement. No other clause changes.
2. **Implementation must be honest.** Remove `AccessibleSelector`, the sessionStorage hand-off and every inline `!important` outline override. The real Astryx Selector trigger receives focus programmatically after an attention-card click; ring visibility follows `:focus-visible` (pointer-initiated focus shows no ring; keyboard focus shows the 2px token ring) in the stylesheet, not per-element inline styles. If Astryx's trigger cannot be focused programmatically, that is a finding to report with evidence, not a reason to fake a control.
3. **Layout switch.** One button, accessible name "Kanban / Table layout", `aria-pressed` true when Table is active, both segment labels visible (bebb5416 addendum 3 stands).
4. Round accounting: the BLOCKED return caused by the predicate defect does not consume round 5; round 5 resumes after T-36 with the honest implementation. Rounds remain capped at six.
5. The scratch `client/dom-focus-census.mjs` is not part of T-32 and must not be committed.
