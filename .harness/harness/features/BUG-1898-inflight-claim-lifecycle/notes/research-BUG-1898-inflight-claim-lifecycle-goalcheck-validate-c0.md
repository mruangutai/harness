# BUG-1898 goal-check — validate c0

## Scope and verdict

**FAIL** at review SHA `84c3a6cbe74c7c27337d4372a68be60fca834118` over canonical range `a4d72e7fc91d0cf7a568d9e2a5225465a422170e..84c3a6cbe74c7c27337d4372a68be60fca834118`. The shipped exact-id lifecycle behavior and the configured unit/integration matrices are green, but SC-01 explicitly requires automated proof that a suite run preserves an unrelated seeded live claim. No automated test performs that scenario; only the unrun live probe's S4 does. That is a real T-03/T-04 coverage failure, separate from SC-07's expected pending operator gate.

Evidence is kept in three lanes:

- **Shipped behavior:** run start claims or binds the exact runtime id; settlement releases by result-row/lifecycle id; digest validation requires feature plus exact agent id, preserves a parent with a live child, and uses the canonical feature root; DEC-204 and the cutover checklist state the same current truth.
- **Automated/inspection proof:** QA observed the 42-file unit and 69-file integration runners exit 0 and independently reproduced the red baseline for SC-01 through SC-06 (`notes/review-harness-qa-c0.md:9-30`). Pinned inspection passes SC-08 (`notes/review-harness-qa-c0.md:32-34`). The green matrix does not supply SC-01's missing suite-plus-sentinel case.
- **Operator proof:** `notes/live-omp-probe.md:1-43` truthfully has no live receipt. SC-07 remains a required pre-merge operator gate and is not itself a validation-panel defect (`notes/review-harness-qa-c0.md:36`).

## Perspective grades — exactly one line per declared perspective

- **partial — operator** — SC-01 is partial because direct exact-release preservation passes but no automated suite-plus-sentinel test exists; SC-07 is separately pending the operator's live OMP receipt.
- **pass — orchestrator** — SC-02, SC-04, and SC-06 are met by exact run-start/reclaim/hold coverage, actual-id reordered settlement and receipt rollback, and exact held-child refusal/recovery (`notes/review-harness-qa-c0.md:24,26,28`).
- **pass — code maintainer** — SC-03 and SC-05 are met by the single registry API/canonical-root and one-PM cases plus the wrong-bus mutant that accepts only `pi.events` (`notes/review-harness-qa-c0.md:25,27`).
- **pass — reader** — SC-08 is met at the pin by DEC-100/DEC-204 current truth, the generated index, the exact manual cutover, and the explicitly non-gating first post-merge follow-up (`notes/review-harness-qa-c0.md:32-34`).

## Success-criterion status

| SC | Verdict | Method | Evidence |
|---|---|---|---|
| SC-01 | partial | automated | Direct validation preservation passes at `tests/integration/test-validate-digest.py:5712-5760`, but no automated test invokes a suite around a seeded unrelated claim. `tests/integration/test-run-unit-tests-kinds.py:116-129` only pins registration/exclusion; the sole suite-preservation implementation is unrun live-probe S4. See `notes/review-harness-qa-c0.md:3,23,38-40`. |
| SC-02 | met | automated | Unit matrix 98/98 hook cases; exact bind/reclaim/held paths at `tests/unit/omp-hooks.test.ts:1875-2001`, red on baseline. See `notes/review-harness-qa-c0.md:11,24`. |
| SC-03 | met | automated | Registry run-start, PM conflict, canonical root, and exact recovery at `tests/integration/test-inflight-registry.py:1238-1410`; feature-worktree release is red on baseline. See `notes/review-harness-qa-c0.md:25`. |
| SC-04 | met | automated | Reordered actual ids, never-started receipt rollback, and lifecycle settlement at `tests/unit/omp-hooks.test.ts:2003-2113`, red on baseline. See `notes/review-harness-qa-c0.md:26`. |
| SC-05 | met | automated | `tests/integration/test-check-omp-port.py:194-214` makes the wrong `pi.on` bus fail and the pin pass. See `notes/review-harness-qa-c0.md:27`. |
| SC-06 | met | automated | Feature-root release, exact held child, next-yield recovery, and parent-only release at `tests/integration/test-validate-digest.py:5769-5844`, red on baseline. See `notes/review-harness-qa-c0.md:28`. |
| SC-07 | not_met | uat | No live OMP receipt exists. This is the declared operator-run merge gate, not a panel failure. See `notes/live-omp-probe.md:1-43` and `notes/review-harness-qa-c0.md:36`. |
| SC-08 | met | inspection | Pinned DEC-204/DEC-100 text, index row, and `notes/ship-checklist.md:13-115` pass inspection. See `notes/review-harness-qa-c0.md:32-34`. |

## Finding and must-fix

### GC-01 — automated suite preservation is unproved

- **kind:** substance
- **severity:** high
- **reader:** harness-pm
- **owner:** T-03/T-04
- **scope change:** no; the clause is already explicit in SC-01 and both tasks trace it
- **concrete failure scenario:** a suite invocation regresses to releasing a claim it does not own. Direct digest cases still preserve their fixtures, the runner-kind declaration still passes, and both configured matrices remain green because none seeds an unrelated live claim around a suite invocation. The operator probe would detect the defect only if SC-07 is later run, which cannot satisfy SC-01's `verify: automated` contract.
- **must fix:** add a non-recursive automated suite-plus-sentinel case that fails on claim mutation and passes at the implementation pin, or obtain approval to narrow SC-01. Keep SC-07 as an independent live-runtime gate.
- **evidence:** `notes/review-harness-qa-c0.md:3,38-40`; `plan.yaml:219-226`; `tests/manual/probe-inflight-claim-lifecycle.py:412-432`.

## Assessed and dismissed simplify candidates

1. **Runtime-id `settleRun` dedupe** — `kind: correctness`; `severity: high if applied`; `reader: harness-pm`; owner T-02; dismissed. Concrete scenario: a settled run wakes and reclaims under the same runtime id; process-wide dedupe suppresses its second settlement release and leaks the new claim. The current per-dispatch settled set and one-spawn `release-run` keep the required idempotence without breaking revival (`runs/build-main-direct/digest.md:42-47`; `tests/unit/omp-hooks.test.ts:1892-1905`).
2. **Share `authorize_runtime_identity`'s `_is_unbound_receipt` predicate** — `kind: proportionality`; `severity: low`; `reader: harness-pm`; owner T-01; dismissed. Concrete scenario if the candidate-set semantics drift: a receipt with the wrong parent/runtime becomes eligible, or a valid direct run claim becomes ineligible, producing cross-attachment or a false hold. The shipped paths are green and the refactor has no signed behavioral need, so changing selection during validation would add risk rather than discharge a criterion (`runs/build-main-direct/digest.md:48-49`).
3. **Drop `_held_children`'s lead/orchestrator pre-filter** — `kind: maintainability`; `severity: low`; `reader: harness-pm`; owner T-03; dismissed at this pin. Concrete future scenario: a newly task-enabled governed non-lead could yield while its child remains live if the predicate were not updated. That seat does not exist at the pin: the only agent headers granting `task` are the three team leads, all normalized to `lead`, and `harness-orchestrator`; the current filter therefore misses no dispatch-capable governed seat. Removing it now adds a registry read on every governed return without protecting another reachable path. Revisit with a discriminating held-child test if another persona receives `task` (`84c3a6c:.omp/agents/harness-{product,eng,validator}-lead.md:8`; `84c3a6c:.omp/agents/harness-orchestrator.md:8`; `validate-digest.py:2260-2269`).

No candidate is an open finding, and none repairs GC-01.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "At 84c3a6cbe74c7c27337d4372a68be60fca834118, orchestrator, maintainer, and reader outcomes pass, but operator is partial because SC-01 lacks automated suite-plus-sentinel proof; SC-07 remains the separate pending operator merge gate."
  reviewed_sha: 84c3a6cbe74c7c27337d4372a68be60fca834118
  reviewed_range: a4d72e7fc91d0cf7a568d9e2a5225465a422170e..84c3a6cbe74c7c27337d4372a68be60fca834118
  feasibility: clear
  surface: L
  flags: [coverage-gap, exact-identity, lifecycle, operator-merge-gate]
  recommend: proceed
  tasks: 5
  decisions: 7
  needs_approval: false
  risk: high
  perspectives:
    - { perspective: operator, grade: partial, carrying_sc: "SC-01, SC-07", evidence: "notes/review-harness-qa-c0.md:3,23,36,38-40" }
    - { perspective: orchestrator, grade: pass, carrying_sc: "SC-02, SC-04, SC-06", evidence: "notes/review-harness-qa-c0.md:24,26,28" }
    - { perspective: "code maintainer", grade: pass, carrying_sc: "SC-03, SC-05", evidence: "notes/review-harness-qa-c0.md:25,27" }
    - { perspective: reader, grade: pass, carrying_sc: SC-08, evidence: "notes/review-harness-qa-c0.md:32-34" }
  sc_status:
    - { id: SC-01, verdict: partial, method: automated, evidence: "Direct preservation passes; automated suite-plus-sentinel case absent — notes/review-harness-qa-c0.md:3,23,38-40" }
    - { id: SC-02, verdict: met, method: automated, evidence: "notes/review-harness-qa-c0.md:11,24; tests/unit/omp-hooks.test.ts:1875-2001" }
    - { id: SC-03, verdict: met, method: automated, evidence: "notes/review-harness-qa-c0.md:25; tests/integration/test-inflight-registry.py:1238-1410" }
    - { id: SC-04, verdict: met, method: automated, evidence: "notes/review-harness-qa-c0.md:26; tests/unit/omp-hooks.test.ts:2003-2113" }
    - { id: SC-05, verdict: met, method: automated, evidence: "notes/review-harness-qa-c0.md:27; tests/integration/test-check-omp-port.py:194-214" }
    - { id: SC-06, verdict: met, method: automated, evidence: "notes/review-harness-qa-c0.md:28; tests/integration/test-validate-digest.py:5769-5844" }
    - { id: SC-07, verdict: not_met, method: uat, evidence: "notes/live-omp-probe.md:1-43 — no live receipt; operator merge gate pending, not a panel defect" }
    - { id: SC-08, verdict: met, method: inspection, evidence: "notes/review-harness-qa-c0.md:32-34; pinned DEC-100/DEC-204/index/checklist" }
  merge_gate:
    status: blocked
    validation_blocker: GC-01
    operator_gate: "SC-07 live OMP PASS remains required after GC-01 is repaired; dry-run is not a receipt."
  findings:
    - id: GC-01
      kind: substance
      severity: high
      reader: harness-pm
      scenario: "A suite releases an unrelated live claim, while direct digest tests and both configured matrices remain green because no automated suite-plus-sentinel case exists."
      owner: "T-03/T-04"
      scope_change: false
      evidence: "notes/review-harness-qa-c0.md:3,38-40; plan.yaml:219-226"
  must_fix: [GC-01]
  assessed_candidates:
    - { candidate: "settleRun runtime-id dedupe", disposition: dismissed, kind: correctness, severity: high-if-applied, reader: harness-pm, scenario: "A revived same-id run's later settlement is skipped and its fresh claim leaks.", owner: T-02 }
    - { candidate: "share _is_unbound_receipt in authorize_runtime_identity", disposition: dismissed, kind: proportionality, severity: low, reader: harness-pm, scenario: "Candidate-set drift cross-attaches a receipt or falsely holds a valid run.", owner: T-01 }
    - { candidate: "remove _held_children role pre-filter", disposition: dismissed-at-pin, kind: maintainability, severity: low, reader: harness-pm, scenario: "Only a future newly task-enabled non-lead could be missed; no current dispatch-capable governed seat is outside lead/orchestrator.", owner: T-03 }
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle/.harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/research-BUG-1898-inflight-claim-lifecycle-goalcheck-validate-c0.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle/.harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/research-BUG-1898-inflight-claim-lifecycle-goalcheck-validate-c0.md
```
