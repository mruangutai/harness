# T-19 intent self-quotation corrected; one more of the same class found in T-21

**Two edits, both inside `intent:` blocks, nothing else touched.** T-19's stale quotation of its own
verify block is repaired without weakening the disclosure. The bounded self-consistency sweep over
the ten run-20/23 tasks found exactly one further instance of the same class (T-21) and it is fixed.

## T-19 — the fix

The clause at `plan.yaml:1448` claimed the signed repair was `KEPT VERBATIM ... reading
grep -q '^KIND-DRIFT:'`. That string is not in the block; the block reads
`grep -qE '^(KIND-DRIFT|MISCONFIGURED):'` (`plan.yaml:1437`).

The rewritten clause says what is true: the signed **substance** — column-0 anchoring, `^...:` rather
than the bare token — is kept and now extended to the second detector, so the gate is stronger than
the one signed; the signed **spelling** is not kept, for the two reasons already stated lower in the
same intent (the `--check-kinds` substitution for the `--kind integration` run, and the second
detector), which are referenced rather than re-derived. The measured justification is carried over
unchanged (bare pattern matches 6 indented `ok    case N:` labels from
`test-run-unit-tests-kinds.py` on a GREEN run; real emissions at column 0).

Quotation verified verbatim: `safe_load`ed the file and asserted
`"grep -qE '^(KIND-DRIFT|MISCONFIGURED):'" in tasks['T-19']['verify']` → `True`, and the same string
now appears in the intent → `True`; old `'^KIND-DRIFT:'` gone → `True`.

## Self-consistency sweep — per task, all ten

Method: `safe_load` the plan, then read every intent line matching
`verify|grep|exit|--|block|:\d+|sed|python3|awk|git show|\.sh|\.py` against that task's own
`verify:` block.

| Task | Result |
|---|---|
| T-03 | none. "three negative assertions" = the three `&& exit 1` clauses; "former grep for the bare substring claim was dropped" is true of the current block |
| T-18 | none. "two-sided" matches the MISSING/STILL REGISTERED pair |
| T-19 | **corrected** (above) |
| T-20 | none. "two-sided" matches `git cat-file -e` at 48bbe7e + `git ls-files` absence |
| T-21 | **corrected**. The preserved instruction record (now `:1671-`) says the generator "IS EXPECTED TO EXIT 1" and that "the verify asserts ... an ORPHAN line for DEC-140"; the current block requires `gen-decisions-index.py --stdout` to exit 0. Per that task's own rule ("the instruction below is untouched ... the record of what was written") I did **not** rewrite the record — I extended the `THE VERIFY IS NOW A REVERSAL CHECK` paragraph with a reading note stating that the paragraph below describes the OLD block and is not a description of the current one |
| T-24 | none. `--check-kinds`, both detector prefixes, the pipe/tail warning and the 0.57s/157.7s figures all match the block |
| T-25 | none. "both halves ... then runs `--check-kinds`" matches |
| T-27 | none. "first clause is a positive control - exactly 11 markers at 48bbe7e" matches `-eq 11` |
| T-28 | none. "asserts that clause POSITIVELY" matches the two `grep -qF` clauses; the diff-against-generator claim matches |
| T-29 | none. The quoted enumeration command matches `P=`/`git grep -lE "$P"`; "floor of 60 is the positive control" matches `-ge 60`; "requires the string test_kinds" matches `grep -qF 'test_kinds'`. Its quotation of the config value `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` re-derived against `.harness/harness.json` `test_kinds.integration.cmd` — verbatim match |

## Out of scope, observed, not edited

T-03's intent says the entry "must state all six rules - the sixth names one mechanical check where
it once named two" while its own preamble says the removal ruling deleted the sixth rule that
mandated claim markers. That is an intent-vs-intent tension, not a verify-block description, so it is
outside this dispatch's named class. Flagged as `open_questions` Q1 — non-blocking.

## Evidence

- `check-plan-routes.py <plan>` → `0 violation(s) across 1 plan(s)`, exit 0. The two pre-existing
  `DEVIATION T-22/T-23` lines are informational (`main-session-direct` declarations) and are not
  counted as violations; unchanged by this edit.
- `git diff -U0` on the plan: `1 file changed, 19 insertions(+), 6 deletions(-)`, hunks
  `@@ -1448,5 +1448,13 @@` and `@@ -1624 +1632,6 @@`. The `approval:` block is lines 6-9; no hunk
  reaches it, and `safe_load` still reads
  `approval: {status: approved, approved_by: operator, date: 2026-08-29}`.
- HEAD unmoved at `d3cdea5` (the dispatch cited `457a73c`; the worktree was already ahead of that
  when I arrived — I made no commit and moved nothing). Plan file remains ` M`, uncommitted.
