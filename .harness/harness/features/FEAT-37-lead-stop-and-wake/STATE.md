# STATE

## Current

- feature: FEAT-37-lead-stop-and-wake
- run: eng segment returned BLOCKED. T-07 designed but UNWRITABLE; T-08 never dispatched.
- squad: eng (last)
- status: Building — cycles 1/10, runs 15/20, HEAD a53e6b3

**THE BLOCKER, MEASURED BY ME AND NOT RELAYED.** The write hook runs
`${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/check-domain.sh` — the OUTER main checkout's copy.
`_root()` (check-domain.sh:128-154) resolves the root from that script's OWN bin dir via
`harness_boundary.resolve_root(_bin_dir)`, so `root` is the outer checkout and the manifest read at
line 331 is the OUTER `.harness/team-config.yaml`. That file (outer branch
`fix/868-analysis-digest-and-lead-notes`) has `evals/**` at line 183 and does NOT have the D-16 grant
`.claude/skills/harness/evals/**`, which exists ONLY on this feature branch at line 191.

**THE DISCRIMINATING PROBE, WITH ITS CONTROL.** Running the OUTER script:
`--resolve .claude/skills/harness/evals/lead-never-wait/run-eval.py` → **NOBODY**, and the same for the
absolute worktree path. `--resolve` on the receipt path the member DID write successfully →
**harness-ai-dev**. So worktree-prefix stripping works and the manifest's CONTENT is the sole cause.
Running the WORKTREE's copy of the same script returns `harness-ai-dev` for the evals path — which is
why the grant looked proven at signature. **The signature-time proof ran the wrong copy of the script.**
`check-plan-routes.py` has the same blind spot: it validates against the branch config, not the config
the hook will actually consult.

**PHYSICAL CORROBORATION.** `.claude/skills/harness/evals/lead-never-wait/` exists as TWO EMPTY
DIRECTORIES — `mkdir` succeeded, every file write was denied. Git does not track empty directories, so
they never appeared in `git status`.

**THE WORK IS SALVAGED AND COMMITTED.** `notes/receipt-harness-ai-dev-T-07-c0.md` (157 lines) holds the
full text of all three T-07 files plus ai-dev's out-of-repo measurement: `RATE 13/13 (100.00%)`, nine
violating cases flagged, and both `--prove-discrimination` halves firing. That run was in a scratchpad,
NOT the plan's `verify:`, so **T-07 is not done and its status stays `pending`.** T-08 was correctly not
dispatched: its verify `eval`s a command whose eval is not on disk, so `T08_FAIL` was its only reachable
output.

**RE-DERIVED FOR THE NEXT RUN so it need not be spent again:** nothing enforcing consumes
`test_kinds.eval.cmd`. The only programmatic `test_kinds` reader under `.claude/skills/harness/bin/` is
`run-unit-tests.sh:108`, which reads `integration.detect`. `check-state.sh:479` is a comment. Widening
`eval.detect` is safe; `integration.detect` beside it is NOT, and dev-ops must be told so.

**BUDGET: 15 of 20 runs, FIVE remain, and five segments remain** — T-07+T-08 (one run once unblocked),
the qa gate, the panel, the goal-check, the docs sweep. Zero spare. Cycles stay 1/10; the lead spent no
send-backs, deliberately, because re-dispatch reproduces the denial.

**UNCHANGED AND STILL BINDING:** SC-08 stays `not_met` (D-13; the operator runs it after merge from the
main checkout). The five INV-26 card-station violations are the operator's under DEC-174. The task
numbering gap is deliberate and the struck id is not named here; the struck regression is issue #903.
`review_sha` is `none` and must not be pinned until the matrix is green and simplify has run. No PR, no
merge.

## Open Questions

- Q1 (was: D-02 and D-11 spell the ruling AMEND) — RESOLVED at re-plan. Both now read "corrected IN
  PLACE". The only `AMEND` strings left in `plan.yaml` are T-05's and T-06's own DO NOT ADD AN
  AMENDMENT instructions.
- Q2 (was: DEC-199 amend or STRIKE) — RESOLVED. Corrected in place. D-11 and T-06 carry the reasoning.
- Q3 (was: the #811 split ruling) — RESOLVED by operator ruling of 2026-08-24. D-07 is the strike
  record. Issue #811 stays OPEN and returns to the backlog.
- Q4: `notes/root-cause-*.md` is in no member's domain, so debug reports fall back to receipt paths.
- Q5: engineer DIGESTs carry no `files_touched`, so a member that wrote a receipt reported no files;
  the lead reconstructs it by hand. Schema gap or intended?
- Q6 (the #866 deadlock) — HALF CLOSED BY FEAT-42, and the note that said otherwise is now corrected.
  The dispatch end is fixed: `release_cmd` prints an absolute single-agent command, so a refusal no
  longer tells an agent to wipe every feature's live claims. The RETURN end is what T-04 still
  corrects. This feature does not close #866 and never claimed to.
- Q7: single-flight is keyed per checkout, so several orchestrators' children can share one registry
  when they run from one cwd.
