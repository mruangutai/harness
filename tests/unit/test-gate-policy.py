#!/usr/bin/env python3
"""Contract tests for the harness gate policy loader and evaluators."""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_os.path.dirname(_anchor_tests))
import importlib.util
import json
import os
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
HERE = BIN_DIR
spec = importlib.util.spec_from_file_location("gate_policy", os.path.join(HERE, "gate_policy.py"))
gate_policy = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = gate_policy
spec.loader.exec_module(gate_policy)
from harness_config_support import build_config, write_config  # noqa: E402


# FEAT-61 T-04 removed these gate keys from the vocabulary; under the harness.json schema
# (FEAT-2297) a config still carrying them is invalid and refused, never silently ignored.
REMOVED_GATE_KEYS = {"qa_gate": "sometimes", "uat": ["blocking"], "merge": None}


def check(actual, expected, label):
    if actual != expected:
        print(f"FAIL {label}: expected {expected!r}, got {actual!r}")
        return 1
    print(f"ok    {label}")
    return 0


def expect_policy_error(call, gate, value, label):
    try:
        call()
    except gate_policy.GatePolicyError as error:
        failures = check(error.gate, gate, f"{label}: names {gate}")
        failures += check(error.value, value, f"{label}: carries offending value")
        return failures
    except Exception as error:
        print(f"FAIL {label}: raised {type(error).__name__}, not GatePolicyError")
        return 1
    print(f"FAIL {label}: did not raise GatePolicyError")
    return 1


def check_policy_loading():
    failures = 0
    with tempfile.TemporaryDirectory() as directory:
        valid = os.path.join(directory, "harness.json")
        write_config(valid, {"gates": {"review": "blocking"}})
        failures += check(gate_policy.load_policy(valid), {"review": "blocking"},
                          "loader resolves review by name from the validated config")
        legacy = build_config({"gates": {"review": "blocking"}})
        legacy["gates"].update(REMOVED_GATE_KEYS)
        legacy_path = os.path.join(directory, "legacy.json")
        with open(legacy_path, "w", encoding="utf-8") as fixture:
            json.dump(legacy, fixture)
        try:
            gate_policy.load_policy(legacy_path)
            print("FAIL removed gate keys are refused: did not raise")
            failures += 1
        except gate_policy.GatePolicyError as error:
            failures += check((error.gate, "qa_gate" in str(error.value)), ("config", True),
                              "removed gate keys are refused, naming the key")
    return failures


def check_review_evaluation():
    failures = 0
    failures += check(
        gate_policy.evaluate_review("advisory_unless_high", ["must fix"], "none"),
        "FAIL", "review blocks must_fix even without a severity escalation")
    failures += check(
        gate_policy.evaluate_review("advisory_unless_high", [], "med"),
        "PASS", "review passes a clean medium-severity report")
    failures += check(
        gate_policy.evaluate_review("advisory_unless_high", [], "high"),
        "FAIL", "review blocks high severity")
    failures += check(
        gate_policy.evaluate_review("blocking", ["finding"], "none"),
        "FAIL", "blocking review blocks findings")
    failures += check(
        gate_policy.evaluate_review("advisory", ["must fix"], "critical"),
        "PASS", "advisory review always passes")
    failures += expect_policy_error(
        lambda: gate_policy.evaluate_review("blocking", [], "unknown"),
        "severity_max", "unknown", "unknown review severity raises loudly")
    return failures



def main():
    return sum((check_policy_loading(), check_review_evaluation()))


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
