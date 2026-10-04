# Handoff — BUG-1016-worktree-relative-paths, validate → ship — written at 8c370f7c, seq-9

## Next

Main session presents `notes/ship-review-validate-c3-validator.md` to the operator and
runs ship on acceptance: `gh-sync.py ship` from the MAIN checkout (not the worktree) with
`--body-file` naming the briefing, backlog rows B-1..B-6 as issues unless struck, then
merge `feat/BUG-1016-worktree-relative-paths` at tip 8c370f7c (code paths identical to the
pin ef9cbce2). No orchestrator run remains: validate PASS at `runs/validate-c3-validator`
with `must_fix: []`, SC-01..SC-07 all met (plan.yaml T-01, T-02; BRIEF SC-01..SC-07).

## Trust

- validate c3 PASS, must_fix empty, severity_max none, SC-01..SC-07 met — `runs/validate-c3-validator/digest.md`, validate-digest.py harness-validator-lead exit 0 — verified-at 8c370f7c
- T-01 verify `python3 tests/unit/test-omp-hooks.py` 124 pass / 0 fail, exit 0 — orchestrator re-run in the worktree; qa c3 pinned re-run `notes/review-harness-qa-c3.md:16` — verified-at ef9cbce2
- R2 regression discriminates: adapter at a6a1e9c8^ with the new tests → 123/1, sole red is the R2 test; adapter restored, tree clean — orchestrator probe; qa c3 `notes/review-harness-qa-c3.md:20-21` — verified-at ef9cbce2
- Code paths (.omp, tests) byte-identical between pin ef9cbce2 and tip 8c370f7c — `git diff --quiet ef9cbce2 HEAD -- .omp tests` empty — verified-at 8c370f7c
- Board at `review` for #1016 #1570 #2016 #2017 #2018; plan.yaml `status: review` — gh-sync status review output, commit ef9cbce2 — verified-at ef9cbce2
- cycles_used 4/10; rework_minutes 40/90; rework_rounds 0/2; runs 9/20; amendments 0 — `feature-record.py spend`, feature.json — verified-at 8c370f7c

## Dead ends

- Simplify F1 (rootedHooks fixture duplicates governedUriHooks, tests/unit/omp-hooks.test.ts:1291) is operator-ruled backlog, never a fix run — `runs/build-simplify-eng/digest.md` — verified-at ef9cbce2
- `ast_edit` outside the hook mutation set is pre-existing and out of scope — `notes/t01-receipts-main-session.md` § Deviations, DEC-251 — verified-at ef9cbce2
- Documentor Q1 (re-sign D-01/T-02 singular `path` wording for ast_edit `paths: string[]`) is advisory, pm-owned, not a ship gate — `runs/t02-docs-product/digest.md` — verified-at ef9cbce2
- Q1 check-domain refusing `agent://` and `xd://` writes is a harness defect outside this diff — `runs/validate-c3-validator/digest.md` open_questions — verified-at ef9cbce2

## Working set

- .harness/harness/features/BUG-1016-worktree-relative-paths/notes/ship-review-validate-c3-validator.md
- .harness/harness/features/BUG-1016-worktree-relative-paths/feature.json
- .harness/harness/features/BUG-1016-worktree-relative-paths/plan.yaml
- .harness/harness/features/BUG-1016-worktree-relative-paths/runs/validate-c3-validator/digest.md
- .harness/harness/features/BUG-1016-worktree-relative-paths/STATE.md

## Done when

Scope: operator accepts the ship briefing and the main session ships and merges 8c370f7c
Authority: brief-perspective:.harness/harness/features/BUG-1016-worktree-relative-paths/BRIEF.md#operator
Authority: brief-perspective:.harness/harness/features/BUG-1016-worktree-relative-paths/BRIEF.md#code maintainer
