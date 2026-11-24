"""`record-amendments`: a lead digest's amendments spliced and ledgered as one act. (FEAT-70)"""
import contextlib
import json
import os
import sys
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import amendment_contract
import feature_json_write
import harness_boundary
import harness_merge
from plan_merge.guards import (
    _die, _pending_replay_lines, _refuse_illegal_amendment, _reload_or_refuse, _resolve_plan,
    _sole_item,
)
from plan_merge.text import (
    _field_block, _item_by_id, _item_range, _render_field, _structured_field_lines,
)
from plan_merge.panel import _lead_digest

# ---------------------------------------------------------------------------
# BUG-1716 — `record-amendments`: the engineering lead's in-build corrections to a signed
# task's HOW, transcribed from its digest in ONE command (D-04). BUG-285 spent three blocked
# runs, three product amendment runs and three operator round-trips applying three
# recommendations the operator adopted every time; this verb is that transcript.
#
# IT IS A COMPARE-AND-SPLICE, NOT A WRITE. Every entry names `was`; the current field must
# equal it (parsed value, so YAML presentation is not the question) or the whole invocation
# refuses — before the lock for a fast answer, under the lock for the guarantee. A rerun is
# therefore refused by construction: the field now equals `now`, not `was`. One judgement
# per entry lands in feature.json; `signed_task_hashes` is NOT revised, because the hash is
# what lets INV-40 tell a ledgered amendment from an unrecorded edit.
def _amendment_entry(raw, index):
    """One validated, normalized {task, field, was, now, reason}, or a MergeRefusal(5) naming
    the index and the bad key. The rules are amendment_contract's — the same ones
    validate-digest.py graded the lead's return with, so a return that validated records."""
    if not isinstance(raw, dict):
        raise harness_merge.MergeRefusal(5, [f"plan-merge: amendments[{index}] is not a mapping."])
    faults = amendment_contract.entry_errors(raw, index)
    if faults:
        raise harness_merge.MergeRefusal(5, [f"plan-merge: {msg}" for msg in faults])
    return amendment_contract.normalized(raw)


def _digest_amendments(digest):
    """The digest's amendments, validated and refused on a repeated (task, field)."""
    raw = digest.get("amendments")
    if not isinstance(raw, list) or not raw:
        raise harness_merge.MergeRefusal(
            2, ["plan-merge: the digest carries no amendments to record — `amendments:` is "
                "absent or empty, so there is nothing to transcribe."])
    entries = [_amendment_entry(item, i) for i, item in enumerate(raw)]
    targets = [(e["task"], e["field"]) for e in entries]
    repeated = next((t for i, t in enumerate(targets) if t in targets[:i]), None)
    if repeated:
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: {repeated[0]}.{repeated[1]} is amended twice in one digest — one "
                "target, one entry; the second would overwrite the first's `was`."])
    return entries


def _amendment_against_plan(entry, plan_doc, what):
    """Refuse unless `entry.task` exists in `plan_doc` and its field equals `entry.was`."""
    task = _item_by_id(plan_doc.get("tasks") or [], entry["task"])
    if task is None:
        raise harness_merge.MergeRefusal(
            3, [f"plan-merge: {entry['task']} is not a task in the plan ({what}); an "
                "amendment corrects an EXISTING task and never adds one."])
    current = task.get(entry["field"])
    if current != entry["was"]:
        already = (" — the field already equals `now`, so this amendment was recorded before"
                   if current == entry["now"] else "")
        raise harness_merge.MergeRefusal(
            6, [f"plan-merge: {entry['task']}.{entry['field']} does not equal the amendment's "
                f"`was` ({what}){already}.",
                f"  current: {current!r}", f"  was:     {entry['was']!r}",
                "  record-amendments is a compare-and-splice; re-read the field and re-derive."])


def _amendment_judgement(entry, at):
    return {"at": at, "by": "harness-orchestrator", "kind": "amendment",
            "decision": f"{entry['task']}.{entry['field']}", "reason": entry["reason"]}


def _distinct_instants(count):
    """`count` strictly increasing ISO instants. `overrule-amendment` selects an entry by its
    exact `at`, so two amendments recorded in one act must not share one; microseconds keep
    them apart and a same-tick collision is bumped rather than left equal."""
    out, last = [], None
    for _ in range(count):
        now = datetime.now(timezone.utc)
        if last is not None and now <= last:
            now = last + timedelta(microseconds=1)
        out.append(now.isoformat(timespec="microseconds"))
        last = now
    return out


def _splice_amendments(cur, entries):
    """The plan lines with every entry's `now` spliced over its field block, task by task.
    Entries are applied in digest order; each splice re-locates its field because earlier
    splices move lines. Text fields keep the original form (`|` body reused); a files list is
    rendered the way `amend --yaml-value` renders one. Nothing outside the named field blocks
    is re-rendered."""
    for entry in entries:
        start, end, indent = _item_range(cur, "tasks", entry["task"])
        if start is None:
            raise harness_merge.MergeRefusal(
                3, [f"plan-merge: {entry['task']} vanished from tasks: under the lock."])
        located = _field_block(cur, start, end, indent, entry["field"])
        if located is None:
            raise harness_merge.MergeRefusal(
                4, [f"plan-merge: {entry['task']} carries no {entry['field']}: field under "
                    "the lock; an amendment replaces a field and never adds one."])
        first, last, field_indent = located
        if entry["field"] == "files":
            rendered = _structured_field_lines(field_indent, "files", entry["now"])
        else:
            rendered = _render_field(field_indent, entry["field"], entry["now"], cur[first:last])
        cur = cur[:first] + rendered + cur[last:]
    return cur


def _amended_plan_bytes(base_bytes, entries):
    """The spliced plan bytes, every guard applied, or a refusal. Pure: no write here."""
    base_doc = _reload_or_refuse(base_bytes)
    # THE LOAD-BEARING CHECK: `was` still equals the field under the lock.
    for entry in entries:
        _amendment_against_plan(entry, base_doc, "under the lock")
    lines = base_bytes.decode("utf-8").splitlines(keepends=True)
    spliced = "".join(_splice_amendments(lines, entries)).encode("utf-8")
    reloaded = _reload_or_refuse(spliced)
    _verify_amendments_landed(reloaded, entries)
    _refuse_illegal_amendment(base_doc, reloaded)
    if reloaded.get("approval") != base_doc.get("approval"):
        raise harness_merge.MergeRefusal(
            8, ["plan-merge: the splice touched approval: — REFUSING (DEC-120)."])
    return spliced


def _verify_amendments_landed(reloaded, entries):
    for entry in entries:
        got = _sole_item(reloaded, "tasks", entry["task"]).get(entry["field"])
        if got != entry["now"]:
            raise harness_merge.MergeRefusal(
                5, [f"plan-merge: {entry['task']}.{entry['field']} reloads as {got!r}, not the "
                    "amendment's `now` — REFUSING to write a splice that lies."])


def _ledger_transform(feature_json, judgements):
    """The ledger side of the pair: feature.json's bytes with `judgements` appended to its
    `judgements` ledger, or a refusal when the file vanished since the preflight."""
    def transform(base):
        doc = feature_json_write.parse_doc(base, feature_json)
        if doc is None:
            raise harness_merge.MergeRefusal(
                feature_json_write.SCHEMA_REFUSAL_CODE,
                [f"REFUSED: {feature_json} vanished between the preflight and the write."])
        ledger = doc.get("judgements")
        doc["judgements"] = (list(ledger) if isinstance(ledger, list) else []) + judgements
        return json.dumps(doc, indent=2) + "\n"

    return transform


def _record_amendments_locked(resolved, feature_json, entries):
    """record-amendments' two writes: the digest's entries spliced, one judgement each."""
    judgements = [_amendment_judgement(e, at)
                  for e, at in zip(entries, _distinct_instants(len(entries)))]
    write_plan_and_ledger(resolved, feature_json,
                          lambda base: _amended_plan_bytes(base, entries), judgements)


def _pair_failure(exc, resolved, feature_json):
    """The refusal reporting a failed pair write, decided by the core's exception type alone —
    never by looking at the disk. `exc` is a JournalPending, a MergeRefusal, or an OSError or
    ValueError raised before the journal was published."""
    if isinstance(exc, harness_merge.JournalPending) and exc.replay:
        return harness_merge.MergeRefusal(2, _pending_replay_lines(exc))
    if isinstance(exc, harness_merge.JournalPending):
        return harness_merge.MergeRefusal(2, [
            f"plan-merge: the write to {resolved} and {feature_json} failed after its intent "
            f"journal was published: {type(exc.cause).__name__}: {exc.cause}",
            f"  the transaction is journaled in {exc.journal}; the next plan-merge or "
            "feature.json write completes it."])
    if isinstance(exc, harness_merge.MergeRefusal):
        return harness_merge.MergeRefusal(exc.code, list(exc.lines) + ["  nothing was written."])
    return harness_merge.MergeRefusal(
        2, [f"plan-merge: the ledger write to {feature_json} failed: {type(exc).__name__}: {exc}",
            "  nothing was written."])


def _relay_after_commit(ledger_path):
    """The committed pair's changed-state feedback, advisory only: the write has landed, so a
    failure here is one stderr line (itself best-effort) and never a refusal.
    changed_state_feedback already absorbs its subprocess's (OSError, SubprocessError); what is
    left is printing to stderr — OSError on a broken pipe, ValueError on a closed stream."""
    try:
        harness_boundary.relay_changed_state_feedback(ledger_path)
    except (OSError, ValueError) as exc:
        with contextlib.suppress(OSError):
            print("plan-merge: changed-state feedback after the committed write failed: "
                  f"{type(exc).__name__}: {exc}", file=sys.stderr)


def write_plan_and_ledger(resolved, feature_json, splice, judgements):
    """The plan splice and its ledger judgements as ONE journaled transaction:
    harness_merge.locked_pair_update with plan.yaml as the primary, replaced before
    feature.json, under plan.yaml.lock then feature.json.lock — the one lock order, never
    reversed. The ledger side keeps feature.json's schema non-regression check
    (feature_json_write.schema_checked_transform).

    Both transforms run before anything is written, so a refusal or error there — a stale
    `was`, a schema regression, LOCKED, an unopenable lock — leaves both files as they were,
    and the refusal says nothing was written. There is NO compensation path. Once the intent
    journal is published the transaction is committed-pending: a failure after that point is
    reported as journaled, and the next plan-merge or feature.json write naming either file
    completes it. A failed replay of an EARLIER journal is committed-pending too, and this
    call's own change was never attempted. The outcome is read from the core's exception
    type, never from the disk. The handled classes are the boundary's real ones —
    JournalPending, MergeRefusal, then OSError and ValueError (json, UTF-8 and base64 faults,
    the pair's own ValueError); anything else is a bug and propagates as a traceback, a
    published journal kept on disk for the next write to roll forward.

    The changed-state feedback (FEAT-62 T-03) runs once, for the ledger, after the commit, when
    both files are already dirty; a second --changed run for the plan would only repeat it. It
    is advisory: the write has landed, so a feedback failure is noted on stderr and the verb
    still prints its receipts and exits 0.

    LEDGER-FIRST STAYS REJECTED (BUG-1716 validate c0 V-01, c1 V-01). The ledger once landed
    first, so a plan write that failed afterwards left a judgement for an amendment the plan
    never carried: the audit trail lying in the direction nothing detects. The journal now
    rolls either order forward. Plan-first still decides what is left if a journal is ever
    removed by hand before completion: an unledgered plan edit, which INV-40 reports."""
    try:
        ledger_path, ledger = feature_json_write.schema_checked_transform(
            feature_json, _ledger_transform(feature_json, judgements))
        harness_merge.locked_pair_update(resolved, splice, ledger_path, ledger)
    except (harness_merge.JournalPending, harness_merge.MergeRefusal, OSError, ValueError) as exc:
        raise _pair_failure(exc, resolved, feature_json) from exc
    _relay_after_commit(ledger_path)


def _record_amendments_preflight(resolved, feature_json, entries):
    """Every refusal that needs no lock: each entry against the plan as it is now, and the
    ledger's existence and shape. A refusal here leaves both documents byte-identical."""
    with open(resolved, "rb") as fh:
        plan_doc = _reload_or_refuse(fh.read())
    for entry in entries:
        _amendment_against_plan(entry, plan_doc, "preflight")
    if not os.path.isfile(feature_json):
        raise harness_merge.MergeRefusal(
            2, [f"plan-merge: {feature_json} does not exist, so the amendment judgements have "
                "nowhere to go — REFUSING to amend the plan without its ledger."])
    with open(feature_json, "rb") as fh:
        if feature_json_write.parse_doc(fh.read(), feature_json) is None:
            raise harness_merge.MergeRefusal(
                feature_json_write.SCHEMA_REFUSAL_CODE, [f"plan-merge: {feature_json} is empty."])


def cmd_record_amendments(args):
    """`record-amendments --file <plan.yaml> --digest <eng-lead digest.md>` (BUG-1716 T-04)."""
    resolved = _resolve_plan(args.file)
    feature_json = os.path.join(os.path.dirname(resolved), "feature.json")
    try:
        entries = _digest_amendments(_lead_digest(args.digest))
        _record_amendments_preflight(resolved, feature_json, entries)
        _record_amendments_locked(resolved, feature_json, entries)
    except harness_merge.MergeRefusal as refusal:
        _die(refusal.code, *refusal.lines)
    for entry in entries:
        print(f"AMENDED {entry['task']}.{entry['field']} judgement=amendment")
    print(f"APPLIED {resolved}")
    print(f"APPLIED {feature_json}")
    sys.exit(0)
