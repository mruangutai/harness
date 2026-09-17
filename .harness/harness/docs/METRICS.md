# Metrics dashboard operations

Start the local dashboard from an onboarded project's checkout:

```sh
python3 .agents/skills/harness/bin/dashboard/serve.py
```

It resolves the project root from the current checkout's git root, binds only to `127.0.0.1`, and serves on port `8971`. Use `--root <project>` to select another onboarded project, `--port <n>` to change the port, or `--check` to run the prerequisite gate without binding a port or serving. A busy selected port is a startup error. See `.claude/skills/harness/bin/dashboard/serve.py:275-316`.

## Prerequisite gate

The gate checks exactly these five prerequisites before serving:

1. Python 3.10 or newer.
2. PyYAML, installed with `python3 -m pip install pyyaml`.
3. Flask, installed with `python3 -m pip install flask`.
4. The selected project's `.harness/harness.json`.
5. The committed dashboard bundle at `.claude/skills/harness/bin/dashboard/client/dist/index.html`.

Flask is dashboard-only, not a Harness platform prerequisite. `jsonschema` is not part of this dashboard gate (`dashboard/serve.py:31-55`).

## What the dashboard shows

The windows are `30d`, `90d`, and `all`. The seven KPIs are **Throughput**, **Rework**, **Blocking Human Touchpoints**, **Escaped Defects**, **Code Grading**, **Usage by Agent / Model Tier**, and **Merged PRs Over Time** (`dashboard/client/src/tiles.tsx:9-23`). The payload states these sourcing rules verbatim:

- BUG-NN feature units first added in the selected window and Revert commits are counted; subjects beginning with fix are excluded because they are usually within-feature repairs.
- code-grade.py whole-repo mode supplies each record's bar.
- Weekly counts are shipped features read from the durable ship record; each shipped feature represents one merged PR under DEC-200; nullable pr fields do not affect the count.

Viewing is read-only. Requests compute from local files and local git history but do not append metrics. The sole trend write happens at the user-gated ship step: it appends and commits one record to `.harness/metrics/trend.jsonl` (`dashboard/trend.py:16-29,78-111`; `gh-sync.py:2161-2164`). The trend begins with the first ship after this capability landed; earlier history is never backfilled (`dashboard/client/src/gapstates.tsx:19-20`).

The work list lives on `/`.
Feature and bug detail lives at `/work/$id`.
No standalone `/work` route is registered.

KPI detail lives at `/kpi/$n`; those three product routes are registered in `dashboard/client/src/routes.tsx:84-88`.

## Work status and sources

Status rank is `needs-you` > `blocked` > `stalled` > `over-budget` > `running` > `stale`; the first applicable label wins (`dashboard/attention.py:15,52-61,122-135`).

- `needs-you`: an open grilling note, a run awaiting the operator, an open question in `STATE.md`, or pending plan approval.
- `blocked`: the current run state is blocked.
- `stalled`: the current run is running and the newest `STATE.md` or run-state write is at least 45 minutes old.
- `over-budget`: remaining rework cycles are at or below the configured boundary.
- `running`: the current run is running and has not crossed the stalled threshold.
- `stale`: a non-terminal feature or bug with no governed-file write for at least seven days and no higher-ranked status.

Thresholds live in the `dashboard` block of `.harness/harness.json`: `stalled_minutes` is `45`, `stale_days` is `7`, and `over_budget_remaining_cycles` is `1`. Thus over-budget begins when `max_total_cycles - cycles_used <= 1` (`dashboard/attention.py:38-49,92-118,150-153`).

Feature and bug rows come from local `.harness/<segment>/features/*` files; grilling rows come from local `.harness/notes/grilling-*.md`; linked-worktree rows come from local git worktree metadata. A readable matching linked worktree wins over the main feature directory; otherwise the main copy is used. Each row exposes `source_path`, `main_path`, and `worktree_path` so the selected copy is explicit (`dashboard/work.py:59-95,139-196,365-385`). Malformed or unreadable sources remain visible with their path and reason rather than disappearing (`dashboard/serve.py:190-235`). The operational data view performs no GitHub read and no network read.

Use the **Refresh** button to re-read disk and git metadata; there is no background watcher (`dashboard/client/src/work-view.tsx:16-24`).
