"""feature_record/schema.py — the schema-checking module for a feature's execution
state (feature.json), FEAT-14 D-03.

Imported IN PROCESS by check-domain.py (T-06) and by validate-feature-json.py
(this directory's thin CLI wrapper) — never spawned as a subprocess on the
write-time path, so a schema violation can be attributed to the real file it
came from rather than a temporary one, and the missing-dependency case is an
ordinary `except ImportError` branch rather than a subprocess that failed to
launch.

`jsonschema` is imported at MODULE level, inside a try, with the result
cached in JSONSCHEMA_AVAILABLE. Never import it inside a per-file function:
check-domain.py's post sweep calls the entry point once per candidate file,
and a per-call import would pay the (measured) +42.6ms cost, and print the
unavailability message, once per file instead of once per process.

THE JSON PATH — problems_for_text(), and problems_for_file() on a `.json`
path — DEPENDS ON STDLIB `json` AND `jsonschema` ONLY, NEVER PyYAML. This is
deliberate, not an oversight: check-domain.py's neighbouring `state.yaml`
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
from feature_record.binding import mirror_provenance_problem


try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    jsonschema = None
    JSONSCHEMA_AVAILABLE = False

# What a validator built on this dependency raises for a CONTRACT defect (a schema jsonschema
# itself rejects) -- the one place that names it, so a caller's boundary can catch it without
# guarding the import a second time (FEAT-63 T-02; D-12's one-guard rule). Empty when the
# dependency is absent: the caller's ImportError branch is then the one that fires.
SCHEMA_ERRORS = (jsonschema.exceptions.SchemaError,) if jsonschema is not None else ()

BIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BIN_DIR not in sys.path:
    sys.path.insert(0, BIN_DIR)

SCHEMA_PATH = os.path.join(os.path.dirname(BIN_DIR), "schemas", "feature.json")

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

SCHEMA_REL = os.path.join(".claude", "skills", "harness", "schemas", "feature.json")


def schema_path_for(for_path):
    """The schema that governs `for_path` — the one belonging to the CHECKOUT the file
    lives in, not the one beside this module.

    ISSUE #749, MEASURED LIVE 2026-08-23 during FEAT-26's ship. check-domain.py refused a
    legitimate write — `undeclared key 'source_issues' at /github` — because the key WAS
    declared in the worktree's own schemas/feature.json and was NOT in main's. The hook
    then imported this module from the main checkout, so the schema always came from main
    whatever tree was being written.

    THE GENERAL SHAPE, and it is why this is worth a walk-up: a feature that ADDS a schema
    key cannot write data using that key until it merges, and so cannot demonstrate the key
    working before it merges. The schema and the data land in ONE commit; the guard read
    them from TWO trees. `github` carries additionalProperties: false (DEC-191), so any new
    key under it hits this.

    WALK UP FOR THE SCHEMA FILE ITSELF, never for the `.claude` directory — probing a
    directory resolves $HOME in a global install, which is the defect dispatch-guard.py's
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
    """Read schemas/feature.json for the tree `for_path` lives in, falling back to the copy
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


def _code_run_recorded(feature_doc):
    # A run that graded a specification and no code (`code_grade: n_a`) — the plan-flow SIMPLIFY
    # pass an engineering lead hosts before signature (DEC-195) — is not started work.
    return feature_doc is not None and any(
        isinstance(run, dict) and run.get("code_grade") != "n_a"
        and (run.get("squad") == "engineering" or run.get("code_reviewing"))
        for run in feature_doc.get("runs") or [])


def _task_started(plan, feature_doc):
    started = {"building", "done"} if feature_doc is not None else {"done"}
    return any(task.get("status") in started
               for task in plan.get("tasks") or [] if isinstance(task, dict))


def recovery_command_for(feat_dir, feature_doc=None):
    """Select the receipt recovery command, sharing work-started rules."""
    import artifact_accessors
    import harness_yaml
    try:
        plan = artifact_accessors.load_plan(os.path.join(feat_dir, "plan.yaml"))
    except harness_yaml.YamlParseError:
        return "recover-terminal"
    if (plan.get("status") in {"review", "done"} or _code_run_recorded(feature_doc)
            or _task_started(plan, feature_doc)):
        return "recover-terminal"
    return "open"


def recovery_command_line(feat_dir, feature_doc=None, bound_repo=None):
    """Every gate's recovery instruction, verb included ("run …" or "edit …"). A mapping with
    bad provenance has no command: no tool can prove which repository its numbers live in."""
    real = os.path.realpath(feat_dir)
    if feature_doc is not None and mirror_provenance_problem(feature_doc, bound_repo):
        return (f"edit the github block of {os.path.join(real, 'feature.json')} by hand (no "
                f"command repairs it) so github.repo is {bound_repo!r} and every recorded "
                f"number lives there")
    command = recovery_command_for(feat_dir, feature_doc)
    line = f"run python3 .claude/skills/harness/bin/gh-sync.py {command} {real}"
    return line + (" --yes" if command == "recover-terminal" else "")


# SC-07 (FEAT-31 T-15): every runs[] entry names the agent that executed it. The rule runs
# beside the jsonschema pass rather than as a schema `required` so that it checks the VALUE
# (a blank string names no agent) and its refusal names the rule. It is uniform: no feature
# and no entry index is exempt.
def _runs_agent_problems(doc, display):
    """Every runs entry must carry a non-empty string `agent`. Runs ALONGSIDE the
    jsonschema validation, never inside it, and its problems join the same returned list
    so check-domain.py reports them through the path it already has."""
    if not isinstance(doc, dict):
        return []
    runs = doc.get("runs")
    if not isinstance(runs, list):
        return []
    return [_missing_agent(i, display) for i, entry in enumerate(runs) if not _names_agent(entry)]


def _names_agent(entry):
    agent = entry.get("agent") if isinstance(entry, dict) else None
    return isinstance(agent, str) and bool(agent.strip())


def _missing_agent(i, display):
    return (f"{display}: runs[{i}] is missing a non-empty 'agent' — every run entry "
            f"must name the agent that executed it (SC-07).")


def _problems_for_doc(doc, display, for_path=None):
    schema = load_schema(for_path)
    validator = jsonschema.Draft202012Validator(schema)
    problems = []
    for error in sorted(validator.iter_errors(doc), key=lambda e: [str(p) for p in e.absolute_path]):
        problems.extend(_error_problems(error, display))
    problems.extend(_runs_agent_problems(doc, display))
    return problems


def _error_problems(error, display):
    """The problem lines one jsonschema error renders as."""
    pointer = _pointer(error.absolute_path)
    if error.validator == "additionalProperties":
        return [f"{display}: undeclared key {key!r} at {pointer}. {_REDIRECT}"
                for key in _undeclared_keys(error)]
    if error.validator == "unevaluatedProperties":
        return [f"{display}: {pointer}: {error.message}. {_REDIRECT}"]
    if error.validator == "required":
        return [f"{display}: missing required key {key!r} at {pointer} "
                f"(required by SPEC 11.3)." for key in _missing_keys(error)]
    return [f"{display}: {pointer}: {error.message}"]


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
    — this is the entry point check-domain.py imports at T-06, and it is why
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
