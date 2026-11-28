#!/usr/bin/env python3
"""Contract tests for the harness gate policy loader and evaluators."""
import json
import os
import sys
import tempfile

import unit_support  # noqa: F401  (puts bin/ and tests/ on sys.path)
import gate_policy  # noqa: E402
from check_support import Checks  # noqa: E402
from harness_config_support import build_config, write_config  # noqa: E402

C = Checks()

# FEAT-61 T-04 removed these gate keys from the vocabulary; under the harness.json schema
# (FEAT-2297) a config still carrying them is invalid and refused, never silently ignored.
REMOVED_GATE_KEYS = {"qa_gate": "sometimes", "uat": ["blocking"], "merge": None}

# (policy, must_fix, severity_max, expected verdict, label)
REVIEW_CASES = [
    ("advisory_unless_high", ["must fix"], "none", "FAIL",
     "review blocks must_fix even without a severity escalation"),
    ("advisory_unless_high", [], "med", "PASS", "review passes a clean medium-severity report"),
    ("advisory_unless_high", [], "high", "FAIL", "review blocks high severity"),
    ("blocking", ["finding"], "none", "FAIL", "blocking review blocks findings"),
    ("advisory", ["must fix"], "critical", "PASS", "advisory review always passes"),
]


def check(actual, expected, label):
    return C.check(label, actual == expected, f"expected {expected!r}, got {actual!r}")


def policy_error(call):
    """Run call; return (GatePolicyError, "") or (None, why it did not raise one)."""
    try:
        call()
    except gate_policy.GatePolicyError as error:
        return error, ""
    except Exception as error:
        return None, f"raised {type(error).__name__}, not GatePolicyError"
    return None, "did not raise GatePolicyError"


def expect_policy_error(call, gate, value, label):
    error, why = policy_error(call)
    if error is None:
        C.check(f"{label}: names {gate}", False, why)
        C.check(f"{label}: carries offending value", False, why)
        return
    check(error.gate, gate, f"{label}: names {gate}")
    check(error.value, value, f"{label}: carries offending value")


def check_policy_loading():
    with tempfile.TemporaryDirectory() as directory:
        valid = os.path.join(directory, "harness.json")
        write_config(valid, {"gates": {"review": "blocking"}})
        check(gate_policy.load_policy(valid), {"review": "blocking"},
              "loader resolves review by name from the validated config")
        legacy = build_config({"gates": {"review": "blocking"}})
        legacy["gates"].update(REMOVED_GATE_KEYS)
        legacy_path = os.path.join(directory, "legacy.json")
        with open(legacy_path, "w", encoding="utf-8") as fixture:
            json.dump(legacy, fixture)
        error, why = policy_error(lambda: gate_policy.load_policy(legacy_path))
        seen = (error.gate, "qa_gate" in str(error.value)) if error else why
        check(seen, ("config", True), "removed gate keys are refused, naming the key")


def check_review_evaluation():
    for policy, must_fix, severity, verdict, label in REVIEW_CASES:
        check(gate_policy.evaluate_review(policy, must_fix, severity), verdict, label)
    expect_policy_error(
        lambda: gate_policy.evaluate_review("blocking", [], "unknown"),
        "severity_max", "unknown", "unknown review severity raises loudly")


if __name__ == "__main__":
    check_policy_loading()
    check_review_evaluation()
    sys.exit(C.report())
