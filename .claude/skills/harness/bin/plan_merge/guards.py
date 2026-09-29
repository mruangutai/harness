"""Destination, reload, schema and lock guards shared by every verb; the one write route. (FEAT-70)"""
import os
import re
import sys
import tempfile

import artifact_accessors
import factory_config
import gh_board
import harness_boundary
import harness_merge
import harness_yaml
import plan_anchors

# The bin directory is the package's parent: plan_merge/ sits beside the siblings it
# imports and the two tools it loads by path. (FEAT-70)
BIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# A features directory either directly under a .harness segment or nested one segment deeper
# (repo-tier), a FEAT- or BUG- prefixed directory, and the literal filename plan.yaml. Matched
# on the RESOLVED path only (harness_merge.require_destination), never the literal argument.
PLAN_TAIL = re.compile(
    r"(?:^|/)\.harness/(?:[^/]+/)?features/(?:FEAT|BUG)-[^/]+/plan\.yaml$"
)


def _resolve_plan(file_path):
    """require_destination on the RESOLVED path, or print the refusal and exit its code.

    Extracted so all five verbs share ONE destination guard. A second copy would be a second
    place for exit 9 to stop being true."""
    try:
        return harness_merge.require_destination(
            file_path,
            PLAN_TAIL,
            "a plan.yaml under a features directory",
            [
                "  a legal path looks like .harness/features/FEAT-NN-slug/plan.yaml or",
                "  .harness/<repo>/features/FEAT-NN-slug/plan.yaml.",
                "  This tool merges plan.yaml only.",
            ],
        )
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)


def _harness_root(start):
    """Walk up from `start` to the checkout whose manifest declares a harness, or None.

    THE PROBE NAMES THE MANIFEST, NEVER THE `.harness` DIRECTORY. A probe for the directory
    resolves $HOME as a root in the global install — B-7 verbatim — and
    test-check-plan-routes.py's case_20 asserts that no copy of this idiom regresses.

    Extracted from `_legal_stations` (FEAT-41 F-05), whose docstring already described this as
    its own named step. It is a walk with a termination condition, which is a different kind of
    thing from choosing a vocabulary, and the two were interleaved in one body at grade 3.
    """
    root = start
    while True:
        if os.path.isfile(os.path.join(root, harness_boundary.MARKER)):
            return root
        parent = os.path.dirname(root)
        if parent == root:
            return None
        root = parent


def _legal_stations(resolved):
    """The station vocabulary the target plan.yaml's own checkout declares, plus the terminal
    marker, as an ordered tuple.

    IMPORTED, NEVER RESPELLED (FEAT-41 T-03). factory_config owns MANDATED_STATIONS and
    TERMINAL_STATIONS; declaring either here would be a second vocabulary, and since this module
    is imported by nothing, check-plan-routes.py and check-domain.py would each respell it as a
    bare literal and D-05's claim that the marker is declared once in code would be false the
    day it landed.

    The board is read from the harness.json of the checkout the plan belongs to. A checkout with
    no board declared — every test fixture, and any project that has not onboarded a board — is
    NOT a licence to accept anything: the mandate still applies, because MANDATED_STATIONS is
    what a declaration is checked against in the first place.

    THE ROOT PROBE NAMES THE MANIFEST, NEVER THE `.harness` DIRECTORY. A probe for the directory
    resolves $HOME as a root in the global install — B-7 verbatim — and
    test-check-plan-routes.py's case_20 asserts that no copy of this idiom regresses. The walk
    starts from the plan.yaml's own directory rather than from this script's location, because
    the vocabulary that governs a write belongs to the checkout being written to, not to
    whichever checkout happens to be running the tool.
    """
    root = _harness_root(os.path.dirname(os.path.abspath(resolved)))
    stations = None
    if root is not None:
        try:
            board = gh_board.load_board(root)
            if board is not None:
                stations = factory_config.station_names(board)
        except artifact_accessors.FleetError:
            # An unusable board declaration is not this tool's error to report — the state gate
            # and every board writer already name it loudly. Fall back to the mandate so a
            # station write is still validated rather than waved through.
            stations = None
    if stations is None:
        stations = factory_config.MANDATED_STATIONS
    return tuple(stations) + factory_config.TERMINAL_STATIONS


def _refuse_illegal_station(station, legal):
    """Exit 4, naming the offending value and every legal one.

    CALLED BEFORE THE LOCK IS TAKEN, deliberately: a refused value must never open the file, so
    a typo cannot contend for the lock or leave a partial write behind."""
    print(
        f"plan-merge: {station!r} is not a legal station — expected one of: "
        + ", ".join(legal),
        file=sys.stderr,
    )
    sys.exit(4)


def _reload_or_refuse(spliced_bytes):
    """The spliced document, or a refusal naming the splice as the fault."""
    try:
        return harness_yaml.load_str(spliced_bytes.decode("utf-8"), "<spliced plan>")
    except harness_yaml.YamlParseError as exc:
        raise harness_merge.MergeRefusal(
            5, ["UNPARSEABLE: the amended plan does not load — REFUSING to write it.",
                f"  {exc}",
                "  this is a splice defect, not a bad value: the base parsed."])


def _sole_item(reloaded, key, iid):
    """The one item under `key` whose id is `iid`, or a refusal.

    Exactly one is required: a duplicate id cannot be amended unambiguously, and binding to
    the first match silently is what the code-reviewer found in cycle 0.
    """
    items = (reloaded or {}).get(key)
    if not isinstance(items, list):
        raise harness_merge.MergeRefusal(
            5, [f"REFUSED: {key}: is not a list after the amendment — REFUSING to write it."])
    got = [it for it in items if isinstance(it, dict) and it.get("id") == iid]
    if len(got) != 1:
        raise harness_merge.MergeRefusal(
            5, [f"REFUSED: {iid} appears {len(got)} time(s) under {key}: after the amendment; "
                "exactly one is required. A duplicate id cannot be amended unambiguously."])
    return got[0]


def _schema_error(doc):
    """The plan-schema complaint about `doc`, or None when it satisfies the schema.

    ONE HOME FOR THE SCHEMA, called through `harness_yaml.validate_plan_doc` -- the same function
    `load_plan` uses (FEAT-41 HIGH-1). A copy of the rules here would be a second place for them
    to stop being true, which is the defect this feature keeps finding in its own work.
    """
    try:
        harness_yaml.validate_plan_doc(doc, "the merged plan")
    except harness_yaml.PlanSchemaError as exc:
        return exc
    return None


def _anchor_faults(doc):
    """`  <task id> files: <message>` for every `files:` entry plan_anchors refuses, in order."""
    tasks = (doc.get("tasks") or []) if isinstance(doc, dict) else []
    return [f"  {task.get('id') or '<no id>'} files: {message}"
            for task in tasks if isinstance(task, dict)
            for message in plan_anchors.refusals(task.get("files"))]


def _refuse_illegal_anchors(doc, where):
    """MergeRefusal(2) naming every `files:` entry in `doc`'s tasks that plan_anchors refuses.

    C4: a line-number anchor `path:NN` is refused at WRITE, so it cannot enter a signed plan;
    `check` then only has to resolve the forms that can survive `main` moving. Every offending
    entry is named, with its task, in one refusal — a caller fixing them one at a time is the
    round trip this feature exists to remove."""
    faults = _anchor_faults(doc)
    if faults:
        raise harness_merge.MergeRefusal(
            2, [f"REFUSED: {where} carries a files: entry this tool will not write."] + faults
               + ["  legal forms: path, path#symbol, {path: <p>, quote: <q>} (plan_anchors.py)."])


def _load_mapping_value(path, what):
    try:
        value = harness_yaml.load_file(path)
    except harness_yaml.YamlParseError as exc:
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: cannot load {what} value from {path}: {exc}"])
    if not isinstance(value, dict):
        raise harness_merge.MergeRefusal(5, [f"plan-merge: {what} value must be a mapping"])
    return value


def _load_base_doc(text):
    """The plan on disk as a mapping, or a refusal that names the plan as the side at fault."""
    try:
        doc = harness_yaml.load_str(text, "<base plan>")
    except harness_yaml.YamlParseError as exc:
        raise harness_merge.MergeRefusal(
            5, ["UNPARSEABLE: the plan on disk does not parse, so nothing can be spliced into "
                f"it — {exc}"])
    return doc if isinstance(doc, dict) else {}


def _refuse_governed_agent(action, where):
    """Exit 10 unless the caller is the main session — the identity rule cmd_sign_approval
    documents, shared by every verb that writes the signature in either direction."""
    agent = os.environ.get("HARNESS_AGENT_TYPE") or ""
    if not agent:
        return
    _die(10, f"REFUSED: {agent} may not {action} an approval — only the main session may "
             "(REQ-05/DEC-120).",
         f"This is enforced from inside {where} itself, not only by the calling hook, so no "
         "shell form of this call can reach a write.")


def _locked_plan_update(resolved, transform):
    """Every mutating verb's plan write: harness_merge.locked_update, then -- once its lock is
    released -- the changed-state feedback loop on stderr (FEAT-62 T-03). A refusal raises
    out of locked_update before the relay is reached, so a refused verb stays silent here."""
    harness_merge.locked_update(resolved, transform)
    harness_boundary.relay_changed_state_feedback(resolved)


def _replace_bytes(path, data):
    """Atomic whole-file replace, the same tempfile+os.replace shape locked_update uses."""
    directory = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp_path = tempfile.mkstemp(dir=directory)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.replace(tmp_path, path)
    except BaseException:
        try:
            os.remove(tmp_path)
        except FileNotFoundError:
            pass
        raise


def _restore_plan(resolved, base_bytes):
    """Put the pre-splice bytes back; a failed restore is its own loud line, never silent."""
    try:
        _replace_bytes(resolved, base_bytes)
    except OSError as exc:
        return [f"  AND the plan splice could NOT be restored in {resolved} ({exc}); the plan "
                "carries the amendment with no judgement — restore it from git before anything "
                "else."]
    return [f"  the plan splice was restored byte for byte in {resolved}; nothing landed."]


def _die(code, *lines):
    """Print a refusal to stderr and exit. Collapses the print/exit pairs that made
    `cmd_amend` an ABC outlier without changing a single message."""
    for line in lines:
        print(line, file=sys.stderr)
    sys.exit(code)
