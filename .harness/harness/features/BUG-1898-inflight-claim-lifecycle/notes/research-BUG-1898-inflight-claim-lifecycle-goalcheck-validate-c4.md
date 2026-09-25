# Goal-check — BUG-1898 validate-c4

**BLUF: FAIL.** At exact pin `f73c999482fd931021a3eb50d30aa8ab2a885283`, all eight BRIEF success criteria and all four perspectives have evidence, including SC-07's required operator-recorded PASS 29/29. The ship gate nevertheless fails: security review found a medium-severity, must-fix T-04 oracle gap that can let the live probe claim “no row … crossed personas” without checking the nested governed lead's registry persona.

## Scope and provenance

- Exact pin graded: `f73c999482fd931021a3eb50d30aa8ab2a885283`; no working-tree HEAD was substituted.
- Canonical range: `a4d72e7fc91d0cf7a568d9e2a5225465a422170e..f73c999482fd931021a3eb50d30aa8ab2a885283` (53 paths).
- Focused comparison: `6bfc21e3ccdf78eb86cdd0eb250067348d887096..f73c999482fd931021a3eb50d30aa8ab2a885283` (12 paths).
- Pinned blobs inspected: hook `df09436aaac9cfa0bd7f7fa840cd0c5c7c95ed64`, probe `1aae87d1a566ea5a212fea8b787a669734ea9eed`, and receipt `b7f5ae62377dbf522a3cf88ba32ef24a6783f8c6`. The hook is unchanged from wake-fix commit `815d5ccbfffb937136d275fea826f53018f8f192`; pin `f73c999…` couples the corrected probe and final receipt to that hook. The receipt itself records the feature-worktree cwd and confirms “the hook under test is this worktree's” (`notes/live-omp-probe.md:525-540`).
- I collected QA/reviewer evidence rather than re-testing. I did not rerun the credentialled live OMP probe.

## Perspective coverage

- **operator — PASS:** SC-01 proves preservation/refusal behavior, and SC-07 records the required real-session PASS, suite sentinel preservation, and empty final registry.
- **orchestrator — PASS:** SC-02, SC-04, and SC-06 cover exact-id pre-write ownership, real-id mixed batches, held children, exact settlement, and targeted recovery.
- **code maintainer — PASS:** SC-03 and SC-05 cover the canonical registry API, one-PM invariant, non-PM multi-flight, DEC-100 pass-through, and `pi.events` lifecycle delivery.
- **reader — PASS:** SC-08 exposes current decisions, exact cutover, red-first evidence, and the separate live receipt. The gate failure below is independent of perspective coverage: a substantive review finding can block shipment even when the BRIEF criteria have evidence.

## Success-criterion outcomes

| SC | Verdict | Method | Evidence |
|---|---|---|---|
| SC-01 | met | automated | QA c4 cites `tests/integration/test-suite-claim-preservation.py:107-121`; retained exact-mutant and red-first receipts are at `notes/review-harness-qa-c3.md:13-22` and `notes/review-harness-qa-c0.md:23`. |
| SC-02 | met | automated | `tests/unit/omp-hooks.test.ts:1875-2002`; the exact wake case drives only `agent_start` after settlement at `:1892-1911`, and `:1913-1923` blocks writes before reclaim. QA c4's exact-pin focused unit run passed 99/99. |
| SC-03 | met | automated | `tests/integration/test-inflight-registry.py:1238-1410`, with retained baseline-red receipt at `notes/review-harness-qa-c0.md:25`. |
| SC-04 | met | automated | `tests/unit/omp-hooks.test.ts:2020-2130`, with retained baseline-red receipt at `notes/review-harness-qa-c0.md:26`. |
| SC-05 | met | automated | `tests/integration/test-check-omp-port.py:194-214`, with wrong-bus red at `notes/review-harness-qa-c0.md:27`. |
| SC-06 | met | automated | `tests/integration/test-validate-digest.py:5815-5844`, with retained baseline-red receipt at `notes/review-harness-qa-c0.md:28`. |
| SC-07 | met | uat receipt | **Receipt only:** final `notes/live-omp-probe.md:522-561` records PASS 29/29; `:543-561` covers lifecycle settlement, exact-id wake/write/sample, mixed real ids, sentinel preservation, all observed children, and empty final registry; `:563-714` records the real ids and empty before/after arrays. The probe was not rerun. The active oracle finding below still blocks the security gate and requires a replacement receipt. |
| SC-08 | met | inspection | Exact-pin `DECISIONS.md:1373-1377,6361-6440`, `DECISIONS-INDEX.md:204`, and `notes/ship-checklist.md:5-11,38-116` preserve DEC-100 pass-through plus child self-refusal, rewrite DEC-204 to exact-id/current truth, enumerate exact one-row cutover, and keep the first post-merge cycle non-gating. |

SC-07 is graded from the immutable operator receipt as required. Its literal criterion asks for a recorded PASS with the listed runtime outcomes, which the receipt supplies. That does not waive an independently discovered security defect in how one stronger T-04 assertion is computed.

## Wake-path assessment

The supplied OMP premise is implemented coherently at the pin:

- `.omp/extensions/harness-hooks.ts:909-915` gives `before_agent_start` and wake handling one `openRun` gate opener. It publishes `unready`, performs the exact-id `startRun`, then publishes only `ready` or cause-bearing `held`.
- `agent_end` resets a governed run to `unready` before the empty-final-text return (`:1339-1345`). A turn ending without yield therefore must reopen on the next turn; because its row is still live, exact-id run-start reuses it.
- `agent_start` conditionally reopens only a governed non-ready run (`:978-985`). An ordinary first turn remains ready and is not double-claimed; a settled turn recreates its released exact-id claim; a held turn retries but stays held on refusal.
- Tool authorization blocks every non-yield tool until ready (`:1016-1019`), and the BLOCKED-only rule still gates yield. Main has no `currentAgent`, so wake handling is inert for Main.
- The unit case at `omp-hooks.test.ts:1892-1911` models the actual `#wakeForIrc` turn shape—`agent_start` without another `before_agent_start`—then observes exact `Lead.Dev` reclaim before a write. The adjacent test at `:1913-1923` proves a write remains blocked between end and reclaim.

No production wake-path defect was found.

## T-04 probe and receipt correspondence

The requested pin corrections are present:

- S3 dispatches nested `harness-eng-lead` with a lead-shaped digest (`tests/manual/probe-inflight-claim-lifecycle.py:77-99,393-411`).
- Plain-id collection excludes every `harness-*` persona (`:424-428`).
- S2 captures its sample index immediately before the wake prompt and evaluates only later samples (`:367-390`).
- The RPC driver waits for `get_state.isStreaming == false` and sends with `streamingBehavior: followUp` (`:285-302`).
- Nested lineage is recovered from lead-held claim samples as well as Main-visible direct children (`:413-422`).
- The final receipt records `Nest.Probe` as a started and completed `harness-eng-lead` (`notes/live-omp-probe.md:665-684`) and empty before/after registries (`:712-713`).

Those corrections do not close the active oracle gap: S3's expected governed set is still formed only from direct `harness-orchestrator` starts.

## Active finding

### F-SEC-C4-01 — nested governed lead omitted from persona and settlement oracle

- **kind:** substance
- **severity:** med
- **disposition:** must-fix
- **owner:** T-04
- **evidence:** `tests/manual/probe-inflight-claim-lifecycle.py:393-450`; security artifact `notes/review-harness-security-reviewer-c4.md:14-20`.
- **concrete failure scenario:** if sampled id `Nest.Probe` is bound in the claim registry to `harness-qa` instead of `harness-eng-lead`, the id still contains `.`, is excluded from plain ids, is not one of the two direct orchestrator ids, and supplies the required nested lineage. The two orchestrators can settle. All six S3 checks can therefore print PASS even though the nested governed claim crossed personas, allowing a reviewer to accept a false security assertion.
- **required correction:** derive every governed `(id, expected persona)` pair from lifecycle starts, including the nested lead; check every sampled governed row for exact persona agreement; settlement-check every governed id; then have the operator regenerate the credentialled live receipt.

## Dismissed and closed findings

- **Duplicate first-turn claim:** dismissed; `before_agent_start` leaves the gate ready and the needed-only `agent_start` guard returns.
- **No-yield turn loses ownership:** dismissed; `agent_end` resets only local readiness, and next-turn exact-id run-start reuses the still-live row.
- **Held retry authorizes a write or changes identity:** dismissed; `openRun` first publishes unready and failed exact-id retry publishes held, both blocked by the tool gate.
- **Main accidentally claims:** dismissed; no governed `currentAgent` is established for Main, so both gate handlers return.
- **S2 samples a pre-wake claim:** dismissed; the qualifying sample window begins immediately before the wake prompt.
- **S3 accepts the nested governed lead as a plain/non-governed id:** dismissed; all `harness-*` personas are excluded from plain ids and nested lineage comes from sampled claims. This does not dismiss F-SEC-C4-01, which concerns the missing expected-persona comparison.
- **F-01 (T-03 unreadable-registry fail-open):** remains closed by strict pre-release reads; no regression in the focused delta.
- **F-02 (T-03 complexity):** remains closed by the split settlement logic and the clean c4 code review/grade.
- **F-QA-01 (T-03/T-04 weak mutant oracle):** remains closed by exact two-label equality plus singleton and substitution negative controls. It is distinct from the nested-lead live-oracle gap.
- **Earlier failed live receipts:** retained as honest history and superseded by the final run for SC-07; they were not rewritten.
- **INV-43 seq-3 late succession in `notes/handoff-validate.md`:** residual ledger defect only, not a code finding, not a blocker, and not a request to rewrite history.

## Verification and cleanup

- QA c4: `bun test tests/unit/omp-hooks.test.ts` exited 0 with 99 pass / 0 fail; probe `--dry-run` exited 0 and started no OMP session; `tests/integration/test-run-unit-tests-kinds.py` exited 0 with 8/8. Evidence: `notes/review-harness-qa-c4.md:7-17`.
- Code review c4: PASS, no production/spec finding; evidence: `notes/review-harness-code-reviewer-c4.md:3-17`.
- Security review c4: FAIL with F-SEC-C4-01; evidence: `notes/review-harness-security-reviewer-c4.md:12-20`.
- Live OMP was not rerun. SC-07 uses only `notes/live-omp-probe.md:522-714`.
- Created immutable archive scratch `/tmp/BUG-1898-goalcheck-c4.iS7tYP`; removed it and verified the path absent. No scratch worktree was created. No source or test file was edited.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Exact pin f73c999 satisfies SC-01..SC-08, but T-04's nested-lead persona oracle has a medium must-fix security gap."
  feasibility: clear
  surface: L
  flags: [security, exact-pin, lifecycle, live-uat, ledger-residual]
  recommend: proceed
  tasks: 5
  decisions: 7
  needs_approval: false
  risk: med
  sc_status:
    - { id: SC-01, verdict: met, method: automated, evidence: "QA c4; tests/integration/test-suite-claim-preservation.py:107-121" }
    - { id: SC-02, verdict: met, method: automated, evidence: "QA c4; tests/unit/omp-hooks.test.ts:1875-2002" }
    - { id: SC-03, verdict: met, method: automated, evidence: "QA c4; tests/integration/test-inflight-registry.py:1238-1410" }
    - { id: SC-04, verdict: met, method: automated, evidence: "QA c4; tests/unit/omp-hooks.test.ts:2020-2130" }
    - { id: SC-05, verdict: met, method: automated, evidence: "QA c4; tests/integration/test-check-omp-port.py:194-214" }
    - { id: SC-06, verdict: met, method: automated, evidence: "QA c4; tests/integration/test-validate-digest.py:5815-5844" }
    - { id: SC-07, verdict: met, method: uat, evidence: "notes/live-omp-probe.md:522-714 — retained PASS 29/29 and empty before/after registry; no rerun" }
    - { id: SC-08, verdict: met, method: inspection, evidence: "DECISIONS.md:1373-1377,6361-6440; DECISIONS-INDEX.md:204; ship-checklist.md:5-11,38-116" }
  open_questions: []
  files_touched:
    - .harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/research-BUG-1898-inflight-claim-lifecycle-goalcheck-validate-c4.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle/.harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/research-BUG-1898-inflight-claim-lifecycle-goalcheck-validate-c4.md
```
