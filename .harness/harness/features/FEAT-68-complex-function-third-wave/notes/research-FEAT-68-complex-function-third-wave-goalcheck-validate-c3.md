# FEAT-68 goal-check — validate c3

## BLUF

**FAIL** at exact review SHA `b6b8c28d4a71bfe8ba25482eceee24d28a9e15d6`. The code-maintainer outcome is delivered, but the operator outcome is not. The authorized matrix and T-01 assertions pass; the implementation remains pinned at `9ab1813e86067ca4a21a84f49364cf4f453055b4`; and the renderer cutover is complete. Direct VF-04-C2 re-grading nevertheless shows that the repaired repository-root command still cannot resolve the scripts, while the runnable feature-worktree command erases its own reproduction instructions and obtains the table hashes and raw-difference/ledger bytes from different suite executions. SC-02 and SC-04 are therefore not met. SC-05 remains partial and its final actual ship-review Markdown/no-HTML-sibling observation is not permitted after this unclean panel.

Reviewed baseline `e655f14a56a14bf1777cae55a19195c9af10505d`, review SHA `b6b8c28d4a71bfe8ba25482eceee24d28a9e15d6`, and immutable implementation pin `9ab1813e86067ca4a21a84f49364cf4f453055b4`. File/line citations below refer to committed review-SHA content unless explicitly identified as QA's direct rerun result. I did not run the cross-module matrix or mutate evidence; QA alone ran those commands.

## Perspective coverage

- **operator — FAIL** — SC-02 is not met because the retained raw-difference bytes and ledger are produced by a second execution rather than the execution whose hashes/comparison table are reported. SC-04 is not met because the declared repository-root reproduction still exits before reaching the scripts, and the runnable alternative overwrites the durable reproduction record. SC-05 is partial pending the deliberately sequenced final observation.
- **code maintainer — PASS** — SC-01 and SC-03 are met. All five targets and selected new helpers satisfy the grade bar, the settled driver/rule decompositions preserve ordering and fail-closed behavior, the renderer and prescribed residue are removed, and no production surface changes after the immutable implementation pin.

## Success-criterion outcomes

| SC | Verdict | Method | Evidence |
|---|---|---|---|
| SC-01 | met | automated | `notes/review-harness-qa-c3.md:10-23` records unit discovery 41, integration discovery 70 with zero failures, and the literal T-01 assertions passing at the review SHA. `notes/red-first-receipts.md:19-31` records the detached baseline failing on exactly the five named grade-1 targets. `notes/review-harness-code-reviewer-c3.md:9` independently reports 34/34 changed/new functions at grade 4 or 5 and all targets present. |
| SC-02 | not_met | automated evidence plus inspection | The direct runnable reproduction still reports 53/57 normalized-identical (`notes/review-harness-qa-c3.md:16-23`), and the committed receipt/ledger agree on the c2 run's D-02..D-05 tokens (`notes/clean-pin-byte-receipts.md:103-147,167-175`; `notes/build-divergences.md:25-46`). But `notes/receipt-scripts/feat68-cleanpin.py:24-31` runs each pin suite and records its comparison and hashes, then `:55-62` runs every suite again to obtain raw differences. The nondeterministic D-02..D-05 bytes therefore cannot be the raw streams behind the table hashes. QA's direct rerun confirmed new raw bytes inconsistent with the committed ledger (`notes/review-harness-qa-c3.md:34-45`). The signed raw-bytes-and-hashes-preserved clause is not discharged. |
| SC-03 | met | inspection | `notes/review-harness-code-reviewer-c3.md:9-13,27-37` reports the complete implementation inspection: only the five named production scripts change plus renderer deletion; order, accumulation, comments, default-deny behavior, reference/test cleanup, and grade-exemption removal conform. A direct post-pin scope check found no `.claude`, `tests`, or `.omp/commands/harness.md` changes after `9ab1813e`; direct tree measurement found 102 baseline HTML notes, zero remaining at the review SHA, and zero missing Markdown sources. |
| SC-04 | not_met | inspection plus direct bounded reproduction | The repair correctly makes `feat68-cleanpin.py` load `feat68-grade-assert.py` from its own directory and accept `/tmp/feat68-baseline.json` or `FEAT68_BASELINE_JSON` (`notes/receipt-scripts/feat68-cleanpin.py:20-21,38-40`). However the receipt declares repository root `/Users/molchairuangutai/GitHub/harness` and `SCRIPTS=.harness/harness/features/FEAT-68-complex-function-third-wave/notes/receipt-scripts` (`notes/clean-pin-byte-receipts.md:22-32`); QA ran that literal root and step 3 exited 2 because that path is absent (`notes/review-harness-qa-c3.md:24-33`). From the feature worktree the command exits 0, but `feat68-cleanpin.py:42-76` overwrites the receipt without emitting `## Reproduction`, contradicting the committed claim that the file is exactly its output (`notes/clean-pin-byte-receipts.md:191-194`), and its two suite passes break byte-to-hash provenance. |
| SC-05 | partial | automated plus inspection | QA's unit/integration matrix and the T-01 HTML-removal/prohibited-reference assertions pass (`notes/review-harness-qa-c3.md:10-23`). Direct pinned inspection found no prohibited `render-brief`/`md_to_html` reference outside the allowed historical areas, 102 baseline HTML derivatives and zero review-SHA survivors, with every corresponding Markdown source retained. The final actual validate-produced ship-review Markdown/no-HTML-sibling observation is deliberately post-clean-panel and does not yet exist. This c3 panel is not clean, so it does not permit that observation now. |

## VF-04-C2 disposition

**NOT CLOSED.** The c2 edit repairs two implementation details: the grade assertion is loaded as a sibling, and baseline JSON accepts the default or environment override. The review-SHA receipt also shows 53/57 and its committed ledger mirrors that particular c2 run's D-02..D-05 tokens. Those facts do not repair the finding:

1. At the receipt's declared repository root, its new `SCRIPTS` path is still absent; QA's literal step-3 execution exits 2 before using the existing detached checkouts.
2. At the feature-worktree root, the script runs but replaces the receipt with output that contains no Reproduction section, so the resulting artifact cannot carry the command needed to reproduce itself.
3. The script's first suite pass supplies comparison verdicts and hashes, while a second pass supplies raw differences. D-02..D-05 are intentionally nondeterministic, so the ledger bytes cannot bind to the table hashes.

This preserves the disagreement: code and security marked VF-04-C2 closed from static path/sibling/receipt inspection (`notes/review-harness-code-reviewer-c3.md:9-13`; `notes/review-harness-security-reviewer-c3.md:14-25`), while QA's literal execution and the source's two-pass structure falsify that closure (`notes/review-harness-qa-c3.md:24-47`).

## Findings

### GC-C3-01 — declared repository root still cannot execute step 3

- **kind:** form
- **severity:** med
- **task_binding:** T-01
- **owner:** main-session-direct
- **new_class:** false
- **scope_change:** false
- **scenario:** An auditor starts at the exact root named by the receipt and sets its exact `SCRIPTS` value. `feat68-cleanpin.py` is absent there, so Python exits 2 before opening baseline JSON, resolving either detached checkout, or reproducing 53/57. The old wrong-relative-path failure therefore survives with a longer but still wrong relative path.
- **anchors:** `notes/clean-pin-byte-receipts.md:22-32`; `notes/review-harness-qa-c3.md:24-33`.
- **remedy:** Make the declared working directory and script home agree, then execute the exact preserved command from that directory. Do not alter the implementation pin or settled A-1..A-4 rulings.

### GC-C3-02 — the preserved command is self-erasing and splits hashes from raw bytes

- **kind:** substance
- **severity:** high
- **task_binding:** T-01
- **owner:** main-session-direct
- **new_class:** true
- **scope_change:** false
- **scenario:** From the feature worktree the command exits 0, but it overwrites the receipt without its Reproduction section. More importantly, a behavior-changing first-run diagnostic can be represented only by an unauditable hash while the second run's nondeterministic diagnostic is ledgered instead. The record can then report 53/57 without preserving and ruling the actual bytes whose hashes/comparison produced that total.
- **anchors:** `notes/receipt-scripts/feat68-cleanpin.py:24-31,42-76`; `notes/clean-pin-byte-receipts.md:191-194`; `notes/review-harness-qa-c3.md:34-45`.
- **remedy:** Produce one durable, rerunnable receipt that retains its exact invocation and derives comparison result, full raw streams, hashes, exact differences, and ledger bytes from the same per-suite execution.

### GC-C3-03 — incidental generated repository files

- **kind:** form
- **severity:** low
- **task_binding:** T-01
- **owner:** main-session-direct
- **new_class:** true
- **scope_change:** false
- **scenario:** The review SHA includes an unbound zero-byte `feature.json.lock` and CPython-3.14 bytecode under `notes/receipt-scripts/__pycache__/`; the bytecode was added by the c2 evidence-only repair despite A-4's bounded scope and can become stale beside the authoritative source.
- **anchors:** `notes/review-harness-code-reviewer-c3.md:15-25`; c2 repair diff `ab17ca17..b6b8c28d`.
- **remedy:** Remove both incidental generated files before merge.
- **disposition:** advisory/non-gating, preserving the code reviewer's stated disposition; it does not change the SC verdicts above.

## Complete must-fix set

1. **GC-C3-01 / VF-04-C3** — repair the still-unresolvable declared-root invocation and prove the literal command reaches the preserved scripts.
2. **GC-C3-02 / VF-05-C3** — make reproduction durable and single-capture so raw bytes, hashes, comparisons, and ledger entries share provenance.

GC-C3-03 is retained as an actionable low advisory rather than silently discarded. No finding is unrated. The authorized 3 rounds / 120 minutes are exhausted; another evidence repair requires escalation rather than an unapproved fourth loop.

## T-01 and final SC-05 sequencing

**T-01: FAIL.** SC-01 and SC-03 are met; SC-02 and SC-04 are not met; SC-05 is partial.

A genuinely clean future panel would permit the operator/orchestrator to perform SC-05's final actual ship-review Markdown/no-HTML-sibling observation. This c3 result is not clean, so that observation must not be created or claimed now.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Code-maintainer passes, but operator fails: VF-04-C2 remains open, byte/hash provenance is split across two executions, and SC-05 cannot advance."
  feasibility: risky
  surface: L
  flags: [evidence-integrity, reproducibility, scope-hygiene, sequencing]
  recommend: halt
  tasks: 1
  decisions: 0
  needs_approval: false
  risk: high
  sc_status:
    - { id: SC-01, verdict: met, method: automated, evidence: "notes/review-harness-qa-c3.md:10-23; notes/red-first-receipts.md:19-31" }
    - { id: SC-02, verdict: not_met, method: automated, evidence: "notes/receipt-scripts/feat68-cleanpin.py:24-31,55-62; notes/review-harness-qa-c3.md:34-45" }
    - { id: SC-03, verdict: met, method: inspection, evidence: "notes/review-harness-code-reviewer-c3.md:9-13,27-37" }
    - { id: SC-04, verdict: not_met, method: inspection, evidence: "notes/clean-pin-byte-receipts.md:22-32,191-194; notes/review-harness-qa-c3.md:24-47" }
    - { id: SC-05, verdict: partial, method: automated, evidence: "notes/review-harness-qa-c3.md:10-23; final observation blocked until a clean panel" }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-68-complex-function-third-wave/.harness/harness/features/FEAT-68-complex-function-third-wave/notes/research-FEAT-68-complex-function-third-wave-goalcheck-validate-c3.md
```
