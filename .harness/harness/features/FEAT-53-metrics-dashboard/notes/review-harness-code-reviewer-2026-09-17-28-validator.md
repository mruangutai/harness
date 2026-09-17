# FEAT-53 U-01 fix — pinned code review

**PASS.** Review pin `ebce36e77769a64ac0e302692d8aa350dceca0e4`, base `daba2af5513a0316f57ed8729576acb0e582708b`; reviewed only `daba2af5513a0316f57ed8729576acb0e582708b..ebce36e77769a64ac0e302692d8aa350dceca0e4`, excluding later pin-only commit `a103cc48`.

## Stage 1 — spec compliance: PASS

The UAT ruling and amended T-13/T-14 are implemented without a source/test/dist mismatch. T-13's reset → core → neutral-theme imports are exactly ordered before `Theme` (`client/src/main.tsx:1-5`); pinned `dist/index.html:7-8` references `index-DnXu7ssi.js` and non-empty `index-BGeYwNXA.css`. The pinned assets are 901,892 and 188,908 bytes with SHA-256 `5bf1886b9b7f72d560a1f3f384098678902681c6a54d4304a0cea96db2ba40c6` and `7c69bb6816bed97825d53307cb6e92c6b8b477e090fbd4ebd746bf3f1dfda86e`; the CSS contains the reset/Astryx/theme output. T-14 uses one shared numeric summation mechanism at both tile and panel call sites (`client/src/panels.tsx:14-21,94`; `client/src/tiles.tsx:5,22`), retains numeric zero, ignores object/non-number members, and cannot stringify the breakdown as `[object Object]`. Throughput uses the exact `excluded_features` payload reason only when `measured_features === 0`; without that entry, numeric zero remains rendered (`client/src/tiles.tsx:15-17,27-28`), satisfying D-19.

The binding UAT ruling, engineering receipt, engineering digest, amended plan T-13/T-14, pinned source, focused tests, `dist/index.html`, generated JS/CSS names/content, and recorded scoped build/test evidence were examined. The engineering receipt records T-13 build/CSS inspection PASS and T-14 7 focused tests/22 assertions PASS; those commands were not rerun per dispatch. Pinned asset bytes match the checkout paths inspected, and the compiled JS contains both `measured_features`/`excluded_features` precedence and unattributed-total behavior; no source/dist mismatch was found.

## Stage 2 — code quality: PASS with one medium test-strength note

The implementation is direct and fail-closed for the ruled payloads. The KPI 6 tile and panel tests independently bind `26 of 40 commits unattributed` and reject `[object Object]` (`client/src/kpi-content.test.tsx:29-34`; `client/src/panels.test.tsx:86-91`). The Throughput test binds the exact unavailable reason and absence of a rendered zero (`client/src/kpi-content.test.tsx:36-42`). However, the focused tests do not exercise Throughput's complementary legitimate-zero case at `measured_features: 0` with no unavailable entry; the earlier “measured zero” test uses Throughput value 4 with two measured features (`client/src/kpi-content.test.tsx:6-27`).

**Finding (T-14, substance, med):** If a future edit at `client/src/tiles.tsx:15-17` fabricates an unavailable state solely because `measured_features` is zero, a browser user would see a legitimate measured zero as unavailable, while the current focused tests could remain green. Remedy: add a tile case with `median_cycle_time_days: 0`, `measured_features: 0`, and `unavailable: {}` that asserts the Throughput tile renders `0` and no unavailable treatment. Current shipped behavior is correct, so this is not `must_fix` in the single authorized validation cycle.

Mechanical Python grade over `merge-base(origin/main, ebce36e7)..ebce36e7`: PASS (400 passing records; no severity or reason-required records). Human commits in the pinned range: `29fdbdc1779c2aa46396dd343d6240de7c350800`, `e7805af1a70cbeb413fa819efd69524b0e71bfb7`.

`must_fix: []`
