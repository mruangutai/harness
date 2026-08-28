#!/usr/bin/env python3
"""Contract tests for the harness gate policy loader and evaluators."""
import importlib.util
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("gate_policy", os.path.join(HERE, "gate_policy.py"))
gate_policy = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = gate_policy
spec.loader.exec_module(gate_policy)


FIXTURE_POLICY = {
    "gates": {
        "qa_gate": "blocking",
        "review": "advisory_unless_high",
        "uat": "blocking_when_uat_criteria_exist",
        "merge": "user_gated",
    }
}


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


def main():
    failures = 0
    with tempfile.TemporaryDirectory() as directory:
        fixture_path = write_fixture(directory, "harness.json", FIXTURE_POLICY)
        policy = gate_policy.load_policy(fixture_path)
        failures += check(policy["qa_gate"], "blocking", "loader resolves qa_gate by name from fixture")
        failures += check(policy["review"], "advisory_unless_high", "loader resolves review by name from fixture")
        failures += check(policy["uat"], "blocking_when_uat_criteria_exist", "loader resolves uat by name from fixture")
        failures += check(policy["merge"], "user_gated", "loader resolves merge by name from fixture")

        invalid = {"gates": dict(FIXTURE_POLICY["gates"], qa_gate="sometimes")}
        failures += expect_policy_error(
            lambda: gate_policy.load_policy(write_fixture(directory, "invalid.json", invalid)),
            "qa_gate",
            "sometimes",
            "unrecognised qa_gate policy",
        )
        invalid_shape = {"gates": dict(FIXTURE_POLICY["gates"], qa_gate=["blocking"])}
        failures += expect_policy_error(
            lambda: gate_policy.load_policy(write_fixture(directory, "invalid-shape.json", invalid_shape)),
            "qa_gate",
            ["blocking"],
            "non-string qa_gate policy",
        )
        failures += expect_policy_error(
            lambda: gate_policy.load_policy(write_fixture(directory, "missing-gates.json", {})),
            "gates",
            None,
            "absent gates block",
        )
        missing_key = {"gates": dict(FIXTURE_POLICY["gates"])}
        del missing_key["gates"]["merge"]
        failures += expect_policy_error(
            lambda: gate_policy.load_policy(write_fixture(directory, "missing-key.json", missing_key)),
            "merge",
            None,
            "absent named gate",
        )
        malformed_path = os.path.join(directory, "malformed.json")
        with open(malformed_path, "w", encoding="utf-8") as fixture:
            fixture.write("{")
        failures += expect_policy_error(
            lambda: gate_policy.load_policy(malformed_path),
            "config",
            malformed_path,
            "unparseable configuration",
        )
        unreadable_path = os.path.join(directory, "not-present.json")
        failures += expect_policy_error(
            lambda: gate_policy.load_policy(unreadable_path),
            "config",
            unreadable_path,
            "unreadable configuration",
        )

    failures += check(
        gate_policy.evaluate_review("advisory_unless_high", ["must fix"], "none"),
        "FAIL",
        "review blocks must_fix even without a severity escalation",
    )
    failures += check(
        gate_policy.evaluate_review("advisory_unless_high", [], "med"),
        "PASS",
        "review passes a clean medium-severity report",
    )
    failures += check(
        gate_policy.evaluate_review("advisory_unless_high", [], "high"),
        "FAIL",
        "review blocks high severity",
    )
    failures += check(
        gate_policy.evaluate_review("blocking", ["finding"], "none"),
        "FAIL",
        "blocking review blocks findings",
    )
    failures += check(
        gate_policy.evaluate_review("advisory", ["must fix"], "critical"),
        "PASS",
        "advisory review always passes",
    )
    failures += expect_policy_error(
        lambda: gate_policy.evaluate_review("blocking", [], "unknown"),
        "severity_max",
        "unknown",
        "unknown review severity raises loudly",
    )

    qa_result = gate_policy.evaluate_qa("blocking", {"unit": "pass", "integration": "skipped"})
    failures += check(qa_result, "PASS", "blocking QA does not fail skipped suite")
    failures += check(qa_result.detail, "skipped: integration", "QA detail reports skipped suite")
    failures += check(
        gate_policy.evaluate_qa("blocking", {"unit": "fail", "integration": "skipped"}),
        "FAIL",
        "blocking QA blocks failed suite",
    )
    failures += check(
        gate_policy.evaluate_qa("advisory", {"unit": "fail"}),
        "PASS",
        "advisory QA always passes",
    )
    return failures


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
