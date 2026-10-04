# BUG-1016 — scope and architecture review

PASS: both tasks serve live requirements; proceed with the operator-confirmed plan mission. No mission-proportionality dissent, unnecessary task, or blocking architecture defect identified.

- **Spec compliance first:** T-01 covers SC-01–SC-06 and SC-07's implementation/test agreement; T-02 completes SC-07's documented contract (`plan.yaml:31,60`). All trace IDs exist; no orphan SCs or out-of-scope deliverables. Ship the seven-tool effective-input rewrite, default/list/hashline/MV coverage, authority/refusal controls, unchanged URI policy, behavior tests and decision/index—not a new resolver or host behavior.
- **Topology/gates:** T-01 → T-02 is acyclic (`plan.yaml:36,64`); their four owned paths do not overlap. T-01 reruns the whole adapter suite after its final code/test mutation; T-02 changes only docs/index and verifies their consistency (`plan.yaml:57,75`). No planned successor invalidates an earlier code gate, and retained tests are explicitly preserved controls rather than proof of obsolete relative-path behavior.
- **Architecture second:** the existing tool-call revised-input seam carries the same effective input to execution and policy (`plan.yaml:47,52,56`). Shared relative-path classification and one resolver answer per call provide depth/leverage across seven tools, with locality in the existing adapter and tests; no new discovery adapter, persistent cache, or pass-through layer is required. Hashline parsing is shape-specific, while authority remains the ready runtime claim/currentFeature and existing feature-root resolver (`plan.yaml:48–52`).
- **Policy/modes:** lexical rewriting preserves selectors, explicit absolute/tilde/URI destinations and non-path fields; default behavior is restricted to the three search tools. BUG-2003 remains downstream with mixed-target pre/post enforcement (`plan.yaml:50–56`). Hook and co-changed tests are main-session-direct; documentation alone is team-executed (`plan.yaml:33–35,62–64`), respecting DEC-174.
- **SC-07 inspection coverage:** `BRIEF.md:27–28` and `plan.yaml:73–75` specify pinned decision/index/adapter/test inspection. This plan review confirms the inspection obligation, not its future implementation result. No build, lint, test, formatter, diff or verification command was run; source facts in grilling were supplied inputs.

```yaml
VERDICT: PASS
DIGEST:
  headline: Both tasks are necessary; existing seams and authority support the full scoped cutover.
  severity_max: none
  findings: []
  must_fix: []
  spec_violations: []
  code_grade: n_a
  reviewed: plan:/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/plan.yaml
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/notes/review-harness-code-reviewer-plan-c1.md
```
