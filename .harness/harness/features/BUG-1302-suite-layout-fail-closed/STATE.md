# STATE

## Current

- feature: BUG-1302-suite-layout-fail-closed
- squad: none
- status: review

Plan and BRIEF are approved. The main session completed all five DEC-174 tasks, ran each
focused suite, recorded the required red demonstrations, applied the sole simplify finding,
and moved `plan.yaml` to `review`. The next phase is independent validation against the pinned
`feature.json` `review_sha`; the build evidence is in `notes/handoff-build.md`.

## Open Questions

- DEC-174 does not enumerate `run-unit-tests.sh` by name, but the Advisor ruled its carve-out
  binds both gate test files by category. This build followed that ruling.
- The B-6 hard-failure remedy and its fixture-maintenance red are accepted as the Advisor's
  recommended tradeoff; the failure names both repairs.
- Structural AST pins may need main-session fixture maintenance after a legitimate refactor;
  that low false-positive cost is recorded in BRIEF.md.
- Harness tooling defects observed during planning remain outside this issue's scope.
