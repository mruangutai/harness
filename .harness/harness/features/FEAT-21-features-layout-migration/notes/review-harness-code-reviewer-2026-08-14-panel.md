# Code review — FEAT-21, review panel `code`, run 2026-08-14-3-panel-validator

Reviewed: `62fef85..b1d3925`. Confirmed 8 commits in range via `git rev-list --count`; the
three not named in the dispatch (`5c39f8c`, `649b36b`, `3df7002`) are state/record-only
(`STATE.md`, `feature.json`, `plan.yaml`, `notes/`) — verified by `git show --stat` on each,
no code paths touched. `feature.json:6` `review_sha: "b1d3925"` matches this review's pin.

**VERDICT: PASS.** No must_fix. One non-gating spec_violation (scope_creep), two low/info
quality notes, one open process question (Q-E, already on the board).

## Priority 1 — D-08 label fix, both halves (`check-state.sh:55-59` + 17 call sites)

**Built correctly. MF-1 is genuinely fixed.**

- `_feat_dirs` (`:55-57`) and `fpath()` (`:58-59`) exist exactly as described. `fpath()` is
  called at 17 sites (not 18 — `grep -c "fpath(feat\|fpath(_feat"` returns 18 only because it
  also matches the `def fpath(feat, ...)` line itself; the dispatch's "18" almost certainly
  made the same count). All 17 carry a real tail (`'BRIEF.md'`, `'plan.yaml'`, `'STATE.md'`,
  `'feature.json'`, `'PLAN.md'`) — no call site is bare, none double-applies.
- Swept every remaining `{feat}`-only label in the file (full `grep -n` of the diff plus the
  live file): all of them name the feature or a `T-NN`/run id, never build a path string —
  consistent with T-05's rule ("where a finding names a feature and not a path, leave it as
  the bare name"). One pre-existing bare-name label at `:638` (`INV-18`,
  `os.path.basename(fdir)`) was **not** touched by this diff (confirmed via `git diff
  ea937b1 d033b9d`) and doesn't build a path string either — out of scope, not a defect.
- The deferral half held: `briefs`, `plans`, `states`, `plan_docs` and the station-mirror
  `_feat = os.path.basename(_fp)` (`:1161`) all still key on the bare basename — grepped every
  `os.path.basename` site in the file, none gained a segment. `plan_docs.get(_feat)` still
  resolves for every feature, so the fail-open D-08 was written to prevent (INV-26 silently
  skipping every feature) is not reintroduced.
- Test fixtures: every builder in `test-check-state.py` moved to
  `.harness/harness/features/FEAT-TEST` except the one deliberate legacy holdout in `case_x`
  (`:1613`, commented as intentional — legacy reader stubs need legacy evidence). No stale
  fixture silently globs zero and reports false-clean.
- Repo-wide sweep of `.claude/skills/harness/bin/*.py|*.sh` for the old
  `os.path.join(H/h, "features", ...)` shape at the tip of the range: only the two sanctioned
  survivors remain (`layout_fixtures.py:42` legacy stub text, `layout_migration.py:91` the
  detector's own regex literal). No live silent fail-open glob left in production code.

**Two quality notes, neither must_fix:**

1. `test-check-state.py` case (n) (`~1546-1548` in the diff, budget-line case) had its
   assertion **weakened**, not just updated, to accommodate the fpath() label change: the old
   check was an exact contiguous substring, `"INV-23 FEAT-TEST/feature.json is" in out`; the
   new one is three independent substrings `"INV-23 " in out and "FEAT-TEST" in out and
   "feature.json is" in out`. Concrete consequence: if `fpath()` regresses to its own
   `?`-fallback path (`.harness/?/features/FEAT-TEST/feature.json`), this case still passes,
   because all three keyword fragments are still present — it never asserts the segmented path
   text is actually in the message. I grepped the whole suite for any assertion containing the
   literal discovered segment (`harness/features/FEAT-TEST` or similar) and found none. This
   **corroborates, not extends,** the already-recorded Q-H gap ("neutering `fpath()` leaves the
   suite at exit 0") — I'm not re-filing it, just naming the exact mechanism in this commit
   that produced it, for whoever eventually closes Q-H.
2. `_feat_dirs` (`:55-57`) is itself keyed by the bare basename `os.path.basename(_d)`. D-08's
   own text says the label mechanism carries "none of that risk" the deferred key-collision fix
   defers — but under the same deferred precondition (two repository segments holding a
   same-named feature directory), `_feat_dirs` collapses last-write-wins exactly like the dicts
   D-08 protected, so a label for one of the two colliding features would point at the *other*
   repository's file: a confidently wrong path, not the visible `?` placeholder Q-H covers.
   Currently unreachable (one repository exists, same precondition D-08 names), same unit 5/8
   remediation. Flagging only because D-08's "at none of that risk" is a slight overstatement,
   per P-06 — not a new defect to fix now.

## Priority 2 — `b1d3925` scope, as fact for the SC-12 assessment

- Sole file touched: `.claude/skills/harness/bin/test-layout-migration.py` (confirmed via
  `git show --stat`). No source file, gate script, or fixture the cluster depends on.
- Not literally "purely additive" in line terms: 61 insertions / 64 deletions — a rewrite of
  case 20, not an append. It **deletes** the two hand-mirrored helpers (`_ci_text`,
  `_inv27_text`) and their five `SurfaceReport`-constructed parity checks, replacing them with
  `_parity_tree`/`_parity`, which run the **real** `check-state.sh` via `subprocess` against a
  built fixture tree and compare its `INV-27` lines to `layout_migration.scan()`+`render()`
  over the same tree — a genuine strengthening (no second mirror exists in the file after this
  commit, confirmed by reading the diff in full).
- One scenario is **dropped**, not carried over: the old `"CANNOT_VERIFY no-rows"` parity case.
  The new code says so in-place (a comment, not silently): it can't be staged through a real
  fixture tree (needs a `READER_TABLE` override) and is asserted to be covered elsewhere
  (`test-check-state.py`'s `case_x`, `cause_text`'s unit coverage) — reporting this as fact per
  your request, not ruling on whether the coverage claim holds or whether SC-12's atomicity
  purpose survives a third, post-cluster commit.
- Ran the suite at the tip of the range: `python3 test-layout-migration.py` — all case-20
  assertions print `ok` (10 checks across 5 parity scenarios), suite exits clean.
- The commit message's discriminating-mutation claim ("the reader-drop mutant... now reddens
  the MIXED parity case") is proven at `835692a`, one commit **past** `b1d3925`, outside this
  review's range. I did not re-derive it (I'm read-only and range-bound) — what I can attest is
  that case 20 is green at the tip of `62fef85..b1d3925` and no longer contains a hand-built
  mirror.
- `d033b9d`'s cluster is intact as one commit — confirmed nothing in `62fef85..b1d3925` besides
  `b1d3925` itself touches any file inside that cluster's diff.

## Priority 3 — Expertise hygiene process (Q-E, `STATE.md:57-58`)

**Assessment, not a ruling — routes to the same open question already on the board.**

The STRING fix is correct: `.harness/expertise/harness-pm.md:7` now reads
`.harness/harness/features/` (verified via `git diff ea937b1 d033b9d` — a single-line path
re-anchor, no restructuring, no new Pattern/Gotcha/Outcome entry). It closes the qa precommit
panel's routed advisory (`notes/review-harness-qa-2026-08-14-precommit.md:22`, ADV-4).

The process gap: this file is **named in no task's `files:` list** anywhere in `plan.yaml` — I
grepped the whole plan for `.harness/expertise/` and got zero hits; T-07's 19-file
"re-anchor the guard-enforced instruction paths" task lists only agents/skills/team-yaml/
`.gitignore`, not Expertise. That makes this a `scope_creep` finding by Stage 1's own test
(nothing in the plan asked for this specific file) — filing it as exactly one row below, per
P-15, because it's real and undisclosed-in-the-plan even though the content is correct and
was flagged in advance by qa.

What would catch a non-benign version of the same edit: I checked `check-plan-routes.py`
(`:3-8`, its own docstring) — it is a **plan-phase** tool that validates each task's *declared*
`files:` list routes to a permitted agent. It does not reconcile the actual landed diff against
the plan's declared files, so a file appearing in `git diff` but named in no task is invisible
to it. There's no gate distinguishing "this Expertise write is a plan-scoped re-anchor" from
"this Expertise write is an undisclosed doctrine change" — enforcement here is per-agent-write-
permission (main-session-direct, DEC-174, broadly permitted inside `.harness/`), not per-
artifact-lineage. The asymmetry showed up live in this very review: `bash-write-guard.sh`
blocked my own routine `git show ... > /tmp/...` redirect at the tool route (a read-only
agent, any write, anywhere) — a strict per-agent-route control — while a builder's 617-file
cluster commit carried an edit to injected, cross-feature Expertise that no automated gate
examined at all.

Two catch-options, offered as assessment for the operator, not a recommendation ranked between
them: (a) extend `check-plan-routes.py` (or add a PR-time step) to reconcile the actual commit
diff against the union of every task's declared `files:`, so an unrouted-but-permitted file at
least surfaces; (b) scope `bash-write-guard.sh` so writes to `.harness/expertise/*.md` require
either a distillation-dispatch marker or containment to a pre-existing entry's literal text (a
"re-anchor shape" heuristic).

## Stage 1 — spec compliance, remainder

Inspection SCs verified at file:line (SC-07/SC-12 already ruled per dispatch, not re-derived):

- **SC-02** (`BRIEF.md:93-98`) — met. Pre-move capture
  (`notes/layout-boundary-2026-08-14.md:7-10`) reads `features: CLEAN — evidence legacy` /
  `docs: CLEAN — evidence legacy` / `0 mixed, 0 cannot-verify` at `HEAD: 5afa7e3` (`:3`).
  Post-move capture (`:64-67`) reads `features: CLEAN — evidence migrated` / `docs: CLEAN —
  evidence legacy` / `0 mixed, 0 cannot-verify`. One already-disclosed wording gap, not new:
  the post-move capture is headed "Working tree over HEAD: ea937b1... this capture rides in
  the cluster commit" (`:60`) rather than naming `d033b9d` itself — it can't, chicken-and-egg,
  since the capture predates its own commit. `STATE.md:60` already records this exact gap
  under "Criterion-wording drifts pm reported and did not rewrite" — confirmation, not news
  (P-07).
- **SC-09** (`BRIEF.md:123-124`) — met. `.gitignore:7` at `b1d3925` reads
  `.harness/*/features/*/runs/**`. Spot-checked live: `git check-ignore` and `git status
  --porcelain --ignored` both show every `.harness/harness/features/*/runs/` as `!!` ignored.
- **SC-11** (`BRIEF.md:130-131`) — met. `git diff ea937b1 b1d3925 --stat -- docs/harness/`
  is empty; none of the three DOCS-surface readers (`gen-decisions-index.py`,
  `harness_boundary.py`, `factory_config.py`) appear in the range's diff stat.

No task marked `done` in the reviewed range was found carrying an unbuilt signed clause beyond
the one already fixed (MF-1/D-08) and the one filed above (Q-E's scope_creep, non-gating).

## Fail-open hunt, summary

Every discovery glob touched by `d033b9d`/`b1d3925` converted consistently
(`H, "features"` → `H, "*", "features"`) with no orphaned old-shape glob left live; `fpath()`'s
miss path degrades to a visible `?` placeholder rather than a silently plausible wrong path (it
still lands in `bad`/`warn`, so invariant enforcement itself never fails open) — except the
`_feat_dirs` collision noted above, which is a different, currently-unreachable, already-
deferred risk. Case 20's rewrite in `b1d3925` removes a fail-open of exactly the measured-
pattern class (a hand-mirrored comparison that can't detect drift in what it copies) rather
than introducing one.

```yaml
VERDICT: PASS
DIGEST:
  headline: D-08's label fix is genuinely complete at both halves; b1d3925 is test-only and strengthens case 20 but drops a no-rows scenario; one undisclosed Expertise edit rides the cluster, benign in content but caught by no gate.
  severity_max: low
  findings: 3
  must_fix: []
  spec_violations:
    - { kind: scope_creep, path: ".harness/expertise/harness-pm.md", ref: "Q-E / STATE.md:57" }
  reviewed: "62fef85..b1d3925"
  human_commits_in_scope: []
  open_questions:
    - { id: Q-E, question: "Is a feature commit an acceptable carrier for an edit to injected, cross-repo Expertise with no task in plan.yaml naming the file? check-plan-routes.py is plan-time only and does not reconcile the landed diff against declared files, so nothing but a human reviewer would catch a non-benign version of this same edit. Two catch-options offered, no ranking: diff-vs-plan reconciliation at review time, or write-guard scoping of .harness/expertise/*.md to distillation dispatches.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-21-features-layout-migration/notes/review-harness-code-reviewer-2026-08-14-panel.md
```
