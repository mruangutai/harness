# Observations — harness-orchestrator — BUG-1016-worktree-relative-paths

- 2026-10-04: plan-phase.md names no simplify pass, but harness-simplify requires one on the draft before signature; pm escalated it (E1). Ran it as a separate eng-lead run (flag-only) + a product-lead apply run, both 0 cycles — three runs for a plan intake is the expected shape, not drift.
- 2026-10-04: dispatch-guard compares the HARNESS-FEATURE-TREE-ROOT line against the resolver and refused a path typo at exit 2 before spawn — the line is checked, not decorative.
- 2026-10-04: two squads reported `write agent://` and `write xd://report_issue` refused by check-domain as filesystem paths `agent:/`/`xd:/` despite BUG-2003 shipped; routed as a harness-defect open question, not fixed here.
- 2026-10-04: documentor tasks are PRODUCT squad work; build.yaml cannot reach documentor. Opened t02 against eng-lead by reflex and had to close it BLOCKED at 0 cycles — read the team-config member list before run-start, not after.
- 2026-10-04: after an IRC resume (not a fresh dispatch) every `task` call was refused by the live hook with the runtime-lineage MISSING_CAPABILITY message while write/bash still passed; the hook state for a resumed orchestrator had no agent id. A resume by peer message is not equivalent to a re-dispatch for the dispatch gate.
