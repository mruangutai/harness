# FEAT-53 UI review — 2026-09-17-28-validator

PASS — the committed production bundle at review pin `ebce36e77769a64ac0e302692d8aa350dceca0e4` closes U-01 on the real dashboard surface. The reviewed delta base is `daba2af5513a0316f57ed8729576acb0e582708b`; later pin-only commit `a103cc48c75d2c8890b25b616bc2bbe082f67602` was excluded.

- Surface: actual `.claude/skills/harness/bin/dashboard/serve.py`, invoked from the assigned checkout as `uv run --with flask --with pyyaml python .claude/skills/harness/bin/dashboard/serve.py --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53 --port 8765` because the workstation Python lacked the declared Flask/PyYAML prerequisites. Browser URL: `http://127.0.0.1:8765/`; Chromium desktop viewport: `1440 × 1100`.
- Pin identity: the working-tree `serve.py` and `client/dist/` were byte-identical to review pin `ebce36e…` (`git diff --exit-code`), and pinned `client/dist/index.html` names `./assets/index-DnXu7ssi.js` and `./assets/index-BGeYwNXA.css`. The pinned tree contains those exact assets.
- Browser/network evidence: Flask served `/` 200, `/assets/index-BGeYwNXA.css` 200, `/assets/index-DnXu7ssi.js` 200, `/api/work?window=all&repo=all` 200, and `/api/kpis?window=all&repo=all` 200 during capture. The CSS therefore loaded in the browser rather than merely appearing in HTML.
- Styling: the screenshot shows fixed-dark Neutral/Astryx presentation with a structured dashboard container, styled type hierarchy, radio controls, select, buttons, links/tabs, bordered KPI cards, hatched unavailable states, and a separately bordered, wrapped error region. This is not browser-default rendering; error content remains readable and spatially separated from the controls and KPI grid.
- KPI 6: `Usage by Agent / Model Tier` visibly shows numeric `0` with `2175 of 2175 commits unattributed`; `[object Object]` is absent.
- Throughput: visibly renders the hatched `unavailable` treatment and exact reason `91 features lack a ship record or approval date`; it does not render numeric `0` as the tile value.
- Screenshot: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard/runs/2026-09-17-28-validator/ui-browser-evidence.png`; verified non-empty PNG, 1440 × 1100 RGB, 138016 bytes.
- Server stop: successful; supervised `serve.py` process stopped after capture (terminated with supervisor signal, exit 143).

```yaml
VERDICT: PASS
DIGEST:
  headline: "The real committed dashboard bundle loads Astryx CSS and visibly fixes KPI 6 and Throughput at the immutable review pin."
  mode: B
  in_scope: true
  severity_max: none
  findings: []
  must_fix: []
  states_unspecified: []
  contract_violations: []
  a11y: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard/notes/review-harness-ui-reviewer-2026-09-17-28-validator.md
```
