# Goal-check — FEAT-1928 reconciled plan against operator intent

## Verdict

PASS. The reconciled plan fully covers the unchanged BRIEF perspectives and every stated reconciliation condition. This is a plan-coverage verdict, not implementation evidence: BRIEF and plan approval are pending, and the future post-FEAT-70 re-anchor remains an explicit T-04 pre-start gate.

## Perspective grades

- **operator — PASS — SC-01, SC-04, SC-05 → T-02.** T-02 owns strict schema-control refusal and injection for all Harness dispatches, including main-session and batched items; it blocks malformed text, null, absent data, wrappers, and malformed mappings; and it requires the credentialled null-rejection/retry/valid-completion receipt before deleting the host workaround (`plan.yaml` T-02 `intent`, `files`, and `verify`).
- **orchestrator — PASS — SC-02 → T-02.** T-02 hard-cuts every live persona return to the typed object, preserves persona field semantics, replaces all named fenced return templates with schema pointers and complete object examples, and adds the remaining-template census (`plan.yaml` T-02 `intent`).
- **code maintainer — PASS — SC-03 → T-01, T-02; SC-08 → T-02, T-03.** T-01 creates the 16 canonical closed schemas and separate live/historical Python adapters; T-02 derives and caches ref-free provider bundles from those files, runs the canonical provider suites, and removes duplicate text-era machinery; T-03 consolidates the decision and current doctrine without changing DEC-208 (`plan.yaml` T-01–T-03 `traces` and `intent`).
- **reader — PASS — SC-06 → T-02; SC-07 → T-01, T-02, T-03, T-04.** T-02 owns baseline/object parity, validated deterministic append, state-reader migration, and historical byte/readability proof; T-01 owns final-fenced historical mapping selection and byte identity; T-04 narrowly migrates the five plan-reader symbols while preserving panel/amendment semantics; T-03 documents the durable format (`plan.yaml` T-01–T-04 `traces` and `intent`).

## Reconciliation acceptance conditions

- **PASS — c0/c1 history preserved.** `plan.yaml panel.readers` retains c0 scope, should-not-exist, and design as `ran`, plus c1 scope and goalcheck as `ran`. Its first six findings retain the six c0 identities, severities, kinds, resolved dispositions, resolutions, and the proportionality scopes: `PF-46c11c31db161761db0befcad94fd5e4`, `PF-2152e99c614b8117f2d5d7cb07da4650`, `PF-c1933229b1130a1069210611b7fa6716`, `PF-07c8bfd5b15e0be57f42a6411b08f4d6`, `PF-cc37152910176cfd4e8609a231d529e7`, and `PF-6f1d2cf3ee6a1a5c4a1d8b6e6e1649`. This agrees with `runs/plan-product/panel-c0.md`, `runs/plan-c1-product/panel-c1.md`, and the apply receipt.
- **PASS — every drift correction is explicit.** T-01 requires direct-route canonical-reader rows and `scanned_files`, bans broad catches and a second private importlib loader. T-02 retargets `_inv15_digest_verdict` to `check_state/run_state.py`, owns `ctx.py`, `table.py`, `feature_record.py`, and the FEAT-69 structure lock, preserves exactly one invariant owner, updates INV-15/46 declared reads, and explicitly deletes the #1960/#1969 string and last-message branches plus both named pinning tests. The lane covers `check-state.py and check_state/**`. T-04 handles the FEAT-70 symbol move. These exhaust the corrections in `agent://PlanDrift/report` and `local://feat1928-drift.md`.
- **PASS — FEAT-70 gate is narrow.** Only T-04 has the FEAT-70 hard pre-start gate. Its moving source slice is exactly `_lead_digest`, `_digest_mapping`, `_digest_findings`, `cmd_record_amendments`, and `cmd_record_panel`, with only their owning reference and integration-test surface. T-01 and T-02 explicitly remain runnable while T-04 waits; T-03's dependency is final doctrine sequencing rather than a second FEAT-70 implementation gate (`plan.yaml` T-04 `files`, `depends_on`, and `intent`).
- **PASS — post-merge re-resolution and approval handling are explicit.** T-04 requires FEAT-70 to be merged into the feature worktree, resolves all five symbols to exact package-module anchors, updates its `files` through the control-plane plan-merge apply/amend verb, invokes the resolved post-FEAT-70 check entry point with the feature plan and worktree root, and requires zero failures. If this occurs after a signature, the files amendment resets approval and implementation cannot start until operator re-signature; if FEAT-70 lands first, re-anchor and check precede the first signature (`plan.yaml` T-04 `intent`).
- **PASS — enforcement routing is direct.** T-01, T-02, and T-04 are `main-session-direct`; the lanes route schemas, adapters, validator, hook, dispatch guard, state/plan readers, enforcement configuration, owning tests, and runtime contract files directly. T-03 is the sole team task and owns only decision/doctrine/operator-documentation files (`plan.yaml lanes` and task `execution_mode`).
- **PASS — approvals are pending.** `BRIEF.md Approval.status` is `pending`; `plan.yaml approval.status` is `pending`, records the T-04 reset reason, and has `needs_approval: true`.
- **PASS — historical rework ruling preserved.** `feature.json rework` remains `rounds: 2`, `wall_clock_minutes: 90`, pointing to `notes/approval-2026-09-28.md`, whose approval record states the same ruling.
- **PASS — settled scope and design are unchanged.** BRIEF still contains SC-01–SC-08 and the same four perspectives; `plan.yaml` retains D-01–D-05. Reconciliation changes are confined to drift-correct task ownership/anchors/intent, the added T-04 phase boundary, panel history, and the consequent approval reset. Nothing in the grilling record's settled destination, schema authority, hard cut, parity, live null gate, durable append rules, or decision cutover is reopened (`.harness/notes/grilling-digest-object-contract-2026-09-28.md`; apply receipt `Conclusion`).

## Scoped check evidence

The apply receipt is sufficient evidence for the reconciled plan's current scoped structural gate: it names the exact command and root, reports each task separately (`T-01` 22, `T-02` 36, `T-03` 6, `T-04` 7 anchors), and records `4 task(s), 71 anchor(s) resolved, 0 failure(s)`. That is the appropriate feature-scoped check; a project-wide check was neither needed nor claimed.

The one evidence-horizon gap is expected: this receipt cannot prove the post-FEAT-70 package locations or the later amended plan check because FEAT-70 has not yet supplied those locations. T-04 closes that gap as a mandatory pre-start re-resolve/update/check and re-signature gate. No present reconciliation acceptance condition is left uncovered.

## Principles applied

- **Experience First** — graded the plan in the words of all four unchanged BRIEF perspectives rather than treating a green structural check as the product outcome.
- **Outcome-Oriented Execution** — accepted the narrow FEAT-70 phase boundary because it protects the final symbol-resolved state without serializing unrelated T-01/T-02 enforcement work.

## Open questions

None.
