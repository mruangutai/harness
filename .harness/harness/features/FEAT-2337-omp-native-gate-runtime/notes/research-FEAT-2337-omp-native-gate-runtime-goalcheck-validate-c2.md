# FEAT-2337 goalcheck — validate c2

**All four perspectives, SC-01–SC-10 and DEC-100/DEC-255 are met; GC-02 is resolved. Validation remains provisionally ESCALATE, not PASS: current QA evidence was not yet available, and the ruled owner-manifest red must remain honest.** No new findings, approval request or UAT is introduced. This is a goalcheck, not a suite-green receipt or merge authorization.

## Subject, scope and evidence transfer

Review pin **9d9d940b2504a028699228bf275d395e641741f0** (P) agrees with live feature.json review_sha. Every current-content citation below means `git show P:<path>`, never the control-plane copy. The approved pinned BRIEF perspectives and plan decisions_affected were read. AGENTS.md Project map designates this product's `.harness/harness/docs/SPEC.md` and `DECISIONS.md`; conventional docs/spec.md, docs/decisions.md and docs/architecture.md are absent, and no architecture document is supplied.

Independently inspected the complete diff and each intervening commit from c1 **6143625f5262f246d51d642662899a44a8d545d9** to P. Outside this feature directory, the only changes are the six documentation/prompt surfaces in **34ef5cea3234974fa26c09f4ef35885fbbc4564c** listed below. The other three commits change only feature records. No implementation, tests, fixtures, runner, test configuration, CI, extension or benchmark code changed, including through an intervening change/revert. The fix.yaml changes are comments and QA prompt text, not execution wiring. Thus c1 behavioral, grading and benchmark evidence transfers to unchanged subjects; it is not re-execution at P. No benchmark rerun is warranted.

Evidence abbreviations, all under this feature directory: **Q1** = notes/review-harness-qa-c1.md; **R1** = notes/review-harness-code-reviewer-c1.md (unchanged cutover observations only; its unconditional PASS was superseded by notes/review-harness-code-reviewer-c1-assessment.md); **G1** = notes/research-FEAT-2337-omp-native-gate-runtime-goalcheck-validate-c1.md:68–113, final addendum; **C1** = runs/r-20261122-4-validate-validator/digest.md. C1 reconciles the original findings; this assessment independently checks their corrected landing.

## GC-02 — resolved by normative repair, behavior unchanged

Original finding: **kind substance; severity med; owner T-03; SC-09/D-02**. Scenario: normal live fix-run feature.json/notes dirt was allowed by the approved ruling and implementation, but unqualified clean-tree policy told readers otherwise. Each formerly affected surface now states the trusted feature-directory exception:

| Pinned surface | Evidence |
|---|---|
| .harness/harness/docs/DECISIONS.md | :8428–8436: trusted HEAD descendant; clean outside the feature directory; tracked/untracked-unignored distinction and live-record rationale |
| .harness/harness/docs/SPEC.md §9.3 | :1604–1607: fix HEAD descendant, clean outside the feature directory |
| .claude/skills/harness/teams/fix.yaml | :71–77,90–96: both comment and actual QA dispatch prompt state the exception |
| .omp/agents/harness-qa.md | :58–61: fixed tip, clean outside the feature directory, in its own fix run |
| .omp/agents/harness-validator-lead.md | :101–107: same exception; existing #2356 limitation retained |
| .claude/skills/harness-verification-rules/SKILL.md | :39–47: same exception and receipt/repair obligations |

This matches notes/answers-2026-11-22-fix-run-receipts.md:44–51. At P, unchanged `.claude/skills/harness/bin/validate-digest.py:2569–2589` enumerates tracked/untracked-unignored dirt and rejects only paths outside feature_rel + `/`, while requiring tested HEAD and ancestry. Unchanged `tests/integration/test-validate-digest.py:2368–2386` covers feature-local note acceptance, external tracked/untracked dirt refusal and validate-run rejection of code-changing descendants. Q1:18,34 records the passing 78-case receipt group and retained red-first evidence. Documentation was repaired to the approved behavior; the implementation was neither tightened nor newly authorized.

## Perspective coverage

| Perspective | Grade | Discharging SCs and shipped traces |
|---|---|---|
| operator | met | SC-01/02/03/07 → T-01/T-02/T-03; async/timeout/ordered refusal behavior and trusted lookup (Q1:29–31,35; R1:12,16–17) |
| orchestrator | met | SC-04/06 → T-01/T-02/T-03; paired benchmark and exact-coverage receipts (Q1:19–22,32,34) |
| code maintainer | met | SC-05/09 → T-02/T-03; shared validator, migrated callers and corrected current guidance (Q1:33; six pinned surfaces above) |
| reader | met | SC-08/10 → T-01/T-02/T-03; discriminating grading, clean cutover and explicit installed/candidate boundary (Q1:17,23,36; R1:12) |

## SC outcomes

| SC | Grade / method | Owning task(s); discriminating evidence |
|---|---|---|
| SC-01 | met / automated | T-01; Q1:14,18,29: omp-hooks.test.ts budget/heartbeat/delayed-helper cases and runtime run_heartbeat; t01-red-green.md captures natural RED |
| SC-02 | met / automated | T-01; Q1:15,18,30: test-omp-native-gate-runtime.py run_timeout_case/run_merge_gate_abnormal and test-merge-gate.py; focused 37/37; natural RED in t01-red-green.md and merge-gate-narrow-red-green.md |
| SC-03 | met / automated | T-01; Q1:14,18,31: all-five barrier, run_overlap/run_composition, ordered/rejected outcomes; natural RED in t01-red-green.md |
| SC-04 | met / automated | T-01; Q1:19–22,32: dedicated after-suites --benchmark at c1, 3 warmups/15 alternating pairs, all samples and host/Python/Bun identities; medians 177.5/53.7 ms, ratio 0.302; benchmark_verdict failing-ratio exit-1 wiring in t01-red-green.md, not a claimed pre-fix timing mutant |
| SC-05 | met / automated | T-02/T-03; Q1:14,18,33: test-integration-shard-validation.py unit_kind_cases and test-integration-shard-aggregation.py kind_seam_cases, git-tested-tree coverage and preserved four-shard defaults; t02-red-green.md natural RED |
| SC-06 | met / automated | T-02/T-03; Q1:15,18,34: run_feat2337_qa_receipt_cases 78/78 and run_feat2337_receipt_grant_cases 21/21, real-runner receipts/zero-rerun witness/fix/refusal cases; natural RED in t02-red-green.md, t02-fixrun-red-green.md and t03-red-green.md. Separate owner-manifest gate is not a failed receipt assertion |
| SC-07 | met / automated | T-02/T-03; Q1:15,35: run_bug919_qa_matrix_cases, run_bug2253_cases and migrated #1185/#1883 lookup/refusal cases; t02-red-green.md natural RED |
| SC-08 | met / automated | T-03; Q1:17,36: explicit --feat2337 mode at committed c1 tip grades 156 functions >=3 and grade-2 mutant reds. Authorized d04c765a population includes some upstream functions; not exclusively feature-owned. No new exemption or default cumulative policy |
| SC-09 | met / inspection | T-03; P: .harness/harness/docs/DECISIONS.md:1372–1421,8394–8465 and six-surface repair above; unchanged R1:11 guidance/README/CI inspection applies. P: DECISIONS-INDEX.md:109,238 retains correct heading anchors and 28-/29-word ruling tails; only the final decision entry grew, so later anchors do not shift |
| SC-10 | met / inspection | T-01/T-02/T-03; R1:12,16–18 cites unchanged harness-hooks.ts:451–563 and validate-digest.py:2371–2670: asynchronous cutover, old rerun/seam/parser removed, five independent copied-bootstrap gates and PR CI retained. Q1:23 separately identifies installed enforcement |

## Decision-disposition outcomes

| Decision / plan row identity | Grade / method | Pinned evidence and owner |
|---|---|---|
| DEC-100; decisions_affected[0], amend; nominated Only-a-refusal-blocks clause → D-01 | met / inspection | **9d9d940b2504a028699228bf275d395e641741f0:.harness/harness/docs/DECISIONS.md:1372–1421** replaces the clause in place with async/killed-30-second semantics, broad/narrow/helper handling and ordered five-process composition; T-03 owns landing |
| DEC-255; new D-02, not an amend/strike row | met / inspection | **9d9d940b2504a028699228bf275d395e641741f0:.harness/harness/docs/DECISIONS.md:8394–8465**, especially :8428–8436, states receipt identity/coverage/repair/force-add/CI trust and approved dirt exception; T-03 owns landing |

No strike rows exist. decisions_affected[1–21] are keep rows, not separate landing grades under canonical PM Mode 2: DEC-174/205/234/254/120/179/182/187/202/232/127/188/204/208/211/213/218/233/237/238/250. Their text is unchanged from c1; DEC-174/205/234 boundaries remain intact. There is no partial/not_met disposition to remediate; any decision-landing regression routes to DECISIONS.md-owning T-03, never an unowned re-plan.

## Current gate boundary and adequacy limits

A single availability check found **notes/review-harness-qa-c2.md not yet present**. No waiting, polling, test execution, source edits or independent green claim occurred. The SC grades above use established c1 evidence bound to unchanged subjects; **the current gate condition remains provisional for validator fan-in**, not inferred from a ruling or absent note.

The binding notes/answers-2026-11-22-manifest-gate.md:14–30 resolves **GC-03 (kind substance, severity high, T-03 grant/deployment boundary)**: scenario is the intended linked-worktree owner-manifest divergence detector, not a test defect. If c2's only red is test-check-plan-routes.py, its independent-clone run at P is green, and GC-02 verifies (established above), terminal consolidation is **ESCALATE, matrix_ok false**; escalation resolved with that ruling as decided_by. QA/validator must verify the first two conditions from current receipts and the paired clone, preserve the red, and require green clean-checkout PR CI before merge. Any other red or new substantive defect is genuine FAIL. No control-plane deployment or test weakening is authorized here.

GC-01 remains retracted; no mandatory base movement is resurrected. C1 records unit 64/64 and integration 90/91 files green, with red integration receipt committed honestly. Most historical failing-before receipts are builder captures, not independent historical reproductions; SC-04 wiring evidence is not a serial-execution mutation. Runtime TypeScript proof is not static typechecking (#2257). Known #2344/#2356/#2359/#2387 and canonical-reader baseline failures are not new findings. Q1:23 identifies the historical installed launcher/version/hash separately: installed/control-plane #919 rerun enforcement is not candidate receipt enforcement; no current installed identity is inferred from that historical measurement. Main must force-add c2 ignored receipts with the closed record; that future duty is not already failed. Open product questions: **none**.
