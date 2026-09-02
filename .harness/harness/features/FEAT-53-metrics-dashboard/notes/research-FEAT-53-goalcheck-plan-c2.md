# Goal-check — FEAT-53 plan, cycle 3 — does this plan deliver the operator's stated intent?

> **STATUS: the FAIL below was correct when taken and is kept verbatim as the record. Every
> blocking item in it was closed in loop-back 2 on 2026-09-01 — see
> `## Cycle-2 closure re-grade` at the foot of this file for the per-item re-grade and the
> final verdict. Read the FAIL as history, not as the current state.**

**BLUF: NOT YET — the three ruled fixes all landed in substance, but fix 1 (Flask) left three
downstream statements false, one of which turns a REQUIRED CI check red on every PR of this
feature. Do not sign as-is; one more pm cycle closes all of it.** Graded against
`.harness/notes/grilling-metrics-dashboard-2026-09-01.md` and
`notes/answers-2026-09-01-plan-signature.md`, not against BRIEF's restatement.

## 1. DEC-1 — framework: **DELIVERED**

- `plan.yaml` **D-03** now chooses Flask ("one WSGI application object in dashboard/serve.py")
  and rejects FastAPI+uvicorn, a Node server and stdlib `ThreadingHTTPServer` **by name with a
  reason each** (`dec: DEC-190`) — the DEC-190-style justification the ruling demanded, visible
  as the decision itself rather than inside a `because:` reversal.
- **T-12 is consistent**: Flask routing decorators; gate asserts `THAT FLASK IMPORTS` and prints
  `python3 -m pip install flask`; `127.0.0.1` only, no bind flag (D-05); read-only (REQ-13);
  port 8971; `--check`; `/assets` via `send_from_directory` **plus** the explicit
  `mimetypes.guess_type` fallback table (.js/.mjs/.css/.html/.svg/.woff2/.map); 8.0s ceiling with
  its measurement paragraph. New test case: Flask made unimportable must gate. All survive.
- **No line in `plan.yaml` or `BRIEF.md` asserts a stdlib server.** Five hits, all rejected-
  alternative or historical ("replacing what this task said while D-03 named the stdlib server",
  plan.yaml:725). BRIEF:107-111 carries the Flask constraint, marked dashboard-only + SUPPLIES.
  Out-of-scope but stale: `STATE.md:17` still says "D-03 ships a stdlib server".

## 2. DEC-4 / PF-328f8f3c — no fabricated zero: **DELIVERED**

- **D-21** (plan.yaml:125) is a decision with a computable predicate: epoch file
  `.harness/metrics/instrumented_at` vs the feature's start instant (`approval.date`, else the
  author date of the first commit adding the feature dir). Four ordered branches in **T-11**
  (plan.yaml:643-694); a zero is reachable **through branch 4 only**, each null carrying a D-19
  specific sentence. **T-20** supplies the three call sites, so branch 4 is not dead.
- **Two separate assertions**, labels greped verbatim by T-11's verify, plus `! grep FAIL` so a
  passing exit cannot mask a printed failure. **BRIEF SC-17** states both branches, the no-epoch
  project, and the aggregate's named not-tracked term — `verify: automated  evidence: integration`
  (T-11 extends `test-metrics-trend.py`, which T-10 registers in INTEGRATION_SCRIPTS: kind matches).
- Two residual holes, both small: (a) SC-17's **aggregate** clause is asserted in
  `test-metrics-kpi.py`, a **unit** script, so that clause's declared evidence kind is wrong;
  (b) **T-06** lists a per-feature `touchpoints` field but never says what it holds before T-11
  wires `count()` — only T-06's general contract paragraph forbids a 0 there.

## 3. DEC-4 / PF-7408d83a — the chart is actually mounted: **DELIVERED, with two green-with-nothing paths**

- **T-21** wires `charts.tsx` into `panels.tsx` and its verify **executes a render** —
  `npm run test` → `vitest run` (script pinned and asserted by T-04's verify), `getByTestId`
  over the real components, exit status checked by the `out="$(...)" &&` form. Prerequisites are
  **planned, not assumed**: toolchain (vitest, jsdom, @testing-library/react, `vitest.config.ts`,
  ResizeObserver stub) in **T-04**; the `test-metrics-client-render.py` detect literal in **T-03**;
  INTEGRATION_SCRIPTS registration + `npm ci` CI step in **T-22**, with NO SOFT SKIP. No dependency
  cycle: T-21←(T-14,T-15), T-22←(T-03,T-21); full 22-node graph is acyclic.
- **Hole A — a skipped test greens the gate.** Both T-21's verify and T-22's script assert only
  "label appears in output" + exit 0. `test.skip("grading panel mounts…")` prints the label under
  `--reporter=verbose` and exits 0 [INFERENCE: vitest verbose lists skipped names]. Fix: assert a
  pass marker or count, or `--reporter=json`.
- **Hole B — the testid is not the chart.** A literal `<div data-testid="chart-shape-a"/>` in
  `panels.tsx` (or a stub export in `charts.tsx`) satisfies both cases. The intent forbids it; the
  assertion does not. Fix: also assert a chart-internal artifact inside that subtree (an `svg`, or
  T-15's five fixed grade categories / `strokeDasharray` output).
- **No SC covers it.** PF-328f8f3c got SC-17; PF-7408d83a got no criterion, so the only executing
  rendered-surface gate in the feature is ungraded at goal-check.

## 4. Did the fixes break something previously consistent? **YES — three items, one blocking**

- **BLOCKING — CI cannot run this feature's own integration suite.** `.github/workflows/tests.yml`
  installs only `pyyaml jsonschema` (:67-68) and runs `run-unit-tests.sh --kind integration` as a
  required check (:89-92). T-12 registers `test-metrics-dashboard.py` there and its positive cases
  need Flask importable. plan.yaml:1215 decided "no task touches harness-init or tests.yml for
  Flask" — correct for the *platform prerequisite* question, wrong for CI: the required check goes
  red every run. The grilling's own words were "explicit, in a prerequisite gate **/ CI**"
  (grilling:22-24). Needs one `pip install flask` step in that job (T-22's lane).
- **T-16 asserts a now-false claim**: "a user of any onboarded project needs python3 and nothing
  else" (plan.yaml:924).
- **T-17 documents the wrong prerequisites**: "python3, PyYAML, jsonschema, an onboarded
  harness.json, and the committed bundle" (plan.yaml:960-961) — **Flask missing**, and
  `jsonschema` present although T-12 explicitly forbids gating on it (plan.yaml:743-745). T-17's
  verify greps none of these, so wrong docs ship green against REQ-14.
- **BRIEF verification gap now false**: BRIEF:133-136 says React component behaviour is "unproven
  by any gate" — T-21/T-22 install an executing render gate under the `integration` kind.
- Checked clean: no cycle; SC-17 present in both directions of the coverage table (REQ-06, REQ-11
  rows and the SC→REQ column, BRIEF:230/235/241); T-11's `traces` REQ-06+REQ-11 both covered;
  **D-21 contradicts neither D-16, D-18 nor D-19** (it extends `record()` with a write-once epoch
  and supplies the touchpoints branch D-19's contract demands); REQ-01/REQ-02's "no manual build
  step" is untouched — the committed `dist` (D-04/T-16) is what that clause is about and the Flask
  install is a REQ-14 prerequisite, gated loudly; nothing in the plan now relies on a
  `ThreadingHTTPServer`-only behaviour (D-05's unbounded-thread rationale was carried over to
  werkzeug `threaded=True`, plan.yaml:725-733).

## Open questions

- **Q1 (med, new):** nothing commits or asserts the durability of `.harness/metrics/instrumented_at`.
  It is created at runtime inside a worktree (DEC-95) and no task lists it; if it is lost with the
  worktree and recreated later, the branch-3/branch-4 boundary silently moves and previously
  tracked features flip to "not tracked". `trend.jsonl` has SC-09 for exactly this; the epoch has
  nothing.
- **Q2 (med, carried, unruled):** grilling KPI 1 says "cycle time from **BRIEF** approval to ship"
  (grilling:26) and REQ-03 repeats it; D-14/T-06/D-21 all measure from `plan.yaml approval.date`.
  Raised as F2 in `notes/research-FEAT-53-goalcheck-plan-c1.md`; it was not among DEC-1..DEC-5 and
  is still unresolved at signature.
- **Q3 (low):** `panel.readers` lists two readers (`should-not-exist`, `scope`) against 8 findings —
  consistent with the transcribed digest, flagged only so a reviewer does not read it as truncation.
- **Q4 (known, one line):** the ~205-line trailing comment block `plan-merge.py apply` carried into
  `plan.yaml` before `panel:` is the already-raised harness defect (pm Q1), routed separately.
- DESIGN.md's touchpoint aggregate was deliberately not opened (concurrent write this wave).

---

## Cycle-2 closure re-grade — 2026-09-01, loop-back 2 (same pm persona, plan cycle 3)

**Everything above is the record of what FAILED at cycle 2 and stands unedited.** This section
re-grades each blocking item against the plan as it is now. Verdict flips **FAIL -> PASS on the
five items routed back**; two items were routed elsewhere and are unchanged here by design.

| item (as graded above) | was | now | what closed it |
|---|---|---|---|
| §4 CI cannot run the integration kind (blocking) | FAIL | **closed** | T-22 intent now adds `flask` to `tests.yml`'s pip step (or one beside it), naming WHY — the integration context is a required check and it runs T-12's script — and states that this is a claim about THIS repo's test job, not a ninth platform prerequisite |
| §4 T-16 asserts "python3 and nothing else" | FAIL | **closed** | T-16 intent now says: no node toolchain and no build step, only python3, PyYAML and Flask, gated by `serve.py --check`; and forbids restating the old sentence, naming it false since D-03 |
| §4 T-17 documents the wrong prerequisites, verify greps none of them | FAIL | **closed** | T-17 intent lists the five gate checks with Flask, and forbids listing `jsonschema` with T-12's reason; T-17 verify now pins `Flask`, `PyYAML`, `python3 -m pip install flask`, `harness.json`, `client/dist/index.html`. Proven discriminating: a METRICS.md fixture without Flask exits 1 `missing Flask`; the same file with it exits 0 |
| §3 hole A — a skipped case greens the gate | FAIL | **closed** | T-21 verify drives `--reporter=json` and requires each label to be carried by an `assertionResults` entry with `status == "passed"`. Proven on the verbatim snippet over seven synthetic reporter payloads: both-passed 0, npm-preamble 0, describe-prefixed 0, skipped 1, pending 1, failed 1, absent 1 |
| §3 hole B — the testid is not the chart | FAIL | **closed** | each case now also asserts INSIDE the subtree: Shape A an `svg` plus the five fixed grade categories each as its own element's text (T-15's fixed five-category domain, one bin label per bin); Shape B an `svg`, >= 2 path descendants for the fixture's two contiguous runs (T-15's one-line-per-run), and the direct end-of-line series label. Both reds must be DEMONSTRATED — unimported module, then a testid-only placeholder |
| §3 no SC covers the mount gate | FAIL | **closed** | BRIEF **SC-18**, `verify: automated  evidence: integration` — integration, not unit, because T-22 registers the script in `INTEGRATION_SCRIPTS` (declaring it `unit` would have reproduced PF-d2fc9563). Coverage table updated in both directions (REQ-07, REQ-12) |
| §4 BRIEF gap says React behaviour is unproven by any gate | FAIL | **closed** | BRIEF `## Verification gaps` now says component behaviour is *partly* proven, names the T-21/T-22 gate and its kind, and bounds it: two chart mounts and their own output, no browser, no typecheck, no interaction. The standing runner gap is still recorded as a dev-ops backlog task |
| Q1 epoch durability (med, new) | open | **closed as recorded accepted risk** | D-21 `because:` now records that nothing commits `.harness/metrics/instrumented_at` and no task can — `check-domain.sh --resolve` answers NOBODY for that path — and names exactly what moves if it is lost: features starting before the new epoch flip from branch 4 to branch 3 and report unavailable-never-tracked instead of a measured count. That is loss in the SAFE direction; a fabricated zero would need the epoch lost while a feature's own `touchpoints.jsonl` survived with a start after the new epoch, and a worktree reclamation takes both together. T-11's branch-1 case pins the post-loss state |

**Not closed here, and deliberately so.** Q2 above (grilling line 26 measures cycle time from
**BRIEF** approval; D-14/T-06/D-21 measure from `plan.yaml approval.date`) is an operator
decision, raised as F2 at cycle 1 and still unruled — it goes up with the signature request and
nothing in the plan was quietly reworded to hide it. `STATE.md:17`'s stale stdlib-server line is
the orchestrator's. DESIGN.md's touchpoint tile was the visual designer's, in parallel. The
~205-line trailing comment block that `plan-merge.py apply` left in `plan.yaml` is the already-
raised harness defect; this cycle used `amend` only, which splices one field block and adds no
comments, so nothing was added to it.

**One residual assumption, stated rather than buried.** The verify's per-case status check
depends on vitest's `json` reporter emitting jest-shaped `testResults[].assertionResults[]` with
`status` and `fullName` [INFERENCE — proven against synthetic payloads of that shape, not against
the pinned vitest, which is not installed until T-04]. T-21's intent therefore instructs the
implementer to STOP and report if the pinned vitest does not emit that reporter, rather than
falling back to a label grep.

## Final verdict — does this plan deliver the operator's stated intent?

**YES, subject to the signature decisions the plan itself raises.** All three DEC-1/DEC-4
rulings are delivered (unchanged from the grades above), the three false downstream statements
the Flask fix left are corrected, the render gate can no longer go green with nothing mounted or
with a placeholder mounted, the only executing rendered-surface gate in the feature now carries a
success criterion, and the epoch's durability has an explicit answer instead of silence. What
remains for the operator is what was always theirs: D-08 (the alpha charting library), D-20 (the
client build vs a server-rendered surface), and the unruled cycle-time origin above.

