schema: plan/1
feature: FEAT-53-metrics-dashboard
tasks:
  - id: T-15
    title: Render the two chart shapes and probe the alpha API against the capability list
    traces: [REQ-07, REQ-10, REQ-11]
    change_type: frontend
    execution_mode: team
    execution_agent: harness-frontend-dev
    depends_on: [T-14]
    status: ready
    files:
      - .claude/skills/harness/bin/dashboard/client/src/charts.tsx
      - .claude/skills/harness/bin/dashboard/client/CAP-probe.md
    verify: |
      npm --prefix .claude/skills/harness/bin/dashboard/client run build && python3 -c "import pathlib,sys;t=pathlib.Path('.claude/skills/harness/bin/dashboard/client/CAP-probe.md').read_text();[sys.exit('missing CAP') for i in range(1,14) if 'CAP-%02d' % i not in t]"
    intent: |
      Build the two chart shapes DESIGN C-2 specifies with TanStack Charts (D-08), and record the
      probe.
      FIRST, before writing the charts, put each of CAP-01 through CAP-13 to the installed alpha API
      and write CAP-probe.md beside the client package: one row per capability, met or not met, with
      the API surface you used or the reason it is absent. Where a capability is absent, take
      DESIGN's stated fallback for it and say in the row that you did. It lives in the client tree
      rather than under notes/prototypes/ because that directory is the visual designer's grant and
      you could not write it.
      THE FALLBACK TRIGGER (D-08): if any of CAP-01, CAP-05, CAP-07 or CAP-11 is unmet, STOP, do not
      write the charts, and return with the probe as your artifact - those four are hard requirements
      and their absence is the trigger to swap to React Charts, which is a decision above your tier.
      SHAPE A, the grading histogram: pre-binned counts as a bar series over an ordinal axis of
      exactly five grade categories, each bar taking its own grade token from the datum, an empty
      category rendered as an empty bar and never dropped, per-record bar membership encoded as a
      datum-derived hatch on the sub-portion and NEVER as one global reference line at 4, the chart
      aria-hidden beside the real table T-14 supplies, and a bin label per bin so no legend is
      needed. Zero graded functions hands over to NoShipRecords before the chart mounts.
      SHAPE B, the time-series lines: a temporal x axis with irregularly spaced points, a missing
      point BREAKS the line with no interpolation and no coercion to zero - segment each series
      server-side into contiguous runs and render one line per run if the library's null handling is
      not explicitly documented. Per-series dash pattern (solid, 6-2 dash, 2-2 dot) and marker shape
      (circle, square, triangle) set independently of colour, plus a direct end-of-line label, so hue
      is never the only carrier. Every colour, stroke and dash is a theme token passed in; no library
      default is used. Histogram height 280px, time-series 320px, both filling container width.
      CAP-08 is open (DESIGN Q2): one plot with three y axes if the alpha supports it, otherwise
      three stacked single-series plots sharing one x axis. Either satisfies every requirement - say
      in the probe which you built.
