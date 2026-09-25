# QA gate — BUG-1898 c0

**BLUF: FAIL.** The configured automated matrix is green at review SHA `84c3a6cbe74c7c27337d4372a68be60fca834118`, and red-baseline discrimination was observed for SC-01–SC-06. But SC-01 explicitly requires preservation during both direct validation **and a suite run**; no automated test seeds an unrelated live claim around a suite invocation. The only suite-preservation scenario is the pending live OMP probe, so the automated criterion is incomplete.

## Scope and matrix

Phase 1 (BRIEF + plan only) expected: integration proof for SC-01/03/05/06, unit proof for SC-02/04, direct and suite-preservation coverage for SC-01, no UI surface, and inspection for SC-08. Tasks T-01/T-02 (`cross_module`) require unit + integration; T-03 (`bugfix`, runtime) requires unit; T-04 changes `harness.json` shape and requires integration. Union: **unit, integration**.

| kind | state | configured command and observed result | discovery / relevant proof |
|---|---|---|---|
| unit | satisfied | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit` → 0 | 42 files; `tests/unit/omp-hooks.test.ts` → 98/98 |
| integration | satisfied | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind integration` → 0 | 69 files; includes `test-inflight-registry.py`, `test-validate-digest.py`, `test-check-omp-port.py`, and `test-run-unit-tests-kinds.py` |
| typecheck | not_applicable | no configured command (`cmd: null`, unresolved); not in matrix | Explicit BRIEF gap for `.omp/extensions/harness-hooks.ts`; no result claimed |
| component / ui | not_applicable | unresolved null commands; no matching component/browser surface | BRIEF: non-UI lifecycle change |
| inflight_claim_lifecycle_live | locally_run | deliberately outside automated matrix | registered at `.harness/harness.json:320`; live receipt absent by design; it is SC-07's operator merge gate |

Matrix floor is met: `matrix_ok: true`. The gate verdict is nevertheless FAIL for the coverage finding below.

## Automated SC evidence and fail-first

| SC | current-pin passing evidence | observed red-baseline evidence (`0aa337f1`) |
|---|---|---|
| SC-01 | Integration matrix exit 0; direct exact-release cases at `tests/integration/test-validate-digest.py:5712-5760` | Current test against baseline: 7/76 BUG-1898 exact-release checks passed; missing identity released claims (`artifact://365:243-391`) |
| SC-02 | Unit matrix exit 0; `tests/unit/omp-hooks.test.ts:1875-2001` binds/reclaims/holds exact ids before writes | Current unit test against baseline: 85 pass, 13 fail; run-start binding, wake reclaim, markerless recovery and held-refusal assertions fail (`artifact://362`) |
| SC-03 | Integration matrix exit 0; `tests/integration/test-inflight-registry.py:1238-1410` covers run-start, PM conflict, canonical root and exact recovery | Current registry test against baseline exited 1 because BUG-1898 run-start/find-run cases are absent; current digest test also red on feature-worktree release (`artifact://365:378-380`) |
| SC-04 | Unit matrix exit 0; `tests/unit/omp-hooks.test.ts:2003-2113` covers reordered IDs, never-started receipts, and event settlement | Current unit test against baseline: the reordered-batch and `pi.events` settlement cases fail (`artifact://362`) |
| SC-05 | Integration matrix exit 0; `tests/integration/test-check-omp-port.py:194-214` installs the `pi.on` mutant | Current port test against baseline: 28/30; wrong-bus assertion and diagnostic both fail |
| SC-06 | Integration matrix exit 0; `tests/integration/test-validate-digest.py:5769-5844` covers feature-root release, exact held child, post-settlement yield, and recovery selector | Current digest test against baseline: 7/76 BUG-1898 exact-release checks passed; feature-worktree release, held-child refusal, exact recovery and parent-only release fail (`artifact://365:378-391`) |

These are retained command outcomes in the isolated red-proof worktree, not a narrative claim. The current pin's two configured runners are the green receipts above.

## SC-08 inspection

PASS by inspection: `git show 84c3a6c:.harness/harness/docs/DECISIONS.md` shows DEC-204's current-truth run-start/exact-id language and DEC-100-compatible self-refusal (`DECISIONS.md:6361-6395`), exact canonical-root release and `pi.events` semantics (`6409-6438`); the generated index has DEC-204 at `DECISIONS-INDEX.md:204`; and `notes/ship-checklist.md:13-115` specifies pre-load enumeration, individual evidence-backed releases, forbids bulk/persona release, and makes the first post-merge cycle follow-up only.

SC-07 was not run. `notes/live-omp-probe.md:1-43` truthfully records no live run; it remains the required operator merge gate and is not a panel failure.

## Finding

- **F-QA-01** — `kind: substance`; `severity: high`; `reader: harness-qa`; owner: **T-03/T-04**. `tests/integration/test-validate-digest.py:5712-5760` proves direct digest validation preserves seeded claims, but no automated test invokes a suite while an unrelated sentinel is live. `tests/integration/test-run-unit-tests-kinds.py:116-129` only proves live-probe registration/exclusion; `plan.yaml:219-226` explicitly removed the suite-sentinel scenario and leaves actual suite preservation to SC-07. If a suite invocation releases a claim it does not own, every configured automated gate can remain green and the SC-01 suite clause is violated. Add an isolated automated suite-plus-sentinel assertion or narrow SC-01 with approval; the live probe cannot satisfy `verify: automated`.

## Assessed, dismissed simplify candidates

1. Runtime-id `settleRun` dedupe: reject; a wake reuses the same id and `omp-hooks.test.ts:1892-1905` requires a new exact claim after settlement, so dedupe can suppress the required release/reclaim lifecycle.
2. Share `_is_unbound_receipt` with `authorize_runtime_identity`: reject for this pin; it changes candidate selection outside D-02 and has no signed behavioral need.
3. Remove `_held_children` lead/orchestrator pre-filter: dismiss for current scope. All three team leads normalize to `lead`, and orchestrator is the sole other dispatcher (`.harness/team-config.yaml:300-327`; `validate-digest.py:2260-2269`). Dropping it adds a registry read on every member return. A future dispatch-capable non-lead must change this predicate with a test; no current dispatched seat is missed.

## Principles applied

- **Build the Lever** — used the configured per-kind runners and isolated red-baseline worktree instead of hand-counting assertions.
