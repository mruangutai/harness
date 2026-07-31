# STATE

## Current

- feature: FEAT-03-subissue-mirror
- run: .harness/features/FEAT-03-subissue-mirror/runs/2026-07-31-04-eng/state.yaml
- squad: none
- status: awaiting-user
- phase: plan — at the approval gate, this phase's exit predicate (DEC-148). Fix cycle 1 closed PASS.
- note: BRIEF.md and PLAN.md are REPAIRED and sign-ready, committed at 4bd0faa; both `## Approval`
  `status: pending` (only the main session signs). Fix cycle 1 (`cycles_used: 1`, DEC-157): pm
  answered all six `must_fix` in artifact text (run 03-product PASS, no send-back), and eng-lead
  re-verified them per-defect-id (run 04-eng PASS, `defect_verdicts` MF-1..MF-6 all `resolved`, no
  new blocking findings). Decomposition unchanged at T-01..T-08; no new `D-NN`. `review_sha` stays
  `1ce886a` deliberately — 4bd0faa touched only `.harness/` artifacts, so every code anchor holds.
  MF-1's trap is closed and I re-checked it directly: SC-06 now discriminates on payload/lookup
  (`"-F", f"sub_issue_id=`, `"-F", f"issue_id=`, `"--jq", ".id"`, `/parent"`) with an explicit
  carve-out that the list GETs at `wayfind.py:113` and `:117` stay; all four strings are present in
  `wayfind.py` today (counts 1/1/2/1), so each absence-grep fails now and can only pass after T-02.
  Q7 (budget) is resolved: the user raised `harness.json budgets.per_feature_usd` 40 -> 120 at
  commit 1ce886a, `feature.yaml max_cost_usd` mirrors it, and the task count was deliberately held
  at 8 so the decomposition under the user's pending signature did not move. ~$87 of $120 spent,
  all in planning. Segments 1b and 3 remain skipped. Next phase: build, on signature — see
  notes/handoff-plan.md.

## Open Questions

- Q13 (NEW, for the user at signature) — **SC-13 is a success criterion only the user can satisfy.**
  BRIEF grew 12 SC -> 13 this cycle; SC-13 is the checkable form of REQ-09's second clause, and its
  subject (`.claude/skills/harness/SKILL.md:137,144`) is covered by no agent domain. MF-5's remedy
  now rests entirely on that edit: eng-lead accepted a softening of its own run-02 wording (the
  `<!-- stale: -->` marker became optional at PLAN:56-57, with SC-13's ship-gate grep substituted as
  the detection mechanism). Consequence if the edit is not made before ship: SC-13 is unmet at
  goal-check, the gap can be routed to no lead, and the feature goes BLOCKED on a criterion the plan
  always knew was un-owned. Named at PLAN `## Preconditions`:46-57. Distinct from Q1, which predates
  SC-13's existence.
- Q14 (NEW, orchestrator, harness defect) — `bash-write-guard.sh` reads `<noreply@anthropic.com>` in
  a `git commit -m` argument as a shell redirect and BLOCKS the call ("redirect targets 1,"). The
  Co-Authored-By trailer is mandated, so every orchestrator commit hits this and must be routed
  through a `-F <file>` message written into the agent's own domain. A rule backfiring, not a
  workaround to keep.
- Q1 (pm) — `.claude/skills/harness/SKILL.md:137,144` state the mirror contract this feature
  reverses; no agent domain covers that file. ANSWERED IN PLAN, not closed: pm kept REQ-09 whole and
  named the SKILL.md edit as a main-session pre-ship step (PLAN `## Preconditions`:46-57, T-08),
  with SC-13 as its checkable form and the `check-docs.sh` consequence stated both ways. See Q13.
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
  which check-state.sh rejects per DEC-156. Refinement found this cycle: the obvious fix (rename the
  placeholder to `run_cost_usd:`) is ALSO rejected — `CHECKPOINT_KEYS` (check-state.sh:258-268)
  admits only `cost`, so the metered figure must nest as `cost.run_usd`. Hand-resolved that way in
  all four run dirs; the playbook instruction and the invariant still disagree.
- Q12 (orchestrator, tree dirt) — RESOLVED at f929d44: `__pycache__/` and `*.pyc` ignored in both
  `.gitignore` and `templates/gitignore.snippet`, the tracked `.pyc` untracked, tree clean.
  This also discharges MF-6.
