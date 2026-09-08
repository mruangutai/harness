# STATE

## Current

- feature: BUG-124-run-dir-squad-suffix
- run: [.]harness/harness/features/BUG-124-run-dir-squad-suffix/runs/2026-09-07-1-eng/state.yaml
- squad: eng
- status: in_progress

**ENG SEGMENT COMPLETE. The build's remaining segments are qa, then SIMPLIFY, then the
Building -> Review seam.** Station `building`; T-01 and T-02 `building`; T-03 still `ready`.
`cycles_used: 1` (the eng run was a clean first pass and adds ZERO — no send-backs), eight runs
against budgets 10 and 20. Everything below is committed at `e7994376` on
`feat/BUG-124-run-dir-squad-suffix`. No `review_sha` exists and none is owed until the seam.

**Next (cited to plan.yaml):** the qa segment — `harness-qa` through `harness-validator-lead`,
enforcing `test_matrix` over the eng diff. It has ONE named thing to audit beyond the matrix: Q1
below, the test-first ordering exception the eng lead self-reported. Then SIMPLIFY to
`harness-eng-lead` (its dispatch must tell the lead to read `harness-simplify/SKILL.md` first), then
pin `review_sha` and `gh-sync.py status <feature-dir> review`.

**T-03 is NOT eng work and was correctly left undone.** `execution_mode: main-session-direct`,
`depends_on: [T-02]` — `check-domain --resolve` answers NOBODY for `.claude/skills/harness/SKILL.md`.
It is a pre-ship step for the main session, not a task any squad can be handed.

Trust (claim — pointer — verified-at e7994376, ORCHESTRATOR-MEASURED unless attributed):
- T-01's `verify:` exits 0, run verbatim by me from the worktree root: 62 of 62 unit cases pass
  including the 15 new run-dir cases, and the inline assertion block passes (`t01-eng`,
  `plan-product`, `2026-08-26-2-plan-product` accepted; `eng-t01` and `plan_product` rejected;
  the `[.]harness/` spelling invisible to `run_dir_refs`; every form prefixed `<task-or-purpose>-`).
- T-02's `verify:` exits 0, run verbatim by me: 69 of 69 integration cases pass and the live guard
  really refuses the inverted-slug payload.
- **The RED proof is mine, not a relayed claim.** I re-ran the NEW suite against the pre-change
  guard — `DISPATCH_GUARD_BIN=/Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/dispatch-guard.sh`,
  md5 `ca904b2906ad8d44662db428cb2dbc89`, byte-identical to `6d969ed3`'s copy — and got 61 of 69
  with exactly these 8 red: 18a (x2), 18b, 18g, 21-message, 22 (x2), 23-message. The plan required
  (a),(b),(f),(g) red; (e) and (i) also went red because the member asserted their message TEXT
  rather than only the exit code, which is stronger than the plan asked for.
- Both test files are PURELY ADDITIVE — `git diff --numstat` shows 183/0 and 115/0, so the
  docstring's "no existing case edited" holds mechanically, and the 48 pre-existing checks are
  among the 61 that survive the red run.
- `harness_boundary.py` is +99/-0: no existing symbol changed, so the hooks that import it
  (check-domain, bash-write-guard) cannot have regressed by deletion.
- The check sits AFTER the `harness_boundary`/`inflight_registry` import block and BEFORE `_root_for`
  and the single-flight claim — read in the diff, and case 18g proves a refusal strands no claim.
- The two SKIPPED texts are distinct and neither contains the other (cases 21 and 23 each assert
  its own text present AND the other absent).
- The refusal never prints a raw anchored run-dir path: it prints the tail through
  `.replace(".harness/", "[.]harness/")`, and case 18h pastes the exact stderr back into a governed
  dispatch and is not refused.
- The vocabulary is derived, never literal: case 22 invents `oddsquad` in a throwaway manifest and
  the refusal names `<task-or-purpose>-oddsquad`. No squad token is spelled in the guard.
- Operator signature is on disk and committed at `80ce35d1`: BRIEF `status: approved`, plan
  `approval.status: approved` with five `rulings` overruling R-1..R-5.
- No stray registry claim: `inflight_registry.py list` names no BUG-124 claim after my verify runs.

Dead ends for the next phase:
- Do NOT re-litigate R-1..R-5 — `plan.yaml` `approval.rulings` records the operator's overrule of
  each, with a reason. They are closed, not deferred.
- Do NOT re-run the eng verifies as if unmeasured, and do NOT re-derive the RED proof by copying the
  bin tree: `bash-write-guard.sh` refuses an orchestrator `cp` to a temp dir, and pointing
  `DISPATCH_GUARD_BIN` at the MAIN checkout's guard is the working route (it is pre-change and
  md5-identical to `6d969ed3`).
- Do NOT hand T-03 to a squad (see the paragraph above).
- Do NOT run the whole `run-unit-tests.sh` while four sibling BUG flows are live; the two named test
  files are the scoped proof.
- Do NOT edit `plan.yaml` by hand; `plan-merge.py` is the only write route and `approval:` is the
  main session's alone.
- The plan-phase handoff note still cannot be written — `handoff_done_when.py` grades a
  worktree-hosted feature against the OWNER root and refuses both the relative and the absolute
  spelling (Q2). This `## Current` is the supported disk-only substitute.

Working set: plan.yaml (tasks at 231; T-03 at 491), notes/receipt-harness-backend-dev-T-01-c1.md,
notes/receipt-harness-backend-dev-T-02-c1.md, .claude/skills/harness/bin/dispatch-guard.sh,
tests/integration/test-dispatch-guard.py

## Open Questions

- Q1 (for qa, non-blocking, self-reported by the eng lead and NOT hidden): T-02's production code
  was written BEFORE its new integration cases; the member then reverted `dispatch-guard.sh` to the
  pre-T-02 state, wrote the cases, watched them fail, and reapplied the implementation
  byte-verified. So the RED evidence is genuine — I reproduced it independently, above — but the
  AUTHORING ORDER was not test-first and qa's audit will see it. Recorded here so the audit finds it
  declared rather than concealed. T-01 is not implicated.
- Q2 (harness defect, one class, two symptoms, both diagnosed, both for the harness owner):
  worktree-hosted features are graded against the OWNER checkout root. (a)
  `handoff_done_when.problems()` receives the owner root while the note's feature-dir prefix comes
  from its own worktree-relative path (handoff_done_when.py:11,51-54), and an absolute pointer is
  separately refused as "is absolute" (:69-70), so there is NO legal spelling and no handoff note
  can be written at all. (b) `check-state.sh` globs the owner checkout's `.harness/*/features/*`
  (:118-120), so a full run from inside this worktree cannot grade this feature.
- Q3 (advisory, no task): three pre-D-05 artifacts keep raw anchored `eng-t01` paths
  (`runs/goalcheck-plan-product/digest.md:11`, `runs/planpanel-validator/digest.md:19`,
  `notes/research-BUG-124-goalcheck-plan-c0.md:67`). Now that T-02 has landed IN THIS WORKTREE,
  pasting one verbatim into a dispatch will be refused once the change reaches the main checkout —
  recoverable in one re-spelling. Left as-is on purpose: rewriting a recorded artifact to look
  better falsifies the record.
- Q4 (operator, already accepted at signature): T-02's SECOND parse of `team-config.yaml` inside the
  derivation subprocess. It shipped as designed and is what makes case 23 distinguishable from
  case 21.
