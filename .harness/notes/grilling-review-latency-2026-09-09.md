# Grilling — reducing wall-clock time spent in review without lowering review quality — 2026-09-09

## Destination

The review path costs materially less wall-clock time per feature, with no reviewer role weakened
and no gate relaxed. Reaching the end looks like: the reviewer dispatch contract, the review team
DAG and the plan-phase segment ordering all changed and signed, with evidence that no historically
measured finding would have been lost under the new rules.

## Settled

- What problem are we solving? → Total wall-clock time spent in review, not cost and not token
  volume. Cost savings are welcome but never the justification.
- May review quality be traded for speed? → No. The severity bar, the Stage-1-before-Stage-2 order,
  qa's source-blind Phase 1, the full panel at cycle 0, and `validate-digest.py`'s independent
  `code_grade` recomputation all stay exactly as they are.
- Which levers are in this effort? → Six: (1) a delta-review contract at cycle >= 1; (2) reviewer
  surface declaration so a scoped-out reviewer is not re-dispatched; (3) orchestrator-precomputed
  mechanical panel inputs; (4) the panel's gate-only qa step made conditional on the pin having
  moved; (5) the plan-phase goal-check and plan-panel run concurrently; and (6) the per-worktree
  footprint of the feature tree, added by the user after the first five and called out as key.
- What is lever 6, exactly? → Every feature worktree carries a full copy of every other feature's
  history. Reduce what a live worktree must hold, without deleting any record and without
  removing standing worktrees (the user declined that separately). The record stays complete in
  the default branch; what changes is how much of it a working checkout materialises.
- What must lever 6 never do? → No gate may quietly stop checking because a checkout holds fewer
  feature directories than the repository does. An invariant that iterates `features/*` and finds
  fewer of them must say so and refuse, never report clean. This is the fail-open shape the panel
  exists to catch, and it is the whole risk of the obvious mechanism (sparse checkout).
- How aggressive is the delta contract? → Delta by default at every cycle >= 1: review
  `prev_review_sha..review_sha` plus a mandatory re-check of every prior finding. Full-diff review
  snaps back when the delta touches a file the previous round did not review, when `[harness:human]`
  commits appear in the range, and on the final round before ship.
- How is a scoped-out reviewer skipped? → The reviewer declares, alongside `in_scope: false`, the
  path patterns it judged absent. A later round skips it only when the delta intersects none of
  them. The judgement stays with the role; the arithmetic does not. A hand-maintained central
  path→reviewer map was rejected: it drifts silently and becomes a second source of truth about
  domains.
- What proves the delta contract does not lose findings? → Replay all 21 measured FAIL-after-PASS
  re-runs in `.harness/harness/features/*/notes/` and show each finding is still reachable under
  the new rules. This is a gating criterion, not a sample.
- Does run wall-clock instrumentation land here? → No. Adding `started_at`/`finished_at` to
  `feature.json` `runs:` needs a signed decision, a `feature-schema.json` change and CI, and the
  schema edit is main-session-direct. It is a separate follow-up; this effort is judged on review
  quality, and its speed claim stays an estimate until then.
- Do the integration-suite file splits belong here? → No. They are main-session-direct under
  DEC-174 (tests of gate scripts) and are already running in parallel under issue #1527.

## Not yet specified

- Whether the delta contract needs a distinct spelling in the reviewer digest — a `reviewed:` form
  that names both SHAs — or whether the existing `reviewed:` field carries it unchanged.
- How the plan-phase concurrency interacts with `panel_findings.py`'s PF- id computation when the
  goal-check note and the panel land in the same synthesis rather than in sequence.
- Whether the surface declaration belongs in each reviewer's digest schema or in its report file.
- Which mechanism serves lever 6: a sparse checkout that materialises only the worktree's own
  feature directory, or archiving terminal features so the tree shrinks everywhere including the
  default branch. Both were named; neither was chosen. The choice turns on how many readers walk
  `features/*` and whether each can be made to refuse rather than under-report.
- Whether the same reasoning applies to `.harness/harness/features/*/runs/` independently of
  `notes/`, since the two differ by an order of magnitude in file count per byte.

## Out of scope

- Cost, token budgets and model routing. DEC-178 removed the meter; this effort does not restore it.
- Change-based test selection. DEC-211 rejected it and that stands; suite work here is parallelism
  and per-file cost only.
- The number of reviewers on the panel. The four roles stay; the panel is already dispatched in one
  turn, so removing a role saves cost, not wall clock.
- Deleting or pruning standing worktrees. The user declined this explicitly; lever 6 reduces what
  a worktree holds, never how many exist.
- Deleting, pruning or lossily rewriting any feature's recorded history. The record is evidence.
- `check-state.sh`'s GitHub project-board query, which is 11.3s of its 14.3s runtime. Measured
  during this grilling and filed as issue #1541; it is gate tooling, not this feature's surface.
- Any relaxation of the gate rule (`must_fix` non-empty or `severity_max >= high` → FAIL).
- `feature.json` schema changes (see instrumentation, above).

## Facts I verified (so pm does not re-derive them)

- Validator runs per feature: median 4, mean 5.0 across 66 features — from `feature.json` `runs:`
  at `7e0c2ec1`.
- Post-pin reviewer notes by cycle: c0 127, c1 87, c2 48, c3 31, c4 24. 60% of all reviewer spawns
  are re-runs — counted from `features/*/notes/review-harness-*-cN.md`.
- Re-run yield: 126 re-runs followed a PASS by the same reviewer; 105 (83%) re-confirmed PASS, 21
  produced FAIL. Every one of the 21 I sampled located its finding inside the fix delta.
- `security-reviewer` re-ran 16 times after its own scope-out and found nothing in any of them.
  `ui-reviewer` re-ran 38 times after a scope-out with 5 later FAILs, 4 of which were plan-phase
  (Mode A) runs, not post-pin.
- Reviewers already improvise delta review: `BUG-1308/notes/review-harness-code-reviewer-c4.md`
  opens "cycle 4 (DELTA, final)"; `BUG-440/notes/review-harness-security-reviewer-c3.md` proves
  byte-identity outside the delta by hash before scoping to it.
- `harness-review/SKILL.md:28` currently states the absolute the delta contract contradicts:
  "Every subsequent step diffs `base..<review_sha>`. **Never `..HEAD`**."
- `teams/review.yaml` dispatches all four reviewers with `depends_on: []` in one turn, so the panel
  is already parallel; the lead's synthesis is not a dispatched step.
- The panel's `qa` step is gate-only (D-08) and re-runs the same `test_matrix` the qa segment
  already ran; 157 segment notes vs 91 panel notes across the corpus, and the panel step FAILed
  9 times in 91.
- `harness/SKILL.md:110-117` sequences the product goal-check before the plan-panel and feeds its
  note in as an input.
- Suite wall clock is not a review lever: inside a feature worktree the integration suite is 75.6s
  (`test-check-state.py 73.01s`), matching the 44-99s recorded in historical qa notes. The 240s I
  first measured occurs only in the main checkout, where `.claude/worktrees/` exists; that is
  issue #1525, fixed in PR #1526, and it saves nothing in the agent loop.
- Worktree footprint, measured at `7e0c2ec1`: `.claude/worktrees/` is 1.17 GB across 27 live
  worktrees. A worktree is ~43 MB, of which **36 MB (84%) is `.harness/`**. Git objects are shared
  through the one object store, so this is purely materialised working files.
- The feature tree itself: 86 feature directories, **3928 files, 34.3 MB**. `notes/` alone is
  21.2 MB in 2520 files (62% of bytes, 64% of files); `runs/` is 5.3 MB in 799 files; top-level
  feature files are 6.5 MB; `observations/` is 1.2 MB.
- **72 of the 86 features are terminal (`status: done` or `abandoned`), holding 33.8 MB — 98.5% of
  the tree.** Every live worktree materialises all of it, so roughly 920 MB of the 1.17 GB is dead
  features copied 27 times.
- 93% of the repository's tracked files (3211 of 3469) live under `.harness/`.
- What the bulk actually costs in time, measured, so lever 6 is not oversold: 1.38s per
  `check-state.sh` run in `worktree_terminal.classify_all` (75 git calls across 30 worktrees), and
  it scales with worktree count. `git status` in a worktree is 0.06s. Feature COUNT costs nothing
  measurable: check-state took 14.7s with 86 feature dirs and 14.65s with 16.
- Readers that walk `features/*` and would therefore see less in a sparse checkout:
  `check-state.sh` (INV-17, INV-23, INV-28 and others), `board_lifecycle.py`,
  `check-plan-routes.py`, `factory_decompose.py`, `feature-worktree.py`, `feature_json_write.py`,
  `feature_schema.py`, `harness_boundary.py`, `layout_fixtures.py`, `layout_migration.py`,
  `quarantine.py`. This list is the fail-open surface, not a task list.
