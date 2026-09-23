# Observations — harness-frontend-dev — FEAT-53

- 2026-09-16: A fixed configured scaleBand domain retained a zero-count grade as a rendered bar, while scaleUtc measured irregular-date gaps at the actual 1:60 ratio.
- 2026-09-16: Installing the DESIGN-pinned Neutral theme alongside the existing Astryx core pin requires npm peer resolution to retain test and StyleX peer packages; `--legacy-peer-deps` leaves the client unable to run its scoped verify.
- 2026-09-16: T-14 exact forbidden-path scan includes T-13 routes.test.tsx retired-route assertions, so it fails independently of T-14 source.
- 2026-09-16: Runtime-literal scans over TSX must exclude test modules when those tests intentionally preserve retired literals as negative-route assertions.
- 2026-09-17: Dashboard client dist resolves outside the FEAT-53 worktree; running the signed Vite build mutates it but the write guard prevents restoring its tracked baseline from this task worktree.
- 2026-09-17: Vitest 5's JSON reporter wrote only client/.vitest/json/output.json while the signed T-21 command expected JSON on stdout; report a configuration mismatch rather than substituting a grep.
- 2026-09-17: Vite must be launched with its client directory as cwd; npm --prefix exec started from the worktree returned 404 for the source root.
- 2026-09-17: Astryx Table enforces a 960px minimum width; the responsive dashboard must explicitly reset table min-width to avoid page-level overflow below 832px.
- 2026-09-17: A receipt that cites browser evidence must record the pre-fix SHA/artifact and the exact computed or geometry values; source CSS alone cannot discharge runtime findings.
- 2026-09-17: Explicit Astryx reset, core and neutral theme imports in main.tsx cause Vite to emit the committed CSS asset referenced by dist/index.html.
- 2026-09-22: Vite base "./" makes deep dashboard routes request relative assets that receive the SPA fallback HTML; root base preserves route asset loading.
- 2026-09-22: Astryx Selector renders a button-backed combobox while C3 applies input-only value assertion; an overlay input repaired role/value discovery but its status attention transition still did not update router state after three source-side fixes.
- 2026-09-22: Exact T-32 round-5 lane reached 21/23; both VIS-DENSITY projects exhausted the 30s test deadline after overview-default, so remaining captures attempted page.addStyleTag on a closed page. results.json references 29 existing WebPs and eight nonempty trace ZIPs, but each density record lacks six required labels.
- 2026-09-22: T-32 c5 disclosure source passed both focused VIS-DENSITY projects in 9.6s, but the one exact 23-test lane timed out at 30s on both VIS-DENSITY projects after five evidence captures; results retain 21 passed, 37 WebPs, and eight nonempty traces.
- 2026-09-22: Round-5 exact UI lane ran 21/23; both VIS-DENSITY initial-request-error captures hit the 210000ms test timeout before table-overflow, which closed the page and produced evidence-label mismatch errors in results.json.
