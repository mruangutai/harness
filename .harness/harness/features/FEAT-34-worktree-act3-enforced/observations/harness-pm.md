# Observations - harness-pm

- 2026-08-24: FEAT-34 plan round. plan-merge.py REFUSES a create-path proposal carrying an
  approval mapping (exit 8, "the signer is the main session"), but check-state.sh then reports
  VIOLATION "plan.yaml has no approval: block". Measured by stashing the file: 0 violations
  without plan.yaml, 1 with it. A plan created by the sanctioned tool is a state violation
  until the main session writes the block. Raised as an open_question, not worked around.
- 2026-08-24: the operator's "re-derive every citation" instruction paid twice on FEAT-34, and
  the second time was the one nobody predicted. SKILL.md:321 -> :430 was the expected drift from
  FEAT-35. The unexpected one: the signed brief's INV-numbering premise ("check-state.sh contains
  zero occurrences of either INV-28 or INV-29") was FALSIFIED at HEAD - FEAT-26's T-05 landed and
  INV-28 is now at check-state.sh:1044/:1068/:1080. A brief's own reasoning rots as fast as its
  line numbers.
- 2026-08-24: check-domain.sh --resolve is a DOMAIN GRANT, not a LANE. It printed
  "harness-backend-dev harness-dev-ops" for check-state.sh and test-check-state.py, both of which
  DEC-174 amendment 4 puts on main-session-direct. check-plan-routes.py agrees and prints these as
  DEVIATION rather than VIOLATION - so the tool records the disagreement instead of resolving it,
  and the planner must. Record the verbatim tool output AND the overriding decision in the lane row.
- 2026-08-24: measuring a premise can be done through its REPAIR. #806 claimed ten Done features'
  milestones were open; all 24 read closed by the time I looked. Ten carried closed_at inside a
  four-second window (2026-08-24T14:07:46-50Z) while their PRs merged 1-18 days earlier. cmd_ship
  closes the milestone unconditionally, so the batch signature proves ship never ran at merge time.
  A premise that no longer reproduces is not automatically falsified - look for the repair's trace.
- 2026-08-24: shrinking a blocking open question beats raising it whole. Q1 (where the tracked
  hooks dir lives) looked like it blocked the entire hook half. Putting the hook BODY in
  .claude/skills/harness/bin/post-merge-sweep.sh - granted, testable by a test that installs it
  itself - left only the tracked shim and the core.hooksPath install unspecifiable. Q1 went from
  blocking 3 SCs to blocking 1.
- 2026-08-24: FEAT-34 resume. The default Bash cwd for this pm spawn WAS the worktree (pwd + git rev-parse --show-toplevel both returned the FEAT-34 worktree), so check-state.sh and check-plan-routes.py measured the right tree; the orchestrator hit the opposite. Verify cwd rather than trusting either claim.
- 2026-08-24: settings.snippet.json points all seven hook entries at ${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/, which falsifies the harness-init prose that the harness is "not copied into a product repository". An initialised project provably carries .claude/skills/harness/. That evidence decided D-08 against a repo-root .githooks/.
- 2026-08-24: FEAT-34 plan-fix. A plan verify that greps a runner run can be vacuous because the runner rejects the ARG FORM first: `run-unit-tests.sh integration` (bare positional) exits 2 at :33-36 before either checker runs, so `grep -c KIND-DRIFT` printed 0 on every tree. The flag is `--kind`; `--check-kinds` runs both checkers and no tests. Always run a plan verify against a deliberately wrong copy of the tree before writing it.
- 2026-08-24: FEAT-34 D-10. `classify(root)` over one `git worktree list` cannot serve a "every repository" requirement when the other repos are separate git repositories (feature-worktree.py dest_for joins WORKTREES_SEGMENT to owner_root only). A green per-repo unit test looks like coverage and is not. Check whether the TEST calls the function once per repo or once total.
