# FEAT-2225 — validate c5 goal-check

**PASS — SC-01..SC-06 met; C4-F1 repaired at the pin.** Review pin: `7065b650ab3b94bae3175978bfd0cf0d62478c89`; prior c4: `a5d8687f31c9f05fa77f4d16f3634c3869f47b1f`. Read amended BRIEF through pinned git show. Evidence paths below are feature-relative unless explicitly repository paths. No tests, builds, lint, formatters, source edits or replan; no fresh QA or shipment approval claimed.

## Evidence binding and correction

Independent pinned diff confirms exactly eight changed files: repository `.harness/harness/docs/DECISIONS-INDEX.md`, feature.json, the fix receipt and five c4 assessment notes. BRIEF, plan, source, tests, configurations, fixtures and other guidance are unchanged. Therefore c4 evidence subjects and acceptance contract transfer unchanged; this is evidence transfer, not re-execution.

The sole product delta is index line 236: DEC-253 tags change from `[expertise,dispatch,worktree,map]` to `[expertise,dispatch,state,worktree]`; ruling, refs and source anchor remain identical. This directly eliminates the mismatch reported in `research-FEAT-2225-member-expertise-writes-goalcheck-validate-c4.md:22,34` and QA `review-harness-qa-c4.md:23-24,47`. Pinned `receipt-harness-documentor-fix-c4.md`, Commands and outcomes / Actual index diff, records regeneration, comparison exit 1 → 0 and `test_committed_index_matches_a_fresh_regeneration` red → green (12 integration cases passed). Its fix commit is `8257a2e02d84a1fb32f91b24d645cd9404bf092e`. PM independently measured the committed correction, not the executable gates. **C4-F1 medium/substance/T-02 CLOSED by repair**, not authority change.

## Acceptance outcomes — one grade each

| Criterion / perspective | Grade | Evidence and task trace |
|---|---|---|
| SC-01 / operator | met | Carry c4 goalcheck:17: QA c3 fail-first row 43; `tests/unit/omp-hooks.test.ts:3376-3520` five real-host capability representatives, both tiers/all verbs; `tests/integration/test-member-expertise.py:67-86` independent all-16 tool/Write/grant assertions. T-01/T-03/T-04. |
| SC-02 / orchestrator | met | Carry c4:18,24-28: QA c3 rows 38-44 and `tests/integration/test-validate-digest.py#run_member_expertise_committed_tamper_cases`, c2 consolidation/lineage/empty/refusal groups and red-first receipts. Receipt consistency remains proven within the operator-ruled local-ref boundary, shared by live yield and close. T-01/T-03/T-04. |
| SC-03 / code maintainer | met | Carry c4:19: QA c3 guard/authority and fail-first row 45; `expertise-merge.py:1564-1595`, host hooks `:1177-1200`, `validate-digest.py:2017-2029`; amended local-default-ref close boundary plus live-remote merge containment `merge-gate.py:412-478,523-527`. F2 resolved by authorized amendment, not fixed. T-01/T-04. |
| SC-04 / operator | met | Carry c4:20: QA c3 fail-first row 46; `test-expertise-merge.py#case_replay_collision_and_repeat/#case_supersession_flow`, `:2241-2268,2295-2302`, independently discriminating unchained-batch regression. Covers remapping, refusal, supersession/history and repeat safety. T-01/T-03/T-04. |
| SC-05 / orchestrator | met | Carry c4:21: QA c3 fail-first row 47 / red-first-t04-merge-gate.md (23 reds), c2 merge/Main-hook evidence; unchanged `test-merge-gate.py`, Main-hook tests and serialized executor retain live-remote containment and DEC-220 provenance. T-04. |
| SC-06 / code maintainer | met | Carry c4:22 guidance/decision inspection and `review-harness-code-reviewer-c4.md`, SC-06 inspection: SPEC §5.3 `:942-949,970-974`, DEC-253 `:8199-8206,8222-8226`, c2/c3 preserved decision/strike/reference inspection. Fresh pinned index `:236` now matches the formerly failing generated tags; fix receipt above supplies regeneration evidence. T-02/T-03/T-04. |

Repository script/test paths in this table are under `.claude/skills/harness/bin/` and `tests/integration/` respectively where shortened; host hooks are `.omp/extensions/harness-hooks.ts`.

## Perspective coverage and residuals

- **operator — met:** SC-01/04 discharge independent member application, no scribe, preservation and original-author conflict recovery.
- **orchestrator — met:** SC-02/05 discharge verified applied reports, exact consolidation and serialized live-remote merge containment without acquiring another persona's pen.
- **code maintainer — met:** SC-03/06 discharge bounded enforcement, retained grants and current application/decision guidance, now including the corrected index.

F1/high/T-04 and F3/med/T-04 remain CLOSED by unchanged c4 evidence. F2/high/T-01+T-04 remains an operator-ruled boundary (`answers-2026-11-21-f2-ruling.md:10-15`, hardening #2251), not a must-fix. **C4-W1 low/form remains advisory:** unchanged SPEC :945 / DEC-253 :8201-8202 live-yield language does not make live yield stronger than durable close; `review-harness-code-reviewer-c4.md`, C4-W1, documents their shared verifier. SC-02/06 are graded with that accepted boundary, not an invented live-only guarantee. Standing null-typecheck, credentialled handoff probe and historical raw-log limitations remain disclosed; this acceptance assessment does not waive other ship gates.

## SC-09 cadence accounting

This is the assigned validate-phase goalcheck following c4's amendment-induced regrade and C4-F1 correction. Normal cadence remains one goal-check at plan exit and one at validate exit (SPEC §11.6; DEC-231), never per cycle. As recorded in c3's SC-09 cadence section and c4:3, these extra targeted regrades are an explicit execution-history deviation, not permission for per-cycle checks, a seventh feature criterion or a new approval. SC-01..05 are carried by citation; SC-06's failed index clause is freshly reassessed.

Open questions: none. Must-fix: none. Final executable verification remains QA-owned.
