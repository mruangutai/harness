#!/usr/bin/env python3
"""plan-merge.py — the second plan writer that adds tasks and never deletes them
(FEAT-32 T-03, D-01..D-04, DEC-182, DEC-120).

Reproduces and fixes #628: two whole-file writes to the same plan.yaml, one after another,
silently lose whatever the first one added. This CLI never does a whole-file rewrite of an
existing plan.yaml. It SPLICES TEXT — never re-renders through a YAML dumper (D-03) — keyed on
each task/decision's `id`, under harness_merge.locked_update so the replace stays atomic and the
lock stays the one shared with every other write route in this feature.

    plan-merge.py apply             --file <plan.yaml> --proposal <path or - for stdin>
    plan-merge.py add-tasks         --file <plan.yaml> --proposal <path or - for stdin>
    plan-merge.py set-task-station  --file <plan.yaml> --task T-NN --station <name>
    plan-merge.py set-feature-station --file <plan.yaml> --station <name>
    plan-merge.py sign-approval     --file <plan.yaml> --by <name> --date <YYYY-MM-DD>

FIVE VERBS, ONE WRITE ROUTE (FEAT-41 T-03). Every verb goes through
harness_merge.locked_update and the text splice, and require_destination (exit 9) guards every
path. ADD-ONLY IS A PROPERTY OF `apply` AND ITS ALIAS, NOT OF THE TOOL: the lock and the splice
are what fix #628 and they hold for all five, while never deleting a task is a promise those two
verbs alone make.

`set-task-station` and `set-feature-station` validate the station against the vocabulary
factory_config declares — MANDATED_STATIONS plus TERMINAL_MARKER, imported, never respelled —
resolved through the harness.json of the checkout the target plan.yaml belongs to. The check runs
BEFORE the lock is taken, so a refused value never opens the file.

`approval:` is written by EXACTLY ONE VERB, `sign-approval` (D-04, amended by FEAT-41 T-03).
Every other verb leaves the base file's approval bytes byte for byte. The main session — nobody
else — signs approval, and now does so through this tool rather than by hand. A proposal
that carries an approval mapping which PARSES differently from the base's is a REFUSAL (exit 8),
not a silent drop: `apply` must be INCAPABLE of writing a signature (step 7) and must also NOTICE
a caller that tried to sneak one past it (step 7b) — two different jobs, so two different guards.

THAT PROHIBITION IS UNCHANGED IN FORCE AND NARROWER IN SCOPE. Before FEAT-41 T-03 the tool had
one verb, so "apply cannot sign" and "this tool cannot sign" were the same sentence; they are not
any more. Signing moved from a hand edit into `sign-approval` so that it happens under the same
lock as every other plan write — a signature spliced by hand while another writer held the file
was the remaining unguarded route into plan.yaml. `apply` still cannot sign, and still refuses a
proposal that tries.

Exit codes are the interface:
    0  applied — stdout lists ADDED/PRESERVED ids, an IGNORED-APPROVAL line if the proposal
       carried an approval block, and a final APPLIED line
    3  the task id named by --task is absent from the plan (the message names the ids present)
    4  the value given to --station is not a legal station (the message lists the legal ones)
    5  a side (base or proposal) failed to parse as YAML
    6  the lock could not be acquired within the retry budget (harness_merge)
    7  the same id, or the same top-level key, carries two different loaded values
    8  the proposal's approval mapping parses differently from the base's
    9  --file does not resolve to a plan.yaml this tool owns

python3 stdlib plus PyYAML (DEC-171 requires it here; imported plainly, never through
harness_yaml.py — that divergence is raised upward as a decision question, not resolved here).
"""
import argparse
import os
import re
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import factory_config  # noqa: E402  (local import, after sys.path fix-up)
import gh_board  # noqa: E402
import harness_boundary  # noqa: E402
import harness_merge  # noqa: E402

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

# A features directory either directly under a .harness segment or nested one segment deeper
# (repo-tier), a FEAT- or BUG- prefixed directory, and the literal filename plan.yaml. Matched
# on the RESOLVED path only (harness_merge.require_destination), never the literal argument.
PLAN_TAIL = re.compile(
    r"(?:^|/)\.harness/(?:[^/]+/)?features/(?:FEAT|BUG)-[^/]+/plan\.yaml$"
)

TOP_KEY_RE = re.compile(r"^([A-Za-z_][\w-]*):")
DASH_RE = re.compile(r"^(\s*)-\s")

UNION_KEYS = ("tasks", "decisions")


def _resolve_plan(file_path):
    """require_destination on the RESOLVED path, or print the refusal and exit its code.

    Extracted so all five verbs share ONE destination guard. A second copy would be a second
    place for exit 9 to stop being true."""
    try:
        return harness_merge.require_destination(
            file_path,
            PLAN_TAIL,
            "a plan.yaml under a features directory",
            [
                "  a legal path looks like .harness/features/FEAT-NN-slug/plan.yaml or",
                "  .harness/<repo>/features/FEAT-NN-slug/plan.yaml.",
                "  This tool merges plan.yaml only.",
            ],
        )
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)


def _legal_stations(resolved):
    """The station vocabulary the target plan.yaml's own checkout declares, plus the terminal
    marker, as an ordered tuple.

    IMPORTED, NEVER RESPELLED (FEAT-41 T-03). factory_config owns MANDATED_STATIONS and
    TERMINAL_MARKER; declaring either here would be a second vocabulary, and since this module
    is imported by nothing, check-plan-routes.py and check-domain.sh would each respell it as a
    bare literal and D-05's claim that the marker is declared once in code would be false the
    day it landed.

    The board is read from the harness.json of the checkout the plan belongs to. A checkout with
    no board declared — every test fixture, and any project that has not onboarded a board — is
    NOT a licence to accept anything: the mandate still applies, because MANDATED_STATIONS is
    what a declaration is checked against in the first place.

    THE ROOT PROBE NAMES THE MANIFEST, NEVER THE `.harness` DIRECTORY. A probe for the directory
    resolves $HOME as a root in the global install — B-7 verbatim — and
    test-check-plan-routes.py's case_20 asserts that no copy of this idiom regresses. The walk
    starts from the plan.yaml's own directory rather than from this script's location, because
    the vocabulary that governs a write belongs to the checkout being written to, not to
    whichever checkout happens to be running the tool.
    """
    root = os.path.dirname(os.path.abspath(resolved))
    while True:
        if os.path.isfile(os.path.join(root, harness_boundary.MARKER)):
            break
        parent = os.path.dirname(root)
        if parent == root:
            root = None
            break
        root = parent
    stations = None
    if root is not None:
        try:
            board = gh_board.load_board(root)
            if board is not None:
                stations = factory_config.station_names(board)
        except factory_config.FleetError:
            # An unusable board declaration is not this tool's error to report — the state gate
            # and every board writer already name it loudly. Fall back to the mandate so a
            # station write is still validated rather than waved through.
            stations = None
    if stations is None:
        stations = factory_config.MANDATED_STATIONS
    return tuple(stations) + (factory_config.TERMINAL_MARKER,)


def _refuse_illegal_station(station, legal):
    """Exit 4, naming the offending value and every legal one.

    CALLED BEFORE THE LOCK IS TAKEN, deliberately: a refused value must never open the file, so
    a typo cannot contend for the lock or leave a partial write behind."""
    print(
        f"plan-merge: {station!r} is not a legal station — expected one of: "
        + ", ".join(legal),
        file=sys.stderr,
    )
    sys.exit(4)



def _index_top_keys(text):
    """Return (lines, order, ranges, preamble_lines).

    lines:     text.splitlines(keepends=True)
    order:     top-level key names in file order (first occurrence only)
    ranges:    {key: (start_line, end_line)} half-open, end exclusive
    preamble:  every line before the first top-level key (comments, blank lines) — always
               carried from the BASE side untouched; a proposal's preamble is never consulted.
    """
    lines = text.splitlines(keepends=True)
    positions = []
    seen = set()
    for i, line in enumerate(lines):
        m = TOP_KEY_RE.match(line)
        if m and m.group(1) not in seen:
            positions.append((m.group(1), i))
            seen.add(m.group(1))
    order = [name for name, _ in positions]
    ranges = {}
    for idx, (name, start) in enumerate(positions):
        end = positions[idx + 1][1] if idx + 1 < len(positions) else len(lines)
        ranges[name] = (start, end)
    preamble_end = positions[0][1] if positions else len(lines)
    return lines, order, ranges, lines[:preamble_end]


def _index_list_items(lines, key_range):
    """Within key_range=(start,end), find each list item's (start,end) by locating every dash
    line at the SAME indent as the first dash line found. Returns [(start,end), ...] in text
    order; the caller zips this against the already-safe_load-ed list for that key, in the
    order PyYAML preserves for a block sequence."""
    start, end = key_range
    dash_lines = []
    indent = None
    for i in range(start, end):
        m = DASH_RE.match(lines[i])
        if m:
            cur = m.group(1)
            if indent is None:
                indent = cur
            if cur == indent:
                dash_lines.append(i)
    ranges = []
    for idx, s in enumerate(dash_lines):
        e = dash_lines[idx + 1] if idx + 1 < len(dash_lines) else end
        ranges.append((s, e))
    return ranges


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
        reloaded = yaml.safe_load(spliced_bytes.decode("utf-8"))
    except yaml.YAMLError as exc:
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


def _verify_spliced(spliced_bytes, base_doc, prop_doc, out_order, added_ids):
    """Refuse rather than return a splice that does not reload as the merge it reported."""
    try:
        reloaded = yaml.safe_load(spliced_bytes.decode("utf-8"))
    except yaml.YAMLError as exc:
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
    for key in UNION_KEYS:
        if key not in out_order:
            continue
        want = [_item_id(i) for i in (base_doc.get(key) or [])]
        for item in prop_doc.get(key) or []:
            iid = _item_id(item)
            if iid not in want:
                want.append(iid)
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


def apply_merge(base_bytes, proposal_text):
    """The whole algorithm. Returns (output_bytes, added_ids, preserved_ids, ignored_approval).
    Raises harness_merge.MergeRefusal(5|7|8) with nothing to write, per plan-merge.py's contract
    with harness_merge.locked_update: a raised MergeRefusal leaves the file untouched."""
    if base_bytes is None:
        # Step 3: a base that does not exist is an empty mapping; the proposal is written whole
        # UNLESS it carries an approval key. Read together with step 7b (D-04): the empty
        # mapping has no approval key at all, so a proposal's approval value always "differs"
        # from the base's absent one — the same structural refusal step 7b applies elsewhere,
        # here on the create path, so the tool never becomes capable of writing a signature to
        # a brand-new file.
        try:
            prop_doc = yaml.safe_load(proposal_text)
        except yaml.YAMLError as exc:
            raise harness_merge.MergeRefusal(
                5, [f"UNPARSEABLE: proposal failed to parse: {exc}"]
            )
        prop_doc = prop_doc if isinstance(prop_doc, dict) else {}
        if APPROVAL_REFUSAL and "approval" in prop_doc:
            raise harness_merge.MergeRefusal(
                8,
                [
                    "REFUSED: proposal carries an approval mapping and the base does not exist "
                    "(treated as an empty mapping with no approval key).",
                    "  base approval: <absent>",
                    f"  proposal approval: {prop_doc.get('approval')!r}",
                    "  the signer is the main session; plan-merge.py never writes approval.",
                ],
            )
        return proposal_text.encode("utf-8"), [], [], False

    base_text = base_bytes.decode("utf-8")
    try:
        base_doc = yaml.safe_load(base_text)
    except yaml.YAMLError as exc:
        raise harness_merge.MergeRefusal(5, [f"UNPARSEABLE: base failed to parse: {exc}"])
    try:
        prop_doc = yaml.safe_load(proposal_text)
    except yaml.YAMLError as exc:
        raise harness_merge.MergeRefusal(5, [f"UNPARSEABLE: proposal failed to parse: {exc}"])
    base_doc = base_doc if isinstance(base_doc, dict) else {}
    prop_doc = prop_doc if isinstance(prop_doc, dict) else {}

    if not UNION_MERGE:
        # Step 5, off: today's last-writer-wins, verbatim.
        return proposal_text.encode("utf-8"), [], [], False

    base_lines, base_order, base_ranges, base_preamble = _index_top_keys(base_text)
    prop_lines, prop_order, prop_ranges, _prop_preamble = _index_top_keys(proposal_text)

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

    out_order = list(base_order)
    for key in prop_order:
        if key not in out_order:
            out_order.append(key)

    out_chunks = ["".join(base_preamble)]
    added_ids, preserved_ids = [], []

    for key in out_order:
        if key == "approval":
            # Step 7: the base's line range, byte for byte, always. If the base has no
            # approval block at all, this tool still never writes one — there is nothing to
            # carry forward, and the proposal's is ignored the same as everywhere else.
            if base_has_approval:
                s, e = base_ranges["approval"]
                out_chunks.append("".join(base_lines[s:e]))
            continue

        if key in UNION_KEYS:
            base_list = base_doc.get(key) or []
            prop_list = prop_doc.get(key) or []
            base_item_ranges = (
                _index_list_items(base_lines, base_ranges[key]) if key in base_ranges else []
            )
            prop_item_ranges = (
                _index_list_items(prop_lines, prop_ranges[key]) if key in prop_ranges else []
            )
            if len(base_item_ranges) != len(base_list) or len(prop_item_ranges) != len(
                prop_list
            ):
                raise harness_merge.MergeRefusal(
                    5,
                    [
                        f"UNPARSEABLE: could not align text ranges with parsed items for "
                        f"'{key}' — the block's formatting is not one dash per item."
                    ],
                )

            if key in base_ranges:
                out_chunks.append(_key_head(base_lines, base_ranges[key], base_item_ranges))
            elif key in prop_ranges:
                out_chunks.append(_key_head(prop_lines, prop_ranges[key], prop_item_ranges))
            else:
                continue

            base_by_id = {}
            for (s, e), item in zip(base_item_ranges, base_list):
                base_by_id[_item_id(item)] = (s, e, item)
            prop_by_id = {}
            prop_id_order = []
            for (s, e), item in zip(prop_item_ranges, prop_list):
                iid = _item_id(item)
                prop_by_id[iid] = (s, e, item)
                prop_id_order.append(iid)

            for iid, (s, e, item) in base_by_id.items():
                out_chunks.append("".join(base_lines[s:e]))
                if iid in prop_by_id:
                    _, _, pitem = prop_by_id[iid]
                    if pitem == item:
                        preserved_ids.append(iid)
                    else:
                        raise harness_merge.MergeRefusal(
                            7,
                            [
                                f"CONFLICT: id={iid!r} in '{key}' carries two different values.",
                                f"  base: {item!r}",
                                f"  proposal: {pitem!r}",
                            ],
                        )
            # THE ADDITION IS RE-INDENTED TO THE BASE'S LIST, never appended verbatim. When
            # the base has no items of its own there is nothing to match, and the key head came
            # from the proposal too, so its own indentation is already consistent.
            base_indent = _item_indent(base_lines, base_item_ranges)
            prop_indent = _item_indent(prop_lines, prop_item_ranges)
            for iid in prop_id_order:
                if iid not in base_by_id:
                    s, e, _item = prop_by_id[iid]
                    item_lines = prop_lines[s:e]
                    if base_indent is not None and prop_indent is not None:
                        item_lines = _reindent(
                            item_lines, base_indent - prop_indent, iid, key
                        )
                    out_chunks.append("".join(item_lines))
                    added_ids.append(iid)
            continue

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
            s, e = base_ranges[key]
            out_chunks.append("".join(base_lines[s:e]))
        elif in_base:
            s, e = base_ranges[key]
            out_chunks.append("".join(base_lines[s:e]))
        elif in_prop:
            s, e = prop_ranges[key]
            out_chunks.append("".join(prop_lines[s:e]))

    spliced_bytes = "".join(out_chunks).encode("utf-8")

    if PRESERVE_BASE_BYTES:
        # STEP 9: THE RESULT IS PARSED BEFORE IT IS WRITTEN, and this guard is general.
        # Steps 5-8 parse the BASE and the PROPOSAL; nothing parsed the OUTPUT, so a splice
        # defect could — and on 2026-08-31 did — write a signed plan that PyYAML cannot load
        # while printing ADDED and exiting 0. A tool whose whole promise is "the base's bytes
        # survive" must not be able to hand back bytes that are not a plan.
        #
        # It also checks the MERGE, not merely the syntax: every id the caller is about to be
        # told was added or preserved must actually be present in the reloaded document. A
        # splice that lands text in the wrong block can still parse.
        _verify_spliced(spliced_bytes, base_doc, prop_doc, out_order, added_ids)
        return spliced_bytes, added_ids, preserved_ids, ignored_approval

    # PRESERVE_BASE_BYTES off: what a naive implementation does — render the whole merged
    # document through yaml.safe_dump instead of splicing. Comments and quoting do not survive
    # this path; that is exactly the property the red proof grades.
    merged_doc = dict(base_doc)
    for key in UNION_KEYS:
        if key not in out_order:
            continue
        base_list = base_doc.get(key) or []
        merged_list = list(base_list)
        seen = {_item_id(i) for i in base_list}
        for item in prop_doc.get(key) or []:
            iid = _item_id(item)
            if iid not in seen:
                merged_list.append(item)
                seen.add(iid)
        if merged_list:
            merged_doc[key] = merged_list
    for key in prop_doc:
        if key in UNION_KEYS or key == "approval":
            continue
        if key not in merged_doc:
            merged_doc[key] = prop_doc[key]
    if base_has_approval:
        merged_doc["approval"] = base_approval
    dumped = yaml.safe_dump(merged_doc, sort_keys=False, allow_unicode=True).encode("utf-8")
    return dumped, added_ids, preserved_ids, ignored_approval


def cmd_apply(args):
    resolved = _resolve_plan(args.file)

    if args.proposal == "-":
        proposal_text = sys.stdin.read()
    else:
        with open(args.proposal, encoding="utf-8") as f:
            proposal_text = f.read()

    result = {}

    def transform(base_bytes):
        out_bytes, added, preserved, ignored_approval = apply_merge(base_bytes, proposal_text)
        result["added"] = added
        result["preserved"] = preserved
        result["ignored_approval"] = ignored_approval
        return out_bytes

    try:
        harness_merge.locked_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)

    for eid in result.get("added", []):
        print(f"ADDED {eid}")
    for eid in result.get("preserved", []):
        print(f"PRESERVED {eid}")
    if result.get("ignored_approval"):
        print("IGNORED-APPROVAL: proposal's approval block was not written; base's kept")
    print(f"APPLIED {resolved}")
    sys.exit(0)


TASK_ID_RE = re.compile(r"^(\s*)-\s+id:\s*(\S+)\s*$")
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
    ids_present = []
    start = None
    indent = ""
    for i in range(lo, hi):
        line = lines[i]
        m = TASK_ID_RE.match(line)
        if m:
            ids_present.append(m.group(2))
            if m.group(2) == task_id and start is None:
                start, indent = i, m.group(1)
            elif start is not None and m.group(1) == indent:
                break
    if start is None:
        return None, ids_present
    for j in range(start, len(lines)):
        m2 = TASK_ID_RE.match(lines[j])
        if m2 and j != start and m2.group(1) == indent:
            break
        ms = STATUS_LINE_RE.match(lines[j])
        if ms and len(ms.group(1)) > len(indent):
            return j, ms.group(1)
    return None, ids_present


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
        harness_merge.locked_update(resolved, transform)
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


def cmd_set_feature_station(args):
    resolved = _resolve_plan(args.file)
    legal = _legal_stations(resolved)
    if args.station not in legal:
        _refuse_illegal_station(args.station, legal)

    def transform(base_bytes):
        text = base_bytes.decode("utf-8")
        lines = text.splitlines(keepends=True)
        # REPLACE the existing top-level status, or INSERT immediately after `feature:` so the
        # file keeps a stable key order. Appending at the end would work and would also make
        # every plan.yaml's key order depend on the order the verbs happened to run in.
        for i, line in enumerate(lines):
            m = STATUS_LINE_RE.match(line)
            if m and m.group(1) == "":
                newline = "\n" if line.endswith("\n") else ""
                lines[i] = f"status: {args.station}{newline}"
                return "".join(lines).encode("utf-8")
        for i, line in enumerate(lines):
            if FEATURE_LINE_RE.match(line):
                lines.insert(i + 1, f"status: {args.station}\n")
                return "".join(lines).encode("utf-8")
        raise harness_merge.MergeRefusal(
            5, [f"plan-merge: {resolved} carries no top-level feature: key to anchor status to"]
        )

    try:
        harness_merge.locked_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)
    print(f"STATION {resolved} -> {args.station}")
    print(f"APPLIED {resolved}")
    sys.exit(0)


def cmd_sign_approval(args):
    """THE ONLY WAY THE APPROVAL MAPPING IS EVER WRITTEN (D-04, FEAT-41 T-03).

    Every other verb leaves the base's approval bytes byte-identical and `apply` still exits 8
    on a proposal carrying a different one. That prohibition and this verb are the same rule seen
    from two sides: approval is written HERE, deliberately, by the main session, and nowhere
    else by accident."""
    resolved = _resolve_plan(args.file)

    def transform(base_bytes):
        text = base_bytes.decode("utf-8")
        lines = text.splitlines(keepends=True)
        start = None
        for i, line in enumerate(lines):
            if re.match(r"^approval:\s*$", line):
                start = i
                break
        if start is None:
            raise harness_merge.MergeRefusal(
                5, [f"plan-merge: {resolved} carries no approval: mapping to sign"]
            )
        end = len(lines)
        for j in range(start + 1, len(lines)):
            if lines[j].strip() and not lines[j].startswith((" ", "\t")):
                end = j
                break
        fields = {"status": "approved", "approved_by": args.by, "date": args.date}
        written = set()
        out = []
        for line in lines[start + 1:end]:
            m = re.match(r"^(\s+)(status|approved_by|date):\s*(.*)$", line)
            if m and m.group(2) not in written:
                out.append(_field_lines(m.group(1), m.group(2), fields[m.group(2)]))
                written.add(m.group(2))
            else:
                out.append(line)
        for key in ("status", "approved_by", "date"):
            if key not in written:
                out.insert(0, _field_lines("  ", key, fields[key]))
        spliced = "".join(lines[:start + 1] + out + lines[end:]).encode("utf-8")
        _verify_signature(spliced, resolved, fields)
        return spliced

    try:
        harness_merge.locked_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)
    print(f"SIGNED {resolved} by {args.by} on {args.date}")
    print(f"APPLIED {resolved}")
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(prog="plan-merge.py")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # ADD-ONLY IS A PROPERTY OF THESE TWO VERBS, NOT OF THE TOOL (FEAT-41 T-03). The lock and
    # the splice are what fix #628 and they apply to every verb; never deleting a task is a
    # separate promise that `apply` and its alias alone make.
    for name, helptext in (
        ("apply", "merge a proposal into a plan.yaml — adds, never deletes"),
        ("add-tasks", "alias of apply, for callers that only add tasks — identical code path"),
    ):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--file", required=True, help="path to the plan.yaml")
        p.add_argument(
            "--proposal", required=True, help="path to the proposed plan.yaml, or - for stdin"
        )
        p.set_defaults(func=cmd_apply)

    p_task = sub.add_parser(
        "set-task-station", help="set ONE task's status, by splicing its one line"
    )
    p_task.add_argument("--file", required=True, help="path to the plan.yaml")
    p_task.add_argument("--task", required=True, help="the task id, T-NN")
    p_task.add_argument("--station", required=True, help="one of the six stations, or abandoned")
    p_task.set_defaults(func=cmd_set_task_station)

    p_feat = sub.add_parser(
        "set-feature-station", help="set or insert the top-level status key"
    )
    p_feat.add_argument("--file", required=True, help="path to the plan.yaml")
    p_feat.add_argument("--station", required=True, help="one of the six stations, or abandoned")
    p_feat.set_defaults(func=cmd_set_feature_station)

    p_sign = sub.add_parser(
        "sign-approval", help="the ONLY route that writes the approval mapping"
    )
    p_sign.add_argument("--file", required=True, help="path to the plan.yaml")
    p_sign.add_argument("--by", required=True, help="the signer's name")
    p_sign.add_argument("--date", required=True, help="YYYY-MM-DD")
    p_sign.set_defaults(func=cmd_sign_approval)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
