# T-01 fail-first record

Verify run at the T-01 build tip before commit. The red-first block runs tests/unit/test-practicality-rule.py at HEAD and over a git archive of base 3e979ae3 with the new test file copied in:

```
red-first: 16 of 16 cases; not green now or not red at base: []
```

All 16 refusal and relief cases are green at HEAD and red at base. Every verify command exited 0.
