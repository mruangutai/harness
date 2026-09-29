"""`delete-items`: the verb the add-only property left missing. (FEAT-70)"""
import sys

import harness_merge
import harness_yaml
from plan_merge.stations import APPROVAL_RESET_LINE, _maybe_reset_approval
from plan_merge.text import (
    DASH_RE, _index_list_items, _index_top_keys, _item_delete_end, _item_id, _splice_out,
)
from plan_merge.guards import (
    _die, _locked_plan_update, _reload_or_refuse, _resolve_plan, _schema_error,
)

# ---------------------------------------------------------------------------
# `delete-items` — the verb the add-only property left missing.
#
# `apply` is add-only by promise, `amend` replaces ONE field of ONE existing item, and FEAT-41
# T-09 (#1045) denies every editor and shell write of a plan.yaml to every author. Each is
# correct alone; together they left an operator-ruled SCOPE REMOVAL with no route at all — not
# a permission anybody could be granted, a verb nobody had written. This is the same shape
# BUG-1128 fixed for correcting a field, one step further: a rule shipped without reconciling
# what it makes impossible.
#
# IT IS THE SAME WRITER AS EVERY OTHER VERB. The lock, the byte-level splice, the
# reload-or-refuse and the do-no-harm schema check are what fix #628 and they are properties of
# the TOOL; add-only is a property of two verbs. So this one reuses all four rather than
# growing a second write path, and it never re-renders a line: it FILTERS lines, so every
# survivor is byte-identical and a review diff shows deletions only.
#
# WHAT IT DELIBERATELY CANNOT DO: delete by predicate (only ids, named one at a time), delete a
# field (that is `amend`), delete `approval:` (the main session's alone, DEC-120), or delete
# anything quietly — an unknown id, a repeated id, or a surviving `depends_on` edge naming the
# doomed task is a loud non-zero refusal, and a refused call writes nothing.
DELETABLE_KEYS = ("tasks", "decisions")


def _refuse_empty_request(requested, reason):
    """Refuse a call that names nothing to delete, or gives no reason for deleting it.

    `--reason` IS REQUIRED AND IS NEVER WRITTEN. It exists so a refusal can name why a deletion
    was asked for and so a caller cannot delete by reflex; an empty one defeats both, so it is
    refused rather than accepted as a formality.
    """
    if not requested:
        raise harness_merge.MergeRefusal(
            2, ["plan-merge: delete-items needs at least one --task or --decision.",
                "  A call that names nothing to delete is a write with no subject, and "
                "reporting success for it would teach the caller that a typo'd flag worked."])
    if not reason.strip():
        raise harness_merge.MergeRefusal(
            2, ["plan-merge: --reason must not be empty.",
                "  It is never written into the plan; it exists so a deletion cannot be made "
                "by reflex and so a refusal can name why one was asked for."])


def _refuse_repeated_id(requested):
    """Refuse an id given twice, NEVER a set union.

    Deleting one item twice cannot be what was meant, and de-duplicating it silently would
    swallow the far likelier explanation — that one of the other ids the caller typed is wrong.
    """
    seen = set()
    for _key, iid in requested:
        if iid in seen:
            raise harness_merge.MergeRefusal(
                2, [f"plan-merge: {iid} was named twice on the command line.",
                    "  Deleting one item twice cannot be what was meant, and accepting it "
                    "would hide a typo in one of the other ids."])
        seen.add(iid)


def _requested_deletions(args):
    """[(key, id)] in command-line order, or a MergeRefusal(2) naming the offending value.

    CHECKED BEFORE THE LOCK IS TAKEN, the discipline `_refuse_illegal_station` states in full:
    a refused command line must never open the file, so a typo cannot contend for the lock or
    leave a partial write behind.
    """
    requested = [("tasks", tid) for tid in args.task]
    requested += [("decisions", did) for did in args.decision]
    _refuse_empty_request(requested, args.reason)
    _refuse_repeated_id(requested)
    return requested


def _item_delete_ranges(lines, key_range, items, key):
    """[(start, end)] per parsed item of `key`, in text order, or a refusal.

    THE ALIGNMENT IS `apply_merge`'S OWN, AND SO IS ITS REFUSAL: one dash per item is what lets
    a text range and a parsed item be zipped, and a delete that mis-aligned them would remove
    the wrong item's bytes while reporting the id it was asked for.
    """
    item_ranges = _index_list_items(lines, key_range)
    if len(item_ranges) != len(items):
        raise harness_merge.MergeRefusal(
            5, [f"UNPARSEABLE: could not align text ranges with parsed items for '{key}' — "
                "the block's formatting is not one dash per item."])
    return [
        (start, _item_delete_end(lines, start, end, DASH_RE.match(lines[start]).group(1)))
        for start, end in item_ranges
    ]


def _locate_one(present, key, iid):
    """The index of `iid` in `present`, or the refusal that names the concrete miss.

    AN ABSENT ID IS NEVER A NO-OP (exit 3): a delete that reported success for an id it could
    not find would tell a caller who mistyped one that their scope removal had happened. The id
    list is SCOPED TO `key`, the precedent `_task_status_line` set — offering decision ids for a
    `--task` miss invites a retry that fails for an unrelated reason.

    A DUPLICATE ID IN THE PLAN IS ALSO A REFUSAL (exit 5), `_sole_item`'s rule verbatim: which
    of two items carrying one id was meant cannot be known, and binding to the first match
    silently is what the code-reviewer found in `amend`'s cycle 0.
    """
    hits = [index for index, pid in enumerate(present) if pid == iid]
    if not hits:
        raise harness_merge.MergeRefusal(
            3, [f"plan-merge: {iid} is not under {key}: in this plan, so there is nothing to "
                "delete — REFUSING, rather than reporting a deletion that did not happen.",
                f"  {key}: carries: {', '.join(str(p) for p in present) or '(none)'}"])
    if len(hits) != 1:
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: {iid} appears {len(hits)} time(s) under {key}:; exactly one is "
                "required. A duplicate id cannot be deleted unambiguously."])
    return hits[0]


def _deletion_ranges(lines, base_doc, requested):
    """The text ranges every requested id occupies, or the refusal that names the miss."""
    _l, _order, key_ranges, _pre = _index_top_keys("".join(lines))
    ranges = []
    for key in DELETABLE_KEYS:
        wanted = [iid for k, iid in requested if k == key]
        if not wanted:
            continue
        items = base_doc.get(key) if isinstance(base_doc.get(key), list) else []
        present = [_item_id(item) for item in items]
        item_ranges = (_item_delete_ranges(lines, key_ranges[key], items, key)
                       if key in key_ranges else [])
        ranges.extend(item_ranges[_locate_one(present, key, iid)] for iid in wanted)
    return ranges


def _task_edges(task, doomed):
    """`<tid> depends_on <entry>` for every doomed id this ONE task names, or [] for none.

    A DOOMED TASK CONTRIBUTES NOTHING. A task being deleted in the same call may name another
    being deleted in the same call — that is a scope removal, not a dangling edge, and counting
    it would make the verb unable to remove a dependent pair, which is the ordinary case.

    A `depends_on` THAT IS NOT A LIST IS NOT READ AS ONE, for `harness_yaml._depends_on_entries`'
    own measured reason: iterated as-is, a bare string walks CHARACTERS and reports phantom ids.
    Nothing can be proven dangling from a malformed field, so this reports none and leaves the
    shape complaint to the schema, which already owns it.
    """
    if not isinstance(task, dict) or _item_id(task) in doomed:
        return []
    entries = task.get("depends_on")
    if not isinstance(entries, list):
        return []
    tid = _item_id(task)
    return [f"{tid} depends_on {entry}" for entry in entries if str(entry) in doomed]


def _dangling_edges(base_doc, doomed):
    """Every edge the deletion would leave pointing at a task that is no longer there."""
    return [edge
            for task in (base_doc.get("tasks") or [])
            for edge in _task_edges(task, doomed)]


def _refuse_dangling_depends_on(base_doc, requested):
    """Refuse a deletion that would leave a SURVIVING task's `depends_on` naming a deleted one.

    ISSUE #201's OWN DEFECT, FROM THE OTHER SIDE. `harness_yaml._validate_plan_depends_on`
    refuses a plan whose edge names an absent task, so the do-no-harm schema check below would
    also catch this — but ONLY when the base was already schema-legal, and do-no-harm
    deliberately skips it for a plan mid-authoring, which is most plans a scope removal is run
    against. The schema is therefore not a substitute for this check: it is a second net with a
    hole exactly where a delete is most likely to be used. This check also names the EDGE,
    which the schema's own complaint cannot do, because it fires on the finished document
    rather than on the request.
    """
    doomed = {iid for key, iid in requested if key == "tasks"}
    dangling = _dangling_edges(base_doc, doomed) if doomed else []
    if not dangling:
        return
    raise harness_merge.MergeRefusal(
        4, ["REFUSED: this deletion would leave a dangling depends_on edge — REFUSING to "
            "write it.",
            f"  {', '.join(dangling)}",
            "  amend the surviving task's depends_on first, or delete that task in the "
            "same call. A plan whose edge names an absent task is issue #201's defect, and "
            "a delete verb that creates one is worse than no delete verb."])


def _survivors(base_doc, key, requested):
    doomed = {iid for k, iid in requested if k == key}
    return [item for item in (base_doc.get(key) or []) if _item_id(item) not in doomed]


def _verify_deletion(spliced_bytes, base_doc, requested):
    """Refuse rather than write a deletion that does not reload as the one that was asked for.

    IT COMPARES WHOLE PARSED ITEMS, NOT IDS, for the reason `_verify_amend` states: a boundary
    error leaves a document that parses perfectly. A range one line long takes the next item's
    `- id:` line and MERGES two items into one; a range one line short leaves an orphaned field
    on the neighbour. An id-only check sees neither — the first because the merged item still
    carries the survivor's id, the second because no id moved at all.

    BOTH LISTS ARE CHECKED even when only one was touched, because a mis-computed range in
    `tasks:` can only be proven not to have reached `decisions:` by looking.
    """
    reloaded = _reload_or_refuse(spliced_bytes)
    if not isinstance(reloaded, dict):
        raise harness_merge.MergeRefusal(
            5, ["UNPARSEABLE: the pruned plan is not a mapping — REFUSING to write it."])
    for key in DELETABLE_KEYS:
        want = _survivors(base_doc, key, requested)
        got = reloaded.get(key) or []
        if got == want:
            continue
        want_ids = [_item_id(item) for item in want]
        got_ids = [_item_id(item) for item in got]
        detail = (f"  expected ids: {want_ids!r}\n  reloaded ids: {got_ids!r}"
                  if want_ids != got_ids else
                  "  the ids match, so a SURVIVOR's own fields changed: that is a boundary "
                  "error, which a check on ids alone cannot see.")
        raise harness_merge.MergeRefusal(
            5, [f"REFUSED: '{key}' does not reload as the deletion that was computed — "
                "REFUSING to write it.", detail])
    return reloaded


def _deleted_bytes(base_bytes, requested, receipt=None):
    """The plan's bytes with every requested item's lines removed, or a refusal.

    THE WHOLE EDIT AS A FUNCTION OF BYTES, `_signed_approval_bytes`'s shape: the verb's lock
    plumbing stays three lines and this stays reachable from a unit test, which is the remedy
    `_require_locked_hash` and `_verify_amend` both got for the same reason. `receipt`, when
    given, is a dict that learns whether the approval was reset (C4).
    """
    raw = base_bytes.decode("utf-8")
    try:
        base_doc = harness_yaml.load_str(raw, "<base plan>")
    except harness_yaml.YamlParseError as exc:
        raise harness_merge.MergeRefusal(
            5, ["UNPARSEABLE: the plan on disk does not parse, so delete-items cannot tell "
                "which bytes belong to the items it was asked to remove.",
                f"  {exc}"])
    base_doc = base_doc if isinstance(base_doc, dict) else {}
    lines = raw.splitlines(keepends=True)
    ranges = _deletion_ranges(lines, base_doc, requested)
    _refuse_dangling_depends_on(base_doc, requested)
    spliced = _reset_after_deletion(_splice_out(lines, ranges), base_doc, requested, receipt)
    reloaded = _verify_deletion(spliced, base_doc, requested)
    # DO NO HARM, the rule `apply` and `amend` both hold to: the result is held to the plan
    # schema only when the BASE satisfied it. A plan mid-authoring legitimately does not, and
    # refusing to prune it would make this verb useless exactly where scope is still moving.
    if _schema_error(base_doc) is None:
        err = _schema_error(reloaded)
        if err is not None:
            raise harness_merge.MergeRefusal(
                5, ["ILLEGAL PLAN: this deletion would make a legal plan illegal — REFUSING "
                    "to write it.",
                    f"  {err}",
                    "  the base satisfied the plan schema and the pruned result does not, so "
                    "the deletion itself is what the schema refuses."])
    return spliced


def _reset_after_deletion(spliced, base_doc, requested, receipt):
    """DELETING A TASK CHANGES THE TASK SET (C4): an approved plan is reset to pending. A
    decision's removal is not the task set and leaves the signature standing."""
    doomed_tasks = [iid for key, iid in requested if key == "tasks"]
    text, reset = _maybe_reset_approval(spliced.decode("utf-8"), base_doc, "delete-items",
                                        doomed_tasks)
    if receipt is not None:
        receipt["reset"] = reset
    return text.encode("utf-8")


def cmd_delete_items(args):
    """Delete whole tasks and decisions by id, under the same lock every other verb takes."""
    resolved = _resolve_plan(args.file)
    try:
        requested = _requested_deletions(args)
    except harness_merge.MergeRefusal as refusal:
        _die(refusal.code, *refusal.lines)

    receipt = {}

    def transform(base_bytes):
        if base_bytes is None:
            raise harness_merge.MergeRefusal(
                3, [f"plan-merge: {resolved} does not exist, so there is nothing to delete."])
        return _deleted_bytes(base_bytes, requested, receipt)

    try:
        _locked_plan_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)
    for key, iid in requested:
        print(f"DELETED {key}:{iid}")
    # THE REASON IS PRINTED, NEVER WRITTEN. The plan carries no record of it by design — the
    # operator's ruling lives in the feature's own notes — so the receipt is where it has to
    # appear for a run log to say why ten items went.
    print(f"DELETED-ITEMS {len(requested)} from {resolved} — reason: {args.reason}")
    if receipt.get("reset"):
        print(APPROVAL_RESET_LINE)
    print(f"APPLIED {resolved}")
    sys.exit(0)
