# FEAT-43 cycle-11 B-01–B-08 receipt

**BLUF:** The complete repair cluster is covered. Revision inputs are resolved to commit OIDs before any diff/show; both CLI and library reject option-like and blob revisions in either position, and grade 2 remains `RESULT: FAIL` with exit 0.

## B-01 through B-08 evidence

- **B-01:** Grade-2 records retain `RESULT: FAIL`, `SEVERITY: med`, and `REASON REQUIRED` while `_status` returns 0 for grade-2-only runs.
- **B-02:** `case_27` is no longer grade 1; the real range has zero grade-1 records.
- **B-03:** `test-code-grade-cli.py` drives `--base=<value>` and `--head=<value>` separately with option-like values and explicit blob OIDs. It checks exit 2, the exact `invalid Git commit revision: <value>` diagnostic, existing selected files unchanged, absent selected files uncreated, no option-derived Git argv, no diff/show argv, and `--end-of-options` before blob commit resolution. `test-code-grade.py` performs the same base/head matrix through `gated_set` with captured subprocess argv.
- **B-04:** Control-byte path output remains JSON-escaped and single-line in normal, parse-error, and ungraded reports.
- **B-05:** Every metric fixture, including `bindings-and-calls`, retains its adjacent hand derivation.
- **B-06:** Direction-pair checks require strict grade movement, not metric movement alone.
- **B-07:** The changed-path-order control invokes `_diff_report` with both supplied orders and asserts identical rendered output.
- **B-08:** Text and JSON preserve the five production/test bar outcomes; grade-2-only reports `RESULT: FAIL` and exits 0.

The B-03 option discriminator was mutation-proved twice: changing either CLI or library `revision.startswith("-")` guard to `False` made its corresponding focused test exit 1 with all four base/head option-argv checks failing. Each temporary source mutation was restored to its pre-mutation SHA-256 (`code-grade.py` `e803bcd4882e083257b242cd7a432cfb441feff60954e389c294b0b0af66b8bc`; `code_grade.py` `a7663be6b02138f3cdbe578981265c58361bbab8b4f638aba4872f4ff2338841`).

## Focused verification

```text
$ /opt/homebrew/bin/python3 .claude/skills/harness/bin/test-code-grade.py
PASS test-code-grade
(exit 0)

$ /opt/homebrew/bin/python3 .claude/skills/harness/bin/test-code-grade-cli.py
PASS test-code-grade-cli
(exit 0)

$ PATH=/opt/homebrew/bin:/usr/bin:/bin /opt/homebrew/bin/python3 .claude/skills/harness/bin/test-check-plan-routes.py
ALL PASS
(exit 0)
```

## Real grader evidence

`git stash create` produced working-tree-equivalent object `a32278514431999d742d4647022d69c5e8144185` without commit or HEAD movement.

```text
$ /opt/homebrew/bin/python3 .claude/skills/harness/bin/code-grade.py --json --base df63193 --head a32278514431999d742d4647022d69c5e8144185
(exit 1; passing 97; existing below-bar non-grade-2 record remains)

$ /opt/homebrew/bin/python3 .claude/skills/harness/bin/code-grade.py --json --base df63193 --head a32278514431999d742d4647022d69c5e8144185 | /opt/homebrew/bin/python3 -c 'import json,sys; print(sum(record["grade"] == 1 for record in json.load(sys.stdin)["records"]))'
0
(pipeline exit 0)
```

## Full repair surfaces and dependency

Engineering-touched source/test files: `.claude/skills/harness/bin/code_grade.py`, `.claude/skills/harness/bin/code-grade.py`, `.claude/skills/harness/bin/test-code-grade.py`, `.claude/skills/harness/bin/test-code-grade-cli.py`, and `.claude/skills/harness/bin/test-check-plan-routes.py`. The independent main-session-direct DEC-174 slice owns only `.claude/skills/harness/bin/validate-digest.py` and `.claude/skills/harness/bin/test-validate-digest.py`; it was not an editing dependency for these engineering files, although concurrent `test-validate-digest.py` bytes can affect the all-working-tree real-grader census and zero-grade-1 measurement.
