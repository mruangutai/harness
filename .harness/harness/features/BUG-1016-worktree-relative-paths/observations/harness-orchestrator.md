# Observations — harness-orchestrator — BUG-1016-worktree-relative-paths

- 2026-10-04: plan-phase.md names no simplify pass, but harness-simplify requires one on the draft before signature; pm escalated it (E1). Ran it as a separate eng-lead run (flag-only) + a product-lead apply run, both 0 cycles — three runs for a plan intake is the expected shape, not drift.
- 2026-10-04: dispatch-guard compares the HARNESS-FEATURE-TREE-ROOT line against the resolver and refused a path typo at exit 2 before spawn — the line is checked, not decorative.
- 2026-10-04: two squads reported `write agent://` and `write xd://report_issue` refused by check-domain as filesystem paths `agent:/`/`xd:/` despite BUG-2003 shipped; routed as a harness-defect open question, not fixed here.
