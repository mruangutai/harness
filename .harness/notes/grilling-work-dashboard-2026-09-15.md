# Grilling — fleet-wide work dashboard (operational view, as a FEAT-53 amendment) — 2026-09-15

## Destination

FEAT-53-metrics-dashboard, amended in place, gains an attention-ranked **operational view** of every
unit of Harness work across the fleet — FEAT and BUG features, grilling sessions, worktrees —
alongside its six KPIs, on the one server and client shell FEAT-53 already plans. Reaching the
end: `dashboard/serve.py` starts, the operator opens it, and the attention view is complete and
truthful against disk, including features whose live state exists only in a worktree. The
amended plan is signed once, under FEAT-53's existing DEC-75 bundled prototype-and-plan approval.

## Mission

mission: plan
reason: new public surface (fleet collector + API routes + view), new schema surfaces (grilling
front-matter, `dashboard:` config block); executed as an amendment to FEAT-53's plan.yaml
(station `plan`, approval pending), not a new feature.
confirmed-by: operator — overriding my recommendation to invert (new feature takes FEAT-53's
infrastructure tasks and ships first; FEAT-53 shrinks to KPIs). Operator ruled: extend FEAT-53 in
place with roughly six operational-view tasks.

## Settled

- Purpose → an attention-ranked operational view: "what needs me, what is running, what is
  stalled/stale, what is over budget" across the fleet. Not a KPI dashboard; not a replacement for
  the GitHub board, which stays a write-only mirror.
- Scope of work items → (1) every `features/<id>/` under every `.harness/<segment>/`, kind derived
  from the id prefix (`FEAT` / `BUG`); (2) grilling sessions (`notes/grilling-*.md`); (3) worktrees
  themselves, so an orphaned or terminal-feature worktree (INV-29) is a visible row. Wayfinding
  efforts and board drift are **out of v1** (see Out of scope).
- Interface → FEAT-53's: React + TanStack Router/Query on Astryx (D-07, D-20), committed bundle
  (D-04), **Flask** WSGI app in `bin/dashboard/serve.py` (D-03). The stdlib-`http.server` answer
  given earlier in this sitting is withdrawn in favour of D-03 — extending in place inherits
  FEAT-53's operator-ruled decisions rather than re-litigating them.
- Relationship to KPIs → one feature, one signature. The operational view is added as its own lane
  in FEAT-53's plan so its tasks can build and be observed independently of the KPI tiles; both
  mount on the same shell (T-13) and server (T-12).
- FEAT-61 prototype → adopt the data layer, restart the interface. The uncommitted
  `harness-observe.py` (plan.yaml station + STATE.md `## Current` + feature.json budget +
  `feature-record.py spend` join, ATTN ranking) on the `FEAT-61-observe-dashboard` worktree seeds
  the collector. Its fixed-width table and the `plugins/harness-work-status/` Herdr plugin are
  discarded. The worktree is brought under this feature's governance or removed.
- Source of truth → **disk only**. The dashboard never contacts GitHub. All fleet members' feature
  state already lives centrally in this control plane (DEC-221), so fleet-wide = every segment.
- Live state precedence → the **worktree copy wins**, the main-checkout copy is the fallback, and
  the item records both paths. The collector enumerates `git worktree list` for the control plane
  and for every `workspace_root/<repo>` (DEC-193) and maps worktrees to feature dirs by id prefix
  (short `FEAT-32` and long `FEAT-32-slug` forms both occur today).
- Attention states, all derived from disk: `needs-you` (run `awaiting_user`, STATE.md open
  questions non-empty, plan approval unsigned, grilling note `open`), `blocked` (run `blocked`),
  `running`, `stalled` (running, no state write for **45 min** = `budgets.rework_round_minutes`),
  `stale` (non-terminal, untouched for **7 days**), `over-budget` (`cycles_used` at or near
  `max_total_cycles`). Thresholds live in a new `harness.json` `dashboard:` block.
- Grilling session status → YAML front-matter on the note, written by the grilling skill:
  `status: open | handed-off | abandoned`, `became: <FEAT-id>` filled when `/harness-plan` or
  `/harness-patch` starts from it. Enforced by the skill and a check-state invariant. The 46
  existing notes are backfilled by a one-shot script (default `handed-off` when a plan/BRIEF cites
  the path, else `abandoned`) with a manual review pass.
- Launch → FEAT-53's D-06/D-17: `python3 .agents/skills/harness/bin/dashboard/serve.py`, on
  demand, no slash command, no background job. Recompute per request (D-06). The `/harness-dashboard`
  command answer given earlier is withdrawn in favour of D-17. An mtime cache over collected files
  is permitted only if it does not contradict D-06/D-09 — pm decides.
- Fleet scope → widens FEAT-53 REQ-02's single-project `--root`: the collector scans every
  `.harness/<segment>/features/*` in the control plane plus their worktrees. KPIs keep their
  per-project resolution; only the operational view is fleet-wide.
- Access → bind `127.0.0.1` only, no auth — FEAT-53 D-05, unchanged.
- Frontend toolchain → FEAT-53 T-04/T-16 already own this; no new decision.
- Composition (settled 2026-09-15, after the plan amendment; supersedes the first composition
  round in this sitting; input to the DESIGN.md amendment and to BRIEF perspectives):
  - **One perspective and definition of done per route** in the BRIEF (`## Done when — by
    perspective`, DEC-231), each discharged by an SC with a `verify:`.
  - Routes, exactly four; `/features`, `/features/$featureId` and any `/kpis` page are retired:
    - `/` — **Overview**: header (window selector + **repo dropdown**, both URL params, default
      `all`, applied on every route); attention strip (counts per state in D-25 order, each linking
      to `/work?attention=<state>`); the **needs-you** rows; the seven **repo-level** KPI tiles as
      designed. One screen at 1440.
    - `/kpi/$n` — one KPI's panel (chart/table as designed), reached from its tile. Row → `/work/$id`.
    - `/work` — every item (FEAT, BUG, grilling, worktree). Filters: status/station, attention,
      kind, repo — "waiting on me" is `attention=needs-you`. Columns: id · repo · station and
      phase · attention + reasons · elapsed (total and by phase, in-progress shows so-far) · runs ·
      cycles/max · tokens (null-aware). Three layouts prototyped for comparison before one is
      chosen — (a) grouped list in attention order, (b) kanban by station with attention badges,
      (c) flat sortable filterable table.
    - `/work/$id` — one item, id carries the kind (`/work/FEAT-53`, `/work/BUG-285`): operational
      header first (station, phase, run, attention, both paths, budget, elapsed by phase, tokens),
      then that feature's **per-feature** KPIs (the former `/features/$featureId` content).
      Grilling and worktree rows have no page and expand inline on `/work`.
  - KPIs at two levels: repo-level on `/` (sliced by the repo dropdown), per-feature on `/work/$id`.
  - SC-11's drill becomes tile → `/kpi/$n` → row → `/work/$id`: still three routes, no restart.
- Phases for elapsed time → `plan → build → validate` from the existing seam handoffs (DEC-159)
  plus run `started_at`/`ended_at`; total runs from BRIEF approval date to ship or now. Stations
  are not timestamped and are not the phase model.
- Tokens → **instrumented in this feature**: the orchestrator measures tokens at run-end from the
  host transcript and `feature-record.py run-end` records them (DEC-227's measured path, today
  never exercised — 0 of 1336 runs carry a value). The dashboard sums per item and per phase,
  null-aware: "unmeasured n of m runs" beside the total, never a 0 (D-19). Totals start the day it
  lands; no backfill.
- Cost → **tokens only, no dollars** in this feature. DEC-178 stays struck; a dollar figure is its
  own later decision once tokens are real and the main-session blind spot has an answer.

Facts for this round: across `.harness/*/features/*/feature.json` at f5ffdcf4 — 82 features,
1336 runs, **0 runs with `tokens`**, 35 runs with both `started_at` and `ended_at`.

- Prototype review rulings (operator, 2026-09-16, against the rebuilt T-05 prototype):
  - **One screen.** `/` is the single dashboard: header · attention strip · **Repository KPIs**
    (first section) · the work list. The separate `/work` route and the "Work" header toggle are
    retired; the Repository dropdown (top right) is the only repo selector. `/kpi/$n` and
    `/work/$id` remain as drills. Amends D-29/D-30.
  - Work list layouts: **Kanban and Table only** (grouped list dropped); toggle labels "Kanban",
    "Table" — no letter prefixes; active state without the white border.
  - Column "Attention + reasons" → **"Status"**; the filter "Attention" → "Status". The redundant
    Repository filter beside Kind is removed.
  - No colour-on-text or coloured borders/top-lines for status in the table: **Astryx icons** carry
    the state. Attention cards: neutral (white) border; state colour on the label text only.
  - Casing: every title, card label, dropdown item and toggle label is capitalised consistently
    (Title Case for labels; sentence case for descriptions).
  - Focus rings: no visible outline after mouse interaction on any surface (page title, dropdown
    selection, toggle). Keyboard focus stays visible (`:focus-visible`) — C-3 is unchanged.
  - Content width: constrained and centred per desktop dashboard practice (max-width container),
    not full-bleed.
  - Sparklines: keep the 14-day daily horizon (C-1); strip spans the tile's full width.
  - The "Honest-state gallery" leaves the dashboard; the C-4 simultaneous-visibility gate is met by
    a fixture-only route in the prototype, never a product surface.

## Not yet specified

- The JSON API shape and how much of it the later KPI feature will reuse — sharp enough for pm
  to specify, listed here so the KPI feature's needs (per-feature runs, cycles, approval date) are
  visible when the collector's output is designed.
- Whether `running` can be told apart from "process died" other than by the 45-minute stall
  heuristic — disk carries no liveness signal today.
- How the `dashboard:` block is validated (harness.json schema is versioned; a `schema_version`
  bump may be needed).

## Out of scope

- GitHub reads of any kind (operator ruled disk-only). Consequently: board drift and tracker-mode
  wayfinding efforts are **not in v1** — `board_lifecycle.py audit` records nothing locally and
  `wayfind.py` keeps all ticket state in GitHub, so neither is visible from disk. Each needs its
  own local receipt first; both were offered and declined for v1.
- Nothing about the six KPIs, `trend.jsonl`, touchpoints or charting changes — FEAT-53's
  D-10..D-16, D-18, D-21..D-23 stand as ruled.
- Dollar cost (DEC-178). Fixing the GitHub board itself (issue #61 measured its limits).
- Network exposure or multi-user access.

## Facts I verified (so pm does not re-derive them)

- Station vocabulary is `factory_config.MANDATED_STATIONS` (`backlog, plan, ready, building,
  review, done`) plus `TERMINAL_MARKER = 'abandoned'` — `.claude/skills/harness/bin/factory_config.py:44,51`, at f5ffdcf4.
- `feature.json` is schema-closed (`additionalProperties: false`, DEC-191) with no status key;
  station lives in `plan.yaml` top-level `status:`; run state in `runs/<run>/state.yaml` with
  status `running|awaiting_user|blocked|complete|failed` (SPEC.md:2053-2059).
- No cross-repo aggregation exists: every reader globs `.harness/*/features/*` in one checkout;
  `board_lifecycle._status_findings` self-skips foreign repos.
- Worktree-only state is a measured defect: `feature_schema.py:216-236` carries two hand-written
  exemptions caused by it. Running the FEAT-61 prototype against main at f5ffdcf4 rendered 12 of
  18 rows with `unknown` station or status.
- FEAT-61 worktree: branch at f5ffdcf4 with three untracked files (`harness-observe.py`,
  `plugins/`, `tests/unit/test-harness-observe.py`); no BRIEF/plan.yaml/feature.json for FEAT-61
  anywhere. GitHub issue #61 is an unrelated closed wayfinder research ticket.
- 46 `grilling-*.md` notes exist in `.harness/notes/`; none has front-matter or a status field.
- `board_lifecycle.py audit` prints findings and writes nothing; `wayfind.py` refuses in
  markdown mode and persists nothing locally in tracker mode (`wayfind.py:58-59`).
- Fleet: `.harness/factory/fleet.yaml` lists `mruangutai/kaya-ai` and
  `mruangutai/harness-factory-smoke`; `mruangutai/harness` deliberately absent (DEC-174). 11
  worktrees registered on this control plane (`git worktree list`).
- Repo is Python 3 stdlib-first: only PyYAML (DEC-171) and jsonschema (DEC-190) are required; no
  `package.json`, no JS toolchain, no web server anywhere.
- The 2026-09-01 metrics grilling measured a full disk collect at ~1.1 s for 50 features.
- FEAT-53 at `feat/FEAT-53` worktree HEAD ab0c1501 (2026-09-03): station `plan`, approval
  `pending`, STATE.md `awaiting-user` — blocked on T-05 (rebuild + browser-observe the prototype)
  then a fresh panel read then one DEC-75 signature. 22 tasks, 23 decisions, 7 plan cycles. 27
  uncommitted files in the worktree, all under `notes/prototypes/` and `notes/mockups/`.
- FEAT-53 rulings this amendment inherits unchanged: D-03 Flask, D-04 committed bundle, D-05
  loopback/no auth, D-06 on-demand recompute, D-07 React/TanStack/Astryx, D-17 `serve.py` no
  slash command, D-19 null-plus-unavailable-sentence for anything uncomputable.
- Amendment path: FEAT-53's plan is real YAML at
  `.harness/harness/features/FEAT-53-metrics-dashboard/plan.yaml`; the plan-amend verb exists
  (BUG-1128-plan-amend-verb, station `review` on main).
