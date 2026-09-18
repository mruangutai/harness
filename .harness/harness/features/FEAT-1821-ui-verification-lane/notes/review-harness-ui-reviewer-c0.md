# Mode B UI evidence audit — 711ba16227eda39ddb397ed574e4ca199fbc5984

**FAIL.** The committed bundle is structurally fail-open: `results.json` labels all four inspection records `evidence` and reports no missing IDs even though its own errors say every signed inspection setup/capture failed, and the referenced WebPs confirm blank or wrong-state captures. This is a FEAT-1821 evidence-lane defect, not one of FEAT-53's expected 22 product predicate failures.

## Pin, binding, and accounting

- Audited immutable `HEAD`/review pin `711ba16227eda39ddb397ed574e4ca199fbc5984`.
- Opened and inspected `results.json` and **41/41 referenced committed WebPs**: 21 desktop-1440 and 20 desktop-1920. All files were readable.
- Binding is correct: schema `harness-ui-results/1`, feature `FEAT-53-metrics-dashboard`, run `FEAT-1821-initial-red`, DESIGN path, projects `1440×1100` and `1920×1100`, and `served_bundle_commit=0ef52107fde67b1f42cb51a16c773635dc73a408`, an exact full match for required `0ef52107` (`results.json:1-17`).
- Structural lists are arithmetically complete: 12 listed IDs, 12 observed IDs, `missing_check_ids: []`; applicability is 12 at desktop-1440 and 11 at desktop-1920 because SRC-TOKENS is once-only (`results.json:18-77`). The 23 records comprise 1 passed, 18 failed, 4 `evidence`; summary is failed (`results.json:1088-1092`). Check IDs/titles/methods/surfaces and 41 screenshot metadata entries align with DESIGN's check table and 22-row inspection manifest (`DESIGN.md:860-915`).

## Finding

**F1 — substance · critical · task scope — T-06, owner: main-session-direct.** Inspection evidence is accepted despite failed setup and captures that do not prove their labels.

- Concrete failure scenario: a reviewer trusts `status: evidence` plus `missing_check_ids: []` and approves density/prototype, keyboard/focus, accessibility, dark-theme, overflow, or error-state behavior although no matching rendered state was captured.
- Evidence: all four inspection records preserve `Error: every signed inspection setup and capture must execute`, each reporting 41 setup/capture failures (`results.json:491-546,733-766,864-917,1010-1042`), yet each remains `status: evidence` and the top-level missing list remains empty.
- WebP inspection: the named VIS captures are materially stale/mismatched. At both projects, `VIS-DENSITY--overview-default`, `--kpi-unavailable`, `--work-detail-long-content`, `--filtered-zero`, and `--source-error-with-valid-rows` are blank white rather than their declared states. Other VIS captures repeatedly show the same generic Operations Dashboard with KPI HTTP-500/source warnings and ordinary work rows rather than the declared KPI drill, work drill, open disclosure, long-content, sticky-overflow, or default-prototype states. Automated evidence is also unreliable as visual proof: several execution images are blank, while others show unrelated filter/error states.
- Comparison: approved prototype `notes/prototypes/FEAT-53/observed-{1440,1920}.png` shows the dark 7-KPI 4+3 grid, status cards, and populated work table. The committed blank/generic-error images cannot establish the matching hierarchy or interactions required by `DESIGN.md:883-915`; visible route focus, restored focus, open disclosure focus, sticky overflow, hatch, non-colour equivalents, and axe-covered states are therefore unverified.
- Required fix: T-06/main-session-direct must rerun only the configured lane and commit evidence whose pixels correspond to every declared route/fixture/setup, or make the producer/gate reject any inspection record whose setup failed. Never convert failed setup into `evidence` merely because a non-empty WebP exists.

## Expected product RED, kept separate

The 22 failed executable records (geometry, identity/status placement, keyboard/focus, contrast, hatch, table, and accessibility) plus green SRC-TOKENS are honest FEAT-53 product signal and are not findings against FEAT-1821. The gate here is solely the structurally incomplete/mismatched inspection evidence above.

```yaml
VERDICT: FAIL
DIGEST:
  headline: Committed inspection evidence fails open: 41 readable WebPs exist, but required states are blank or mismatched despite setup failures.
  mode: B
  in_scope: true
  severity_max: critical
  findings: [{ kind: substance, scope: task, severity: critical, reader: ui-reviewer, summary: "T-06/main-session-direct records VIS evidence after every signed inspection setup failed; blank and wrong-state WebPs can falsely satisfy completeness.", why: "A reviewer can approve density, prototype fidelity, accessibility, dark-theme, overflow, and focus behavior without evidence of the declared state." }]
  must_fix: ["T-06/main-session-direct: rerun the configured lane and commit state-matching captures, and fail producer/gate when an inspection setup failed instead of accepting any non-empty WebP."]
  states_unspecified: []
  contract_violations: [{ path: ".harness/harness/features/FEAT-53-metrics-dashboard/runs/FEAT-1821-initial-red/ui/results.json:491-546,733-766,864-917,1010-1042", actual: "Four VIS records say status=evidence while each reports all signed setup/capture execution failed; multiple referenced images are blank and the remainder show unrelated generic error/list states.", specified: "DESIGN.md:883-915 requires each exact route, fixture, interaction, project, screenshot, and same-state prototype comparison." }]
  a11y: ["A11Y-AXE is honestly RED, but its execution WebPs and the VIS keyboard/focus captures do not visually prove the named routes or focus states; accessibility remains unverified, not passed."]
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-ui-reviewer-c0.md
```
