# Research — abandonment source disposal

Two file-disjoint team tasks and three pending contract decisions are ready for plan review. BRIEF and plan approval remain pending; no implementation or live disposal occurred.

## Evidence and choices

- Reused operator-confirmed grilling `/Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-abandon-source-tickets-2026-11-02.md`, including its verified facts at c5233803/e817d357; no corpus scan or dry-run reproduction. PRODUCT baseline: `e817d3572087c9b9052e1f673c2ee177403a5896`.
- Read PRODUCT DEC-138 reason provenance, DEC-203 section 8 close-before-Backlog, DEC-238/INV-51 station-before-prune, configured test matrix and AGENTS.md guidance mapping. Generic `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` are absent; actual specification is `.harness/harness/docs/SPEC.md` and decisions are `.harness/harness/docs/DECISIONS.md`.
- Read configured `mruangutai/harness` backlog and #2161. Its shared-ticket Constraint is expressly overruled by settled grilling; confirmation accepts that another active feature may cite the source. Initial issue fetch used the wrong repository spelling, then was corrected from configuration.
- D-01 amends DEC-203 with explicit source opt-in, not a corpus guard; D-02 recommends already-abandoned local no-ops while disposal proceeds and retained runs still prune; D-03 recommends the exact original parent reason-file contents for every source comment.
- Individual domain resolution grants code/tests to backend-dev and dev-ops (tests also qa), decisions/index to documentor. Backend owns T-01 because this is CLI lifecycle logic; documentor owns T-02, depending on T-01. Shipping suite is read-only regression input, not an unnecessary owned edit.
- Prototype assessment: no DESIGN/prototype for this CLI-only change. The real dry-run contract and fake-gh cases provide the meaningful preview. Seven SCs: five automated (four integration, one unit), one pinned-content inspection, one operator post-merge acceptance.

## Structural verification

`plan-merge.py apply` exit 0 printed APPLIED; no APPROVAL-RESET receipt occurred, so no remote status call was made. Its automatic changed-state hook reported unsigned BRIEF and missing build_entry; these remain pending-plan/signature concerns, not authorization to sign or open the mirror.

Required `plan-merge.py check --file <absolute feature plan.yaml> --root <PRODUCT>` exited 0: T-01 three anchors, T-02 two anchors, two tasks, five anchors resolved, zero failures. No build, test, lint, formatter or live #1774 operation ran. A blocked proc stdin attempt was stopped and reported to tool QA; only plan-merge wrote plan.yaml, using this research path temporarily as its YAML proposal before this compact receipt replaced it.

## Future evidence and acceptance

QA must capture named red-first source/unopened/planner cases, positive/negative flag combinations, each source's ordering and exact body-file path, failure continuation, already-abandoned local behavior, and existing reject/ship regressions. SC-07 stays not met until after merge: use the merged executable with the archived FEAT-1774 record from `feat/FEAT-1774-observations-hindsight` (grilling archive revision fc13c4c9), review `abandon <archive-feature-dir> --reason-file <operator-signed-file> --close-sources`, then the operator alone repeats with `--close-sources --yes`. Observe #1774 closed not_planned, Backlog, abandoned label, verbatim reason comment, and local abandoned/no runs; retain executable and archive revision provenance. Do not use the archive's older executable or depend on this worktree surviving.

## Principles applied

- Experience First — make the complete dry-run list the operator's meaningful control, with no surprise source writes.
- Redesign From First Principles — integrate sources and local finalization into the existing abandonment plan/apply path.
- PRODUCT PRINCIPLES, No more specific than necessary — pin effects/order without requiring a new abstraction.
- PRODUCT PRINCIPLES, Verification is the product — separate fake-gh proofs from actual post-merge operator acceptance.

## Open questions

None for drafting. D-01 through D-03 await signature; the parent lead owns the four-angle simplification and panel gates before presenting the plan for signature.
