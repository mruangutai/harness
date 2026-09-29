"""`record-amendments`: a lead digest's amendments spliced and ledgered as one act. (FEAT-70)"""
import json
import os
import sys
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import amendment_contract
import feature_json_write
import harness_merge
from plan_merge.guards import (
    _die, _reload_or_refuse, _replace_bytes, _resolve_plan, _restore_plan, _schema_error,
    _sole_item,
)
from plan_merge.text import _field_block, _item_range, _render_field, _structured_field_lines
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
    task = next((t for t in (plan_doc.get("tasks") or [])
                 if isinstance(t, dict) and t.get("id") == entry["task"]), None)
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
    if _schema_error(base_doc) is None:
        err = _schema_error(reloaded)
        if err:
            raise harness_merge.MergeRefusal(
                8, [f"plan-merge: the amended plan would not be legal — {err}"])
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


def _record_amendment_judgements(feature_json, judgements):
    """Append `judgements` to feature.json's ledger via feature_json_write (its own lock,
    schema check and refusal)."""
    def transform(base):
        doc = feature_json_write.parse_doc(base, feature_json)
        if doc is None:
            raise harness_merge.MergeRefusal(
                feature_json_write.SCHEMA_REFUSAL_CODE,
                [f"REFUSED: {feature_json} vanished between the preflight and the write."])
        ledger = doc.get("judgements")
        doc["judgements"] = (list(ledger) if isinstance(ledger, list) else []) + judgements
        return json.dumps(doc, indent=2) + "\n"

    feature_json_write.write_feature_json(feature_json, transform)


def _record_amendments_locked(resolved, feature_json, entries):
    """Both writes under the PLAN's lock, plan first, ledger second, and the plan RESTORED if
    the ledger write fails for ANY reason — a refusal or an ordinary I/O error (validate c0
    V-01, c1 V-01). Before this the ledger landed first, so a plan write that failed
    afterwards left a judgement for an amendment that never reached the plan — the audit
    trail lying in the direction nothing detects. The lock is held across the restore.

    The changed-state feedback (FEAT-62 T-03) is NOT relayed here for the plan: the ledger
    write inside write_feature_json relays once with both files already dirty, and a second
    --changed run over the same tree would only repeat it."""
    with harness_merge.acquire(resolved + ".lock"):
        with open(resolved, "rb") as fh:
            base_bytes = fh.read()
        spliced = _amended_plan_bytes(base_bytes, entries)
        judgements = [_amendment_judgement(e, at)
                      for e, at in zip(entries, _distinct_instants(len(entries)))]
        _replace_bytes(resolved, spliced)
        try:
            _record_amendment_judgements(feature_json, judgements)
        except harness_merge.MergeRefusal as refusal:
            raise harness_merge.MergeRefusal(
                refusal.code, list(refusal.lines) + _restore_plan(resolved, base_bytes))
        except BaseException as exc:
            raise harness_merge.MergeRefusal(
                2, [f"plan-merge: the ledger write to {feature_json} failed: "
                    f"{type(exc).__name__}: {exc}"] + _restore_plan(resolved, base_bytes)) from exc


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
