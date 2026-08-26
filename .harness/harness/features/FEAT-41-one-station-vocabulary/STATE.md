# STATE

## Current

- feature: FEAT-41-one-station-vocabulary
- run: .harness/harness/features/FEAT-41-one-station-vocabulary/runs/2026-08-25-03-product/state.yaml
- squad: none
- status: awaiting-user

## Open Questions

- Q1: board semantics. A ready task projects to the BACKLOG station under D-11's documented exception. Operator confirms or reverses.
- Q2: D-09 record shape. AMEND vs DEC-188's in-place clause STRIKE, which has 11 working precedents. Orchestrator read: strike form.
- Q3: glossary scope. WARN only, fires independently of this feature. Separate real defect: DEC-162 index row says .harness/codebase/glossary.md, code tests .harness/glossary.md.
- Q4: no code-review pass ran at plan phase. The operator-facing CLI text this feature changes went unexamined by any reviewer.
- Q5: the design-contract scope-out has no shelf life; nothing re-gates if a UI-shaped file appears at build.
- Q6 (harness defect): run digests are gitignored and die with the worktree, but the briefing procedure cites them as its completeness disclosure.
- Q7 (harness defect): SubagentStop blocks an orchestrator turn-end while children run; DEC-201 says every dispatch ends the turn. Both cannot hold.
