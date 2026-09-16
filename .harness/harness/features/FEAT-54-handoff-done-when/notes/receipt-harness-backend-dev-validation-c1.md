# Validation c1 receipt — unreadable Edit case

PASS: the focused case `handoff pre-Edit unreadable existing file fails closed` is present at `tests/integration/test-check-domain.py:4130-4157`.

The case writes invalid UTF-8 bytes to the existing handoff fixture, invokes the actual PreToolUse Edit hook with a candidate edit, and jointly requires exit 2, combined stderr/stdout to report that the candidate cannot be reconstructed, and byte-identical preservation of the unreadable fixture. Its `finally` block restores the prior valid fixture bytes for following cases.

Per dispatch, no commands, tests, formatters, linters, suites, or code-grade were run. The final relevant section was read after editing.
