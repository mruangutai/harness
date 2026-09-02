# BRIEF — FEAT-53 Metrics dashboard

## Problem

The factory produces the data needed to judge itself and nobody can see it. Every feature's
`feature.json`, every commit, every gate artifact is on disk, but answering "is a feature getting
faster or slower to ship", "how much rework are we paying", "how often does a defect escape four
gates", or "how much of this is still a human unblocking things" requires a human to open ~50 files
and count by hand — so it is never answered, and the org steers on impressions. Two named gaps prove
the cost: FEAT-08 D-06 recorded that a healthy 16-run feature and a healthy 4-run feature report the
same `cycles_used` and filed it unbuilt; `BUILD.md` item 11 ("batch human touchpoints to two") is
recorded `pending` and was never instrumented, so the target has no measurement behind it.

## Goal

Any onboarded project gets a live, interactive dashboard that computes seven self-visibility KPIs from
that project's own `.harness/` data, git history and code grader, and serves them in a browser the
user can actually explore — feature by feature, and over time as it accrues. It is for the user's own
visibility into their factory, not an investment gate and not a cross-project leaderboard. It ships
as part of the Harness distribution; this repository is only its first consumer.

## Requirements

- REQ-01: A user can start the dashboard for a project and reach it through one documented entry
  point, with no hand-assembled URL, no manual build step and no per-project wiring.
- REQ-02: The dashboard reports on whichever onboarded project it is run against, reading that
  project's own `.harness/`, git history and code, with no code change per project and no value
  derived from the Harness repository leaking into another project's numbers.
- REQ-03: Throughput is visible per feature: elapsed time from BRIEF approval to ship, plus the run
  count and change size for that feature — the FEAT-08 D-06 gap.
- REQ-04: Rework is visible per feature and in aggregate as cycles consumed against cycles allowed.
- REQ-05: Escaped defects are visible as an ongoing measurement — post-ship defects attributable to
  shipped work — with the sourcing rule stated where the number is shown.
- REQ-06: Blocking human touchpoints are counted per feature. This obliges the counter to be
  incremented when a touchpoint happens; a count reconstructed later from prose is not a measurement.
- REQ-07: Code grading is reported as a distribution — the share of graded functions at or above bar,
  plus the named grade-1 and grade-2 outliers. A bare mean is not an acceptable presentation.
- REQ-08: The grading view states which languages it covers and what share of the viewed project's
  code is therefore ungraded, computed from that project at the moment it is viewed.
- REQ-09: Usage is attributable to the agent and model tier that produced the work, derived from the
  commit record rather than asserted.
- REQ-10: Trend over time for cycle time, touchpoints and code grade accrues from a durable record
  written at each ship, which survives reclamation of the worktree the feature was built in and
  survives two features shipping concurrently.
- REQ-11: Any KPI with no data for a feature or a period is shown as unavailable with the reason,
  never as zero, blank or an interpolation. Features shipped before this capability existed have no
  trend line and the UI says so.
- REQ-12: The user can change what is shown from the browser — choose a feature, choose a time
  window, drill from an aggregate to the features behind it — without editing a file, restarting the
  server or re-running a command.
- REQ-13: Viewing the dashboard does not mutate the project. It is read-only over `.harness/`, git
  and the grader; the only write anywhere in this feature is the append at ship (REQ-10).
- REQ-14: On a machine missing the dashboard's runtime prerequisites, starting it fails loudly,
  naming the missing prerequisite and how to install it. It never renders a partial page or a
  substitute number.
- REQ-15: Merged pull requests are visible over time, as a count for the window broken into weekly
  buckets, with the sourcing rule stated where the number is shown: that the count is of shipped
  features read from the durable ship record REQ-10 writes, and that one shipped feature is one
  merged PR because DEC-200 holds exactly one merged PR per shipped feature. A shipped feature whose
  record carries no `pr` still counts as one shipped feature and therefore one merged PR; a count of
  populated `pr` fields under-reports and is not an acceptable presentation. A week in which the
  record shows no ship is shown as unavailable with the reason naming that week, never as zero
  (REQ-11).

## Constraints

Settled by the user in `.harness/notes/grilling-metrics-dashboard-2026-09-01.md`; these are
decisions, not requirements — the requirements above survive changing every one of them.

- Architecture is a live interactive server (backend + frontend), a deliberate break from this
  repo's only precedent, the `render-brief.py` static-HTML-from-markdown family. No web-app
  infrastructure exists here today — no `package.json`, no JS framework.
- Frontend is React with TanStack libraries for data fetching and routing. Charting is TanStack
  Charts, chosen with its alpha status known and accepted; eng-lead checks at plan time that the
  current alpha API covers distribution histograms and time-series lines. **The fallback named at
  the grilling — npm `react-charts` — is dead**: last published 2023-11-02 with a React 16 peer,
  against this client's React 19 substrate, so it cannot install beside Astryx at all. The alpha
  was **accepted on 2026-09-01** (`notes/answers-2026-09-01-plan-signature.md`, DEC-3) with the
  rollback plan `D-08` now documents: the exact version pin plus the committed bundle, DESIGN
  C-2's in-place workaround wherever an unmet capability's `If absent` cell names one, and a
  `T-18` STOP wherever it reads hard requirement. No fallback library is named in advance,
  because none survives the React 19 substrate check today.
- **Disclosure, new since the grilling.** Plan review found that having a client build at all — the
  frontend framework, `package.json` and the committed bundle — was never weighed against a
  server-rendered HTML surface served off the same Python server, which would satisfy REQ-01 and
  REQ-12 too and would remove the entire alpha-charting risk. What the grilling rejected was the
  `render-brief.py` static-HTML-from-markdown convention, which is a different thing. Plan `D-20`
  writes that decision down, and it was **ruled on 2026-09-01** (same answers file, DEC-2): the
  client build is **kept**, and the server-rendered alternative stands recorded as weighed and
  rejected rather than as a question open at signature.
- UI substrate stays Astryx (`@astryxdesign/core`), already pinned at `team-config.yaml:93-99`. No
  second-substrate deviation. SUPPLIES.
- No new database and no cache at launch. Five of seven KPIs compute on request from `feature.json`,
  git log and a live `code-grade.py` run. The other two read an appended log rather than computing —
  blocking human touchpoints from `touchpoints.jsonl`, and merged PRs by week from
  `.harness/metrics/trend.jsonl` — and neither adds a data source. The grilling's ~1.1s observation is **superseded**: it
  predates the per-branch change-size work the plan specifies, and a per-item re-measurement on
  2026-09-01 puts the honest per-request total at 4.3–5.3s at current scale
  (`notes/receipt-harness-data-engineer-b-efficiency.md`), ~3.6s once the plan's single-call
  `git diff` and memoised plan reads land. The deferral still holds at that cost. A derived,
  gitignored, rebuildable SQLite cache is the named lever if querying ever gets slow — never the
  source of truth. Deferred, not rejected.
- Trend data appends one JSON line per ship to `.harness/metrics/trend.jsonl`, not new `feature.json`
  keys: DEC-191 closed that key set with `additionalProperties: false`, so extending it means a
  schema-version bump and a migration across ~50 files for data that is project-wide. BLOCKS the
  `feature.json` route; SUPPLIES the JSONL route. Plain-text line appends are also what makes two
  concurrent worktree ships (DEC-95) 3-way mergeable, which a binary DB file is not.
- History is never recomputed. Re-running `code-grade.py` over ~967 commits (≈16 min) is explicitly
  avoided; the trend starts the day this ships.
- KPI 5 reports a distribution plus named outliers, never a bare mean. Grading uses `code-grade.py`'s
  existing whole-repo mode (bare `paths...`, no diff) — `.claude/skills/harness/bin/code-grade.py:134-142`. SUPPLIES.
- KPI 6 ships labelled "by agent / model tier" (sonnet vs opus), not "by provider": every one of the
  16 agents is pinned to one Anthropic model (DEC-155), so a provider grouping has nothing to
  discriminate on. It relabels only once a host project configures heterogeneous providers.
- KPI 6's attribution rests on `commit_attribution` tagging agent commits `[harness:<step-id>]` and
  human commits `[harness:human]` (`harness.json` `commit_attribution`) — a step-id, not an agent or
  a model, so a real join is required. SUPPLIES the signal, BLOCKS any assumption it is free.
- The runtime dependencies are declared and gated the way DEC-190 gated `jsonschema` — an explicit
  prerequisite check with a loud failure, never a silent assumption or a quieter degraded mode.
- The backend is a real web framework — plan `D-03` settled **Flask** on 2026-09-01, with FastAPI +
  uvicorn, a Node server and a hand-written route table all rejected by name. It is a
  **dashboard-only** prerequisite, gated in the entry point's own REQ-14 check and nowhere else:
  no harness `bin/` script outside `bin/dashboard/` imports it, so it is deliberately **not** a
  ninth platform prerequisite beside PyYAML and `jsonschema`. SUPPLIES.
- Code authority stays inside DEC-193's two locations; nothing here introduces a third checkout.

## Out of scope

- Reviving dollar or cost metering. DEC-178 removed it because the meter structurally could not see
  main-session work; any future cost metric is its own decision that fixes that blind spot first.
- True cross-model-provider aggregation, until an org actually configures heterogeneous providers.
- Cross-project comparison as a primary use case. Nothing here may require multiple projects
  reporting to one place.
- Grading `.sh` and `.ts` code. The grader does not support them and teaching it is not this
  feature's job — REQ-08 exists to disclose that gap, not to close it.

## Verification gaps

Read against `test_kinds` in `.harness/harness.json`: `unit` and `integration` are the only kinds
with a runner. `component`, `ui`, `typecheck` and `eval` all ship `cmd: null`, status `unresolved`.

- `ui` has no runner: no browser-driver test can prove any rendered behaviour of this dashboard.
  Every rendered-surface claim is therefore carried by SC-02, SC-08 and SC-11 (uat, executed by the
  user) and by SC-15 (ui-reviewer inspection). Nothing about the browser experience is automatically
  proven, and no SC below claims otherwise.
- `component` and `typecheck` have no runner, and this feature introduces the first `.tsx` and
  `.ts` application code in the repo. TypeScript type soundness is therefore unproven by any gate.
  React component behaviour is **partly** proven, and this line was corrected on 2026-09-01: plan
  `T-21` and `T-22` install one executing render gate — vitest + jsdom + `@testing-library/react`,
  driven from `test-metrics-client-render.py`, registered in `INTEGRATION_SCRIPTS`, so it runs
  under the `integration` kind in CI — and SC-18 rests on it. What that gate does **not** cover is
  every other rendered behaviour: it asserts the three gated chart mounts — Shape A in the grading
  panel, Shape B in a trend panel, and Shape B in the merged-PR panel — and each of those charts'
  own output, and nothing else. No browser, no type checking, no interaction. The standing
  `component`/`typecheck` runner gap is still a dev-ops backlog task in its own right and this
  feature does not close it.
- SC-06's literal sweep cannot cover the bare-digit tokens `12` (the `.sh` count) and `3` (the
  `.ts` count): both occur inside values this feature legitimately ships. `12` occurs in
  `127.0.0.1` — `D-05`'s loopback-only bind, shipped in `serve.py` by `T-12` and required in
  `METRICS.md` by `T-17`'s verify — and in `122` itself, one of the mix literals the sweep hunts
  in its own right, so a bare-`12` sweep cannot tell a legitimate hit from the literal it is
  looking for. `3` occurs in the tile grid's own dimensions, the fixed `3x3` seven-tile grid
  (`T-05`, `T-14`), and in `python3`, the documented start command (`T-17`). So a literal grep
  for either cannot discriminate a seeded mix figure from an unrelated number. Those two are
  therefore **not machine-checked**; they are carried by SC-15's ui-reviewer inspection at
  `review_sha`.

## Success Criteria

- SC-01: Invoking the documented entry point on a clean checkout serves the KPI payload; with a
  runtime prerequisite absent, the same invocation exits non-zero naming that prerequisite and serves
  nothing. Both branches asserted separately.
  verify: automated        evidence: integration
- SC-02: A user runs the documented command on this repository and reaches a working dashboard in a
  browser, without being told anything the documentation does not say.
  verify: uat
- SC-03: Run against a fixture project directory carrying its own `.harness/` with features absent
  from this repository, every KPI in the payload reflects the fixture, and no figure equals this
  repository's value for the same KPI.
  verify: automated        evidence: integration
- SC-04: For a fixture with hand-labelled expected values, each of the six KPIs enumerated in this
  criterion — throughput, rework, escaped defects, touchpoints, grading distribution, agent/model
  usage — is asserted individually against the hand-labelled number, not against a second run of the
  same code. Six assertions, one per KPI named here, not one aggregate comparison.
  verify: automated        evidence: unit
- SC-05: The grading KPI's payload carries both the at-or-above-bar share and the named grade-1 and
  grade-2 outlier list; a payload carrying only a central tendency fails the assertion.
  verify: automated        evidence: unit
- SC-06: The ungraded-share figure changes when the fixture project's file mix changes, proving it is
  computed per project at view time; and neither of the two grep-discriminating literals of this
  repository's measured file mix — `107` (its `.py` count) and `122` (its tracked-file total) —
  appears anywhere in the dashboard's own shipped source, asserted over every tracked path under
  `bin/dashboard/` read at `review_sha` via `git show <review_sha>:<path>`, with the assertion
  demonstrated failing before it passes. See `## Verification gaps` for the two tokens no grep can
  discriminate.
  verify: automated        evidence: unit
- SC-07: For a feature with no ship record, every trend KPI in the payload is marked unavailable with
  a reason; no field carries 0, null-as-zero or a value interpolated from neighbouring features.
  Asserted per trend KPI.
  verify: automated        evidence: unit
- SC-08: A user viewing a feature that shipped before this capability existed sees stated absence of
  trend data, and is not shown a chart that reads as zero or flat.
  verify: uat
- SC-09: A ship appends exactly one record to the project's trend file with every prior byte
  unchanged; and two records appended in two separate worktrees both survive a git merge of those
  branches, neither silently dropped.
  verify: automated        evidence: integration
- SC-10: A simulated run in which two blocking human touchpoints occur reports two — the counter is
  incremented at each event and the shipped record carries the final count. A run with zero reports
  zero. The two-touchpoint case must be demonstrated failing before the mechanism exists.
  verify: automated        evidence: integration
- SC-11: From the browser the user selects a feature and a time window and drills from an aggregate
  to the per-feature rows behind it, with no server restart and no file edit.
  verify: uat
- SC-12: `git status` is byte-identical before and after serving every dashboard view against a clean
  project checkout — no file created, modified or deleted under `.harness/` or anywhere else.
  verify: automated        evidence: integration
- SC-13: The escaped-defect figure for a fixture git history equals the count a human labelled by the
  documented sourcing rule, and that rule is stated in the UI beside the number.
  verify: automated        evidence: unit
- SC-14: For a fixture whose commits carry step-ids resolving to agents pinned to two different model
  tiers, usage appears under both tiers; a commit whose step-id cannot be joined appears as
  explicitly unattributed rather than being dropped from the totals.
  verify: automated        evidence: unit
- SC-15: The dashboard's surface conforms to the DESIGN.md contract and uses the Astryx substrate
  rather than unstyled framework defaults; ui-reviewer cites `file:line` at `review_sha`.
  verify: inspection
- SC-16: A full KPI computation for this repository at its current scale completes inside the budget
  the plan pins, measured by the test rather than asserted, so the no-cache decision stays
  falsifiable. Baseline, re-measured per item on 2026-09-01 at 47 real feature branches, 106 tracked
  `.py` files and 978 commits: the honest per-request total is 4.3–5.3s
  (`notes/receipt-harness-data-engineer-b-efficiency.md`). The plan pins an **8.0s** ceiling and
  projects ~3.6s once T-06's single-call `git diff` and T-09's memoised plan reads land. The
  grilling's ~1.1s figure predates the per-branch change-size work T-06 specifies and is superseded.
  verify: automated        evidence: integration
- SC-17: The blocking-touchpoint count distinguishes tracked-and-genuinely-zero from never-tracked,
  asserted as two separate cases and never as one: for a fixture project carrying the
  instrumentation epoch, a feature whose start is **after** the epoch and whose `touchpoints.jsonl`
  is absent reports `0` with **no** entry in its `unavailable` map; a feature whose start is
  **before** the epoch reports `null` with the specific reason naming that touchpoints were never
  tracked for it, and is asserted to be neither `0` nor `"0"`. A fixture project carrying no epoch
  at all reports every feature as unavailable. The aggregate reports the not-tracked count by name,
  so no mean is taken over a fabricated zero.
  verify: automated        evidence: integration
- SC-18: The two chart shapes are actually mounted inside the panels that ship them, proven by an
  executing render rather than by source text: rendering the real grading panel, a real trend panel
  and the real merged-PR panel through `@testing-library/react` over a whole fixture payload puts
  each chart's element in the document, **and** that element's own subtree carries output only the
  chart component can produce — the five fixed grade categories inside the Shape A subtree, and one
  plotted line per contiguous run inside each Shape B subtree. All three cases are graded by *status*
  from a machine-readable reporter, so a skipped case fails the gate; and each is demonstrated
  failing first, against `charts.tsx` present-but-unimported and against a placeholder element
  carrying the testid alone.
  verify: automated        evidence: integration
- SC-19: For a fixture ship record spanning several weeks, the payload's weekly merged-PR series
  carries one bucket per week in the window in ascending order, matching the week count the payload
  itself returns; each bucket's value equals the hand-labelled count of shipped features whose ship
  date falls in that week; a fixture record carrying no `pr` is counted, so a series computed from
  populated `pr` fields alone fails the assertion; and a week with no ship record is `null` carrying
  the specific reason naming that week's date, asserted to be neither `0` nor `"0"`. Four
  assertions, not one aggregate comparison, and the empty-week case is demonstrated failing before
  it passes.
  verify: automated        evidence: integration
- SC-20: The merged-PR tile states its sourcing rule as persistent inline text beneath the figure —
  not a tooltip, not a footnote, not a link — naming that the count is of shipped features and that
  one shipped feature is one merged PR; and KPI 7 carries no per-feature column on the `/features`
  route and no presence on `/features/$featureId`. ui-reviewer cites `file:line` for each clause,
  reading the shipped source at `review_sha` via `git show <review_sha>:<path>`.
  verify: inspection

### Coverage — total in both directions

| REQ | covered by | SC | traces |
|---|---|---|---|
| REQ-01 | SC-01, SC-02, SC-15 | SC-01 | REQ-01, REQ-14 |
| REQ-02 | SC-03, SC-16 | SC-02 | REQ-01 |
| REQ-03 | SC-04 | SC-03 | REQ-02 |
| REQ-04 | SC-04 | SC-04 | REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-09 |
| REQ-05 | SC-04, SC-13 | SC-05 | REQ-07 |
| REQ-06 | SC-04, SC-10, SC-17 | SC-06 | REQ-08 |
| REQ-07 | SC-04, SC-05, SC-18 | SC-07 | REQ-11 |
| REQ-08 | SC-06 | SC-08 | REQ-11 |
| REQ-09 | SC-04, SC-14 | SC-09 | REQ-10 |
| REQ-10 | SC-09 | SC-10 | REQ-06 |
| REQ-11 | SC-07, SC-08, SC-17, SC-19 | SC-11 | REQ-12 |
| REQ-12 | SC-11, SC-15, SC-16, SC-18 | SC-12 | REQ-13 |
| REQ-13 | SC-12 | SC-13 | REQ-05 |
| REQ-14 | SC-01 | SC-14 | REQ-09 |
| REQ-15 | SC-19, SC-20 | SC-15 | REQ-01, REQ-12 |
|  |  | SC-16 | REQ-02, REQ-12 |
|  |  | SC-17 | REQ-06, REQ-11 |
|  |  | SC-18 | REQ-07, REQ-12 |
|  |  | SC-19 | REQ-11, REQ-15 |
|  |  | SC-20 | REQ-15 |

## Approval

status: approved
approved-by: operator (Mike Ruangutai), via main session
date: 2026-09-02
