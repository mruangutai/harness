#!/usr/bin/env python3
"""Contract tests for the harness gate policy loader and evaluators."""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
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


FIXTURE_POLICY = {"gates": {"review": "advisory_unless_high"}}
# FEAT-61 T-04: the keys load_policy stopped reading. An old harness.json still carrying them,
# with any value at all, must load exactly as a review-only one does.
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


def write_fixture(directory, name, payload):
    path = os.path.join(directory, name)
    with open(path, "w", encoding="utf-8") as fixture:
        json.dump(payload, fixture)
    return path


def check_policy_loading():
    failures = 0
    with tempfile.TemporaryDirectory() as directory:
        fixture_path = write_fixture(directory, "harness.json", FIXTURE_POLICY)
        failures += check(gate_policy.load_policy(fixture_path), {"review": "advisory_unless_high"},
                          "loader resolves review by name from a review-only fixture")
        legacy = {"gates": dict(FIXTURE_POLICY["gates"], **REMOVED_GATE_KEYS)}
        failures += check(gate_policy.load_policy(write_fixture(directory, "legacy.json", legacy)),
                          {"review": "advisory_unless_high"},
                          "loader ignores removed gate keys whatever their values")
        invalid = {"gates": {"review": "sometimes"}}
        failures += expect_policy_error(
            lambda: gate_policy.load_policy(write_fixture(directory, "invalid.json", invalid)),
            "review", "sometimes", "unrecognised review policy")
        invalid_shape = {"gates": {"review": ["blocking"]}}
        failures += expect_policy_error(
            lambda: gate_policy.load_policy(write_fixture(directory, "invalid-shape.json", invalid_shape)),
            "review", ["blocking"], "non-string review policy")
        failures += expect_policy_error(
            lambda: gate_policy.load_policy(write_fixture(directory, "missing-gates.json", {})),
            "gates", None, "absent gates block")
        failures += expect_policy_error(
            lambda: gate_policy.load_policy(write_fixture(directory, "missing-key.json", {"gates": {}})),
            "review", None, "absent review gate")
        malformed_path = os.path.join(directory, "malformed.json")
        with open(malformed_path, "w", encoding="utf-8") as fixture:
            fixture.write("{")
        failures += expect_policy_error(
            lambda: gate_policy.load_policy(malformed_path),
            "config", malformed_path, "unparseable configuration")
        unreadable_path = os.path.join(directory, "not-present.json")
        failures += expect_policy_error(
            lambda: gate_policy.load_policy(unreadable_path),
            "config", unreadable_path, "unreadable configuration")
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
