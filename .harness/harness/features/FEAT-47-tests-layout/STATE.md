# STATE

## Current

- feature: FEAT-47-tests-layout
- run: .harness/harness/features/FEAT-47-tests-layout/runs/2026-09-02-01-advisor-validator/state.yaml
- squad: none
- status: awaiting-user

Plan is signed (`approval.status: approved`, Mike Ruangutai, 2026-09-02); the feature and all seven
tasks stand at station `ready`. Nothing has been built: `dafd8e8` carries plan artifacts only against
`origin/main` `e74e088`. FEAT-48 has merged, so the build's cross-feature precondition holds.

**The build cannot be executed by this orchestrator or by any squad beneath it.** All seven tasks
declare `execution_mode: main-session-direct` citing DEC-174; the live domain hook denies
`harness-orchestrator` every implementation surface (measured — a probe Write to
`.claude/skills/harness/bin/.orch-probe.tmp` returned `check-domain: BLOCKED`); `tests/**` and
`.harness/team-config.yaml` resolve to `NOBODY`; and `check-state.sh` INV-17 independently reports
that no squad runs this feature. A `fable-advisor` consult
(`runs/2026-09-02-01-advisor-validator/`) found no legitimate squad-executable route.

The handback for the main session — execution order, stale premises, per-task build-time derivations
and the residual backlog — is `notes/handback-segments-2026-09-02.md`.

Bookkeeping reconciled this run: feature.json's illegal `status` key removed and both validator runs
recorded with `code_grade: n_a`; `cycles_used: 2` derived from `panel.cycle: 2` and the c0/c1/c2
plan-panel artifacts; every station written through `plan-merge.py`; the GitHub mirror opened
(milestone #42, parent #1236, sub-issues #1237-#1243); the malformed cycle-2 lead digest repaired by
its own squad. `check-state.sh` now reports zero FEAT-47 violations.

## Open Questions

- Q1 (blocking, for the operator): every FEAT-47 task is `main-session-direct` under DEC-174 and the
  advisor confirms no squad route exists. Accept the handback and execute the seven tasks directly in
  the order T-01, T-02, T-03, T-04, T-05, T-07, T-06 — or send the lanes back to pm for a re-plan
  under a new signature. Blocked: the entire build phase.
