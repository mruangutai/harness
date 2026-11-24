# Handoff — FEAT-2458, build → validate — written at 90b5ac6a, seq-1

## Next

Dispatch ONE `validate` run to `harness-validator-lead` (slug `validate-validator`,
`HARNESS-MISSION: validate`) over the pinned `review_sha` — the seam commit that marks T-01 and
T-02 `done`. Inputs: BRIEF.md SC-01..SC-10, plan.yaml T-01/T-02, `notes/simplify-pass.md`.
Readers: qa (test_matrix for `cross_module`, fail-first per automated SC), code, security,
ui (expected to self-scope out; its own verdict is recorded), pm goalcheck (one grade per
perspective: operator, code maintainer). Fixes are main-session-direct (DEC-174): a `must_fix`
returns to Main inside the rework ruling (2 rounds / 90 min), never to a hosted dev.

## Trust

- T-01 and T-02 are ancestors of the tip, in dependency order — `git merge-base --is-ancestor 35f67a65 90b5ac6a`, same for 1d8e8446 — verified-at 90b5ac6a
- The code diff is eight files, the plan's `files:` plus the simplify note — `git diff --stat 322b12b0..90b5ac6a` — verified-at 90b5ac6a
- `tests/integration/test-worktree-terminal.py` and `tests/integration/test-post-merge-sweep.py` exit 0 with HARNESS_AGENT_TYPE unset — orchestrator re-run in the worktree — verified-at 90b5ac6a
- The hook calls `worktree_terminal.classify_feature(` and carries no `def _repo_arg_for_segment` — grep of `.claude/skills/harness/bin/post-merge-sweep.py` — verified-at 90b5ac6a
- The branch is 0 commits behind origin/main after a fetch — `git rev-list --count HEAD..origin/main` — verified-at 90b5ac6a
- RED was observed before each task (T-01 11 rows AttributeError; T-02 rows 2,3,4,7,8) — `notes/simplify-pass.md` (Main's record) — UNVERIFIED
- The remaining T-02 verify members (check-plan-routes, structure locks, broad-catch census, no-distribution, canonical-reader audit) exit 0 — `notes/simplify-pass.md` (Main's record) — UNVERIFIED
- SIMPLIFY pass found nothing over 322b12b0..1d8e8446 — `notes/simplify-pass.md` — UNVERIFIED

## Dead ends

- No hosted `fix` run exists for this plan: both tasks are main-session-direct, so there is no owning dev — plan.yaml T-01/T-02 `execution_mode` — verified-at 90b5ac6a
- PF-9ad7c4848ca7e33119b82234b0637509 (exact-id match) is overruled as applied and is not a finding to re-raise — `notes/approval-decision-2026-11-23.md` Q-05 — verified-at 90b5ac6a
- `not_terminal` spelling, per-removed-stamp lines, D-03 and the UnicodeDecodeError catch are signed, not open — `notes/approval-decision-2026-11-23.md` Q-01..Q-04 — verified-at 90b5ac6a
- The control-plane copies of the hook and `worktree_terminal.py` are pre-change until merge; readers grade the worktree copy at `review_sha` only — `.claude/skills/harness/bin/post-merge-sweep.py` in the main checkout — verified-at 90b5ac6a

## Working set

- .harness/harness/features/FEAT-2458-shape-stamp-sweep/BRIEF.md
- .harness/harness/features/FEAT-2458-shape-stamp-sweep/plan.yaml
- .harness/harness/features/FEAT-2458-shape-stamp-sweep/feature.json
- .harness/harness/features/FEAT-2458-shape-stamp-sweep/notes/simplify-pass.md
- .harness/harness/features/FEAT-2458-shape-stamp-sweep/notes/approval-decision-2026-11-23.md

## Done when

Scope: validate run returned over the pinned review_sha with a consolidated must-fix list
Authority: brief-perspective:.harness/harness/features/FEAT-2458-shape-stamp-sweep/BRIEF.md#operator
Authority: brief-perspective:.harness/harness/features/FEAT-2458-shape-stamp-sweep/BRIEF.md#code maintainer
