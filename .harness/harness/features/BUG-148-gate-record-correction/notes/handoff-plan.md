# Handoff — BUG-148-gate-record-correction, plan → build — written at 41c16c7, seq-1

## Next

Await the operator's signature ruling on the four batched questions (STATE.md `## Open Questions`;
Q1 is blocking). On `approved` with no plan change: dispatch T-01 to `harness-product-lead` for
`harness-documentor` (rewrite DEC-174's evidence sentence, regenerate `DECISIONS-INDEX.md`), then
execute T-02 yourself in the orchestrator lane — `.harness/*/features/*/STATE.md` resolves to
`harness-orchestrator` and no member persona holds it. Both tasks are `depends_on: []`; T-01 first
keeps the index regeneration and its integration test in one commit.

## Trust

- `gen-decisions-index.py --check` fell through to the WRITE path on 2026-08-03 and exited 0 having regenerated the index; argv validation landed later at `ffbdbfa1` — `git show 99b380e3:.claude/skills/harness/bin/gen-decisions-index.py:371`, `git log -S` — verified-at 41c16c7, independently confirmed by both panel readers
- T-01 and T-02 route to granted lanes — `check-plan-routes.py` exit 0, "OK T-01 granted to harness-documentor / OK T-02 granted to harness-orchestrator" — verified-at 41c16c7
- SC-04's integration suite is green pre-correction and reddens only if the index is not regenerated — `bash .agents/skills/harness/bin/run-unit-tests.sh --kind integration` exit 0 — verified-at 41c16c7 by pm, NOT re-run by the orchestrator
- The panel record in `plan.yaml` `panel:` satisfies INV-32 — `check-state.sh` reports no INV-32 finding against this feature — verified-at 41c16c7

## Dead ends

- `git merge-base origin/main <sha>` is not a usable diff baseline here: it is `8bdc2477` and the range already carries three foreign paths — `git diff --name-only $(git merge-base origin/main HEAD)..HEAD` — verified-at 41c16c7. SC-03/SC-05 use the branch base `41c16c7` instead
- An appended dated note in `DECISIONS.md` is foreclosed, not merely disfavoured — DEC-205 plus `tests/integration/test-gen-decisions-index.py:844-870` rejects an `**Amendment` construct — verified-at 41c16c7 by the code reviewer
- A `Write` of FEAT-05's `STATE.md` is denied pre-hoc (165 lines vs the 120-line budget, 7 headings vs 2) — `check-domain.sh:1796-1824` — verified-at 41c16c7; T-02 uses `Edit`

## Working set

- .harness/harness/features/BUG-148-gate-record-correction/BRIEF.md
- .harness/harness/features/BUG-148-gate-record-correction/plan.yaml
- .harness/harness/features/BUG-148-gate-record-correction/STATE.md
- .harness/harness/features/BUG-148-gate-record-correction/notes/research-BUG-148-goalcheck-plan-c0.md
- .harness/harness/features/BUG-148-gate-record-correction/notes/review-harness-code-reviewer-planpanel-c0.md

## Done when

Scope: the operator's signature on BUG-148's plan package, with rulings on Q1–Q4
Authority: approval:.claude/worktrees/harness/BUG-148-gate-record-correction/.harness/harness/features/BUG-148-gate-record-correction/BRIEF.md#Approval
