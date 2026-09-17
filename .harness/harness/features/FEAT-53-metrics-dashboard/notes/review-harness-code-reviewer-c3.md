# FEAT-53 pinned code review — cycle 3

BLUF: **FAIL.** Stage 1 finds the complete implementation and final frontend repair compliant with the signed BRIEF/decisions at `ffd9fb0204701cdae968ef0febc86943fb4829bd`; Stage 2 confirms the frontend closures but the canonical full-feature grade remains red on four high records already identified in cycle 0.

## Stage 1 — spec compliance: PASS

The complete `a18d6a9f1f832084df84be22097a409d73bf4f61..ffd9fb0204701cdae968ef0febc86943fb4829bd` diff traces to the signed tasks and D-01..D-31. No omission, mismatch, or scope creep was found. T-17 documentation remains explicitly planned-post-gate, not emergent scope. Closed direct-lane V-09 (T-24/T-25/T-30), V-10, V-11, V-16, and V-20 were not reopened.

Inspection criteria remain satisfied in shipped source: SC-15's Astryx substrate and three-route shell are visible at `client/src/routes.tsx:35-89`; SC-20's keyboard-operable adjacent disclosures and KPI-4/KPI-7 sourcing-rule selection are at `client/src/panels.tsx:11-13,60-71`. The independent UI reader owns the full visual-contract judgment.

Frontend dispositions at the pin: **V-02 resolved**—KPI and work queries render independent success/error regions (`routes.tsx:52-62`); **V-03 resolved**—the KPI route consumes the live top-level payload (`routes.tsx:64-72`); **V-17 resolved**—the 2px `:focus-visible` rule remains (`routes.tsx:42`); **V-18 resolved**—24px/16px shell gutters and constrained tables remain (`routes.tsx:42`); **fixed-dark resolved**—root dark color scheme and opaque body ground remain (`routes.tsx:42`). These closures agree with the pinned route-suite/build and actual-browser evidence recorded in `receipt-harness-frontend-dev-fix-c2.md`; the reverse V-02 assertion's missing fail-first proof is a QA-record issue, not a shipped-code mismatch.

Human-authored commits in the canonical range: `91bfa049`, `c83feaa6`, `1745ca83`, `ab0c1501`, `ca4ac5bc`, `d9b6354b`, `60a2c900`, `7dbb0259`.

## Stage 2 — code quality: FAIL

Fail-open reassessment found no new silent omission: rejected KPI/work requests remain isolated and visible; the live KPI payload no longer passes through a fabricated adapter; invalid KPI ids do not fabricate a panel. The two cycle-0 collector fail-open defects were repaired before this pin and are not re-raised.

Canonical command:

`python3 /Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/code-grade.py --base a18d6a9f1f832084df84be22097a409d73bf4f61 --head ffd9fb0204701cdae968ef0febc86943fb4829bd`

Result: exit 1, `code_grade: fail`, **317 passing functions** and these ten failing records:

- high: `dashboard/kpi.py:28 compute` — grade 3 (cyclomatic 7, cognitive 1, ABC 25.9; ABC driver), T-06.
- high: `dashboard/work.py:325 _tokens` — grade 3 (9, 4, 19.4; cyclomatic), T-31.
- high: `tests/integration/test-metrics-dashboard.py:108 test_work_api_filters_live_disk_payload_and_preserves_static_routes` — grade 1 (6, 0, 72.2; ABC), T-27.
- high: `tests/integration/test-work-dashboard.py:196 worktree_case` — grade 1 (23, 11, 63.2; cyclomatic+ABC), T-26.
- med/grade-2, reason accepted: `attention.py:76 _feature_attention` (12, 17, 37.0), T-24, keeps precedence evaluation together; inherited and non-actionable under the closed V-09/V-16/V-20 lane.
- med/grade-2, reason accepted: `trend.py:152 _records` (9, 18, 19.3), T-10, one normalization pass.
- med/grade-2, reason accepted: `grilling_status.py:27 parse` (10, 14, 26.2), T-25, one front-matter grammar; inherited and non-actionable under the closed direct lane.
- med/grade-2, reason accepted: `test-metrics-trend.py:248 TrendTest.test_cmd_ship_records_trend_before_board_writes_and_handles_failure` (15, 2, 28.5), T-19, one ordered ship scenario.
- med/grade-2, reason accepted: `test-work-dashboard.py:149 metrics_case` (7, 5, 35.0), T-31, one phase/token aggregation scenario.
- med/grade-2, reason accepted: `test-metrics-kpi.py:42 KpiCoreTest.test_hand_labelled_feature_and_aggregate_values` (5, 0, 28.0), T-06, one hand-labelled KPI contract.

The four high records are inherited from the complete-feature cycle-0 review, not defects introduced by `ffd9fb02`; they remain actionable full-feature grade failures because each binds to a signed task and concrete maintenance failure scenario. No repair-diff Python path exists, so none is attributable to the final frontend repair.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "The pinned implementation is spec-compliant and all frontend closures hold, but four inherited full-feature high grade failures remain actionable."
  severity_max: high
  findings:
    - { kind: substance, scope: task, severity: high, reader: code-reviewer, summary: "T-06: dashboard/kpi.py compute remains grade 3.", why: "When a KPI source is added or changed, the wide orchestration can omit it from feature enrichment or aggregate output, shipping mutually inconsistent dashboard figures." }
    - { kind: substance, scope: task, severity: high, reader: code-reviewer, summary: "T-31: dashboard/work.py _tokens remains grade 3.", why: "When a run squad or phase mapping changes, total accounting can be updated without the matching phase branch, shipping totals that disagree with phase totals." }
    - { kind: substance, scope: task, severity: high, reader: code-reviewer, summary: "T-27: the work API integration test remains grade 1.", why: "When one API/static-route contract changes, the oversized multi-contract test can obscure or accidentally weaken another assertion, allowing a route regression to ship without a localizable guard." }
    - { kind: substance, scope: task, severity: high, reader: code-reviewer, summary: "T-26: the worktree integration case remains grade 1.", why: "When one worktree fixture branch changes, shared setup and assertions can overwrite or bypass another case, allowing primary/orphan/terminal or worktree-wins behavior to regress unnoticed." }
  must_fix:
    - "Bring the four named high-grade functions to their production/test bars without weakening their observable contracts."
  spec_violations: []
  code_grade: fail
  reviewed: "a18d6a9f1f832084df84be22097a409d73bf4f61..ffd9fb0204701cdae968ef0febc86943fb4829bd"
  human_commits_in_scope: [91bfa049b87c9534610aeaca92bacb7ba520d9a2, c83feaa6098cb6614ecb381b56211ad0e946a7a9, 1745ca83891cb98bf1313c166add3dea75210455, ab0c15019429a79f11d7c4a5665ebd20cb7e738a, ca4ac5bc2deddff7b9ddc34eff2b60c54ba088f1, d9b6354b6837ca4762fccf8518a45c6b9f414b4b, 60a2c900f59116ef23ecc5fc8b87c9d9092490a8, 7dbb025995b92a45c6a9d4035b56917a00fc7699]
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard/notes/review-harness-code-reviewer-c3.md
```
