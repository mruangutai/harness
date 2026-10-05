# STATE

## Current

- feature: FEAT-1559-corpus-outside-worktree
- mission: plan, signed 2026-10-04 by mruangutai; rework rounds=2, minutes=120
- station: building (main-session-direct under DEC-174)
- T-01: built. `feature_corpus.py`, `worktree-state.py`, `f58_sparse_fixture.py` and three test
  files; red and green evidence in notes/suite-baseline.md. Registered unit (50 files) and
  integration (80 files) suites pass; canonical-reader audit clean.
- T-01 amendments: unit tests renamed `test-worktree-state-rules.py` and
  `test-feature-corpus-discovery.py` (basename clashes refused by run-unit-tests.py)
- T-02: built (29b1a7db). `check_state/corpus.py` preflight and INV-52; audit preload scoped to
  the selected feature; receipt in notes/receipt-T-02.md.
- This worktree converted with `worktree-state.py --repair`: 117 feature dirs to 1; `--verify`
  exits 0.
- T-03: built. Gates, repo-wide discovery and two more readers go through `feature_corpus`
  (`population`, `corpus_roots`, `corpus_path`); census markers on every detected site. Five
  suite files that read other features locally were fixed by plan amendment. The INV-48
  `harness-simplify` conflict is resolved by `check-skill-refs` reading the main corpus. Unit
  (52 files) and integration (83 files) suites pass in this sparse worktree; check-state exit
  0. Receipt in notes/receipt-T-03.md.
- next: T-04, the post-checkout / post-merge / post-rewrite shims that run `--repair`
- cycles_used: 0 / 10
- board: milestone #99, parent #2086, tasks #2088-#2094

## Open Questions

- none
