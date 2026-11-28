# Send-back criteria — draft step (written before dispatch, P-05)

Draft is sent back if any is missing:
1. BRIEF SCs cover: no STATE.md under any feature dir (39 deleted on main); templates/STATE.md deleted; no live text in skills/agents/references/templates/team-config comments/bin/tests mentioning STATE.md except named byte-identical historical records.
2. Orchestrator per-cycle read and post-close-run write (harness/SKILL.md:39,75,90) replaced by plan.yaml + feature.json + latest run digest open_questions/answers notes; no new feature.json field, no replacement status file.
3. check-state INV-2, INV-5, INV-23 STATE half and check-domain STATE budget/section rule removed with tests; SC for no orphan INV ids / rule-table rows; check-state and check-domain green over features with and without the file.
4. decisions_affected: DEC-45 strike (DEC-188, strike record kept), DEC-129 and DEC-150 amend in place (no "Amended by", DEC-205), each other state-tagged decision from the grilling artifact dispositioned; DECISIONS-INDEX regenerated, rulings <=30 words; a task owns DECISIONS.md.
5. Every task execution_mode: main-session-direct (DEC-174).
6. Open question with recommendation on build start vs FEAT-2643; coordination note for FEAT-2641, FEAT-2688, BUG-2524.
7. plan-merge.py check --root <worktree> exit 0; both artifacts pending.
