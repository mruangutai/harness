# STATE

## Current

- feature: FEAT-2037-product-document-guidance
- run: runs/validate-c1-validator/digest.md (CLOSED ESCALATE, cycles 0; squad validator; pin 17c3cd5b; qa PASS · code PASS · security PASS · ui PASS · goalcheck ESCALATE; must_fix []; severity_max none; findings []; matrix_ok true; SC-04 met; SC-01..03 not_met uat NOT RUN) · simplify-c1-eng (CLOSED PASS) · validate-validator (CLOSED ESCALATE, pre-#2131, superseded) · simplify-eng (CLOSED BLOCKED --refused-return) · qa-validator (CLOSED ESCALATE, superseded) · correction-verify-product PASS · preflight-product PASS · preflight-eng BLOCKED --refused-return · plan-product PASS
- squad: none (all runs terminal)
- status: review (plan.yaml; T-01 done; cards #2037/#2072/#2073 at Review, verified via gh)
- mission: patch
- cycles_used: 0/10 (rework_rounds 0 of 1; rework_minutes 32 of 45; total runs 9 of 20 informational; wall_clock_minutes 105; tokens 340968; judgements 11)
- review_sha: 17c3cd5b (unchanged; 17c3cd5b..HEAD touches only feature records; canonical range 37cfcfd4..17c3cd5b = four T-01 paths +33/-3)
- brief: BRIEF.md (approved; one Verification-gaps bullet reworded by operator 3a386e7e, Q-09; main validate-digest.py probe: malformed False, nonautomated waiver True)
- plan: plan.yaml (approved operator/2026-10-05; T-01 signed hash f5538093…671b unchanged; unchanged this run)
- goalcheck c1: operator fail (SC-01) · orchestrator fail (SC-02) · reader partial (SC-04 met, SC-03 not_met) — notes/research-FEAT-2037-product-document-guidance-goalcheck-validate-c1.md
- sc-04: PASS by independent inspection at 17c3cd5b — notes/review-harness-code-reviewer-c1.md:9-15 (four pinned reads, file:line per file)
- sc-01..03: NOT RUN — verify: uat, operator-only; notes/uat-product-document-guidance-c0.md, 27 assertions NOT RUN
- briefing: notes/ship-review-validate-c1-validator.md (backlog B-1..B-4)
- next: operator runs and records the 27-assertion UAT (Q-11); on pass, main decides merge (fast-forward of four files from 37cfcfd4). No fix target exists: must_fix [] and all four production paths are main-session-direct. No PR, merge, distill, ship or issue closure by the orchestrator.

## Open Questions

- Q-01 (nonblocking, execution-time): edited harness-principles delivery to governed subagents must be shown with loaded-source evidence before SC-01..SC-03 can be graded; notes/research-preflight-product.md, notes/receipt-harness-dev-ops-preflight-eng.md.
- Q-02 (nonblocking, execution-time): main must capture actual nested dispatches/absolute reads and byte-restore decoys in the observed CONTROL, never staged in the main checkout.
- Q-03 (RESOLVED this run): refused eng-lead returns were runs registered `--squad eng`; digest_destination.LEAD_SQUADS binds harness-eng-lead to `engineering` (both pre- and post-#2131). simplify-c1-eng registered `engineering` and its return landed with the fenced record.
- Q-04 (harness defect, nonblocking): plan-merge amend by harness-pm ledgered the T-01.verify amendment judgement with `by: main-session`.
- Q-05 (SUPERSEDED by Q-08/Q-09): post-#2131 validate-digest.py exempts fail_first [] when every BRIEF SC is inspection/uat and no SC declaration is malformed.
- Q-06 (harness defect, nonblocking): code-reviewer's note reads `code_grade: pass` while its accepted return was corrected to `n_a`; reviewer-owned, not repaired.
- Q-07 (MAIN assessment, historical): earlier orchestrator advanced past QA ESCALATE and refused SIMPLIFY; history preserved.
- Q-08 (BLOCKING, main-session): the main checkout /Users/molchairuangutai/GitHub/harness is at 2d28b79e and does not contain 37cfcfd4 (#2131). harness-hooks.ts gateRoot() resolves every gate from the main checkout, so the host's validate-digest.py (L1506) still refuses QA PASS + matrix_ok true + fail_first [] unconditionally, and .omp/agents/harness-qa.md there still carries the old rule. A validate rerun now reproduces the ESCALATE. Needs a fast-forward of the main checkout to origin/main (HEAD move — refused for the orchestrator) and a hook reload.
- Q-09 (BLOCKING, operator ruling): even the #2131 copy fails closed on this BRIEF: `_malformed_sc_declarations` matches the `## Verification gaps` bullet `- SC-01–SC-03 are NOT RUN YET.` (a bullet naming SC- without the `SC-NN:` declaration shape), so `_known_nonautomated_criteria` is False. Probe with the worktree copy: rewording that one bullet to `- The three UAT criteria (operator, orchestrator, reader) are NOT RUN YET.` flips it to True with all four SCs read as uat/inspection. The BRIEF is operator-approved; recommendation: authorize that one-line form reword (pm or main-session-direct), no SC text or approval change.
- Q-08 (RESOLVED 2026-10-07): main checkout at 37cfcfd4; host gates carry #2131.
- Q-09 (RESOLVED 2026-10-07): operator reworded the bullet in 3a386e7e (notes/receipt-operator-brief-reword-2026-10-07.md); waiver verified True against main's validate-digest.py.
- Q-10 (RESOLVED 2026-10-07): BUG-2037-readiness-contracts worktree removed; check-state --feature exits 0.
- Q-11 (BLOCKING, operator): run and record the 27-assertion UAT for SC-01..SC-03; until then goalcheck stays fail/fail/partial and the feature is not done.
- QA-SUITE-NONE (harness defect, nonblocking): validate-digest.py _declined_gate_errors (L1443-1449) refuses an honest qa PASS with suite none when the matrix requires zero kinds; qa ran unit+integration at HEAD unasked to get its return accepted. Backlog B-1; runs/validate-c1-validator/digest.md § Residual host contract issue.
