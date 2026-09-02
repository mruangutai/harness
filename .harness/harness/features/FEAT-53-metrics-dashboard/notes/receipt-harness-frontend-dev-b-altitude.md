# B-ALTITUDE — FEAT-53 plan, altitude read

BLUF: 17 tasks is close to the right altitude. T-06..T-11 are correctly split by
capability, not by file — no merges recommended (all six: `leave`). Three real altitude
defects survive: a window-resolution rule restated instead of shared (fold-in), a
client task (T-15) instructed to do server-side work it has no grant to touch
(fold-in), and `touchpoints.py` homed inside the dashboard subtree when it is a
harness-wide instrument the dashboard should merely read (fold-in). Accepted
residuals (alpha chart lib, no auth, no database, no automated `ui` gate) are all
right to accept and all carry a named compensating control already in BRIEF/D-05/D-08/D-09.

## Findings

### ALT-1 — window→date-range resolution has no single authoritative home
Location: T-06 intent (`kpi.py`, "Window filtering keys on shipped_at; 30d and 90d
are relative to generated_at") vs T-08 intent (`defects.py`, `escaped(project_root,
window)` — no restatement of the boundary rule), T-09 intent (`attribution.py`, "For
every commit in the window" — same), T-10 intent (`trend.py`, `read(project_root,
window)` — same).
Summary: four backend tasks each take a `window` token and independently decide what
"30d relative to generated_at" means for their own dataset (features, commits,
trend points), with no named shared function.
Concrete cost: nothing stops the four private implementations from disagreeing at an
edge (calendar days vs 24h, inclusive/exclusive boundary), which would make a feature
counted "in the 90d window" for throughput but excluded from it for attribution — a
silent cross-KPI inconsistency no test in the plan would catch, since each task's
tests are fixture-local to that module.
Alternative: T-06 exposes one `resolve_window(token, generated_at) -> (start, end)`
in `kpi.py`; T-08/T-09/T-10 intents say "call kpi.resolve_window" instead of
restating window semantics.
changes_task_set: no
remedy_cost: amend (intent text only — kpi.py is already in every affected task's
`files:`, and dependency ordering already has T-08/T-09/T-10 reaching T-06)
**fold-in**

### ALT-2 — T-15 is told to do server-side work it has no path to do
Location: T-15 intent ("segment each series server-side into contiguous runs and
render one line per run if the library's null handling is not explicitly
documented") vs T-15 `files:` (`charts.tsx`, `CAP-probe.md` only — no backend path)
vs T-10 intent (`trend.py`/`kpi.py`'s `read()`, which returns raw points with no
mention of segmenting into contiguous runs).
Summary: the fallback for CAP-09 (missing point breaks the line) is written as
server-side segmentation, but the server task that owns that data (T-10) never
implements it, and the client task told to fall back to it (T-15,
harness-frontend-dev) is not granted any server file.
Concrete cost: if the CAP-probe finds the alpha library's null handling undocumented
— the exact condition the intent hedges on — frontend-dev cannot comply as written:
it cannot edit `trend.py` to segment server-side (ungranted), and doing the
segmentation client-side instead reproduces the exact anti-pattern this angle
checks for — the client recomputing something the server payload should already
carry.
Alternative: make trend segmentation unconditional and own it in T-10 — `read()`
always returns each series pre-segmented into contiguous runs, so T-15 only renders
what it is given and never branches on library behaviour to decide where a
computation happens.
changes_task_set: no
remedy_cost: amend (T-10 intent gains one sentence on the return shape; T-15 intent
loses the conditional server-side branch — no `files:`/`depends_on:` change)
**fold-in**

### ALT-3 — touchpoints.py is homed inside the dashboard subtree, not bin/ proper
Location: T-11 `files:` (`.claude/skills/harness/bin/dashboard/touchpoints.py`) vs
the plan's own lane rows (`.harness/harness/features/*/touchpoints.jsonl` is granted
to `harness-orchestrator`, not to any dashboard-owning agent) vs D-16 (the three
counted events — approval request, escalation, uat request — are raised by the
orchestrator, pm and validator, none of which are dashboard code).
Summary: the library every future caller (orchestrator, pm, validator) must import
to call `record()` is planned to live inside `bin/dashboard/`, the subtree D-01/D-02
model and grant specifically as the dashboard's own client+server source.
Concrete cost: harness-wide instrumentation ends up physically inside a UI feature's
directory; a caller outside the dashboard team's domain has to reach into
`bin/dashboard/` for a dependency that has nothing to do with rendering a dashboard,
and if the dashboard subtree is ever relocated or removed the touchpoint-counting
mechanism goes with it for no reason connected to its own purpose.
Alternative: home `touchpoints.py` at `.claude/skills/harness/bin/touchpoints.py`
(already covered by the existing `.claude/skills/harness/bin/**` grant), with
`kpi.py` importing it from there — the dashboard reads an instrument the harness
proper owns, not the reverse.
changes_task_set: no (T-11 still stands, only its `files:` path moves)
remedy_cost: whole-file-recreate (`files:` is a list field)
**fold-in**

## T-06..T-11 granularity verdict, pair by pair

- T-06 (kpi.py core + fixture) — foundational, every later task depends on it. `leave`.
- T-06→T-07 (grading.py): independent capability (file-mix, bins, outliers), own
  fixture assertions, own failure mode (a grade regression in this repo would fail
  T-07's test without touching T-08/T-09's tests). Merging would put three unrelated
  KPI computations behind one verify command, so a grading-fixture break would block
  landing defects/attribution work that has nothing to do with it. `leave`.
- T-07→T-08 (defects.py): same reasoning — different data source (git log directly,
  not feature.json), different fixture shape (BUG-NN dirs + Revert commits). `leave`.
- T-08→T-09 (attribution.py): same — different data source (commit subjects joined
  through plan.yaml + agent front matter), most complex resolution ladder of the
  six. Merging with T-08 would make one task own two unrelated join mechanisms.
  `leave`.
- T-09→T-10 (trend.py): T-10 legitimately depends on T-07 and T-09's output shapes
  (the trend record embeds `grade` and `attribution` objects) — this is a real
  ordering dependency, not a file-boundary artifact. Distinct mechanism (append-only
  write, the feature's only write path) from anything in T-06..T-09. `leave`.
- T-10→T-11 (touchpoints.py): distinct file, distinct trigger mechanism (event
  recording vs computed aggregation), distinct test additions. Not a natural merge
  target for T-10 despite sharing `test-metrics-trend.py`. `leave`.

None of the five modules' additions to `kpi.py` are more than a wiring line into the
aggregate dict — that repeated touch is the cost of the split, and it is cheap
compared to what a merge would lose: five independently red/green verify commands
mapping 1:1 to five independently reviewable capabilities.

## Cleared (checked, no finding)

- Unavailability contract (D-19): stated once, in T-06, "which every later task
  obeys" — later tasks reference it rather than restate it.
- No-central-tendency rule (D-12): stated once, in T-07 (KPI 5's only owner).
- Theme-token rule (raw hex in exactly one file): stated once, in T-13.
- File-mix forbidden-literal rule (SC-06): stated twice (T-07 prose, T-14 with an
  enforcing grep) but legitimately so — two different codebases (Python source,
  TSX source), each independently verified; not a drift risk.
- Client never re-derives what the server should send: grading bins/shares (CAP-01,
  T-07/T-14), escaped-defect count and sourcing rule (T-08/T-14), attribution
  buckets (T-09/T-14) all arrive computed in the payload and are only rendered
  client-side. (ALT-2 above is the one place this breaks down.)
- Residual: alpha charting library — compensating control named and enforced (D-08's
  four-capability trigger, T-15's probe-before-build gate). Right to accept.
- Residual: no auth on the bound port — compensating control named (D-05, 127.0.0.1
  only, no bind flag) and re-asserted in T-12. Right to accept for a single-operator
  local instrument.
- Residual: no database — compensating control named (D-09's cost measurement) and
  actually tested (T-12's verify enforces the 5.0s budget against the 1.1s baseline,
  SC-16). Right to accept.
- Residual: no automated `ui` gate — the sharpest one, and it checks out: BRIEF.md
  lines 110-113 name the control explicitly (SC-02/SC-08/SC-11 as `uat`, SC-15 as
  `ui-reviewer` inspection at `review_sha`). No plan *task* establishes uat/review —
  correctly so, since those are standard pipeline steps generated from `verify: uat`
  / `verify: inspection` SC markers by the harness proper, not build tasks in this
  plan. Same shape every other feature uses; not a gap unique to FEAT-53.
