# BUG-2161 pending-plan review · plan-c0

**PASS — no findings. Mission proportionality is justified:** a new public opt-in flag and the bounded DEC-203 contract change warrant the chosen plan lane. No task-level proportionality finding or panel re-cycle is warranted.

Target: pending BRIEF.md and plan.yaml in this feature checkout; contextual source baseline e817d3572087c9b9052e1f673c2ee177403a5896. feature.json records the matching feature branch and no review pin. This is specification/architecture assessment, not implementation approval; code_grade: n_a.

## Stage 1 — intent and traceability

- Settled grilling constraints survive in BRIEF.md:17-29 and plan.yaml:36-46,65-72: explicit --close-sources plus --yes, no-flag source silence, close-before-Backlog, abandoned label, original reason-file, complete dry run, no corpus check, unopened local finalization, unchanged close guard/reject, and archived already-abandoned #1774 acceptance after merge.
- No orphan or dangling SC traces: T-01 implements SC-01–05, the CLI part of SC-06 and the behavior needed by SC-07; T-02 supplies SC-06's decision/index content and SC-07's durable operator sequence (plan.yaml:48-93). Neither task claims to execute operator acceptance. D-01–03 each have corresponding task instructions; both tasks serve criteria.
- SC-06 inspection obligation is explicitly assigned at plan.yaml:93, targeting DEC-203 section 8, its generated index, and CLI usage. Its pinned-content inspection is **not yet satisfied**: implementation and review_sha do not exist. SC-07 likewise remains open until the post-merge operator receipt, as BRIEF.md:33 states.
- T-02 follows T-01 and edits only decision/index files. Its declared writes do not overlap T-01's executable/test inputs; the examined abandonment and ship suites do not read those decision/index files. No identified successor invalidates the focused gate. QA's configured matrix remains additional, not replaced by focused verification (plan.yaml:72).

## Stage 2 — architecture and maintainability

- **Depth/locality:** extend the existing planner/executor module rather than introducing another command or framework. _abandon_plan and _apply_abandon_plan already share the operation list (.claude/skills/harness/bin/gh-sync.py:1597,1735); source inclusion and reason provenance remain local there.
- **Seams/adapters:** CLI parsing is the consent seam; existing external-write interception and fake-gh integration exercise the real planner/executor and command respectively. No speculative adapter, persistent resource, pass-through module or compatibility layer is proposed.
- **State:** source authority remains parse_source_issues(plan.yaml), not an additional synchronized mirror (gh-sync.py:469). Already-abandoned re-entry checks existing station authority while preserving station-before-prune; no second lifecycle state is introduced.
- **Specificity:** helper names and false-default threading reuse the existing interface, rather than prescribing a new abstraction. Per-source assertions, failure continuation and operation ordering pin observable acceptance. No dead tasks or unnecessary abstraction identified.

## Principles applied

- Delete First: removing the unopened early exit is preferable to a parallel disposal path; the existing planner/executor is retained.
- Model the Domain: one abandonment operation plan owns reported and applied source effects, avoiding independent render/execution state.

Open questions: none. No tests, builds, checks, live writes, or implementation mutations performed.
