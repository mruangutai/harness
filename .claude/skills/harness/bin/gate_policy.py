"""Load and evaluate the configured harness gate policies."""
import json


GATE_VOCABULARIES = {
    "qa_gate": frozenset(("blocking", "advisory")),
    "review": frozenset(("blocking", "advisory", "advisory_unless_high")),
    "uat": frozenset(("blocking", "blocking_when_uat_criteria_exist", "advisory")),
    "merge": frozenset(("user_gated", "autonomous")),
}
SEVERITIES = frozenset(("none", "low", "med", "high", "critical"))
SUITE_OUTCOMES = frozenset(("pass", "fail", "skipped"))


class GatePolicyError(ValueError):
    """A required gate policy is absent, unreadable, or invalid."""

    def __init__(self, gate, value):
        self.gate = gate
        self.value = value
        super().__init__(f"invalid gate policy for {gate}: {value!r}")


class QaResult(str):
    """A QA verdict whose detail preserves suites that were deliberately skipped."""

    def __new__(cls, verdict, detail):
        result = super().__new__(cls, verdict)
        result.detail = detail
        return result


def _load_config(harness_json_path):
    try:
        with open(harness_json_path, encoding="utf-8") as config_file:
            return json.load(config_file)
    except (OSError, json.JSONDecodeError) as error:
        raise GatePolicyError("config", harness_json_path) from error


def _require_gates(config):
    try:
        gates = config["gates"]
    except (KeyError, TypeError) as error:
        raise GatePolicyError("gates", None) from error
    if not isinstance(gates, dict):
        raise GatePolicyError("gates", gates)
    return gates


def _resolve_gate(gates, gate, vocabulary):
    try:
        value = gates[gate]
    except KeyError as error:
        raise GatePolicyError(gate, None) from error
    if not isinstance(value, str) or value not in vocabulary:
        raise GatePolicyError(gate, value)
    return value


def load_policy(harness_json_path):
    """Return all configured gates, rejecting every missing or invalid input loudly."""
    gates = _require_gates(_load_config(harness_json_path))
    return {gate: _resolve_gate(gates, gate, vocabulary)
            for gate, vocabulary in GATE_VOCABULARIES.items()}


def evaluate_review(policy, must_fix, severity_max):
    """Return the review verdict prescribed by DEC-31 for the declared policy."""
    if policy not in GATE_VOCABULARIES["review"]:
        raise GatePolicyError("review", policy)
    if severity_max not in SEVERITIES:
        raise GatePolicyError("severity_max", severity_max)
    if policy == "advisory":
        return "PASS"
    if policy == "blocking":
        return "FAIL" if must_fix else "PASS"
    if must_fix or severity_max in {"high", "critical"}:
        return "FAIL"
    return "PASS"


def _validate_suites(suites):
    skipped = []
    for suite, outcome in suites.items():
        if outcome not in SUITE_OUTCOMES:
            raise GatePolicyError(str(suite), outcome)
        if outcome == "skipped":
            skipped.append(str(suite))
    return skipped


def evaluate_qa(policy, suites):
    """Return the QA verdict and preserve skipped suites in its detail."""
    if policy not in GATE_VOCABULARIES["qa_gate"]:
        raise GatePolicyError("qa_gate", policy)

    skipped = _validate_suites(suites)
    detail = "skipped: " + ", ".join(skipped) if skipped else ""
    if policy == "blocking" and any(outcome == "fail" for outcome in suites.values()):
        return QaResult("FAIL", detail)
    return QaResult("PASS", detail)
