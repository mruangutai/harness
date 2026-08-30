# Q13 — Cycle 29 authorized for the merge-only substring gate defect

**Authorization issued by the operator on 2026-08-30**, after the stop order that halted the first,
unauthorized attempt. `max_total_cycles` and `cycles_used` both become **29**.

## Correction to the dispatch's premise, stated rather than worked around

The instruction says "resume from the existing uncommitted one-file edit." **That edit no longer
exists.** The operator's own prior stop order required the tree be preserved at merge `1d292c2` plus
review artifacts only, so both hunks — the `import re` and the changed predicate — were reverted by
hand, and `git diff` over `.claude` against `1d292c2` was verified empty. This cycle therefore
**redoes** the work rather than resuming it. Nothing is lost: the remedy is one assertion and it is
specified below.

## The defect

`.claude/skills/harness/bin/test-validate-feature-json.py:350-351`, in `case_root_resolves`:

```python
"1 file(s)" not in r.stderr
```

A **substring test on a rendered count**. The repository holds 41 feature directories, stderr reads
`41 file(s)`, and `"1 file(s)" in "41 file(s)"` is `True`, so the negative assertion trips.

Attribution is measured: the test passes at `6d6d1ce` (origin/main), passes at `cbdadef` (the
feature), and fails **only** at the merge `1d292c2`, which unions FEAT-43's and FEAT-44's feature
directories, 40 → 41. The file's own source is byte-identical at all three commits.

Affected gate: `run-unit-tests.sh --kind unit` — red at the merged head, green at both parents.

## Scope

1. Replace the false substring assertion.
2. **Add a permanent, mutation-sensitive control** proving `1 file(s)` trips the predicate while
   `41 file(s)` does not — **independent of the live repository count**. This is the part the first
   attempt lacked, and it is what makes the fix durable rather than momentary.
3. Run the target test and the full `--kind unit` gate; run the focused FEAT-43 suites; run the
   merge-delta review; re-pin to the exact final commit; refresh goal-check and briefing only as
   required; run the canonical state gate before each commit; commit by explicit pathspec.

**Two constraints that are the point of the remedy, not decoration:**

- **Fix the assertion, never the count.** Trimming the tree to 40 directories turns it green with the
  bug intact, and it returns at 51, 61, 21.
- **A green `--kind unit` run is not proof.** The threshold is live-tree state; archive one feature
  directory and the original assertion passes untouched. The control in item 2 is what closes this,
  because it does not depend on the tree at all.

**Out of scope:** every other remediation, merge, ship, issue creation and distillation. This is a
time bomb in `main` independently of FEAT-43 — it fires whenever main's own feature count ends in
`1` — and that is a backlog row against its owner, not extra work here.
