# T-15 receipt — render two chart shapes

**BLUF:** Shape A uses the fixed five-grade ordinal domain and Shape B uses UTC-scaled, pre-segmented runs; CAP-08 is three independently coloured single-series plots, not three incommensurable series on one canvas.

- **Fail-first:** Before `charts.tsx` existed, the signed verify built successfully then its static proof failed with `FileNotFoundError` for `.claude/skills/harness/bin/dashboard/client/src/charts.tsx` (exit 1).
- **Changed source:** `.claude/skills/harness/bin/dashboard/client/src/charts.tsx` only. It exports `ShapeA` and `ShapeB`; Shape A is `aria-hidden`, has `keyboard: false`, fixed grades 1–5, datum-derived grade-token fills and no global bar line. Shape B uses `scaleUtc`, emits one `lineY` mark per supplied contiguous run, sets each mark's `strokeDasharray`, and carries circle, square, and triangle marker forms with direct end labels.
- **CAP-08 composition:** Shape B stacks the cycle-time, touchpoints, and grade-share single-series plots under one window. Each series provides its KPI identity hue, dash, marker, label, and unit; no `series-1`, `series-2`, or `series-3` role exists.
- **Implementation commit:** `495987fde0293a95dc6b6383a5b7e8718d7c3d3c` (`[harness:t-15] render chart shapes`).
- **Generated dist:** not staged or committed by this task. The signed build generated client dist output through a path resolved outside this worktree; the write guard denied restoring its tracked `.gitkeep` baseline. This has been escalated to the lead for restoration before T-16; this task cannot truthfully claim an unchanged generated dist tree.

## Signed verification

Command (verbatim):

```sh
npm --prefix .claude/skills/harness/bin/dashboard/client run build && python3 -c "import pathlib,sys;s=pathlib.Path('.claude/skills/harness/bin/dashboard/client/src/charts.tsx').read_text();[sys.exit('missing '+k) for k in ['strokeDasharray','keyboard'] if k not in s];sys.exit(0 if ('scaleUtc' in s or 'scaleTime' in s) else 'no temporal scale - scaleBand/scalePoint fabricates cadence, CAP-07')"
```

Output (verbatim):

```text
> build
> vite build

vite v8.3.0 building client environment for production...
[warn] `inlineDynamicImports` option is deprecated, please use `codeSplitting: false` instead.
transforming...
✓ 2599 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                  0.32 kB │ gzip:   0.23 kB
dist/assets/index-DzoXKmQ_.js  697.35 kB │ gzip: 213.24 kB

[plugin builtin:vite-reporter]
(!) Some chunks are larger than 500 kB after minification. Consider:
- Using dynamic import() to code-split the application
- Use build.rolldownOptions.output.codeSplitting to improve chunking: https://rolldown.rs/reference/OutputOptions.codeSplitting
- Adjust chunk size limit for this warning via build.chunkSizeWarningLimit.
✓ built in 150ms
```

Result: exit 0.
