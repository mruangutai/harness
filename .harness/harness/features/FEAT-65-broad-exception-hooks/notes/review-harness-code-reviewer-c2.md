# Code review — FEAT-65 validate c2

## Conclusion

Stage 1 **PASS** at `ffcc2dafa29fc56ae8a9634e9ed1508e1433661d`: SC-01..SC-10 and D-01..D-05 are satisfied. The regenerated SC-01 evidence closes QA-65-01 with the pin's test bytes against both trees. Stage 2 **PASS with one medium advisory**: CR-02 remains reproducible; CR-03 is mechanical grade-2 reader load without an observable failure and is dismissed as non-gating.

Reviewed `4e8c73c07e5f1f102c392fe3800616fc94a1c53d..ffcc2dafa29fc56ae8a9634e9ed1508e1433661d`. The only dirty tracked path is Harness-owned `feature.json`; implementation review used the immutable pin. Human commits in range: none.

## Stage 1 — spec compliance

- **SC-01 PASS:** `notes/byte-evidence-vs-baseline.md` now records all 22 owning suites with each test file as committed at the pin: 15 suites fail against baseline production and pass at the pin; seven unaffected suites are byte-identical. The c1→c2 ledger row in `notes/build-divergences.md` records this regeneration, and `git diff 7596434c..ffcc2daf -- .claude tests` is empty. QA-65-01 is independently **closed**.
- **SC-02 PASS:** regenerated evidence retains discriminating baseline failures and pin passes for the canonical open/closed guard diagnostics and verdicts.
- **SC-03 PASS:** the 77 classified sites remain typed, deleted absorbers, or sole-guard treatments; unrelated defects and process-control escapes are evidenced at the required seams.
- **SC-04 PASS:** current evidence reports zero broad catches in the eleven hooks, two in `harness_boundary.py`, the singleton ceiling mapping, and discriminating increase/reduction/embedded-program mutants.
- **SC-05 PASS:** the five copied DEC-234 prologues have the same digest and each-copy mutation reddens the lock.
- **SC-06 PASS (inspection):** the classification and ledger account for 24 + 18 + 35 = 77 sites exactly once; treatments match D-01 and no second failure wrapper is present.
- **SC-07 PASS (inspection):** D-01..D-15 contain old/new bytes or explicit no-byte-change rulings and owning cases. The c1→c2 row changes evidence provenance only; no production/test bytes moved.
- **SC-08 PASS (inspection):** `notes/clean-pin-byte-receipts.md` names immutable implementation pin `97d14f0b`, a clean checkout, 23 successful suite invocations, zero-hook/two-boundary census, five-way identity, and explicitly disclaims self-inclusion.
- **SC-09 PASS:** the pin-owned unit test is red against baseline and green at pin; the authoritative `feature-record.py` command remains unwrapped, loud, and nonzero for an injected defect.
- **SC-10 PASS:** the pin-owned integration test is red against baseline and green at pin; `inflight_registry.py` remains unwrapped, loud, and nonzero for injected `ps` and feature-root defects.
- **D-01..D-05 PASS:** classification, preserved verdicts/ledgered bytes, exact inflight tuples and fallback, copied prologues, and later-committed immutable-pin receipt match the signed decisions.

No scope creep, omission, mismatch, unledgered operator-visible divergence, fail-open regression, or silent unrelated-defect path was found.

## Stage 2 — code quality

`code-grade.py --base 4e8c73c0 --head ffcc2daf` reports 46 passing changed functions and one test-only grade-2 function; every changed production function meets the production bar. Production/test bytes are unchanged since the implementation review; current notes and ledger evidence do not alter runtime quality.

### Findings

1. **CR-02 — advisory, unchanged** · task T-04 · kind `substance` · reader severity `med` · disposition `advisory` · SC-04 · `.claude/skills/harness/bin/check-plan-routes.py:2207-2223`. `_embedded_programs` treats every string constant that parses as a try-bearing module as executable. Current-pin remeasurement with a harmless function docstring containing a complete `try/except Exception` returned a broad-catch count of `1`. **Failure scenario:** a maintainer adds that documentation example to a hook; plan-route validation falsely blocks it even though no interpreter executes the string. No such false positive exists in the pinned production files, so the advisory does not gate.

### Assessed and dismissed

- **CR-03 — dismissed, unchanged reader severity `med`** · task T-04 · kind `substance` · SC-03 · `tests/unit/test-harness-boundary.py:1017`. Mechanical grade remains 2 (ABC 27.1), but direct inspection shows independent literal assertions for success, open, closed, `KeyboardInterrupt`, `SystemExit`, and the exact guarded-hook set; no shared mutable assertion state or observable false pass was identified. **Hypothesized scenario reassessed:** reusing open-path state for closed-path assertions would mask a wrong verdict, but this test recomputes `rc` and captured stderr for each path. Splitting it is style/readability absent a demonstrated shipped failure, so it is not carried as a finding.

No developer receipt asserted a checkable **Build the Lever** or **Test Behavior** principle. Known host gap **#1898 lineage failures: 0**; no artifact write was refused.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Stage 1 passes SC-01..SC-10 at ffcc2daf; Stage 2 passes with CR-02 as the sole medium advisory, while CR-03 is dismissed absent observable failure."
  severity_max: med
  findings:
    - { id: CR-02, kind: substance, scope: task, severity: med, reader: code-reviewer, SC: SC-04, path: ".claude/skills/harness/bin/check-plan-routes.py:2207-2223", summary: "Embedded-program census treats any parseable try-bearing string as executable.", why: "T-04 failure scenario: a harmless complete try/except example in a docstring produces count 1 and falsely blocks plan routes; current pin contains no triggering docstring, so disposition is advisory.", tasks: [T-04], disposition: advisory }
  must_fix: []
  spec_violations: []
  code_grade: grade_2
  grade_2_reasons:
    - "tests/unit/test-harness-boundary.py:1017 case_hook_guard_contract is test-only contract coverage; despite ABC 27.1, each branch recomputes its observed result and no concrete false-pass scenario was found, so CR-03 is assessed and dismissed."
  reviewed: "4e8c73c07e5f1f102c392fe3800616fc94a1c53d..ffcc2dafa29fc56ae8a9634e9ed1508e1433661d"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-65-broad-exception-hooks/.harness/harness/features/FEAT-65-broad-exception-hooks/notes/review-harness-code-reviewer-c2.md
```
