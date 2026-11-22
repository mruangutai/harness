# QA gate c1 — FEAT-2340 @ 125a04f8 (baseline e239d881)

**BLUF: PASS.** SC-03 integration regression evidence is green at the pin; matrix floor is empty, so no kind is required; fail_first is `[]` by SC-03's own regression-only claim. No findings.

## Phase 1 (BRIEF + plan only)
Expected: one integration run of tests/integration/test-check-domain*.py, exit 0, no FAIL, no test rewrites; no unit suites expected (BRIEF Verification gaps). SC-01/02/04 are inspection, not QA-gated.

## Matrix
harness.json test_matrix: `docs` = `{always: []}`, `scaffolding` = `{always: []}` (T-01 docs, T-02 scaffolding). No required kind, `kinds: []`, `matrix_ok: true`. Integration is `active` (`detect tests/integration/**`) and was run as the SC-03 evidence, not as a floor requirement.

## Gate run (once, in pinned checkout at 125a04f8, `pinned-checkout.py` key c1/harness-qa, removed on return)
Command = plan T-02 verify equivalent (`run_pool.py` over `tests/integration/test-check-domain*.py`, HARNESS_AGENT_TYPE unset). 8 suites: rc 0, 8 `PASS test-check-domain*.py` lines, 478 `ok` lines, no `FAIL`/Traceback line, pool wall 10.82 s (inside 55 s budget).
Comparison to recorded receipts: sorted `ok`/`PASS` line set equals `notes/verify-T02-baseline.out` (pre-refactor e239d881 behavior; rc=0 wall=11s) and `notes/verify-T02-post.out` (rc=0 wall=10s). Identical green before and after, as expected for a semantics-preserving refactor.

## fail_first
`[]` — SC-03 explicitly claims regression evidence, not that suites fail on the unmodified gate (BRIEF SC-03). Baseline-green receipt is the intended record. No red-before claim made.

## Scope spot-checks (not gating, inspection SCs owned by other readers)
- `git diff e239d881..125a04f8 -- tests` is empty: no test/fixture rewrites (SC-03 "without test rewrites").
- Production diff confined to the three guidance files and check-domain.py (the `.claude/skills` paths); in check-domain.py `_I`, `_RE_HANDOFF_CYCLE`, `VERB` have zero matches, `re.IGNORECASE` appears 9 times.

## Coverage gaps (known, by design)
Multi-cycle handoff canonicalization (`handoff-x-c1-c2.md`) and legacy-vs-shape diagnostic ordering for mixed-case Plan.yaml beside PLAN.md have no existing test; BRIEF assigns them to SC-02 inspection. Reported as scope boundary, not a finding. No unit suite exists for check-domain (BRIEF: unit not claimed).

## Caveats
- Worktree HEAD is e1149f8e (re-pin commit); it differs from 125a04f8 only in feature.json. Gate ran at 125a04f8.
- Control-plane check-domain.py is the old copy by design; the pin runs the new one.
- Only `tests/integration/test-check-domain*.py` were run (assigned gate); the full integration suite was not.
