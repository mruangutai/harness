# Handoff — FEAT-2229-decision-dispositions, plan → build — written at 864ab473, seq-3

## Next

Enter build per `references/build-phase.md`: the plan's `github.build_entry` is opened and the station is `ready`. Run `gh-sync.py status <feature-dir> building`, then execute in dependency order — T-01 (`depends_on: []`) and T-02 (`depends_on: [T-01]`) are `execution_mode: main-session-direct` (DEC-174; T-01 cross_module over plan_merge/check.py, union.py, panel.py, harness_yaml.py, harness.json + template era key; T-02 docs over templates/plan.yaml, teams/plan.yaml, teams/validate.yaml, .omp/agents/harness-pm.md, patch-lane, validator-lead) and are NOT dispatchable to any lead: return them to the main session as two dependency-ordered segments, each with its `verify:` verbatim (plan.yaml T-01.verify, T-02.verify). T-03 (`depends_on: [T-01, T-02]`, `execution_agent: harness-documentor`, DECISIONS.md D-01→DEC-254 + DEC-188 amend, index, SPEC) is the one squad task: the documentor persona belongs to the product squad, so dispatch it to `harness-product-lead` after T-01 and T-02 have PASS segments. Carry the simplify briefing row A-1 into T-01's segment: prefer the supplied `--root` for era configuration; reuse `plan_merge.guards._harness_root` only if discovery is needed (runs/r-20261121-simplify-eng/digest.md).

## Trust

- Plan signed, `approval.status: approved`, `status: ready`, rework ruling 3 rounds / 90 min, `signed_task_hashes` for T-01..T-03 — plan.yaml:3-7, feature.json `rework`/`signed_task_hashes`, notes/answers-2026-11-21-signoff.md — verified-at 864ab473
- `plan-merge.py check --root <worktree>` exits 0: 3 tasks, 20 anchors, 0 failures — runs/r-20261121-plan-c2-product/digest.md adequacy_notes — verified-at 46e7437f
- Panel cycle 2 recorded with scope ran and the c1 high substance finding PF-c88b62ae… `disposition: resolved` by T-01; should-not-exist/design/goalcheck skipped with reasons — plan.yaml `panel:` block — verified-at 46e7437f
- Goal-check at plan exit graded all three perspectives pass — notes/research-FEAT-2229-decision-dispositions-goalcheck-plan.md — verified-at 46e7437f
- `cycles_used` is 0; the plan run's FAIL was scope's substance finding applied in-run and re-paneled, not a rework send-back — feature.json `runs[]`, `judgements[]` (regate continue) — verified-at 864ab473
- Simplify pass (DEC-195) ran over the plan draft, flag-only; S-2 folded into T-03.intent, A-1 is the implementation briefing row above, R-1/S-1/A-2 leave — runs/r-20261121-simplify-eng/digest.md, notes/research-decision-dispositions-simplify-c2.md — verified-at 46e7437f
- `github.build_entry: opened`, milestone 117, parent issue 2277 — feature.json `github` — UNVERIFIED (reported by Main; re-read feature.json before `status building`)

## Dead ends

- No validate-time script for disposition grading: pm's goal-check grades each amend/strike row like an SC — grilling artifact `## Settled` (.harness/notes/grilling-decision-dispositions-2026-11-21.md), BRIEF SC-05 — verified-at 46e7437f
- No reciprocal-link check, no `relied_on_by`, no DECISIONS.md prose blast-radius line, no general stale-decision detection — BRIEF.md `## Out of scope` — verified-at 46e7437f
- No backfill or refusal of plans drafted before `decision_dispositions_era_start`; this plan itself predates the key and is not graded by the new check — BRIEF SC-03, DEC-227 — verified-at 46e7437f
- Do not dispatch T-01 or T-02 to a lead: `check-domain` resolves their `files:` to NOBODY, so a squad write is refused mid-run — plan.yaml T-01/T-02 `execution_reason` — verified-at 46e7437f

## Working set

- .harness/harness/features/FEAT-2229-decision-dispositions/plan.yaml (tasks T-01..T-03, `decisions_affected:`)
- .harness/harness/features/FEAT-2229-decision-dispositions/BRIEF.md (SC-01..SC-07, perspectives)
- .harness/harness/features/FEAT-2229-decision-dispositions/feature.json
- .harness/harness/features/FEAT-2229-decision-dispositions/runs/r-20261121-simplify-eng/digest.md (A-1 briefing row)
- /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/references/build-phase.md

## Done when

Scope: build entry recorded and T-01's main-session-direct segment returned for execution
Authority: brief-perspective:.harness/harness/features/FEAT-2229-decision-dispositions/BRIEF.md#code maintainer
Authority: plan-task:T-01.verify
