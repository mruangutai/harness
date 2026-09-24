# Code review — FEAT-65 validate c1

## Conclusion

Stage 1 **PASS**: SC-01..SC-10, D-01..D-05, ledger D-15, and both c0 findings are satisfied. Stage 2 **PASS with two medium advisories**: shipped behavior is correct, while the embedded-program census over-approximates executability and one changed test function is mechanical grade 2.

## Stage 1 — spec compliance

- **SC-01 PASS:** `notes/byte-evidence-vs-baseline.md` uses pin-committed tests against baseline production; D-01..D-14 ledger every intentional operator-visible divergence.
- **SC-02 PASS:** retained red cases discriminate the canonical open/closed diagnostics and preserved verdicts.
- **SC-03 PASS:** all 77 sites have typed, deleted-absorber, or sole-guard treatment; unrelated defects and process-control exceptions remain loud at required seams.
- **SC-04 PASS:** zero catches in eleven hooks and exactly two in `harness_boundary.py`; increase, reduction, third-catch, and embedded-program mutants discriminate.
- **SC-05 PASS:** five DEC-234 prologues are byte-identical and each-copy mutations redden the lock.
- **SC-06 PASS (inspection):** the classification accounts for 24 + 18 + 35 = 77 sites exactly once and pinned treatments match it, with one `hook_guard` idiom.
- **SC-07 PASS (inspection):** D-01..D-15 give old/new bytes or an explicit no-byte-change ruling and owning cases; no unledgered operator-visible change was found.
- **SC-08 PASS (inspection):** the later-committed clean receipt names immutable implementation pin `97d14f0b`, all 23 suite streams, census/prologue results, and disclaims existence inside that pin.
- **SC-09 PASS:** the pin test is red on baseline and green at the pin; `feature-record.py` direct-command defects remain loud/nonzero.
- **SC-10 PASS:** the pin test is red on baseline and green at the pin; `inflight_registry.py` direct-command defects remain loud/nonzero.
- **D-01..D-05 PASS:** classification, bytes/verdicts, exact inflight tuples/fallbacks, copied prologues, and immutable-pin receipt policy match the approved choices.

## c0 dispositions and falsification

- **QA-65-01 CLOSED:** `git diff --quiet a17269db..7596434c -- <15 named test files>` proves the retained test bytes did not move after the receipt run. SC-01 is sourced by `notes/byte-evidence-vs-baseline.md`; SC-02/03/04/05/09/10 are indexed in `notes/red-first-receipts.md`, each with the pin test against baseline production (exit 1), the same test green at the pin (exit 0), and verbatim red output.
- **CR-01 CLOSED:** `branch-create-gate.py:87` catches exactly `(OSError, ValueError, AttributeError)`. Baseline inspection gives four carrier catches plus one embedded catch = **5**; the pin census gives **0**. `check-plan-routes.py:2207-2232` counts embedded parseable try-bearing Python. Narrow runs of `test-branch-create-gate.py` and `test-broad-catch-census.py` exited 0, proving expected no-file/invalid-JSON/non-object recovery, unrelated non-mapping-`github` loudness, and the embedded broad-catch mutant.

No scope creep, omission, classification mismatch, fail-open regression, silent unrelated-defect path, unledgered byte, incorrect pin claim, or missing required mutation seam was found.

## Stage 2 — code quality

Production changes centralize the sole broad hook boundary, delete local absorbers, preserve direct-command loudness, and keep typed recovery local. Code grading over the pinned range reports 46 passing changed functions and one grade-2 test function; every changed production function meets grade 4.

## Findings

1. **CR-02** · reader: `harness-code-reviewer` · SC: SC-04 · `check-plan-routes.py:2216` · a harmless docstring/diagnostic containing a complete `try/except Exception` example parses and counts as executable, falsely blocking routes although no interpreter consumes it. Satisfies: identify interpreter-fed values or exclude docstrings/non-executed literals; add a complete parseable docstring mutant. kind: substance · severity: med · owned tasks: T-04.
2. **CR-03** · reader: `harness-code-reviewer` · SC: SC-03 · `tests/unit/test-harness-boundary.py:1017` · another contract branch added to the already high-ABC test can wrongly reuse setup/assertion state across open, closed, and process-control cases. Satisfies: split independent guard contracts into focused behavioral cases. kind: substance · severity: med · owned tasks: T-04. Mechanical grade-2 advisory; non-blocking.

Gap #1898 did not occur. No principles claim in a developer receipt required checking.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Stage 1 passes all ten SCs and closes QA-65-01/CR-01; Stage 2 passes with two non-blocking medium advisories."
  severity_max: med
  findings:
    - { id: CR-02, kind: substance, scope: task, severity: med, reader: code-reviewer, SC: SC-04, path: ".claude/skills/harness/bin/check-plan-routes.py:2216", summary: "Embedded-program census treats any parseable try-bearing string as executable.", why: "A complete try/except example in a docstring can falsely block routes; restrict detection to interpreter-fed strings and add that mutant.", tasks: [T-04] }
    - { id: CR-03, kind: substance, scope: task, severity: med, reader: code-reviewer, SC: SC-03, path: "tests/unit/test-harness-boundary.py:1017", summary: "Changed hook_guard contract test is mechanical grade 2.", why: "Its high ABC load mixes independent open, closed, and process-control contracts; split focused behavioral cases.", tasks: [T-04] }
  must_fix: []
  spec_violations: []
  code_grade: grade_2
  grade_2_reasons:
    - "tests/unit/test-harness-boundary.py:1017 case_hook_guard_contract is test-only contract coverage whose independent assertions remain readable, but its ABC load merits the non-blocking CR-03 split."
  reviewed: "4e8c73c07e5f1f102c392fe3800616fc94a1c53d..7596434cdd4931512a008db8f2fce2ec9b9456b9"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-65-broad-exception-hooks/.harness/harness/features/FEAT-65-broad-exception-hooks/notes/review-harness-code-reviewer-c1.md
```
