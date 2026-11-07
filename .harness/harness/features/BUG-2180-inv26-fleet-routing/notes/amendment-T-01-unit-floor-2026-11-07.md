# T-01 amendment — DEC-217 unit floor (2026-11-07)

Validate run `2026-11-07-02-validate-validator` returned FAIL at 556a23ff. Its must-fix 2 says that no unit-kind test exercises the changed INV-26 logic. QA found that the bugfix runtime-code unit floor (DEC-217) is not met, and its blocking Q1 asked whether T-01's signed `files:` could be extended.

The signed BRIEF already requires this coverage. Its Verification gaps line says: "QA must also satisfy the bugfix runtime-code unit floor (DEC-217)". The plan's `files:` simply omitted the unit-test surface.

Advisor ruling Inv26RoutingAdvisor, 2026-11-07, decided to record the files amendment directly, with no operator round-trip. The reasons:
- production scope and task count are unchanged;
- the amendment corrects the task's HOW so that it matches its own signed requirement.

The change adds one unit-test file to T-01. Behaviour, SCs and production files are unchanged.

## Amendment record

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
          "tests/integration/test-check-state-inv26.py"
        ],
        "now": [
          ".claude/skills/harness/bin/check_state/board.py",
          "tests/integration/test-check-state-inv26.py",
          "tests/unit/test-check-state-inv26-routing.py"
        ],
        "reason": "DEC-217 bugfix unit floor named in the signed BRIEF; validate c0 must-fix 2; advisor ruling Inv26RoutingAdvisor"
      }
    ]
  }
}
```
