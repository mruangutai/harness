# Grilling — self-visibility metrics dashboard — 2026-09-01

## Destination

A live, interactive web dashboard — a new general capability shipped as part of Harness (any
onboarded project gets it, not bespoke to this meta-repo) — that computes six self-visibility KPIs
from a project's own `.harness/` data and serves them through a real web framework (backend +
frontend), a deliberate break from the existing static-HTML-render convention. Reaching the end
looks like an approved `BRIEF.md` with `REQ-NN`/`SC-NN` for this feature, ready to hand to
`/harness-plan`.

## Settled

- Purpose → self-visibility for the user. Not a go/no-go investment gate (that was the pilot's old
  SC-1..SC-5 role) and not primarily cross-project comparison.
- Delivered as a full feature through the normal harness process (BRIEF → PLAN → build → review →
  QA → ship), not a quick script.
- Scope → general capability: ships as part of the Harness distribution, usable by any onboarded
  project against its own `.harness/` data.
- Architecture → a live interactive server, explicitly NOT the `render-brief.py` static-HTML
  convention. Chosen after being told that convention exists and is the only precedent in this repo.
- Dependency posture → a real web framework (backend + a JS charting lib) is justified for this
  feature. pm/eng-lead record that justification the same way DEC-190 justified `jsonschema`
  (explicit, in a prerequisite gate / CI, not silently assumed).
- KPI set (six):
  1. **Throughput** — cycle time from BRIEF approval to ship, plus run count/size per feature (the
     gap FEAT-08 D-06 identified and filed to backlog, never built).
  2. **Rework/stability** — `cycles_used / max_total_cycles` ratio per feature, aggregated across
     features.
  3. **Escaped defects** — post-ship bugs/reverts/hotfixes the four gate artifacts should have
     caught, as an ongoing measurement (generalizing SC-4's one-time kaya-ai method).
  4. **Autonomy** — blocking human touchpoints per feature (SC-2's never-instrumented target).
  5. **Code-grading average** — reported as a **distribution** (% of graded functions at/above bar,
     plus a named list of grade-1/grade-2 outliers), never a bare mean. Computed via
     `code-grade.py`'s existing whole-repo mode (`paths=<all tracked .py files>`, no diff). Explicitly
     caveated as Python-only in the UI — the .py/.sh/.ts ratio must be computed live per project, not
     hardcoded from this repo's measurement.
  6. **Usage by "model provider"** — *nice to have*. Ships as "by agent / model tier" (e.g. sonnet vs
     opus), since every agent in this org is pinned to one provider today (DEC-155) and a literal
     provider grouping has nothing to discriminate on yet. Relabels as true cross-provider only once a
     host project configures heterogeneous providers per agent. Requires resolving the commit
     `[harness:<step-id>]` prefix → that step's `execution_agent` (from the owning PLAN task) → that
     agent's pinned `model:` — a real join, scoped as its own task, not assumed free.
- Not reviving a dollar-cost meter: DEC-178 removed the previous one because it structurally
  couldn't see main-session work. Nothing in this feature reintroduces a spend-based metric without
  first fixing that blind spot — out of scope here.
- **Storage: no new database, no cache, at launch.** Four of six KPIs (rework ratio, run
  count/size/branch/PR, code-grading distribution, escaped defects, agent/model attribution) are
  computed on request directly from existing sources — `feature.json`, git log, and a live
  `code-grade.py` run — with no new storage at all. Measured at this repo's current scale: reading
  all 50 `feature.json` files takes 0.039s, a full git-log scan takes 0.034s, and a whole-repo
  `code-grade.py` run takes ~1.04s — roughly **1.1s total**, not the 15-minute worry that prompted
  the question.
- **Trend data (cycle time, touchpoints, code-grading over time) lands in a new append-only
  `.harness/metrics/trend.jsonl`, one JSON line written by the orchestrator at each ship** — never
  a recomputed history. The one operation that WOULD be slow — re-running `code-grade.py` against
  every historical commit to build a trend (≈967 commits × ~1s ≈ 16 minutes at this repo's current
  history) — is explicitly avoided. The trend starts the day this ships; features shipped earlier
  have no line, which is an honest gap, not fabricated backfill.
- **`trend.jsonl`, not new `feature.json` fields**, because `feature.json`'s key set is closed and
  CI-enforced (DEC-191, `additionalProperties: false`) — extending it needs a schema-version bump
  and a migration across 50 existing files for data that is project-wide, not a property of any one
  feature. A dedicated file avoids reopening that schema.
- **Database reconsidered and explicitly deferred, not rejected.** The blocking constraint: features
  build in separate git worktrees (DEC-95) and a durable trend record must survive worktree
  reclamation, so it must be git-committed — and a binary database file cannot be 3-way merged by
  git the way `trend.jsonl`'s pure line-appends can, so two features shipping concurrently from
  different worktrees would silently lose one side's row on merge. Plain-text JSONL avoids that
  hazard the same way every other durable harness artifact (`feature.json`, `logs/<date>.md`,
  `plan.yaml`) already does. If interactive querying over `trend.jsonl` ever gets slow, the lever is
  a **derived, gitignored, rebuildable SQLite cache** the live server builds from `trend.jsonl` on
  read — never the source of truth — same "DERIVED, NEVER AUTHORED" relationship `render-brief.py`
  already has to its markdown source. Not built now; flagged for pm/eng-lead if scale ever demands
  it.

- Frontend framework → **React**, with **TanStack** libraries (data fetching/routing) for the
  client. UI substrate stays **Astryx** (`@astryxdesign/core`, already pinned in
  `team-config.yaml:93-99`) — no second-substrate deviation needed.
- Charting → **TanStack Charts**, chosen with the alpha status named above known and accepted —
  not a silent default. pm records this as the PLAN Decision itself (library + the alpha-vs-stable
  tradeoff against React Charts), since the choice is now made; eng-lead's architecture review
  checks at PLAN time whether TanStack Charts' current alpha API actually covers this feature's
  chart needs (distribution histograms, time-series trend lines) before build starts, and names a
  fallback path to React Charts if it doesn't.

## Not yet specified

- Exact backend framework choice and how its addition is justified/gated — a DEC-190-style
  prerequisite check, or something new.
- Hosting/access model: local-only bound to localhost per project (consistent with Harness's
  single-checkout pattern, DEC-193) vs. anything network-exposed. Not asked of the user yet.
- Trigger/refresh: on-demand start via a command (this repo's own convention is the supervised
  background-job mechanism, per `AGENTS.md`) vs. auto-started at a lifecycle point; whether KPIs
  recompute per page load or need a background refresh job.
- Where the escaped-defect signal is sourced per project — this repo's own git history, or does it
  need a per-project mining convention like DEC-96's kaya-ai analysis (reverts, hotfix commits,
  `fix:` following a feature)? Needs research, not assumed.
- Exact commit-prefix → step-id → `execution_agent` → model join mechanics for KPI 6.
- Where the dashboard's entry point lives in the distributed skill/bin tree, and whether it needs a
  new slash command.
- Exact `trend.jsonl` line schema (field names/types for `feature_id`, ship timestamp, cycle-time
  start point, touchpoint count, code-grade distribution) and exactly how the orchestrator sources
  "when this feature's BRIEF was approved" — its own runtime knowledge of the flow, or a read of
  `logs/<date>.md` — since no structured approval timestamp exists anywhere today.
- How blocking touchpoints are actually counted at the moment they happen (which routing/escalation
  event increments the counter, and where that running count lives until ship writes the final
  line) — `logs/<date>.md` is prose, not a counter, so this needs a real mechanism, not a parse.

## Out of scope

- Reviving dollar/cost metering (DEC-178). Any future cost metric is its own decision addressing the
  main-session blind spot first.
- True cross-model-provider aggregation until an org actually configures heterogeneous providers.
- Cross-project comparison as a primary use case — self-visibility per project is the driver; nothing
  here should require multiple projects reporting to one place.
- Shell (`.sh`) and TypeScript (`.ts`) code grading — the grader doesn't support them; not this
  feature's job to add that.

## Facts I verified (so pm does not re-derive them)

- `code-grade.py` already supports whole-repo grading via bare `paths...` args, no diff required —
  `.claude/skills/harness/bin/code-grade.py:134-142`.
- Repo file mix at HEAD: 107 tracked `.py`, 12 `.sh`, 3 `.ts` (`git ls-files`).
- All 16 agent definitions in `.claude/agents/*.md` pin `model: sonnet` or `model: opus` —
  Anthropic only, no other provider configured anywhere in this org.
- `commit_attribution` (`.harness/harness.json:156-159`) tags agent commits `[harness:<step-id>]`,
  human commits `[harness:human]` — step-id, not agent name or model.
- DEC-178: cost tracking (meter, budgets, invariant, reporting) removed entirely because "the meter
  never saw main-session work"; historical `cost_usd` values are the only surviving record.
- DEC-96/97: base escaped-defect rate measured once from kaya-ai history — 0.44 defects/feature (19
  escaped-defect PRs / 43 feature units / 470 commits), ~79% catchable by the four gate artifacts —
  a one-time historical study, not a live metric.
- `BUILD.md` item 11, "batch human touchpoints to two," is recorded `pending` — never shipped as an
  ongoing measurement.
- FEAT-08 D-06 named the run-count/size gap explicitly and filed it to backlog, unbuilt: "cycles_used
  counts rework loops only... a healthy 16-run feature and a healthy 4-run feature both report the
  same number."
- No existing web-app infrastructure anywhere in the repo: no `package.json`, no JS UI framework —
  only the `render-brief.py`-family static-HTML-from-markdown renderers used for ship-review
  briefings.
