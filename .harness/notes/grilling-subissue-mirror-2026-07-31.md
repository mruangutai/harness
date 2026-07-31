# Grilling — sub-issue mirror migration — 2026-07-31

## Destination

**Feature A: the mirror closes correctly, for both terminal states.** `close-task` closes exactly
one task; ship and abandon each have a path. Reaching it means the FEAT-03 "CLOSE-TASK HAZARD,
ELEVENFOLD" is structurally impossible rather than hand-guarded.

**Feature B (sequenced after A, separate BRIEF):** PLAN gains `depends_on:` per task; gh-sync emits
native `blocked_by` edges; check-state validates ordering; the lead's DAG is read from PLAN rather
than re-derived per run. Split from A because "done" genuinely differs, and because A fixes a live
defect that must not wait behind a pm-format change's review surface.

## Settled

- **Task unit** → one **sub-issue per `T-NN`** under one parent. Sub-issues are the unit of work;
  the parent is the deliberate container.
- **Parent origin, first match wins** → (1) the effort's wayfinding map issue, when that effort
  produced exactly this feature — **frozen at hand-off**: prune `## Not yet specified` and
  `## Out of scope`, add `Superseded by BRIEF.md at <sha>`, keep Destination + Decisions as the
  rationale above the tree; (2) the backlog issue pm absorbed (kaya's #48 pattern); (3) a fresh
  parent when there is nothing to absorb.
- **Parent title** → `FEAT-NN-<slug> — <human phrase>`, pm authoring the phrase from BRIEF's Goal.
  Same em-dash convention `T-NN` issues already use. Id stays the leading machine-matchable token.
- **`parent:` is recorded, never discovered** → written to `feature.yaml github.parent` at creation.
  `wayfind.py`'s `parent_of` is a READ and gh-sync must not use it (DEC-138).
- **Milestone stays** → it remains the definition of done (Problem + Goal + SC checklist). Verified
  an issue can be a sub-issue *and* carry a milestone, so both coexist with distinct jobs.
- **`absorbs:` stops closing** → `close-task` closes only the task's own sub-issue. Absorbed issues
  are surfaced in the **ship briefing's proposed-backlog section** — what the feature covered, what
  remains — and the mirror closes only what the user marks done at acceptance. Same briefing-gated
  route DEC-138 am.4 already uses for residual findings, for the same reason: work items change state
  through a human signature, never a script's inference.
- **Abandonment** → `cmd_abandon` closes the feature's own sub-issues `state_reason: not_planned`,
  leaves an adopted parent open, closes the milestone (milestones take no state_reason). The *why* is
  posted verbatim from the signed ship-review via `--reason-file` (DEC-138 am.5/am.6).
- **Migration scope** → **new features only.** FEAT-01/02 are shipped (retrofitting risks closing
  settled work); FEAT-03 is mid-build with its hazard documented and worked around, and rewiring the
  mirror under a running build is not worth it.
- **Shared helpers** → extract `parent_of`, create-then-attach and the `blocked_by` write from
  `wayfind.py` so gh-sync and wayfind share one copy. Two copies of the id-not-number trap is the
  duplication class DEC-158 keeps finding.
- **BRIEF stays a signed file in the repo**, never a GitHub issue — a wiki-editable UI feeding an
  approval-gated artifact is the DEC-19 bypass shape, and agents need a non-volatile goal of record.

## Not yet specified

- Whether the ship-briefing "absorbed issues" section needs a machine-readable form (checkbox
  parsing) or whether the orchestrator reading the signed prose is sufficient. Sharpens once the
  briefing template is being edited.

## Out of scope

- **Feature B's contents** (PLAN `depends_on:`, `blocked_by` edges, ordering validation) — sequenced,
  not abandoned.
- **Retrofitting FEAT-01/02/03.**
- **Inducting kaya's pre-harness decisions** — a genuinely different destination the user raised: the
  decisions already made in code and PR threads have no home in harness today (`PLAN ## Decisions`
  is per-feature and forward-looking; the codebase map records what IS, never why; kaya has no
  project-level decision record like harness's own DECISIONS.md). That is its own **wayfinding
  effort** — tickets of the form "does decision X still hold?", survivors recorded with rationale,
  killed ones in `## Out of scope` so a future scan does not resurrect them. Not part of this
  migration; likely needs the decision record to exist first.

## Facts I verified (so pm does not re-derive them)

- **The flat model has a 0-for-3 record** — `feature.yaml github.issues`: FEAT-01 collides T-03 and
  T-04 both onto #31; FEAT-02 maps all tasks to #120; FEAT-03 maps all eleven to #48 with milestone
  #10 empty (open=0/closed=0). Not sloppiness — DEC-138 am.1 predicted it: "intake absorbs, never
  imports 1:1."
- **Closure does not cascade in either direction** — probed in `mruangutai/harness` (#1/#2/#3, since
  closed): one sub closed → parent open; last sub closed → parent still open at 100%; parent closed →
  subs stay open. Recorded as DEC-168.
- **`state_reason` enum is exactly `completed` · `not_planned` · `duplicate`** — `not_doing` returns
  422, so "not doing" can only be a label, never a close reason.
- **`sub_issues_summary` is eventually consistent** — read `total: 1` immediately after the second
  attach, corrected to `total: 2` seconds later. Never assert on it right after a write.
- **APIs live on gh 2.92.0 / the pinned repo**: `issues/{n}/sub_issues`,
  `issues/{n}/dependencies/blocked_by`, `issues/{n}/parent`.
- **PLAN has no task-dependency field** — `parse_tasks` reads `change_type`, `traces`, `absorbs` only;
  ordering is implicit in `T-NN` numbering and prose. The lead's run `state.yaml` carries `depends_on`
  per step, so the information exists but is re-derived per run. This is what makes Feature B a
  pm-format change rather than a mirror change.
- **`gh-sync.py` shape**: `cmd_open` creates milestone-then-issues, saving `feature.yaml` after every
  create (DEC-131 crash discipline); `cmd_close_task` closes the task issue plus everything in
  `absorbs:`; `cmd_ship` closes the milestone only.
- **DEC-138 am.4 already establishes the briefing-gated route** for turning residuals into issues at
  the user's signature — the absorbed-issues line reuses it rather than inventing a path.
