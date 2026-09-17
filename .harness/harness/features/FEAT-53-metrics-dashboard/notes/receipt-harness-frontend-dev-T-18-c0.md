# T-18 receipt — alpha charting capability probe

**BLUF:** `@tanstack/charts@0.18.0` clears all thirteen recorded capabilities; D-08 does not trigger and the client may proceed.

- **Probe method:** A synthetic, deleted DOM-host entry point mounted a fixed-domain five-row `barY` chart and a `lineY` chart using `d3-scale`'s `scaleUtc`; it used only synthetic data and no client UI or chart component.
- **CAP-01:** Five pre-binned grade rows, including `grade: '2', count: 0`, rendered exactly 5 SVG bars from configured domain `['1','2','3','4','5']`.
- **CAP-07:** Adjacent date gaps measured 9.321311 px (one day) and 559.278689 px (sixty days), ratio 60.000000, using `scaleUtc`.
- **CAP-11 reading:** `lineY` supplies SVG `strokeDasharray`; independent per-series dashes use one line mark per series, while documented public `createMark` makes square and triangle markers authorable beyond built-in dot and hexagon.
- **Trigger analysis:** CAP-01, CAP-05, CAP-07, and CAP-11 are met. CAP-05 is intentionally inert app composition. No D-08 trigger fired; no operator decision is required.
- **Commit:** `1999f3a2 [harness:t-18] probe alpha charting capabilities`.

## Scoped verification

Command (verbatim):

```sh
python3 -c "import pathlib,re,sys;t=pathlib.Path('.claude/skills/harness/bin/dashboard/client/CAP-probe.md').read_text();[sys.exit('missing CAP-%02d' % i) for i in range(1,14) if 'CAP-%02d' % i not in t];sys.exit(0 if re.search(r'^VERDICT: (PROCEED|STOP)$', t, re.M) else 'no VERDICT: PROCEED or VERDICT: STOP line')"
```

Output (verbatim):

```text
(no output; exit 0)
```
