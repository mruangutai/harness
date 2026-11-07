# Code review — FEAT-71 — c0

**FAIL — T-01 meets the inspected corpus-independence scope, but its exact pinned Python range fails the mandatory complexity audit.**

Range: `4a05030d..3e6add2af05f5b801afec1ef69440fe54e1529a4`. Source read through `git show` and `git diff`, never substituted HEAD. Six feature commits; no `[harness:human]` commits. The sole dirty tracked path was this feature's orchestration-owned `feature.json`.

## Stage 1 — specification compliance

BRIEF and empty plan `decisions: []` read before diff; binding grilling, operator five-survivor answer, and all five ledger amendments considered. No spec violation found. Clone hooksPath/local-main setup serves the standalone post-merge acceptance rather than weakening an SC; QA owns execution.

- **SC-01 inspection: met.** Pinned `.harness/harness/features/` tree contains exactly the five BRIEF survivors (including this intake); `BRIEF.md:18` defines the exact-set assertion.
- **SC-04 inspection: met.** Pinned deletion inventory removes both retired probes; `.harness/harness.json:168` proceeds to integration after retained live kinds. `suite_layout.py:19` has an empty exception registry. `tests/manual/probe-omp-session-accessor.py:41` carries the reproduction and measured limitations, and `:79` points beside itself. Cross-path `git diff` proves the accessor extension byte-identical (R100). DEC-204 loses only its obsolete merge-gate sentence (`DECISIONS.md:6567`); skill examples/source-pointer edits are removal-only.
- **SC-05 inspection: met.** Pinned record deletion list removes the authorized older records; no `.harness/kaya/`, expertise, README, or `docs/` diff. `notes/record-deletion-receipt.md:5` records the authorized edited/untracked bytes which git cannot prove. SPEC changes only an example path. DEC-159/215/220 truth updates remove precisely the authorized historical exceptions; DEC-213 follows probe relocation; DEC-250 records the approved probe retirement. No independent lifecycle/decision-policy change identified. Index anchors follow the resulting document.
- **SC-02/03 source assessment:** uniform agent, receipt, collision and five-section rules remain; missing receipts now deny. Classification remains AST/disposition/DEC-174 guarded (`check-plan-routes.py:1192,1408,1630`), while historical task labels no longer require deleted plans. Explicit row plans still fail when unreadable or missing the source. The real inventory has no plan ownership claims. Conversion fixtures execute repair, verification, idempotence and dirty-byte comparisons (`test-corpus-non-regression.py:209-328`), rather than replacing the manifest checks with skips. Both corpus-size floors become asserted synthetic non-vacuity. Automated SC verdicts remain QA-owned.

## Stage 2 — ranked findings (all T-01)

1. **High · substance · CR-01:** `tests/integration/test-check-state-records.py:798`, `case_t06_build_entry_invariant`: cyclomatic **9**, cognitive **6**, ABC **46.7**, **grade 1**, ABC driver, test bar 3. Running the required grader on this exact range exits **1**, reporting `SEVERITY: high`; consequently this pin cannot pass the code-grade gate even if all 141 suite files pass. Reduce the changed function's fixture/assertion orchestration to meet its bar without weakening the receipt matrix. **Must fix.**
2. **Med · substance · CR-02:** `tests/integration/test-check-state-handoff.py:489`, `case_t14_exempt_shape`: cyclomatic **13**, cognitive **8**, ABC **30.6**, **grade 2**, cyclomatic+ABC driver. A future exemption/shape edit must track three independent outcomes in one function. Written grade-2 reason: this cohesive synthetic case deliberately observes existing-note shape rejection, missing-note suppression, and the named exemption notice together; separating those observations risks losing their shared-state contrast. Advisory, not blocking.
3. **Med · substance · CR-03:** `tests/integration/test-post-merge-sweep.py:974`, `_t07_sweep`: cyclomatic **4**, cognitive **3**, ABC **26.6**, **grade 2**, ABC driver. Extending a receipt case requires tracing repository setup, receipt mutation, commit, worktree creation and process execution in this helper. Written grade-2 reason: these operations form one disposable real-git fixture lifecycle reused by both the retention matrix and uniform-id probes, keeping their setup identical. Advisory, not blocking.

## Evidence and limits

Executed only `python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/code-grade.py --base 4a05030d --head 3e6add2af05f5b801afec1ef69440fe54e1529a4`: exit 1; 28 passing records, two grade-2 med records, one grade-1 high record. `code_grade: fail`. No suites, builds, lint, formatting, or live probes run. Builder's standalone 141-file receipt is evidence read, not an independent execution claim. No runtime defect beyond the mandatory grading failure established.

## Principles applied

- **Migrate Callers, Then Delete Legacy APIs:** judged the removed receipt/collision parameters and baseline loading as one cutover, not grounds for compatibility shims.
- **Delete First:** accepted removal of historical ownership pointers and exception data while checking the generic enforcement branches survive; did not demand replacement policy machinery.

Open questions: none. Source edits: none.
