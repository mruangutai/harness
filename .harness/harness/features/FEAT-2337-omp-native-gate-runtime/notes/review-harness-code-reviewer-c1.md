# FEAT-2337 code review c1

**PASS — no actionable spec-compliance or code-quality findings in T-01–T-03.** Static review, not a QA execution receipt.

## Scope and stage 1 — compliance

Reviewed `0d7326e40137dfce63f5b7b33af95ee126f90971..6143625f5262f246d51d642662899a44a8d545d9`, excluding feature records. Independently confirmed merge-base, feature.json pin, full commit list and no `[harness:human]` commits. The later checkout HEAD `04db582f` changes only feature bookkeeping; its source matches the pin. Initial tracked dirt was feature.json only.

All 24 source paths bind to T-01, T-02 or T-03; test-merge-gate.py is explicitly added by the approved timeout ruling. Read BRIEF, signed decisions, apply research and all four answers notes, including the fix-run clean-tree clarification. AGENTS.md maps product guidance to `.harness/harness/docs/{SPEC,DECISIONS}.md`; no architecture document exists. No unapproved omission, mismatch or scope growth found.

- **SC-09 inspection:** pinned `DECISIONS.md:1370–1422,8394–8462` rewrites DEC-100 in place and adds DEC-255; DEC-174/205/234 remain intact. `DECISIONS-INDEX.md` carries the new 29-word ruling. Role/team/verification guidance, SPEC §9.3 and README retain repair, ignored-receipt force-add and unchanged CI duties.
- **SC-10 inspection:** `.omp/extensions/harness-hooks.ts:451–563` replaces synchronous policy spawning with bounded async execution and five independent launches. `validate-digest.py:2371–2670` replaces reruns with receipts; the legacy runner seam and pooled-only parser are removed, standing callers migrate, copied bootstrap gates and PR CI are unchanged. Positive behavior assertions accompany removal checks. Build evidence explicitly distinguishes candidate source from installed enforcement.

## Stage 2 — code quality

- **T-01:** inventoried every runner invocation and promise-forwarding caller, including registry startup/revival, destination binding, authorization/rooting, expertise, post-write, dispatch attach/rollback, yield, spend and lifecycle release. Claim precedes reconciliation; readiness waits for claim/destination answers; cleanup awaits releases. `spawnPolicy` has one settlement guard, timer cleanup, process-group SIGKILL on deadline/exit and pipe destruction at deadline. Five-gate collection uses allSettled and declared order, preserving refusal precedence and every unavailable notice, including rejected siblings. Main and governed merge paths share narrow failure classification.
- **T-02:** followed exact QA/parent claims through trusted checkout, unique open validator run and registered review pin to the receipt path. Checked symlink/nonregular-file refusal, full integer-zero and exact-coverage validation, per-commit ancestry including merge parents/renames/reverts, and fix slug/mission/HEAD/clean-tree exceptions. Missing identities and expected evidence failures refuse; accepted receipt forgery and outer unexpected-hook unavailability remain explicit trust boundaries, not new findings. Migrated identity tests distinguish earlier refusals from merely missing receipts.
- **T-03:** grants add only manifest paths in authored/template layouts. Grant tests retain state/digest/log/role/checkout refusals. Feature grading stays explicit-mode-only, uses committed objects and the shared classifier, with a grade-2 mutant control and no exemptions. Its actual fixed base is **d04c765a**, as the approved grading-base note and pinned line 316 state; dd04e52a is historical plan context, not the shipped constant.

**Complexity/risk:** supplied measured records in `notes/t02-fixrun-red-green.md` give production `_receipt_context` grade 4 (CC 2 / cognitive 2 / ABC 16.9), `_kind_problems` grade 4 (8 / 6 / 15.5), `_fix_lineage` grade 4 (4 / 2 / 9.0), `_checked_receipts` grade 5 (4 / 3 / 7.8), and `check_qa_matrix_claim` grade 4 (4 / 2 / 9.4). T-01/T-03 notes record changed test functions at least grade 3. No below-bar new/worsened function identified by inspection. `code_grade: pass` is the expected mechanical classification **[INFERENCE]**, not a claim that I executed the exact-range grader. Execution was reserved to QA; canonical recomputation remains authoritative. Highest reviewed risks were async authority ordering and receipt identity/lineage, not style.

## Principles applied

- **Migrate Callers, Then Delete Legacy APIs:** checked all policy callers and deletion of the rerun implementation without compatibility shims.
- **Type System Discipline / Model the Domain:** checked Promise-returning runner propagation, readiness state and ordered outcome handling rather than demanding unrelated type redesign.

## Verification and open questions

No tests, suites, builds, linters, formatters, benchmark, mutants or grader were executed by this reviewer. Read existing red/green evidence; final pinned executions belong to QA. QA/lead should retain canonical `code-grade.py --base 0d7326e4 --head 6143625f` output with final verification; it was requested but not available to this reader. No product decision question or must-fix remains. Known baseline issues listed in the dispatch are not reported as regressions.
