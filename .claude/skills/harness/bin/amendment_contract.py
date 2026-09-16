"""amendment_contract.py — the closed shape of an engineering lead's `amendments:` entry.

BUG-1716 D-02: an amendment is exactly {task, field, was, now, reason}; `task` is a plan task id
(T-NN), `field` is one of a task's HOW fields (intent, files, verify), `reason` is one non-empty
line of at most 240 characters, and `was`/`now` are strings for a text field or lists of legal
plan file entries (plan_anchors) for `files`. ONE authority: validate-digest.py grades the lead's
return with it and plan-merge.py record-amendments refuses on it, so the two cannot drift.

Every checker returns a list of messages — empty when the rule holds — each prefixed with the
entry's index and the offending key, so a lead reading the refusal knows which line to fix.
"""
import re

import plan_anchors

KEYS = ("task", "field", "was", "now", "reason")
FIELDS = ("intent", "files", "verify")
REASON_MAX = 240
_TASK_RE = re.compile(r"^T-\d{2,}$")


def _keys(entry, where):
    extra = sorted(set(entry) - set(KEYS))
    missing = [k for k in KEYS if k not in entry]
    out = []
    if extra:
        out.append(f"{where} carries unknown key(s) {extra} — an entry is exactly {list(KEYS)}.")
    if missing:
        out.append(f"{where} is missing {missing} — an entry is exactly {list(KEYS)}.")
    return out


def _task(entry, where):
    task = entry.get("task")
    if "task" not in entry or (isinstance(task, str) and _TASK_RE.match(task)):
        return []
    return [f"{where}.task={task!r} — an amendment targets one PLAN task (T-NN); a success "
            f"criterion or decision is never amended by a lead (that is BLOCKED with a "
            f"recommendation)."]


def _field(entry, where):
    if "field" not in entry or entry.get("field") in FIELDS:
        return []
    return [f"{where}.field={entry.get('field')!r} — only {list(FIELDS)} are a task's HOW; "
            f"anything else changes what was signed."]


def _reason(entry, where):
    reason = entry.get("reason")
    if "reason" not in entry or (isinstance(reason, str) and reason.strip()
                                 and "\n" not in reason.strip() and len(reason) <= REASON_MAX):
        return []
    return [f"{where}.reason must be one non-empty line of at most {REASON_MAX} characters — "
            f"it becomes the ledger entry's reason (DEC-230)."]


def _files_value(value, where, key):
    if not isinstance(value, list):
        return [f"{where}.{key}: a files amendment carries a LIST of plan file entries, not "
                f"{type(value).__name__}."]
    return [f"{where}.{key}: {msg}" for msg in plan_anchors.refusals(value)]


def _text_value(value, where, key, field):
    if isinstance(value, str):
        return []
    return [f"{where}.{key}: a {field} amendment carries the text as a string, not "
            f"{type(value).__name__}."]


def _values(entry, where):
    field = entry.get("field")
    if field not in FIELDS:
        return []
    out = []
    for key in ("was", "now"):
        if key not in entry:
            continue
        if field == "files":
            out.extend(_files_value(entry[key], where, key))
        else:
            out.extend(_text_value(entry[key], where, key, field))
    return out


def entry_errors(entry, index):
    """Every fault in ONE parsed amendment mapping, each naming `amendments[index]` and the key.
    `entry` must already be a mapping; the caller reports a non-mapping in its own words."""
    where = f"amendments[{index}]"
    return [msg for check in (_keys, _task, _field, _reason, _values)
            for msg in check(entry, where)]


def normalized(entry):
    """The entry as the ledger and the splice consume it — reason stripped, nothing else touched."""
    return {"task": entry["task"], "field": entry["field"], "was": entry["was"],
            "now": entry["now"], "reason": entry["reason"].strip()}
