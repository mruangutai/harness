# A1 — backend server choice and its gate (harness-backend-dev)

**BLUF:** A1 is `sound-with-gap` — stdlib-only is the right call and the prerequisite gate adds no
undeclared dependency, but T-12's route table is silent on asset MIME types (a real load-bearing
gap for a served ES-module bundle), its `jsonschema` assertion checks a library the dashboard never
imports, and the dependency graph never makes T-12 wait on T-08 even though T-12's own verify checks
the KPI that only T-08 populates.

## A1a — the server choice: `sound-with-gap`
Citation: D-03 (plan.yaml:46-49), T-12 intent (plan.yaml:507-537).

stdlib `ThreadingHTTPServer` + hand-written routes is RIGHT, not merely defensible, for three
read-only loopback GETs, and D-03's reasoning is the correct one to weigh: every runtime import here
lands in the Harness **distribution**, paid by every onboarded project forever, not by one app.
FastAPI+uvicorn and Flask both fail that math for three routes; a Node server is additionally wrong
because it would reintroduce exactly the Node runtime dependency D-04 spends its whole reasoning
avoiding (T-12/T-16 exist so a user needs only python3) — D-03's "because" line doesn't state this
tie to D-04 explicitly, which is a citation gap worth one line but not a wrong call.

Checked the route table against what a framework would have caught for free:
- query-parameter parsing (`window`): covered — trivial with `urllib.parse.parse_qs`, a framework buys nothing here.
- 400/404 JSON bodies: explicitly specified (plan.yaml:526-527).
- `/assets/` traversal guard: explicitly specified, "strict path check that refuses any traversal outside dist" (plan.yaml:524-525).
- **MIME types: NOT specified anywhere in T-12's intent or verify.** T-04 builds a single-chunk ES module (`<script type="module">`, plan.yaml:215); browsers enforce strict `Content-Type` on module scripts and refuse to execute one served as the wrong type or `text/plain`. A hand-rolled route table has no free `mimetypes.guess_type` unless someone remembers to call it. T-12's verify never fetches an asset file and checks its header; T-16's smoke test only fetches `/` and `/api/kpis` (plan.yaml:679-681). Nothing in the 17 tasks would catch a serve-time MIME regression before a user hits a blank page.
- concurrency safety given `kpi.compute` shelling to git and `code-grade.py`: sound. T-07 explicitly requires the grader subprocess be run with `cwd=project_root` rather than `os.chdir` (plan.yaml:320-321), which is the one thing that would have made `ThreadingHTTPServer` unsafe here; that hazard is pre-empted.
- stampede / resource-exhaustion bound: **not bounded, and nobody says so.** `ThreadingHTTPServer` spawns one OS thread per accepted connection with no cap; each thread can trigger the ~1.1-5s git+`code-grade.py` fan-out. Loopback + single operator makes the realistic blast radius small, but the plan states the 1.1s baseline and the 5.0s ceiling (D-06, T-12 verify) without ever stating the concurrency bound is an accepted risk rather than an overlooked one.

## A1b — the gate: `sound`, with one overstated citation
Citation: DEC-190 full text (DECISIONS.md:5219-5249, "Where it is declared" at :5233-5238); harness-init prerequisites 7/8 (.agents/skills/harness-init/SKILL.md:47); CI install step (.github/workflows/tests.yml, "Install PyYAML and jsonschema" step, `pip install pyyaml jsonschema`).

**PyYAML and jsonschema are already required harness-wide prerequisites** — declared at
`.agents/skills/harness-init/SKILL.md:47` (items 7 and 8, install commands at :61-65) and asserted
in CI (`.github/workflows/tests.yml`, the "Install PyYAML and jsonschema" step). T-12 is **not**
newly depending on either; its serve-time `--check` re-asserts an already-required prerequisite at
the point of use, which is defense in depth, not a new undeclared dependency. That is exactly why
none of the 17 tasks touches `harness-init/SKILL.md` or `tests.yml` — correctly so, since there is
nothing new to declare there. The exact file/line a genuinely new dependency would need is
`.agents/skills/harness-init/SKILL.md:47,61-65` plus `.github/workflows/tests.yml`'s install step;
no task in this plan writes either.

The gap: **nothing in the dashboard's own module set (`kpi.py`, `grading.py`, `defects.py`,
`attribution.py`, `trend.py`, `touchpoints.py`, `serve.py`) ever imports `jsonschema`.** Schema
validation against `feature-schema.json` lives in `validate-feature-json.py` / `check-domain.sh`,
which the dashboard never calls — it reads `feature.json` as plain JSON and `plan.yaml` as plain
YAML (T-06 intent, plan.yaml:268-271). So T-12's gate is checking a library the request path never
touches. Harmless (it's already required regardless of this feature), but the citation of DEC-190 in
D-03/T-12 reads as if the dashboard is load-bearing on `jsonschema`; it is not — only on `yaml`.

## A1c — topological order: `sound-with-gap`
Mechanically verified with python3 + PyYAML: **acyclic**, every `depends_on` references an existing
id, and file order T-01..T-17 **is** a valid topological order (all three checked programmatically,
not by hand).

T-01 correctly precedes every task that needs the widened grant: T-13 depends on it directly
(plan.yaml:544), T-14/T-15 inherit it transitively through T-13. T-04 and T-05 correctly do not
depend on T-01 — T-04's execution_agent is harness-dev-ops (broader domain already) and T-05 writes
under the prototypes path already granted to harness-visual-designer by the lanes table.

**The graph does drop one real edge.** T-06 explicitly leaves `aggregate.escaped_defects` null until
"later tasks replace them" (plan.yaml:280-281); only T-08 fills it (plan.yaml:346-378). T-12 serves
`kpi.compute()` verbatim over `/api/kpis` and its own verify asserts "every KPI reflects the fixture"
(plan.yaml:533) — escaped defects is one of the six KPIs (D-12 through D-19's KPI list). But T-12's
`depends_on: [T-03, T-10, T-11]` (plan.yaml:499) never reaches T-08: T-10 depends on `[T-03, T-07,
T-09]` (plan.yaml:424) — not T-08, because the trend record schema (D-18) has no `escaped_defects`
field, so T-10 legitimately doesn't need it. T-08 is a sibling of T-07/T-09, all three depending only
on T-06, with no edge into T-12's chain at all. A scheduler that dispatches ready tasks by
`depends_on` satisfaction (rather than strict file order) can execute or verify T-12 before T-08
lands, producing a null `escaped_defects` in the served payload and a verify failure — or a false
green if the fixture's escaped-defect count happens to be attempted at zero.

## Findings

1. **id:** F-A1-01 | **severity:** blocking | **citation:** T-12 intent, plan.yaml:507-537 (no MIME-type
   language); T-12 verify, plan.yaml:530-537 (no asset-header assertion); T-16 verify smoke test,
   plan.yaml:679-681 (fetches `/` and `/api/kpis` only). **Consequence:** the built single-chunk ES
   module bundle (T-04, single-chunk vite output) is served with no specified `Content-Type`; a
   browser enforcing strict MIME checking on `<script type="module">` refuses to execute a
   wrong-typed or defaulted asset response, and the dashboard renders a blank page for every user,
   with no task's verify catching it before ship. **Alternative:** add one sentence to T-12's intent
   requiring `mimetypes.guess_type` (or an explicit extension table) on every `/assets/` response,
   and extend T-12's verify to fetch one asset and assert its `Content-Type` header. **remedy_cost:**
   amend (both are text-scalar `intent:`/`verify:` edits, no `files:` change).

2. **id:** F-A1-02 | **severity:** advisory | **citation:** T-12 intent, plan.yaml:508-510 (stdlib
   `ThreadingHTTPServer`, no thread-count language) and D-06 (plan.yaml:58-61, 1.1s recompute cost).
   **Consequence:** `ThreadingHTTPServer` spawns one unbounded OS thread per connection; a burst of
   concurrent `/api/kpis` requests each triggers a multi-second git + `code-grade.py` subprocess
   fan-out with no queueing or cap, an unbounded-resource mode the plan never states is accepted.
   Loopback-only + single-operator makes the realistic blast radius small. **Alternative:** one
   sentence in T-12's intent naming the bound as an accepted risk (or a `ThreadingHTTPServer`
   subclass capping concurrent threads). **remedy_cost:** amend.

3. **id:** F-A1-03 | **severity:** advisory | **citation:** T-12 intent, plan.yaml:516-517
   ("assert ... that yaml and jsonschema import"); dashboard file list across T-06/T-07/T-08/T-09/T-10/T-11
   (plan.yaml:258-259, 312-313, 355-356, 388-389, 427-429, 466-467) — none imports `jsonschema`;
   actual jsonschema consumers are `validate-feature-json.py`/`check-domain.sh`, never called by the
   dashboard. **Consequence:** not a functional bug (jsonschema is already a harness-wide required
   prerequisite regardless of FEAT-53), but the gate asserts a dependency the dashboard's request
   path never exercises, and D-03/T-12's DEC-190 citation reads as if the dashboard is load-bearing
   on `jsonschema` when only `yaml` is. **Alternative:** either drop the `jsonschema` assertion from
   T-12's gate (yaml alone covers the dashboard's real needs) or add one clause noting it is
   deliberate belt-and-suspenders against the harness-wide requirement. **remedy_cost:** amend.

4. **id:** F-A1-04 | **severity:** blocking | **citation:** T-06 intent, plan.yaml:280-281 (defers
   `escaped_defects` to "later tasks"); T-08, plan.yaml:346-378 (the only task that fills it); T-10
   `depends_on`, plan.yaml:424 (`[T-03, T-07, T-09]`, omits T-08); T-12 `depends_on`, plan.yaml:499
   (`[T-03, T-10, T-11]`, never reaches T-08); T-12 verify, plan.yaml:533 ("every KPI reflects the
   fixture"). **Consequence:** under any scheduler that dispatches ready tasks by `depends_on`
   satisfaction rather than strict file order, T-12 can be built/verified concurrently with or before
   T-08, so the payload T-12 serves and tests can have a null `escaped_defects` where the verify
   expects the fixture's real count — a graph defect independent of whether the current orchestrator
   happens to run tasks in file order. **Alternative:** add `T-08` to T-12's `depends_on` list.
   **remedy_cost:** whole-file-recreate (`depends_on` is a list field; `plan-merge.py amend` refuses
   list fields at exit 4).
