# Explore — move pm's T-NN tickets to the issue + sub-issue model

**Recommendation: YES, and it fixes a live defect rather than adding polish.** The flat model
DEC-138 specified (one issue per `T-NN`) has never once been used as designed, and the workaround
every feature reached for has disabled `close-task` for the whole build. Sub-issues are the shape
the work actually has.

## The evidence — the specified model has a 0-for-3 record

`feature.yaml` `github.issues` across every kaya feature:

| Feature | Milestone | T-NN → issue mapping | Reality |
|---|---|---|---|
| FEAT-01 | #8 | T-01→83, T-02→168, **T-03→31, T-04→31** | many-to-one collision |
| FEAT-02 | #9 | **all → #120** | one issue for every task |
| FEAT-03 | #10 (open=0, closed=0) | **all 11 → #48** | one issue, milestone EMPTY |

DEC-138 says one issue per T-NN; three features produced zero instances of it. Not sloppiness — its
own amendment predicted why: *"Intake absorbs, never imports 1:1."* pm plans by the work's real
shape, so tasks are usually **parts of** an existing backlog issue, not new peers of it.

## The live defect this causes

FEAT-03's own `feature.yaml` documents it, in caps: a **"CLOSE-TASK HAZARD, ELEVENFOLD"** — because
all eleven tasks map to #48, `close-task` on *any* task closes #48, so the note instructs that
close-task must not be run at all during the build. The mirror's task-closure half is switched off
for the entire feature, by hand, with a comment as the only guard.

The flat model forces a lose-lose: either create per-task issues that duplicate or conflict with
partially-absorbed backlog items (#315/#209/#309/#312/#305 are each only *partly* covered), or map
many tasks to one issue and give up per-task closure.

## Why sub-issues resolve it

Adopt the existing backlog issue (#48) as the **parent**; create one **sub-issue per T-NN**. Then:

- `close-task` closes that task's own sub-issue — the hazard disappears, no hand-guard needed.
- The parent closes at ship acceptance, its natural moment, exactly as the milestone does today.
- Partially-absorbed backlog issues stay untouched and separate; `absorbs:` keeps its current
  meaning without a closure side effect.
- GitHub renders the tree and a completion count natively (`sub_issues_summary` — verified live:
  `{completed, percent_completed, total}`), so feature progress is visible without opening anything.
- Task ordering can ride native `blocked_by` edges, which is what makes GitHub show what is
  actually startable.

## Answers to the questions the task raised

**Milestone vs parent issue — keep both, they do different jobs.** Verified: an issue can be a
sub-issue *and* carry a milestone (#48 sits in milestone FEAT-01 today). The milestone remains the
**definition of done** — its description holds Problem + Goal + the SC checklist, per DEC-138's
amendment — while the parent issue holds the **task tree**. Note today's milestone #10 is *empty*
(open=0/closed=0) precisely because no issues were created; sub-issues would populate it and give
the progress bar something real to count.

**Native `blocked_by` for task order — worth it, and cheap.** PLAN's task ordering is already
computed; emitting it as dependency edges is one extra call per edge at `open` time. Value is the
same as wayfinding's frontier: the human sees what is startable without reading PLAN. **PLAN stays
the source of truth** — DEC-138's asymmetric truth is untouched, since these edges are written
outbound and never read back into planning.

**DEC-138 collision — none.** Creating sub-issue links and dependency edges is *outbound*, which is
all DEC-138 constrains after approval. Nothing here reads issue state into PLAN. (Wayfinding does
read state, but only pre-approval, where DEC-138 already sanctions issues as pm's input.)

**Migration — new features only.** FEAT-01 and FEAT-02 are shipped; retrofitting them buys nothing
and risks closing settled issues. FEAT-03 is mid-build with its hazard documented and worked around
— converting it live would rewire the mirror underneath a running build. Apply to the next feature
that runs `open`.

**Shared helpers — extract, do not reimplement.** `wayfind.py` already has the three primitives:
`parent_of`, create-then-attach (the sub-issue API takes the child's internal `id`, not its
`number`), and the `blocked_by` write. `gh-sync.py` needs all three. Two copies of the id-not-number
trap is exactly the duplication class DEC-158 keeps finding — the extraction is part of the work,
not a follow-up.

## Open questions for the plan

1. **Closure semantics — RESOLVED empirically** (probe in `mruangutai/harness`, scratch issues
   #1/#2/#3, since closed): **closure does not cascade in either direction.** Closing one sub leaves
   the parent open; closing the LAST sub still leaves the parent open (summary reached
   `completed: 2, percent_completed: 100` and the parent stayed `open`); closing the parent leaves
   every open sub OPEN. Consequences for the design, all good: `close-task` on a sub-issue closes
   exactly that task and nothing else — the FEAT-03 hazard cannot recur; the parent must be closed
   deliberately at ship acceptance (it will never drift closed on its own); and a parent closed early
   does not silently orphan-close outstanding tasks. Also observed: `sub_issues_summary` is
   **eventually consistent** — it read `total: 1` immediately after the second attach and corrected
   to `total: 2` within seconds, so never assert on it straight after a write.
2. **What is the parent when nothing is adopted? — and the wayfinding continuity.** A greenfield
   feature has no backlog issue to adopt. Three candidates, and the third is the interesting one:
   (a) create a bare `FEAT-NN` parent issue; (b) let the milestone stand alone with flat task issues
   (the model as specified, finally used); (c) **the effort's wayfinding map issue BECOMES the
   feature's parent issue.** (c) has real pull: the map already holds `## Destination` and
   `## Decisions so far` — precisely the rationale a reader of the tasks needs — so the issue that
   held the decisions grows the tasks that implement them, and the audit trail is one object instead
   of two. The cost to weigh: the map's `## Not yet specified` and `## Out of scope` sections go stale
   the moment BRIEF is signed (BRIEF's scope supersedes them), so either they get pruned at hand-off
   or the parent body carries dead sections. Also, one effort may spawn several features — then it is
   one map parent to many feature parents, and (c) only fits the 1:1 case.
   **User's stated direction:** sub-issues are the unit of work; the parent is the deliberate,
   intentional container — and wayfinding reinforces exactly that reading.
3. **`absorbs:` semantics** — today it closes absorbed issues on task closure. With partial
   absorption being the norm, should it stop closing and only cross-reference?
4. **`parent:` is recorded, never discovered.** `wayfind.py`'s `parent_of` is a *read*; `gh-sync`
   must not use it. Record `parent:` in `feature.yaml` beside `milestone:` at creation, so the mirror
   stays write-only and idempotency keeps coming from local receipts (DEC-138).
5. **Abandonment — decided (user, 2026-07-31): close as `not_planned`.** Verified enum: GitHub
   accepts exactly `completed` · `not_planned` · `duplicate` as `state_reason`; `not_doing` is a 422,
   and "not doing" can only ever be a label, not a close reason. So `not_planned` is the mechanism,
   and the *why* IS posted as a comment — taken **verbatim from the ship-review artifact the user
   signed**, never composed by the mirror (DEC-138 am.6: provenance, not silence). Implementation
   consequence: `cmd_abandon` takes `--reason-file <path>`, so the mirror has no text of its own to
   editorialize with.
   **This is only implementable after the migration**, which is why no `abandon` subcommand exists
   yet: today's recorded "issues" are adopted backlog items (all of FEAT-03's eleven point at #48,
   which is still wanted), so nothing is unambiguously the feature's to close. Post-migration the
   feature's own **sub-issues** are unambiguously ours → close those `not_planned`; leave the adopted
   parent open; close the milestone (milestones take no `state_reason` — close is close). Ship-side
   symmetry: `cmd_ship` closes parent + milestone on acceptance, `cmd_abandon` closes sub-issues
   `not_planned` + milestone on abandonment.

## Cost and shape

Small: `gh-sync.py cmd_open` gains create-then-attach plus optional dependency edges; `close_task`
becomes correct instead of hazardous; `feature.yaml` records `parent:` alongside `milestone:`. It is
a normal feature — one `change_type: api`-ish task set with real verify steps — so it goes through
`/harness-plan`, not a side edit. **The `absorbs:`/closure question (open #3) is the one thing that
could change the shape, so it belongs in the grilling before pm plans it.**
