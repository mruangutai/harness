# Handoff — BUG-2451, build → validate — written at a4356cb5, seq-1

## Next

Dispatch ONE `validate` run to `harness-validator-lead` (slug `validate-validator`,
`HARNESS-MISSION: validate`) over the pinned `review_sha` — the seam commit that marks T-01
`done` and contains a4356cb5. Inputs: BRIEF.md SC-01..SC-04, plan.yaml T-01,
`notes/red-first-T-01.md`, `notes/simplify-pass.md`. Readers: qa (test_matrix for `bugfix`,
fail-first for SC-01 and SC-02), code, security, ui (its own verdict is recorded), pm goalcheck
(one grade per perspective: operator, code maintainer; D-01 / DEC-238 disposition). T-01 is
main-session-direct (DEC-174, DEC-179): a `must_fix` returns to Main inside the rework ruling
(1 round / 45 min), never to a hosted dev.

## Trust

- T-01 (725e625a) and the simplify record (9cc888fb) are ancestors of the tip — `git merge-base --is-ancestor` for each — verified-at a4356cb5
- The branch is 0 commits behind origin/main (e83c4e20) — `git rev-list --count HEAD..origin/main` — verified-at a4356cb5
- The diff against origin/main is T-01's five `files:` plus this feature directory, nothing else — `git diff --stat e83c4e20 HEAD` — verified-at a4356cb5
- `tests/unit/test-prune-run-evidence.py` exits 0 with HARNESS_AGENT_TYPE unset, 46 PASS / 0 FAIL, all three T-01 verify lines present — orchestrator re-run in the worktree — verified-at a4356cb5
- The generated decisions index equals the committed one — `gen-decisions-index.py --stdout | diff` exit 0 — verified-at a4356cb5
- The pruner source names git and subprocess only in its docstring — grep of `.claude/skills/harness/bin/prune-run-evidence.py` — verified-at a4356cb5
- RED against the 47d6c54d pruner was assertion failures (subprocess under an audit hook, staging output, five-file text), then green — `notes/red-first-T-01.md` (Main's record) — UNVERIFIED
- SIMPLIFY found nothing across four angles — `notes/simplify-pass.md` (Main's record) — UNVERIFIED
- run-unit-tests rc 0 for unit and integration, check-state clean, worktree-state converged at a4356cb5 — Main's dispatch to this run — UNVERIFIED

## Dead ends

- No hosted `fix` run exists for this plan: T-01 is main-session-direct, so there is no owning dev — plan.yaml T-01 `execution_mode` — verified-at a4356cb5
- Product docs/spec.md, docs/decisions.md and docs/architecture.md are absent and not substituted; their absence is not a finding — BRIEF.md `## Constraints` — verified-at a4356cb5
- DEC-257's own text, .gitignore, templates/gitignore.snippet, merge-gitignore.py and checkout-upgrade.md are out of scope; the forbidden-claim scan covers only the changed surfaces — BRIEF.md `## Out of scope` — verified-at a4356cb5
- The control-plane copy of the pruner is pre-change until merge; readers grade the worktree copy at `review_sha` only — `.claude/skills/harness/bin/prune-run-evidence.py` in the main checkout — verified-at a4356cb5

## Working set

- .harness/harness/features/BUG-2451-prune-staging-dec257/BRIEF.md
- .harness/harness/features/BUG-2451-prune-staging-dec257/plan.yaml
- .harness/harness/features/BUG-2451-prune-staging-dec257/feature.json
- .harness/harness/features/BUG-2451-prune-staging-dec257/notes/red-first-T-01.md
- .harness/harness/features/BUG-2451-prune-staging-dec257/notes/simplify-pass.md

## Done when

Scope: validate run returned over the pinned review_sha with a consolidated must-fix list
Authority: brief-perspective:.harness/harness/features/BUG-2451-prune-staging-dec257/BRIEF.md#operator
Authority: brief-perspective:.harness/harness/features/BUG-2451-prune-staging-dec257/BRIEF.md#code maintainer
