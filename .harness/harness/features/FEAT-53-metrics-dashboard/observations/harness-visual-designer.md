# Observations - harness-visual-designer

- 2026-09-01: FEAT-51 — computing WCAG ratios for my own proposed tokens (a 20-line python run) turned two contract claims from assertion into measurement, and the mutual contrast of two series colours (1.51:1 light, 1.21:1 dark) became the evidence for the "never hue alone" rule instead of a platitude. Cheap; do it every time a palette is proposed.
- 2026-09-01: FEAT-51 — my illustrative figure ("N of 122 ungraded") was arithmetically wrong on first write: I carried the .py count instead of the .sh+.ts sum. An illustration is still a number a reviewer will check; derive it, do not eyeball it.
- 2026-09-01: FEAT-53 prototype. My dispatch asserted `@astryxdesign/core: 0.5.2` in package.json was
  an INVENTED version and told me to replace it with `"*"`. `npm view @astryxdesign/core version`
  returns 0.5.2 — the package is real, latest is 0.5.2, and it installs. I kept the exact pin and
  reported the corrected premise instead of writing a README that claimed the version was
  unresolvable. Lesson: a dispatch premise of the form "X is fabricated" is a hypothesis; one
  registry call settles it, and writing the instructed falsehood would have poisoned the record.
- 2026-09-01: the same probe paid for itself twice — installing the package let me read its real
  export surface (105 components, defineTheme with [light,dark] tuples, a `Theme mode='system'`
  provider that IS the OS-preference default, and a `dataTokenDefaults` data-viz palette). Custom
  token names not in Astryx's CoreTokenName union survive defineTheme at runtime and emit as
  `light-dark(...)` CSS, which is what let the nine DESIGN tokens plus the type/radius/size scale
  live in the one defineTheme call instead of as raw values in components.
- 2026-09-01: T-05's `verify` command concatenates every file under the prototype dir via
  `rglob('*')` and `read_text()`. It raises UnicodeDecodeError once `npm install` or `vite build` has
  run, because node_modules/dist hold binary files. A verify command scoped to a directory that a
  build populates needs an ignore list or `errors='ignore'`. Raised as an open question.
- 2026-09-01: an SSR smoke harness (`vite build --ssr` + renderToString + string assertions) is a
  cheap, decisive substitute for a browser when verifying a gap-state contract: "S-1 mounts no
  <svg>" and "more polylines than series, so the line breaks" are both checkable in the HTML string,
  and neither is checkable by reading the source. It does NOT verify appearance, and I said so.
- 2026-09-01: rewording DESIGN.md C-1 tile 3 for D-21 (two-term aggregate becomes three-term) left the same claim standing in my own prototype fixture (`notes/prototypes/FEAT-53/src/fixture.js:198,206,214` — "per-feature mean · 1 of 2 features at zero") and in its tile unit label (line 261). A contract reword has restatements in the runnable prototype, not only in prose; grep the prototype for the old phrasing too.
- 2026-09-02: DESIGN.md grid literal is machine-coupled to BRIEF `## Verification gaps` (which cites the grid literal as a reason a bare-digit grep for the file-mix count cannot discriminate). Changing the landing grid is therefore never a design-only edit: report the exact literal to pm in the DIGEST or the BRIEF paragraph silently goes false.
- 2026-09-02: when a contract enumerates surfaces by count ("the six surfaces"), the count leaks into derived counts elsewhere — non-trend KPI count, trend-KPI id list, focus order, panel inventory, and a prototype-status paragraph asserting what the prototype covers. Grep the count word, then grep each derived count separately.
- 2026-09-02: FEAT-53 c5 — `check-domain` denies harness-visual-designer `features/<FEAT>/notes/research-*.md` even when the dispatch names it; permitted per-feature notes are only `notes/mockups/**` and `notes/prototypes/**`. Filed the DESIGN.md contract-edit record under `notes/mockups/` with a header explaining why.
- 2026-09-02: FEAT-53 — DESIGN.md's dead `react-charts` fallback (B-21) existed in exactly ONE place (C-2 opening paragraph); a whole-file case-insensitive sweep for `react[- ]?charts` found no second copy, unlike plan.yaml/BRIEF which each carried several. Sweeping first was still cheap and is what let me assert "every occurrence accounted for".
- 2026-09-04: FEAT-53 dashboard redesign. A prototype "verified without a browser" hid three faults that only a render shows: a measured-width SVG inside a CSS grid widened its track until the third column left the 1440 viewport (grid items default min-width:auto — set minWidth:0 on every grid child); a 45° hatch used as a *background* under its own reason text made every S-4 sentence unreadable (hatch the glyph badge only, keep the sentence on the card); a y-axis title collided with the top gridline label. None was visible in SSR HTML or in any assertion.
- 2026-09-04: TanStack Router silently matches NOTHING when validateSearch returns a type the URL parse disagrees with — `?sort=1` parses to the number 1, a validateSearch returning '1' sends it into a normalising rewrite that never settles, and `router.state.matches` comes back empty with status undefined. matchRoutes() still matched, which is what made it look like a render bug rather than a search-param bug.
- 2026-09-04: headless Chrome + CDP over node's global WebSocket (node >=22) is enough to look at a local SPA: Emulation.setDeviceMetricsOverride for the viewport, Runtime.evaluate to set localStorage and reload for a theme, Page.captureScreenshot per scroll position. ~40 lines, no puppeteer install, and the PNGs read straight back into context.
- 2026-09-04: a contract asking for "all five gap states simultaneously visible" can be unsatisfiable under the payload semantics nobody wrote down — S-1 (no ship record in the window) and S-2 (a pre-capability feature among features that DO have data) are mutually exclusive if window membership means "shipped in the window". It became satisfiable only by naming the alternative reading (membership = cycle activity) in the fixture and raising the choice as an open question for pm.
- 2026-09-04: FEAT-53 "use the astryx theme and font" was never a font-family problem — the computed
  families were already Astryx's. The three real causes were (a) a parallel size scale applied via
  inline `fontSize`, (b) a mono family forced onto 241 non-code elements, (c) overriding Astryx's
  own surface/border/text tokens in `defineTheme`. Diagnose "wrong font" by reading computed
  `font-family` first; if it already matches the system, the complaint is about application, not family.
- 2026-09-04: measuring a design claim in the browser beats asserting it — a CDP probe counting
  elements whose computed font-family is monospace (241 before, 14 after) and reading
  `getComputedStyle(documentElement).getPropertyValue('--color-background-card')` proved both the
  mono purge and the removal of the theme override in a way source-reading cannot.
- 2026-09-04: nesting an Astryx Text with type="code" inside one with type="supporting" resets the
  size UP to the code preset's base (14px), silently enlarging a meta line. Astryx type presets do
  not inherit down; a nested Text is a fresh preset.
- 2026-09-04: withdrawing a surface override changes every contrast ratio measured against it. Astryx
  dark card is #1F1F22, lighter than the #181C23 the old ladder used, so all dark ratios dropped
  0.2 to 1.8. Re-measure the whole table, not the tokens you think you changed.
- 2026-09-04: FEAT-53 layout pass. Astryx 0.5.2's Grid `columns={{minWidth, max}}` is auto-fill, so it cannot express a hard breakpoint (at 1200px it yields five or six tiles across, not the four the contract pins) and cannot express a 7fr/5fr split at all. A one-file stylesheet with media queries was the only mechanism; StyleX would be native but this prototype runs without its build step.
- 2026-09-04: Astryx table cells carry `max-width: 0` (the trick behind `text-overflow`), and header cells are always `white-space: nowrap` plus ellipsis. Consequence: a `min-width` on a pinned first column makes it eat the whole row, a `width` collapses it to one character per line, and any two-word column name truncates in a narrow column. What worked: lift `max-width` to `none` on that table, then a `width` hint on the first column, plus `white-space: normal !important` on header cells. Astryx atomic classes carry a `:not(#\#)` specificity hack, so an override needs `!important`.
- 2026-09-04: measuring beat looking on this pass. All four layout faults (pinned column, header truncation, an "S-1" badge ellipsised to "S…" in a 189px tile, a sparkline overflowing by exactly its 4px flex gap) were found by a CDP sweep comparing scrollWidth against clientWidth, not by reading a screenshot. Run that sweep before looking at anything.
- 2026-09-04: `npm run smoke` here is `vite build --ssr --outDir .smoke`, which EMPTIES .smoke/ — a throwaway verification script parked there is deleted mid-run. Park throwaways in their own dot-dir.
- 2026-09-04: FEAT-53, adopting @astryxdesign/theme-neutral. A theme package's BUILT stylesheet is
  `@scope ([data-astryx-theme="<its own name>"])`, and core's <Theme> writes OUR theme's name to
  <html>. So the documented "import core/astryx.css then theme/theme.css" wiring is inert the moment
  you consume the theme through `extends:` under a different name — proved it twice (no computed
  token differed; the 1920x1080 dark PNG was md5-identical with and without the import). Read a
  vendor stylesheet's selectors before believing its README's import order.
- 2026-09-04: FEAT-53. Swapping the base theme moved surfaces I had already measured against:
  Neutral's `muted` EQUALS `card` in dark and `surface` equals `card` in light, so the hatch ground
  token that worked under core's defaults showed nothing in one theme. The translucent generic fill
  (--color-neutral) was the only ground that recesses in both. When a substrate swaps, re-derive
  every composited ground, not just the foreground ratios.
- 2026-09-04: FEAT-53. Measuring a text token only against `card` hid a real failure: the shell's
  provenance line sits on `body`, where the light tertiary was 4.09:1. Grep for the token's call
  sites and measure against every ground it actually lands on.
- 2026-09-04: FEAT-53. A monochrome theme accent (Neutral's --color-text-accent is #262626/#EBEBEB)
  silently deletes a colour-only link affordance, and that exposed a pre-existing fault: Astryx's
  <Link as={RouterLink}> renders a <button> with no href, so nothing on the page was ever an anchor.
  Probing computed styles of the ELEMENT (tag, parent, href) rather than the colour is what found it.
- 2026-09-04: no browser tool in this persona and no playwright module installed, but
  ~/Library/Caches/ms-playwright/chromium-1228/.../Google Chrome for Testing.app is on disk and node
  26 has a global WebSocket — a ~100-line CDP driver (spawn --headless=new --remote-debugging-port=0,
  parse the ws:// URL off stderr, Target.attachToTarget, Emulation.setDeviceMetricsOverride,
  Runtime.evaluate, Page.captureScreenshot) gives real getComputedStyle + screenshots. Note the app
  bundle is named "Google Chrome for Testing", not "Chromium".
- 2026-09-04 (FEAT-53, tiles/tickets/split revision): Astryx `Stack` silently drops invalid
  alignment values. `justify="space-between"` is not in `StackMainAlignment` (`between` is) and
  `align="baseline"` is not in `StackCrossAlignment` (`start|center|end|stretch`), so both compiled
  to `justify-content: normal` / default `align-items` with NO warning. Every prior pass of this
  prototype carried both faults and no one saw them: the header control sat beside the title (right
  edge 668px in a 1920 viewport) and display figures were not on a baseline with their units. Found
  by measuring `getBoundingClientRect` + `getComputedStyle` on the control's ancestor chain, not by
  looking. Lesson: when a layout prop appears to do nothing, read the component's `.d.ts` union
  before adding CSS around it.
- 2026-09-04 (FEAT-53): evenly spaced TICK INDICES collapse on a temporal axis. When the fixture
  gained a busy last fortnight, six index-spaced x ticks over 26 ship records overlapped by 46px
  because the times were clustered. The fix that generalises: walk the points and take a tick only
  where its x clears the previous tick by one label width.
- 2026-09-04 (FEAT-53): a collision detector is cheap and finds what eyes miss — collect every
  `<text>` in every `<svg>`, group by rounded baseline y, sort by x, compare adjacent boxes. It
  caught three faults in one run (overlapping ticks, two end labels on one baseline, an ellipsised
  S-4 badge). Kept at /tmp/feat53-cdp/measure.js with a CDP driver that emulates
  `prefers-color-scheme` so "dark with the OS set to light" is measured rather than asserted.
- 2026-09-04 (FEAT-53): an operator revision can silently retire a demonstrated state. Making the
  fixture's last 14 days busy (so the tile sparklines have data) means NO window holds zero ship
  records, which removed S-1 from the overview. Kept it demonstrable by adding a post-capability
  feature that has not shipped (FIX-09) — the same treatment at feature scope. Worth checking, on
  any fixture change, which states the change makes unreachable.
- 2026-09-04 (FEAT-53, harness): bash-write-guard resolves a RELATIVE path against the main checkout
  rather than the command's cwd — `rm src/lib/themeMode.jsx` from inside the worktree was refused as
  "outside your domain", then as "belongs in worktree <the worktree I was in>". An absolute worktree
  path worked. Raised as an open question in the digest.
- 2026-09-05: FEAT-53 — measuring a "before" page height after the fact is a trap: `vite build`
  empties dist/, the prior revision was uncommitted, so both the old bundle and the old source were
  gone before I thought to measure. Reconstructed it by re-inserting the removed sentences into
  their own live containers over CDP (real widths, presets, flex gaps) and labelled the number a
  reconstruction. Next time: capture the baseline metric BEFORE the first edit.
- 2026-09-05: FEAT-53 — Astryx `Popover` content is mounted by an effect into the top layer, so
  `renderToString` emits only the trigger and an empty `<template>`. That made "the phrase is no
  longer on the surface" trivially assertable in the SSR smoke, and it means popover copy can never
  be asserted there — the browser is the only place it exists.
- 2026-09-05: FEAT-53 — CDP `Input.dispatchKeyEvent` with `type:"keyDown"` + `text:"\r"` did NOT
  make a focused native <button> fire its click; `type:"rawKeyDown"` then `keyUp` did. A keyboard
  test that "fails" this way is a harness artifact, not a component defect — check the dispatch
  shape before filing the bug.
- 2026-09-05: harness defect worth watching — mid-run every Write/Edit began failing with
  "check-domain: BLOCKED ... No module named 'gh_issue_types'" because a sibling worktree's
  half-landed change made `.claude/skills/harness/bin/factory_gh.py` import a module that only
  exists in that worktree. It cleared on its own after ~2 minutes. Also: the bash write-guard
  resolves relative `cp` targets against the repo root, not cwd — absolute paths, and one file per
  command, are what pass.
