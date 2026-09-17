---
status: open
---
# Grilling — automated UI verification lane — 2026-09-17

## Destination
A `ui` test kind that renders the **served, committed** client bundle in a real browser at the
contract's viewports, asserts DESIGN.md's measurable rules, and leaves screenshot + results
evidence under the validate run. QA gates on it; `harness-ui-reviewer` judges from its evidence
instead of from source. FEAT-53 is the first consumer: its checks and specs are written here and
run **red** on the divergences the operator saw; FEAT-53 turns them green on resume.

## Mission
mission: plan
reason: three enforcement surfaces change — harness.json's `ui` kind and the matrix gate, the
harness-ui-reviewer agent definition, and CI — so the patch test fails on rule 3 outright.
confirmed-by: operator

## Settled
- Why this exists → the `ui` kind is `unresolved`/`cmd: null` and documented as "skipped, does
  NOT fail"; the ui-reviewer audits source, not pixels (its own §Known limit). Three FEAT-53
  validate rounds passed a bundle that shipped no CSS and diverges from the prototype on header
  layout, KPI identity hues, status-label colour and the table. A person saw each in seconds.
- Tooling → `@playwright/test` in the client package (pinned Chromium; `webServer` runs
  `serve.py --root <fixture>`; projects for 1440 and 1920 viewports; `@axe-core/playwright` for
  accessibility/contrast). Rejected: Puppeteer (no runner/diff/a11y), Cypress (heavier, poor
  multi-viewport), BackstopJS (pixels only), Chromatic (SaaS).
- Gating → measurements gate (DESIGN's numbers, token colours, tab order, focus-visible, contrast
  become assertions that fail). Screenshots are always captured as evidence. Pixel baselines
  (`toHaveScreenshot`) gate only where a feature commits them — opt-in, never default.
- Evidence → `runs/<id>/ui/results.json` + per-test screenshots as webp, committed. Playwright
  HTML report and traces gitignored (local debugging only).
- Traceability / "touched surface has specs" → DESIGN.md grows a `## Checks` table (check id →
  spec title). visual-designer owns the table; frontend-dev writes the specs. The lane FAILS if
  results.json lacks any listed id. Missing evidence is FAIL, never skip.
- Fail-open closed → `ui` becomes `active` with a real `cmd`; the matrix's `has_interaction_flow`
  branch FAILS when the lane has no specs for the touched surface. harness.json, gate scripts and
  the agent file change through the main-session direct lane (DEC-174); `tests.yml` gains
  `npx playwright install --with-deps chromium` after its existing `npm ci` (dev-ops).
- harness-ui-reviewer Mode B → consumes the lane's screenshots + results and judges against
  DESIGN.md and the prototype; may re-run the lane; never ad-hoc CDP/browser scripting. A
  dimension with no evidence is a FAIL finding, not "human check required".
- Base branch → this feature's worktree stacks on `feat/FEAT-53` and merges back into
  `feat/FEAT-53`; FEAT-53 carries both to main in one PR. (main has no dashboard client; a lane
  proven on a throwaway page proves nothing.) Recorded as an operator ruling deviating from
  "worktree from main".
- First consumer → lane + FEAT-53's `## Checks` table + its specs, written and RUN here, expected
  red on the known defects. Fixing FEAT-53's defects stays in FEAT-53 (it resumes at 40/45 cycles
  with the lane as its signal).

## Not yet specified
- Which DESIGN.md rules are automatable now versus stay inspection-only (e.g. "dense over airy");
  the `## Checks` table will draw that line per rule.
- `results.json` schema (fields QA's gate and the reviewer read) and how the check id is carried
  in the Playwright test title/annotation.
- Whether `dashboard/fixtures/project-a` carries enough operational data (attention states,
  grilling, worktree rows, unavailable KPIs) for deterministic screenshots, or needs extending.
- How the gate resolves "touched surface" for a diff that changes a shared component but no
  route: probably every listed check runs regardless; pm to confirm.

## Out of scope
- Fixing FEAT-53's header/hue/table defects (FEAT-53 on resume).
- Light theme, layouts below 640 px (DESIGN C-3 / §Out of scope already rule them out).
- A baseline-approval touchpoint for pixel diffs (baselines are opt-in; no workflow for them yet).
- Storybook or any component gallery; the prototype's `/__fixtures/gap-states` idea for the build
  is FEAT-53's if it wants it.
- Retro-auditing older UI features; the lane applies from its landing forward.

## Facts I verified (so pm does not re-derive them)
- `harness.json` `test_kinds.ui`: `status: unresolved`, `cmd: null`, `_reason` says qa records
  `ui: skipped (no browser target)` and does NOT fail — checked at `ac486811` (feat/FEAT-53).
- `test_matrix.frontend` and `.feature` both carry `when: [{kind: ui, if: has_interaction_flow}]`.
- `.claude/agents/harness-ui-reviewer.md` tools: Read, Glob, Grep, Bash, Write; §"Known limit — you
  audit SOURCE, not pixels" at lines 85–92.
- `serve.py --root <path>` and `--port` exist (`serve.py:296-297`); fixture control plane at
  `.claude/skills/harness/bin/dashboard/fixtures/project-a`, used by `tests/integration/test-metrics-dashboard.py`.
- Client package: vitest + jsdom only; scripts `build`, `dev`, `test`; no Playwright/Puppeteer.
  Chromium 1243 already cached at `~/Library/Caches/ms-playwright` (OMP's browser tool).
- `.github/workflows/tests.yml:89` runs `npm ci --prefix .claude/skills/harness/bin/dashboard/client`;
  no browser install step.
- DESIGN.md pins measurable rules: header ≥72 px with window control then 180 px Repository
  Selector at right (§Single-dashboard composition 1); 4+3 tiles at ≥1024 (KPI-R1); identity hue
  on tile label dot / sparkline / end dot (§Direction encoding); status hue on attention-card label
  text only; `:focus-visible` rules and exact Tab order (§Keyboard operability); per-token contrast
  table (§Palette); hatch gradient stops (C-4). It also names source greps (hex outside theme,
  `fontSize:` in components, charts without a token colour prop).
- Prototype (operator-approved reference) at
  `.harness/harness/features/FEAT-53-metrics-dashboard/notes/prototypes/FEAT-53/` with
  `observed-1440.png` / `observed-1920.png` and `src/layout.css`; the build has no `layout.css`.
- FEAT-53 paused at run 29 (eng PASS, unvalidated), cycles 40/45, review_sha at the error-list fix;
  `main` at `23d6745b` has no dashboard client.
