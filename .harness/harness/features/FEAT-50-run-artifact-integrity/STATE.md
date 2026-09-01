# STATE

## Current

- feature: FEAT-50-run-artifact-integrity
- run: .harness/harness/features/FEAT-50-run-artifact-integrity/runs/2026-08-31-7-product/state.yaml
- squad: none
- status: awaiting-user

Plan phase COMPLETE, amended under the operator's rulings, re-panelled, and back at its
user gate. `BRIEF.md` and `plan.yaml` are `approval.status: pending`; only the main
session signs. **No `high`, `critical` or unrated panel finding survives** — that is the
fact the signature gate turns on, and it is what changed about signability.

Cycle 1 ran four sequenced squad segments: the plan amendment, pm's goal-check of the
amended plan against stated intent, the `plan-panel` team, and pm's transcription of
`panel:`. 7 of 10 cycles used, 10 of 20 runs recorded.

The plan covers issues #1056, #1057, #1058 and the `validate-digest.py` artifact-path
resolution defect the operator newly authorized. 9 REQ, 21 SC, 12 tasks (10
`main-session-direct` under DEC-174, 2 `team`), 11 decisions, 14 lane rows, `panel:`
recording 3 readers `ran` and 11 open findings at `severity_max: med`. All four rulings
are recorded verbatim in `notes/answers-2026-08-31-plan.md`: INV-32 answered `choice: d`
so SC-11 requires `check-state.sh` exit 0 unweakened and no INV-32 work is planned; both
`high` findings closed by FIX with `approval.rulings` absent (`PF-3d9ac1d0…` by
REQ-08/T-09/T-10/D-10, `PF-964d6356…` by T-02 step 5 and SC-17); the fourth defect
planned as REQ-09/T-11/T-12/D-11/SC-20/SC-21; Q4 out of scope and untouched.

The external INV-32 hold is LIFTED — the operator reported the fix merged into `main`,
so D-09's precondition is met. **Build does not start**: that is the operator's
instruction and the plan phase's own boundary. The feature branch is not yet updated
from `origin/main` (the main session does that after this commit), which is why SC-11 is
not gradeable in this worktree.

Gates at the amended plan: `check-plan-routes.py` exits 0, `0 violation(s) across 1
plan(s)`, 9 DEVIATION lines all DEC-174 carve-outs. `harness_yaml.load_plan` loads
clean. All eleven `PF-` ids independently recomputed with `panel_findings.finding_id`
and all eleven match, which is what proves the five carried cycle-0 summaries were
carried verbatim. Nothing under `.claude/skills/` was modified in this phase.

## Open Questions

- Q1 (non-blocking, next phase): SC-11's clearing act for its rows 3–5 — the three
  DEC-156-failing lead digests under `runs/` — is owned by no task. pm's goal-check and
  panel finding `PF-b3e87de8…` reached this independently. The authoring leads' contexts
  are gone and a third party rewriting another agent's digest would falsify it
  (PRINCIPLES rule 15), so the honest disposition is the accepted-residual branch: the
  three cannot reach the default branch because `.gitignore:7` excludes
  `.harness/*/features/*/runs/**` (confirmed with `git check-ignore -v`) and the worktree
  is removed post-merge.
- Q2 (non-blocking, operator's to direct at signature): finding `PF-f52c5043…` (`med`) —
  T-03's binding sits inside `domain_check()`'s allow/shared branches while `classify`'s
  `not_a_domain_question` outcome returns earlier, so the two checkout-binding fixes are
  asymmetric in verdict-shape coverage. Measured and settled as INERT today: no
  production code sets `HARNESS_PROJECT_DIR`, so a governed agent's resolved root is
  always the main checkout and the premise cannot hold. Kept open at the reader's own
  severity; closing it would be a NEW task, never a severity change.
