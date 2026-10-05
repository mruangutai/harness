"""`amend`: one field on one item, under a compare-and-swap hash. (FEAT-70)"""
import hashlib
import os
import sys
import yaml
from datetime import datetime, timezone

import artifact_accessors
import harness_merge
import harness_yaml
from plan_merge.amendments import write_plan_and_ledger
from plan_merge.stations import APPROVAL_RESET_LINE
from plan_merge.text import (
    _UNPARSEABLE, _dedent_value, _expected_value, _field_block, _item_range, _parsed_value,
    _render_field, _structured_field_lines,
)
from plan_merge.guards import (
    _die, _locked_plan_update, _refuse_illegal_amendment, _refuse_illegal_anchors,
    _reload_or_refuse, _resolve_plan, _sole_item,
)

def _verify_amend(spliced_bytes, key, iid, field, want):
    """Refuse rather than write an amendment that does not reload as the one asked for.

    THE DISCIPLINE `cmd_sign_approval` ALREADY HELD, and `amend` did not inherit (BUG-1128
    panel V3). The compare-and-swap protects CONTENT: it proves the block being replaced is
    the block that was read. It says nothing about LOCATION or RESULT, because both hashes are
    computed over whatever the locator returned — so they agree perfectly on the wrong block,
    and a splice into the wrong field reports success at exit 0.

    IT COMPARES VALUES, NOT SYNTAX, for the same reason `_verify_signature` does: a wrong-field
    write and a silently re-formed value both leave a document that parses.

    It CANNOT see a boundary error — `_trim_tail` owns that (panel N1) — because a deleted
    adjacent comment leaves the amended value exactly as asked.
    """
    reloaded = _reload_or_refuse(spliced_bytes)
    item = _sole_item(reloaded, key, iid)
    if item.get(field) != want:
        raise harness_merge.MergeRefusal(
            5, [f"REFUSED: the amendment does not reload as written — {iid}.{field} would not "
                "say what was asked for. This is the wrong-field write the content hash cannot "
                "see.",
                f"  asked for: {want!r}",
                f"  reloads as: {item.get(field)!r}"])
    return reloaded


# ---------------------------------------------------------------------------
# BUG-1128 — `amend`, the route that did not exist.
#
# FEAT-41 T-09 denies every Edit/Write to a plan.yaml for every author, and `apply`
# was ADD-ONLY (exit 7 on a changed value — FEAT-59 SC-08 has since made a proposal's
# fields replace the base's; `amend` remains the hash-checked route for a single field
# on a plan another writer may be touching). Correct separately; together they left a
# signed plan uncorrectable by anyone, and FEAT-46 accumulated eight staged-but-
# unappliable amendment blocks. This is the same shape BUG-1080 fixed one layer up:
# a rule shipped without reconciling what it makes impossible.
#
# IT IS A COMPARE-AND-SWAP, NOT A WRITE. `--show` prints the field block and its
# sha256; a replace must name that hash. The lock alone cannot help here: a caller
# that read the field, thought, and then wrote would clobber a concurrent edit while
# holding the lock perfectly. The hash is what makes the read part of the promise.
#
# IT REACHES `decisions:`. FEAT-46's worst overclaims are D-05 and D-14, so a
# task-scoped verb would leave exactly the blocks that motivated it unreachable.
# `approval:` is NOT reachable: it is the main session's alone (DEC-120) and
# `sign-approval` is its only writer.
AMENDABLE_KEYS = ("tasks", "decisions")


def _amend_locate(args, resolved, lines):
    """(first, last, indent) for the field named by `args`, or a refusal.

    Both refusals name what IS present, because a caller who mistyped needs the real list
    rather than a bare no. The id list is scoped to `--key`, the precedent
    `_task_status_line` set: offering decision ids for a `--key tasks` miss invites a retry
    that fails for an unrelated reason.
    """
    start, end, info = _item_range(lines, args.key, args.id)
    if start is None:
        _die(3, f"plan-merge: {args.id} is not under {args.key}: in {resolved} — it carries: "
                f"{', '.join(info) or '(none)'}")
    located = _field_block(lines, start, end, info, args.field)
    if located is None:
        _die(4, f"plan-merge: {args.id} carries no {args.field}: field. amend REPLACES; adding "
                f"a field is apply's job, and a verb that silently grows a plan is how it "
                f"acquires a key nobody reviewed.")
    return located


def _require_locked_hash(block_lines, expected, iid, field):
    """Refuse unless the block under the lock still hashes to what the caller named.

    THE CHECK THAT IS ACTUALLY LOAD-BEARING. The pre-lock check gives the caller a fast,
    precise refusal; this one is the guarantee, because only here are the bytes known not to be
    changing underneath. A caller that read a field, thought about it, and then wrote would
    otherwise clobber a concurrent edit while holding the lock perfectly.

    EXTRACTED SO IT CAN BE PINNED (panel F2). It survived being mutated out at 0 of 244 FAIL
    for four consecutive cycles, because nothing could reach it: reproducing the race
    end-to-end needs two processes interleaved inside one flock. As a named function it is
    unit-testable, which is the same remedy `_verify_amend` got for the same reason.
    """
    if hashlib.sha256("".join(block_lines).encode("utf-8")).hexdigest() != expected:
        raise harness_merge.MergeRefusal(
            6, [f"plan-merge: {iid}.{field} changed between the read and the lock."])


def _amend_show(lines, located, field, actual, raw, key, iid, yaml_value=False):
    """Print the field value and its hash, preserving structured values only by opt-in."""
    first, last, indent = located
    value = _parsed_value(raw, key, iid, field)
    if value is _UNPARSEABLE:
        sys.stderr.write("plan-merge: this plan does not parse, so the value below is derived "
                         "from raw lines and may not match what YAML would load. It is shown to "
                         "help you repair the document, not to be fed back verbatim.\n")
        sys.stdout.write(_dedent_value(lines[first:last], indent, field))
    elif isinstance(value, str):
        sys.stdout.write(value if value.endswith("\n") else value + "\n")
    elif yaml_value and isinstance(value, (list, dict)):
        sys.stdout.write(yaml.safe_dump(value, sort_keys=False))
    else:
        _die(4, f"plan-merge: {iid}.{field} is a {type(value).__name__}, not text. amend "
                f"replaces TEXT scalars unless --yaml-value explicitly selects a list or "
                f"mapping field.")
    print(f"sha256: {actual}")
    sys.exit(0)


def _load_structured_value(path):
    try:
        value = harness_yaml.load_file(path)
    except harness_yaml.YamlParseError as exc:
        _die(5, f"plan-merge: cannot load structured value from {path}: {exc}")
    if not isinstance(value, (list, dict)):
        _die(5, "plan-merge: --yaml-value requires a YAML list or mapping")
    return value


def _amend_preconditions(args, actual):
    """Refuse a replace that is missing its expectation, or naming a stale one."""
    if not args.expect_sha256 or not args.value_file:
        _die(2, "plan-merge: a replace needs BOTH --expect-sha256 and --value-file. Omitting "
                "the hash would make this a force-write, which is the hand-edit T-09 denies "
                "wearing a tool's name. Run --show first.")
    if args.expect_sha256 != actual:
        _die(6, f"plan-merge: --expect-sha256 does not match {args.id}.{args.field} — the field "
                f"changed since you read it. expected {args.expect_sha256} actual sha256: "
                f"{actual}. Re-run --show and re-derive your replacement.")


def _amended_text(cur, first, last, rendered, want, args, base_doc, result):
    """The plan text with the field spliced in, the C4 guards applied.

    A `files:` replacement is held to plan_anchors' grammar — a line-number anchor is refused
    here as it is in `apply`. Replacing a field on an existing item leaves the signature
    standing (BUG-1716 D-04): the task set is unchanged, and a task-text change without a
    ledgered amendment is INV-40's finding. `result["reset"]` stays False for the receipt."""
    if args.field == "files":
        _refuse_illegal_anchors({"tasks": [{"id": args.id, "files": want}]},
                                f"the replacement for {args.id}.files")
    result["reset"] = False
    return "".join(cur[:first] + rendered + cur[last:])


def _amend_request(args):
    """(want_value, value_text): a structured replacement loaded from --value-file, or the
    text one read verbatim. (FEAT-70, from cmd_amend)"""
    if args.yaml_value:
        return _load_structured_value(args.value_file), None
    with open(args.value_file, encoding="utf-8") as fh:
        return None, fh.read()


def _locate_under_lock(cur, args):
    """(first, last, indent) of the field under the lock, or the two vanished refusals.
    (FEAT-70, from cmd_amend.transform)"""
    s2, e2, i2 = _item_range(cur, args.key, args.id)
    if s2 is None:
        raise harness_merge.MergeRefusal(
            3, [f"plan-merge: {args.id} vanished from {args.key}: under the lock."])
    loc2 = _field_block(cur, s2, e2, i2, args.field)
    if loc2 is None:
        raise harness_merge.MergeRefusal(
            4, [f"plan-merge: {args.id}.{args.field} vanished under the lock."])
    return loc2


def _amend_rendered(cur, raw, f2, l2, ind2, args, want_value, value_text):
    """(rendered lines, expected reload value) for the replacement at [f2, l2) with field indent
    `ind2`. (FEAT-70, from cmd_amend.transform)"""
    if not args.yaml_value:
        rendered = _render_field(ind2, args.field, value_text, cur[f2:l2])
        return rendered, _expected_value(rendered, ind2, args.field)
    current = _parsed_value(raw, args.key, args.id, args.field)
    if not isinstance(current, (list, dict)):
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: {args.id}.{args.field} is not a list or mapping under "
                "the lock; --yaml-value cannot change a scalar field's type."])
    return _structured_field_lines(ind2, args.field, want_value), want_value


def _amend_preflight(args):
    """Everything before the lock: the key vocabulary, destination, the field's current bytes
    and hash, `--show`, and the compare-and-swap preconditions. Returns the resolved plan path.
    (FEAT-70, from cmd_amend)"""
    if args.key not in AMENDABLE_KEYS:
        _die(2, f"plan-merge: --key {args.key} is not amendable — expected one of: "
                f"{', '.join(AMENDABLE_KEYS)}. `approval:` is the main session's alone "
                f"(DEC-120) and sign-approval is its only writer.")

    resolved = _resolve_plan(args.file)
    with open(resolved, "rb") as fh:
        raw = fh.read().decode("utf-8")
    lines = raw.splitlines(keepends=True)
    located = _amend_locate(args, resolved, lines)
    first, last, _ = located
    actual = hashlib.sha256("".join(lines[first:last]).encode("utf-8")).hexdigest()

    if args.show:
        _amend_show(lines, located, args.field, actual, raw, args.key, args.id,
                    yaml_value=args.yaml_value)
    _amend_preconditions(args, actual)
    return resolved


# #1985 — the signed text changes only with its ledger entry. INV-40 (d) flags a task whose
# intent/files/verify no longer hash to what sign-approval recorded unless judgements[] carries
# an amendment naming that task. `record-amendments` always wrote one; `amend` wrote none, so
# every amend of a signed field manufactured an INV-40 finding with nobody's reason on record.
# Exactly that case is ledgered here — the same field set and the same signed_task_hashes
# INV-40 grades — so pre-signature planning edits add no noise to the operator's audit.
LEDGERED_FIELDS = ("intent", "files", "verify")


def _ledgered_target(args, resolved):
    """feature.json's path when this replace changes a signed task field, else None."""
    if args.key != "tasks" or args.field not in LEDGERED_FIELDS:
        return None
    feature_json = os.path.join(os.path.dirname(resolved), "feature.json")
    try:
        record = artifact_accessors.load_feature_json(feature_json)
    except artifact_accessors.FeatureJsonError as error:
        _die(2, f"plan-merge: cannot tell whether {args.id}.{args.field} is signed text — {error}")
    signed = record.get("signed_task_hashes") if isinstance(record, dict) else None
    return feature_json if isinstance(signed, dict) and args.id in signed else None


def _amend_judgement(args):
    if not (args.reason or "").strip():
        _die(2, f"plan-merge: {args.id}.{args.field} is signed text, so the change is ledgered "
                "as an amendment judgement (INV-40) — supply --reason saying why it changed.")
    return {"at": datetime.now(timezone.utc).isoformat(timespec="microseconds"),
            "by": os.environ.get("HARNESS_AGENT_TYPE") or "main-session",
            "kind": "amendment", "decision": f"{args.id}.{args.field}",
            "reason": args.reason.strip()}


def cmd_amend(args):
    resolved = _amend_preflight(args)
    ledger = _ledgered_target(args, resolved)
    judgement = _amend_judgement(args) if ledger else None
    want_value, value_text = _amend_request(args)
    result = {}

    def transform(base_bytes):
        # THE BASE IS PARSED FIRST (panel V4, and its own de-vacuumed test). It used to be
        # parsed last, outside a try, so a broken plan either crashed with a traceback or was
        # reported as "a splice defect: the base parsed" — which was false. Repairing a plan
        # nobody else may edit is this verb's whole purpose, so an unreadable base must refuse
        # cleanly and say which document is at fault.
        raw = base_bytes.decode("utf-8")
        try:
            base_doc = harness_yaml.load_str(raw, "<base plan>")
        except harness_yaml.YamlParseError as exc:
            raise harness_merge.MergeRefusal(
                8, [f"plan-merge: the plan on disk does not parse, so amend cannot tell whether "
                    f"its own splice made things worse — {exc}"])
        cur = raw.splitlines(keepends=True)
        f2, l2, ind2 = _locate_under_lock(cur, args)
        _require_locked_hash(cur[f2:l2], args.expect_sha256, args.id, args.field)
        rendered, want = _amend_rendered(cur, raw, f2, l2, ind2, args, want_value, value_text)
        spliced = _amended_text(cur, f2, l2, rendered, want, args, base_doc, result)
        reloaded = _verify_amend(spliced.encode("utf-8"), args.key, args.id, args.field, want)
        # DO NO HARM: hold the splice to the plan schema only when the BASE satisfied it. A plan
        # mid-authoring legitimately does not, and refusing to amend it would make this verb
        # useless exactly where it is needed most.
        _refuse_illegal_amendment(base_doc, reloaded)
        return spliced.encode("utf-8")

    try:
        if ledger:
            write_plan_and_ledger(resolved, ledger, transform, [judgement])
        else:
            _locked_plan_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        _die(refusal.code, *refusal.lines)
    print(f"AMENDED {args.key}:{args.id}.{args.field}"
          + (" judgement=amendment" if ledger else ""))
    if result.get("reset"):
        print(APPROVAL_RESET_LINE)
    print(f"APPLIED {resolved}")
    if ledger:
        print(f"APPLIED {ledger}")
    sys.exit(0)
