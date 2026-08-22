#!/usr/bin/env python3
"""feature_schema.py — the schema-checking module for a feature's execution
state (feature.json), FEAT-14 D-03.

Imported IN PROCESS by check-domain.sh (T-06) and by validate-feature-json.py
(this directory's thin CLI wrapper) — never spawned as a subprocess on the
write-time path, so a schema violation can be attributed to the real file it
came from rather than a temporary one, and the missing-dependency case is an
ordinary `except ImportError` branch rather than a subprocess that failed to
launch.

`jsonschema` is imported at MODULE level, inside a try, with the result
cached in JSONSCHEMA_AVAILABLE. Never import it inside a per-file function:
check-domain.sh's post sweep calls the entry point once per candidate file,
and a per-call import would pay the (measured) +42.6ms cost, and print the
unavailability message, once per file instead of once per process.

THE JSON PATH — problems_for_text(), and problems_for_file() on a `.json`
path — DEPENDS ON STDLIB `json` AND `jsonschema` ONLY, NEVER PyYAML. This is
deliberate, not an oversight: check-domain.sh's neighbouring `state.yaml`
branch returns `[]` (a fail-open the operator ruled on, DEC-154) when PyYAML
is absent, because state.yaml genuinely has no other way to be read. This
module's JSON path has no PyYAML dependency to be absent in the first place,
so it must never be made to match that shape — a checker with a dependency it
does not need is a checker that can fail for someone else's reason. The YAML
path exists only in problems_for_file(), for a non-`.json` extension, and it
imports harness_yaml LAZILY, inside that one branch, so a JSON-only caller
never pulls PyYAML in at all (T-01 receipt records this placement).
"""
import json
import os
import sys

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    jsonschema = None
    JSONSCHEMA_AVAILABLE = False

BIN_DIR = os.path.dirname(os.path.abspath(__file__))
if BIN_DIR not in sys.path:
    sys.path.insert(0, BIN_DIR)

SCHEMA_PATH = os.path.join(BIN_DIR, "feature-schema.json")

# Verbatim text, per T-01's intent — never return [] on this path and never
# emit the word "skip": [] means checked and clean, and a checker that
# cannot run must never be indistinguishable from one that passed.
UNAVAILABLE_MESSAGE = (
    "jsonschema is REQUIRED and is not importable, so this file CANNOT be checked.\n"
    "Install it with: python3 -m pip install jsonschema  (or python3 -m pip install "
    "--user --break-system-packages jsonschema)"
)

# The redirection sentence, printed verbatim on every undeclared-key
# rejection regardless of nesting level (REQ-03 / the "Where the prose goes
# instead" table) — the destination does not vary by where the key sits.
_REDIRECT = (
    "This file holds execution state only. An operator ruling goes in that feature's "
    "plan.yaml under approval.rulings; run narrative, findings and corrections go in "
    "that run's digest; current state and open questions go in STATE.md; "
    "measurements, research and receipts go in notes/."
)

_schema_cache = None


def load_schema():
    """Read feature-schema.json from beside this module. Cached after the
    first read — the schema file does not change within one process."""
    global _schema_cache
    if _schema_cache is None:
        with open(SCHEMA_PATH, encoding="utf-8") as f:
            _schema_cache = json.load(f)
    return _schema_cache


def _missing_keys(error):
    """error.validator == 'required'. Recover exactly which keys are missing
    by diffing the schema's OWN `required` list against the instance, rather
    than parsing jsonschema's message text — the message wording is not a
    contract the schema author controls."""
    required = error.schema.get("required", [])
    instance = error.instance if isinstance(error.instance, dict) else {}
    return sorted(set(required) - set(instance))


def _undeclared_keys(error):
    """error.validator == 'additionalProperties'. Same technique: diff the
    schema's declared `properties` against the instance's actual keys."""
    allowed = set(error.schema.get("properties", {}))
    instance = error.instance if isinstance(error.instance, dict) else {}
    return sorted(set(instance) - allowed)


def _pointer(path):
    if not path:
        return "/"
    return "/" + "/".join(str(p) for p in path)


# ---------------------------------------------------------------------------
# SC-07's positional rule (FEAT-31 T-15). Read D-23 before changing any of it.
#
# THE TENSION THIS RESOLVES. SC-07 requires BOTH that a NEW runs entry omitting
# `agent` is refused at the write path, AND that every feature.json already on disk
# still validates. A schema `required` satisfies the first and breaks the second:
# check-domain.sh's post sweep reaches feature.json files a change never touched, so
# every Bash command in the repository would start exiting 2. No existing feature.json
# is migrated (operator ruling, 2026-08-20), so absence must keep meaning "predates
# the change" — which makes the rule POSITIONAL, not a schema requirement.
#
# THE MAP IS FROZEN AT A SHA, and this one was generated at 1929774 in the FEAT-31
# worktree with exactly:
#   python3 -c "import glob,json;print({f.split('/')[3]: len(json.load(open(f)).get('runs') or []) for f in sorted(glob.glob('.harness/*/features/*/feature.json'))})"
# It read 31 features holding 393 runs entries, largest FEAT-10-software-factory at 32
# and FEAT-31 itself at 9. The plan's baseline at 2cf792f was 31 features and 390
# entries with FEAT-31 at 6; the whole difference is FEAT-31's own three later runs,
# which is expected because this feature appends an entry per run while it executes.
#
# THREE CONSEQUENCES, all deliberate, and the second is the one that will surprise
# someone:
#   1. A feature ABSENT from the map defaults to 0, so a NEW feature's FIRST run entry
#      is required to carry `agent`. That is the point.
#   2. DELETING a legacy runs entry shifts the indices, and an entry that was exempt at
#      index 5 becomes index 4 and is then REQUIRED to carry the field. That is a loud
#      denial rather than a silent pass, which is the direction this must fail in.
#   3. A display path from which no feature directory name can be read also defaults to
#      0 — a fixture, a temp file, an unexpected layout. Strict, and it fails loudly.
RUNS_AGENT_EXEMPT = {
    "FEAT-01": 1,
    "FEAT-02": 4,
    "FEAT-03-subissue-mirror": 19,
    "FEAT-04-decisions-index": 15,
    "FEAT-05-pyyaml-file-parsers": 6,
    "FEAT-06-team-layer-inv6": 15,
    "FEAT-07-verify-teeth-batch-probe": 14,
    "FEAT-08-remove-cost-tracking": 15,
    "FEAT-09-plan-time-route-check": 9,
    "FEAT-10-software-factory": 32,
    "FEAT-11-graphql-field-resolve": 16,
    "FEAT-12-end-copy-distribution": 16,
    "FEAT-13-single-issue-board-lookup": 13,
    "FEAT-14-feature-json-schema": 21,
    "FEAT-15-domain-product-base": 2,
    "FEAT-16-factory-per-repo-board": 11,
    "FEAT-17-guard-boundaries": 10,
    "FEAT-18-board-truth": 8,
    "FEAT-19-central-product-config": 4,
    "FEAT-20-migration-detector": 10,
    "FEAT-21-features-layout-migration": 10,
    "FEAT-22-docs-layout-migration": 23,
    "FEAT-23-ship-flow-fixes": 20,
    "FEAT-24-config-responsibility-split": 24,
    "FEAT-25-claim-feature-root": 14,
    "FEAT-26-pr-linkage-recorded": 1,
    "FEAT-27-expertise-repository-tier": 16,
    "FEAT-28-ci-wiring-asserted": 4,
    "FEAT-29-graphql-budget": 19,
    "FEAT-30-worktree-per-feature": 12,
    "FEAT-31-orchestrator-context-watch": 9,
}

_FEATURES_SEGMENT = "features"


def _feature_dir_name(display):
    """The feature directory name inside `display`, or None.

    Derived from the PATH the caller named in the message, because that is the only
    identity available: problems_for_text is handed TEXT and a display path, never a
    real file. For a real write the path is
    .harness/<repo>/features/<FEAT-NN-slug>/feature.json, so the name is the segment
    after `features`. Returns None rather than guessing when there is no such segment
    — and None defaults to zero exemptions, which denies rather than permits."""
    parts = str(display).replace(os.sep, "/").split("/")
    try:
        i = parts.index(_FEATURES_SEGMENT)
    except ValueError:
        return None
    return parts[i + 1] if i + 1 < len(parts) else None


def _runs_agent_problems(doc, display):
    """Every runs entry at or past its feature's exempt count must carry a non-empty
    string `agent`. Runs ALONGSIDE the jsonschema validation, never inside it, and its
    problems join the same returned list so check-domain.sh reports them through the
    path it already has."""
    if not isinstance(doc, dict):
        return []
    runs = doc.get("runs")
    if not isinstance(runs, list):
        return []
    exempt = RUNS_AGENT_EXEMPT.get(_feature_dir_name(display), 0)
    problems = []
    for i, entry in enumerate(runs):
        if i < exempt:
            continue
        agent = entry.get("agent") if isinstance(entry, dict) else None
        if not isinstance(agent, str) or not agent.strip():
            problems.append(
                f"{display}: runs[{i}] is missing a non-empty 'agent' — a run entry "
                f"written after FEAT-31 must name the agent that executed it (SC-07). "
                f"The first {exempt} entr{'y' if exempt == 1 else 'ies'} of this "
                f"feature predate the rule and are exempt."
            )
    return problems


def _problems_for_doc(doc, display):
    schema = load_schema()
    validator = jsonschema.Draft202012Validator(schema)
    problems = []
    for error in sorted(validator.iter_errors(doc), key=lambda e: [str(p) for p in e.absolute_path]):
        pointer = _pointer(error.absolute_path)
        if error.validator == "additionalProperties":
            for key in _undeclared_keys(error):
                problems.append(f"{display}: undeclared key {key!r} at {pointer}. {_REDIRECT}")
        elif error.validator == "required":
            for key in _missing_keys(error):
                problems.append(
                    f"{display}: missing required key {key!r} at {pointer} "
                    f"(required by SPEC 11.3)."
                )
        else:
            problems.append(f"{display}: {pointer}: {error.message}")
    problems.extend(_runs_agent_problems(doc, display))
    return problems


def problems_for_text(text, display):
    """Validate JSON document TEXT against the schema. Returns a list of
    stderr LINES, [] when clean. Never exits, never writes a temporary file
    — this is the entry point check-domain.sh imports at T-06, and it is why
    the module exists: a subprocess cannot be handed the real path, and its
    launch failure would escape as a non-blocking exit 1. `display` is the
    path to name IN THE MESSAGE, not a hint for how to parse `text` — this
    function always parses `text` as JSON."""
    if not JSONSCHEMA_AVAILABLE:
        return [UNAVAILABLE_MESSAGE]
    try:
        doc = json.loads(text)
    except json.JSONDecodeError as e:
        return [f"{display}: not valid JSON: {e}"]
    return _problems_for_doc(doc, display)


def problems_for_file(path):
    """Same as problems_for_text, reading from disk. LOAD BY EXTENSION, never
    one permissive loader: a `.json` path is read as text and validated
    through problems_for_text (stdlib json + jsonschema only, see module
    docstring); anything else is read with harness_yaml.load_file, imported
    LAZILY here so the `.json` path above never pulls PyYAML in at all. A
    `.json` file that is valid YAML but not valid JSON is REJECTED, naming
    the JSON decode error — without this a feature.json no `json.load`
    consumer can read would validate clean."""
    if not JSONSCHEMA_AVAILABLE:
        return [UNAVAILABLE_MESSAGE]

    if path.endswith(".json"):
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            return [f"{path}: cannot be read: {e}"]
        return problems_for_text(text, path)

    # Lazy import, deliberately confined to THIS branch — see module
    # docstring and T-01's receipt: this is what makes "the .json path never
    # imports PyYAML" empirically checkable rather than merely asserted.
    import harness_yaml
    try:
        doc = harness_yaml.load_file(path)
    except harness_yaml.YamlParseError as e:
        return [f"{path}: not valid YAML: {e}"]
    return _problems_for_doc(doc, path)
