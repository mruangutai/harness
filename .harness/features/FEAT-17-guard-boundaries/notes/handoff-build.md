# Handoff — FEAT-17-guard-boundaries, build → validate/ship — written at e4336a3, seq-1

## Next

STOP AND ASK THE OPERATOR — do not dispatch. All seven plan.yaml tasks have landed and the four
gates are green, but the SC goal-check (BRIEF SC-01..SC-10) has NOT been run and the feature has not
been moved to Review. The build dispatch reserved that decision to the operator explicitly. When the
operator releases it, the next action is pm's goal-check through harness-product-lead, against
BRIEF.md `## Success Criteria`; SC-09 is the only `verify: inspection` criterion and rests on
notes/worktree-list-before.md, notes/worktree-list-after.md and the tag archive/worktree-r6.

## Trust

- All 7 tasks landed; T-07 at 01d8f60, T-01..T-06 at 5854d12/f869cd3/3d327dd/a665465/0d9ba16/232fe06 — `git log --oneline` on feat/FEAT-17-guard-boundaries — verified-at e4336a3
- T-07 verify passes on the COMMITTED tree and regeneration is byte-identical — re-ran the verify clause, then `git status --porcelain` empty — verified-at 01d8f60
- check-state.sh exit 0; check-plan-routes.py exit 0 with 0 violations across 8 plans — ran both directly — verified-at e4336a3
- run-unit-tests.sh exit 0, 152 PASS / 0 FAIL, and all four relevant suites ran — /tmp/feat17-units.log, grepped for each suite by name — verified-at e4336a3
- DEC-193 carries all 3 deliberate divergences, the --resolve note, and the root-side/target-side split — read docs/harness/DECISIONS.md:5687-5763 directly, not the digest — verified-at 01d8f60
- The index is generated EXCEPT the ruling after ` :: `, which its author hand-writes — the file's own header, plus test_preserves_hand_written_rulings_by_dec_number — verified-at 01d8f60
- plan.yaml's T-07 intent anchor "line 676" is ROTTEN; the gate is at check-domain.sh:534 — `sed -n '534p'` and `sed -n '676p'` — verified-at e4336a3
- SC goal-check has NOT been run; no SC has been verified by its declared method this phase — UNVERIFIED against the criteria themselves

## Dead ends

- Do NOT re-run or re-dispatch T-01..T-06 — plan.yaml execution_mode main-session-direct under the DEC-174 carve-out; they were executed directly and are committed — verified-at e4336a3
- Do NOT hand-edit docs/harness/DECISIONS-INDEX.md left of ` :: ` — regenerate with gen-decisions-index.py; the ruling right of ` :: ` is the exception and is already written — index header, verified-at 01d8f60
- Do NOT flip T-07's status in plan.yaml — plan.yaml is pm's domain, not the orchestrator's; the observed convention (f9488a2) is the main session records done — playbook authority boundary, verified-at e4336a3
- Do NOT add a `phase:` key to feature.json — DEC-191 closed the key set with additionalProperties false and DEC-192 deleted `phase`; `status: Building` carries it — feature-schema.json, verified-at e4336a3

## Working set

- .harness/features/FEAT-17-guard-boundaries/BRIEF.md — the 10 SCs the goal-check runs against
- .harness/features/FEAT-17-guard-boundaries/plan.yaml — T-07 intent at lines 928-983; approval + ruling R-01 at lines 4-40
- .harness/features/FEAT-17-guard-boundaries/feature.json — 7 runs, cycles 6/10, status Building
- docs/harness/DECISIONS.md:5687 — DEC-193, this feature's only doc deliverable
- .harness/features/FEAT-17-guard-boundaries/runs/2026-08-12-07-t07-product/digest.md — the T-07 run
