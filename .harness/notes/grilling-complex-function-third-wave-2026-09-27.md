# Grilling — complex function, third wave: the last five evaluators, and render-brief removed — 2026-09-27

## Destination
The five grade-1 rule evaluators left on origin/main after FEAT-67 —
`check-plan-routes.process_plan_yaml` (108 lines, cyc 29 / cog 52 / abc 60.2),
`harness_boundary.classify` (150, 29 / 26 / 57.3), `board_lifecycle._audit_findings`
(106, 21 / 24 / 56.4), `layout_migration.scan` (52, 21 / 21 / 45.7) and
`check-domain.domain_check` (284, 14 / 17 / 53.3) — each become a small driver over per-rule
(or per-phase) functions, every function left behind grading at bar 4 or better on
`code-grade.py` (grade 2 excepted, as the grader excepts it); every owning suite byte-identical
to the baseline except enumerated, ruled divergences. The sixth grade-1 evaluator,
`render-brief.md_to_html`, is **deleted with its script**: the operator does not use the HTML
reading view of ship-review briefings, so the renderer, its test, the briefing.md step that
invokes it, and the 102 tracked derived `notes/ship-review-*.html` files go. After this wave
the evaluator half of the complex-function family is closed; only CLI dispatchers and the
lighter grade-1 functions remain.

## Mission
mission: patch
reason: cause known (one body per rule set), diff bounded (five functions in five named files,
one script removed with its single reference and derived outputs), no new public interface,
schema or enforcement surface — the grade ratchet already in code_grade holds the result.
confirmed-by: operator (picked (a) "all six in one wave" with the deviation "we don't need the
render brief as html; I don't use it at all", 2026-09-27)

## Settled (carried from FEAT-66/FEAT-67's trees; see those grilling notes)
- Target → **(a)**: the surviving drivers reach bar 4 too.
- Mission → patch; separate pins declined.
- Proof → byte identity across every owning suite at a clean detached checkout of the pin under
  `.claude/worktrees/harness/`; divergences ledgered old/new/ruling in built form; red-first
  receipts committed after the pin; raw checkout-root path lines normalised up front (D-09);
  SC-01 lock = the plan's inline grade assertion, no permanent lock file; SC-02 fail-first =
  baseline-vs-pin comparison; `change_type: cross_module`.
- Execution → enforcement files (DEC-174): `execution_mode: main-session-direct`.
- Shape → pm fixes it per function from the branch inventory. Known now:
  - `process_plan_yaml` — a per-task rule evaluator appending findings: rule table.
  - `classify` — the boundary rule over (target, root, globs, shared, label): ordered
    short-circuit phases; **the most-imported module in the tree** (~20 owning suites), so the
    byte run is the biggest of the wave and every phase's early return must keep its order.
  - `_audit_findings` — per-issue rule evaluator over the board: rule table.
  - `layout_migration.scan` — small scanner: phases.
  - `domain_check` — long and flat (cyc 14 / cog 17, 284 lines): its grade is driven by ABC
    (assignments/calls), not branching, so the split is by phase, not by rule.
- Comments → load-bearing; move byte-for-byte; new facts carry the feature id.
- Grade-2 helpers stay at 2 where a split would land at 3 (FEAT-67 precedent).

## The deviation: render-brief.py removed
- What goes: `.claude/skills/harness/bin/render-brief.py`; `tests/unit/test-render-brief.py`;
  the sentence in `.claude/skills/harness/references/briefing.md` step 4 that runs it (DEC-141
  it cites governs `render-map.py`, not this renderer — the "never hand-authored" clause is
  moot once no HTML exists); the `render-brief.py` row in
  `tests/integration/canonical-reader-classification.json`; the 102 tracked
  `.harness/harness/features/*/notes/*.html` files (derived, never authored; the markdown stays
  the record).
- What stays: `test-gen-decisions-index.py` mentions render-brief only in a comment about the
  hyphenated-module loading mechanism — reword that comment, nothing else.
- Proof for the deletion: no reference to `render-brief` or `md_to_html` remains outside
  `.harness/notes/`, `.harness/logs/`, DECISIONS and feature-history dirs; both test kinds
  green; validate produces a briefing with no `.html` sibling.
- Not a byte-identity subject: the deletion has no owning suite left; its owning suite is what
  is deleted.

## Out of scope
- The 9 CLI dispatchers (argparse fan-out) and the 9 lighter grade-1 functions — later waves.
- `check-skill-refs.scan` — exists only on the operator's `skills/optimization-pass` branch,
  not on origin/main.
- Any behaviour change in the five files; any new lock, verb or schema. #1928 stays parked.

## Facts I verified
- Grades at origin/main `e655f14a` via `code_grade.grade_source`; positions:
  process_plan_yaml check-plan-routes.py:379–487; classify harness_boundary.py:842–992;
  scan layout_migration.py:224–276; _audit_findings board_lifecycle.py:795–901;
  domain_check check-domain.py:855–1139.
- render-brief references: grep over the tree excluding worktrees/feature dirs/logs/DECISIONS —
  exactly the items listed above; no agent file, team file, check-state/check-domain/gh-sync
  path names it.
- Owning suites: test-check-plan-routes.py (+ the check-state/validate-feature-json users);
  the ~20 files importing harness_boundary (list by grep at build time); test-board-lifecycle.py,
  test-gh-board.py, test-config-shape-matrix.py, test-check-state-entry.py, test-gh-sync-ship.py,
  test-factory-integration.py; test-layout-migration.py, test-check-state-worktrees.py; the
  eight test-check-domain*.py + check_domain_support.py + test-bash-write-guard.py.
- Estimate: ~2 h build, ~30 min validate, as FEAT-67 scaled by two.
