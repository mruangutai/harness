# FEAT-68 goal-check — validate c4

## BLUF

**FAIL** at immutable review SHA `9d495ccdf9f8216a54a06356fe8c14227f190938` against baseline `e655f14a56a14bf1777cae55a19195c9af10505d` and implementation pin `9ab1813e86067ca4a21a84f49364cf4f453055b4`. The five code-maintainer targets satisfy the complexity and decomposition contract, all signed test/assertion commands pass, and c3's two receipt-provenance remedies reproduce successfully. The operator outcome nevertheless fails because `notes/build-divergences.md` replaces portions of D-02 through D-04's required exact old/new streams with literal ellipses. The full streams exist in the generated receipt, but the approved T-01 contract requires the divergence ledger itself to retain exact old and new bytes. The eventual c4 Markdown-only ship briefing remains possible, but this non-clean panel does not permit that sequenced final observation.

I inspected the complete `e655f14a56a14bf1777cae55a19195c9af10505d..9d495ccdf9f8216a54a06356fe8c14227f190938` diff and every required corpus item. QA alone ran the configured unit/integration matrix. File/line citations below refer to review-SHA content unless stated otherwise.

## Perspective coverage

- **operator — FAIL** — SC-02 and SC-04 are partial because the reproducible single-execution receipt retains full streams and hashes, but the required old/new divergence ledger truncates D-02–D-04. SC-05 remains partial: the renderer/residue assertions and both test kinds pass and the tree permits the eventual Markdown-only briefing, but no actual c4 briefing exists before clean fan-in.
- **code maintainer — PASS** — SC-01 and SC-03 are met. The five targets and selected new qualnames meet the grade rule; the settled phase/rule decompositions preserve order, comment association, accumulation, and default-deny behavior; the renderer, its named test, reader row, 102 HTML derivatives, and prescribed residue are removed; no production surface changes after the immutable implementation pin.

## Success-criterion outcomes

| SC | Verdict | Method | Evidence |
|---|---|---|---|
| SC-01 | met | automated | `notes/review-harness-qa-c4.md:10-22,37-41` records 41 unit and 70 integration files, zero failures, the signed grade assertion passing at the pin, and the detached-baseline fail-first assertion naming exactly the five grade-1 targets. The committed receipt records the green pin/red baseline result at `notes/clean-pin-byte-receipts.generated.md:124-140`. |
| SC-02 | partial | automated reproduction plus inspection | QA's isolated preserved reproduction completed all 57 baseline and 57 pin suites with exit 0, reported 53/57 normalized-identical, and differed from the committed generated receipt only by timestamp and ruled D-02–D-05 nondeterminism (`notes/review-harness-qa-c4.md:37-42`; `artifact://4582`; `artifact://4591`). Full differing streams are retained at `notes/clean-pin-byte-receipts.generated.md:82-121`, but D-02–D-04's ledger entries contain literal ellipses at `notes/build-divergences.md:25-41`, so the approved exact-old/new ledger obligation is not delivered. |
| SC-03 | met | inspection | The five drivers preserve original rule/phase order, accumulation, comment association, and fail-closed fall-through (`.claude/skills/harness/bin/check-plan-routes.py:394-527`; `harness_boundary.py:873-1022`; `board_lifecycle.py:812-930`; `layout_migration.py:229-290`; `check-domain.py:880-1054`). The implementation-pin range contains only those five production refactors plus the prescribed renderer/reference/test/HTML cleanup; the review tree deletes exactly 102 baseline HTML files. See `notes/review-harness-code-reviewer-c4.md:8-12`. |
| SC-04 | partial | inspection | Receipts are post-pin: `git log --reverse 9ab1813e86067ca4a21a84f49364cf4f453055b4..9d495ccdf9f8216a54a06356fe8c14227f190938` begins receipt history at `ae0b41d7`, and `git ls-tree` at the implementation pin contains none of the clean-pin receipt files. The handwritten receipt names both full SHAs, feature-worktree root, exact commands, normalization, exits, hashes, comparison, and generated artifact (`notes/clean-pin-byte-receipts.md:1-64`) without claiming residence inside the pin. Chronology and reproducibility are sound, but the D-02–D-04 exact-byte ledger defect above makes the evidence record incomplete. |
| SC-05 | partial | automated plus inspection | QA records both matrix kinds and the signed HTML-removal/prohibited-reference assertions passing (`notes/review-harness-qa-c4.md:10-22,39-43`). The review tree has no feature-note HTML survivor, no renderer, and no c4 ship briefing or `.html` sibling; thus a Markdown-only c4 briefing remains possible (`notes/review-harness-ui-reviewer-c4.md:5-16`). The actual validate-produced c4 briefing is deliberately sequenced after a clean panel and is absent here, so it cannot yet be marked met. |

## Fresh c3 remedy adjudication

1. **Single suite execution and shared dataflow — verified.** `notes/receipt-scripts/feat68-cleanpin.py:25-33` has one `subprocess.run` per suite; that call's `p.stdout` and `p.stderr` feed the row hashes and `outputs[s]`. Raw-difference lines consume only `outputs[s]` at `:59-63`. The separate grade-lock subprocesses are not suite executions.
2. **Runnable durable reproduction — verified.** `notes/clean-pin-byte-receipts.md:16-32` starts from the feature worktree root, sets `SCRIPTS=.harness/harness/features/FEAT-68-complex-function-third-wave/notes/receipt-scripts`, invokes the generator, and cites `notes/clean-pin-byte-receipts.generated.md`. QA's isolated execution exited 0 and preserved the handwritten instructions (`notes/review-harness-qa-c4.md:37-42`).
3. **Same-execution D-02–D-05 provenance — verified, but ledger exactness fails.** The committed generated receipt's full raw lines and the ledger's visible new tokens agree, so the c3 single-capture remedy is real. D-02–D-04 still abbreviate the old/new streams with `…`; provenance does not satisfy the separate requirement that the ledger retain exact bytes.
4. **Chronology — verified.** The implementation pin is an ancestor of the review SHA, all receipt commits follow it, and no receipt claims to be part of it. No production change follows the pin.
5. **Eventual c4 briefing — possible, not delivered.** Neither `ship-review-validate-c4-validator.md` nor an HTML sibling exists at the review SHA; the renderer is absent. The eventual orchestrator could write Markdown alone, but this goal-check does not create it.

The prior VF-04-C3/VF-05-C3 reproduction and split-capture defects are closed by items 1–3. The `feature.json.lock` half of prior VF-06-C3 is absent from the review SHA. Its bytecode half survives as the non-gating advisory below.

## Findings

### QA-C4-01 — divergence ledger abbreviates required exact bytes

- **kind:** form
- **severity:** med
- **task_binding / ownership:** T-01 / main-session-direct
- **affected SC:** SC-02, SC-04
- **scenario:** An auditor reading the required ledger cannot recover the actual baseline or pin stream for D-02, D-03, or D-04 because portions are replaced by literal ellipses. A changed byte outside each displayed fragment could therefore be omitted while the ledger still appears complete. The generated sibling happens to retain the full streams, but that does not deliver T-01's explicit exact-old/exact-new ledger contract.
- **evidence:** `BRIEF.md:18-25`; `plan.yaml` T-01 intent; `notes/build-divergences.md:25-41`; `notes/clean-pin-byte-receipts.generated.md:82-85,100-107,118-121`; `notes/review-harness-qa-c4.md:13-30,37-42`.
- **disposition:** gating; no fix, re-plan, or further panel is requested by this read-only final regate.

### CR-C4-01 — retained receipt-script bytecode

- **kind:** form
- **severity:** low
- **task_binding / ownership:** T-01 / main-session-direct
- **affected SC:** SC-04
- **scenario:** Three opaque CPython 3.14 cache files remain beside the authoritative receipt-script sources and could become stale if those sources changed, confusing a later evidence consumer. They do not affect current shipped code or the reproduced source/generated-receipt binding.
- **evidence:** review-SHA tree paths `notes/receipt-scripts/__pycache__/*.pyc`; `notes/review-harness-code-reviewer-c4.md:14-16`.
- **disposition:** advisory/non-gating; retained from VF-06-C3 rather than silently dropped.

No finding is unrated. The exact-byte ledger defect is the complete gating set for this PM lens.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Code-maintainer passes and c3's remedies reproduce, but operator fails because D-02–D-04's required exact-byte ledger is truncated."
  feasibility: risky
  surface: L
  flags: [evidence-integrity, reproducibility, sequencing, scope-hygiene]
  recommend: halt
  tasks: 1
  decisions: 0
  needs_approval: false
  risk: med
  sc_status:
    - { id: SC-01, verdict: met, method: automated, evidence: "notes/review-harness-qa-c4.md:10-22,37-41" }
    - { id: SC-02, verdict: partial, method: automated, evidence: "notes/review-harness-qa-c4.md:13-30,37-42; notes/build-divergences.md:25-41; notes/clean-pin-byte-receipts.generated.md:82-121" }
    - { id: SC-03, verdict: met, method: inspection, evidence: "notes/review-harness-code-reviewer-c4.md:8-12" }
    - { id: SC-04, verdict: partial, method: inspection, evidence: "notes/clean-pin-byte-receipts.md:1-64; notes/build-divergences.md:25-41" }
    - { id: SC-05, verdict: partial, method: automated, evidence: "notes/review-harness-qa-c4.md:10-22,39-43; notes/review-harness-ui-reviewer-c4.md:5-16" }
  findings:
    - { id: QA-C4-01, kind: form, severity: med, task_binding: T-01, affected_sc: [SC-02, SC-04], scenario: "D-02–D-04 replace portions of required exact old/new ledger bytes with literal ellipses.", evidence: "notes/build-divergences.md:25-41; notes/clean-pin-byte-receipts.generated.md:82-121" }
    - { id: CR-C4-01, kind: form, severity: low, task_binding: T-01, affected_sc: [SC-04], scenario: "Three committed receipt-script bytecode files can become stale beside authoritative source.", evidence: "notes/review-harness-code-reviewer-c4.md:14-16", disposition: advisory }
  open_questions: []
  files_touched: [.harness/harness/features/FEAT-68-complex-function-third-wave/notes/research-FEAT-68-complex-function-third-wave-goalcheck-validate-c4.md]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-68-complex-function-third-wave/.harness/harness/features/FEAT-68-complex-function-third-wave/notes/research-FEAT-68-complex-function-third-wave-goalcheck-validate-c4.md
```
