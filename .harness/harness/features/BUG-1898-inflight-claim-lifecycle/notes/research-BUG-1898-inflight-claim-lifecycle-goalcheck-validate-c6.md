# Goal-check — BUG-1898 validate-c6

**BLUF: PASS.** At immutable pin `47b345fe65e992e07386de717f43b9f8dd495dc8`, all eight approved success criteria and all four Done-when perspectives are met. The c6 oracle closes F-SEC-C5-01: every descendant id is gathered, but only a direct `harness-eng-lead` child with the governed orchestrator as its exact parent is accepted; deeper, wrong-persona, wrong-parent, and mixed samples all fail S3. No singleton/crossed-row escape remains in the scoped oracle.

## Scope and exact-pin provenance

- Graded pin: `47b345fe65e992e07386de717f43b9f8dd495dc8`; merge base with `origin/main`: `a4d72e7fc91d0cf7a568d9e2a5225465a422170e`. Canonical range: 71 files, +7106/-554.
- Focused range `7893fe7a23e493dcd1554e439f28e3c9832b4de4..47b345fe65e992e07386de717f43b9f8dd495dc8`: 10 files, +486/-8. Its only executable delta is `tests/manual/probe-inflight-claim-lifecycle.py`, +15/-6; the other nine paths are feature state, receipts, reviews, and observations.
- Inspection and the adversarial oracle ran from `git archive 47b345fe65e992e07386de717f43b9f8dd495dc8`, not the mutable working tree. The archived probe hash matched pinned blob `a4254a45a0f789d11ce33ff6bb4e4ea812921116`; the archived live receipt matched pinned blob `a6f7cab812161a58d6053c08d032963c49cbb029`.
- C6 QA independently ran the required scoped matrix in an exact-pin archive: `bun test tests/unit/omp-hooks.test.ts` passed 99/99 with 273 expectations, `python3 tests/integration/test-run-unit-tests-kinds.py` passed 8/8, and probe compilation passed (`notes/review-harness-qa-c6.md:7-10`). Its SC-01 through SC-06 red-first evidence remains at `notes/review-harness-qa-c0.md:23-28`; `git diff --exit-code 7893fe7a...47b345fe...` over all five carrying unit/integration files also exited 0. No credentialled or live mode was run.

## Perspective grades

- **operator — pass (SC-01, SC-07):** retained automated evidence proves exact refusal/release and unrelated-claim preservation; the final operator-authorized receipt records the real OMP PASS 29/29, unchanged sentinel, and empty registry before and after.
- **orchestrator — pass (SC-02, SC-04, SC-06):** retained exact-id claim/reclaim, mixed-batch matching, held-child refusal, settlement, and exact recovery evidence is unchanged, while the corrected pinned S3 oracle rejects every named identity/lineage mutant.
- **code maintainer — pass (SC-03, SC-05):** retained tests cover the single feature-root/run-claim API, one-PM plus legal non-PM concurrency, DEC-100 pass-through, and `pi.events`; the focused executable delta does not touch those contracts.
- **reader — pass (SC-08):** pinned current-truth decisions, generated index, exact one-time cutover, red-first receipts, and distinct operator-run merge receipt remain inspectable and mutually consistent.

## Success-criterion outcomes

| SC | Verdict | Method | Pinned evidence |
|---|---|---|---|
| SC-01 | met | automated | T-03/T-04; retained QA evidence names `tests/integration/test-suite-claim-preservation.py:107-121` and red-first `notes/review-harness-qa-c0.md:23`; carrying test is byte-unchanged in the focused range. |
| SC-02 | met | automated | T-01/T-02; c6 QA's exact-pin unit run passed 99/99 with 273 expectations, including wake reclaim at `tests/unit/omp-hooks.test.ts:1875-2002`; baseline 85 pass/13 fail is retained at `notes/review-harness-qa-c5.md:20-21`. |
| SC-03 | met | automated | T-01/T-03; `tests/integration/test-inflight-registry.py:1238-1410`, red-first at `notes/review-harness-qa-c0.md:25`; file unchanged. |
| SC-04 | met | automated | T-02/T-04; `tests/unit/omp-hooks.test.ts:2020-2130`, red-first at `notes/review-harness-qa-c0.md:26`; file unchanged. The corrected manual oracle independently confirms the final real-id acceptance boundary. |
| SC-05 | met | automated | T-02; `tests/integration/test-check-omp-port.py:194-214`, including wrong-bus red-first at `notes/review-harness-qa-c0.md:27`; file unchanged. |
| SC-06 | met | automated | T-03; `tests/integration/test-validate-digest.py:5815-5844`, red-first at `notes/review-harness-qa-c0.md:28`; file unchanged. |
| SC-07 | met | uat | **Only the final operator-authorized entry is used:** `notes/live-omp-probe.md:1105-1297`, run `2026-09-25T13:18:49+00:00`, PASS 29/29. S1-S5 are green at `:1115-1144`; the real S3 row is started/completed `Nest.Probe`, persona `harness-eng-lead`, under governed orchestrator `Nest` at `:1248-1266`; snapshots are `before: []` and `after: []` at `:1294-1295`. This observed direct-child shape is exactly the pinned oracle's sole accepting lineage shape. |
| SC-08 | met | inspection | T-05; pinned `DECISIONS.md:1373-1377` preserves DEC-100 crash pass-through plus self-refusal, `:6361-6440` states exact-id run start, `pi.events`, id-keyed settlement, canonical registry, and exact release; generated `DECISIONS-INDEX.md:109,204-205` reflects DEC-100/204/205; `notes/ship-checklist.md:5-11,38-116` gives per-registry enumerate/classify/exact-release/re-enumerate cutover and makes the first post-merge cycle non-gating. |

## F-SEC-C5-01 disposition and adversarial proof

**Closed at the pin.** `_governing_root` finds the governed orchestrator for any-depth descendants (`tests/manual/probe-inflight-claim-lifecycle.py:433-435`), and `nested_ids` gathers every such id (`:438-441`). `crossed_rows` then marks every gathered descendant crossed unless it is exactly one segment below that root, persona `harness-eng-lead`, and `parent_agent_id` exactly the root (`:444-458`). S3 separately requires exactly one gathered nested id and no crossed row (`:461-472`), then its final absence selector checks `governed + nested` (`:473-475`). A pinned-tree search found no second implementation of these predicates; other hits were historical review notes.

The pinned import-and-call oracle returned:

| Case | `nested_ids` | crossed rows | S3 identity result |
|---|---:|---:|---|
| actual `Nest.Probe`, `harness-eng-lead`, parent `Nest`, with valid top-level `Nest`/`Plain` orchestrators | 1 | 0 | pass |
| c5 counterexample: `Nest.Probe.Deep`, `harness-qa`, parent `Nest.Probe` | 1 | 1 | fail |
| structurally deeper otherwise-correct lead: `Nest.Probe.Deep`, `harness-eng-lead`, parent `Nest` | 1 | 1 | fail |
| direct child, wrong persona | 1 | 1 | fail |
| direct child, wrong parent | 1 | 1 | fail |
| mixed valid `Nest.Probe` plus invalid deeper row | 2 | 1 | fail |

An exhaustive bounded cross-product over depths 1–3, the required/wrong personas, and exact/intermediate/wrong parents printed `PASS exhaustive-singleton-and-crossed`: only the one direct, exact-persona, exact-parent row passed. Correct top-level governed orchestrator rows remained uncrossed. This re-measures the failed c5 premise rather than inferring closure from a green suite.

## Findings, residuals, and cleanup

- Findings: none; no must-fix remains. Independent c6 security review also closes F-SEC-C5-01 and reports no scoped security finding (`notes/review-harness-security-reviewer-c6.md:3,13-38`).
- `notes/handoff-validate.md` seq-3's historical INV-43 late succession remains a named non-blocking ledger residual. The operator-owned dirty residual `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/bug1898-overlay.mIdqOR` was not touched.
- Scratch archive `/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmp.FQ4bhD00wk`, generated cache, and oracle process state were removed; `test ! -e` exited 0. No scratch worktree was created.
- No source, test, config, plan, brief, feature state, run state, or other reader note was modified. No formatter, linter, project-wide build/suite, or live probe was run.

```yaml
VERDICT: PASS
DIGEST:
  headline: "All four perspectives and SC-01..SC-08 are met at 47b345fe; the c5 deeper-lineage bypass is closed with no remaining singleton/crossed-row escape."
  feasibility: clear
  surface: L
  flags: [security, exact-pin, lifecycle, live-uat, ledger-residual]
  recommend: proceed
  tasks: 5
  decisions: 7
  needs_approval: false
  risk: low
  sc_status:
    - { id: SC-01, verdict: met, method: automated, evidence: "retained QA evidence; tests/integration/test-suite-claim-preservation.py:107-121; carrying test unchanged at pin" }
    - { id: SC-02, verdict: met, method: automated, evidence: "c6 QA exact-pin 99/99; tests/unit/omp-hooks.test.ts:1875-2002; retained baseline red" }
    - { id: SC-03, verdict: met, method: automated, evidence: "tests/integration/test-inflight-registry.py:1238-1410; carrying test unchanged at pin" }
    - { id: SC-04, verdict: met, method: automated, evidence: "tests/unit/omp-hooks.test.ts:2020-2130 plus pinned adversarial oracle; carrying unit test unchanged" }
    - { id: SC-05, verdict: met, method: automated, evidence: "tests/integration/test-check-omp-port.py:194-214; carrying test unchanged at pin" }
    - { id: SC-06, verdict: met, method: automated, evidence: "tests/integration/test-validate-digest.py:5815-5844; carrying test unchanged at pin" }
    - { id: SC-07, verdict: met, method: uat, evidence: "final operator-authorized notes/live-omp-probe.md:1105-1297 only; PASS 29/29, valid Nest.Probe shape, registry empty before/after" }
    - { id: SC-08, verdict: met, method: inspection, evidence: "pinned DECISIONS.md:1373-1377,6361-6440; DECISIONS-INDEX.md:109,204-205; ship-checklist.md:5-11,38-116" }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle/.harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/research-BUG-1898-inflight-claim-lifecycle-goalcheck-validate-c6.md
```
