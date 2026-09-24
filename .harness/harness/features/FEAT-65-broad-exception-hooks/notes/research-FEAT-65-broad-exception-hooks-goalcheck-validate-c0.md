# FEAT-65 goal-check — validate cycle 0

## Overall verdict

**FAIL.** The current unit and integration matrices are green, but seven automated criteria explicitly require fail-first evidence and no SC-bound pre-fix failing execution was retained. Independently, an executable `except Exception` survives inside `branch-create-gate.py`'s embedded configuration reader and is invisible to the shipped AST census. All three declared perspectives therefore fail.

## Pin and evidence basis

- Graded immutable range: baseline `4e8c73c07e5f1f102c392fe3800616fc94a1c53d` through review SHA `75a36628079ab1b37f7bd53f3100bde7305a8133`.
- All five shared artifacts were read at the review SHA: `notes/clean-pin-byte-receipts.md`, `notes/byte-evidence-vs-baseline.md`, `notes/build-divergences.md`, `notes/research-FEAT-65-hook-site-classification.md`, and `runs/build-main-direct/digest.md`.
- The clean-checkout receipt is implementation-pin evidence, not evidence that existed at that pin: it records execution at `79b7c2682a4ca174aa19f48259d10d3b60bb43e5`, expressly says it was committed later (`notes/clean-pin-byte-receipts.md:3-7`), and the pinned `79b7c268..75a36628` name-status range adds that receipt, the byte-evidence note, and the build digest without changing implementation or tests. The receipt and digest do exist in the review SHA's tree.
- QA separately executed the configured unit and integration runners in a checkout of the review SHA; both passed (`notes/review-harness-qa-c0.md:11-27`). Those green review-SHA runs do not supply the missing pre-fix failures (`notes/review-harness-qa-c0.md:29-42`).

## Success-criterion dispositions

| Criterion | Grade | Evidence and reason |
|---|---|---|
| SC-01 | **partial** | The clean implementation-pin receipts show every T-01–T-04 owning suite exiting 0 (`notes/clean-pin-byte-receipts.md:9-31`), the baseline comparison records suite exits and normalized streams (`notes/byte-evidence-vs-baseline.md:12-275`), and D-01–D-14 ledger the intended visible changes (`notes/build-divergences.md:14-163`). The required SC-bound pre-change failing receipt is absent; the build digest's generic red claim names no failing command, test, assertion, or output (`notes/review-harness-qa-c0.md:31-33,42`). |
| SC-02 | **partial** | Current integration cases cover the canonical open diagnostic, merge-gate's closed form, preserved exit verdicts, and process-control escape (`tests/integration/test-check-domain.py:50-88`, `tests/integration/test-merge-gate.py:294-307`), and both integration matrices are green. The criterion also requires red-first hook cases, but no retained pre-fix failure is bound to these cases (`notes/review-harness-qa-c0.md:34,42`). |
| SC-03 | **fail** | Besides the missing fail-first receipt (`notes/review-harness-qa-c0.md:35,42`), the shipped treatment is false for a scoped hook: executable Python in `branch-create-gate.py:81-88` retains `except Exception`, so an unrelated defect in the isolated configuration reader is silently converted to `false -` instead of escaping loudly. This contradicts the typed configuration-boundary classification (`notes/research-FEAT-65-hook-site-classification.md:80`) and is recorded as CR-01 (`notes/review-harness-code-reviewer-c0.md:9-19`). |
| SC-04 | **fail** | The unit census and increase/reduction mutants are green and the receipt reports eleven hooks at 0 with `harness_boundary.py: 2` (`notes/clean-pin-byte-receipts.md:30-31,33-54`; `tests/unit/test-broad-catch-census.py:106-121`). However, the census parses only the carrier module and misses the executable broad catch stored in `_CONFIG_READER` at `branch-create-gate.py:81-88`, so the complete zero-catch result is unsound (CR-01, `notes/review-harness-code-reviewer-c0.md:9-17`). The required pre-fix red run is also absent (`notes/review-harness-qa-c0.md:36,42`). |
| SC-05 | **partial** | The clean-pin receipt records identical hashes for all five prologues and the required tuple (`notes/clean-pin-byte-receipts.md:56-66`); the current unit lock mutates each copy independently (`tests/unit/test-broad-catch-census.py:140-156`) and is green at the review SHA. No retained pre-fix failing lock execution proves the required red-first state (`notes/review-harness-qa-c0.md:37,42`). |
| SC-06 | **fail** | The classification accounts numerically for 24 + 18 + 35 = 77 baseline sites (`notes/research-FEAT-65-hook-site-classification.md:3-21,27-89`), but the shipped branch-create configuration treatment does not match its typed-boundary classification: the embedded executable reader still broadly absorbs unrelated defects at `branch-create-gate.py:81-88`. Therefore the inspection's treatment-match and no-surviving-idiom claims are false (CR-01, `notes/review-harness-code-reviewer-c0.md:9-19`). |
| SC-07 | **pass** | At the review SHA, `notes/build-divergences.md:14-163` supplies D-01–D-14 with old bytes, new bytes or explicit no-byte-change treatment, ruling, and owning re-pinned case. The pinned code review found no independent mismatch for this criterion (`notes/review-harness-code-reviewer-c0.md:19`), while `notes/byte-evidence-vs-baseline.md:12-275` supplies the baseline suite comparison. |
| SC-08 | **pass** | `notes/clean-pin-byte-receipts.md:3-7` names the full implementation pin, clean detached checkout, and later-commit caveat; lines 9-31 record commands' suite/exit/stdout/stderr evidence, lines 33-54 record the 0/2 census, and lines 56-66 record five-way identity. The review SHA contains the tracked receipt, while the pinned post-implementation diff shows it was added after `79b7c268`, exactly as required. |
| SC-09 | **partial** | The current unit case injects an unexpected `RuntimeError` into the authoritative direct command and requires loud stderr plus nonzero exit (`tests/unit/test-feature-record.py:939-953`); the unit matrix is green. The required retained pre-fix failing execution is absent (`notes/review-harness-qa-c0.md:38,42`). |
| SC-10 | **partial** | The current integration case injects an unexpected direct `feature-root` failure and requires loud stderr plus nonzero exit (`tests/integration/test-inflight-registry.py:1262-1280`); the integration matrix is green. The required retained pre-fix failing execution is absent (`notes/review-harness-qa-c0.md:39,42`). |

## Perspective grades

- **operator — fail.** All four operator criteria are only partial: current behavior is covered and green, but each signed criterion requires a retained fail-first proof that is absent. The operator cannot rely on the complete approved evidence contract.
- **code maintainer — fail.** The typed-boundary and zero-catch outcomes are false because `branch-create-gate.py:84` still broadly catches in executable embedded Python; the prologue-lock outcome also lacks its required fail-first receipt.
- **reader — fail.** The divergence ledger and later-committed clean-pin receipt pass, but the claimed one-to-one shipped treatment does not: the classification/census misses the surviving executable embedded broad catch.

## Gate findings

### QA-65-01 — fail-first gate is unearned

- **SC:** SC-01, SC-02, SC-03, SC-04, SC-05, SC-09, SC-10
- **Location:** `runs/build-main-direct/digest.md:48-51`; missing from the five shared evidence artifacts
- **Concrete failure scenario:** a newly added assertion can be green at the review pin without ever having failed against the targeted pre-change behavior, so the evidence cannot distinguish a regression-catching assertion from an always-green one.
- **Satisfying remedy:** retain a pre-fix failing execution for each automated criterion, naming the exact covering test, command, assertion, and output, alongside the corresponding post-fix green result.
- **Kind / severity / ownership:** substance / high / T-01, T-02, T-03, T-04

### CR-01 — executable broad catch survives outside the census

- **SC:** SC-03, SC-04, SC-06
- **Location:** `.claude/skills/harness/bin/branch-create-gate.py:84` at the review SHA
- **Concrete failure scenario:** when the isolated configuration reader encounters an unrelated programming defect, `except Exception` converts it to an empty configuration and prints `false -`; the hook defect is silently absorbed while the carrier-module AST census still reports zero.
- **Satisfying remedy:** narrow or remove the embedded catch while preserving expected malformed/unavailable-config behavior, make the census cover executable embedded Python, and add a discriminating expected-error versus unrelated-defect case.
- **Kind / severity / ownership:** substance / high / T-03 and T-04

## Open questions

None.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "FEAT-65 fails all three perspective grades: required fail-first proof is absent, and an executable broad catch survives outside the census."
  feasibility: risky
  surface: L
  flags: [verification, spec-compliance, census-blind-spot]
  recommend: halt
  tasks: 4
  decisions: 5
  needs_approval: false
  risk: high
  sc_status:
    - { id: SC-01, verdict: partial, method: automated, evidence: "review-harness-qa-c0.md:31-33,42" }
    - { id: SC-02, verdict: partial, method: automated, evidence: "review-harness-qa-c0.md:34,42" }
    - { id: SC-03, verdict: fail, method: automated, evidence: "review-harness-code-reviewer-c0.md:9-19; branch-create-gate.py:81-88" }
    - { id: SC-04, verdict: fail, method: automated, evidence: "review-harness-code-reviewer-c0.md:9-17; review-harness-qa-c0.md:36,42" }
    - { id: SC-05, verdict: partial, method: automated, evidence: "clean-pin-byte-receipts.md:56-66; review-harness-qa-c0.md:37,42" }
    - { id: SC-06, verdict: fail, method: inspection, evidence: "review-harness-code-reviewer-c0.md:9-19; branch-create-gate.py:81-88" }
    - { id: SC-07, verdict: pass, method: inspection, evidence: "build-divergences.md:14-163; byte-evidence-vs-baseline.md:12-275" }
    - { id: SC-08, verdict: pass, method: inspection, evidence: "clean-pin-byte-receipts.md:3-66; pinned 79b7c268..75a36628 artifact diff" }
    - { id: SC-09, verdict: partial, method: automated, evidence: "test-feature-record.py:939-953; review-harness-qa-c0.md:38,42" }
    - { id: SC-10, verdict: partial, method: automated, evidence: "test-inflight-registry.py:1262-1280; review-harness-qa-c0.md:39,42" }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-65-broad-exception-hooks/.harness/harness/features/FEAT-65-broad-exception-hooks/notes/research-FEAT-65-broad-exception-hooks-goalcheck-validate-c0.md
```
