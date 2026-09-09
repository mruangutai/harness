# Handoff — BUG-1507-ready-station-signature, build → validate — written at 31b4c8a3, seq-2

## Next

Hand back to the main session: open the PR for `feat/BUG-1507-ready-station-signature`, watch CI,
merge, then `gh-sync.py ship`. Build and validate are both closed — five tasks landed, `qa_gate`
PASS, SIMPLIFY empty, panel PASS at the pin with `must_fix: []`. Nothing is dispatchable inside this
feature: the only work left is the operator-gated PR/merge/ship chain the orchestrator does not run.
The one residual to carry forward is VL-01, as a backlog row, not a fix — see Dead ends.

## Trust

- The panel PASSED at the pin: `severity_max: med`, `must_fix: []`, all four readers RAN, none
  skipped — `feature.json` run `2026-09-08-panel-validator` and
  `notes/review-harness-{code-reviewer,qa,security-reviewer,ui-reviewer}-c0.md` —
  verified-at ac5e24e5.
- `review_sha` is `ac5e24e5`, and it CONTAINS every deliverable: the only later commits write
  records (`feature.json`, `STATE.md`, `notes/`) and touch no code path — verified-at 31b4c8a3.
- SC-04, SC-06, SC-07 and SC-10 re-checked by the orchestrator at the pin itself with
  `git show ac5e24e5:<path>` rather than a working-tree read — SKILL.md:146,
  github-mirror.md:95, gh-sync.py:1312, and an EMPTY diff for factory_config.py / harness.json /
  plan-merge.py / gh_board.py — verified-at ac5e24e5.
- SC-09's two suites pass at the pin: `tests/integration/test-gh-sync.py` and
  `test-board-station.py`, both exit 0, run by the orchestrator itself, not relayed —
  verified-at ac5e24e5.
- The mirror is now truthful: `gh-sync.py open` created milestone #64, parent #1517 and sub-issues
  #1518-#1522, and `status ... review` moved all six to review — `feature.json` `github` block —
  verified-at 31b4c8a3.
- SC-01 is PARTIAL by its own terms and that is the recorded state, not a defect:
  `notes/sc01-ready-write-transcript.md` records clause (c) as not applicable because no sub-issues
  were recorded at signature time. `open` ran only after validate, so re-running the ready write now
  would not reproduce the moment the criterion names — verified-at 31b4c8a3.

## Dead ends

- Do NOT widen T-05's `TOKEN_PATTERN` to cover `plan-merge.py set-feature-station --station` inside
  this feature (VL-01). The pattern is spelled character for character in T-05's SIGNED `intent:`,
  and the gap is latent: both occurrences in the swept corpus are `building`, lowercase and
  accepted — `notes/vl-01-plan-merge-shape-measurement.md`, verified-at ac5e24e5.
- Do NOT re-run the ready write to try to complete SC-01 clause (c). The criterion names the moment
  immediately after signature, and the panel accepted the partial —
  `notes/sc01-ready-write-transcript.md`, verified-at 31b4c8a3.
- Do NOT add `building` to `cmd_status`'s early-return tuple. `load_recorded` raises `SystemExit` on
  an unparseable `feature.json`, so short-circuiting is not behaviour-preserving — `plan.yaml` D-02
  and the docstring paragraph now stating it, verified-at ac5e24e5.

## Working set

- .harness/harness/features/BUG-1507-ready-station-signature/feature.json
- .harness/harness/features/BUG-1507-ready-station-signature/plan.yaml
- .harness/harness/features/BUG-1507-ready-station-signature/notes/vl-01-plan-merge-shape-measurement.md
- .harness/harness/features/BUG-1507-ready-station-signature/notes/review-harness-code-reviewer-c0.md
- .harness/harness/features/BUG-1507-ready-station-signature/notes/qa-BUG-1507-build.md

## Done when

Scope: the main session opens, merges and ships this branch
Authority: brief-sc:SC-09
Authority: brief-sc:SC-02
