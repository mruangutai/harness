# Handoff — FEAT-06, build → validate — written at 071e313, seq-2 (supersedes seq-1)

## Next

**Both validate segments are DONE. The next action is segment 4 — one assertion line — then the
user's UAT.** Superseded detail lives in `STATE.md ## Current`; this note is not the current truth
for anything below.

1. **Segment 4, main-session-direct (DEC-174 carve-out):** add one `check()` to
   `bin/test-harness-yaml-corpus.py` asserting the `teams/` root count is exactly 2, against the
   `counts` dict built at `:172`. **NOT in `test-team-catalog.py`** — T-07's approved verify
   requires that script's output to name exactly TEN checks.
2. **SC-13 (uat) is the user's** — read `teams/build.yaml` and `SKILL.md:40-53`.
3. Then: distillation (precondition is SCs passing), then ship acceptance.

## Trust

- All 10 tasks PASS with ZERO build send-backs; `cycles_used` 5 of 10, the 5th booked against the
  SC-05 remediation routed in this return — `feature.yaml` — verified-at 071e313
- **T-07's ten checks ALL DISCRIMINATE**: 10 of 10 FAILING at `635ef14`, 10/10 at HEAD. Re-run by
  the orchestrator via a detached worktree with `CLAUDE_PROJECT_DIR` repointed — verified-at 9f87c48
- SC-14 measured both ways: `test_matrix` lines 0→2, 8-line window 0→7 hits — verified-at 9f87c48
- SC-15's three legs agree; `SPEC.md:1978` carries exactly ONE `∥`-bearing brace group, so T-07
  check (9) parses unambiguously — verified-at 9f87c48
- All gates green at the orchestrator's own tier, not on report: `run-unit-tests.sh` 0,
  `check-docs.sh` 0, `check-state.sh` zero VIOLATIONs — verified-at 071e313
- **SC-05's premise, verified at source TWICE**: `test-harness-yaml-corpus.py:180-181` asserts
  `n > 0` per root; the `2` at `:174-175` is an f-string LABEL, not a comparison — verified-at 071e313
- `review_sha` pinned `9f87c48` BEFORE the first `squad: validator` entry. **HEAD will move past
  the pin when segment 4 lands — that is fine.** INV-6 requires pinned, not equal-to-HEAD; do NOT
  re-run the advisory panel for one assertion line — verified-at 071e313
- Cost 154-199 MEASURED of a 100 allowance, 1.5-2x over. Dominant line is the orchestrator's own
  session at ~88 (45-57%) — `feature.yaml cost_note` — verified-at 071e313

## Dead ends

- Do NOT re-review the plan or re-open D-01..D-08, the SCs' intent, or retired T-03 — three plan
  gates already spent — `runs/arch-review-eng/digest.md`, `runs/delta-review-eng/digest.md`
- Do NOT re-run the review panel after segment 4 — it is `advisory_unless_high`, returned PASS with
  empty `must_fix`, and one assertion line does not warrant it — `runs/panel-validator/digest.md`
- Do NOT spawn a ui-reviewer — recorded skip; no end-user interaction, diff is scripts/YAML/markdown
- Do NOT action the backlog as build work — the 8 items are for ship acceptance —
  `notes/ship-review-FEAT-06.md`
- Do NOT mark SC-13 met — it is `uat`, the user's alone — `BRIEF.md:195`

## Working set

- `.harness/features/FEAT-06-team-layer-inv6/STATE.md`
- `.harness/features/FEAT-06-team-layer-inv6/feature.yaml`
- `.harness/features/FEAT-06-team-layer-inv6/notes/ship-review-FEAT-06.md`
- `.harness/features/FEAT-06-team-layer-inv6/runs/goalcheck-product/digest.md`
- `.claude/skills/harness/bin/test-harness-yaml-corpus.py`
