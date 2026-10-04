# Handoff — BUG-1016-worktree-relative-paths, build → validate — written at fe8c50ea, seq-6

## Next

Dispatch ONE `validate` team run (`validate-validator`) to `harness-validator-lead` over
`review_sha` 8211687f: qa (test_matrix gate, fail_first evidence per automated SC-01..SC-06
from `notes/t01-receipts-main-session.md`), code, security, ui (self-scopes out: adapter +
docs diff), pm goalcheck (SC-01..SC-07, second and last grade, written to
`notes/research-BUG-1016-worktree-relative-paths-goalcheck-validate-c1.md`). Inputs:
plan.yaml T-01/T-02, BRIEF.md SC-01..SC-07, DEC-251 at DECISIONS.md @8012. Any must-fix in
`.omp/extensions/harness-hooks.ts` or `tests/unit/omp-hooks.test.ts` is DEC-174
main-session-direct: NOT a `fix` run — return it to the main session as a blocking question.

## Trust

- T-01 verify `python3 tests/unit/test-omp-hooks.py` exit 0, 123 pass / 0 fail — re-run by orchestrator in the worktree — verified-at c2d4d7b6
- T-02 verify (index regenerate | diff) exit 0, empty diff — re-run by orchestrator — verified-at 89b7d960
- DEC-251 present in DECISIONS.md and DECISIONS-INDEX.md, both tasks `done` in plan.yaml — `git show 8211687f:.harness/harness/docs/DECISIONS.md` @8012, plan.yaml T-01/T-02 `status: done` — verified-at 8211687f
- Code paths unchanged between c2d4d7b6 and the pin 8211687f — `git diff --stat c2d4d7b6 8211687f -- .omp tests .harness/harness/docs` empty — verified-at 8211687f
- Simplify run build-simplify-eng: 8/8 angle steps PASS, nothing applied; lead verdict FAIL on a false premise (feature.json delta was its own run-start + host token stamp), 1 cycle charged to satisfy the FAIL-cycle invariant — `runs/build-simplify-eng/digest.md`, feature.json judgements — verified-at c2d4d7b6
- Board at `review` for #1016 #1570 #2016 #2017 #2018 — gh-sync output, plan.yaml `status: review` — verified-at 8211687f

## Dead ends

- `ast_edit` outside the hook mutation set is pre-existing and out of scope for a fix cycle — `notes/t01-receipts-main-session.md` § Deviations, DEC-251 — verified-at 8211687f
- Simplify F1 (rootedHooks fixture duplicates governedUriHooks, tests/unit/omp-hooks.test.ts:1291) is flag-only, DEC-174 file; relayed to main session, never a `fix` run — `runs/build-simplify-eng/digest.md` — verified-at c2d4d7b6
- Documentor Q1 (re-sign D-01/T-02 singular-`path` wording for ast_edit `paths: string[]`) is advisory, pm-owned, not a validate input — `runs/t02-docs-product/digest.md` — verified-at 89b7d960

## Working set

- .harness/harness/features/BUG-1016-worktree-relative-paths/feature.json
- .harness/harness/features/BUG-1016-worktree-relative-paths/plan.yaml
- .harness/harness/features/BUG-1016-worktree-relative-paths/BRIEF.md
- .harness/harness/features/BUG-1016-worktree-relative-paths/notes/t01-receipts-main-session.md
- .harness/harness/features/BUG-1016-worktree-relative-paths/STATE.md

## Done when

Scope: validate run dispatched over 8211687f and closed with a clean panel
Authority: brief-perspective:.harness/harness/features/BUG-1016-worktree-relative-paths/BRIEF.md#operator
Authority: brief-perspective:.harness/harness/features/BUG-1016-worktree-relative-paths/BRIEF.md#code maintainer
