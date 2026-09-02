# Goal-check — plan vs stated intent — FEAT-53 — cycle 1

> **Does this plan deliver the operator's stated intent?**

**Yes — with four drifts to settle at signature.** Checked against
`.harness/notes/grilling-metrics-dashboard-2026-09-01.md` (140 lines), not BRIEF.md. 13 top-level
Settled bullets walked (the dispatch said fourteen; the artifact carries thirteen, the KPI bullet
holding six sub-shapes): **11 satisfied, 1 partial, 1 drifted.** All 8 Not-yet-specified bullets are
resolved — none absent. No creep into any of the 4 Out-of-scope items. Both falsified facts reach the
TASKS, not just the research note. One of the remaining seven facts has gone stale, and it has taken
a verification guard with it (F3).

## Findings

| id | sev | artifact bullet | plan id | finding |
|---|---|---|---|---|
| F1 | **med** | Destination ("through a real web framework (backend + frontend)"), Settled 5 (dependency posture), NYS-1 | **D-03** | The operator settled that a real web-framework backend is justified and asked how its addition would be gated. D-03 rejects FastAPI, Flask and a Node server and ships python3 stdlib. The engineering merit was reviewed (`runs/2026-09-01-01-eng` A1) — the **reversal of a settled item was not**. D-03's `because` argues cost only; nothing tells the operator a settled bullet was re-decided. It belongs on the signature agenda beside D-08 and D-20, not inside a `because`. |
| F2 | **med** | Settled 6, KPI 1 ("cycle time from **BRIEF** approval to ship"); BRIEF REQ-03 repeats it | **D-14, T-06** | Cycle time starts at `plan.yaml approval.date` — **plan** approval, not BRIEF approval. The measurement therefore excludes the brief→plan interval. The choice is forced (no structured BRIEF timestamp exists) and D-14's reasoning is sound, but the *definition change* is undisclosed in both D-14 and T-06, and REQ-03 still says BRIEF. Either D-14 names the substitution or REQ-03 is wrong. |
| F3 | **med** | Facts 2 ("107 `.py`, 12 `.sh`, 3 `.ts`") | **T-07, T-14** (and T-05) | Stale: measured now at `origin/main` and on this branch, **106 tracked `.py`**, so the mix total is **121, not 122**. T-07's and T-14's anti-hardcoding sweeps grep for the literals `107` and `122` — neither is a live figure any more, so a hardcoded *current* mix figure (`106`/`121`) passes the guard clean. T-12's own text already says "106 tracked .py", so the plan carries both numbers. The guard needs the digits re-derived at build time, not pinned in the plan. |
| F4 | **med** | Destination ("any onboarded project gets it"), Settled 6 KPI 1 ("run count/**size** per feature") | **T-06** | Change size comes from `git diff <default>...<feature-branch>` and is `null` with a reason "when the branch is gone". This repo keeps 49 remote branches; most onboarded projects delete merged branches, so half of KPI 1 is **permanently unavailable off this repo** — honest, but empty. `review_sha` survives the prune, is non-null in **52** of this repo's `feature.json` files, and T-06 already reads the field; `git diff <default>...<review_sha>` is still the single three-dot call T-06's perf rule demands. Cheap fix, real generality gain. |
| F5 | low | Settled 6, KPI 6 ("by **agent** / model tier") | **T-09, T-14** | `by_tier` keys are model names only. T-09's ladder resolves `execution_agent` en route and discards it, while T-14's tile is labelled "Usage by agent/model tier" — a label promising a dimension the payload cannot serve. Keeping the agent name in the record costs nothing. |
| F6 | low | Settled 13 (charting) — **D-08 decision support, not a defect** | **D-08 vs T-18** | D-08's fallback trigger is "any of CAP-01, CAP-05, CAP-07 or CAP-11 unmet". T-18 instructs that CAP-05 is **inert as a trigger** — app composition, passes for any library — and DESIGN calls it "cheap — the table is ours". The trigger is effectively **three** capabilities, not four. The operator is choosing whether to accept the alpha; the width of the net is exactly what that turns on. |
| F7 | low | Settled 5 + 13 — **D-20 decision support, not a defect** | **D-20** | D-20 says the server-rendered option deletes three of the four firsts and the alpha risk. It does not say that it also **ends the settled dependency posture in both halves** (no backend framework *and* no JS charting library), makes D-08 moot, and voids D-02/D-04/D-07/D-08 plus T-01, T-02, T-04, T-13, T-14, T-15, T-16 and T-18 — over a third of the plan. An operator answering yes-or-no should see that blast radius. |
| F8 | info | Settled 8 (storage, "roughly 1.1s total") | D-06, D-09, T-12 | The operator's own measured premise is superseded: 3.6s projected, 8.0s gate ceiling, per-item measurement of 2026-09-01. The *conclusion* (no cache at launch) is unchanged and T-12 re-measures it every run, so the deferral stays falsifiable. Disclosed explicitly in all three ids — correct handling, but the operator should know his number moved ~3x. |

## Per-section evidence

**1 · Destination — met, and visible in the tasks.** Per-project resolution is implemented, not
asserted: T-06 `compute(project_root, window)` "reads no path relative to the process cwd and no
value from this repository"; T-07 runs the grader as a subprocess with `cwd=project_root` precisely
because `code-grade.py` resolves the git root from cwd; T-09 reads `project_root/.claude/agents/`;
T-11 writes `project_root/.harness/<repo>/features/<id>/touchpoints.jsonl`; T-12 `--root` defaults to
the git root of cwd. It is *proved* by task, not claimed: T-06 builds fixture `project-a` with feature
ids absent from this repo, and T-12 asserts "every KPI reflects the fixture and no figure equals this
repository's value for the same KPI". Distribution shape: D-01 places source in the authored skill
tree; T-16 commits the bundle so a project needs python3 only; T-02 ships the ignore rules through
`templates/gitignore.snippet`; T-17 writes METRICS.md for "a user who has just onboarded a project".
A project *gets* the capability by being pointed at, consistent with the single-checkout pattern.
F4 is the one place generality is thinner than the destination claims.

**2 · Settled, one at a time.** 1 purpose ✓ (no go/no-go framing anywhere) · 2 normal process ✓ ·
3 general capability ✓ (above) · 4 live server, not the static-render convention ✓ (D-03 serves live,
D-06 recomputes per request; D-20's alternative is still live-server) · **5 dependency posture ✗ F1** ·
6 KPI set **partial**, see below · 7 no dollar meter ✓ (grepped: the only `spend` in plan.yaml is
"spend about a second of the request budget") · 8 no DB, no cache at launch ✓ D-09 (F8) ·
9 append-only `trend.jsonl`, never recomputed, no backfill ✓ D-10 + T-10 + T-19 (the writer is
`gh-sync.py cmd_ship` rather than "the orchestrator" — same moment, structural instead of prose) ·
10 not new `feature.json` keys ✓ D-11, and T-11 forbids a counter key explicitly ·
11 DB **deferred, not rejected** ✓ D-09 names the derived, gitignored, rebuildable cache as the future
lever; the merge hazard behind the operator's choice is honoured operationally by T-10's test of three
worktrees landed by two sequential merges · 12 React + TanStack Router/Query on Astryx, no second
substrate ✓ D-07 · 13 TanStack Charts, alpha named and accepted ✓ D-08 (F6; and the capability *spec*
was done at plan time as CAP-01…13 in DESIGN while the *probe* is T-18, first client task, ahead of
all client UI — substance kept, literal "before build starts" moved).

**Six KPI shapes.** KPI 1 throughput — runs ✓, change size ✓ but F4, cycle time F2. KPI 2 rework ✓
T-06 (both terms, "never as a lone ratio" — stronger than asked). KPI 3 escaped defects as an
**ongoing** measurement ✓ T-08 + D-15, windowed, `sourcing_rule` carried in the payload. KPI 4 the
never-instrumented touchpoint count ✓ D-16 + T-11 recording at the moment, **and T-20 supplies the
three call sites** — without it the number would be a permanent silent zero. KPI 5 ✓ all of it:
distribution + named grade-1/grade-2 outliers (D-12, T-07 `outliers` holds every one, T-14 renders
them as text, never behind a hover), **no mean or median anywhere in the payload**, `code-grade.py`
whole-repo mode via its real `--json` contract (`records`/`passing`/`ungraded`, confirmed at
`code-grade.py:154`), Python-only caveat persistent in the UI (T-14 `GradingCaveat` S-3), and the
`.py/.sh/.ts` ratio computed live from `git -C project_root ls-files` — never hardcoded (F3 is about
the guard, not the computation). KPI 6 ✓ as its own task T-09 with the full four-hop join and named
unattributed buckets; F5 is the missing agent dimension.

**3 · Not yet specified — 8 of 8 resolved, none absent.** 1 → D-03 + T-12's prerequisite gate
(resolved by elimination; F1). 2 hosting → D-05 (127.0.0.1, no bind flag, no auth). 3 trigger/refresh
→ D-06 (one on-demand command, per-request recompute, no background job, no auto-start). 4 escaped-
defect sourcing → researched, then D-15 + T-08. 5 join mechanics → T-09's six-step ladder. 6 entry
point + slash command → D-17 (`bin/dashboard/serve.py`, no new command, `.claude/commands/**` is
granted to nobody). 7 `trend.jsonl` schema + approval sourcing → D-18 + T-10 + D-14 (F2). 8 how
touchpoints are counted at the moment and where the running count lives → D-16 + T-11
(`touchpoints.jsonl` per feature) + T-20.

**4 · Out of scope — no creep.** Dollar/cost metering: absent (grep clean). True cross-provider
aggregation: T-09 buckets by *model name found*, never by provider, and D-13 forbids a two-bucket
split — no provider dimension exists. Cross-project comparison: one project per instance via `--root`;
nothing aggregates across projects. `.sh`/`.ts` grading: T-07 only *counts* them as ungraded share by
extension and sets `languages_covered: ["python"]` — required by KPI 5's live ratio, not creep.

**5 · Facts.** Both corrections reach the TASKS: (a) `approval.date` → **D-14** *and* T-06's intent
("approved_on comes from plan.yaml approval.date"), carried into T-10 and T-19 — the artifact's "no
structured approval timestamp exists anywhere today" is dead; (b) commit-attribution sparsity →
**D-13** (753 of 975) *and* T-09's intent, with all four unattributed buckets named and T-14 putting
the unattributed count on the tile. Of the other seven: fact 2 is stale → **F3**; fact 1 holds
(`--json` at `code-grade.py:138`, whole-repo `paths...`); fact 3 holds (16 agent files, 16 with a
`model:` key); facts 4, 5, 6, 8 hold; fact 9 ("no `package.json` anywhere") still holds in the tracked
tree today (0 tracked) but is being falsified as we speak by T-05 in flight and then T-04 — expected,
not drift. Commit count has moved 974 vs the artifact-era ~967; the plan's own 975/978 figures are
consistent with that and nothing rests on the exact value.

## Open questions for signature

- Q1 (blocking): does the operator confirm **no backend framework** (D-03), which reverses Settled 5?
- Q2: is cycle time measured from **plan** approval (D-14/T-06) acceptable, or must REQ-03's "BRIEF
  approval" be honoured or reworded?
- Q3: D-08 — the fallback trigger is three live capabilities, not four (CAP-05 is inert). Q4: D-20 —
  the no-npm option also ends the settled JS-charting posture and voids ~8 tasks.
