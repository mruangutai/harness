# Handoff — FEAT-2225-member-expertise-writes, validate c2 → fix (main-session-direct segment) → validate c3 — written after r-20261121-7 closed, seq-7

## Next

Validate c2 over review_sha 238058677e6bbeafd5f05cefa9db2ffb76686418 (code tree ≡ 06ab8282) returned FAIL: F1 and F3 CLOSED by every reader; **F2 STILL OPEN, high substance, T-01 + T-04** (runs/r-20261121-7-validate-c2-validator/digest.md). T-04 is main-session-direct (DEC-174) and F2's caller half lives there, so — as at c1 — no squad `fix` run can own it. The main session executes ONE fix segment inside the worktree, then re-delegates the orchestrator for re-pin + `gh-sync.py status review` + ONE `validate` c3 dispatch. That c3 is rework round 2 of 2 under the ruling (notes/answers-2026-11-21-signoff.md); 25 of 90 rework minutes are spent. Station is `building` (gh-sync written at this seam); cycles_used 1 / 10.

F2, verified by the orchestrator at the pin (premise, not restated from the readers):

- `.claude/skills/harness/bin/expertise-merge.py` `_anchor_states` (:1558-1562 at the pin) accepts the feature's own `HEAD` blob state as a chain anchor, and `_refuse_unreceipted_content` passes when ANY chain state intersects an anchor.
- `.claude/skills/harness/bin/validate-digest.py` `_verify_receipt` (:2264-2272) passes no `--base`, so at live yield and durable close the only anchor is HEAD.
- Scenario (code + security, source-derived, not executed): a governed author with retained own-file Write deletes pre-existing G-01 without an op, commits it, then legitimately applies P-01 through `expertise_apply`. Chain `current → before_sha256 == HEAD` passes; the deletion reaches close unrefused. Replay/merge-distill catch it later; SC-03 ("cannot pass close-run or replay/merge integrity checks") and T-04's intent ("fail existing close verification AND replay/merge integrity gates") require refusal at close. The receipt's `## Known limits` row is the finding, not a waiver.

Fix segment (one, with its verify):

1. **F2 / T-01 half** — `expertise-merge.py` `verify-receipt`: anchor the write chain on an INDEPENDENTLY AUTHORIZED base state — the exact main blob the distill PR replays onto (the same `--base <main-sha>` replay already takes; merge-base of the feature branch with the default branch when no explicit base is passed) — never the feature's own HEAD. Preserve ordered/superseded batches, identical-add preservation, and the uncommitted-deletion refusal already landed. Regression in `tests/integration/test-expertise-merge.py`: unrelated edit COMMITTED between the baseline and the first receipted application must refuse exit 15 for member and lead; clean, supersession and post-replay controls stay as they are.
2. **F2 / T-04 half** — `validate-digest.py` `_verify_receipt`: supply the base to `verify-receipt` (resolve it once, from the registry/feature context or the default branch, never from a digest field a caller could author). Regression in `tests/integration/test-validate-digest.py`: the committed-tamper scenario refused at live yield and at durable close-run.
3. Verify: T-01 and T-04 `verify:` verbatim from plan.yaml, then `python3 tests/unit/test-expertise-ops.py && python3 tests/integration/test-expertise-merge.py && python3 tests/integration/test-validate-digest.py && bun test tests/unit/omp-hooks.test.ts`; red-first notes under `notes/red-first-fix-c2-*.md`; receipt `notes/receipt-main-session-fix-c2.md`.

After the segment: `code-grade.py --base 594af2a8 --head HEAD` rc 0; run-unit-tests unit + integration under `env -u HARNESS_AGENT_TYPE`; check-plan-routes, --canonical-reader-audit, check-instruction-paths, check-state rc 0.

Advisory, not gating (QA N2, settled `form` by orchestrator judgement): QA's isolated mutant removing the unchained-active-batch guard leaves the suites green (`coverage_gaps`); a discriminating assertion in the F2 regression would close it in the same segment. Raw T-01/QA logs remain volatile under /tmp.

## Trust

- Validate c2 r-20261121-7: five readers ran and every structured return was accepted (QA-RETURN resolved: stale OMP process predating the BUG-2171 fix at 594af2a8/#2230, session restarted) — runs/r-20261121-7-validate-c2-validator/digest.md — source
- Matrix green at the pin: unit 61 files/1132 PASS, integration 88 files/2909 PASS, configured runners exit 0 under `env -u HARNESS_AGENT_TYPE`; T-01/T-02/T-04 verifies exit 0 — notes/review-harness-qa-c2.md — source
- Code reviewer re-ran `code-grade.py --base 594af2a8 --head 23805867`: exit 0, 441 passing — notes/review-harness-code-reviewer-c2.md — source
- F2 premise (HEAD anchor; no `--base` from validate-digest) re-read by the orchestrator at the pin — verified-at 23805867
- Goal-check c2: SC-01 met, SC-02 partial, SC-03 not_met, SC-04/05/06 met; perspectives operator pass, orchestrator partial, maintainer fail — notes/research-FEAT-2225-member-expertise-writes-goalcheck-validate-c2.md — source
- `run-start --regate` was REFUSED for r-7 ("owes no regate") because r-6 closed BLOCKED (refused return), not FAIL; the ledger therefore records rework_rounds 0 while the operator's framing counts c2 as round 1. The run-start after r-7 (a FAIL) WILL owe a `--regate` — supply it — source

## Dead ends

- Spelling a feature-artifact path relative, or through `$VAR`, in a bash commit line is refused by bash-write-guard; absolute paths pass — source
- `gh-sync.py status` rewrites plan.yaml's `status:`; INV-33 is a byte comparison of plan.yaml at the pin, so every station write needs a re-pin to the commit carrying it (sequence: pin → status → commit → re-pin → commit) — source

## Working set

- .harness/harness/features/FEAT-2225-member-expertise-writes/feature.json (review_sha re-pinned to the station commit; stale once the fix lands — re-pin)
- .harness/harness/features/FEAT-2225-member-expertise-writes/plan.yaml (status building)
- .harness/harness/features/FEAT-2225-member-expertise-writes/runs/r-20261121-7-validate-c2-validator/digest.md
- notes/review-harness-code-reviewer-c2.md, notes/review-harness-security-reviewer-c2.md, notes/review-harness-qa-c2.md
- notes/receipt-main-session-fix-c1.md (`## Known limits`, first row, is F2)

## Done when

Scope: F2 landed in the worktree with its regressions red-first, every verify above rc 0, then validate c3 PASS over a fresh pin
Authority: plan-task:T-01.verify
Authority: plan-task:T-04.verify
Authority: brief-perspective:.harness/harness/features/FEAT-2225-member-expertise-writes/BRIEF.md#orchestrator
