# Receipt — harness-backend-dev — simplify-apply — BUG-124

## Task
Apply the ONE authorized SIMPLIFY finding (SIMPLIFICATION angle, `dispatch-guard.sh:158`):
collapse the mutually-exclusive `if refs and not globs: ... elif refs and globs: ...` pair into a
single nest on `refs`, keeping both inner blocks byte-identical apart from indentation.

## Change
File: `.claude/skills/harness/bin/dispatch-guard.sh`, BUG-124 T-02 run-dir shape check block.

Before:
```python
if refs and not globs:
    ...
elif refs and globs:
    ...
```

After:
```python
if refs:
    if not globs:
        ...
    else:
        ...
```

Both inner bodies are unchanged text, only re-indented by one level. No message string was
reflowed or re-wrapped. `sys.exit(2)` still fires from the same point (inside `if bad:`, inside
the `else` branch, inside `if refs:`), still inside the pre-existing `try`/`except SystemExit:
raise`/`except Exception` structure. `hb.run_dir_refs`, `hb.run_dir_slug_ok`, `hb.run_dir_forms`
call sites are untouched.

## Verification

`bash -n .claude/skills/harness/bin/dispatch-guard.sh` → `BASH_SYNTAX_OK` (script parses; the
python3 heredoc region's semantic indentation is valid).

```
git diff --stat -- .claude/skills/harness/bin/dispatch-guard.sh
 .claude/skills/harness/bin/dispatch-guard.sh | 47 ++++++++++++++--------------
 1 file changed, 24 insertions(+), 23 deletions(-)
```

```
git status --porcelain
 M .claude/skills/harness/bin/dispatch-guard.sh
?? .harness/harness/features/BUG-124-run-dir-squad-suffix/notes/receipt-harness-backend-dev-simplify-altitude-c4.md
?? .harness/harness/features/BUG-124-run-dir-squad-suffix/notes/receipt-harness-backend-dev-simplify-reuse-c4.md
?? .harness/harness/features/BUG-124-run-dir-squad-suffix/notes/receipt-harness-dev-ops-simplify-efficiency-c4.md
?? .harness/harness/features/BUG-124-run-dir-squad-suffix/notes/receipt-harness-dev-ops-simplify-simplification-c4.md
```
Only `dispatch-guard.sh` was modified by me; the four `??` receipts belong to sibling SIMPLIFY
readers (not written by this dispatch) and this dispatch's own receipt is the fifth (this file).

Suite run:
```
env -u HARNESS_AGENT_TYPE bash .claude/skills/harness/bin/run-unit-tests.sh
```
`suite_exit: 0`
`fail_lines: 0` (count of `^FAIL ` lines in captured stdout+stderr)
Runner tail: "pool: 8 workers, 80 files, 65.49s wall" — final line is the pool summary of
`run-unit-tests.sh` itself, not a single script's "N/N checks passed" tail; multiple constituent
scripts individually report e.g. `PASS - 18/18 checks passed`, `9/9 checks passed`,
`28/28 checks passed.`, `all checks passed.`, `18/18 reviewer severity_max enum checks passed.`
— all green, zero `^FAIL ` lines anywhere in the captured log.

Nothing staged, nothing committed.
