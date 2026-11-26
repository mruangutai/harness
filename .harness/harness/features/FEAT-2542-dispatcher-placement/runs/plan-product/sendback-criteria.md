# Send-back criteria — FEAT-2542 plan-product, written before any return (P-05)

## draft (pm) — FAIL / send back if any holds
1. BRIEF.md or plan.yaml missing, or plan not `approval.status: pending`, or `approval:` beyond pending written, or `panel:` written.
2. `plan-merge.py check --file <plan.yaml> --root <worktree>` not reported exit 0 with its output line.
3. Grilling rulings re-decided: #2532 discriminator not inside `_mission_scope`, keyed on anything but trusted placement (claim -> feature -> one open registered run -> DISTILL_RUN_RE); a preflight reorder; exemption resting on declared text / child field.
4. #2542: any of the five placement states not exit-2 lineage denial naming cause+remedy; `emit_unavailable` not rejected; Main / non-lead path changed; terminal claim-step pass-through changed.
5. DEC: no new DEC task; `decisions_affected` amends/strikes DEC-100 or DEC-253 (each may appear only as `keep` with reason, or be absent with the reason stated).
6. SCs written as instance lists rather than classes with invariant + LEAVE list; SC-route / SC-placement / SC-characterization / SC-record missing.
7. Characterization note `notes/research-*.md` missing, or rows not measured (no exit code + message), or registries empty/stub, or no row proving harness_agent_id + dispatcher in LEADS reached the branch, or no FEAT-2489 product->code-reviewer distill row; or the probe left anything in the worktree / edited dispatch-guard.py or its test.
8. Any task lacking `execution_mode: main-session-direct`; any task routed through a team run.
9. Non-goals not carried verbatim; test matrix misses: case-33 extension, placement-state cases, exemption-does-not-fire-on-failed-placement, cases 32-37 green, sc02_scope_reader + sc02_plan_status_refusals unmodified anchors.
10. Rework 2 rounds / 90 min written as approval rather than proposal.

## apply (pm)
- record-panel and check both exit 0 reported; every substance/form finding has an explicit disposition; scope: mission findings left untouched.

## goalcheck (pm)
- one grade per declared perspective against the grilling (not the BRIEF), naming SCs + tasks.
