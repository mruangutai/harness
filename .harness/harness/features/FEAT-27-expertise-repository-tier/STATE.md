# STATE

## Current

- feature: FEAT-27-expertise-repository-tier
- run: .harness/harness/features/FEAT-27-expertise-repository-tier/runs/distill-*/state.yaml
- squad: all three (distillation)
- status: in-flight

Mission ship, close-out. Branch `feat/FEAT-27-expertise-repository-tier`, **`review_sha` pinned at
`9b929de`** — the tip the panel and the goal-check both graded. `cycles_used` 3 of 10; 12 runs
against an informational budget of 20. Mirror: milestone 17, parent #494 adopted and now at
`Review`; all seven sub-issues closed (#565, #566, #567, #568, #569, #570, #573).

**All seven tasks are done and every gate has passed.** The blocking qa gate returned `matrix_ok:
true` for the whole feature. The review panel — the feature's first, four reviewers including a
security reviewer that stayed in scope and a ui reviewer that looked before scoping out — returned
`severity_max: med`, `must_fix: []`, which is ADVISORY under `gates.review:
advisory_unless_high`. The goal-check returned **all eleven criteria met**, nine of eleven on
measurements pm took itself rather than inherited, and judged the BRIEF's goal and effort #336's
DC-3 closed.

Verified at my own tier, not relayed: both suites green at the pin (`unit` exit 0, `integration`
exit 0, zero `FAIL` lines, exit status captured in a variable); sixteen `--resolve` calls each
returning the agent's own name with a `NOBODY` negative control; fifteen craft and six repository
Expertise files each named `OK`.

**Remaining:** distillation (three leads, dispatched in one turn), then the CEO briefing. Ship-refresh
is SKIPPED with reason — `.harness/codebase/` does not exist, so there is no map to intersect.

**Two things the operator must settle**, both carried in the briefing: whether `plan.yaml` needed
re-signature after T-07 joined the task set post-signature (the artifact carries one flat `approved`
with a single same-day date and no amendment field, so it cannot evidence its own amendment either
way), and the disposition of ~20 non-gating backlog rows.

**Distillation output must NOT be committed to this branch.** Writes to `.harness/expertise/**` and
`.harness/harness/expertise/**` fall outside every task's `files:` list except T-04's migration, and
committing them here repeats FEAT-25's B-18. They are left in the working tree for the operator to
land separately.

## Open Questions

- **Blocking, operator only:** was `plan.yaml` re-signed after T-07 was added? I proceeded on the
  operator's explicit "Q4 is ADOPTED … one follow-up task this cycle" instruction, which named the
  lane, `change_type` and mechanism, and on `plan.yaml` reading `approved` so the step-0 gate passed.
  product-lead had flagged it blocking before T-07 dispatched. Recorded as a judgement I made, not a
  formality that was satisfied.
- `check-state.sh:149`'s comment names an approval-reset rule that neither `:133-139` nor `:150-154`
  implements — an amended-but-unsigned plan reports green. Under the DEC-174 carve-out, so a human
  fixes it directly.
- `DEC-27` is falsified on two clauses by this feature's own shipped code and carries no strike
  record, which DEC-188 requires. Not fixed here: `DECISIONS.md` and `DECISIONS-INDEX.md` are
  uncommitted under another flow carrying DEC-174 amendment 4, so editing them would collide.
- Six assertions that cannot redden, plus seven new panel findings, all outside every SC's text and
  none a delivery gap. Ranked in the briefing.
- SC-02's declared `evidence: integration` names a suite with no case for it; the criterion is met by
  direct measurement, the declaration is aspirational.
- Entry ids are renumbered in the DESTINATION on migration, which no criterion checks and which
  dents DEC-66's stable-reference rationale. A constraint reading, so approval-gated.
- `SendMessage` is unavailable at the lead tier, so a lead cannot course-correct an in-flight member.
  Raised independently by two leads. Harness defect, not Expertise.
