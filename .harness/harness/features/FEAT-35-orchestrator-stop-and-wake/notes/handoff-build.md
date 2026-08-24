# Handoff — FEAT-35, build → commit + validate — written at d7e8c66, seq-4

## Next

All five tasks are BUILT and every gate passes. The next act is the operator's: commit the branch,
then decide the validate phase. Whoever commits MUST write `status: done` for T-04 and T-05 in
`plan.yaml` in that same act — both still read `building` because the playbook couples the `done`
write to the commit, and no commit was authorised in this phase. That coupling has a seam gap worth
naming: both tasks are `execution_mode: team`, so the mirror table assigns the `done` write to the
orchestrator, but the operator is committing from the main session, where no orchestrator is present.

## Trust

- T-04 landed: DEC-201 at `.harness/harness/docs/DECISIONS.md:6800`, index row 219, and the task's
  own `verify:` printed `T-04-PASS` — re-run by the orchestrator, not relayed — verified-at d7e8c66
- The id correction is complete: `plan.yaml` contains ZERO occurrences of `DEC-200`, and the
  `approval:` mapping still reads `approved`/`operator`/`2026-08-23` — read at source — verified-at
  d7e8c66
- `.claude/skills/harness/SKILL.md:50` reads `(DEC-201)`, so the citation now resolves — grepped —
  verified-at d7e8c66
- T-05 landed: registered at `run-unit-tests.sh:17`, 9/9 green at HEAD, 9 named failures against the
  `569d417` copy covering all eight assertions, `--kind unit` exits 0 — all re-run by the
  orchestrator — verified-at d7e8c66
- SC-05 is MEASURED, superseding this note's seq-3 claim that it was unverified: the plan-phase
  orchestrator survived a 1057.1s gap past the 600s watchdog with zero stall calls. **The limit
  travels with the number** — that run was under a dispatch-level OVERRIDE, not the rewritten
  playbook, so it proves the BEHAVIOUR and not the causal link — main session's measurement,
  recorded in notes/answers-t04-build-2026-08-24.md — verified-at d7e8c66
- DEC-201's incident sentence is UNVERIFIED and internally tense: it attributes both the 342
  `echo hold` calls and the watchdog death to ONE orchestrator, while its own control paragraph
  says the two failing sidecars are distinct and the dead one had ZERO assistant events — which
  cannot be an agent that made 450 Bash calls. Settle against #744 before or shortly after commit.
- `feature.json`'s `t04-product` entry now reads PASS where it read ESCALATE. The escalation is NOT
  erased: it survives in that run's digest, in the lead's `escalations:` trace, and in
  `cycles_used: 2` — read at source — verified-at d7e8c66

## Dead ends

- Do not `git add -A`; the tree carries orchestrator-owned state beside the task files — `git status
  --porcelain` at d7e8c66
- Do not move any GitHub card by hand; the four INV-26 rows are ACCEPTED and three close from the
  PR's `Closes` lines at merge — notes/answers-t04-build-2026-08-24.md Q3
- Do not fix the missing DEC-NN collision guard or T-05's line-scoped assertion 6 here; the operator
  files both as tickets — notes/answers-t04-build-2026-08-24.md Q4/Q5
- Do not amend `plan.yaml`'s T-04 intent line reading "after DEC-199"; it is a harmless historical
  artifact and pm was correctly scoped to the two id occurrences — runs/t04-product/digest.md Q1

## Working set

- `.harness/harness/features/FEAT-35-orchestrator-stop-and-wake/plan.yaml`
- `.harness/harness/features/FEAT-35-orchestrator-stop-and-wake/notes/answers-t04-build-2026-08-24.md`
- `.harness/harness/features/FEAT-35-orchestrator-stop-and-wake/runs/t04-product/digest.md`
- `.harness/harness/features/FEAT-35-orchestrator-stop-and-wake/runs/t05-eng/digest.md`
- `.harness/harness/docs/DECISIONS.md`
