"""Load and evaluate the configured harness gate policies."""
import artifact_accessors


# FEAT-61 T-04 (SC-04): review is the only gate any process reads. qa_gate, uat and merge were
# loaded and vocabulary-checked here without a consumer, so they left the vocabulary, the live
# config, the template and the example in one cutover. Unread policy is dead config; a knob
# returns with its reader if one is ever wanted. An old harness.json still carrying those keys
# loads exactly as a review-only one does.
GATE_VOCABULARIES = {
    "review": frozenset(("blocking", "advisory", "advisory_unless_high")),
}
SEVERITIES = frozenset(("none", "low", "med", "high", "critical"))


class GatePolicyError(ValueError):
    """A required gate policy is absent, unreadable, or invalid."""

    def __init__(self, gate, value):
        self.gate = gate
        self.value = value
        super().__init__(f"invalid gate policy for {gate}: {value!r}")


def _load_config(harness_json_path):
    try:
        return artifact_accessors.load_harness_json(harness_json_path)
    except artifact_accessors.ArtifactAccessError as error:
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
    """Return the configured review gate, rejecting every missing or invalid input loudly."""
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
