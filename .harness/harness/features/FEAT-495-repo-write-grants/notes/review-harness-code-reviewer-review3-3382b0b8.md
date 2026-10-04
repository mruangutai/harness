# FAIL — Bash's worktree carve-out still bypasses repository authority

Reviewed `9f9a7301d85e40a2f6d8753506e6cef146c8eb85..3382b0b8`; fix cycle `cb43f16e..3382b0b8`. Initial tree clean; no `[harness:human]` commits. Stage 1 compared SC-01..SC-08, D-01..D-06 and DEC-250 before Stage 2. No build-lead amendment digest supplied; approved T-06 records the run-start cutover.

## Findings (ranked)

- **R8 high, substance — SC-01/SC-02 omission:** `.claude/skills/harness/bin/bash-write-guard.py:976-978` continues for lexical `.claude/worktrees/` targets before classification/binding at :979-982. **REASONED:** `<root>/.claude/worktrees/foreign` is a symlink to declared product-b; product-a child runs `echo x > .claude/worktrees/foreign/change.md`. `claim_checkout_guard` realpaths the destination and returns immediately outside Harness root (:861-863); the unconditional continue permits the detectable foreign-product write without consulting `repository_binding`. R2's cache fix leaves this parallel bypass intact. Require repository binding before this carve-out, preserving its domain exemption afterward. Add an own/foreign-product worktree-shaped symlink pair requiring exit 2 and `mismatched` for foreign.
- **R6 med, substance — accepted grade-2 cost:** `dispatch-guard.py:345`, `_repository_identity`: cyclomatic/cognitive/ABC 14/22/37.4, grade 2. Required reason is at :347: cohesive artifact/header/fleet correspondence preflight. No new must-fix.
- **R7 med, substance — accepted grade-2 cost:** `inflight_registry.py:211`, `_expire`: 8/16/15.8, grade 2. Required reason is at :214: coherent lifetime predicate. No new must-fix.

## Prior fixes and specification inspection

- R1 corrected by `harness_boundary.py:77,934`; own/foreign control-plane Write assertions at `tests/integration/test-check-domain-claims.py:464-473` distinguish reverting segment attribution (own allow; foreign exit 2 plus `mismatched`).
- R2's cache ordering corrected at `bash-write-guard.py:979-985`; foreign-product cache-symlink regression at `tests/integration/test-bash-write-guard.py:1660-1669` requires the distinguishing refusal.
- R3 corrected at `inflight_registry.py:692-695`; `tests/integration/test-inflight-registry.py:1253-1271` releases a child, creates a pending sibling receipt, requires authorization False and checks the receipt remains unbound.
- R4/R5 resolved mechanically: pinned grading emits no high record; split case-38 functions grade 4; `classify` no longer emits a gated record. R6/R7 reasons accepted.
- **SC-07 inspection:** `check-domain.py:818` and `bash-write-guard.py:894` call the same exact-lineage/repository decision (`inflight_registry.py:761`); two-base classification remains shared (`harness_boundary.py:901-921`). R8 limits its Bash reach.
- SC-01/02 remain incomplete because of R8. SC-03/08 dispatch correspondence and authored-lineage refusal are at `dispatch-guard.py:181-192,345-411`; run-start behavior/refusal assertions are at `test-inflight-registry.py:1208-1250`. SC-04 recorded live PASS 28/28 at `notes/live-omp-probe.md:339-376` was read, not rerun. SC-05 early resolver stays ahead of runtime guards (`check-domain.py:164`). SC-06 exemptions/existing worktree paths remain; same-product siblings are asserted at `test-check-domain-claims.py:477-482` and `test-bash-write-guard.py:1670-1674`. No unrelated shipped change identified; developer receipts contain no Principles applied claims to check.

Measured this run: pinned `code-grade.py`, 41 passing records and two med grade-2 records. Regression discrimination above is inspected, not mutant-executed. No tests, live probe, source edits, or commits. Main should run deterministic boundary/registry/dispatch/Write/Edit/Bash/OMP suites and the discriminating R8 regression after fixing it.

## Principles applied

- Model the Domain: resolved repository ownership precedes lexical location exemptions.

Open questions: none. Must fix R8. `code_grade: grade_2`.
