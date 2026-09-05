# STATE

## Current

- feature: BUG-1286-test-tree-enforcement
- run: .harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-31-product/state.yaml
- squad: none
- status: ready

Plan phase complete. The operator approved BRIEF.md and plan.yaml on 2026-09-05, and `gh-sync.py
status ... ready` recorded the Ready station. The GitHub mirror found no task sub-issues to move.

The cycle-10 panel PASSED at `severity_max: med`, `must_fix` empty, with nothing high, critical or
unrated. Its five non-gating findings carry into build. T-01 must re-prove the four specified red
cases against the built artifact; all plan-phase results were simulations of the specification.

BRIEF carries 9 REQ and 19 SC over eleven acceptance criteria; plan.yaml carries 6 decisions and
5 tasks. Preserved: REQ-09's breadth, full-relative-path `fnmatch` semantics over every running
kind, normalization plus `..` rejection, the manual-probe rule, the F-01 fix, D-05's FEAT-44
exception, and the three-kind blast-radius disclosure.

## Open Questions

- Five cycle-10 findings, all `disposition: open`, in the batched signature review. One med:
  PF-7f5eff475a69a7db20cc8293d4b6e9f7 — condition (b)'s NON-DEGENERATE conjunct requires a wildcard
  in the core, which is unmotivated by the fixed-literal insight and trips fail-closed on a fully
  literal core such as `**/test_foo.py`. Two low and two info concern the same conjunct and the
  BRIEF's residual bullet exemplifying only one of the three live `**/` patterns. The panel's own
  recommendation is to carry them rather than spend the last cycle: none gates, `gates.review` is
  `advisory_unless_high`, and the remedy is one clause a build-phase task can carry.
- The honest limit the panel refused to soften: every green/red result on record is a hand-simulation
  of a SPECIFICATION against reader-written reimplementations. Three independent implementations
  agree and none is the artifact that ships; T-01's mandate to re-prove the four red cases against
  the BUILT artifact is the only thing that closes it, and it is deferred to build.
- Harness defect the panel surfaced: `validate-digest.py` requires a `code_grade` and then rejects
  every value for a plan-phase feature, because `feature.json` necessarily reads `review_sha: none`
  before the Building-to-Review seam. It refuses every plan-phase code-reviewer digest, so a reader
  that did its job settles as `failed`. The remedy edits `.claude/skills/harness/bin/`, which no lead
  or reader may write.
