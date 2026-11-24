"""Destination, reload, schema and lock guards shared by every verb; the one write route. (FEAT-70)"""
import contextlib
import os
import re
import sys

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


def _pending_replay_lines(pending):
    """The two lines for a harness_merge.JournalPending raised by a failed replay: the earlier
    transaction stays pending, and this command's own change was never written."""
    return [f"plan-merge: completing the pending intent journal {pending.journal} failed: "
            f"{type(pending.cause).__name__}: {pending.cause}",
            "  this command did not write its change; the journaled transaction stays pending "
            "and the next plan-merge or feature.json write completes it."]


def _recover_plan_journals(resolved):
    """harness_merge.recover_journals(resolved), every failure of its real classes reported as a
    MergeRefusal. A refusal (JOURNAL UNREADABLE or DIVERGED, exit 5; LOCKED, exit 6) passes
    through. A failed replay is committed-pending and says so (exit 2). An OSError (listing the
    directory, opening a lock) or a ValueError (a malformed HARNESS_LOCK_TIMEOUT_SECONDS) came
    before any member was written — harness_merge raises every later OSError as JournalPending
    — so "nothing changed" is true of it (exit 2). Anything else is a bug and propagates as a
    traceback rather than be stamped "nothing changed"; a journal it leaves stays on disk."""
    try:
        harness_merge.recover_journals(resolved)
    except harness_merge.JournalPending as pending:
        raise harness_merge.MergeRefusal(2, _pending_replay_lines(pending)) from pending
    except harness_merge.MergeRefusal:
        raise
    except (OSError, ValueError) as exc:
        raise harness_merge.MergeRefusal(
            2, [f"plan-merge: recovering the intent journal for {resolved} failed: "
                f"{type(exc).__name__}: {exc}",
                "  no file was changed; this command wrote nothing."]) from exc


def _resolve_plan(file_path, recover=True):
    """require_destination on the RESOLVED path, then — unless `recover` is false — the
    completion of any intent journal naming the plan; or print the refusal and exit its code.

    Extracted so every verb shares ONE destination guard. A second copy would be a second
    place for exit 9 to stop being true.

    WHY MUTATING VERBS RECOVER HERE (FEAT-2488). record-amendments and amend refuse in a
    lock-free preflight — a field already at `now`, a stale --expect-sha256 — before they reach
    any harness_merge write, so recovery inside the core's writes alone would leave a torn
    amendment pair in place on the most natural next invocation: the operator re-running the
    verb. harness_merge.recover_journals stays the one recovery entry point; this only calls
    it. Read-only invocations — `check`, and `amend --show` — pass recover=False. A recovery
    failure of the boundary's own classes prints its refusal, never a Traceback."""
    try:
        resolved = harness_merge.require_destination(
            file_path,
            PLAN_TAIL,
            "a plan.yaml under a features directory",
            [
                "  a legal path looks like .harness/features/FEAT-NN-slug/plan.yaml or",
                "  .harness/<repo>/features/FEAT-NN-slug/plan.yaml.",
                "  This tool merges plan.yaml only.",
            ],
        )
        if recover:
            _recover_plan_journals(resolved)
        return resolved
    except harness_merge.MergeRefusal as refusal:
        _die(refusal.code, *refusal.lines)


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
    no board declared (github.board null) is NOT a licence to accept anything: the mandate still
    applies, because MANDATED_STATIONS is what a declaration is checked against in the first
    place. A missing or invalid config is NOT a null board: it exits 2 naming the loader's
    diagnosis (FEAT-2297), before any lock — never a fallback to the mandate.

    THE ROOT PROBE NAMES THE MANIFEST, NEVER THE `.harness` DIRECTORY. A probe for the directory
    resolves $HOME as a root in the global install — B-7 verbatim — and
    test-check-plan-routes.py's case_20 asserts that no copy of this idiom regresses. The walk
    starts from the plan.yaml's own directory rather than from this script's location, because
    the vocabulary that governs a write belongs to the checkout being written to, not to
    whichever checkout happens to be running the tool.
    """
    root = _harness_root(os.path.dirname(os.path.abspath(resolved)))
    try:
        board = gh_board.load_board(root) if root is not None else None
    except artifact_accessors.FleetError as error:
        _die(2, f"plan-merge: {error}")
    stations = factory_config.station_names(board) if board is not None else None
    if stations is None:
        stations = factory_config.MANDATED_STATIONS
    return tuple(stations) + factory_config.TERMINAL_STATIONS


def _refuse_illegal_station(station, legal):
    """Exit 4, naming the offending value and every legal one.

    CALLED BEFORE THE LOCK IS TAKEN, deliberately: a refused value must never open the file, so
    a typo cannot contend for the lock or leave a partial write behind."""
    _die(4, f"plan-merge: {station!r} is not a legal station — expected one of: "
         + ", ".join(legal))


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



def _refuse_illegal_amendment(base_doc, reloaded):
    """DO NO HARM: hold an amended plan to the schema only when the BASE satisfied it. A plan
    mid-authoring legitimately does not, and refusing to amend it would make the verb useless
    exactly where it is needed most. One refusal for `amend` and `record-amendments`. (FEAT-70)"""
    if _schema_error(base_doc) is None:
        err = _schema_error(reloaded)
        if err:
            raise harness_merge.MergeRefusal(
                8, [f"plan-merge: the amended plan would not be legal — {err}"])

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


# What a write to process stdio can raise (validate c3 MF-11): a real stream fails with the
# OSError family (a broken pipe; io.UnsupportedOperation subclasses OSError and ValueError), a
# closed one with ValueError, and a missing one — None, its fd closed at exec — or a replacement
# without the attribute with AttributeError. A tuple, never Exception (FEAT-63's broad-catch
# census): a replacement object raising outside it is its caller's contract breach.
_STDIO_FAULTS = (OSError, ValueError, AttributeError)
_STDIO_FDS = {"stdout": 1, "stderr": 2}


def _silence(stream, expected_fd):
    """Point fd `expected_fd` at os.devnull when it is `stream`'s own descriptor, so the bytes
    buffered stdio still holds — which interpreter finalization flushes again, exiting 120 when
    that flush fails too (validate c2 MF-9) — drain into nothing. ONLY then: a replacement
    stream on a caller-owned descriptor is never touched (validate c3), and a stream with no
    fileno, a closed one or one whose fileno() is unsupported has no process descriptor to
    drain."""
    with contextlib.suppress(*_STDIO_FAULTS):
        fileno = getattr(stream, "fileno", None)
        if fileno is None or fileno() != expected_fd:
            return
        devnull = os.open(os.devnull, os.O_WRONLY)
        try:
            os.dup2(devnull, expected_fd)
        finally:
            os.close(devnull)


def _emit(name, write):
    """THE one stdio emission path (validate c3 MF-11) — receipts, relay, notes, refusals:
    `write(stream)` against sys.<name> ("stdout" or "stderr"), then a flush. None when it
    landed, else what stopped it, as text — never raised, so no state of the stream can change
    the exit code.

    A None stream (its fd closed at exec) is never written to: print(..., file=None) is
    CPython's sys.stdout, so a missing stderr would misroute into the receipts. A fault of
    _STDIO_FAULTS is returned; when the stream can no longer flush either, it is _silence'd so
    finalization cannot fail on it. A fault of `write`'s own work leaves a stream that still
    flushes as it is, so the note that follows can reach it."""
    stream = getattr(sys, name)
    if stream is None:
        return f"sys.{name} is None"
    try:
        write(stream)
        stream.flush()
        return None
    except _STDIO_FAULTS as exc:
        fault = f"{type(exc).__name__}: {exc}"
    try:
        stream.flush()
    except _STDIO_FAULTS:
        _silence(stream, _STDIO_FDS[name])
    return fault


def _print_lines(lines):
    """An _emit `write`: each line printed to the stream it is given."""
    def write(stream):
        for line in lines:
            print(line, file=stream)
    return write


def _note_on_stderr(line):
    """One best-effort stderr line through _emit; a stderr that cannot take it is the end."""
    _emit("stderr", _print_lines([line]))


def _relay_after_commit(path):
    """The changed-state feedback for a write that has committed, advisory only: the write has
    landed, so a failure here is one stderr line (itself best-effort, _note_on_stderr) and
    never a refusal, a traceback or a nonzero exit. relay_changed_state_feedback prints to
    sys.stderr itself, so it runs inside _emit("stderr"): never with stderr None, where its rows
    would print to stdout; and its faults — a broken pipe, a closed stream, or anything of the
    tuple changed_state_feedback does not absorb — are returned, never raised."""
    fault = _emit("stderr", lambda _stream: harness_boundary.relay_changed_state_feedback(path))
    if fault is not None:
        _note_on_stderr(f"plan-merge: changed-state feedback after the committed write failed: "
                        f"{fault}")


def _print_receipts(*lines):
    """A committed write's receipts, one per line on stdout, flushed, through _emit. The write
    has landed, so a stdout that cannot take them — None, closed or a broken pipe — costs the
    receipts, never the outcome: one best-effort stderr line says the write landed, and the
    verb still exits 0."""
    fault = _emit("stdout", _print_lines(lines))
    if fault is not None:
        _note_on_stderr(f"plan-merge: the write landed, but its receipts could not be printed: "
                        f"{fault}")


def _locked_plan_update(resolved, transform):
    """Every mutating verb's plan write: harness_merge.locked_update, then -- once its lock is
    released -- the changed-state feedback loop on stderr (FEAT-62 T-03), advisory after the
    commit (_relay_after_commit). A refusal raises out of locked_update before the relay is
    reached, so a refused verb stays silent here."""
    harness_merge.locked_update(resolved, transform)
    _relay_after_commit(resolved)


def _die(code, *lines):
    """Print a refusal to stderr and exit `code`. Collapses the print/exit pairs that made
    `cmd_amend` an ABC outlier without changing a single message. The lines go through _emit,
    because a refusal can follow a published journal (committed-pending, exit 2): no state of
    stderr may turn that code into a traceback's 1 or move the lines onto stdout."""
    _emit("stderr", _print_lines(lines))
    sys.exit(code)
