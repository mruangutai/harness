# Plan-panel c4 — scope reader — FEAT-53

**BLUF.** All six authorised cycle-4 changes (V-1..V-5, Q3) are genuinely landed in the fields the
operator named, verified at source, not merely from pm's summary. Structural sweep (REQ/SC tracing,
`depends_on` order, `files`-vs-`intent` coverage, stale neighbours of every c4-amended field) turns up
no orphan REQ, no untraced SC, no cycle, no missing file. Three small, non-blocking findings below —
none gates, each is a single-clause edit.

## Job 1 — the six closures, graded at source

| Item | Verdict | Field cited |
|---|---|---|
| **V-1** trend.jsonl committer | **CLOSED** | `D-22.choice` (plan.yaml:135-138) names "the record_ship call T-19 adds to gh-sync.py's cmd_ship"; `T-19.intent` (plan.yaml:1199-1223) has the "APPEND AND ITS COMMIT ARE ONE ACT" sentence, the non-fatal wrap ("never an abort, never a raise"), and the "Do NOT touch this repository's own trend.jsonl" scoping clause that explicitly reconciles the task's own execution against shipped behaviour. `lanes:` gained a `.harness/metrics/trend.jsonl` row (main-session-direct) consistent with `D-22` — no contradiction between the lane grant and T-19's execution-time rule. |
| **V-2** one approval-date authority | **CLOSED** | `D-14.choice` (plan.yaml:96) states the one-authority/two-callers rule; `T-06.files` lists `.claude/skills/harness/bin/brief_approval.py`; `T-06.intent` (plan.yaml:419-420) creates `approval_date(feature_dir)`; `T-11.intent` (plan.yaml:763-767) calls the same function and explicitly forbids restating the parse. Placement outside `bin/dashboard/` is justified (touchpoints.py must not reach into the dashboard subtree) and introduces no import cycle (the module only reads BRIEF.md text) and no task-graph cycle (T-11 depends transitively on T-06 via T-10→T-07/T-09→T-06). |
| **V-3** four gap-state fixtures | **CLOSED** | `T-06.intent` (plan.yaml:428-436) names all four branches, requires four SEPARATE assertions plus an assertion that the four sentences differ, and forbids an aggregate assertion or an unavailable-count assertion. |
| **V-4** copy-to-temp for mutating fixtures | **CLOSED** | `T-11.intent` (plan.yaml:829-837): every writing case copies via `TemporaryDirectory`/`shutil.copytree`; read-only cases must NOT copy; a recursive-digest before/after case is its own assertion. |
| **V-5** day-granularity predicate | **CLOSED** | `D-21.choice` (plan.yaml:125) and `T-11.intent` branch 3 (plan.yaml:778-783) both state UTC-calendar-day comparison, same-day reaches branch 4; `T-06.intent` (plan.yaml:422-424) states its general 00:00:00Z rule is untouched and names this predicate as the sole scoped exception. No contradiction. |
| **Q3** seventh KPI (merged PRs/week) | **CLOSED**, all five sub-checks | (a) empty bucket: `T-10.intent` "no ship record in the week of \<date\>", never 0/"0" (plan.yaml ~660-700). (b) reuses `kpi.resolve_window`, explicit "do NOT restate a window boundary here." (c) no third shape: `T-14.intent`/`T-21.intent` both say "Shape B REUSED... add no third chart shape... CAP-01 to CAP-13 is closed at thirteen"; DESIGN.md:247 independently states "Two chart shapes and three tables exist in this feature, and nothing else." (d) T-21.verify's watched-label array and T-22.intent's three quoted labels are byte-identical strings (`"grading panel mounts the Shape A histogram"`, `"trend panel mounts the Shape B time series"`, `"merged PR panel mounts the Shape B weekly line"`). (e) BRIEF `## Verification gaps` and `T-07.intent` (plan.yaml:541) both correctly read `3x3` now (swept: zero `3x2`/`3×2` occurrences anywhere in plan.yaml). REQ-15 traced by T-10/T-14/T-21; T-22 deliberately not traced (it verifies, delivers nothing) — correct per the plan's own convention (T-22 already omits REQ-10 while gating a REQ-10-related case). |

## Job 2 — structural sweep

- **REQ/SC tracing**: every REQ-01..REQ-15 has ≥1 tracing task; every task's `traces` cites an
  existing REQ. BRIEF `### Coverage` table verified bidirectionally consistent for all 15 REQ rows
  and all 20 SC rows (REQ→SC and SC→REQ agree in both directions) — no orphan, no unknown id.
- **`depends_on` topology**: walked all 22 edges; every dependency a task actually needs is present,
  directly or transitively (e.g. T-12 needs T-07/T-09's work only via T-10, which is depended on;
  T-19 needs T-07/T-09/T-11 similarly transitively). No missing edge, no cycle found — did not need
  to re-derive the full graph mechanically, spot-checks were consistent with the "22/22 acyclic"
  claim.
- **`files` vs amended `intent`**: the two highest-yield sites both check out — `T-06.files` carries
  `brief_approval.py`, `T-19.files` carries `gh-sync.py`. No other c4-amended task (`T-05`, `T-07`,
  `T-10`, `T-14`, `T-21`, `T-22`) needed a new file for its amendment; each amendment lives entirely
  inside existing files already on that task's `files` list.
- **Stale-neighbour check** on `T-05, T-07, T-10, T-14, T-19, T-21, T-22, D-14, D-21, D-22`: no
  contradiction found between an amended field and its neighbour (`T-15` correctly left unamended
  per pm's own note, and independently confirmed it contains no tile-count or shape-count language
  that would need updating; `T-13`/`T-16` similarly contain nothing that references tile count).

## New findings (non-blocking, all single-clause)

- **id**: S-01
  **severity**: low
  **reader**: scope
  **summary**: SC-13 asserts two things ("figure equals the hand-labelled count" AND "that rule is
  stated in the UI beside the number") but declares `verify: automated, evidence: unit`, and only
  the first half is machine-checked.
  **why**: T-08's unit test (backend, `defects.py`) can only prove the count; T-14's verify greps
  for gap-state component names and forbidden literals, not for the escaped-defects
  `sourcing_rule` text being rendered. No inspection SC (unlike SC-06's explicit BRIEF carve-out to
  SC-15) is named as the carrier for the UI half either. A reviewer marking SC-13 "automated: pass"
  would be over-claiming: the UI-visibility clause has no assigned gate at all, mechanical or
  inspection.
  **remedy_size**: single-clause edit — either split SC-13's UI clause into SC-15's inspection scope
  (mirroring the sentence BRIEF already uses for SC-06's carve-out) or narrow SC-13's own text to the
  count-equality claim alone.

- **id**: S-02
  **severity**: med
  **reader**: scope
  **summary**: Backlog rows B-7..B-10 (`notes/ship-review-2026-09-01-plan.md:126-129`), accepted as
  backlog in c1 ("None struck"), have no live carrier anywhere in `plan.yaml` — no task, no lane, no
  panel-tracked `PF-`/`V-` id — unlike B-1..B-5/B-11..B-18, which all reached `panel.findings` with a
  disposition tied to a concrete filing instruction ("filed at ship with label Dashboard").
  **why**: B-7 in particular is labelled `bug`, not `chore` — "KPI 1's change-size half reads `git
  diff default...branch`, which nulls once a merged branch is pruned... half of KPI 1 would be
  permanently empty off this repo" — a real defect against a onboarded-project-generality
  requirement (REQ-02), accepted for later filing and then never wired to anything that actually
  files it. Nothing in the plan calls `gh-sync.py backlog` for these four rows at ship, so they are
  one missed step from being silently lost the moment this feature ships.
  **remedy_size**: single-clause edit — name B-7..B-10 alongside B-1..B-5/B-11..B-18 in whichever
  task or ship-time instruction already files the others (or add one sentence to T-19/T-20's intent
  naming them), so all backlog rows share one filing mechanism rather than four of them depending on
  someone remembering a static note.

- **id**: S-03
  **severity**: low
  **reader**: scope
  **summary**: BRIEF `## Verification gaps` and `T-07.intent` both justify skipping a grep for the
  bare digit `12` by saying it "occurs inside `1024`, `3x3` and `ES2022`" — none of the three
  actually contains the substring `12`. The real carriers are `127.0.0.1` (D-05's bind address,
  `plan.yaml:60`; also in `T-12`) and `122` itself (which is already the other forbidden literal, so
  citing it as an innocent carrier is circular).
  **why**: The conclusion ("12 genuinely cannot be greped bare") still holds, but the stated evidence
  is false, and this sentence is exactly what a future reader would use to decide whether the SC-06
  literal sweep is trustworthy. This is the same defect pm's own cycle-4 goal-check flagged as its
  addendum `open_questions Q1` — independently re-derived here, not copied: I confirmed `12` is not a
  substring of `1024`, `3x3`, or `ES2022` by direct inspection, and that `127.0.0.1` and `122` are.
  **remedy_size**: single-clause edit — swap the cited carriers in both `BRIEF.md ## Verification
  gaps` and `T-07.intent` from `1024, 3x3, ES2022` to the actual ones, or drop the parenthetical
  entirely since the conclusion doesn't need it.

## What I did not re-raise

Confirmed present and correctly dispositioned, not reopened: PF-6aa9faae, PF-04c95fd6, PF-3713534d,
PF-55e28a6a, PF-d2fc9563, PF-ce8b0187, PF-0f3f4101, PF-aa9c41f6, PF-ed0712ea (all `overruled`/
`backlog`), DEC-5 (closed), the accuracy/handoff-eval KPI's absence (correct, out of scope), and the
D-2/D-3-recorded-as-still-open-at-signature record defect plus DESIGN.md:250's stale React Charts
naming (already surfaced in pm's own goal-check as a record defect, not a build defect — noted, not
filed as a new finding here).
