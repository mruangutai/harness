"""`apply` / `add-tasks`: the locked union merge and its self-checks. (FEAT-70)"""
import sys
import yaml

import harness_merge
import harness_yaml
from plan_merge.stations import APPROVAL_RESET_LINE, FEATURE_LINE_RE, _maybe_reset_approval
from plan_merge.text import (
    DASH_RE, _field_block, _field_indent, _field_lines, _index_list_items, _index_top_keys,
    _item_delete_end, _item_id, _item_indent, _key_head, _last_nonblank, _reindent,
    _structured_field_lines,
)
from plan_merge.guards import (
    _locked_plan_update, _refuse_illegal_anchors, _resolve_plan, _schema_error, _sole_item,
)

# Module-level literals. Each is mutated BY NAME in a copy of the tree by the test's red proofs.
# Nothing outside this file's source text ever flips one — no environment variable, no flag.

# Guards step 6 (task/decision union merge). False reproduces today's naive last-writer-wins:
# the proposal's bytes replace the file whole, with no comparison against the base at all.
UNION_MERGE = True


# Guards step 7 (approval is always the base's bytes, verbatim). False renders the WHOLE output
# through yaml.safe_dump instead of splicing text — what a naive implementation does, and what
# the byte-identity test must reject: a dumper round trip destroys comments and normalises
# quoting.
PRESERVE_BASE_BYTES = True


# Guards step 7b (the structural refusal). False skips the parsed-approval comparison entirely,
# so step 7 alone decides and a proposal carrying a different signed approval is silently
# dropped instead of refused.
APPROVAL_REFUSAL = True


UNION_KEYS = ("tasks", "decisions")


def _verify_spliced(spliced_bytes, base_doc, prop_doc, out_order, added_ids, replaced=()):
    """Refuse rather than return a splice that does not reload as the merge it reported.

    `replaced` is [(key, iid, base_item, changes)] for every existing item the proposal
    changed, `changes` being the (iid, field, old, new) rows the receipt will print. Each item
    must reload as the BASE item with exactly those fields at their new values — the fields the
    proposal omitted intact, a proposal `status` NOT laid over (review F7) — because a field
    splice one line long or one line short still parses (the `_verify_amend` lesson)."""
    reloaded = _reload_spliced(spliced_bytes)
    _verify_schema_preserved(base_doc, reloaded)
    _verify_union_ids(reloaded, base_doc, prop_doc, out_order)
    _verify_replaced(reloaded, replaced)
    return reloaded


def _reload_spliced(spliced_bytes):
    """The spliced bytes as a mapping, or the two parse refusals verbatim. (FEAT-70, from
    _verify_spliced)"""
    try:
        reloaded = harness_yaml.load_str(spliced_bytes.decode("utf-8"), "<merged plan>")
    except harness_yaml.YamlParseError as exc:
        raise harness_merge.MergeRefusal(
            5,
            [
                "UNPARSEABLE: the merged plan does not load — REFUSING to write it.",
                f"  {exc}",
                "  this is a splice defect, not a bad proposal: both inputs parsed.",
            ],
        )
    if not isinstance(reloaded, dict):
        raise harness_merge.MergeRefusal(
            5, ["UNPARSEABLE: the merged plan is not a mapping — REFUSING to write it."]
        )
    return reloaded


def _verify_schema_preserved(base_doc, reloaded):
    """The do-no-harm schema rule: a legal base must reload legal. (FEAT-70, from
    _verify_spliced)"""
    # AND IT MUST BE A LEGAL PLAN, NOT MERELY LEGAL YAML (FEAT-41 HIGH-1). `safe_load` above
    # answers "is this YAML"; the schema answers "can a reader act on it". Without this, `apply`
    # minted `station_only: true` onto a task-bearing signed plan, reported APPLIED, exited 0, and
    # left a document no reader can load. Same shape as the splice defect STEP 9 exists for.
    #
    # THE SCHEMA HAS ONE HOME. `validate_plan_doc` is the function `load_plan` itself calls, so
    # the writer cannot drift from the reader; a copy of the rules here would be a second place
    # for them to stop being true.
    # DO NO HARM, RATHER THAN DEMAND PERFECTION. Refusing every merge whose RESULT fails the
    # schema would block legitimate repair of a plan that was already non-conforming -- measured:
    # 21 existing cases went red that way, all with bases whose tasks predate REQUIRED_TASK_FIELDS.
    # So the test is whether this MERGE introduces a violation: valid before, invalid after.
    if _schema_error(base_doc) is None:
        _err = _schema_error(reloaded)
        if _err is not None:
            raise harness_merge.MergeRefusal(
                5,
                ["ILLEGAL PLAN: this merge would make a legal plan illegal — REFUSING to write it.",
                 f"  {_err}",
                 "  the base satisfied the plan schema and the merged result does not, so the "
                 "change itself is what the schema refuses."],
            )


def _expected_union_ids(base_doc, prop_doc, key):
    """Base ids in order, then the proposal's ids not already present. (FEAT-70, from
    _verify_spliced)"""
    want = [_item_id(i) for i in (base_doc.get(key) or [])]
    for item in prop_doc.get(key) or []:
        iid = _item_id(item)
        if iid not in want:
            want.append(iid)
    return want


def _verify_union_ids(reloaded, base_doc, prop_doc, out_order):
    """Every union key in `out_order` reloads with exactly the computed ids, in order. (FEAT-70,
    from _verify_spliced)"""
    for key in UNION_KEYS:
        if key not in out_order:
            continue
        want = _expected_union_ids(base_doc, prop_doc, key)
        got = [_item_id(i) for i in (reloaded.get(key) or [])]
        if got != want:
            raise harness_merge.MergeRefusal(
                5,
                [
                    f"UNPARSEABLE: '{key}' does not reload as the merge that was computed — "
                    "REFUSING to write it.",
                    f"  expected ids: {want!r}",
                    f"  reloaded ids: {got!r}",
                ],
            )

def _verify_replaced(reloaded, replaced):
    """Each replaced item must reload as the BASE item with the REPORTED changes laid over it."""
    for key, iid, base_item, changes in replaced:
        want_item = dict(base_item)
        want_item.update({field: new for _iid, field, _old, new in changes})
        got_item = _sole_item(reloaded, key, iid)
        if got_item != want_item:
            raise harness_merge.MergeRefusal(
                5,
                [f"UNPARSEABLE: id={iid!r} in '{key}' does not reload as the base item with the "
                 "proposal's fields replaced — REFUSING to write it.",
                 f"  expected: {want_item!r}",
                 f"  reloaded: {got_item!r}"],
            )


def _proposal_field_lines(prop_lines, ps, pe, prop_dash, field, value, indent, iid, key):
    """The proposal's OWN lines for `field`, re-indented to the base item — or, when the field
    sits on the proposal's dash line and cannot be located as a block, the value rendered.

    Copying the author's bytes keeps a `verify: |` block a block and a hand-written list a
    list; rendering is the fallback, never the default, for the reason `_render_field` gives."""
    located = _field_block(prop_lines, ps, pe, prop_dash, field)
    if located is not None:
        first, last, prop_indent = located
        return _reindent(prop_lines[first:last], len(indent) - len(prop_indent), iid, key)
    if isinstance(value, (list, dict)):
        return _structured_field_lines(indent, field, value)
    # One element per physical line, the contract `_render_field` keeps (FEAT-70 SC-03).
    return _field_lines(indent, field, value).splitlines(keepends=True)


def _splice_field(lines, dash_indent, field, rendered):
    """`lines` (one item) with `field` replaced by `rendered`, or `rendered` added after the
    item's last own line — before any trailing blank or comment — when the item lacks it."""
    located = _field_block(lines, 0, len(lines), dash_indent, field)
    if located is None:
        own_end = _item_delete_end(lines, 0, len(lines), dash_indent)
        at = _last_nonblank(lines, 0, own_end)
        return lines[:at] + rendered + lines[at:]
    first, last, _indent = located
    return lines[:first] + rendered + lines[last:]


# A PROPOSAL'S `status` ON AN EXISTING ITEM IS IGNORED, NEVER LAID OVER THE BASE'S (review F7).
# The station is set-task-station's and gh-sync's during build; a pm proposal re-applied after
# build entry (to add T-05, say) still carries the `pending` it was drafted with, and laying
# that over `building` rolled the station back — and, counted as a task change, voided the
# signature mid-build. `id` is the item's identity and is never a field to replace.
STATION_FIELD = "status"


def _replace_fields(base_lines, s, e, item, prop_lines, ps, pe, pitem, iid, key):
    """The base item's lines with every field the proposal names replaced or added, plus
    [(iid, field, old, new)] per change and the same tuple per IGNORED `status`. Fields the
    proposal omits are untouched bytes.

    THIS IS WHAT RETIRES apply's EXIT 7 (FEAT-59 SC-08). A changed value is a splice of that
    field's lines only — the same one-block replace `amend` does, without the hash handshake,
    because `apply` is the plan author's own verb and the lock already serialises writers."""
    lines = list(base_lines[s:e])
    dash_indent = DASH_RE.match(lines[0]).group(1)
    prop_dash = DASH_RE.match(prop_lines[ps]).group(1)
    indent = _field_indent(lines, dash_indent)
    changed, ignored = _differing_fields(item, pitem)
    for field, value in changed:
        rendered = _proposal_field_lines(prop_lines, ps, pe, prop_dash, field, value, indent,
                                         iid, key)
        lines = _splice_field(lines, dash_indent, field, rendered)

    def rows(pairs):
        return [(iid, field, item.get(field, _ABSENT), value) for field, value in pairs]

    return lines, rows(changed), rows(ignored)


def _differing_fields(item, pitem):
    """(changed, ignored): the proposal's (field, value) pairs that differ from the base item,
    `id` excluded, split into the ones to splice and the STATION_FIELD ones never laid over.
    (FEAT-70, from _replace_fields)"""
    changed, ignored = [], []
    for field, value in pitem.items():
        if field == "id" or item.get(field, _ABSENT) == value:
            continue
        (ignored if field == STATION_FIELD else changed).append((field, value))
    return changed, ignored


# A field the base item does not carry, for the REPLACED receipt. Distinct from None, which is
# a legal YAML value a field can hold.
_ABSENT = object()


class MergeResult:
    """What `apply_merge` computed, for the receipt `cmd_apply` prints.

    added / preserved: item ids. replaced: (iid, field, old, new) per replaced field, `old`
    being _ABSENT for a field the base item did not carry. ignored: the same tuple per
    proposal `status` that was NOT written (review F7). reset: approval was voided."""

    def __init__(self, out_bytes, added, preserved, ignored_approval, replaced=(), reset=False,
                 ignored=()):
        self.out_bytes = out_bytes
        self.added = added
        self.preserved = preserved
        self.ignored_approval = ignored_approval
        self.replaced = list(replaced)
        self.reset = reset
        self.ignored = list(ignored)


def apply_merge(base_bytes, proposal_text, verb="apply"):
    """The whole algorithm. Returns a MergeResult. Raises harness_merge.MergeRefusal(2|5|7|8)
    with nothing to write, per plan-merge.py's contract with harness_merge.locked_update: a
    raised MergeRefusal leaves the file untouched. `verb` is the command-line name, recorded
    in approval.reset_reason when this merge voids a signature."""
    if base_bytes is None:
        return MergeResult(_seed_new_plan(proposal_text), [], [], False)
    base_doc, prop_doc, base_text = _merge_inputs(base_bytes, proposal_text)

    if not UNION_MERGE:
        # Step 5, off: today's last-writer-wins, verbatim.
        return MergeResult(proposal_text.encode("utf-8"), [], [], False)

    ignored_approval = _refuse_approval_conflict(base_doc, prop_doc)
    out_order, out_text, added_ids, preserved_ids, replaced, changed_tasks, ignored = _merge_keys(
        base_text, proposal_text, base_doc, prop_doc)
    spliced_text, reset = _maybe_reset_approval(out_text, base_doc, verb, changed_tasks)
    changes = _replaced_fields(replaced)
    out_bytes = _final_bytes(spliced_text, base_doc, prop_doc, out_order, added_ids, replaced)
    return MergeResult(out_bytes, added_ids, preserved_ids, ignored_approval, changes, reset, ignored)


def _merge_keys(base_text, proposal_text, base_doc, prop_doc):
    """Every top-level key in merged order, each through `_merge_key`, with the per-key lists
    concatenated in that order: (out_order, out_text, added, preserved, replaced,
    changed_tasks, ignored)."""
    base = _index_top_keys(base_text)
    prop = _index_top_keys(proposal_text)
    out_order = _merged_key_order(base[1], prop[1])
    chunks, added_ids, preserved_ids, replaced, changed_tasks, ignored = _fold_merge_rows(
        _merge_key(key, base, prop, base_doc, prop_doc) for key in out_order)
    return (out_order, "".join([*base[3], *chunks]), added_ids, preserved_ids, replaced,
            changed_tasks, ignored)


def _replaced_fields(replaced):
    """MergeResult's `replaced`: the (iid, field, old, new) rows of every replaced item, flat."""
    return [change for _key, _iid, _item, item_changes in replaced for change in item_changes]


def _fold_merge_rows(rows):
    """The per-key results' six lists, each concatenated in key order."""
    chunks, added, preserved, replaced, changed_tasks, ignored = [], [], [], [], [], []
    for row_chunks, row_added, row_preserved, row_replaced, row_changed, row_ignored in rows:
        chunks += row_chunks
        added += row_added
        preserved += row_preserved
        replaced += row_replaced
        changed_tasks += row_changed
        ignored += row_ignored
    return chunks, added, preserved, replaced, changed_tasks, ignored


def _final_bytes(spliced_text, base_doc, prop_doc, out_order, added_ids, replaced):
    """The bytes to write: the verified splice, or the safe_dump rendering when preservation is off."""
    spliced_bytes = spliced_text.encode("utf-8")
    if PRESERVE_BASE_BYTES:
        # STEP 9: THE RESULT IS PARSED BEFORE IT IS WRITTEN, and this guard is general.
        # Steps 5-8 parse the BASE and the PROPOSAL; nothing parsed the OUTPUT, so a splice
        # defect could — and on 2026-08-31 did — write a signed plan that PyYAML cannot load
        # while printing ADDED and exiting 0. A tool whose whole promise is "the base's bytes
        # survive" must not be able to hand back bytes that are not a plan.
        #
        # It also checks the MERGE, not merely the syntax: every id the caller is about to be
        # told was added or preserved must actually be present in the reloaded document, and
        # every replaced item must reload as base-with-the-reported-changes. A splice that
        # lands text in the wrong block can still parse.
        _verify_spliced(spliced_bytes, base_doc, prop_doc, out_order, added_ids, replaced)
        return spliced_bytes

    # PRESERVE_BASE_BYTES off: what a naive implementation does — render the whole merged
    # document through yaml.safe_dump instead of splicing. Comments and quoting do not survive
    # this path; that is exactly the property the red proof grades.
    return _dump_merged(base_doc, prop_doc, out_order)


def _seed_new_plan(proposal_text):
    """The bytes for a plan with no base: the proposal with a pending approval seeded."""
    # A new plan needs an unsigned approval mapping before the main session can later sign it.
    # The proposal may not supply that mapping: accepting any caller-owned value would let
    # `apply` mint an approved plan, bypassing cmd_sign_approval's identity gate.
    prop_doc = _parsed_proposal(proposal_text)
    if APPROVAL_REFUSAL and "approval" in prop_doc:
        raise harness_merge.MergeRefusal(
            8,
            [
                "REFUSED: proposal carries an approval mapping and the base does not exist.",
                "  base approval: <absent>",
                f"  proposal approval: {prop_doc.get('approval')!r}",
                "  apply seeds a fixed pending mapping; only the main session may approve it through sign-approval.",
            ],
        )
    lines = proposal_text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if FEATURE_LINE_RE.match(line):
            lines[index + 1:index + 1] = ["approval:\n", "  status: pending\n"]
            return "".join(lines).encode("utf-8")
    raise harness_merge.MergeRefusal(
        5, ["UNPARSEABLE: proposal carries no top-level feature: key to anchor approval."]
    )


def _merge_inputs(base_bytes, proposal_text):
    """(base_doc, prop_doc, base_text), both documents parsed and the proposal's anchors checked."""
    base_text = base_bytes.decode("utf-8")
    try:
        base_doc = harness_yaml.load_str(base_text, "<base plan>")
    except harness_yaml.YamlParseError as exc:
        raise harness_merge.MergeRefusal(5, [f"UNPARSEABLE: base failed to parse: {exc}"])
    prop_doc = _parsed_proposal(proposal_text)
    base_doc = base_doc if isinstance(base_doc, dict) else {}
    return base_doc, prop_doc, base_text


def _parsed_proposal(proposal_text):
    """The proposal as a mapping with its anchors checked, or the exit-5 refusal."""
    try:
        prop_doc = harness_yaml.load_str(proposal_text, "<proposal>")
    except harness_yaml.YamlParseError as exc:
        raise harness_merge.MergeRefusal(5, [f"UNPARSEABLE: proposal failed to parse: {exc}"])
    prop_doc = prop_doc if isinstance(prop_doc, dict) else {}
    _refuse_illegal_anchors(prop_doc, "the proposal")
    return prop_doc


def _refuse_approval_conflict(base_doc, prop_doc):
    """Whether the proposal's approval is ignored because the base carries its own."""
    base_has_approval = "approval" in base_doc
    prop_has_approval = "approval" in prop_doc
    base_approval = base_doc.get("approval")
    prop_approval = prop_doc.get("approval")

    # Step 7b: THE STRUCTURAL REFUSAL. Compares PARSED values, never text.
    if (
        APPROVAL_REFUSAL
        and base_has_approval
        and prop_has_approval
        and prop_approval != base_approval
    ):
        raise harness_merge.MergeRefusal(
            8,
            [
                "REFUSED: proposal's approval mapping differs from the base's.",
                f"  base approval: {base_approval!r}",
                f"  proposal approval: {prop_approval!r}",
                "  the signer is the main session; plan-merge.py never writes approval.",
            ],
        )
    ignored_approval = base_has_approval and prop_has_approval
    return ignored_approval


def _merged_key_order(base_order, prop_order):
    out_order = list(base_order)
    for key in prop_order:
        if key not in out_order:
            out_order.append(key)
    return out_order


def _merge_key(key, base, prop, base_doc, prop_doc):
    """One top-level key's (chunks, added, preserved, replaced, changed_tasks, ignored).
    `base` and `prop` are `_index_top_keys` results: (lines, order, ranges, preamble)."""
    base_lines, _base_order, base_ranges, _base_preamble = base
    prop_lines, _prop_order, prop_ranges, _prop_preamble = prop
    if key == "approval":
        # Step 7: the base's line range, byte for byte, always. If the base has no
        # approval block at all, this tool still never writes one — there is nothing to
        # carry forward, and the proposal's is ignored the same as everywhere else.
        if "approval" in base_doc:
            s, e = base_ranges["approval"]
            return ["".join(base_lines[s:e])], [], [], [], [], []
        return [], [], [], [], [], []
    if key in UNION_KEYS:
        return _merge_union_key(key, (base_lines, base_ranges, base_doc),
                                (prop_lines, prop_ranges, prop_doc))
    chunk = _merge_plain_key(key, (base_lines, base_ranges, base_doc), (prop_lines, prop_ranges, prop_doc))
    return chunk, [], [], [], [], []


def _merge_union_key(key, base, prop):
    """A union key's (chunks, added, preserved, replaced, changed_tasks, ignored); `base` and
    `prop` are (lines, ranges, doc)."""
    base_list, base_item_ranges = _aligned_items(key, base)
    prop_list, prop_item_ranges = _aligned_items(key, prop)
    head = _union_key_head(key, base, prop, base_item_ranges, prop_item_ranges)
    if head is None:
        return [], [], [], [], [], []

    base_by_id, _base_id_order = _items_by_id(base_item_ranges, base_list)
    prop_by_id, prop_id_order = _items_by_id(prop_item_ranges, prop_list)
    chunks, preserved, replaced, ignored = _carry_base_items(
        key, base_by_id, prop_by_id, base[0], prop[0])
    # THE ADDITION IS RE-INDENTED TO THE BASE'S LIST, never appended verbatim. When
    # the base has no items of its own there is nothing to match, and the key head came
    # from the proposal too, so its own indentation is already consistent.
    shift = _indent_shift(base[0], base_item_ranges, prop[0], prop_item_ranges)
    added_chunks, added, changed_tasks = _add_new_items(
        key, prop_id_order, base_by_id, prop_by_id, prop[0], shift)
    return [head] + chunks + added_chunks, added, preserved, replaced, changed_tasks, ignored


def _aligned_items(key, side):
    """(parsed items, their text ranges) for one side — (lines, ranges, doc) — of a union key,
    or the alignment refusal."""
    lines, ranges, doc = side
    items = doc.get(key) or []
    item_ranges = _index_list_items(lines, ranges[key]) if key in ranges else []
    if len(item_ranges) != len(items):
        raise harness_merge.MergeRefusal(
            5,
            [
                f"UNPARSEABLE: could not align text ranges with parsed items for "
                f"'{key}' — the block's formatting is not one dash per item."
            ],
        )
    return items, item_ranges


def _union_key_head(key, base, prop, base_item_ranges, prop_item_ranges):
    """The key's head lines from whichever side carries it, base first; None when neither does."""
    base_lines, base_ranges, _base_doc = base
    prop_lines, prop_ranges, _prop_doc = prop
    if key in base_ranges:
        return _key_head(base_lines, base_ranges[key], base_item_ranges)
    if key in prop_ranges:
        return _key_head(prop_lines, prop_ranges[key], prop_item_ranges)
    return None


def _indent_shift(base_lines, base_item_ranges, prop_lines, prop_item_ranges):
    """Columns to shift a proposal item by to sit in the base's list, or None when a side has
    no items to measure."""
    base_indent = _item_indent(base_lines, base_item_ranges)
    prop_indent = _item_indent(prop_lines, prop_item_ranges)
    if base_indent is not None and prop_indent is not None:
        return base_indent - prop_indent
    return None


def _items_by_id(item_ranges, items):
    """({id: (start, end, item)}, ids in list order) — the order keeps a duplicate id's repeats."""
    by_id = {}
    id_order = []
    for (s, e), item in zip(item_ranges, items):
        iid = _item_id(item)
        by_id[iid] = (s, e, item)
        id_order.append(iid)
    return by_id, id_order


def _carry_base_items(key, base_by_id, prop_by_id, base_lines, prop_lines):
    """The base's items in base order — carried, preserved or field-replaced — as
    (chunks, preserved, replaced, ignored)."""
    chunks, preserved, replaced, ignored = [], [], [], []
    for iid, (s, e, item) in base_by_id.items():
        if iid not in prop_by_id:
            chunks.append("".join(base_lines[s:e]))
            continue
        ps, pe, pitem = prop_by_id[iid]
        if pitem == item:
            chunks.append("".join(base_lines[s:e]))
            preserved.append(iid)
            continue
        # THE PROPOSAL'S FIELDS REPLACE THE BASE'S, FIELD BY FIELD (FEAT-59 SC-08).
        # This was exit 7 CONFLICT, and it cost FEAT-54 an amend round trip per field.
        # A `status` that differs is IGNORED, not a change: an item whose only
        # difference is its station is neither replaced nor a reason to void approval.
        item_lines, changes, ignored_here = _replace_fields(
            base_lines, s, e, item, prop_lines, ps, pe, pitem, iid, key)
        chunks.append("".join(item_lines))
        ignored.extend(ignored_here)
        if not changes:
            continue
        replaced.append((key, iid, item, changes))
        # A REPLACED task field no longer voids the signature (BUG-1716 D-04): the
        # signed text is hashed in feature.json at signature, and an unledgered change
        # to it is INV-40's to refuse. Only the TASK SET resets approval now.
    return chunks, preserved, replaced, ignored


def _add_new_items(key, prop_id_order, base_by_id, prop_by_id, prop_lines, shift):
    """The proposal's items the base lacks, in proposal order, re-indented by `shift` when
    both sides have an indent to compare — as (chunks, added, changed_tasks)."""
    chunks, added, changed_tasks = [], [], []
    for iid in prop_id_order:
        if iid in base_by_id:
            continue
        s, e, _item = prop_by_id[iid]
        item_lines = prop_lines[s:e]
        if shift is not None:
            item_lines = _reindent(item_lines, shift, iid, key)
        chunks.append("".join(item_lines))
        added.append(iid)
        if key == "tasks":
            changed_tasks.append(iid)
    return chunks, added, changed_tasks


def _merge_plain_key(key, base, prop):
    """The chunk list for an ordinary top-level key: the base's bytes, or the proposal's when
    only it carries the key; two different values are the exit-7 CONFLICT."""
    base_lines, base_ranges, base_doc = base
    prop_lines, prop_ranges, prop_doc = prop
    # Step 8: every other top-level key.
    in_base = key in base_ranges
    in_prop = key in prop_ranges
    if in_base and in_prop:
        bval, pval = base_doc.get(key), prop_doc.get(key)
        if bval != pval:
            raise harness_merge.MergeRefusal(
                7,
                [
                    f"CONFLICT: top-level key '{key}' carries two different values.",
                    f"  base: {bval!r}",
                    f"  proposal: {pval!r}",
                ],
            )
    if in_base:
        s, e = base_ranges[key]
        return ["".join(base_lines[s:e])]
    if in_prop:
        s, e = prop_ranges[key]
        return ["".join(prop_lines[s:e])]
    return []


def _dump_merged(base_doc, prop_doc, out_order):
    """The PRESERVE_BASE_BYTES-off rendering: the merged document through yaml.safe_dump."""
    merged_doc = dict(base_doc)
    for key in (k for k in UNION_KEYS if k in out_order):
        merged_list = _merged_union_list(base_doc.get(key) or [], prop_doc.get(key) or [])
        if merged_list:
            merged_doc[key] = merged_list
    _carry_plain_keys(merged_doc, prop_doc)
    if "approval" in base_doc:
        merged_doc["approval"] = base_doc.get("approval")
    dumped = yaml.safe_dump(merged_doc, sort_keys=False, allow_unicode=True).encode("utf-8")
    return dumped


def _merged_union_list(base_list, prop_list):
    """The base's items followed by the proposal's whose ids the base lacks."""
    merged_list = list(base_list)
    seen = {_item_id(i) for i in base_list}
    for item in prop_list:
        iid = _item_id(item)
        if iid not in seen:
            merged_list.append(item)
            seen.add(iid)
    return merged_list


def _carry_plain_keys(merged_doc, prop_doc):
    """Add the proposal's ordinary keys the merged document lacks, in place."""
    for key in prop_doc:
        if key in UNION_KEYS or key == "approval":
            continue
        if key not in merged_doc:
            merged_doc[key] = prop_doc[key]


def cmd_apply(args):
    resolved = _resolve_plan(args.file)

    if args.proposal == "-":
        proposal_text = sys.stdin.read()
    else:
        with open(args.proposal, encoding="utf-8") as f:
            proposal_text = f.read()

    result = {}

    def transform(base_bytes):
        merged = apply_merge(base_bytes, proposal_text, args.cmd)
        result["merged"] = merged
        return merged.out_bytes

    try:
        _locked_plan_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)

    _print_apply_receipt(result["merged"])
    print(f"APPLIED {resolved}")
    sys.exit(0)


def _print_apply_receipt(merged):
    for eid in merged.added:
        print(f"ADDED {eid}")
    for eid in merged.preserved:
        print(f"PRESERVED {eid}")
    _print_field_rows(merged)
    if merged.reset:
        print(APPROVAL_RESET_LINE)
    if merged.ignored_approval:
        print("IGNORED-APPROVAL: proposal's approval block was not written; base's kept")


def _print_field_rows(merged):
    """The REPLACED and IGNORED lines of the receipt. (FEAT-70, from _print_apply_receipt)"""
    for iid, field, old, new in merged.replaced:
        was = "<absent>" if old is _ABSENT else repr(old)
        print(f"REPLACED {iid}.{field}: {was} -> {new!r}")
    for iid, field, old, new in merged.ignored:
        keeps = "none" if old is _ABSENT else repr(old)
        print(f"IGNORED {iid}.{field}: proposal's {new!r} was not written; the station is "
              f"set-task-station's (base keeps {keeps})")
