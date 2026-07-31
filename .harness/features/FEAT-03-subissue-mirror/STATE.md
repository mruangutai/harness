# STATE

## Current

- feature: FEAT-03-subissue-mirror
- run: .harness/features/FEAT-03-subissue-mirror/runs/2026-07-31-04-eng/state.yaml
- squad: none
- status: awaiting-user
- phase: plan — at the approval gate, this phase's exit predicate (DEC-148). Fix cycle 1 closed PASS.
- note: BRIEF.md and PLAN.md are REPAIRED and sign-ready; both `## Approval` `status: pending`
  (only the main session signs). Fix cycle 1 (`cycles_used: 1`, DEC-157): pm answered all six
  `must_fix` in artifact text (run 03-product PASS, no send-back), and eng-lead re-verified them
  per-defect-id (run 04-eng PASS, `defect_verdicts` MF-1..MF-6 all `resolved`, no new blocking
  findings). Decomposition unchanged at T-01..T-08; no new `D-NN`. `review_sha: 1ce886a`.
  MF-1's trap is closed and I re-checked it directly: SC-06 now discriminates on payload/lookup
  (`"-F", f"sub_issue_id=`, `"-F", f"issue_id=`, `"--jq", ".id"`, `/parent"`) with an explicit
  carve-out that the list GETs at `wayfind.py:113` and `:117` stay; all four strings are present in
  `wayfind.py` today (counts 1/1/2/1), so each absence-grep fails now and can only pass after T-02.
  Q7 (budget) is resolved: the user raised `harness.json budgets.per_feature_usd` 40 -> 120 at
  commit 1ce886a, `feature.yaml max_cost_usd` mirrors it, and the task count was deliberately held
  at 8 so the decomposition under the user's pending signature did not move (the T-05+T-06 merge
  stayed an advisory). Segments 1b and 3 remain skipped (feature.yaml skipped_segments).
  Next phase: build, on signature — see notes/handoff-plan.md.

## Open Questions

- Q1 (pm) — `.claude/skills/harness/SKILL.md:137,144` state the mirror contract this feature
  reverses; no agent domain covers that file. ANSWERED IN PLAN, not closed: pm kept REQ-09 whole and
  named the SKILL.md edit as a main-session pre-ship step (PLAN `## Preconditions`:46-57, T-08),
  with SC-13 as its checkable form and the `check-docs.sh` consequence stated both ways. The user
  still performs that edit before ship.
- Q2 (pm) — the BRIEF-H1 parent-title contract needs `.claude/skills/harness-brief/SKILL.md`;
  same uncovered-domain problem.
- Q3 (pm) — freezing an adopted wayfinding map issue's body at hand-off is settled in the grilling
  but scoped out of this BRIEF; nobody owns it.
- Q4 (pm) — prototype gate: pm judged NO prototype required (re-confirmed this cycle — the surface
  is `gh-sync.py`/`wayfind.py`/`check-state.sh` behaviour plus a DECISIONS.md amendment, no
  end-user interactive surface), substituting for visual-designer, which never ran. Overridable.
- Q5 (pm) — PLAN adds an `attached:` receipt list to `feature.yaml github:`, a local-state schema
  addition the grilling did not name. eng-lead judged it safely writable under the regex constraint,
  with one sharp edge: the issues reader `^\s{4}(T-\d+):\s*(\d+)` would misread a nested form.
- Q6 (pm) — pm judges the slug `subissue-mirror` narrower than the feature; id not renamed.
- Q7 (RESOLVED at 1ce886a) — budget raised 40 -> 120 by the user; see `## Current`.
- Q8 (eng-lead) — T-08's owner harness-documentor is in the Product squad; the build segment needs
  lateral routing through product-lead, eng-lead cannot spawn it.
- Q9 (eng-lead) — no `build` team yaml exists (only gate-probe.yaml, review.yaml); pre-existing gap
  that the build phase hits.
- Q10 (orchestrator, harness defect) — check-state.sh infers a cycle from any FAIL run, so it fired
  a VIOLATION on the legitimate "FAIL held at the user gate" state DEC-157 defines as zero cycles.
  Moot now `cycles_used: 1`; the over-approximation is still a defect. Also asymmetric: a pending
  PLAN is a `note`, a pending BRIEF is a VIOLATION — yet a plan mission ends with both pending.
- Q11 (orchestrator, harness defect) — the playbook's `cost-report.py --yaml >> <run_dir>/state.yaml`
  append produces a duplicate top-level `cost:` key beside the lead's `cost: pending_orchestrator`,
  which check-state.sh rejects per DEC-156. Hand-resolved in all four run dirs this feature by
  renaming the lead's placeholder to `run_cost_usd:`; the instruction and the invariant still disagree.
- Q12 (orchestrator, tree dirt) — RESOLVED at f929d44: `__pycache__/` and `*.pyc` ignored in both
  `.gitignore` and `templates/gitignore.snippet`, the tracked `.pyc` untracked, tree clean.
  This also discharges MF-6.
