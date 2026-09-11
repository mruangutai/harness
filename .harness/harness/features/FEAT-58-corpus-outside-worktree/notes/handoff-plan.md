# Handoff — FEAT-58-corpus-outside-worktree, plan → build — written at 8cd3934f, seq-8

## Next

Dispatch the build phase. The plan is signed, the station is `ready`, and Build entry has already
run — `feature.json` `github.build_entry` reads `opened`, so `start-task`'s preflight passes. Start
at N-01 (the synthetic fixture and the pre-change failing-test baseline) in `depends_on` order.
Every task is `main-session-direct` under DEC-174, so this feature has NO team-lane build segment:
the main session executes, and the orchestrator's `start-task` ownership does not apply to a
`main-session-direct` task.

**Before the first task: read `notes/mirror-ids-FEAT-58.md`.** The GitHub mirror cannot record this
feature's issue ids and `start-task` will refuse every task with "has no recorded issue". The mirror
is never a gate, so that refusal does not stop build — but do NOT re-run `gh-sync.py open` to
"fix" it, because it will create thirteen duplicate sub-issues.

## Trust

- `plan.yaml` `approval.status: approved` with seven rulings and `BRIEF.md ## Approval` approved-by mruangutai — orchestrator's own read of both files, not a digest claim — verified-at 8cd3934f
- Station `ready`; 13 tasks (N-11 a deliberate gap), 17 decisions, 10 REQ, 15 live criteria (SC-15 a deliberate gap) — orchestrator's own read — verified-at 8cd3934f
- `gh-sync.py:613` filters recorded issue ids through `re.fullmatch(r"T-\d+")` while `:604-608` filters `attached` not at all, which is why `attached` survived and `issues` did not — orchestrator's own read of both sites — verified-at 8cd3934f
- Milestone #66, parent #1641, N-01..N-14 → #1642..#1654, all created and attached — `gh-sync.py open` stdout, captured and transcribed to notes/mirror-ids-FEAT-58.md — verified-at 8cd3934f
- The panel found NOTHING STRUCTURAL and enumerated a producing mechanism for all ten REQs — runs/planpanellast-validator/digest.md — verified-at 8cd3934f
- N-14's three runs discharge H-01 and M-01 — pm and the product lead, argued at source; no test exists yet — UNVERIFIED

## Dead ends

- Re-running `gh-sync.py open`: its skip check reads the emptied map, so it duplicates rather than repairs — gh-sync.py:1185 against :609-614 — verified-at 8cd3934f
- The cycle-8 red-proof staging (stage the pre-fix `feature.json`-keyed derivation, expect a red on 89-versus-79): WITHDRAWN by the operator at signature and now excised from N-13. It yields MISSING=[] / UNEXPECTED=10 arithmetically, which clause 1 tolerates, so it records a FALSE red — notes/answers-operator-c9.md Q1 — verified-at 8cd3934f
- Asserting a gate's decision by exit code, a persisted uniqueness index, remedy (b) for the audit sets, correcting the FEAT-02/FEAT-03 records, `fetch-depth: 0` on CI, and the hardlink half: each rejected on the record with its reason — D-14, D-17, answers-operator-c3/c5/c6 — verified-at 8cd3934f
- Another plan amendment: the operator ruled cycle 8 the last fix round and the unspent cycle is build's margin — notes/answers-operator-c8.md Q8 — verified-at 8cd3934f

## Working set

- .harness/harness/features/FEAT-58-corpus-outside-worktree/plan.yaml
- .harness/harness/features/FEAT-58-corpus-outside-worktree/BRIEF.md
- .harness/harness/features/FEAT-58-corpus-outside-worktree/notes/mirror-ids-FEAT-58.md
- .harness/harness/features/FEAT-58-corpus-outside-worktree/notes/answers-operator-c9.md
- .harness/notes/dod-worktree-corpus-2026-09-10.md

## Done when

Scope: every planned task has a PASS run recorded in feature.json and the test matrix is green
Authority: approval:.harness/harness/features/FEAT-58-corpus-outside-worktree/BRIEF.md#Approval
