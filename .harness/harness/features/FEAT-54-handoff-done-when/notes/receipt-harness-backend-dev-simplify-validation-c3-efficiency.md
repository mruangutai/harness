# SIMPLIFY EFFICIENCY receipt — validation c3

## BLUF

EFFICIENCY finds two advisory-only, structurally evident sources of repeated filesystem work. No source or test changes were made. The separate integration cases are necessary independent falsification and positive controls, not waste; the representation-only digest repairs add no runtime work.

## Findings

1. **File:** `.claude/skills/harness/bin/handoff_done_when.py`  
   **Line:** 89-90  
   **Summary:** `_read_target` performs two consecutive `stat()` calls on the same resolved path.  
   **Concrete cost:** Every resolving finding or approval authority pays one avoidable filesystem metadata lookup; a valid handoff can carry up to four authorities, and this validator participates in write/state gates where filesystem latency is on the gate path.  
   **Alternative:** Store `resolved.stat()` once and read both `st_mode` and `st_size` from that result.  
   **Disposition:** advisory-only; the scoped production file is Main-direct and this dispatch applies nothing.

2. **File:** `tests/unit/test-handoff-done-when.py`  
   **Line:** 55, 128  
   **Summary:** Two positive assertions invoke `problems(...)` twice solely to eagerly construct failure detail.  
   **Concrete cost:** Each redundant invocation creates and removes a temporary directory, creates directories, writes three fixture files, and resolves/reads one or four authority targets; this duplicates identical work without adding an independent observation.  
   **Alternative:** Assign each result to `got` once, then use `got == []` and `repr(got)` in the assertion.  
   **Disposition:** advisory-only; the scoped test file is Main-direct and this dispatch applies nothing.

## Necessary work distinguished from waste

The nested-heading, duplicate-heading, strict-ATX, containment, symlink/FIFO, fail-closed pre-Edit, and positive-resolution cases in the unit and integration files exercise distinct prohibited behaviors or preserve their positive controls. Their separate fixtures and gate invocations are necessary independent falsification, even where setup is similar, and are not findings. The five repaired lead digests listed in `notes/qa-validation-c3.md:36-44` are representation-only records and introduce no startup, hot-path, retained-scope, or test execution cost.

## Execution

No commands, tests, validation, timing, formatters, or linters were run. Zero source/test changes were made; this receipt is the only file written.
