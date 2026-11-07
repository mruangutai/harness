#!/usr/bin/env python3
"""feature_schema.py — the schema-checking module for a feature's execution
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
import hashlib
import stat

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

    ISSUE #749, MEASURED LIVE 2026-08-23 during FEAT-26's ship. check-domain.py refused a
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


def recovery_command_for(feat_dir, feature_doc=None, bound_repo=None, *, replacement=False):
    """Select replacement versus compatible receipt recovery, sharing work-started rules."""
    if feature_doc is not None and not replacement and mirror_provenance_problem(feature_doc, bound_repo):
        return "recover-mirror"
    import artifact_accessors
    import harness_yaml
    try:
        plan = artifact_accessors.load_plan(os.path.join(feat_dir, "plan.yaml"))
    except harness_yaml.YamlParseError:
        return "recover-terminal"
    if plan.get("status") in {"review", "done"}:
        return "recover-terminal"
    # A run that graded a specification and no code (`code_grade: n_a`) — the plan-flow SIMPLIFY
    # pass an engineering lead hosts before signature (DEC-195) — is not started work.
    if feature_doc is not None and any(
            isinstance(run, dict) and run.get("code_grade") != "n_a"
            and (run.get("squad") == "engineering" or run.get("code_reviewing"))
            for run in feature_doc.get("runs") or []):
        return "recover-terminal"
    if any(task.get("status") in ({"building", "done"} if feature_doc is not None else {"done"})
           for task in plan.get("tasks") or [] if isinstance(task, dict)):
        return "recover-terminal"
    return "open"


def recovery_command_line(feat_dir, feature_doc=None, bound_repo=None):
    """Render every gate's recovery instruction from the same selection."""
    command = recovery_command_for(feat_dir, feature_doc, bound_repo)
    line = f"python3 .claude/skills/harness/bin/gh-sync.py {command} {os.path.realpath(feat_dir)}"
    if command != "recover-mirror":
        return line + (" --yes" if command == "recover-terminal" else "")
    github = (feature_doc or {}).get("github") or {}
    previous = (github.get("recovery") or {}).get("from_repo") or github.get("repo") or "<previous-owner/name>"
    return f"{line} --previous-repo {previous} --evidence <target-local-authorization> --yes"


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
    problems = []
    for i, entry in enumerate(runs):
        agent = entry.get("agent") if isinstance(entry, dict) else None
        if not isinstance(agent, str) or not agent.strip():
            problems.append(
                f"{display}: runs[{i}] is missing a non-empty 'agent' — every run entry "
                f"must name the agent that executed it (SC-07)."
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
        elif error.validator == "unevaluatedProperties":
            problems.append(f"{display}: {pointer}: {error.message}. {_REDIRECT}")
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


def resolve_evidence_ref(feature_dir, operand):
    """Normalize a regular, feature-local immutable artifact to its hash-bound reference."""
    root = os.path.realpath(feature_dir)
    raw = os.fspath(operand)
    if ".." in raw.replace("\\", "/").split("/"):
        raise ValueError("evidence must not contain parent traversal")
    path = os.path.abspath(os.path.join(root, raw))
    resolved = os.path.realpath(path)
    if os.path.commonpath((root, resolved)) != root or resolved == root:
        raise ValueError("evidence must stay inside the target feature")
    if not stat.S_ISREG(os.stat(resolved).st_mode):
        raise ValueError("evidence must be a regular file")
    with open(resolved, "rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    return {"path": os.path.relpath(resolved, root), "sha256": digest}


def verify_evidence_ref(feature_dir, ref, subject=None):
    """Verify bytes and, for operator notes, the explicitly authorized subject/effect."""
    if not isinstance(ref, dict) or set(ref) != {"path", "sha256"}:
        raise ValueError("evidence reference requires only path and sha256")
    actual = resolve_evidence_ref(feature_dir, ref["path"])
    if actual != ref:
        raise ValueError("evidence hash does not match the recorded artifact")
    path = os.path.join(feature_dir, actual["path"])
    if subject is None:
        return path
    from artifact_accessors import strict_json_loads
    with open(path, encoding="utf-8") as source:
        note = strict_json_loads(source.read())
    if not isinstance(note, dict) or note.get("feature_id") != subject.get("feature_id"):
        raise ValueError("authorization evidence has a different feature identity")
    effects = note.get("effects")
    matches = [effect for effect in effects if isinstance(effect, dict) and all(
        type(effect.get(key)) is type(value) and effect.get(key) == value
        for key, value in subject.items() if key != "feature_id")
    ] if isinstance(effects, list) else []
    if len(matches) != 1:
        raise ValueError("authorization evidence requires one exact subject/effect")
    return matches[0]


def verify_historical_cycle_count(path, count):
    """An operator note may support missing history, but cannot contradict an explicit count."""
    import digest_record
    try:
        record = digest_record.load_record(path)
    except digest_record.DigestRecordError:
        return
    digest = record.get("DIGEST")
    reported = digest.get("cycles_used") if isinstance(digest, dict) else None
    if type(reported) is int and reported >= 0 and reported != count:
        raise ValueError("historical cycle attribution contradicts the authentic digest count")


def _run_digest_paths(run):
    evidence = run.get("cycle_evidence")
    if evidence:
        yield evidence["path"]
        for previous in evidence.get("previous", []):
            yield previous["path"]
    if run.get("refusal"):
        yield run["refusal"]["digest"]["path"]


def verify_run_digest_owner(run_id, path, runs):
    """A normalized artifact retains its run owner even after attribution correction."""
    parts = path.split(os.sep)
    owner = next((other for other in runs if other["id"] != run_id and
                  (len(parts) > 2 and parts[:2] == ["runs", other["id"]]
                   or path in _run_digest_paths(other))), None)
    if owner:
        raise ValueError(f"digest evidence belongs to run {owner['id']!r}, not {run_id!r}")


def _verify_lead_cycle_evidence(feature_dir, run, runs, path):
    import digest_record
    evidence = run["cycle_evidence"]
    verify_run_digest_owner(run["id"], evidence["path"], runs)
    for previous in evidence.get("previous", []):
        verify_evidence_ref(feature_dir, previous)
        verify_run_digest_owner(run["id"], previous["path"], runs)
    record = digest_record.load_record(path)
    digest = record.get("DIGEST")
    count = digest.get("cycles_used") if isinstance(digest, dict) else None
    if type(count) is not int or count != run.get("cycles_used"):
        raise ValueError("cycle attribution disagrees with digest evidence")


def run_evidence_problems(feature_dir, feature_id, run, runs):
    """Historical evidence is never a live persona return or inferred from its verdict."""
    import digest_record
    problems = []
    try:
        evidence = run.get("cycle_evidence")
        if evidence:
            if type(run.get("cycles_used")) is not int or run["cycles_used"] < 0:
                raise ValueError("cycle evidence requires a nonnegative integer attribution")
            path = verify_evidence_ref(feature_dir, {
                "path": evidence["path"], "sha256": evidence["sha256"]})
            if evidence["source"] == "lead-digest":
                _verify_lead_cycle_evidence(feature_dir, run, runs, path)
            else:
                verify_evidence_ref(feature_dir, evidence["authorization"], {
                    "feature_id": feature_id, "run_id": run["id"],
                    "digest": {"path": evidence["path"], "sha256": evidence["sha256"]},
                    "cycles_used": run.get("cycles_used"), "effect": "record-cycle-evidence"})
                verify_historical_cycle_count(path, run.get("cycles_used"))
        refusal = run.get("refusal")
        if refusal:
            if run.get("verdict") != "BLOCKED" or refusal["run_id"] != run["id"]:
                raise ValueError("refusal requires the same BLOCKED run")
            verify_evidence_ref(feature_dir, refusal["digest"])
            if refusal["source"] == "operator-history":
                verify_evidence_ref(feature_dir, refusal["authorization"], {
                    "feature_id": feature_id, "run_id": run["id"],
                    "digest": refusal["digest"], "effect": "record-refusal"})
    except (OSError, ValueError, TypeError, KeyError, digest_record.DigestRecordError) as error:
        problems.append(str(error))
    return problems


_REPOSITORY = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]*/(?!\.{1,2}$)[A-Za-z0-9_.-]+")


def has_repository_binding(feature_doc):
    """Invalid factory shapes are bound too: no consumer may fall back to the owner."""
    factory = feature_doc.get("factory")
    return factory is not None and (not isinstance(factory, dict) or factory.get("repo") is not None)


def resolve_binding(feature_doc, root):
    """Resolve one feature's repository, board and issue types without owner fallback."""
    import artifact_accessors
    factory = feature_doc.get("factory")
    if factory is not None and not isinstance(factory, dict):
        raise artifact_accessors.FleetError("invalid feature binding", "factory", "expected a mapping")
    bound = factory.get("repo") if factory else None
    if bound is not None:
        return _bound_mirror_binding(bound, root)
    return _owner_mirror_binding(root)


def _bound_mirror_binding(bound, root):
    import artifact_accessors
    import factory_config
    import gh_issue_types
    if not isinstance(bound, str) or not _REPOSITORY.fullmatch(bound):
        raise artifact_accessors.FleetError("invalid feature binding", "factory.repo",
                                          "expected a declared owner/name")
    fleet = artifact_accessors.load_fleet(os.path.join(root, ".harness", "factory", "fleet.yaml"))
    factory_config.repo_entry(fleet, bound)
    config = factory_config.product_config(fleet, bound)
    github = config.get("github")
    if not isinstance(github, dict) or github.get("repo") != bound or not github.get("sync"):
        raise artifact_accessors.FleetError("invalid product mirror", bound,
                                          "github.sync must be enabled and github.repo must match factory.repo")
    return bound, factory_config.board_for(fleet, bound), gh_issue_types.overrides_from_config(config)


def _owner_mirror_binding(root):
    import artifact_accessors
    import gh_board
    import gh_issue_types
    path = os.path.join(root, ".harness", "harness.json")
    try:
        config = artifact_accessors.load_harness_json(path)
    except artifact_accessors.ArtifactAccessError as error:
        raise artifact_accessors.FleetError("owner config unreadable", path, str(error)) from error
    github = config.get("github") or {}
    if not isinstance(github, dict):
        raise artifact_accessors.FleetError("invalid owner mirror", path, "github must be a mapping")
    repo = github.get("repo")
    if not github.get("sync"):
        return repo, None, gh_issue_types.overrides_from_config(config)
    if not isinstance(repo, str) or not _REPOSITORY.fullmatch(repo):
        raise artifact_accessors.FleetError("invalid owner mirror", path, "github.repo must be owner/name")
    return repo, gh_board.load_board(root), gh_issue_types.overrides_from_config(config)


def effective_recorded_repo(doc, bound_repo):
    """The repository a mapping is proven to live in. An UNBOUND feature's pre-provenance
    mapping was created by the owner binding that still resolves it — there was never a second
    destination — so its absent `github.repo` reads as that owner repository. A bound feature's
    absence stays unproven: its old numbers may have come from an ancestor default (DEC-221)."""
    recorded = (doc.get("github") or {}).get("repo")
    if recorded is None and bound_repo and not has_repository_binding(doc):
        return bound_repo
    return recorded


def mirror_provenance_problem(doc, bound_repo):
    """A readable legacy mapping is not permission to reuse its unproven numbers."""
    github = doc.get("github") or {}
    recorded_repo = github.get("repo")
    active = any(github.get(key) for key in ("milestone", "parent", "issues", "attached", "typed"))
    if recorded_repo is not None and recorded_repo != bound_repo and (
            bound_repo is not None or active or github.get("build_entry") in {"opened", "recovered-terminal"}
            or (doc.get("factory") or {}).get("repo") is not None):
        return f"recorded github.repo {recorded_repo!r} conflicts with bound repository {bound_repo!r}"
    if active and (not bound_repo or effective_recorded_repo(doc, bound_repo) != bound_repo):
        return "nonempty mirror has no matching github.repo provenance"
    recovery = github.get("recovery") or {}
    if recovery and (recovery.get("state") != "complete" or recovery.get("pending_create")):
        return "mirror replacement is in progress or has an uncertain pending create"
    if recovery and recovery.get("to_repo") != bound_repo:
        return "mirror replacement targets a different bound repository"
    return None


def receipt_allows_merge(doc, bound_repo):
    """Shared provenance gate: only a recorded, provenanced Build-entry receipt allows."""
    if mirror_provenance_problem(doc, bound_repo):
        return False
    github = doc.get("github") or {}
    entry = github.get("build_entry")
    if entry == "not-applicable":
        return not has_repository_binding(doc)
    if entry in {"opened", "recovered-terminal"}:
        return bool(bound_repo) and effective_recorded_repo(doc, bound_repo) == bound_repo
    return False


def mirror_receipt_for_role(github, role):
    if role in {"milestone", "parent"}:
        return github.get(role)
    if isinstance(role, str) and re.fullmatch(r"task:T-[0-9]{2,}", role):
        return (github.get("issues") or {}).get(role[5:])
    raise ValueError(f"invalid mirror object role: {role!r}")


def _verify_archived_mirror(feature_dir, feature_id, item):
    effect = verify_evidence_ref(feature_dir, item["evidence"], {
        "feature_id": feature_id, "effect": "recover-mirror",
        "from_repo": item["repo"], "reason": item["reason"]})
    if not all(isinstance(effect.get(key), str) and effect[key].strip() for key in ("by", "reason")):
        raise ValueError("mirror authorization requires an operator identity and reason")
    previous_repo = item["previous"].get("repo")
    if previous_repo is not None and previous_repo != item["repo"]:
        raise ValueError("archived mapping conflicts with its previous repository")


def _verify_recovery_generation(feature_dir, feature_id, history, recovery):
    matches = [item for item in history if item["recovery_id"] == recovery["id"]]
    if len(matches) != 1 or matches[0]["repo"] != recovery["from_repo"]:
        raise ValueError("recovery requires exactly one matching archived generation")
    verify_evidence_ref(feature_dir, matches[0]["evidence"], {
        "feature_id": feature_id, "effect": "recover-mirror",
        "from_repo": recovery["from_repo"], "to_repo": recovery["to_repo"],
        "mode": recovery["mode"], "plan_sha256": recovery["plan_sha256"]})


def _verify_reconciled_receipt(feature_dir, feature_id, github, recovery, ref):
    effect = verify_evidence_ref(feature_dir, ref, {
        "feature_id": feature_id, "effect": "adopt-receipt", "recovery_id": recovery["id"],
        "repo": recovery["to_repo"], "plan_sha256": recovery["plan_sha256"]})
    number = effect.get("number")
    if type(number) is not int or number <= 0 or mirror_receipt_for_role(github, effect.get("role")) != number:
        raise ValueError("adoption proof does not match its recorded object")
    if not all(isinstance(effect.get(key), str) and effect[key].strip() for key in ("by", "ownership_evidence")):
        raise ValueError("adoption requires operator identity and ownership evidence")


def mirror_evidence_problems(feature_dir, doc):
    """Check immutable replacement authorizations without consulting remote objects."""
    github = doc.get("github") or {}
    history = github.get("history") or []
    recovery = github.get("recovery") or {}
    try:
        for item in history:
            _verify_archived_mirror(feature_dir, doc["feature_id"], item)
        if recovery:
            _verify_recovery_generation(feature_dir, doc["feature_id"], history, recovery)
            for ref in recovery.get("reconciliation", []):
                _verify_reconciled_receipt(feature_dir, doc["feature_id"], github, recovery, ref)
    except (OSError, ValueError, TypeError, KeyError) as error:
        return [f"mirror evidence: {error}"]
    return []
