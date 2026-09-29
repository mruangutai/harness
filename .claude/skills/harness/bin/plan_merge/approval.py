"""`sign-approval` / `revoke-approval`: the signature, its rework ruling and signed task hashes (DEC-120). (FEAT-70)"""
import hashlib
import json
import os
import re
import sys
import yaml

import factory_config
import feature_json_write
import harness_boundary
import harness_merge
import harness_yaml
from plan_merge.guards import (
    BIN_DIR, _die, _load_base_doc, _locked_plan_update, _refuse_governed_agent, _reload_or_refuse,
    _resolve_plan,
)
from plan_merge.stations import (
    _RESET_LINE_RE, _approval_reset_context, _approval_status, _reset_approval_lines,
    _resume_station, _splice_top_level_status, _verify_reset,
)
from plan_merge.text import _approval_span, _before_trailing_comments, _field_lines

def _panel_finding_ids(doc):
    panel = doc.get("panel") if isinstance(doc, dict) else None
    findings = panel.get("findings", []) if isinstance(panel, dict) else []
    return {
        str(item.get("id", "")).strip()
        for item in findings
        if isinstance(item, dict) and str(item.get("id", "")).strip()
    }


def _parse_overrule(spec, finding_ids):
    finding, separator, reason = spec.partition(":")
    finding, reason = finding.strip(), reason.strip()
    if not separator or not finding or not reason:
        raise harness_merge.MergeRefusal(
            4, ["plan-merge: --overrule must be FINDING-ID:non-empty reason"]
        )
    if finding not in finding_ids:
        present = ", ".join(sorted(finding_ids)) or "<none>"
        raise harness_merge.MergeRefusal(
            4, [f"plan-merge: --overrule finding {finding} is not in panel.findings",
                f"  current finding ids: {present}"],
        )
    return finding, reason


def _requested_overrules(specs, doc, who, date):
    """Validate `FINDING:REASON` arguments against the panel snapshot being signed."""
    invalid_attribution = (
        not str(who).strip()
        or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", str(date).strip())
    )
    if specs and invalid_attribution:
        raise harness_merge.MergeRefusal(
            4, ["plan-merge: --overrule requires a non-empty --by and YYYY-MM-DD --date"]
        )
    finding_ids = _panel_finding_ids(doc)
    parsed = [_parse_overrule(spec, finding_ids) for spec in specs]
    return [
        {"finding": finding, "who": who, "date": date, "reason": reason}
        for finding, reason in parsed
    ]


def _rulings_lines(indent, rulings):
    dumped = yaml.safe_dump(rulings, sort_keys=False, width=10 ** 9, allow_unicode=True)
    return [f"{indent}rulings:\n"] + [
        f"{indent}  {line}\n" for line in dumped.rstrip("\n").split("\n")
    ]


def _rulings_key(lines):
    for index, line in enumerate(lines):
        match = re.match(r"^(\s+)rulings:\s*(.*)$", line)
        if match:
            return index, match.group(1)
    return None, "  "


def _next_approval_key(lines, start, indent):
    sibling = re.compile(rf"^{re.escape(indent)}[A-Za-z_][\w-]*:")
    return next((i for i in range(start, len(lines)) if sibling.match(lines[i])), len(lines))


def _splice_approval_rulings(lines, rulings):
    """Replace only approval.rulings, retaining sibling fields and trailing comments."""
    key_at, indent = _rulings_key(lines)
    if key_at is None:
        insert_at = _before_trailing_comments(lines)
        return lines[:insert_at] + _rulings_lines(indent, rulings) + lines[insert_at:]
    end = _next_approval_key(lines, key_at + 1, indent)
    content_end = _before_trailing_comments(lines[:end], key_at + 1)
    return (lines[:key_at] + _rulings_lines(indent, rulings)
            + lines[content_end:])


def _verify_signature(spliced_bytes, resolved, fields):
    """Refuse rather than write a signature that does not reload as the one that was asked for.

    FEAT-41 F-02, the second half. `_field_lines` above fixes the cause; this catches anything
    it misses, and the two are NOT redundant: the failures where the value is silently coerced
    rather than corrupted (`yes` -> True, `#845 owner` -> None) leave a document that parses
    perfectly, so a check that only asked "does it load" would pass them all.

    IT COMPARES VALUES, NOT SYNTAX. That is the only check that can tell the difference between
    a signature and something that merely looks like one. Exit 5 is the same code the splice
    defect this mirrors already uses -- an unwritable result, not a bad argument.
    """
    try:
        reloaded = harness_yaml.load_str(spliced_bytes.decode("utf-8"), "<spliced signature>")
    except harness_yaml.YamlParseError as exc:
        raise harness_merge.MergeRefusal(
            5,
            [
                "UNPARSEABLE: the signed plan does not load — REFUSING to write it.",
                f"  {exc}",
                "  this is a splice defect, not a bad signature: the base parsed.",
            ],
        )
    if not isinstance(reloaded, dict) or not isinstance(reloaded.get("approval"), dict):
        raise harness_merge.MergeRefusal(
            5, [f"UNPARSEABLE: {resolved} has no approval mapping after signing — "
                "REFUSING to write it."]
        )
    got = reloaded["approval"]
    for key, want in fields.items():
        if got.get(key) != want:
            raise harness_merge.MergeRefusal(
                5,
                [
                    f"REFUSED: the signature does not reload as written — approval.{key} "
                    "would not say what was signed.",
                    f"  asked for: {want!r}",
                    f"  reloads as: {got.get(key)!r}",
                ],
            )


def _approval_fields(base_bytes, args):
    fields = {"status": "approved", "approved_by": args.by, "date": args.date}
    base_doc = _reload_or_refuse(base_bytes)
    requested = _requested_overrules(args.overrule, base_doc, args.by, args.date)
    if not requested:
        return fields
    approval = base_doc.get("approval") or {}
    existing = approval.get("rulings", [])
    if not isinstance(existing, list):
        raise harness_merge.MergeRefusal(
            5, ["plan-merge: approval.rulings is malformed; expected a list"]
        )
    fields["rulings"] = existing + requested
    return fields


def _new_approval_block(fields):
    block = ["approval:\n"]
    block.extend(_field_lines("  ", key, fields[key])
                 for key in ("status", "approved_by", "date"))
    if "rulings" in fields:
        block.extend(_rulings_lines("  ", fields["rulings"]))
    return block


def _replace_signature_fields(body, fields):
    """The approval body with status/approved_by/date rewritten and any auto-reset record
    dropped: a fresh signature supersedes `reset_at`/`reset_reason` (C4), and leaving them
    would make a signed plan read as voided."""
    written = set()
    output = []
    for line in body:
        if _RESET_LINE_RE.match(line):
            continue
        match = re.match(r"^(  )(status|approved_by|date):\s*(.*)$", line)
        if not match or match.group(2) in written:
            output.append(line)
            continue
        output.append(_field_lines(match.group(1), match.group(2), fields[match.group(2)]))
        written.add(match.group(2))
    return output, written


def _updated_approval_body(body, fields):
    output, written = _replace_signature_fields(body, fields)
    missing = [key for key in ("status", "approved_by", "date") if key not in written]
    for key in missing:
        output.insert(0, _field_lines("  ", key, fields[key]))
    if "rulings" in fields:
        return _splice_approval_rulings(output, fields["rulings"])
    return output


def _approval_resume_station(base_bytes):
    """Return the one lower-case station sign-approval must emit for its caller."""
    doc = _reload_or_refuse(base_bytes)
    approval = doc.get("approval") if isinstance(doc, dict) else None
    station = approval.get("resume_station") if isinstance(approval, dict) else None
    station = station or "ready"
    # THE CODOMAIN OF `_resume_station` IS ACTIVE MINUS `plan` (FEAT-61 T-02, validate c1): a
    # reset never resumes at plan. Derived from the table, never respelled, so a station added
    # to the active bucket is resumable without this line learning about it.
    if station not in set(factory_config.ACTIVE_STATIONS) - {"plan"}:
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: approval.resume_station is {station!r}; expected ready, "
                "building, or review before signing"],
        )
    return station


def _signed_approval_bytes(base_bytes, resolved, args):
    lines = base_bytes.decode("utf-8").splitlines(keepends=True)
    fields = _approval_fields(base_bytes, args)
    start, end = _approval_span(lines)
    if start is None:
        insert_at = next(
            (i + 1 for i, line in enumerate(lines) if re.match(r"^feature:\s*", line)), None
        )
        if insert_at is None:
            raise harness_merge.MergeRefusal(
                5, [f"plan-merge: {resolved} carries no feature key before signing"]
            )
        lines[insert_at:insert_at] = _new_approval_block(fields)
    else:
        lines[start + 1:end] = _updated_approval_body(lines[start + 1:end], fields)
    spliced = "".join(lines).encode("utf-8")
    _verify_signature(spliced, resolved, fields)
    return spliced


def cmd_sign_approval(args):
    """THE ONLY WAY A SIGNATURE IS EVER WRITTEN (D-04, FEAT-41 T-03).

    Every verb but the reset writers — the task-changing verbs and `revoke-approval`, which
    only move approved to pending — leaves the base's approval bytes byte-identical, and
    `apply` still exits 8 on a proposal carrying a different one. That prohibition and this
    verb are the same rule seen from two sides: `approved` is written HERE, deliberately, by
    the main session, and nowhere else by accident."""
    # #1103: a structural identity check INSIDE this verb, not only plan-sign-gate.py's hook.
    # That hook must PARSE untrusted shell text to predict whether a command will reach here,
    # and four shell forms have evaded that prediction across three review cycles (FEAT-41
    # F-03, H-02, C2-03, MF-1) while still literally invoking this verb. This check needs no
    # prediction: it reads the caller's own real identity at the moment this code actually runs.
    #
    # HARNESS_AGENT_TYPE is injected onto a governed subagent's Bash environment by the OMP
    # host itself (harness-hooks.ts's `tool_call` handler), from the same `agent_type` the hook
    # payload already carries — never from anything this command's own argv or text supplies,
    # and never set by this process. AN ABSENT VARIABLE IS THE MAIN SESSION, the identical
    # exemption plan-sign-gate.py's own hook already uses for the identical reason ("AN ABSENT
    # OR EMPTY agent_type IS THE MAIN SESSION"), and the one convention this whole codebase
    # applies without exception (dispatch-guard.py, bash-write-guard.py, check-domain.py,
    # validate-digest.py). Treating absence as a refusal here would refuse the main session's
    # own legitimate signature — a stricter check that is wrong, not merely untested.
    #
    # RESIDUAL, STATED RATHER THAN HIDDEN: a caller sophisticated enough to scrub its own
    # environment before invoking this command (`env -u HARNESS_AGENT_TYPE ...`) still defeats
    # this, the same way plan-sign-gate.py's own docstring already concedes for itself — "a
    # guardrail against a signature written out of over-eagerness, NOT a security boundary."
    # This closes the four DEMONSTRATED shell-syntax leaks and needs no new case when a fifth
    # surfaces; it does not claim to close deliberate sabotage of its own identity signal.
    _refuse_governed_agent("sign", "cmd_sign_approval")
    resolved = _resolve_plan(args.file)
    ruling, feature_json = _rework_ruling(args, resolved)
    # THE RULING IS RECORDED BEFORE THE SIGNATURE (review F4). feature_json_write can still
    # refuse past the existence check — invalid JSON, a schema regression, a lock timeout —
    # and a signed plan with no ruling is the half-state SC-15 exists to prevent. The other
    # order fails safe: a ruling without a signature is harmless, and the plan is re-signed.
    if ruling is not None:
        _record_rework(feature_json, ruling)
        print(f"REWORK rounds={ruling['rounds']} minutes={ruling['wall_clock_minutes']} "
              f"decision={ruling['decision']} -> {feature_json}")

    resume = {}

    def transform(base_bytes):
        resume["station"] = _approval_resume_station(base_bytes)
        signed = _signed_approval_bytes(base_bytes, resolved, args)
        # THE HASHES ARE WRITTEN UNDER THE PLAN LOCK, BEFORE THE SIGNATURE LANDS (BUG-1716
        # D-03): they are computed from the very bytes being signed, and a feature.json refusal
        # here aborts the signature, so a signed plan never exists without the hashes INV-40
        # grades its task text against. Hashes without a signature are harmless (re-sign).
        _record_signed_task_hashes(resolved, _reload_or_refuse(signed))
        return signed

    try:
        _locked_plan_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        lines = list(refusal.lines)
        if ruling is not None:
            lines.append(f"  the rework ruling was already recorded in {feature_json}; a ruling "
                         "without a signature is harmless — re-run sign-approval to sign.")
        _die(refusal.code, *lines)
    print(f"RESUME: {resume['station']}")
    print(f"SIGNED {resolved} by {args.by} on {args.date}")
    print(f"APPLIED {resolved}")
    sys.exit(0)


# ---------------------------------------------------------------------------
# `revoke-approval` — the signature's one downward verb (#1675).
#
# The template promised "any change to the task set resets this to pending" and FEAT-59
# delivered it (DEC-229): add-tasks, apply and delete-items void an approved plan
# automatically. What that left unrepresentable is a signature withdrawn WITHOUT a task-set
# change — an operator ruling that the signed scope no longer holds, a plan signed in error.
# BUG-285 sat in that state: four tasks under a signature that covered one, and the only way
# to stop claiming the stale signature was a new one. `sign-approval` writes `approved` and
# nothing else; `amend` refuses `approval:`; the shape gate refuses every editor.
#
# ONE STATE, TWO TRIGGERS. This verb writes exactly the record the automatic reset writes —
# `status: pending`, `reset_at`, `reset_reason` — so every reader that already understands a
# voided signature understands a revoked one; `reset_reason` says which it was. It is the
# main session's alone, as the signature is (DEC-120), and it refuses a plan that is not
# approved: revoking nothing is a mistaken command, not a no-op.


def cmd_revoke_approval(args):
    _refuse_governed_agent("revoke", "cmd_revoke_approval")
    resolved = _resolve_plan(args.file)
    why = " ".join(args.reason.split())
    if not why:
        _die(2, "plan-merge: revoke-approval needs a non-empty --reason; it is written into "
                "approval.reset_reason so the record says why the signature was withdrawn.")
    reason = f"revoke-approval {args.by}: {why}"

    def transform(base_bytes):
        text = base_bytes.decode("utf-8")
        doc = _load_base_doc(text)
        status = _approval_status(doc)
        if status != "approved":
            raise harness_merge.MergeRefusal(
                5, [f"plan-merge: {resolved} approval.status is {status!r}, not approved — "
                    "there is no signature to revoke."])
        context = _approval_reset_context(doc)
        if context is None:
            raise harness_merge.MergeRefusal(
                5, [f"plan-merge: {resolved} is terminal and cannot be reopened by revoking "
                    "its approval."])
        interrupted_phase, _ = context
        resume_station = _resume_station(interrupted_phase, doc)
        lines = _reset_approval_lines(
            text.splitlines(keepends=True), reason, resume_station,
        )
        reset_bytes = _splice_top_level_status(lines, "plan")
        if reset_bytes is None:
            raise harness_merge.MergeRefusal(
                5, [f"REFUSED: revoke-approval cannot pause the feature because its plan "
                    "carries no top-level feature: key to anchor status to"])
        revoked = reset_bytes.decode("utf-8")
        _verify_reset(revoked, "revoke-approval", resume_station)
        return reset_bytes

    try:
        _locked_plan_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        _die(refusal.code, *refusal.lines)
    print(f"REVOKED {resolved} by {args.by}: {why}")
    print(f"APPLIED {resolved}")
    sys.exit(0)


REWORK_RE = re.compile(r"^rounds=(\d+),minutes=(\d+)$")


def _parse_rework(rework, decision):
    """{rounds, wall_clock_minutes, decision} from the two flags, or an exit-2 refusal."""
    if rework is None or decision is None:
        _die(2, "plan-merge: --rework and --decision go together — the ruling is the bounds AND "
                "the record of who set them (SC-15).")
    m = REWORK_RE.match(rework.strip())
    if not m:
        _die(2, f"plan-merge: --rework {rework!r} is not rounds=N,minutes=M with non-negative "
                "integers.")
    if not decision.strip():
        _die(2, "plan-merge: --decision must name the ruling's record, not be empty.")
    return {"rounds": int(m.group(1)), "wall_clock_minutes": int(m.group(2)),
            "decision": decision.strip()}


def _rework_ruling(args, resolved):
    """(ruling, feature_json_path) from --rework/--decision, or (None, None) when neither was
    given. Both or neither; `rounds=N,minutes=M` with non-negative integers; the sibling
    feature.json must EXIST; and --decision must be an existing FILE under the feature
    directory (review F6 parity — the one rule feature-record.py's raise-cycles/set-rework
    apply, reused rather than restated). All refused here, before anything is written, because
    a signature with no auditable ruling is exactly the half-state SC-15 exists to prevent."""
    rework, decision = getattr(args, "rework", None), getattr(args, "decision", None)
    if rework is None and decision is None:
        return None, None
    ruling = _parse_rework(rework, decision)
    feature_json = os.path.join(os.path.dirname(resolved), "feature.json")
    if not os.path.isfile(feature_json):
        _die(2, f"plan-merge: {feature_json} does not exist, so the rework ruling has nowhere "
                "to go — REFUSING to sign. Create the feature's feature.json first.")
    try:
        _feature_record_module()._require_decision_file(feature_json, ruling["decision"],
                                                       "sign-approval --rework")
    except harness_merge.MergeRefusal as refusal:
        _die(2, *refusal.lines)
    return ruling, feature_json


def _feature_record_module():
    """feature-record.py as a module: the hyphen keeps it out of `import`, like check-plan-routes.
    Loaded through the one bin loader (FEAT-61 T-02), unregistered: it declares no dataclass."""
    return harness_boundary.load_repo_module(
        "feature_record", os.path.join(BIN_DIR, "feature-record.py"))


def _record_rework(feature_json, ruling):
    """Set `rework` on the sibling feature.json through the one locked, schema-checked writer
    (feature_json_write, C1). A refusal there propagates its own code."""
    def transform(base):
        doc = feature_json_write.parse_doc(base, feature_json)
        if doc is None:
            raise harness_merge.MergeRefusal(
                feature_json_write.SCHEMA_REFUSAL_CODE,
                [f"REFUSED: {feature_json} vanished between the existence check and the write."])
        doc["rework"] = ruling
        return json.dumps(doc, indent=2) + "\n"

    try:
        feature_json_write.write_feature_json(feature_json, transform)
    except harness_merge.MergeRefusal as refusal:
        _die(refusal.code, *refusal.lines)


SIGNED_TASK_FIELDS = ("files", "intent", "verify")


def signed_task_hash(task):
    """BUG-1716 D-03: lowercase SHA-256 over the canonical UTF-8 JSON of a task's
    {files, intent, verify} — keys sorted recursively, `,`/`:` separators, ensure_ascii off.
    Presentation differences in the YAML (quoting, folding, ordering) hash the same; a
    changed value does not. check-state.py's INV-40 recomputes with THIS function."""
    doc = {field: task.get(field) for field in SIGNED_TASK_FIELDS}
    canonical = json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def signed_task_hashes(plan_doc):
    """{T-NN: hash} for every task in `plan_doc` that carries a string id."""
    return {str(task["id"]): signed_task_hash(task)
            for task in (plan_doc.get("tasks") or []) if isinstance(task, dict) and task.get("id")}


def _record_signed_task_hashes(resolved, plan_doc):
    """Write `signed_task_hashes` for the plan being signed onto the sibling feature.json.

    Absent feature.json: loud on stderr and the signature proceeds — a plan with no ledger is
    not a harness feature INV-40 will ever grade (fixtures and pre-ledger plans), and refusing
    would make sign-approval unusable exactly there. Any other refusal aborts the signature."""
    feature_json = os.path.join(os.path.dirname(resolved), "feature.json")
    if not os.path.isfile(feature_json):
        print(f"plan-merge: NO-HASHES — {feature_json} is absent, so signed_task_hashes were "
              "not recorded and INV-40 cannot grade this plan's task text.", file=sys.stderr)
        return
    hashes = signed_task_hashes(plan_doc)

    def transform(base):
        doc = feature_json_write.parse_doc(base, feature_json)
        if doc is None:
            raise harness_merge.MergeRefusal(
                feature_json_write.SCHEMA_REFUSAL_CODE,
                [f"REFUSED: {feature_json} vanished between the existence check and the write."])
        doc["signed_task_hashes"] = hashes
        return json.dumps(doc, indent=2) + "\n"

    feature_json_write.write_feature_json(feature_json, transform)
    print(f"HASHED {len(hashes)} task(s) -> {feature_json}")
