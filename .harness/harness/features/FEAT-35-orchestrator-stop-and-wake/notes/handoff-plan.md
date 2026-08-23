# Handoff — FEAT-35, plan → build — written at 569d417, seq-2

## Next

Do NOT dispatch anything until BRIEF.md and plan.yaml both read `approved`; mission build stops at
step 0 BLOCKED otherwise. The plan then spans TWO lanes and is no longer single-lane: T-01, T-02 and
T-03 are `main-session-direct` on SKILL.md and the main session executes them itself; T-04 goes to
harness-documentor and T-05 to harness-dev-ops, both `execution_mode: team`, so both enter through
their lead. T-05 depends_on T-03.

## Trust

- Both artifacts are unsigned: plan.yaml:5 `status: pending`, BRIEF.md:135 `status: pending` — read
  at source — verified-at 569d417
- check-plan-routes.py on the revised plan: 5 OK rows, no DEVIATION, `0 violation(s) across 1
  plan(s)` — re-run by the orchestrator, not relayed — verified-at 569d417
- FIX 1 is in T-02's `verify:` and not intent-only — all four literals grepped at plan.yaml:141 —
  verified-at 569d417
- FIX 2 landed: BRIEF.md:67-74 makes `check-domain.sh --resolve` returning NOBODY the operative
  test and cites am.4 for the CATEGORY only — verified-at 569d417
- T-01's verify greps "The single-flight refusal on your return is EXPECTED" and asserts the
  absence of both stay-alive strings — plan.yaml:80 — verified-at 569d417
- The #551 refusal is PER RETURN, not per run: it fired twice in the plan phase, once per
  dispatch-and-stop return. T-01's intent scopes it correctly as "refuses that return once" —
  measured in this session — verified-at 569d417
- The self-id mechanism works: a unique nonce matched exactly one sidecar (af05a0d5a321741b6) and
  context-watch.py takes it POSITIONALLY, not as --agent — run here — verified-at 569d417
- Whether a STOPPED orchestrator survives past 600s with a live child — UNVERIFIED. SC-05 is the
  only thing that measures it, and it is the feature's load-bearing assumption.

## Dead ends

- Do not merge or rebase `chore/744-never-wait-for-a-lead`; D-03 rules absorb-and-abandon and T-01
  rewrites the exact 5 lines f5194d2 inserts — plan.yaml D-03 — verified-at 569d417
- Do not write a DEC-174 amendment 5 for run-unit-tests.sh; D-08 rules T-05 does not make it a gate
  — plan.yaml D-08 — verified-at 569d417
- Do not plan the leads' wait pattern or the fabricated-completion incident; both are OUT by
  operator ruling — notes/answers-2026-08-23-01.md — verified-at 569d417
- Do not design a new handoff seam for the context-triggered case; D-04 rules the existing capped
  note carries it — plan.yaml D-04 — verified-at 569d417

## Working set

- `.harness/harness/features/FEAT-35-orchestrator-stop-and-wake/plan.yaml`
- `.harness/harness/features/FEAT-35-orchestrator-stop-and-wake/BRIEF.md`
- `.harness/harness/features/FEAT-35-orchestrator-stop-and-wake/notes/answers-2026-08-23-01.md`
- `.harness/harness/features/FEAT-35-orchestrator-stop-and-wake/runs/2026-08-23-02-product/digest.md`
- `.claude/skills/harness/SKILL.md`
