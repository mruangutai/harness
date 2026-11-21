# T-01 contract-budget maintenance

Blocked before plan mutation: the helper is outside PM ownership and has not been supplied, and the mandated automatic reset is incompatible with existing-field amendments in the current control plane. The supplied CI observation is **75 machine-field lines / budget 50**; the known failing baseline was not rerun. No plan field or approval was changed.

## Preserved-check equivalence

The signed input is feature `plan.yaml`, T-01 `verify`. Retain the three exact commands: `python3 tests/integration/test-check-omp-port.py`, `python3 tests/unit/test-omp-hooks.py`, and `python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit`. Extract the two historical Python blocks and durable append block without changing their assertions, immutable base `b7af829c0207522b43f978b5275a2ebdc96b3210`, real Bun handler invocation, stdout/stderr capture, or invocation-error discrimination. Preserve the complete credentialled live-smoke command as a reference, never execute it during this maintenance. Human-only prefix preservation, canonical `last_fenced_mapping` selection, PASS and artifact identity assertions remain binding.

## Relocated justification

Only the settled-cause explanation and rationale that canonical-reader output alone cannot establish the writer may move here; all prohibitions, implementation requirements, receipt requirements and live-proof obligations stay in intent. The settled cause is native OMP 18.10.2 `task.structured` defaulting off while Harness never opted in: revalidation strips injected `outputSchema`/`schemaMode`, so the child lacks yield and the existing yield hook is not reached. The canonical reader proves readable appended bytes, not which writer produced them; actual child/lead yield calls and hook-triggered append must still be established from traces.

Product guidance read: `AGENTS.md`; mapped `.harness/harness/docs/SPEC.md` §8.3; mapped decisions DEC-174, DEC-182, DEC-229 and DEC-237. Conventional `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` remain absent as the signed intent already records; no substitute guidance is authored.

## Invariants and receipts

Baseline canonical-JSON SHA-256 fingerprints, collected before amendment (not a failing-gate rerun): non-target plan fields excluding tasks/approval/status `cd2ab8b0465c7701ca8823cf66dc32899a80e644b5a5597c31c122d8f2a681c5`; T-01 excluding intent/verify `f23c294b1562d43bef54cd6474542e7c8b060b1ab97873b2ded8282eb0070dca`; BRIEF bytes `75bb5235556b6f41531db120f32f146c87c1b93aa606456823f29b6e1354016b`. These cover task traces, owned files, execution_mode, statuses, lanes, decisions and SCs. Original verify fingerprint: `6f2c492b3a013134c300b9378fd93acf00e30a434f1dee11038afa33a6b86dfa`.

Original extracted proof-body SHA-256 fingerprints: gate `af856b2e508a443d2b71363e1389e989c5767c0b4279ff56bc08e6ecda99b2cb` (18 lines), real hook `274212d4b1709d8b014929e26b0677af59a22cc442c2239753dd1c5eff484848` (19 lines), append `eafaca99a4515f9513704eb466f6cf986c282d246626aef8a2b9f2aa606ee838` (10 lines). Complete live-smoke command: `dc4c49f54f95c096c44215deb690bfc9ec270327a9289302031b9daf83f201a1` (1,516 characters).

## Open questions

- Main must create/own `notes/verify-task-structured.py` and provide its invocation before PM can wire the extracted checks. Ownership was requested directly from Main. `wait` reported: `Nothing to wait for: Main cannot reply before you finish: it is waiting on your result.` The spawning lead was notified of this ownership blocker.
- Main must resolve the reset conflict: control-plane `plan_merge/amend.py#_amended_text` sets `reset=False`; `plan_merge/union.py#_carry_base_items` explicitly resets only task-set changes, not replacement fields; `plan_merge/stations.py#_reset_approval_lines` and product DEC-229 confirm that policy. The stdout constant still mentions task-field changes, but neither replacement route reaches it. Adding/deleting tasks, modifying control-plane source, or calling sign/revoke is not authorized here.

No suites, tests, builds, lint, formatters or live smoke have been executed for this maintenance.

## Verification disposition

Before: 75 (supplied CI report). After: unchanged; no final `_budget_lines` result is claimed because no amendment could land within the prerequisites. Approval remains the original `approved`, signed by `operator` on `2026-11-21`; feature phase remains `review`. No `APPROVAL-RESET:` receipt exists, so the conditional GitHub status synchronization was not invoked. No plan-verb side effects occurred.

The two authorized gates are reserved for after the helper-backed amendment; neither was executed on the known failing baseline:

- PRODUCT root: `python3 .claude/skills/harness/bin/check-plan-routes.py`
- `python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured/.harness/harness/features/BUG-2171-task-structured/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2171-task-structured`

No plan-changing command was run; therefore no gate/reset stdout is fabricated. The exact proof-body and reference fingerprints above let Main verify a helper extraction without replaying any suite or live smoke.
