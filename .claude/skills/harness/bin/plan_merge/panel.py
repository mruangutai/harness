"""`panel:` / `lanes:` validation and splice, `record-panel`, and `set-key` / `set-panel` / `set-lanes`. (FEAT-70)"""
import os
import sys
import yaml

import digest_record
import harness_merge
import harness_yaml
import panel_findings
from plan_merge.text import (
    DASH_RE, TOP_KEY_RE, _before_trailing_comments, _index_list_items, _index_sub_keys,
    _index_top_keys, _item_delete_end, _item_id, _render_items, _structured_field_lines,
    _sub_key_lines,
)
from plan_merge.guards import (
    _die, _load_base_doc, _load_mapping_value, _locked_plan_update, _reload_or_refuse,
    _resolve_plan, _schema_error,
)

# ---------------------------------------------------------------------------
# `panel:` and `lanes:` — the top-level mappings pm and the orchestrator write (FEAT-59 SC-05,
# SC-08).
#
# TWO PANEL VERBS, ONE SPLICE. `set-panel` takes a whole mapping from a value file; `record-panel`
# derives one from the validator lead's digest. Both land through `_panel_spliced`, which keeps
# the bytes of every finding whose id AND parsed content are unchanged and renders only what
# changed — the property set-task-station has for a status line, applied to a list item.
# Measured on FEAT-54: `set-panel` re-rendered all nine findings on every call, so a review
# diff of a one-finding change touched forty lines and could not show which finding was new.
#
# FINDING IDENTITY IS panel_findings.finding_id, imported. The validator lead never assigns a
# PF- id (it holds no Bash); pm used to run the helper by hand and transcribe. record-panel
# computes it from the digest's reader and summary, once, in the one place check-state.py's
# INV-32 and approval.rulings agree on.
# THE FINDING SHAPE IS panel_findings's TOO (#2095): set-panel validated id and kind only, so the
# template's closed key set and two-value disposition held on record-panel's new findings and
# nowhere else. Every finding a panel verb writes now passes panel_findings.shape_faults.
FINDING_KINDS = panel_findings.FINDING_KINDS
PROPORTIONALITY_SCOPES = panel_findings.PROPORTIONALITY_SCOPES


READER_STATUSES = ("ran", "skipped")


LANES = ("team", "main-session-direct")


def _require_shape(value, required, what):
    """Refuse a mapping missing a required key or carrying the wrong type for one.

    `required` is {key: type}; `cycle` is additionally refused as a bool, which isinstance
    would otherwise accept as an int."""
    missing = [key for key in required if key not in value]
    if missing:
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: {what} value is missing required key(s): {', '.join(missing)}"])
    wrong = [key for key, expected in required.items() if not _is_typed(value[key], expected)]
    if wrong:
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: {what} value has invalid type for: {', '.join(wrong)}"])


def _is_typed(value, expected):
    if expected is int and isinstance(value, bool):
        return False
    return isinstance(value, expected)


def _named_mapping(entry, key, where):
    """Refuse unless `entry` is a mapping whose `key` is a non-empty string."""
    if not isinstance(entry, dict) or not str(entry.get(key, "")).strip():
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: {where} must be a mapping carrying {key}:"])


def _validate_reader(reader, where):
    _named_mapping(reader, "reader", where)
    status = reader.get("status")
    if status not in READER_STATUSES:
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: {where} status {status!r} is not one of "
                f"{', '.join(READER_STATUSES)}"])
    absent = [k for k in ("persona", "reason") if not str(reader.get(k) or "").strip()]
    if status == "skipped" and absent:
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: {where} is skipped without {' and '.join(absent)} — an unrunnable "
                "reader and a clean reader are opposite facts, and the record must say which."])


def _validate_readers(readers, what):
    for index, reader in enumerate(readers):
        _validate_reader(reader, f"{what} readers[{index}]")


def _validate_finding_kind(finding, where):
    kind = finding.get("kind")
    if kind not in FINDING_KINDS:
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: {where} kind {kind!r} is not one of {', '.join(FINDING_KINDS)} — "
                "a finding without a kind cannot say whether it re-gates (FEAT-59 SC-06, C2)."])
    if kind == "proportionality" and finding.get("scope") not in PROPORTIONALITY_SCOPES:
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: {where} is proportionality with scope {finding.get('scope')!r}, not "
                f"one of {', '.join(PROPORTIONALITY_SCOPES)} — task is trimmed at apply, mission "
                "is the only finding that can downgrade the mission (DEC-228)."])


def _validate_panel(panel, what, task_ids=None):
    """The shape both panel verbs hold a mapping to: before the lock with `task_ids` None, and
    again under it against the plan's own task ids, which is where `resolved_by` resolves.
    Every faulty finding is named with every fault, so one refusal says all that must change."""
    _require_shape(panel, {"last_run": str, "cycle": int, "readers": list, "findings": list},
                   what)
    _validate_readers(panel["readers"], what)
    lines = []
    for index, finding in enumerate(panel["findings"]):
        faults = panel_findings.shape_faults(finding, task_ids)
        if faults:
            fid = finding.get("id") if isinstance(finding, dict) else None
            lines.extend(f"plan-merge: {what} findings[{index}] {fid or '<no id>'} {fault}"
                         for fault in faults)
    if lines:
        raise harness_merge.MergeRefusal(
            5, lines + ["  a finding carries templates/plan.yaml's keys and nothing else; "
                        "disposition is open or resolved, and risk acceptance is "
                        "sign-approval --overrule, never a disposition (#2095)."])
    return panel


def _task_ids(doc):
    """The plan's task ids, the set a finding's `resolved_by` must name one of."""
    tasks = doc.get("tasks") if isinstance(doc, dict) else None
    return {str(task.get("id")) for task in tasks or [] if isinstance(task, dict)}


def _validate_lanes(lanes, what):
    _require_shape(lanes, {"resolved_at": str, "rows": list}, what)
    for index, row in enumerate(lanes["rows"]):
        where = f"{what} rows[{index}]"
        _named_mapping(row, "surface", where)
        if row.get("lane") not in LANES:
            raise harness_merge.MergeRefusal(
                5, [f"plan-merge: {where} lane {row.get('lane')!r} is not one of {', '.join(LANES)}"])
    return lanes


def _findings_by_id(lines, item_ranges, base_findings, dash_indent):
    """{id: (start, own_end, end, parsed)} for the base's findings, or a refusal on a duplicate
    id. `end` is the full dash-to-dash range `_index_list_items` gives; `own_end` is where the
    finding's own bytes stop and its trailing comment lines begin."""
    by_id = {}
    for (s, e), item in zip(item_ranges, base_findings):
        fid = str(_item_id(item))
        if fid in by_id:
            raise harness_merge.MergeRefusal(
                5, [f"plan-merge: panel.findings carries {fid} twice; a duplicate id cannot be "
                    "carried unambiguously."])
        by_id[fid] = (s, _item_delete_end(lines, s, e, dash_indent), e, item)
    return by_id


def _finding_lines(finding, base_by_id, lines, dash_indent):
    """One finding's lines, carried THROUGH ITS FULL RANGE (review F10): its own base bytes
    when id and parsed value are unchanged, a render otherwise — and in both cases the comment
    lines that followed it in the base, so a note stays with the finding it followed instead of
    migrating under whichever finding is appended next, or being dropped between two."""
    carried = base_by_id.get(str(_item_id(finding)))
    if carried is None:
        return _render_items([finding], dash_indent)
    s, own_end, e, parsed = carried
    if parsed == finding:
        return lines[s:e]
    return _render_items([finding], dash_indent) + lines[own_end:e]


def _findings_lines(lines, start, end, indent, base_findings, findings):
    """The `findings:` sub-block with every unchanged finding's bytes kept.

    A finding is carried byte for byte when its id is in the base and its parsed value equals
    the base's; anything else is rendered. Falls back to rendering the whole sub-block when the
    base's items cannot be aligned one dash per item, or when either side is the empty list —
    `findings: []` has no dash to splice under."""
    item_ranges = _index_list_items(lines, (start + 1, end))
    if not findings or not base_findings or len(item_ranges) != len(base_findings):
        return _structured_field_lines(indent, "findings", findings)
    dash_indent = DASH_RE.match(lines[item_ranges[0][0]]).group(1)
    base_by_id = _findings_by_id(lines, item_ranges, base_findings, dash_indent)
    out = [lines[start]]
    for finding in findings:
        out.extend(_finding_lines(finding, base_by_id, lines, dash_indent))
    return out


def _panel_sub_block(lines, key, located, indent, base_panel, panel):
    """One sub-key of the rebuilt panel: base bytes when unchanged, an item-wise splice for
    `findings`, a render otherwise. `located` is (start, end, indent) or None when absent."""
    if located is not None and base_panel.get(key) == panel[key]:
        return lines[located[0]:located[1]]
    if key == "findings" and located is not None:
        return _findings_lines(lines, located[0], located[1], indent,
                               base_panel.get(key) or [], panel[key])
    return _structured_field_lines(indent, key, panel[key])


def _panel_block(lines, start, own_end, base_panel, panel):
    """The rebuilt `panel:` block — its own head line, then each sub-key in base order with
    the new keys after, each carried or rendered by `_panel_sub_block`."""
    sub = _index_sub_keys(lines, start + 1, own_end)
    by_key = {key: (s, e, indent) for key, s, e, indent in sub}
    indent = sub[0][3] if sub else "  "
    order = [key for key, _s, _e, _i in sub if key in panel]
    order += [key for key in panel if key not in by_key]
    out = [lines[start]]
    for key in order:
        out.extend(_panel_sub_block(lines, key, by_key.get(key), indent, base_panel, panel))
    return out


def _panel_own_end(lines, start, end):
    """Where the `panel:` block's own bytes stop, inside its top-key range.

    Trailing blank lines and comments at the block's sub-key indent or shallower are the
    document's: they are re-emitted after the rebuilt block, so a wholesale render cannot eat
    them. A DEEPER trailing comment — the template's own `# resolved_by: T-NN` note under the
    last finding — is inside the last sub-key and stays with it (review F10); cutting it off
    here is what re-emitted it under whichever finding was appended next."""
    _keys, indent = _sub_key_lines(lines, start + 1, end)
    width = len(indent or "")
    index = end
    while index > start + 1 and _is_document_tail(lines[index - 1], width):
        index -= 1
    return index


def _is_document_tail(line, width):
    """A blank line, or a comment at `width` or shallower: the document's, not the block's.
    (FEAT-70, from _panel_own_end)"""
    body = line.lstrip()
    if not body:
        return True
    return body.startswith("#") and len(line) - len(body) <= width


def _panel_spliced(base_text, panel):
    """The plan's text with `panel:` replaced by `panel`, byte-preserving where nothing changed.

    Sub-keys whose parsed value is unchanged keep their bytes; `findings` is spliced item by
    item; everything else is rendered at the block's own indent. An absent `panel:` is inserted
    before `tasks:`, where the template has it."""
    lines, _order, ranges, _preamble = _index_top_keys(base_text)
    if "panel" not in ranges:
        replacement = yaml.safe_dump({"panel": panel}, sort_keys=False).splitlines(keepends=True)
        return _insert_top_mapping(lines, ranges, replacement, ("lanes", "decisions", "tasks"))
    base_panel = _load_base_doc(base_text).get("panel")
    start, end = ranges["panel"]
    own_end = _panel_own_end(lines, start, end)
    block = _panel_block(lines, start, own_end,
                         base_panel if isinstance(base_panel, dict) else {}, panel)
    return "".join(lines[:start] + block + lines[own_end:])


def _insert_top_mapping(lines, ranges, replacement, before):
    """Insert a rendered top-level block before the EARLIEST key of `before` that exists, or at
    the end of the document, so key order follows the template rather than the verb order."""
    starts = [ranges[key][0] for key in before if key in ranges]
    if not starts:
        return "".join(lines + replacement)
    at = min(starts)
    return "".join(lines[:at] + replacement + lines[at:])


def _write_top_mapping(resolved, key, value, splice):
    """Run `splice(base_text) -> new_text` under the lock and refuse unless `key` reloads as
    `value` and a legal base stays legal. The shared tail of set-key, set-panel, record-panel
    and set-lanes."""
    def transform(base_bytes):
        base_text = base_bytes.decode("utf-8")
        spliced = splice(base_text).encode("utf-8")
        reloaded = _reload_or_refuse(spliced)
        if reloaded.get(key) != value:
            raise harness_merge.MergeRefusal(
                5, [f"plan-merge: {key} does not reload as the value supplied"])
        if key == "panel":
            _validate_panel(value, key, _task_ids(reloaded))
        # Valid before, invalid after is the test — the same do-no-harm rule apply, amend and
        # delete-items hold to, so a key write cannot turn a legal plan illegal.
        if _schema_error(_load_base_doc(base_text)) is None:
            err = _schema_error(reloaded)
            if err is not None:
                raise harness_merge.MergeRefusal(
                    5, [f"plan-merge: writing {key} would make a legal plan illegal — {err}"])
        return spliced

    try:
        _locked_plan_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)


# ---------------------------------------------------------------------------
# `set-key` — ONE route for every top-level key (#1683).
#
# FEAT-59 closed "`lanes:` has no writer" (#1595, #1636) with `set-lanes`, a verb for that one
# key. The next key to go stale was `source_issues` (BUG-285-canonical-reader, 2026-09-13):
# `apply` exits 7 on a differing top-level key by design, `amend --key` names tasks|decisions
# only, and the shape gate denies every editor write of a plan.yaml to every author. Three
# instances, each an agent blocked mid-run over a route that should already have existed. The
# defect was never "<key> has no writer" — it is that coverage was PER KEY, so every top-level
# key was unwritable until someone hit it in production and filed a ticket. This verb makes
# coverage per DOCUMENT: `--key <name> --value-file <yaml>` replaces the key's own bytes, or
# inserts the key in template order when the plan does not carry it.
#
# THREE KEYS ARE REFUSED BY NAME, WITH THE VERB THAT OWNS THEM. Each has a rule that a whole-
# value write would step around: `approval` is the main session's alone and `sign-approval` its
# only writer (DEC-120) — writing the mapping whole here would be the second way to claim a
# signature; `tasks` and `decisions` are the union verbs' (`apply`, `amend`, `delete-items`),
# which are the ones that reset an approval when the task set changes (#1675) — a task set laid
# over whole would keep a signature it no longer has; `status` is `set-feature-station`'s, which
# validates the station vocabulary. `panel` and `lanes` STAY reachable here, through the same
# validators and splices their named verbs use, so choosing the general verb never skips a shape
# rule. Every other key — `source_issues`, `feature`, `schema`, one a future template adds — is
# checked by the plan schema after the splice, as every other verb's result is.
OWNED_KEYS = {
    "approval": "sign-approval — the main session's alone (DEC-120)",
    "tasks": "apply, add-tasks, amend --key tasks, or delete-items --task",
    "decisions": "apply, amend --key decisions, or delete-items --decision",
    "status": "set-feature-station",
}


# templates/plan.yaml's key order; an absent key is inserted before the first later key present.
TEMPLATE_KEY_ORDER = ("schema", "feature", "status", "source_issues", "approval", "panel",
                      "lanes", "decisions", "tasks")


# Keys whose value has a shape of its own. Each validator refuses a non-mapping and every
# shape fault before the lock is taken.
KEY_VALIDATORS = {"panel": _validate_panel, "lanes": _validate_lanes}


def _load_key_value(path, key):
    """The value for `key` from a YAML file: any YAML value for a plain key, a validated
    mapping for a key in KEY_VALIDATORS. Refuses (5) on a parse or shape fault."""
    validator = KEY_VALIDATORS.get(key)
    if validator is not None:
        return validator(_load_mapping_value(path, key), key)
    try:
        return harness_yaml.load_file(path)
    except harness_yaml.YamlParseError as exc:
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: cannot load {key} value from {path}: {exc}"])


def _insert_before(key):
    """The template keys that follow `key`; an unknown key lands before the union keys."""
    if key in TEMPLATE_KEY_ORDER:
        return TEMPLATE_KEY_ORDER[TEMPLATE_KEY_ORDER.index(key) + 1:]
    return ("decisions", "tasks")


def _key_splice(key, value):
    """`splice(text) -> text` for one top-level key: `panel` keeps its finding-wise splice;
    every other key is replaced through ITS OWN bytes only — trailing blank and comment lines
    inside its top-key range introduce the next key and are kept — or inserted in template
    order when absent."""
    if key == "panel":
        return lambda text: _panel_spliced(text, value)
    replacement = yaml.safe_dump({key: value}, sort_keys=False, allow_unicode=True,
                                 width=10 ** 9).splitlines(keepends=True)

    def splice(text):
        lines, _order, ranges, _preamble = _index_top_keys(text)
        if key not in ranges:
            return _insert_top_mapping(lines, ranges, replacement, _insert_before(key))
        start, end = ranges[key]
        own_end = _before_trailing_comments(lines[:end], floor=start + 1)
        return "".join(lines[:start] + replacement + lines[own_end:])

    return splice


def _set_top_key(file_path, key, value_file):
    """The whole of set-key, set-panel and set-lanes: resolve, refuse an owned key, load and
    validate, splice under the lock. Returns (resolved, value) for the receipt."""
    resolved = _resolve_plan(file_path)
    if key in OWNED_KEYS:
        _die(2, f"plan-merge: {key} is not set-key's to write; its route is {OWNED_KEYS[key]}.")
    if not TOP_KEY_RE.fullmatch(key + ":"):
        # A key the top-key indexer cannot find again would be inserted a second time on the
        # next write; refuse it before the lock rather than write an unreachable key.
        _die(2, f"plan-merge: {key!r} is not a legal top-level key name ([A-Za-z_][\\w-]*).")
    try:
        value = _load_key_value(value_file, key)
    except harness_merge.MergeRefusal as refusal:
        _die(refusal.code, *refusal.lines)
    _write_top_mapping(resolved, key, value, _key_splice(key, value))
    return resolved, value


def cmd_set_key(args):
    resolved, _value = _set_top_key(args.file, args.key, args.value_file)
    print(f"KEY {args.key} -> {resolved}")
    print(f"APPLIED {resolved}")
    sys.exit(0)


def cmd_set_panel(args):
    resolved, panel = _set_top_key(args.file, "panel", args.value_file)
    print(f"PANEL cycle {panel['cycle']} -> {resolved}")
    print(f"APPLIED {resolved}")
    sys.exit(0)


def cmd_set_lanes(args):
    """`lanes:` gets the write route it never had (FEAT-59 SC-08): set-key with the key fixed."""
    resolved, lanes = _set_top_key(args.file, "lanes", args.value_file)
    print(f"LANES {len(lanes['rows'])} row(s) resolved at {lanes['resolved_at']} -> {resolved}")
    print(f"APPLIED {resolved}")
    sys.exit(0)


def _lead_digest(path):
    """The DIGEST mapping of a validator-lead return on disk, or a refusal.

    The durable record (DEC-237) is prose followed by fenced yaml blocks the validator appends;
    digest_record reads the LAST fenced block that loads to a mapping (a later block is a
    correction, DEC-208). No bare-text fallback and no live persona-schema validation: its
    DIGEST must be a mapping, and the consumers below check the keys they use."""
    try:
        record = digest_record.load_record(path)
    except digest_record.DigestRecordError as exc:
        raise harness_merge.MergeRefusal(5, [f"plan-merge: {exc}"])
    digest = record.get("DIGEST")
    if not isinstance(digest, dict):
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: {path}'s last fenced yaml block has no DIGEST: mapping — the "
                "validator lead's return is what record-panel transcribes, and nothing else."])
    return digest


def _digest_finding(finding, where):
    """One panel finding from one digest entry: content-hash id, closed key set, ALWAYS open.

    Every entry needs kind (C2), severity, reader and summary: identity is reader + summary,
    and a finding without a severity or a kind cannot gate. `why` and any other free key the
    lead wrote are NOT carried — panel.findings is the closed shape the template declares.
    The digest's `disposition` is not carried either (review F8 / SEC-04): a new finding
    arrives open whatever the lead wrote, because resolution is set-panel's and the operator's
    ruling's to record, and a finding landing pre-resolved would sign a plan past INV-32 with
    no ruling at all. A digest entry for a finding already in the base is matched by id only;
    the base's value, disposition included, wins."""
    if not isinstance(finding, dict):
        raise harness_merge.MergeRefusal(5, [f"plan-merge: {where} is not a mapping"])
    absent = [k for k in ("severity", "reader", "summary") if not str(finding.get(k) or "").strip()]
    if absent:
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: {where} is missing {', '.join(absent)} — reader and summary are "
                "the finding's identity, severity is what gates."])
    _validate_finding_kind(finding, where)
    reader, summary = str(finding["reader"]), str(finding["summary"])
    entry = {"id": panel_findings.finding_id(reader, summary), "severity": str(finding["severity"]),
             "reader": reader, "kind": finding["kind"], "summary": summary,
             "disposition": "open"}
    if finding["kind"] == "proportionality":
        entry["scope"] = finding["scope"]
    return entry


def _digest_findings(digest, what):
    return [_digest_finding(finding, f"{what} findings[{index}]")
            for index, finding in enumerate(digest.get("findings") or [])]


def _digest_readers(digest, what):
    readers = digest.get("readers")
    if not isinstance(readers, list):
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: {what} carries no readers: list — every reader must appear, ran "
                "or skipped, or a reader that never ran looks clean."])
    _validate_readers(readers, what)
    return readers


def _base_findings(base_text):
    """The base plan's parsed panel.findings mappings, [] when there is no panel yet."""
    base_panel = _load_base_doc(base_text).get("panel") if base_text else None
    findings = base_panel.get("findings") if isinstance(base_panel, dict) else None
    return [f for f in (findings or []) if isinstance(f, dict)]


def _recorded_panel(base_text, digest, cycle, last_run):
    """The panel mapping record-panel writes: the digest's readers, its findings UNIONED with
    the base's — a finding already present keeps its own parsed value (and so, through
    `_panel_spliced`, its own bytes and disposition); a new one is appended open.
    Returns (panel, carried ids, added ids)."""
    what = "lead digest"
    readers = _digest_readers(digest, what)
    findings = _base_findings(base_text)
    present = {str(_item_id(f)) for f in findings}
    incoming = _digest_findings(digest, what)
    carried = [f["id"] for f in incoming if f["id"] in present]
    added = _first_by_id([f for f in incoming if f["id"] not in present])
    findings.extend(added)
    panel = {"last_run": last_run, "cycle": cycle, "readers": readers, "findings": findings}
    # The base's findings are carried byte for byte, so they are held to the template too: a
    # carried departure would otherwise ride every later cycle into the signed plan (#2095).
    task_ids = _task_ids(_load_base_doc(base_text)) if base_text else None
    return _validate_panel(panel, what, task_ids), carried, [f["id"] for f in added]


def _first_by_id(findings):
    """`findings` with every repeat of an id dropped — the lead de-duplicates on normalized
    summary plus reader, which is exactly this id, so a repeat is the same finding twice."""
    seen, out = set(), []
    for finding in findings:
        if finding["id"] not in seen:
            seen.add(finding["id"])
            out.append(finding)
    return out


def cmd_record_panel(args):
    """Write `panel:` FROM the validator lead's digest (FEAT-59 SC-05).

    Before this verb, pm read the lead digest, ran panel_findings.py once per finding, built a
    value file in /tmp and called set-panel — a whole run whose only work was to copy one file
    into another (FEAT-54 c0 and c3, BUG-285 three of nineteen runs). The digest is parsed
    BEFORE the lock, so a malformed one refuses without opening the plan; the base's own
    findings are carried under the lock, so a concurrent set-panel cannot be lost."""
    resolved = _resolve_plan(args.file)
    last_run = args.last_run or os.path.basename(os.path.dirname(os.path.abspath(args.digest)))
    try:
        digest = _lead_digest(args.digest)
        # Shape faults in the digest refuse here, on an empty base, before any lock is taken.
        _recorded_panel("", digest, args.cycle, last_run)
    except harness_merge.MergeRefusal as refusal:
        _die(refusal.code, *refusal.lines)
    result = {}

    def transform(base_bytes):
        text = base_bytes.decode("utf-8")
        panel, carried, added = _recorded_panel(text, digest, args.cycle, last_run)
        spliced = _panel_spliced(text, panel).encode("utf-8")
        reloaded = _reload_or_refuse(spliced)
        if reloaded.get("panel") != panel:
            raise harness_merge.MergeRefusal(
                5, ["plan-merge: panel does not reload as the value recorded"])
        result.update(carried=carried, added=added)
        return spliced

    try:
        _locked_plan_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        _die(refusal.code, *refusal.lines)
    for fid in result["carried"]:
        print(f"CARRIED {fid}")
    for fid in result["added"]:
        print(f"ADDED {fid}")
    print(f"PANEL cycle {args.cycle} from {args.digest} -> {resolved}")
    print(f"APPLIED {resolved}")
    sys.exit(0)
