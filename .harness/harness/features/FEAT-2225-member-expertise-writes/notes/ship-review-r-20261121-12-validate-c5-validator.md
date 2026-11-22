# Ship briefing — FEAT-2225-member-expertise-writes

**Shipped.** PR #2252 merged to main as squash c62ab0a1 after CI went green, operator pre-authorized. The validate c5 panel over review_sha 7065b650 was clean: must_fix empty, test matrix green, SC-01..06 met, severity_max low. The one finding the panels could not close — F2, a feature-local shell moving default-branch refs to hide unreceipted Expertise content from close-time verification — was ruled a documented boundary by the operator (notes/answers-2026-11-21-f2-ruling.md); SC-03, T-04's intent, SPEC §5.3 and DEC-253 now say so, and the hardening is already filed as #2251.

No report round was spawned (DEC-69). Assembled from disk: runs/r-20261121-{1-plan-product, 2-plan-c2-product, 3-t01-eng, 4-t02-product, 5-simplify-eng, 6-validate-validator, 7-validate-c2-validator, 8-validate-c3-validator, 9-amend-f2-product, 10-validate-c4-validator, 11-fix-c4-product, 12-validate-c5-validator}/digest.md, notes/research-FEAT-2225-member-expertise-writes-goalcheck-validate-c5.md, notes/receipt-main-session-fix-c{1,2}.md, observations/harness-orchestrator.md, feature.json.

## Definition of done — graded (validate c5 goal-check)

| Perspective (as signed) | Verdict | Discharged by | Evidence |
|---|---|---|---|
| **operator** — I can finish distillation without acting as another persona's scribe or accepting a false execution-only BLOCKED. Concurrent distills preserve accepted learning or return a real conflict to its author rather than silently losing it. | met | SC-01, SC-04 | goalcheck-validate-c5.md:15,18,26 — tests/unit/omp-hooks.test.ts:3376-3520 (five capability-class representatives), tests/integration/test-member-expertise.py:67-86 (all 16 personas), test-expertise-merge.py replay collision / supersession cases |
| **orchestrator** — I can rely on each member having applied the ops it reports and its lead having checked the result. I confirm completion without acquiring another persona's pen. | met | SC-02, SC-05 | goalcheck-validate-c5.md:16,19,27 — test-validate-digest.py committed-tamper cases, red-first-t04-merge-gate.md (23 reds), merge-gate.py:412-478 live-remote replay containment |
| **code maintainer** — I can change one existing merge mechanism and understand one current application contract, including who writes, where changes land, and how concurrent changes reconcile. Existing capability limits and grants remain intact. | met | SC-03, SC-06 | goalcheck-validate-c5.md:17,20,28 — expertise-merge.py:1564-1595, validate-digest.py:2017-2029, SPEC §5.3 :942-949/:970-974, DEC-253 :8199-8206, DECISIONS-INDEX.md:236 regenerated; SC-03 met against its amended text (F2 ruled, not fixed) |

## Lead summaries, by digest

- **Plan** (runs/r-20261121-1-plan-product, FAIL at 0 cycles; r-20261121-2-plan-c2-product, PASS): four-task plan drafted; the scope reader's high substance finding (T-04 merge-distill omitted the existing mirror-receipt enforcement) was applied inside run 1 and re-paneled in run 2; three proportionality findings trimmed at apply. Signed 2026-11-21.
- **Build** (r-20261121-3-t01-eng PASS at ba3fab79; r-20261121-4-t02-product PASS at 7c2f2d48; T-03/T-04 main-session-direct at fd8ffcdf per DEC-174): core receipts/replay, docs reconciliation, host tool + guards + merge gate landed.
- **SIMPLIFY** (r-20261121-5-simplify-eng, BLOCKED on form): T-01 code-grade debt lifted at f06b2e57, all gates rc 0; three angle readers' structured returns were refused by the host yield gate, their prose receipts retained. The altitude reader's flag A-F1 became validate c1's F1.
- **Validate c1** (r-20261121-6, BLOCKED on QA's return form, findings intact): F1 marker-only distill authority, F2 unreceipted-deletion blind spot, F3 host-to-core proof gap — fixed main-direct at 06ab8282.
- **Validate c2** (r-20261121-7, FAIL): F1/F3 closed; F2 reopened as "HEAD self-authorizes provenance" — fixed main-direct at 219690d0 (anchor on merge-base with the default branch).
- **Validate c3** (r-20261121-8, FAIL): F1/F3 closed; F2 still open — security executed the counterexample (move local `origin/main` / `main` ref; `verify_receipt` flips to verified). Rework ruling (2 rounds / 90 min) exhausted by the operator's count; returned to the operator.
- **Amend** (r-20261121-9-amend-f2-product, PASS): under the ruling, pm amended SC-03 and T-04.intent (ledgered amendment, signature standing), documentor added the boundary clause to SPEC §5.3 and DEC-253. Commit a5d8687f.
- **Validate c4** (r-20261121-10, FAIL): F2 dispositioned as the ruled boundary by every reader, F1/F3 closed; one new must_fix C4-F1 — DECISIONS-INDEX.md left stale by the DEC-253 edit.
- **Fix c4** (r-20261121-11-fix-c4-product, FAIL on the dispatch's own clean-tree acceptance; work verified): index regenerated at 8257a2e0, T-02 verify and test-gen-decisions-index.py 1→0.
- **Validate c5** (r-20261121-12, PASS): C4-F1 resolved, matrix green (unit 61 files / 1136, integration 88 files / 2922), SC-01..06 met; C4-W1 low form advisory retained.

**Open questions:** none blocking. c5's C5-Q3 (an auxiliary runner red in test-validate-digest.py) was closed by measurement at bd62ee2f: 133/133 CLI, 6/6 guard, rc 0. **Resolved escalations:** F2 → operator ruling Option 2 (notes/answers-2026-11-21-f2-ruling.md). **UAT:** not required by the BRIEF.

## Spend and ledger

`feature-record.py spend`: runs 12, wall_clock 196 min, tokens 696,034, rework_minutes 74 of the ruling's 90, rework_rounds 1 (ledger; the operator's count of fix rounds is 3: c1→c2 and c2→c3 main-direct, c4→c5 product). cycles_used 1 / 10 — fix rounds whose lead digests carried `cycles_used: 0` are recorded as `regate` judgements, not cycles. Judgements: 21 (1 mission, 5 regate, 5 succession, 8 continue, 1 finding_kind, 1 amendment). len(runs) 12 of max_total_runs 20 — within budget.

## Amendments (DEC-229)

| at | decision | reason | overruled |
|---|---|---|---|
| 2026-11-21T23:35:35.790499+00:00 | T-04.intent | operator ruling 2026-11-21 (answers-2026-11-21-f2-ruling.md): F2 accepted as a documented boundary; close verification relative to local default branch; hardening #2251 | no |

overrule rate: 0/1. This amendment was operator-directed, not builder-initiated; it is listed because the ledger records it as a departure from the signed T-04 text.

## F2 — the ruled boundary (already filed)

Close-time `verify_receipt` anchors on the default branch as the local repository records it; a governed shell that runs `git update-ref refs/remotes/origin/main`, `git branch -f main` or `git symbolic-ref` can self-authorize a committed unreceipted Expertise change at close. It is contained at `merge-gate.py merge-distill`, which fetches the live remote and refuses a committed blob that differs from the replay. **Hardening is #2251 (already filed by the main session): anchor close verification on an unmovable authority, and have `bash-write-guard.py` refuse default-branch ref moves for governed agents.** Not a backlog row below.

## Proposed backlog

Every residual non-gating finding from c1–c5, the SIMPLIFY advisories and the orchestrator observations. Strike rows by ID; unstruck rows become issues on ship acceptance.

| ID | Nature | Finding | Source |
|---|---|---|---|
| B-1 | chore | C4-W1: SPEC §5.3 :945 and DEC-253 :8201 qualify *durable close* with the local-default-branch boundary but not *live yield*, which uses the same verifier; add the same clause to the live-yield sentence. | c4/c5 code + security notes |
| B-2 | enhancement | N3: an explicit `--base` equal to the feature HEAD self-anchors receipt verification; no caller does this today. Refuse a non-ancestor or HEAD-equal `--base`, with a regression. Candidate to fold into #2251. | review-harness-qa-c3.md, c4/c5 digests |
| B-3 | chore | Fail-first evidence durability: T-01/QA raw red logs live under /tmp and are volatile; the configuration red is receipt-only. Persist raw gate output under the run dir or notes/. | c2 QA-N2, c3–c5 coverage_gaps |
| B-4 | chore | TypeScript typecheck is configured null; no static typecheck ran on .omp/extensions/harness-hooks.ts in any cycle. | plan c1 and every validate coverage_gaps |
| B-5 | chore | SIMPLIFY R-F2/S-F3/A-F3: centralize the distill-token rule and the lead tuple in one shared module instead of restating them in dispatch-guard, the host hook and validate-digest. | receipt-harness-*-r-20261121-5-simplify-eng-{reuse,simplification,altitude}.md |
| B-6 | chore | SIMPLIFY S-F1/A-F2: drop the host's Expertise destination mirror in favour of the core receipt destination once the schema guarantees direct-execute argument validation. | simplification / altitude receipts |
| B-7 | chore | SIMPLIFY S-F2/E-F1/A-F4: unify receipt reads and matching at one core seam (validate-digest currently reads receipts in-process beside the core). | simplification / efficiency / altitude receipts |
| B-8 | chore | SIMPLIFY S-F5: flatten one-caller dispatch helpers in dispatch-guard while keeping lazy destination loading. | simplification receipt |
| B-9 | chore | SIMPLIFY S-F7: reuse `_split_words` in bash-write-guard's HEAD-move loop. | simplification receipt |
| B-10 | chore | SIMPLIFY R-F4: shared git fixture cleanup (`git_support`) across the expertise-merge / merge-gate / member-expertise suites. | reuse receipt |
| B-11 | enhancement | SIMPLIFY S-F9: structured cap-refusal metadata on the shared merge exception, for the next core-interface change. | simplification receipt |
| B-12 | enhancement | SIMPLIFY A-F5: one shared shell-command parser for the guards (interpreter-prefixed, nested-shell, symlink spellings) instead of per-guard tokenizing. | altitude receipt |
| B-13 | bug | Host yield gate refuses read-only members' structured returns (angle readers in SIMPLIFY, QA in validate c1) even wrapped as `{data:{...}}`, while builders' and leads' pass; three SIMPLIFY readers and c1 QA closed BLOCKED on form with substance intact. Partly addressed by BUG-2171 (#2230) for leads; member path unverified. | observations/harness-orchestrator.md; r-5, r-6 digests |
| B-14 | bug | The task host injects `outputSchema`/`schemaMode` into every lead dispatch regardless of the call, contradicting the dispatch rule that harness dispatches carry neither; harmless here (dispatch-guard accepted all starts) but the rule and the host disagree. | observations/harness-orchestrator.md |
| B-15 | enhancement | A docs edit to DECISIONS.md does not regenerate DECISIONS-INDEX.md; the stale index only surfaces at the next full matrix (cost here: one fix + one validate round). Regenerate in the documentor's receipt step or gate it in check-domain's changed-state feedback. | r-10/r-11 digests, observations |
| B-16 | enhancement | harness-validator-lead cannot host harness-documentor, so a T-02 (docs) must_fix cannot use the `fix` team and needs a product-lead run plus a fresh validate. Add the documentor to the fix team's allowed devs or document the two-run route in build-phase.md. | observations/harness-orchestrator.md |
| B-17 | chore | `close-run --cycles-used 1` is refused when the lead digest says 0, so main-session-direct fix rounds never land in `cycles_used` (recorded only as `regate`); `spend.rework_rounds` and the operator's round count diverge. Decide which is authoritative and make the ledger say it. | observations (P-11 refusal), feature.json |
| B-18 | chore | The control-plane `check-state.py` resolves its root to the main checkout and cannot see a worktree's feature (`--feature` → "names no feature directory"); only the worktree's own copy audits it. Document, or make `--checkout` select the corpus. | observations/harness-orchestrator.md |
| B-19 | chore | `run-start --regate` is refused after a run closed BLOCKED, so a BLOCKED-with-findings panel (c1) never counts as a rework round; the ruling's round count under-counts by one. | observations/harness-orchestrator.md |
| B-20 | chore | A run id that differs from its run-dir slug trips INV-8 "dir is absent" for the whole run; the plan dispatch should name the run dir exactly after the run id. | observations/harness-orchestrator.md |

## Branch

Merged: PR #2252 → main c62ab0a1. Feature branch tip at briefing time: 839872e2 (run digests tracked for the repository-state gate). Nothing further to push from this orchestrator.
