# QA gate — FEAT-2225 @ 238058677e6bbeafd5f05cefa9db2ffb76686418 (cycle 2)

**BLUF: PASS.** Required unit + integration kinds ran green, `env -u HARNESS_AGENT_TYPE`; matrix_ok true. c1 F1 CLOSED, F3 CLOSED, F2 CLOSED for the reported counterexample with one residual limit (below, advisory, owner T-01/T-04). Pin removed on return.

Code-tree equivalence (measured): `git diff 238058677 06ab8282 -- . ':!.harness/harness/features'` is empty; only feature.json and plan.yaml differ. Working tree (HEAD 4768f4a1) equals 06ab8282 code-wise. Fix diff 8cddd8cd..06ab8282 read: dispatch-guard, expertise-merge, validate-digest, harness-hooks.ts, tests.

## Phase 1 (from BRIEF/plan, before source)
Expected: the three c1 regressions (marker-without-registered-distill-run refused at write and at dispatch; unrelated unreceipted deletion refused at live yield and durable close; real host-to-core runs for craft+repo add/replace/drop on capability-class reps) plus all c1 coverage. All have a named test. Gap: committed-unreceipted edit (below).

## Matrix (harness.json present; cross_module = always unit+integration for T-01/T-04; docs adds none)
| kind | state | cmd | result |
|---|---|---|---|
| unit | satisfied | `.agents/skills/harness/bin/run-unit-tests.py --kind unit` | exit 0, 61 files, 1132 PASS lines; 4 `FAIL` tokens = test-factory-claim-mutation's own mutation proof (repo G-09), runner exit 0 |
| integration | satisfied | `.agents/skills/harness/bin/run-unit-tests.py --kind integration` | exit 0, 88 files, 2909 PASS, 0 FAIL, "ALL PASSED" |

Task verifies (literal): T-01 exit 0 (test-expertise-ops + test-expertise-merge). T-02 gen-decisions-index diff empty, exit 0. T-03 MANUAL, exercised by T-04's test-member-expertise (0 failures). T-04 exit 0: schemas Ran 34 OK; bun 157 pass/0 fail/877 expect; member-expertise 0 failure(s). typecheck null: not claimed. Logs: /tmp/qa2/{unit,int,t01,t04}.txt (volatile; my domain cannot copy under the feature dir).

## c1 findings
- **F1 high T-04 — CLOSED.** `validate-digest.py --distill-authority` (reuses `_registered_distill_context`); host `distillAuthorityRefusal` runs before member-ops (harness-hooks.ts ~L1177-1198); dispatch-guard `_refuse_unbound_distill_marker`. Tests: test-validate-digest authority 10/10; test-dispatch-guard cases 35-37; omp-hooks mocked F1 + real-lineage F1 (lead and member under `build-engineering` refused, no file, no receipt). Natural red: red-first-fix-c1-digest.md (authority 0/10, dispatch-guard 158/161) and red-first-fix-c1-host.md (2 fail). My own mutant at this pin: neutering `_refuse_unbound_distill_marker` reddens test-dispatch-guard cases 35, 36, 37 (158/161). Legit orchestrator positive control stays green. Host-side authority mutant is the implementer's (host note, 0 pass/2 fail); not rerun by me.
- **F2 high T-01/T-04 — CLOSED for the reported counterexample; residual limit.** `_refuse_unreceipted_content` (expertise-merge.py ~L1560-1578) requires the whole file to chain from a committed state through receipted writes. Natural red: red-first-fix-c1-core.md (unit 1 FAIL, integration 3 FAIL: deletion after, edit of another entry, deletion before the receipted add) and digest note (F2 live/durable 2/6 → 6/6). My mutant: early-return in `_refuse_unreceipted_content` reddens "verify full: ... deletion of pre-existing G-01" plus 4 of 6 validate-digest F2 checks (live member, live lead, durable CLI, close-run). **Discrimination unshown for one leg:** removing only the `unchained` (every active batch on the chain) leg leaves test-expertise-merge and F2 validate-digest fully green; the leg's effect is untested (O-05: not proven useless, just undiscriminated). **Residual (source-derived, not executed; also the receipt's Known limit):** `_anchor_states` accepts HEAD, so an unreceipted edit already committed at HEAD intersects the chain and verify-receipt passes; only merge-time `replay --check`/merge-distill catches it. A mutating replay also makes verify-receipt refuse afterwards. No test pins either boundary. Severity advisory/med, owner T-01 (core) with T-04 (close path); not a new scope item, but whether it blocks SC-02 is the lead's call.
- **F3 med T-04 — CLOSED.** omp-hooks.test.ts:3376-3520 drives `expertise_apply.execute` through the real policyRunner and real core in an isolated committed checkout copy with real claims: five reps (product-lead, code-reviewer, dev-ops, orchestrator, backend-dev) x craft+repository x add/replace/drop; asserts verbatim receipt, counts, destination, file content, and real `verify-receipt` exit 0; forged-persona receipt refused. Tests assert each rep, not an aggregate. All-16 tool lists/Write/own-file grants/guidance remain in test-member-expertise.py (separate, 0 failures). Natural red: not natural (new test over existing behavior); host note records mutant forwarding `--persona harness-qa` → 5 of 7 failed, authority-ignore mutant → 2 of 2 F1 failed. I did not rerun those mutants.

## fail_first (every automated SC) — evidence paths in notes/
SC-01: red-first-T-04-host.md (9 fail), red-first-fix-c1-host.md (5 rep mutant fails), T-01 receipt (63 int/12 unit). SC-02: red-first-T-04-digest.md (22+2), red-first-fix-c1-core.md, red-first-fix-c1-digest.md. SC-03: red-first-T-04-host.md, red-first-T-04-guard.md (51), red-first-fix-c1-digest.md (F1 10/10, 3). SC-04: receipt-harness-backend-dev-T-01-c1.md (63 int/12 unit, 17 mutants; raw /tmp/t01 logs still volatile, c1 G2 stands). SC-05: red-first-t04-merge-gate.md (23). SC-06 inspection.

## Findings (new)
- N1 (kind substance, med-advisory, owner T-01+T-04): committed-unreceipted-edit and post-replay boundaries have no test; `unchained` leg undiscriminated (above).
- N2 (kind evidence, low, owner T-01): c1 G1/G2 durability unchanged (16-persona red receipt-only; T-01 raw reds /tmp).

## Not done
No authored tests. Pinned-checkout in-place mutation was refused by bash-write-guard; mutants ran from copied bin trees under /tmp via existing BIN override variables. Host-side TS mutants not rerun.

## Principles applied
Verification is the product (rule 7): green counted only with named tests and a retained red. Never falsify the record (rule 15): F2 residual and the undiscriminated leg stated, not rounded to CLOSED.
