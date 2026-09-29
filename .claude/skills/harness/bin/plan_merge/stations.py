"""`set-task-station` / `set-feature-station`, station classification, and the approval reset/resume family. (FEAT-70)"""
import re
import sys
from datetime import datetime
from datetime import timezone

import factory_config
import harness_merge
from plan_merge.text import (
    ITEM_ID_RE, _approval_span, _field_lines, _index_top_keys, _sub_key_lines,
)
from plan_merge.guards import (
    _legal_stations, _locked_plan_update, _refuse_illegal_station, _reload_or_refuse,
    _resolve_plan,
)

def _now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _approval_status(doc):
    approval = doc.get("approval") if isinstance(doc, dict) else None
    return approval.get("status") if isinstance(approval, dict) else None


RESET_FIELDS = ("reset_at", "reset_reason", "resume_station")


_RESET_LINE_RE = re.compile(r"^\s+(reset_at|reset_reason|resume_station):")


def _replace_approval_reset(body, status_at, stale, record):
    """Replace one status line and discard prior reset metadata without moving other bytes."""
    out = []
    for index, line in enumerate(body):
        if index in stale:
            continue
        if index == status_at:
            out.extend(record)
            continue
        out.append(line)
    return out


def _reset_approval_lines(lines, reason, resume_station):
    """`lines` with approval.status rewritten to pending and its resume context recorded.

    C4 / SC-08, narrowed by BUG-1716 D-04: a signature is a statement about ONE task set. A
    verb that ADDS or DELETES a task on an approved plan voids it — downward only;
    `sign-approval` is the only writer of `approved`. Replacing text on an existing task does
    NOT: the signed text is hashed into feature.json at signature, a ledgered amendment
    (`record-amendments`) is the sanctioned change, and an unledgered one is INV-40's to
    refuse rather than this verb's to authorize. The signer and date are kept so the operator
    can see what was voided and by which verb; a prior reset record is replaced, not stacked.
    The caller has already established that the parsed approval.status is `approved` or that a
    pending reset carries resume metadata, so the status key is found BY NAME at the mapping's
    own indent. A shape with no status line is returned unchanged and `_verify_reset` refuses it."""
    start, end = _approval_span(lines)
    if start is None:
        return lines
    body = lines[start + 1:end]
    keyed, indent = _sub_key_lines(body, 0, len(body))
    positions = dict(keyed)
    status_at = positions.get("status")
    if status_at is None:
        return lines
    stale = {positions[key] for key in RESET_FIELDS if key in positions}
    record = [_field_lines(indent, "status", "pending"),
              _field_lines(indent, "reset_at", _now_iso()),
              _field_lines(indent, "reset_reason", reason),
              _field_lines(indent, "resume_station", resume_station)]
    out = _replace_approval_reset(body, status_at, stale, record)
    return lines[:start + 1] + out + lines[end:]


def _task_statuses(resulting_doc):
    """Every task's status, an absent one read as ready — the not-started station gh_board
    reads for the same absence.

    STRICT AT THE BOUNDARY (FEAT-61 T-02, D-03): each explicit status crosses factory_config's
    station predicate here, so a status outside the vocabulary — or an empty one — raises
    FleetError whatever the interrupted phase, instead of `_work_started` (a spelled one-off that
    never asks the boundary) reading it as "not started", or the building phase, which consults
    no task status at all, writing a reset over a corrupt plan."""
    tasks = resulting_doc.get("tasks") if isinstance(resulting_doc, dict) else None
    if not isinstance(tasks, list):
        return []
    statuses = [task.get("status", "ready") for task in tasks if isinstance(task, dict)]
    for status in statuses:
        factory_config.is_finished(status)
    return statuses


def _review_complete(statuses):
    """Non-empty and every task finished (FEAT-61 T-02): done, abandoned or rejected. A rejected
    task completes review exactly as an abandoned one does — neither is work still to happen."""
    return bool(statuses) and all(factory_config.is_finished(status) for status in statuses)


# HISTORICAL ONE-OFF, SPELLED ON PURPOSE (FEAT-61 T-02). This is NOT ACTIVE_STATIONS and NOT
# FINISHED_STATIONS, and must not be derived from either: `finished` is not evidence that work
# started — abandoned can happen before execution and rejected happens at intake — so a plan whose
# only non-ready tasks are abandoned or rejected resumes at ready, not building. `plan` and `ready`
# are not evidence either. Exactly building, review and done are.
_WORK_STARTED = ("building", "review", "done")


def _work_started(statuses):
    return any(status in _WORK_STARTED for status in statuses)


def _resume_station(interrupted_phase, resulting_doc):
    """Classify the active station reapproval should restore after a task-set mutation."""
    statuses = _task_statuses(resulting_doc)
    if interrupted_phase == "review":
        return "review" if _review_complete(statuses) else "building"
    if interrupted_phase == "building":
        return "building"
    return "building" if _work_started(statuses) else "ready"


def _verify_reset(text, verb, resume_station):
    """Refuse rather than write a task change unless every reset field reloads as intended."""
    doc = _reload_or_refuse(text.encode("utf-8"))
    approval = doc.get("approval") if isinstance(doc, dict) else None
    got_status = approval.get("status") if isinstance(approval, dict) else None
    got_resume = approval.get("resume_station") if isinstance(approval, dict) else None
    got_phase = doc.get("status") if isinstance(doc, dict) else None
    if (got_status, got_resume, got_phase) != ("pending", resume_station, "plan"):
        raise harness_merge.MergeRefusal(
            5, [f"REFUSED: {verb} changes a task on an approved plan, but the lifecycle reset "
                "would not reload as requested — REFUSING to write it.",
                f"  approval.status reloads as: {got_status!r}",
                f"  approval.resume_station reloads as: {got_resume!r}",
                f"  feature status reloads as: {got_phase!r}",
                "  expected pending approval, the classified resume station, and feature "
                "status plan in one locked update (SC-06/SC-07)."])


def _approval_reset_context(base_doc):
    """Return interrupted phase plus whether this mutation first voids an approval."""
    if not isinstance(base_doc, dict):
        return None
    interrupted_phase = base_doc.get("status") or "plan"
    # A finished feature (done, abandoned, rejected) or a backlog one is never paused at plan;
    # a feature station outside the vocabulary raises here (FEAT-61 T-02, D-03).
    if not factory_config.is_active(interrupted_phase):
        return None
    approval = base_doc.get("approval")
    if not isinstance(approval, dict):
        return None
    if approval.get("status") == "approved":
        return interrupted_phase, True
    if approval.get("status") == "pending" and approval.get("resume_station"):
        return approval["resume_station"], False
    return None


def _maybe_reset_approval(text, base_doc, verb, task_ids):
    """Pause an active feature at plan and retain the station reapproval must restore."""
    context = _approval_reset_context(base_doc) if task_ids else None
    if context is None:
        return text, False
    interrupted_phase, reset = context
    resulting_doc = _reload_or_refuse(text.encode("utf-8"))
    resume_station = _resume_station(interrupted_phase, resulting_doc)
    reason = f"{verb} {', '.join(str(i) for i in task_ids)}"
    lines = _reset_approval_lines(
        text.splitlines(keepends=True), reason, resume_station,
    )
    reset_bytes = _splice_top_level_status(lines, "plan")
    if reset_bytes is None:
        raise harness_merge.MergeRefusal(
            5, [f"REFUSED: {verb} cannot pause the feature because its plan carries no "
                "top-level feature: key to anchor status to"],
        )
    reset_text = reset_bytes.decode("utf-8")
    _verify_reset(reset_text, verb, resume_station)
    return reset_text, reset


APPROVAL_RESET_LINE = ("APPROVAL-RESET: the plan was approved and its task set or a task field "
                       "changed; approval.status is pending until the main session signs again")


# The item-id regex is text.py's ITEM_ID_RE: one pattern, two former copies (FEAT-70).
STATUS_LINE_RE = re.compile(r"^(\s*)status:\s*(.*)$")


FEATURE_LINE_RE = re.compile(r"^feature:\s*\S")


def _task_status_line(lines, task_id):
    """(index, indent) of `task_id`'s own status line, or (None, task_ids_present).

    Scans from the task's `- id:` line to the next item at the same indent, so a `status:` key
    nested deeper inside that task — a verify block's own prose, say — cannot be mistaken for
    the task's status. Returns the ids actually present when the id is absent, because a caller
    who mistyped one needs to see the real list, not just a refusal.

    SCOPED TO THE `tasks:` KEY. `- id:` also matches every entry under `decisions:`, and listing
    D-01..D-12 in the exit-3 message for a `--task` mistake invites the operator to retry with a
    decision id — which would then fail for the unrelated reason that decisions carry no status.
    A refusal that suggests a wrong next step is worse than a terse one.
    """
    _lines, _order, ranges, _pre = _index_top_keys("".join(lines))
    if "tasks" not in ranges:
        return None, []
    lo, hi = ranges["tasks"]
    start, indent, ids_present = _task_search(lines, lo, hi, task_id)
    if start is None:
        return None, ids_present
    found = _status_in_task(lines, start, indent)
    if found is None:
        return None, ids_present
    return found


def _task_search(lines, lo, hi, task_id):
    """(start, indent, ids_present) for `task_id` within the tasks range [lo, hi): the id list
    collects every `- id:` seen — the target's own and its terminator's included, in text
    order, the FIRST match of a duplicated id kept — and the scan stops only at a later item
    at the target's indent. Absent: (None, "", ids_present). (FEAT-70, from _task_status_line)"""
    ids_present = []
    start, indent = None, ""
    for i in range(lo, hi):
        m = ITEM_ID_RE.match(lines[i])
        if not m:
            continue
        ids_present.append(m.group(2))
        if start is None:
            if m.group(2) == task_id:
                start, indent = i, m.group(1)
        elif m.group(1) == indent:
            break
    return start, indent, ids_present


def _closes_item(line, indent):
    """True when `line` opens the next item at `indent` — the end of the item being scanned."""
    m = ITEM_ID_RE.match(line)
    return bool(m) and m.group(1) == indent


def _status_in_task(lines, start, indent):
    """(index, indent) of the first `status:` line nested deeper than the item opened at
    `start`, scanning to the input's end and stopping at the next item at the same indent;
    None when the item carries no status of its own. (FEAT-70, from _task_status_line)"""
    for j in range(start + 1, len(lines)):
        if _closes_item(lines[j], indent):
            return None
        ms = STATUS_LINE_RE.match(lines[j])
        if ms and len(ms.group(1)) > len(indent):
            return j, ms.group(1)
    return None

def cmd_set_task_station(args):
    resolved = _resolve_plan(args.file)
    legal = _legal_stations(resolved)
    if args.station not in legal:
        _refuse_illegal_station(args.station, legal)

    missing = {}

    def transform(base_bytes):
        text = base_bytes.decode("utf-8")
        lines = text.splitlines(keepends=True)
        idx, info = _task_status_line(lines, args.task)
        if idx is None:
            missing["ids"] = info
            return base_bytes
        newline = "\n" if lines[idx].endswith("\n") else ""
        lines[idx] = f"{info}status: {args.station}{newline}"
        return "".join(lines).encode("utf-8")

    try:
        _locked_plan_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)

    if "ids" in missing:
        present = ", ".join(missing["ids"]) or "(none)"
        print(f"plan-merge: {args.task} is not in {resolved} — it carries: {present}",
              file=sys.stderr)
        sys.exit(3)
    print(f"STATION {args.task} -> {args.station}")
    print(f"APPLIED {resolved}")
    sys.exit(0)


def _replace_top_level_status(lines, station):
    """Rewrite an existing column-0 `status:` line in place. True when one was found.

    The indent group must be EMPTY: every task carries its own `status:` and an indented match
    would rewrite the first task's station instead of the feature's.
    """
    for i, line in enumerate(lines):
        m = STATUS_LINE_RE.match(line)
        if m and m.group(1) == "":
            newline = "\n" if line.endswith("\n") else ""
            lines[i] = f"status: {station}{newline}"
            return True
    return False


def _insert_status_after_feature(lines, station):
    """Insert a `status:` line immediately after the top-level `feature:` key. True when done."""
    for i, line in enumerate(lines):
        if FEATURE_LINE_RE.match(line):
            lines.insert(i + 1, f"status: {station}\n")
            return True
    return False


def _splice_top_level_status(lines, station):
    """Set plan.yaml's top-level `status`, returning the new bytes, or None if there is nowhere.

    None means the document carries no top-level `feature:` key to anchor to, which the caller
    turns into a refusal — this function never raises, so the lock plumbing and the text edit
    stay separable. Extracted from `cmd_set_feature_station.transform` (FEAT-41 F-05), which
    interleaved two splice strategies with the refusal at grade 3.

    REPLACE the existing top-level status, or INSERT immediately after `feature:` so the file
    keeps a stable key order. Appending at the end would work and would also make every
    plan.yaml's key order depend on the order the verbs happened to run in.
    """
    if (_replace_top_level_status(lines, station)
            or _insert_status_after_feature(lines, station)):
        return "".join(lines).encode("utf-8")
    return None


def cmd_set_feature_station(args):
    resolved = _resolve_plan(args.file)
    legal = _legal_stations(resolved)
    if args.station not in legal:
        _refuse_illegal_station(args.station, legal)

    def transform(base_bytes):
        lines = base_bytes.decode("utf-8").splitlines(keepends=True)
        spliced = _splice_top_level_status(lines, args.station)
        if spliced is None:
            raise harness_merge.MergeRefusal(
                5,
                [f"plan-merge: {resolved} carries no top-level feature: key to anchor status to"],
            )
        return spliced

    try:
        _locked_plan_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)
    print(f"STATION {resolved} -> {args.station}")
    print(f"APPLIED {resolved}")
    sys.exit(0)
