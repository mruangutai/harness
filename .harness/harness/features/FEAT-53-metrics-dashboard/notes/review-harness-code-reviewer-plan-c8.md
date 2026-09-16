# FEAT-53 plan review — code reviewer — cycle 8

## Verdict

FAIL. Stage 1 does not pass, so no implementation-code quality review was performed. The amended bundle still contains mutually exclusive build instructions and one ready task that would overwrite the operator-accepted immutable prototype.

## Common-bundle inspection record

Inspected the exact required common bundle: `BRIEF.md`, `plan.yaml`, `DESIGN.md`; prototype `README.md`, `observed-1440.png`, `observed-1920.png`, `package.json`, `.gitignore`, `vite.config.js`, `index.html`, `package-lock.json`, `.smoke/smoke.js`, `dist/index.html`, `dist/assets/index-LDjg9Bo3.js`, `dist/assets/index-_XzjF1xX.css`, `src/smoke.jsx`, `src/layout.css`, `src/ui.jsx`, `src/router.jsx`, `src/theme.js`, `src/fixture.js`, and `src/main.jsx`. Also inspected the operator-intent note, especially Mission, Composition, Prototype review rulings, Out of scope, and inherited rulings. The accepted 1440 observation shows Repository KPIs before Work List; the 1920 image is explicitly retained as older geometry evidence by the prototype README, not treated as the selected composition.

## Stage 1 — spec compliance

### F1 — high — substance

**Summary:** T-05 remains ready to replace an operator-accepted immutable prototype and specifies the superseded 3x3/full-width-tile composition.

**Consequence:** When the plan executes, T-05 instructs a visual designer to replace prototype bytes the operator has frozen, and to produce a 3x3 grid with KPI 7 full-width. The accepted prototype and current DESIGN instead show the selected 4+3 desktop KPI layout. A faithful executor therefore either destroys approved evidence or violates the task; downstream T-13/T-28 then consume whichever contradictory artifact results.

**Evidence:** `plan.yaml:494-529` marks T-05 `ready`, says “Replace the committed, pre-contract prototype,” and mandates the 3x3/full-width third row. The operator note’s Prototype review rulings says the rebuilt prototype was accepted; the assignment makes all prototype bytes immutable. `src/layout.css:346-358` implements four tiles then three at desktop, and `src/ui.jsx:323-329` places Repository KPIs before Work List.

**Required correction:** Convert T-05 from executable replacement work into completed/accepted evidence (or otherwise remove it from the ready DAG) and make downstream tasks consume the immutable artifact without rewriting it. Remove the superseded 3x3/full-width directions wherever they remain in executable tasks.

### F2 — high — substance

**Summary:** T-14 and T-28 still give mutually exclusive landing composition and KPI-layout instructions.

**Consequence:** T-14 tells the frontend implementer to put the attention strip and needs-you rows before a fixed 3x3 KPI grid, with KPI 7 alone full-width; T-28 says Repository KPIs are first but grammatically also places the attention strip before them. Following T-14 produces a dashboard that fails the operator-selected and visually accepted Repository-KPIs-first 4+3 composition; following the accepted prototype violates T-14’s literal contract.

**Evidence:** `plan.yaml:1204-1232` contains the stale landing and tile-grid contract. `plan.yaml:1933-1942` says “header first, then ... attention strip, T-14’s Repository KPIs section first,” an internally impossible order. D-30 at `plan.yaml:293-296`, DESIGN keyboard evidence at `DESIGN.md:873-876`, and the accepted prototype `src/ui.jsx:323-329` put all KPI controls before the Status cards; `src/layout.css:346-358` defines 4+3 desktop columns.

**Required correction:** Make T-14 and T-28 state one order—header, Repository KPIs, then Work List with its Status cards—and one accepted 4+3 desktop KPI layout. Remove the stale standalone “needs-you rows” and 3x3/full-width-tile instructions.

### F3 — high — substance

**Summary:** SC-13/SC-20 and T-14 require persistent inline sourcing rules while DESIGN and the immutable prototype require one-click InfoDisclosure.

**Consequence:** A builder who follows the success criteria and T-14 must add inline copy that contradicts the accepted density ruling; a builder who follows DESIGN and the approved prototype cannot truthfully pass SC-13/SC-20. The bundle therefore has no single verifiable completion state.

**Evidence:** `BRIEF.md:306-308` requires the escaped-defect rule beside the number; `BRIEF.md:352-356` requires KPI 7’s rule as persistent inline text. `DESIGN.md:304-314` expressly requires InfoDisclosure and records the criteria conflict as unresolved; `DESIGN.md:903-906` nevertheless says no open questions. `plan.yaml:1230-1232` repeats the inline requirement. The prototype’s KPI tile/panel uses `InfoDisclosure` in `src/ui.jsx` and does not render persistent sourcing text beneath those figures.

**Required correction:** Resolve the bundle to the operator-selected InfoDisclosure behavior by amending SC-13/SC-20 and T-14 consistently (or obtain and record a contrary operator ruling). Do not leave DESIGN’s explicit conflict beside “Open questions: None.”

### F4 — high — substance

**Summary:** T-17 documents a retired `/work` route and its verification cannot distinguish that dead route from valid `/work/$id` links.

**Consequence:** The shipped operator documentation can direct users to `/work`, which the final three-route contract requires to be unregistered. T-17’s substring check for `/work` still passes when the document contains only `/work/$id`, so the verification does not guard the intended route statement either way.

**Evidence:** D-29 at `plan.yaml:287-290` and T-13 at `plan.yaml:1191-1203` require exactly `/`, `/kpi/$n`, and `/work/$id`, explicitly retiring `/work`. T-17 at `plan.yaml:1333-1387` says “Document /work as the fleet-wide operational route,” while its verify merely searches for the substring `/work`.

**Required correction:** Document the work list on `/` and detail route `/work/$id`; remove the standalone `/work` instruction and make verification assert the actual route wording/behavior rather than an ambiguous substring.

### F5 — med — substance

**Summary:** T-26 and T-31 may run concurrently while both edit and verify the same collector and test file.

**Consequence:** Both ready backend tasks modify `dashboard/work.py` and `test-work-dashboard.py`, but neither depends on the other. Parallel execution can conflict or let the later task invalidate the earlier task’s focused verification before T-27 consumes both results.

**Evidence:** `plan.yaml:1886-1903` and `plan.yaml:2016-2045` name the same files; T-26 depends on T-23/T-24, while T-31 depends on T-23/T-30. T-27 waits for both, but that does not serialize their writes.

**Required correction:** Serialize T-26 and T-31, or combine their same-module collector work, and ensure the successor reruns the affected collector cases.

## Stage 2 — code quality

Not reached because Stage 1 failed. This is a plan review; `code_grade: n_a`. No implementation code, build, formatter, linter, test, or validation command was reviewed or run.

## Plausible concerns assessed and dismissed

- **Mission proportionality:** dismissed. The operator explicitly confirmed a plan mission for the new public collector/API/UI/schema surface; no downgrade is recommended.
- **Three-route model, disk-only boundary, tokens, and cost:** dismissed. T-13/T-28 preserve exactly `/`, `/kpi/$n`, `/work/$id`; T-27/T-28 retain disk-derived work data, run-end/null-aware tokens, and no dollar cost. T-17’s stale documentation instruction is the isolated route violation reported above.
- **SC trace coverage:** dismissed. SC-21 through SC-29 have task traces across T-23–T-31, and the earlier KPI criteria remain connected through their REQ-bearing tasks. No orphan success criterion was found.
- **DAG cycles and final integration:** dismissed. No dependency cycle was found, and T-27 appropriately waits for T-23–T-26 and T-31. The same-file T-26/T-31 race is separately reported.
- **Deep-module seams:** dismissed. The plan extends the existing collector, Flask server, shared API module, and React shell rather than introducing a second stack; the attention derivation remains a pure layer.
- **Prototype 1920 image differing from the current 1440 composition:** dismissed as a finding. The prototype README identifies it as earlier geometry evidence; current source and the accepted 1440 observation carry the final selection.

## Inspection criteria

No `verify: inspection` success criterion can be certified while the sourcing-rule and composition contracts remain contradictory. In particular SC-20 cannot simultaneously satisfy `BRIEF.md:352-356` and `DESIGN.md:304-314`.
