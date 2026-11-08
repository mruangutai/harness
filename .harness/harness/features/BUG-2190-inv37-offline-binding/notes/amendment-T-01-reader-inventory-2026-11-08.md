# T-01 amendment: canonical-reader inventory row (2026-11-08)

The offline branch loads the fleet locally through the canonical accessor `artifact_accessors.load_fleet`. That is the same accessor `feature_schema._bound_mirror_binding` uses, and `factory_config` has no loader of its own. The canonical-reader audit (`check-plan-routes.py --canonical-reader-audit`, a CI gate) requires an inventory row for every live reader site. T-01 therefore also owns `tests/integration/canonical-reader-classification.json`, for that single row. No behaviour or SC changes.

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
          "tests/unit/test-check-state-inv37-offline.py",
          ".harness/harness/docs/DECISIONS.md",
          ".harness/harness/docs/DECISIONS-INDEX.md"
        ],
        "now": [
          ".claude/skills/harness/bin/check_state/board.py",
          "tests/integration/test-check-state-inv37-offline.py",
          "tests/unit/test-check-state-inv37-offline.py",
          ".harness/harness/docs/DECISIONS.md",
          ".harness/harness/docs/DECISIONS-INDEX.md",
          "tests/integration/canonical-reader-classification.json"
        ],
        "reason": "the offline fleet read is a new canonical load_fleet site; the CI reader audit requires its inventory row"
      }
    ]
  }
}
```
