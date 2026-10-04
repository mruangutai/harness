# Handoff — BUG-1016-worktree-relative-paths, plan → build — written at 17fd638b, seq-3

<!-- Written late: the plan phase closed at signature 8d79d63d without this note; it is
     authored at the build re-entry after T-01 landed main-session-direct (DEC-174),
     before any build-phase run is recorded. -->

## Next

Record T-01 `done` (`plan-merge.py set-task-station --task T-01 --station done`; its
`[harness:t-01]` commit is 10f38a42), then dispatch T-02 as one `build` team run to
`harness-eng-lead`, who routes it to `harness-documentor` (plan.yaml T-02, DEC-251,
traces SC-07). Inputs: plan.yaml T-02 intent, BRIEF.md SC-07 + Constraints, and
`notes/t01-receipts-main-session.md` (the ast_edit `paths: string[]` deviation the DEC
must describe). After T-02 PASS: simplify (eng-lead), seam commit, pin review_sha,
`gh-sync status review`, validate.

## Trust

- Plan and BRIEF are signed `approved` with rework 2 rounds / 90 min — plan.yaml `approval:`, BRIEF.md `## Approval`, feature.json `rework` — verified-at 8d79d63d
- T-01 code + tests landed in the worktree — `git show --stat 10f38a42` (harness-hooks.ts +135/−?, omp-hooks.test.ts +285) — verified-at 10f38a42
- T-01 verify `python3 tests/unit/test-omp-hooks.py` exit 0, 123 pass / 0 fail; 14 red-first cases named — `notes/t01-receipts-main-session.md` (main-session receipt) — UNVERIFIED by this orchestrator; re-run at the pin before validate
- `github.build_entry: opened`; board at `building` for #1016 #1570 #2016 #2017 #2018 — feature.json `github`, STATE.md — verified-at b258df4e
- Panel c1 recorded with 3 findings resolved; goal-check (plan) passed both perspectives — plan.yaml `panel`, `notes/research-…-goalcheck-plan.md` — verified-at 935519f9

## Dead ends

- T-01 is never dispatched to a squad; its cycle attribution is none (main-session-direct is not a run) — plan.yaml T-01 `execution_mode`, ledger.md — verified-at 8d79d63d
- `ast_edit` being outside the hook's mutation set (`write`, `edit`, `bash`) is pre-existing and NOT in scope for a fix cycle here — `notes/t01-receipts-main-session.md` § Deviations — source: main-session receipt
- The T-02 verify diff must run against the worktree's own `gen-decisions-index.py`; the generator is not to be edited — plan.yaml T-02 intent — verified-at 8d79d63d

## Working set

- .harness/harness/features/BUG-1016-worktree-relative-paths/plan.yaml
- .harness/harness/features/BUG-1016-worktree-relative-paths/BRIEF.md
- .harness/harness/features/BUG-1016-worktree-relative-paths/notes/t01-receipts-main-session.md
- .harness/harness/features/BUG-1016-worktree-relative-paths/feature.json
- .harness/harness/features/BUG-1016-worktree-relative-paths/STATE.md

## Done when

Scope: T-02 documentation run dispatched and closed PASS
Authority: brief-perspective:.harness/harness/features/BUG-1016-worktree-relative-paths/BRIEF.md#code maintainer
Authority: plan-task:T-02.verify
Authority: brief-sc:SC-07
