# STATE — FEAT-32-concurrent-write-merge

## Current

Phase: **plan**, at its terminus. `BRIEF.md` (325 lines) and `plan.yaml` (1212 lines, 13 tasks,
8 decisions, 16 SCs, 10 REQs) exist with approval PENDING on both. Nothing is built and nothing
may be built: the plan's own D-01 gates the whole build on FEAT-30 merging to `main` first.

One product run, `runs/2026-08-21-1-product/`, verdict ESCALATE. No rework: `cycles_used` 0 of 10,
1 run of 20.

Route check re-run by the orchestrator at worktree HEAD 5d9b428: `check-plan-routes.py` exits 0,
**zero VIOLATIONs**, 11 DEVIATION lines tree-wide of which **4 belong to FEAT-32** (T-01, T-07,
T-08, T-09) — matching pm's report; the other 7 are pre-existing FEAT-28 and FEAT-29 rows. All 4
are the deliberately-legal DEC-174 shape under DEC-179.

Suite baseline verified by the orchestrator, and pm's figures are exactly right: `--kind unit`
exit 0 / 179 matched lines / 0 FAIL, `--kind integration` exit 0 / 93 / 0. **Both require
`CLAUDE_PROJECT_DIR` to point at this worktree.** Unpinned, both kinds exit 2 with 0 matched
lines, because `run-unit-tests.sh:3` is `cd "${CLAUDE_PROJECT_DIR:-$(pwd)}"` against a relative
`BIN_DIR`, and the main checkout is currently parked on `feat/FEAT-30-worktree-per-feature`. The
plan's precondition at `plan.yaml:299-300` omits the pinning.

Next action is not the orchestrator's: the operator signs, strikes or amends. Three questions
block the build (DEC-90's status, the FEAT-30 start gate, how much of #551 this feature closes)
and four more are correctness fixes pm should apply in one amend pass at signing.

## Open Questions

- Q1 DEC-90 (`DECISIONS.md:1157`) says every single-writer guarantee holds "with no lock
  anywhere". Verified at source. But the clause is descriptive, DEC-90 is wired into **no gate,
  no script and no skill** (grep across `bin/`, `.claude/skills/`, `team-config.yaml`,
  `harness.json` returns nothing), and FEAT-30's approved `expertise-merge.py` already falsifies
  it. `SPEC.md:2180-2183` propagates the claim and must move with whatever is decided.
- Q2 D-01 gates the entire build on FEAT-30 merging to `main`. Accept the delay, or take the
  transcribed-second-copy shape and start now with two lock dialects in one `bin/`?
- Q3 #551 is only partly closed by this plan — its dispatch cause is fixed, its two reporting
  consequences are not, because `validate-digest.py:845` passes through on `stop_hook_active` so
  a SubagentStop refusal can fire at most once and cannot be a wait.
- Q4 T-05 rewires `expertise-merge.py` onto `flock`. Cases 4, 5 and 6 of
  `test-expertise-merge.py` assert `not os.path.exists(path + ".lock")`. Under `flock` on the
  target no sibling lock file ever exists, so all three pass **vacuously** — the plan's own task
  would create three assertions incapable of going red, which is the defect class SC-04 exists to
  prevent. Needs replacement assertions, not the two workarounds the lead proposed.
- Q5 Q8's first half is closed by measurement, not open: `SubagentStop` **does** carry
  `agent_type`. Observed live this run — the hook rejected this orchestrator's return using the
  persona-specific `orchestrator` schema (`validate-digest.py:181-185`, selected at `:196`), and
  `hook_mode` passes through when `agent_type` is absent (`:838`). It did not pass through.
- Q6 `.harness/team-config.yaml:91` grants pm `plan.yaml` with `upsert: true` and the comment
  "except approval: (DEC-129)". **Nothing enforces it** — `grep -n approval check-domain.sh`
  returns one comment at `:808` and no check; every other `approval` hit in `bin/` is a reader.
  Three artifacts also disagree on who signs: the plan template says the orchestrator, the
  orchestrator playbook says the main session, `team-config.yaml` says pm-except-approval.
- Q7 Whether #627 and the #560/#605 personas come into scope. pm called both OUT with reasons;
  the orchestrator concurs and neither blocks.
