"""Line-indexing, field-extraction, render and splice primitives over plan.yaml text; every verb's byte-preserving edit is built from these. (FEAT-70)"""
import re
import yaml

import harness_merge
import harness_yaml

TOP_KEY_RE = re.compile(r"^([A-Za-z_][\w-]*):")


DASH_RE = re.compile(r"^(\s*)-\s")


def _index_top_keys(text):
    """Return (lines, order, ranges, preamble_lines).

    lines:     text.splitlines(keepends=True)
    order:     top-level key names in file order (first occurrence only)
    ranges:    {key: (start_line, end_line)} half-open, end exclusive
    preamble:  every line before the first top-level key (comments, blank lines) — always
               carried from the BASE side untouched; a proposal's preamble is never consulted.
    """
    lines = text.splitlines(keepends=True)
    positions = _top_key_positions(lines)
    order = [name for name, _ in positions]
    ranges = _half_open_ranges(positions, len(lines))
    preamble_end = positions[0][1] if positions else len(lines)
    return lines, order, ranges, lines[:preamble_end]


def _top_key_positions(lines):
    """[(name, line_index)] for the FIRST occurrence of each top-level key, in file order.
    (FEAT-70, from _index_top_keys)"""
    positions = []
    seen = set()
    for i, line in enumerate(lines):
        m = TOP_KEY_RE.match(line)
        if m and m.group(1) not in seen:
            positions.append((m.group(1), i))
            seen.add(m.group(1))
    return positions


def _half_open_ranges(positions, end):
    """{name: (start, next_start_or_end)} over consecutive (name, start) positions; the one
    fold every locator's ranges come from. (FEAT-70, from _index_top_keys / _index_list_items)"""
    starts = [start for _, start in positions] + [end]
    return {name: (starts[i], starts[i + 1]) for i, (name, _) in enumerate(positions)}


def _index_list_items(lines, key_range):
    """Within key_range=(start,end), find each list item's (start,end) by locating every dash
    line at the SAME indent as the first dash line found. Returns [(start,end), ...] in text
    order; the caller zips this against the already-safe_load-ed list for that key, in the
    order PyYAML preserves for a block sequence."""
    start, end = key_range
    dash_lines = _dash_lines_at_first_indent(lines, start, end)
    starts = dash_lines + [end]
    return [(starts[i], starts[i + 1]) for i in range(len(dash_lines))]


def _dash_lines_at_first_indent(lines, start, end):
    """Indices of every dash line in [start, end) at the indent of the first one. (FEAT-70,
    from _index_list_items)"""
    dash_lines = []
    indent = None
    for i in range(start, end):
        m = DASH_RE.match(lines[i])
        if not m:
            continue
        if indent is None:
            indent = m.group(1)
        if m.group(1) == indent:
            dash_lines.append(i)
    return dash_lines


def _field_lines(indent, key, value):
    """Emit `<indent><key>: <value>` as YAML, quoting ONLY when the value needs it.

    FEAT-41 F-02. `sign-approval` is the one verb that writes a free-form operator string:
    every other verb's value is validated against a closed vocabulary before the lock is taken,
    so it cannot carry syntax. `--by` used to be interpolated raw, and a signer name with a
    colon wrote an unparseable SIGNED plan.yaml and exited 0.

    WHY `safe_dump` AND NOT A QUOTING RULE OF OUR OWN. Three of the six failures are not syntax
    errors and no hand-written escape would have caught them: `#845 owner` is swallowed as a
    comment, a bare `yes` reloads as the boolean True, and an embedded newline can open a
    sibling key. PyYAML already knows the whole set; a local rule would only re-derive part of
    it, and would drift from the parser that actually reads the file back.

    QUOTING ONLY WHEN NEEDED IS PART OF THE CONTRACT, not an aesthetic. This document is signed
    and read by a human, and `approved_by: 'Mike Ruangutai'` on every plan would be a visible
    change to every signature for no benefit. test-plan-merge.py asserts the bare form survives.

    A multi-line emission is indented per line so a continuation cannot escape the mapping.
    """
    dumped = yaml.safe_dump({key: value}, default_flow_style=False,
                            width=10 ** 9, allow_unicode=True)
    return "".join(f"{indent}{line}\n" if line else "\n"
                   for line in dumped.rstrip("\n").split("\n"))


def _before_trailing_comments(lines, floor=0):
    index = len(lines)
    while index > floor and (
        not lines[index - 1].strip() or lines[index - 1].lstrip().startswith("#")
    ):
        index -= 1
    return index


def _item_indent(lines, item_ranges):
    """The leading-space width of a list item's own dash line, or None when there are none."""
    if not item_ranges:
        return None
    start, _end = item_ranges[0]
    line = lines[start]
    return len(line) - len(line.lstrip(" "))


def _reindent(item_lines, delta, iid, key):
    """Shift a whole item uniformly, so a proposal's indentation cannot corrupt the base.

    WHY THIS EXISTS, measured on 2026-08-31: FEAT-41's plan indents `decisions:` items two
    spaces. An operator-approved amendment was proposed as a standalone document with items at
    column 0 — valid YAML on its own, and the shape a human writes by hand. The splice appended
    that text verbatim, so a `- id:` landed at column 0 inside a two-space list, and a signed
    1541-line plan stopped loading. `apply` printed ADDED and exited 0.

    UNIFORM is the whole point: every line of the item moves by the same delta, so relative
    structure — nested mappings, block scalars, the `intent: |` body — is preserved exactly.
    Re-indenting per-line by any cleverer rule would rewrite the very text this tool exists to
    splice byte for byte.

    A dedent that would eat non-whitespace is a REFUSAL, never a silent truncation.
    """
    if delta == 0:
        return list(item_lines)
    out = []
    for line in item_lines:
        if not line.strip():
            out.append(line)
            continue
        if delta > 0:
            out.append(" " * delta + line)
            continue
        room = len(line) - len(line.lstrip(" "))
        if room < -delta:
            raise harness_merge.MergeRefusal(
                5,
                [
                    f"UNPARSEABLE: cannot re-indent id={iid!r} in '{key}' to the base's "
                    f"indentation — a line carries only {room} leading space(s) and the "
                    f"proposal is {-delta} deeper than the base.",
                ],
            )
        out.append(line[-delta:])
    return out


def _item_id(item):
    return item.get("id") if isinstance(item, dict) else None


def _key_head(lines, key_range, item_ranges):
    """The key's own line(s) up to the first item — e.g. the 'tasks:' line itself, plus any
    blank line before the first dash."""
    start, end = key_range
    first_item_start = item_ranges[0][0] if item_ranges else end
    return "".join(lines[start:first_item_start])


def _field_indent(lines, dash_indent):
    """The indent an item's own fields sit at: the first sibling key after the dash line, or
    the dash indent plus two when the item carries nothing beyond its dash line."""
    for line in lines[1:]:
        m = SIBLING_KEY_RE.match(line)
        if m and len(m.group(1)) > len(dash_indent):
            return m.group(1)
    return dash_indent + "  "


def _sub_key_lines(lines, lo, hi):
    """[(key, line index)] for every key line at the first indented key indent in lines[lo:hi],
    plus that indent (or None when there is no indented key)."""
    matches = [(i, SIBLING_KEY_RE.match(lines[i])) for i in range(lo, hi)]
    keyed = [(i, m) for i, m in matches if m and m.group(1)]
    if not keyed:
        return [], None
    indent = keyed[0][1].group(1)
    return [(m.group(2), i) for i, m in keyed if m.group(1) == indent], indent


def _index_sub_keys(lines, lo, hi):
    """[(key, start, end, indent)] for the direct sub-keys of a mapping whose body is
    lines[lo:hi]: every key line at the FIRST indent found, each running to the next."""
    found, indent = _sub_key_lines(lines, lo, hi)
    ends = [start for _key, start in found[1:]] + [hi]
    return [(key, start, end, indent) for (key, start), end in zip(found, ends)]


def _render_items(items, dash_indent):
    dumped = yaml.safe_dump(items, sort_keys=False, allow_unicode=True, width=10 ** 9)
    return [dash_indent + ln if ln.strip() else ln for ln in dumped.splitlines(keepends=True)]


def _approval_span(lines):
    start = next((i for i, line in enumerate(lines)
                  if re.match(r"^approval:\s*$", line)), None)
    if start is None:
        return None, None
    end = next((i for i in range(start + 1, len(lines))
                if lines[i].strip() and not lines[i].startswith((" ", "\t"))), len(lines))
    return start, end


ITEM_ID_RE = re.compile(r"^(\s*)-\s+id:\s*(\S+)\s*$")


SIBLING_KEY_RE = re.compile(r"^(\s*)([A-Za-z_][\w-]*):")


def _item_range(lines, key, iid):
    """(start, end, indent) of the `- id: iid` item under top-level `key`.

    Returns (None, None, ids_present) when absent, so the refusal can name what IS there.
    The id list is SCOPED TO `key` — listing decision ids for a `--key tasks` miss would
    invite a retry that fails for an unrelated reason, the precedent _task_status_line set.
    """
    _l, _order, ranges, _pre = _index_top_keys("".join(lines))
    if key not in ranges:
        return None, None, []
    lo, hi = ranges[key]
    return _item_range_within(lines, lo, hi, iid)


def _item_range_within(lines, lo, hi, iid):
    """`_item_range`'s scan over one key's range [lo, hi): (start, end, indent) of the FIRST
    `- id: iid`, ended by the next item at its indent or shallower, else by `hi`; absent,
    (None, None, ids_present). (FEAT-70, from _item_range)"""
    ids_present, start, indent = [], None, ""
    for i in range(lo, hi):
        m = ITEM_ID_RE.match(lines[i])
        if not m:
            continue
        ids_present.append(m.group(2))
        if start is None:
            if m.group(2) == iid:
                start, indent = i, m.group(1)
        elif len(m.group(1)) <= len(indent):
            return start, i, indent
    return _item_closed_by_range(start, hi, indent, ids_present)


def _item_closed_by_range(start, hi, indent, ids_present):
    """The item found ran to the end of its key's range — or was never found. (FEAT-70, from
    _item_range)"""
    if start is None:
        return None, None, ids_present
    return start, hi, indent


BLOCK_HEAD_RE = re.compile(r"^(\s*)([A-Za-z_][\w-]*):\s*([|>][+-]?\d*)\s*$")


def _block_scalar_end(lines, head, end):
    """First index after the block-scalar body opened at `head`.

    A block scalar's body is every following line indented deeper than its key, plus blank
    lines. NOTHING inside it is YAML: it is opaque text. Skipping it is what stops a prose
    line that happens to read `verify:` from being mistaken for a key (BUG-1128 panel V1).
    """
    key_indent = len(BLOCK_HEAD_RE.match(lines[head]).group(1))
    j = head + 1
    while j < end:
        stripped = lines[j].strip()
        if stripped and (len(lines[j]) - len(lines[j].lstrip())) <= key_indent:
            break
        j += 1
    return j


def _trim_tail(lines, first, last, comments_are_document):
    """Pull `last` back past trailing lines that belong to the DOCUMENT, not the field.

    BUG-1128 panel N1, reproduced independently by all four reviewers. The tail scan stopped
    only at the next item or the next sibling key; a `# NOTE` line and a blank line match
    NEITHER, so both were swept into the replaced range and DELETED by the splice, at exit 0
    under a clean AMENDED receipt.

    `_verify_amend` cannot catch that and never could: the amended field's own value is exactly
    what was asked for. Only the boundary was wrong, and a value check cannot see a boundary.

    `comments_are_document` IS NOT A CONVENIENCE. Inside a `|` body a `#` line is CONTENT — a
    shell or Python comment in a verify script — and trimming it silently truncated the value.
    The first cut of this fix did exactly that, found by loading a block whose last line was a
    comment and comparing against `yaml.safe_load`. So comments are document structure for a
    plain scalar, where a continuation cannot begin with `#`, and content for a block scalar.
    """
    while last - 1 > first:
        stripped = lines[last - 1].strip()
        if stripped == "":
            last -= 1
            continue
        if comments_are_document and stripped.startswith("#"):
            last -= 1
            continue
        break
    return last


def _dedent_value(block, indent, field):
    """The field's VALUE as `--value-file` expects it, derived from raw lines only.

    BUG-1128 panel N3. Two shapes, and the inverse of `_render_field` in both:

    A block scalar's value is its body with the emission indent removed, and it keeps a
    trailing newline because `|` does. A plain scalar's value is what follows `field: `, with
    continuation lines joined at one space, which is how YAML folds them.

    No parsing: `--show` must keep working on a plan whose YAML is broken, since repairing one
    is what the verb is for.
    """
    if not block:
        return ""
    if BLOCK_HEAD_RE.match(block[0]):
        body_indent = len(indent) + 2
        out = [ln[body_indent:] if len(ln) > body_indent else ln.lstrip(" ")
               for ln in block[1:]]
        return "".join(out)
    head = block[0].split(":", 1)[1].strip()
    rest = [ln.strip() for ln in block[1:] if ln.strip()]
    return " ".join([head] + rest) + "\n"


def _find_field_line(lines, start, end, item_indent, field):
    """(index, indent) of the item's own `field:` line, or (None, "").

    BLOCK-SCALAR AWARE (BUG-1128 panel V1, three readers). The first cut matched
    `^\\s*field:` over physical lines, so `--field verify` bound to a prose line inside an
    `intent: |` body and the replace corrupted `intent` while reporting `AMENDED ... verify` at
    exit 0. The compare-and-swap could not help: both hashes are taken over whatever the
    locator returns, so they agree perfectly on the wrong block.
    """
    i = start
    while i < end:
        m = SIBLING_KEY_RE.match(lines[i])
        if _is_own_field(m, field, item_indent):
            return i, m.group(1)
        if _opens_nested_block(lines[i], item_indent):
            i = _block_scalar_end(lines, i, end)   # opaque text, never scanned for keys
            continue
        i += 1
    return None, ""


def _is_own_field(m, field, item_indent):
    """The SIBLING_KEY_RE match is `field:` nested inside the item. (FEAT-70, from
    _find_field_line)"""
    return bool(m) and m.group(2) == field and len(m.group(1)) > len(item_indent)


def _opens_nested_block(line, item_indent):
    """`line` is a block-scalar header nested inside the item. (FEAT-70, from _find_field_line)"""
    head = BLOCK_HEAD_RE.match(line)
    return bool(head) and len(head.group(1)) > len(item_indent)


def _plain_scalar_end(lines, first, end, indent):
    """First index after a plain scalar's continuation lines."""
    for j in range(first + 1, end):
        if ITEM_ID_RE.match(lines[j]):
            return j
        m = SIBLING_KEY_RE.match(lines[j])
        if m and len(m.group(1)) <= len(indent):
            return j
    return end


def _field_block(lines, start, end, item_indent, field):
    """(first, last_exclusive, indent) of `field:` inside one item, or None.

    The block runs from the `field:` line through its continuation lines — a plain multi-line
    scalar or a `|` body is one unit — and stops short of trailing comments and blank lines,
    which belong to the document rather than the field (panel N1).
    """
    first, indent = _find_field_line(lines, start, end, item_indent, field)
    if first is None:
        return None
    is_block = bool(BLOCK_HEAD_RE.match(lines[first]))
    if is_block:
        last = _block_scalar_end(lines, first, end)
    else:
        last = _plain_scalar_end(lines, first, end, indent)
    # Comments are DOCUMENT structure for a plain scalar, whose continuation cannot begin with
    # `#`, and CONTENT for a block scalar, whose body routinely carries shell and Python
    # comments. Trimming them from a block silently truncated the value.
    return first, _trim_tail(lines, first, last, not is_block), indent


def _render_field(indent, field, value_text, original):
    """Emit the replacement, PRESERVING THE ORIGINAL FIELD'S FORM.

    Two lessons, both paid for:

    `_field_lines` is the one renderer for a plain value — a local quoting rule re-derives
    only part of what PyYAML knows, and the first cut's rule would have written `title: yes`
    reloading as boolean True.

    BUT `yaml.safe_dump` NEVER EMITS `|` (BUG-1128 panel V2). Routing a literal block through
    it changes the emitted form and drops the trailing newline a `|` body carries, so an
    IDENTITY replace of a `verify: |` field altered what `safe_load` returned. SPEC.md:1813
    makes that literal form a byte-exact contract. So when the original was a block scalar its
    header is REUSED VERBATIM and the body is emitted as given, which is both form-preserving
    and escape-free.

    THE RETURN IS ONE ELEMENT PER PHYSICAL LINE (FEAT-70 SC-03). It used to be the rendered
    block as a single joined element. Every consumer splices it into a `splitlines` list and
    the next locator re-indexes that list by ranges computed over the re-joined TEXT — so a
    block that grew by more lines than the document's tail put every later index past the end
    of the list: `record-amendments` with a second entry after a longer `|` body died with an
    IndexError, its plan and ledger untouched, and a smaller growth bound the wrong line.
    """
    head = BLOCK_HEAD_RE.match(original[0]) if original else None
    if head:
        body_indent = f"{indent}  "
        body = value_text[:-1] if value_text.endswith("\n") else value_text
        out = [original[0]]
        out += [f"{body_indent}{ln}\n" if ln.strip() else "\n"
                for ln in body.split("\n")]
        return out
    return _field_lines(indent, field, value_text.strip("\n")).splitlines(keepends=True)


def _expected_value(rendered, indent, field):
    """What YAML will load from the lines we are about to splice in.

    ASK YAML, DO NOT REIMPLEMENT IT (panel F1), in this direction too. The previous `want` was
    hand-derived — `value_text` for a block header and `value_text.strip()` otherwise — correct
    for `|` and WRONG for `|-`, `|+` and `>`, which strip, keep and fold respectively.

    THE PROBE KEEPS THE ORIGINAL INDENTATION, and that is the whole subtlety. The first cut
    dedented the rendered field to column zero before parsing, which CHANGES THE ANSWER: a
    quoted multi-line scalar folds its newline to a space at column zero and preserves it at
    indent four. Measured, not reasoned about. So the field is parsed inside a synthetic item
    at exactly the nesting it will occupy.

    It is independent of the splice on purpose. Deriving `want` from the spliced document would
    make `_verify_amend` compare that document against itself and pass unconditionally.
    """
    item_indent = indent[:-2] if len(indent) >= 2 else ""
    probe = f"_p:\n{item_indent}- id: _x\n" + "".join(rendered)
    try:
        doc = harness_yaml.load_str(probe, "<rendered field probe>")
    except harness_yaml.YamlParseError:
        return None
    items = (doc or {}).get("_p")
    if not isinstance(items, list) or not items or not isinstance(items[0], dict):
        return None
    return items[0].get(field)


# `None` cannot mean both "the document will not parse" and "the field is null" — conflating
# them made a null field fall through to the line-based reader and print as an empty string
# (panel F1, code-reviewer). A sentinel keeps the two answers separable.
_UNPARSEABLE = object()


def _parsed_value(raw, key, iid, field):
    """The field's value as YAML loads it, or None when the document will not parse.

    ASK YAML, DO NOT REIMPLEMENT IT (panel F1). The line-based reader diverged from the parser
    on four legal shapes at once: `|` clips to one trailing newline, `|-` strips it, `|+` keeps
    every one, and `>` FOLDS newlines into spaces. All four produced the same `--show` output
    and four different real values, so feeding that output back through the tool's own
    documented workflow silently rewrote the field.

    This is the third time in this feature that hand-rolling what PyYAML already knows was the
    defect: first a quoting rule, then form preservation, now value extraction.
    """
    try:
        doc = harness_yaml.load_str(raw, "<base plan>")
    except harness_yaml.YamlParseError:
        return _UNPARSEABLE
    item = _item_by_id((doc or {}).get(key) or [], iid)
    return _UNPARSEABLE if item is None else item.get(field)


def _item_by_id(items, iid):
    """The first mapping in `items` whose `id` is `iid`, else None. (FEAT-70, from
    _parsed_value)"""
    for item in items:
        if isinstance(item, dict) and item.get("id") == iid:
            return item
    return None


def _structured_field_lines(indent, field, value):
    dumped = yaml.safe_dump({field: value}, sort_keys=False).splitlines(keepends=True)
    return [indent + line if line.strip() else line for line in dumped]


def _last_nonblank(lines, lo, hi):
    """1 + the index of the last non-blank line in [lo, hi), or `lo` when they are all blank."""
    for index in range(hi - 1, lo - 1, -1):
        if lines[index].strip():
            return index + 1
    return lo


def _item_delete_end(lines, start, end, indent):
    """Where an item's OWN bytes stop, inside the dash-to-dash range `_index_list_items` gives.

    THE RANGE `_index_list_items` RETURNS IS TOO WIDE TO DELETE. It runs each item to the NEXT
    dash line, and the last item to the end of the key's block, so whatever whitespace and
    comments sit between two items land inside the earlier one. Two different answers are owed,
    and both were measured on FEAT-57's own plan.yaml rather than reasoned about:

    AN ITEM OWNS THE BLANK LINES THAT FOLLOW IT. Deleting five consecutive blank-separated
    tasks while calling those blanks "the document's" left FIVE blank lines behind, four of
    them stranded at end of file, and turned a deletions-only diff into one carrying
    insertions. Whitespace after an item is its separator; a human deleting the item in an
    editor takes it, and taking it is what makes N deletions leave N-1 separators rather than
    N-1 empty lines.

    AN ITEM DOES NOT OWN A TRAILING COMMENT. A `#` line between two items is a note somebody
    wrote about the list, and BUG-1128 panel N1 is this same defect one level down: a `# NOTE`
    matched neither the next item nor the next sibling key, was swept into a replaced range,
    and was deleted at exit 0 under a clean receipt. So the delete stops at the FIRST trailing
    comment line, which keeps that comment and everything after it — including any blank lines
    the comment itself is separated by.

    INSIDE A `|` BODY A `#` LINE IS CONTENT — a shell or Python comment in a verify script —
    and must go WITH the item, or a fragment of the deleted task's own script is orphaned
    inside `tasks:`. So the scan walks block scalars with `_block_scalar_end` and floors the
    trailing-run search past their last non-blank line, which is the split `_trim_tail`'s
    `comments_are_document` argument makes, reused rather than re-derived.
    """
    floor, index = start + 1, start
    while index < end:
        head = BLOCK_HEAD_RE.match(lines[index])
        if head and len(head.group(1)) > len(indent):
            body_end = _block_scalar_end(lines, index, end)
            floor = max(floor, _last_nonblank(lines, index, body_end))
            index = body_end
            continue
        index += 1
    trailing = _before_trailing_comments(lines[:end], floor)
    comment = next((i for i in range(trailing, end)
                    if lines[i].lstrip().startswith("#")), None)
    return end if comment is None else comment


def _splice_out(lines, ranges):
    """`lines` with every range removed, as bytes.

    IT FILTERS LINES AND RENDERS NONE, which is what makes every survivor byte-identical: a
    round trip through a YAML dumper would reformat the whole plan and destroy the review diff
    this tool exists to keep readable (D-03). Overlapping ranges cannot arise from distinct
    items, and a set makes one harmless rather than a double-deletion if one ever did.
    """
    dropped = set()
    for start, end in ranges:
        dropped.update(range(start, end))
    return "".join(line for index, line in enumerate(lines)
                   if index not in dropped).encode("utf-8")
