# Handoff — FEAT-2557, plan → build — written at 2a9d96cb, seq-2

## Next

After the operator re-signs (`plan-merge.py sign-approval`, main session only), the main session
builds plan.yaml task T-01 directly (DEC-174: the plan is wholly main-session-direct, so no lead
is dispatched for the build). T-01 traces SC-01..SC-06 and its intent orders the work in three
steps: `bin/LAYOUT.md`, then the skill and `AGENTS.md`, then DEC-259 and the index. T-01's
verify is the terminal check; run it after all three steps.

## Trust

- plan.yaml carries exactly one task, T-01, main-session-direct over the five ruled files, approval pending — `.harness/harness/features/FEAT-2557-code-layout-pattern/plan.yaml` tasks — verified-at 2a9d96cb
- T-01's merged verify keeps every assertion of the three signed verifies — `.harness/harness/features/FEAT-2557-code-layout-pattern/plan.yaml` T-01.verify against `git show ce74dbff` of the same file — verified-at 2a9d96cb
- BRIEF differs from the signed text only in the Constraints routing bullet; Approval reads pending — `git diff ce74dbff 2a9d96cb` on BRIEF.md — verified-at 2a9d96cb
- check-state reports no INV-32 for this feature when run from this worktree's own copy — `.claude/skills/harness/bin/check-state.py` — verified-at 2a9d96cb
- Source #2557, parent #2558 and T-01 card #2560 were placed at Plan by `gh-sync.py status plan` — `.harness/harness/features/FEAT-2557-code-layout-pattern/plan.yaml` status — verified-at 2a9d96cb
- `plan-merge.py check` and check-plan-routes report 0 failures on the one-task plan — `.harness/harness/features/FEAT-2557-code-layout-pattern/runs/revise-product/digest.md` — UNVERIFIED
- DEC-259 is free — `.harness/harness/features/FEAT-2557-code-layout-pattern/notes/answers-2026-11-27-signoff.md` — UNVERIFIED

## Dead ends

- No gh-sync.py verb reconciles the dropped-task cards #2559 and #2561: `status` skips a receipt whose task left the plan, and INV-26 reports both — `.harness/harness/features/FEAT-2557-code-layout-pattern/feature.json` github.issues — verified-at 2a9d96cb
- Re-routing LAYOUT.md or the decision record to a squad reopens INV-32 — `.harness/harness/features/FEAT-2557-code-layout-pattern/notes/answers-2026-11-27-inv32.md` — verified-at 2a9d96cb

## Working set

- `.harness/harness/features/FEAT-2557-code-layout-pattern/plan.yaml`
- `.harness/harness/features/FEAT-2557-code-layout-pattern/BRIEF.md`
- `.harness/harness/features/FEAT-2557-code-layout-pattern/notes/answers-2026-11-27-inv32.md`
- `.harness/notes/grilling-code-layout-pattern-2026-11-27.md` (main checkout, read-only)

## Done when

Scope: main session builds T-01 after re-signature
Authority: brief-perspective:.harness/harness/features/FEAT-2557-code-layout-pattern/BRIEF.md#code maintainer
Authority: plan-task:T-01.verify
