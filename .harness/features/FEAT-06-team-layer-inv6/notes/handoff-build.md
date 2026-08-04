# Handoff — FEAT-06, build → validate — written at 9f87c48, seq-1

## Next

**Sequence the qa segment, then the review panel.** All 10 tasks are PASS and committed; the build
exit predicate is met. `review_sha` is pinned to **9f87c48**, the commit that CONTAINS T-07.

1. **qa segment** — validator squad, orchestrator-sequenced (`SPEC.md:1978`, D-08's first job).
   `harness-qa` writes and runs the `test_matrix` gate; `loop_back` to the owning dev on failure.
   Run dir slug `qa-validator`. This is the job T-11 just added to the playbook.
2. **review panel** — validator-lead hosts `review.yaml`, now FOUR steps, against `9f87c48`.
3. **pm goal-check** through product-lead. Then ship-refresh, distillation, CEO briefing.

## Trust

- All 10 tasks PASS with ZERO send-backs; `cycles_used` stays 4 of 10 — `feature.yaml tasks:`,
  every verify re-run by the orchestrator itself — verified-at 9f87c48
- **T-07's ten checks ALL DISCRIMINATE**: 10 of 10 FAILING at `635ef14`, 10/10 passing at HEAD.
  Re-run independently by the orchestrator via a detached worktree with `CLAUDE_PROJECT_DIR`
  repointed — not inherited from the executor — verified-at 9f87c48
- SC-14 measured both ways: `test_matrix` lines 0→2, 8-line window 0→7 hits — verified-at 9f87c48
- SC-15's three legs agree — SPEC ship row, SPEC review row, parsed `review.yaml`, all
  `{code, qa, security, ui}`; `SPEC.md:1978` carries exactly ONE `∥`-bearing brace group so T-07
  check (9) parses unambiguously — verified-at 9f87c48
- Three gates green at my own tier, not on report: `run-unit-tests.sh` 0, `check-docs.sh` 0,
  `check-state.sh` zero VIOLATION lines — verified-at 9f87c48
- `team-config.yaml:227` grants exactly `review-harness-qa-*.md`, the spelling T-02's new panel
  step renders — so the panel dispatch will not hit `check-domain.sh` exit 2 — verified-at 9f87c48
- Cost 42.89 measured of the 100 build allowance. **It understates reality**: 9 of 10 tasks ran at
  depth-0 in the main session, which is not separable to this feature — `feature.yaml cost_note`
- Commits: `f45fd0f` (8 tasks), `510b7ff` (T-08), `9f87c48` (T-07). All 10 mirror issues closed

## Dead ends

- Do NOT re-review the plan, re-open D-01..D-08, the 15 SCs' intent, or retired T-03 — three plan
  gates already spent; `runs/arch-review-eng/digest.md`, `runs/delta-review-eng/digest.md`
- Do NOT dispatch a ui-reviewer step. visual-designer ruled no end-user interaction and no
  prototype, on `review.yaml`'s own ui-step self-scope rule — `feature.yaml resolved`
- Do NOT action the ten advisories, AQ-2, issue #36 or `DECISIONS.md:1634` as validate work — they
  are ship-acceptance backlog for the user — `feature.yaml pending`
- Do NOT re-derive issues #10, #19, #20 or the routing wall — filed, out of scope
- Do NOT pre-answer the goal-check. SC-03 and SC-12 are `inspection`, SC-13 is `uat` — pm's and the
  user's, never the orchestrator's to mark — `BRIEF.md ## Success Criteria`

## Working set

- `.harness/features/FEAT-06-team-layer-inv6/feature.yaml`
- `.harness/features/FEAT-06-team-layer-inv6/STATE.md`
- `.harness/features/FEAT-06-team-layer-inv6/BRIEF.md`
- `.harness/features/FEAT-06-team-layer-inv6/PLAN.md`
- `.claude/skills/harness/teams/review.yaml`
