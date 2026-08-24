# Handoff — FEAT-35, validate → ship — written at e0ae671 (STALE PIN), seq-4

## Next

**Two operator rulings, in this order — the first changes what the second is graded against.**
(0) Commit the uncommitted `SKILL.md` nonce fix and RE-PIN `review_sha`; then re-confirm SC-01/02/04
and re-grade SC-06. (1) Rule on SC-03's third clause: the `context-watch.py` row cannot be produced
by any reviewer. My read, matching the c2 lead's: accept the tool's rejection as evidence of
fail-closed behaviour. **Do not dispatch a fourth SC-03 run before both are settled** — three runs
have failed, each on a different gate, and a fourth against unsettled text repeats the mistake that
produced c1 and c2.

## Trust

- SC-03 UNMET three times, new cause each time: c0 empty candidate set, c1 non-unique nonce, c2 tool-level type filter — `runs/2026-08-24-01/-02/-03-validator/digest.md` — verified-at e0ae671
- `context-watch.py` hard-filters: `:53` `ORCHESTRATOR_AGENT_TYPE`, `:303-304` `return None` for any other agentType — **I read both lines myself, not relayed** — verified-at e0ae671
- The c2 run got EXACTLY ONE match and derived the id correctly — the nonce fix works; only the third clause fails — `notes/review-harness-code-reviewer-c2.md:36-43` — verified-at e0ae671
- **The pin is STALE**: `SKILL.md` modified+uncommitted; working tree greps 0 for `7Q4X2M9K`, `e0ae671` greps 2. Merging as-pinned ships the defect — I ran both greps — verified-at e0ae671
- SC-06's c0 certification covers `SKILL.md:99-138`; the uncommitted edit lands inside it, so that grade is stale — c2 lead A-2 — UNVERIFIED by me
- `context-watch.py --warn-for` (`:481`) applies no agentType filter but returns None below threshold — partially confirmed by me; bears on any re-spec — UNVERIFIED in full
- SC-01/02/04/07 met, SC-05 `partial` with post-merge obligation (owner: main session, next build/validate phase); matrix_ok FALSE, accepted — verified-at e0ae671
- Both artifacts signed `approved`/`operator`/`2026-08-24` — `BRIEF.md:142-146`, `plan.yaml:4-7` — verified-at e0ae671

## Dead ends

- Do not dispatch a fourth SC-03 run before the pin moves and the third clause is ruled on — three failures, three distinct gates — verified-at e0ae671
- Do not grade SC-03 via `git show <pin>:` — the pin holds the defective playbook — verified-at e0ae671
- Do not expect any reviewer to produce the `context-watch.py` row — the filter is permanent for every non-orchestrator agentType — verified-at e0ae671
- Do not attempt SC-05 pre-merge — unsatisfiable by construction — answers Q2 — verified-at e0ae671
- Do not set `parent_origin: created`; do not write `base` into feature.json; do not re-file #803/#804/#805/#806/#808/#810 — verified-at e0ae671
- Do not git-restore anything under `runs/` — gitignored at `.gitignore:7`; the `-01-validator` digest is a context reconstruction, content-faithful not byte-identical — verified-at e0ae671

## Working set

- `.harness/harness/features/FEAT-35-orchestrator-stop-and-wake/notes/ship-review-2026-08-24-validate.md`
- `.harness/harness/features/FEAT-35-orchestrator-stop-and-wake/runs/2026-08-24-03-validator/digest.md`
- `.harness/harness/features/FEAT-35-orchestrator-stop-and-wake/notes/review-harness-code-reviewer-c2.md`
- `.harness/harness/features/FEAT-35-orchestrator-stop-and-wake/BRIEF.md`
- `.harness/harness/features/FEAT-35-orchestrator-stop-and-wake/feature.json`
