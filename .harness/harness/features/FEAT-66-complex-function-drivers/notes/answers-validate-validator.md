# FEAT-66 — operator answers to validate c0 (2026-09-26)

Rulings by molchairuangutai on the six must_fix items of runs/validate-validator/digest.md:

- Q1 / MF-05 — SC-02's baseline-vs-pin byte comparison is its fail-first equivalent: **approved** (BRIEF SC-02 amended to say so).
- Q2 / MF-04 — the stale grade-1 exemption for validate-digest.validate in tests/unit/test-code-grade.py: **repair authorized** (test-only, one entry).
- Q3 / MF-06 — T-01 change_type `refactor` → **`cross_module`**.
- Q4 / MF-02 — D-02 **amended to the built form**: the key walk is `_merge_keys`, whose `_fold_merge_rows` extends the six named lists in key order; `apply_merge` constructs MergeResult once on the union path. The D-02-literal form grades 2 (abc 30) and was declined.
- Q5 / MF-01 — the three `ok` lines in test-validate-digest.py that print the running checkout's absolute path are **ruled not a divergence**; exact old/new bytes ledgered as D-09; the normalised comparison stands.
- MF-03 — tests/unit/test-driver-grades.py is removed as a second permanent lock; the red-first evidence is re-taken with the plan's own inline grade assertion (verify block) run against the baseline tree.
