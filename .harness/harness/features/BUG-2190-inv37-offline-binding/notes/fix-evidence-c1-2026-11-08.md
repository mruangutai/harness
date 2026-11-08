# BUG-2190 fix c1 evidence (main session, DEC-174), 2026-11-08

Validate c0 (run `2026-11-08-02-validator`, FAIL) raised two med missing-assertion findings against T-01. Both are inside the signed SCs, so no amendment was needed. c1 is commit `fcc91963` and changes tests only; `board.py` is unchanged.

## SC-02: recovery guidance is selected against factory.repo (QA mutant M6)

- Unit u.2 now also asserts the recovery verb for each case:
  - missing receipt: `gh-sync.py recover-terminal`, because the unit fixture has no plan on disk;
  - owner repo recorded: `recover-mirror`;
  - unproven active mirror: `recover-mirror`.
- Integration i.3 asserts `gh-sync.py open <…/prod/features/FEAT-9002-bound-fixture>`. i.4 asserts `recover-mirror … --previous-repo org/repo`. i.5 asserts `recover-mirror`.
- M6 mutant (`_inv37_finding` passed the owner repository; throwaway, restored): **killed**. Unit `u.2 offline owner repo recorded: recovery guidance…` FAIL, and integration `(i.4)` FAIL. With the owner repository as the selection, recovery would choose `open` where `recover-mirror` is required.

## SC-03: non-mapping factory (QA mutant M4)

- Unit u.3 adds `factory="org/prod"` and `factory=["org/prod"]`. Each must produce `invalid authoritative repository binding … expected a mapping` with `resolve == 0` and `product_config == 0`, so there is no owner fallback and no remote read.
- Integration i.12 checks the same two shapes through the real entrypoint: no traceback, no contents read, and the invalid-binding finding.
- M4 mutant (mapping guard removed; throwaway, restored): **killed**. Integration `(i.12)` FAIL; the unit run crashes with `AttributeError: 'str' object has no attribute 'get'` and exits 1.

## Green at fcc91963

- Unit `test-check-state-inv37-local-binding.py`: exit 0, 18 PASS.
- Integration `test-check-state-inv37-offline.py`: exit 0, 12 ok.
- pyflakes clean.
- `code-grade.py --base 33c0c181 --head fcc91963`: every changed function grades 4.
