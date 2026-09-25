# Goal-check — BUG-1898 validate-c5

**BLUF: FAIL.** At exact pin `7893fe7a23e493dcd1554e439f28e3c9832b4de4`, all eight BRIEF success criteria and all four perspectives remain met, and c5 closes the concrete c4 nested-lead persona/parent omission. Shipment still fails: security review found a distinct medium-severity T-04 oracle bypass in which a deeper lineage such as `Nest.Probe.Deep` can satisfy the one-nested-id check without undergoing persona or parent validation.

## Scope and provenance

- Exact pin graded: `7893fe7a23e493dcd1554e439f28e3c9832b4de4`; no mutable HEAD was substituted.
- Canonical range: merge base `a4d72e7fc91d0cf7a568d9e2a5225465a422170e..7893fe7a23e493dcd1554e439f28e3c9832b4de4` (65 files, +6628/-554).
- Focused comparison: `f73c999482fd931021a3eb50d30aa8ab2a885283..7893fe7a23e493dcd1554e439f28e3c9832b4de4` (16 files, +931/-10). The only executable source/test delta is `tests/manual/probe-inflight-claim-lifecycle.py` (+22/-6); the other 15 paths are feature state and retained validation evidence.
- Pinned probe blob: `6a95d8541431df7e9094543351ce49d4d0fcdb3a`; pinned operator-receipt blob: `3bd76cf0e47421d9928d50caf1dbedb6a02dc6bc`.
- I collected the c5 QA and reviewer evidence rather than re-running settled product suites. I did not run credentialled/live mode.

## Perspective coverage

- **operator — PASS:** SC-01 proves unrelated-claim preservation and exact refusal/release, while SC-07's last operator-authorized receipt records the real-session PASS 29/29, suite-sentinel preservation, and empty registry before and after.
- **orchestrator — PASS:** SC-02, SC-04, and SC-06 retain exact-id pre-write claim/reclaim, id-keyed mixed-batch delivery, held-child refusal, exact settlement, and targeted recovery evidence; c5 changes only the manual S3 oracle.
- **code maintainer — PASS:** SC-03 and SC-05 retain the canonical feature-root/run-claim API, one-PM and legal non-PM concurrency behavior, DEC-100 pass-through, and `pi.events` lifecycle proof.
- **reader — PASS:** SC-08 retains pinned current-truth decisions, exact one-time cutover, red-first evidence, and the separate live receipt; the security finding below is an independent substantive gate, not missing perspective coverage.

## Success-criterion outcomes

| SC | Verdict | Method | Evidence |
|---|---|---|---|
| SC-01 | met | automated | QA c5 cites `tests/integration/test-suite-claim-preservation.py:107-121`; retained exact-mutant/red-first evidence is `notes/review-harness-qa-c0.md:23`. |
| SC-02 | met | automated | `tests/unit/omp-hooks.test.ts:1875-2002`; retained c4 exact-pin run passed **99/99** with 273 assertions, and the baseline-red run was 85 pass/13 fail including wake reclaim (`notes/review-harness-qa-c5.md:7-9,20-21`). |
| SC-03 | met | automated | `tests/integration/test-inflight-registry.py:1238-1410`, with retained baseline-red receipt at `notes/review-harness-qa-c0.md:25`. |
| SC-04 | met | automated | `tests/unit/omp-hooks.test.ts:2020-2130`, with retained baseline-red receipt at `notes/review-harness-qa-c0.md:26`. |
| SC-05 | met | automated | `tests/integration/test-check-omp-port.py:194-214`, with retained wrong-bus red-first evidence at `notes/review-harness-qa-c0.md:27`. |
| SC-06 | met | automated | `tests/integration/test-validate-digest.py:5815-5844`, with retained baseline-red receipt at `notes/review-harness-qa-c0.md:28`. |
| SC-07 | met | uat receipt | **Receipt only:** the last operator-authorized run is `notes/live-omp-probe.md:911-1103`, PASS 29/29. Checks S1-S5 are green at `:921-950`; `Nest.Probe` is the matching started/completed `harness-eng-lead` row under parent `Nest` at `:1055-1072`; registry snapshots are empty before and after at `:1100-1101`. No live rerun was performed by this goal-check. |
| SC-08 | met | inspection | Retained pinned inspection in `notes/research-BUG-1898-inflight-claim-lifecycle-goalcheck-validate-c4.md:31` cites `DECISIONS.md:1373-1377,6361-6440`, `DECISIONS-INDEX.md:204`, and `notes/ship-checklist.md:5-11,38-116` for DEC-100, rewritten DEC-204, exact cutover, and non-gating post-merge evidence. The c5 executable delta cannot alter those records. |

SC-07 is not inferred from dry-run, unit evidence, or my synthetic oracle. Its authority is only the retained operator receipt. The immediately preceding receipt is **FAIL 28/29** at `notes/live-omp-probe.md:717-909`: its S3 check at `:749` wrongly classified dotless top-level `Plain` as nested/crossed even though the observed rows show `Plain` as a top-level orchestrator and `Nest.Probe` as the lead (`:810-878`). The later PASS at `:911-1103` is the retained final receipt and has the same real S3 shape without that misclassification. It also supersedes, for c5, the older c4 PASS at `:522-714`.

## c4 finding disposition

**F-SEC-C4-01 is closed for its stated concrete scenario.** `nested_ids` now requires a governed id plus the dot delimiter, so dotless `Plain` is not nested (`tests/manual/probe-inflight-claim-lifecycle.py:430-436`); `crossed_rows` rejects a direct `Nest.Probe` row unless its persona is `harness-eng-lead` and its parent is `Nest` (`:439-449`); and the final no-row selector includes the nested id (`:452-466`). QA's pinned offline oracle accepted the valid direct row and rejected wrong persona and wrong parent (`notes/review-harness-qa-c5.md:12-16`). My independent pinned-archive oracle likewise passed: valid direct nested lead accepted; dotless `Plain` excluded; wrong nested persona, wrong nested parent, wrong direct persona, and a non-governed claim each rejected.

Closing the c4 scenario does not close the separate c5 finding below.

## Active finding

### F-SEC-C5-01 — deeper lineage bypasses nested persona/parent validation

- **kind:** substance
- **severity:** med
- **owner task:** T-04
- **reader:** security-reviewer
- **evidence:** `tests/manual/probe-inflight-claim-lifecycle.py:433-465`; source-independent adversarial result at `notes/review-harness-security-reviewer-c5.md:14-25`.
- **concrete failure scenario:** a runtime regression supplies the sole sampled descendant as `agent_id=Nest.Probe.Deep`, `agent=harness-qa`, `parent_agent_id=Nest.Probe` instead of the dispatched direct `Nest.Probe` lead. `nested_ids` accepts it because it starts with `Nest.`, so the exact-one check passes. `crossed_rows` derives immediate parent `Nest.Probe`, which is not in the top-level governed set, so it performs neither the nested persona/parent check nor the direct governed/plain checks. Settlement and empty-row checks can also pass. The probe can therefore issue a false PASS for the identity boundary.
- **required correction:** define direct nested membership once and use that same set for singleton, persona, parent, and no-row assertions; treat deeper prefixed descendants as crossed. Regenerate operator evidence only if the corrected executable oracle requires it.

The security reader's adversarial call observed `nested_ids=['Nest.Probe.Deep']` and `crossed_rows=[]`, directly demonstrating the bypass. Code review and QA pass the intended direct-row correction, but their green cases do not negate this deeper-lineage counterexample.

## Reader outcomes and residuals

- QA c5: PASS; retained matrix evidence, 99/99 SC-02 proof, pinned offline oracle, and final receipt accepted (`notes/review-harness-qa-c5.md`).
- Code review c5: PASS; no spec/quality defect for the intended direct-row correction (`notes/review-harness-code-reviewer-c5.md`).
- Security review c5: FAIL; F-SEC-C5-01 is medium and must-fix (`notes/review-harness-security-reviewer-c5.md`).
- UI review c5: PASS/scoped out; no rendered or accessibility surface (`notes/review-harness-ui-reviewer-c5.md`).
- `handoff-validate.md` sequence-3 late succession under INV-43 and the operator-owned dirty overlay remain instructed residuals, not findings and not must-fixes.

## Scoped evidence and cleanup

- `git merge-base origin/main 7893fe7a...` → `a4d72e7fc91d0cf7a568d9e2a5225465a422170e`.
- Canonical `git diff --shortstat` → 65 files, 6628 insertions, 554 deletions; focused `git diff --shortstat` → 16 files, 931 insertions, 10 deletions; focused probe stat → 22 insertions, 6 deletions.
- Independent archive: `git archive 7893fe7a... | tar -x -C /tmp/BUG-1898-goalcheck-c5.YQLmCo`; `python3 offline-oracle.py` exited 0 with the direct-row/dotless/wrong-persona/wrong-parent checks listed above.
- Scratch `/tmp/BUG-1898-goalcheck-c5.YQLmCo`, its oracle, and generated cache were removed; `rm -rf ... && test ! -e ...` exited 0. No scratch worktree was created.
- No source or tests were modified. No formatter, linter, project-wide build/suite, live probe, or operator-owned overlay command ran.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "All SCs remain met and c5 closes the c4 direct nested-lead gap, but a deeper-lineage oracle bypass leaves a medium T-04 security finding."
  feasibility: clear
  surface: L
  flags: [security, exact-pin, lifecycle, live-uat, ledger-residual]
  recommend: proceed
  tasks: 5
  decisions: 7
  needs_approval: false
  risk: med
  sc_status:
    - { id: SC-01, verdict: met, method: automated, evidence: "QA c5; tests/integration/test-suite-claim-preservation.py:107-121" }
    - { id: SC-02, verdict: met, method: automated, evidence: "QA c5 retained c4 99/99; tests/unit/omp-hooks.test.ts:1875-2002" }
    - { id: SC-03, verdict: met, method: automated, evidence: "tests/integration/test-inflight-registry.py:1238-1410" }
    - { id: SC-04, verdict: met, method: automated, evidence: "tests/unit/omp-hooks.test.ts:2020-2130" }
    - { id: SC-05, verdict: met, method: automated, evidence: "tests/integration/test-check-omp-port.py:194-214" }
    - { id: SC-06, verdict: met, method: automated, evidence: "tests/integration/test-validate-digest.py:5815-5844" }
    - { id: SC-07, verdict: met, method: uat, evidence: "receipt only: notes/live-omp-probe.md:911-1103, final PASS 29/29 with matching S3 row and empty before/after; no rerun" }
    - { id: SC-08, verdict: met, method: inspection, evidence: "retained pinned inspection: DECISIONS.md:1373-1377,6361-6440; DECISIONS-INDEX.md:204; ship-checklist.md:5-11,38-116" }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle/.harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/research-BUG-1898-inflight-claim-lifecycle-goalcheck-validate-c5.md
```
