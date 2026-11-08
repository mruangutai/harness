# T-01 amendment: INV-37's declared reads (2026-11-08)

INV-37 now probes `ctx.gh_ok`. The FEAT-62 SC-04 consolidation gate (`feat61_lock_*` in the integration suite) requires every invariant's table row to declare the reads it performs. It reported: `check_state/table.py::inv_37 INV-37 reads gh:auth but its row declares no gh:auth read`. T-01 therefore also owns `.claude/skills/harness/bin/check_state/table.py`, for the single `"gh:auth"` entry on the INV-37 row, which is the same declaration INV-26 and INV-30 carry. No behaviour or SC changes.

```yaml
{
  "VERDICT": "PASS",
  "DIGEST": {
    "amendments": [
      {
        "task": "T-01",
        "field": "files",
        "was": [
          ".claude/skills/harness/bin/check_state/board.py",
          "tests/integration/test-check-state-inv37-offline.py",
          "tests/unit/test-check-state-inv37-local-binding.py",
          ".harness/harness/docs/DECISIONS.md",
          ".harness/harness/docs/DECISIONS-INDEX.md",
          "tests/integration/canonical-reader-classification.json"
        ],
        "now": [
          ".claude/skills/harness/bin/check_state/board.py",
          "tests/integration/test-check-state-inv37-offline.py",
          "tests/unit/test-check-state-inv37-local-binding.py",
          ".harness/harness/docs/DECISIONS.md",
          ".harness/harness/docs/DECISIONS-INDEX.md",
          "tests/integration/canonical-reader-classification.json",
          ".claude/skills/harness/bin/check_state/table.py"
        ],
        "reason": "the FEAT-62 SC-04 gate requires INV-37's row to declare its new gh:auth read"
      }
    ]
  }
}
```
