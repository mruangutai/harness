# STATE

## Current

- feature: FEAT-2037-product-document-guidance
- run: runs/simplify-c1-eng/digest.md (CLOSED PASS, cycles 0; squad engineering; reuse PASS 2/0 · simplification PASS 2/0 · efficiency PASS 1/0 · altitude PASS 1/0; accepted 0; must_fix []; amendments []; severity_max low) · runs/validate-validator (CLOSED ESCALATE, pre-#2131 contract) · runs/simplify-eng (CLOSED BLOCKED --refused-return; cause: registered squad `eng`, binding requires `engineering`) · runs/qa-validator (CLOSED ESCALATE) · correction-verify-product PASS · preflight-product PASS · preflight-eng BLOCKED --refused-return · plan-product PASS
- squad: none (all runs terminal)
- status: review (plan.yaml; T-01 done; cards #2037/#2072/#2073 at review)
- mission: patch
- cycles_used: 0/10 (rework_rounds 0 of 1; rework_minutes 21 of 45 at simplify-c1-eng close; total runs 8, wall_clock_minutes 94, tokens 277410)
- review_sha: see feature.json — re-pinned at the post-simplify seam commit, which contains the unchanged four-file +33/-3 T-01 diff (37cfcfd4..HEAD on the four T-01 paths)
- brief: BRIEF.md (approved; bytes unchanged this run)
- plan: plan.yaml (approved operator/2026-10-05; T-01 signed hash f5538093…671b unchanged; only `status:` moved building→review via gh-sync this run)
- sc-04: PASS by independent inspection at 1e69bf14 — notes/review-harness-code-reviewer-c0.md. That inspection predates the origin/main merge: upstream edits to harness-spec-driven/SKILL.md and SPEC.md now sit in the same files (git diff 1e69bf14 HEAD on the four paths: 2 files, +104/-4, all upstream), while the T-01 hunk itself (37cfcfd4..HEAD) is the same +33/-3. SC-04 must be re-inspected at the new pin by the validate rerun
- sc-01..03: NOT RUN — verify: uat, operator-only; notes/uat-product-document-guidance-c0.md, 27 assertions NOT RUN
- validate rerun: NOT DISPATCHED — two prerequisites outside orchestrator authority (Q-08, Q-09)
- next: operator/main resolves Q-08 and Q-09, then re-delegate: dispatch validate-c1-validator over the pinned review_sha (qa, code, security, ui, goalcheck); must_fix routes to MAIN (all four production paths are NOBODY/main-session-direct), never a fix run. No PR, merge, distill, ship or issue closure.

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
