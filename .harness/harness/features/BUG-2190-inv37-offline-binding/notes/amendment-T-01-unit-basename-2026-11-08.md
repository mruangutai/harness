# T-01 amendment: unit test basename (2026-11-08)

The plan names its unit test and its integration test with the same basename. `run-unit-tests.py --kind unit` refuses that layout (`MISCONFIGURED: test-check-state-inv37-offline.py appears in both tests/unit and tests/integration`; DEC-217 / suite_layout's unique-basename rule). The unit test is therefore renamed to `tests/unit/test-check-state-inv37-local-binding.py`. This follows the BUG-2180 precedent (`test-check-state-inv26.py` / `test-check-state-inv26-routing.py`). Content, cases and SCs are unchanged. The intent's references to the unit file mean this path.

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
          ".harness/harness/docs/DECISIONS-INDEX.md",
          "tests/integration/canonical-reader-classification.json"
        ],
        "now": [
          ".claude/skills/harness/bin/check_state/board.py",
          "tests/integration/test-check-state-inv37-offline.py",
          "tests/unit/test-check-state-inv37-local-binding.py",
          ".harness/harness/docs/DECISIONS.md",
          ".harness/harness/docs/DECISIONS-INDEX.md",
          "tests/integration/canonical-reader-classification.json"
        ],
        "reason": "suite layout forbids one basename in two kind directories"
      },
      {
        "task": "T-01",
        "field": "verify",
        "was": "python3 tests/unit/test-check-state-inv37-offline.py &&\npython3 tests/integration/test-check-state-inv37-offline.py\n",
        "now": "python3 tests/unit/test-check-state-inv37-local-binding.py &&\npython3 tests/integration/test-check-state-inv37-offline.py\n",
        "reason": "follows the unit test rename"
      }
    ]
  }
}
```
