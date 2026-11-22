# Handoff — BUG-2294-prune-keeps-run-digests, build → validate — written at 8101c29daab5a951659f7c7daaa98fb5d45b01e3, seq-1

## Next

Pin `review_sha` to the seam commit, run `gh-sync.py status <feature-dir> review`, then ONE
`validate` dispatch to `harness-validator-lead` (`HARNESS-MISSION: validate`) over that sha,
inputs `feat` and `review_sha`, grading SC-01, SC-02 and SC-03 (BRIEF.md) against T-01
(plan.yaml). T-01 is `main-session-direct` (DEC-174): any `must_fix` routes back to the main
session, never to the engineering lead; the ruling is 1 round / 45 min.

## Trust

- T-01 verify (`python3 tests/unit/test-prune-run-evidence.py`) exits 0 with 20 PASS, 0 FAIL — /tmp run from the worktree — verified-at 8101c29d
- The code diff from base c1724230 touches exactly the five files T-01 owns (`git diff --stat c1724230 8101c29d`) — verified-at 8101c29d
- Red-first evidence against the c1724230 pruner (7 assertion failures, including the FEAT-2229 case losing all 10 cycle_evidence digests) — notes/red-first-T-01.md — UNVERIFIED (main-session claim; qa must re-grade it as `fail_first`)
- SIMPLIFY pass, four angles, no findings — notes/simplify-pass.md, commit d225287c — UNVERIFIED (main-session claim)
- Operator signature: BRIEF `## Approval` approved, plan.yaml `approval.status: approved`, rework 1 round / 45 min — notes/answers-2026-11-22-signoff.md, commit 128a7158 — verified-at 8101c29d

## Dead ends

- SC-02's check-state regression runs `--only INV-7`, not the whole table: a bare fixture trips unrelated repo-level rows (INV-27, INV-31) — notes/red-first-T-01.md — source: main-session judgement at build, do not grade the narrowing as a defect
- INV-17 suppresses `handoff-plan` for an all-main-session-direct plan; this note exists because validate is a squad run — check-state note at 8101c29d — verified-at 8101c29d

## Working set

- .harness/harness/features/BUG-2294-prune-keeps-run-digests/BRIEF.md
- .harness/harness/features/BUG-2294-prune-keeps-run-digests/plan.yaml
- .harness/harness/features/BUG-2294-prune-keeps-run-digests/notes/red-first-T-01.md
- .claude/skills/harness/bin/prune-run-evidence.py
- tests/unit/test-prune-run-evidence.py

## Done when

Scope: one validate run over the pinned seam sha returns a clean panel
Authority: brief-perspective:.harness/harness/features/BUG-2294-prune-keeps-run-digests/BRIEF.md#operator
Authority: brief-perspective:.harness/harness/features/BUG-2294-prune-keeps-run-digests/BRIEF.md#code maintainer
