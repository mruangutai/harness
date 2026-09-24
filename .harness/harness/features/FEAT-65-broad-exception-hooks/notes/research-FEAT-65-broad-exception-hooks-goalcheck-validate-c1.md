# FEAT-65 validate c1 — independent goal-check

Review pin: `7596434cdd4931512a008db8f2fce2ec9b9456b9`  
Baseline: `4e8c73c07e5f1f102c392fe3800616fc94a1c53d`

The feature remains unshippable because SC-01 still lacks the required same-test-at-review-pin fail-first receipt. The other nine criteria pass. CR-01 is closed independently: the embedded reader is typed, executable embedded Python is included in the census, the baseline/pin counts are 5/0, expected config failures recover, and the unrelated defect stays loud.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Nine SCs pass and CR-01 is closed, but QA-65-01 remains open for SC-01 because its retained baseline comparison did not use the tests committed at 7596434."
  feasibility: risky
  surface: L
  flags: [verification]
  recommend: reframe
  risk: high
  tasks: 4
  decisions: 15
  needs_approval: false
  sc_status:
    - id: SC-01
      verdict: partial
      disposition: unmet
      evidence: "notes/byte-evidence-vs-baseline.md:5-10,91-96,129-134 compares each tree's own suite at older heads dd1203a35/e10c56de/ec0996cb; review-harness-qa-c1.md:21-32 confirms the review-pin check-domain/worktree/post test files differ, although its clean-pin suites and build-divergences.md ledger support the remaining preservation clauses."
    - id: SC-02
      verdict: pass
      disposition: met
      evidence: "notes/red-first-receipts.md:11-25,37-50,52-84 retains baseline exit 1/pin exit 0 failures for all five classified guarded hooks; review-harness-qa-c1.md:15-20,25,33 records the green integration matrix and identical receipt tests at 7596434."
    - id: SC-03
      verdict: pass
      disposition: met
      evidence: "notes/red-first-receipts.md:11-25,27-194 retains typed-boundary, absorber-removal, loud-defect and process-control RED/GREEN cases; notes/research-FEAT-65-hook-site-classification.md:23-89 accounts for all 77 sites; review-harness-qa-c1.md:26,34 records green pin evidence."
    - id: SC-04
      verdict: pass
      disposition: met
      evidence: "notes/red-first-receipts.md:148-184,196-203 is RED at baseline and GREEN at the pin; check-plan-routes.py:2196-2200,2207-2235 has the exact 0/2 ceiling and embedded-program census; test-broad-catch-census.py:53-66,127-143 covers the representative increase, third boundary catch, live zeroes, and clean reduction."
    - id: SC-05
      verdict: pass
      disposition: met
      evidence: "notes/red-first-receipts.md:86-116,148-184 retains RED/GREEN prologue evidence; test-broad-catch-census.py:161-177 checks byte identity, the required tuple, and independent mutation of every one of the five copies; notes/clean-pin-byte-receipts.md:58-68 records one shared digest."
    - id: SC-06
      verdict: pass
      disposition: met
      evidence: "notes/research-FEAT-65-hook-site-classification.md:23-99 classifies 24+18+35=77 sites; notes/build-divergences.md:14-176 maps shipped typed/guard/deleted treatments and verdict-preserving cases, including D-15; pinned source has the sole diagnostic in harness_boundary.py:442-462 and only the five classified callers."
    - id: SC-07
      verdict: pass
      disposition: met
      evidence: "notes/build-divergences.md:14-176 records D-01 through D-15 with old/new bytes or no-byte-change ruling and re-pinned cases; notes/byte-evidence-vs-baseline.md:12-275 inventories every owning-suite stream difference against 4e8c73c0."
    - id: SC-08
      verdict: pass
      disposition: met
      evidence: "notes/clean-pin-byte-receipts.md:3-7 names clean implementation pin 97d14f0b, says the receipt lands later, and disclaims existence inside that pin; review SHA 7596434 has parent 97d14f0b and commits that receipt; lines 9-68 record suites, stream digests, 0/2 census, and five-way identity."
    - id: SC-09
      verdict: pass
      disposition: met
      evidence: "notes/red-first-receipts.md:128-135 retains the review-pin unit case failing against baseline and green at pin; review-harness-qa-c1.md:9-14,29,37 records the green unit matrix and identical test file at 7596434."
    - id: SC-10
      verdict: pass
      disposition: met
      evidence: "notes/red-first-receipts.md:137-146 retains the review-pin integration case failing against baseline and green at pin; review-harness-qa-c1.md:15-20,30,38 records the green integration matrix and identical test file at 7596434."
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-65-broad-exception-hooks/.harness/harness/features/FEAT-65-broad-exception-hooks/notes/research-FEAT-65-broad-exception-hooks-goalcheck-validate-c1.md
```

## Perspective grades

| perspective | verdict | carrying SC rows | evidence |
|---|---|---|---|
| operator | partial | SC-01 partial; SC-02, SC-09, SC-10 pass | The observable implementation is green, but the operator's signed fail-first byte-preservation proof is incomplete. |
| code maintainer | pass | SC-03, SC-04, SC-05 pass | Typed boundaries/process control, the 0/2 census, and five-way prologue identity are proven. |
| reader | pass | SC-06, SC-07, SC-08 pass | All 77 treatments, the divergence ledger, and the later-commit clean-pin receipt are traceable. |

## Prior c0 dispositions

| id | disposition | verdict | evidence |
|---|---|---|---|
| QA-65-01 | open | fail | Closed for SC-02, SC-03, SC-04, SC-05, SC-09, and SC-10. It remains open for SC-01: `byte-evidence-vs-baseline.md` names older evidence heads and runs each tree's own test file rather than one test committed at review pin against both production states. |
| CR-01 | closed | pass | `branch-create-gate.py:81-92` catches exactly `(OSError, ValueError, AttributeError)`; `check-plan-routes.py:2207-2235` parses string constants carrying a try; baseline/pin counts are 5/0; `test-branch-create-gate.py:245-274` proves expected recovery and loud unrelated failure; `test-broad-catch-census.py:53-66` proves embedded broad catches count; `build-divergences.md:167-176` records D-15. |

## Findings

- id: `QA-65-01`
- reader: `harness-pm`
- SC: `SC-01`
- exact file:line: `notes/byte-evidence-vs-baseline.md:5-10,91-96,129-134`
- defect: The retained SC-01 baseline runs use suite files from older task heads, while the corresponding tests changed before review SHA `7596434`; both recorded suite sides exit 0, so no test committed at the review pin is shown failing against baseline production.
- concrete failure scenario: A regression or assertion change in the final `test-check-domain.py`, `test-check-domain-worktree.py`, or `test-check-domain-post.py` can escape the receipt: the older baseline-side test never executes that final assertion, yet the recorded comparison remains green.
- satisfies: Copy the tests committed at `7596434` into a clean `4e8c73c0` production tree, run the SC-01 byte-preservation case there and at `7596434` with the same command and production-path overrides, and retain the exact failing assertion/output against baseline plus the green pin result.
- kind: `substance`
- severity: `high`
- owned plan tasks: `T-01`, `T-02`, `T-03`, `T-04`

## Independent CR-01 probe receipts

- Baseline `branch-create-gate.py` has five executable broad handlers: `_resolve_root`, embedded `_CONFIG_READER`, config load, config shape, and command extraction. The pin's `tests/unit/test-broad-catch-census.py` narrow run passed its live zero count and embedded-string mutant.
- The pin's `tests/integration/test-branch-create-gate.py` narrow run passed 14/14, including `run_feat65_config_reader`: absent file, malformed JSON, and non-object top-level JSON return exactly `false -`; a non-mapping `github` block exits 1 with `AttributeError`.
- The review pin's CR-01 production files and these two test files are byte-identical to the locally probed checkout; `7596434` has implementation parent `97d14f0b`.
