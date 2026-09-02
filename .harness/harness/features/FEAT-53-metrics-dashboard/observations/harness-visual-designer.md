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
