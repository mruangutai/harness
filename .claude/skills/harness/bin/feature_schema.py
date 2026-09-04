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
import re
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

_schema_cache = {}

SCHEMA_REL = os.path.join(".claude", "skills", "harness", "bin", "feature-schema.json")


def schema_path_for(for_path):
    """The schema that governs `for_path` — the one belonging to the CHECKOUT the file
    lives in, not the one beside this module.

    ISSUE #749, MEASURED LIVE 2026-08-23 during FEAT-26's ship. check-domain.sh refused a
    legitimate write — `undeclared key 'source_issues' at /github` — because the key WAS
    declared in the worktree's own feature-schema.json and was NOT in main's. The hook
    imports this module through CLAUDE_PROJECT_DIR, which resolves to the main checkout, so
    the schema always came from main whatever tree was being written.

    THE GENERAL SHAPE, and it is why this is worth a walk-up: a feature that ADDS a schema
    key cannot write data using that key until it merges, and so cannot demonstrate the key
    working before it merges. The schema and the data land in ONE commit; the guard read
    them from TWO trees. `github` carries additionalProperties: false (DEC-191), so any new
    key under it hits this.

    WALK UP FOR THE SCHEMA FILE ITSELF, never for the `.claude` directory — probing a
    directory resolves $HOME in a global install, which is the defect dispatch-guard.sh's
    case_20 catches by name.

    Returns None when no checkout schema is found above `for_path`, and the caller then
    falls back to this module's own — so every existing caller, none of which passes a
    path, is unaffected.
    """
    if not for_path:
        return None
    cur = os.path.dirname(os.path.abspath(for_path))
    while cur and cur != os.path.dirname(cur):
        cand = os.path.join(cur, SCHEMA_REL)
        if os.path.isfile(cand):
            return cand
        cur = os.path.dirname(cur)
    return None


def load_schema(for_path=None):
    """Read feature-schema.json for the tree `for_path` lives in, falling back to the copy
    beside this module. Cached PER RESOLVED PATH — a single global cache would serve the
    first tree's schema to every later tree in the same process, which is the same
    wrong-tree bug one level in."""
    resolved = schema_path_for(for_path) or SCHEMA_PATH
    if resolved not in _schema_cache:
        with open(resolved, encoding="utf-8") as f:
            _schema_cache[resolved] = json.load(f)
    return _schema_cache[resolved]


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
    # FEAT-32 and FEAT-33 were ADDED BY HAND, and the reason is the defect in the
    # generator rather than in these two numbers (#718). The map above was generated by
    # scanning ONE working tree, and a feature whose feature.json lives only on its own
    # branch is structurally invisible to that scan -- so both defaulted to 0, and the
    # very first runs[] entry of each was REQUIRED to carry a field none of them have.
    # FEAT-32's orchestrator hit that as an unsatisfiable gate minutes into its build.
    #
    # Both counts are the full length of runs[] at the moment the rule landed, and both
    # exemptions are truthful rather than convenient -- measured, not assumed:
    #   rule enforceable  ee608d2  2026-08-22T08:48:38-07:00  (PR #698 merged)
    #   FEAT-32 runs      d03a835  2026-08-22T06:40:43-07:00  5 runs, 0 with agent
    #   FEAT-33 runs      ccc3803  2026-08-22T08:41:02-07:00  4 runs, 0 with agent
    #
    # Read #718 before adding a third hand-written line. Doing this per feature forever is
    # the symptom; the method cannot see the branches it needs to.
    "FEAT-32-concurrent-write-merge": 5,
    "FEAT-33-board-lifecycle-native": 4,
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


def _problems_for_doc(doc, display, for_path=None):
    schema = load_schema(for_path)
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


# ---------------------------------------------------------------------------
# THE LINE BUDGET COUNTS THE JOURNAL, NOT THE LEDGER (FEAT-54 backlog B-4).
#
# The 300-line cap exists to stop feature.json becoming a narrative — DEC-150's "it is data
# a script parses, not a journal". But `runs:` is exactly the data a script parses, and its
# length is a function of how long the feature ran, not of anyone's prose. MEASURED on
# FEAT-54's own record at `f1ae55f2`: 336 lines total, of which 294 are the 48-entry runs
# array and 42 are everything else. The old cap therefore fired on the one part of the file
# that is legitimately unbounded, and the only ways to satisfy it were to delete real history
# or to raise a number that would be wrong again at 60 runs.
#
# Excluding the array keeps the cap's teeth where they bite: 42 lines of non-runs content has
# a great deal of room before 300, so a feature.json growing comment keys, rationale strings
# or an `escalations` narrative still trips exactly as before.
FEATURE_JSON_LINE_BUDGET = 300


_RUNS_KEY_RE = re.compile(r'"runs"\s*:\s*\[')


def _string_end(text, index):
    """Offset just past the JSON string opening at `index`."""
    index += 1
    while index < len(text):
        if text[index] == "\\":
            index += 2
            continue
        if text[index] == '"':
            return index + 1
        index += 1
    return index


def _array_end(text, start):
    """Offset just past the array opening at `start`, or None if it never closes."""
    depth = 0
    index = start
    while index < len(text):
        char = text[index]
        if char == '"':
            index = _string_end(text, index)
            continue
        if char in "[{":
            depth += 1
        elif char in "]}":
            depth -= 1
            if not depth:
                return index + 1
        index += 1
    return None


def _runs_span(text):
    """(start, end) character offsets of the top-level `runs` array, or None.

    Scans rather than re-serialising, because the budget is about the bytes ON DISK: a
    round-trip through json.dumps would measure a formatting choice this function does not
    make. Strings are skipped wholesale, so a `"runs":[` sequence inside any value — a run
    id, a rationale string, a path — cannot be mistaken for the key.
    """
    index = 0
    while index < len(text):
        char = text[index]
        if char == '"':
            match = _RUNS_KEY_RE.match(text, index)
            if match is None:
                index = _string_end(text, index)
                continue
            start = match.end() - 1
            end = _array_end(text, start)
            return None if end is None else (start, end)
        index += 1
    return None


def journal_lines(text):
    """Line count of a feature.json with its `runs` ledger removed.

    A file with no `runs` key, or one this cannot locate, counts whole — the budget must
    never be loosened by a parse it did not understand.
    """
    span = _runs_span(text)
    if span is None:
        return len(text.splitlines())
    start, end = span
    return len((text[:start] + text[end:]).splitlines())

def problems_for_text(text, display, for_path=None):
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
    return _problems_for_doc(doc, display, for_path)


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
        return problems_for_text(text, path, for_path=path)

    # Lazy import, deliberately confined to THIS branch — see module
    # docstring and T-01's receipt: this is what makes "the .json path never
    # imports PyYAML" empirically checkable rather than merely asserted.
    import harness_yaml
    try:
        doc = harness_yaml.load_file(path)
    except harness_yaml.YamlParseError as e:
        return [f"{path}: not valid YAML: {e}"]
    return _problems_for_doc(doc, path, for_path=path)
