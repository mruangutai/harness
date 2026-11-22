# Handoff — FEAT-2225-member-expertise-writes, validate c5 → ship decision — written after r-20261121-12 closed, seq-12

## Next

Validate c5 over review_sha 7065b650ab3b94bae3175978bfd0cf0d62478c89 returned PASS: must_fix empty, matrix green, SC-01..06 met, severity_max low (runs/r-20261121-12-validate-c5-validator/digest.md). The panel is clean; the feature waits on the operator's ship decision (merge is user-gated). Nothing is pushed.

What happened since seq-8, under the operator's F2 ruling (notes/answers-2026-11-21-f2-ruling.md, Option 2, hardening #2251):

- r-9 amend-f2 (product, PASS, 0 cycles): pm amended BRIEF SC-03's close-run sentence and T-04 `intent` (via `plan-merge.py amend --reason`, ledgered `amendment` judgement `T-04.intent` at 2026-11-21T23:35:35Z; signatures and `signed_task_hashes` untouched; INV-40 holds, no re-signature); documentor added the boundary clause to SPEC §5.3 (:945-950, :973) and DEC-253 (:8202-8206, :8225). Commit a5d8687f.
- r-10 validate-c4 (FAIL, 0 cycles): F1/F3 closed, F2 dispositioned as the ruled boundary by every reader; one new must_fix C4-F1 — DECISIONS-INDEX.md stale because r-9 edited DEC-253 without regenerating (T-02 verify and `test-gen-decisions-index.py` red).
- r-11 fix-c4 (product, documentor): index regenerated at 8257a2e0; both gates 1→0. The lead returned FAIL on the dispatch's own diff-stat acceptance (dirty bookkeeping files, G-06), not on the work; the orchestrator verified T-02 verify rc0 and the integration file rc0 at the tip and closed the run as returned (cycles 0 per authentic digest; ledger rework_rounds 1).
- r-12 validate-c5 (PASS). C5-Q3 (an auxiliary runner red in test-validate-digest.py) was closed by measurement: `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-validate-digest.py` at the tip exits 0 (133/133 CLI, 6/6 guard). C5-Q1 is the ruled boundary itself (#2251), not a question.

Code tree at the pin is byte-identical to 219690d0 (`git diff --stat 219690d0 <pin> -- . ':!.harness'` empty).

## Trust

- c5 five readers ran, every return accepted; must_fix [] — runs/r-20261121-12-validate-c5-validator/digest.md — source
- SC-03 amended text on disk — BRIEF.md:21 — verified-at a5d8687f
- T-04.intent amendment ledgered, signature standing — feature.json judgements[] kind=amendment; check-state rc 0 at bd62ee2f — source
- test-validate-digest.py rc 0 at bd62ee2f (closes C5-Q3) — orchestrator measurement — verified-at bd62ee2f
- Spend at close: runs 12, wall_clock 196 min, tokens 696034, rework_minutes 74 of 90, rework_rounds 1 (ledger) — source

## Dead ends

- `feature-record.py close-run --cycles-used 1` on a lead digest carrying `cycles_used: 0` is refused; the authentic digest count wins, so a fix round's cycle shows in `regate`/`rework_rounds`, not `cycles_used` — source
- The validator lead cannot host harness-documentor (not in its `spawns:`); a T-02 fix is a product-lead run, re-verified by a following validate — source
- Control-plane `check-state.py` resolves its root to the main checkout and cannot see this worktree's feature; use `<worktree>/.claude/skills/harness/bin/check-state.py --feature FEAT-2225-member-expertise-writes` — source

## Working set

- .harness/harness/features/FEAT-2225-member-expertise-writes/feature.json (review_sha 7065b650; r-12 PASS)
- .harness/harness/features/FEAT-2225-member-expertise-writes/BRIEF.md (SC-03 amended) and plan.yaml (T-04 intent amended; status review)
- runs/r-20261121-12-validate-c5-validator/digest.md
- notes/review-harness-{qa,code-reviewer,security-reviewer,ui-reviewer}-c5.md, notes/research-FEAT-2225-member-expertise-writes-goalcheck-validate-c5.md
- notes/answers-2026-11-21-f2-ruling.md

## Done when

Scope: operator ship decision on the clean c5 panel; push the branch tip and open the PR (user-gated)
Authority: brief-perspective:.harness/harness/features/FEAT-2225-member-expertise-writes/BRIEF.md#orchestrator
Authority: plan-task:T-04.verify
Authority: plan-task:T-02.verify
