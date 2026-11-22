# Receipt — main session — FEAT-2225 validate c1 fix segment (F1–F3; main-session-direct, DEC-174)

**BLUF.** All three c1 must-fixes landed with red-first regressions. Handoff: `notes/handoff-validate.md`
seq-6. Panel digest: `runs/r-20261121-6-validate-validator/digest.md`. Generic task workers acting
for the main session built the slices to a shared contract (file ownership disjoint). The main
session integrated them and committed.

| Finding | Change | Red → green |
|---|---|---|
| **F1** high, SC-03: the prose distill marker authorized application | `validate-digest.py --distill-authority` is a CLI over the existing yield lineage code (`_registered_distill_context`), with no second implementation. `expertise_apply` calls it before `member-ops` and refuses unless it answers `{"authorized": true}`. `dispatch-guard.py` refuses a `HARNESS-MISSION: distill` dispatch or lead start that has no bound `distill-*` run; the orchestrator keeps its authority from the feature's registered distill run. | `notes/red-first-fix-c1-digest.md`: authority 0/10, dispatch-guard 158/161 → 10/10, 161/161. `notes/red-first-fix-c1-host.md`: omp-hooks 2 fail → 0. Real regression: a marker under a `build-*` run refuses both lead and member, and no file or receipt is written. |
| **F2** high, SC-02: `verify-receipt` compared only the recorded op keys | `expertise-merge.py verify-receipt` walks the destination's recorded write chain back from the current sha256 to HEAD (or the base). The chain must cover every active batch of the caller, otherwise exit 15 `UNRECEIPTED CONTENT`. Exit contract unchanged, so validate-digest inherits the check. | `notes/red-first-fix-c1-core.md`: unit 1 FAIL, integration 3 FAIL → 0. validate-digest F2 group 2/6 → 6/6, covering live yield and durable close. |
| **F3** med, SC-01: no real host→core representative coverage | The `omp-hooks.test.ts` real-host describe drives `expertise_apply.execute` → real inflight_registry → `--distill-authority` → `member-ops`. Representatives: product-lead, code-reviewer, dev-ops, orchestrator, backend-dev. Each does craft and repository add/replace/drop, checks the verbatim receipt and file content, and passes `verify-receipt`; a forged persona claim is refused. `test-member-expertise.py` keeps the all-16 configuration and guidance checks; its direct-CLI flows were removed because they bypassed the host. | `notes/red-first-fix-c1-host.md`: a mutant forwarding `--persona harness-qa` failed all five representatives. |

## Integration changes by the main session

- `tests/integration/test-lead-start-return.py`: the three `SC-02/<lead>/distill` controls now start on a registered `distill-<suffix>` run. New refusal cases cover the same marker on an `r1-*` run, one per lead.
- `tests/integration/canonical-reader-classification.json`: a row for `validate-digest.py::_authority_request` (`read_hook_payload`, canonical).

## Known limits (stated, not hidden)

- `verify-receipt` cannot see an unreceipted edit that is already committed at HEAD. The merge-time `replay --check` and `merge-distill` blob comparison catch it.
- After a mutating `replay` rewrites a destination onto a new main, `verify-receipt` refuses that file. From then on only the merge path verifies it, which is the DEC-253 order (close, then replay, then merge).
- `harness-hooks.ts` and `omp-hooks.test.ts` are TypeScript, which code-grade does not grade.

## Yield-gate refusals in c1 (QA-RETURN open question)

The root cause is operational, not a code defect. The OMP process hosting this session started at
07:15 on 2026-11-21. The BUG-2171 fix that accepts JSON-text yield data (`594af2a8`, #2230) landed at
12:06. Every Harness agent spawned here runs the stale loaded hook, which refuses `{"data": "<json
text>"}`. The refused QA transcript shows exactly that argument shape. Remedy: restart the session
before validate c2.
