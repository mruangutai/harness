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
- T-04: built. post-checkout and post-rewrite added and post-merge extended: each runs
  `worktree-state.py --repair` on git's checkout, reports every failure and exits 0;
  post-merge still sweeps. All four creators converge before any record exists; merge, rebase
  and amend leave verify 0; class C is skipped byte-identical. On git 2.54 merges keep skip bits,
  so class A is exercised via an index rewrite then amend (receipt-T-04.md). Unit (53) and
  integration (84) suites pass.
- T-05: build half done. OMP absolute-read case, regression locks (mutant-proven), collected
  non-regression (retention, baseline finding subset, manifest consistency) and real-owner checks
  (disposable pin, removed). DEC-214 amended: a concrete landed feature is read at the control
  plane; classifier and the harness-simplify citation follow. Guidance in AGENTS.md,
  .harness/README.md and two skills. Unit (54) and integration (86) suites pass. Receipt half
  (notes/non-regression-receipt.md) waits for review_sha.
- SIMPLIFY done (3dd9e02b): 4 angles, 2 applied (one layout-code table; class-C-only
  classification), 1 skipped with reason; notes/simplify-pass.md.
- Operator rulings 2026-10-05: (1) T-05's receipt runs at the code-final commit, then the seam
  is committed and review_sha pinned there (seam differs only inside this feature's directory);
  (2) T-06 runs after merge under #2101 — T-06 abandoned here, #2094 closed not planned, SC-10
  amended in BRIEF.md, README conversion paragraph updated.
- T-05 receipt half done at code-final 69e3d819 (notes/non-regression-receipt.md):
  pre_change_sha e8d868f7, no other feature directory touched, main-corpus manifest identical
  (4635), clone suites exit 0 (unit 52 files, integration 80 files; the receipt's 54/86 were
  PASS-line counts, corrected by its erratum), real-owner 6/6.
- Validate c1 at review_sha 0e8301a5: FAIL (runs/validate-validator/digest.md). Six must-fix:
  SC-04 discovery gap, two unbound consumers, nine grade failures. The host refused the lead's
  final return; the run was opened at 2026-10-05T15:49Z and recorded late (its ledger
  started_at is the recording time), closed --refused-return BLOCKED, 0 cycles.
- Fix c1, main-session-direct (notes/receipt-main-session-fix-c1.md): all six fixed, with red
  or mutant evidence for each; seam 42856abb.
- Validate c2 (run validate-c1-validator) at 42856abb: FAIL. All six c1 must-fixes confirmed
  closed. One new high (SC-04): population keyed features by id, so one id in two segments
  dropped a directory (board audit, merge-gate owner count).
- Fix c2, main-session-direct (notes/receipt-main-session-fix-c2.md): population keyed by
  (segment, id); four new tests, red at 42856abb. Suites exit 0 (52 / 80 files). This commit is
  the new seam. Rework: round 2 of 2 (ruling: rounds=2, 120 min; 22 min spent at c2 close).
- next: pin review_sha to this seam, `status review`, re-verify as validate-c2-validator
- cycles_used: 0 / 10 (both re-verify reports so far: 0)
- board: milestone #99, parent #2086, tasks #2088-#2093 (T-06's #2094 closed not planned)

## Open Questions

- none
