#!/usr/bin/env python3
"""plan-merge.py — the second plan writer that adds tasks and never deletes them
(FEAT-32 T-03, D-01..D-04, DEC-182, DEC-120).

Reproduces and fixes #628: two whole-file writes to the same plan.yaml, one after another,
silently lose whatever the first one added. This CLI never does a whole-file rewrite of an
existing plan.yaml. It SPLICES TEXT — never re-renders through a YAML dumper (D-03) — keyed on
each task/decision's `id`, under harness_merge.locked_update so the replace stays atomic and the
lock stays the one shared with every other write route in this feature.

    plan-merge.py apply --file <path to a plan.yaml> --proposal <path or - for stdin>

`approval:` is never written by this tool (D-04): it is always the BASE file's bytes, byte for
byte. The main session — nobody else — signs approval, with the Edit tool, directly. A proposal
that carries an approval mapping which PARSES differently from the base's is a REFUSAL (exit 8),
not a silent drop: this tool must be INCAPABLE of writing a signature (step 7) and must also
NOTICE a caller that tried to sneak one past it (step 7b) — two different jobs, so two different
guards.

Exit codes are the interface:
    0  applied — stdout lists ADDED/PRESERVED ids, an IGNORED-APPROVAL line if the proposal
       carried an approval block, and a final APPLIED line
    5  a side (base or proposal) failed to parse as YAML
    6  the lock could not be acquired within the retry budget (harness_merge)
    7  the same id, or the same top-level key, carries two different loaded values
    8  the proposal's approval mapping parses differently from the base's
    9  --file does not resolve to a plan.yaml this tool owns

python3 stdlib plus PyYAML (DEC-171 am.1 requires it here; imported plainly, never through
harness_yaml.py — that divergence is raised upward as a decision question, not resolved here).
"""
import argparse
import os
import re
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness_merge  # noqa: E402  (local import, after sys.path fix-up)

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
            for iid in prop_id_order:
                if iid not in base_by_id:
                    s, e, _item = prop_by_id[iid]
                    out_chunks.append("".join(prop_lines[s:e]))
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
    file_path = args.file
    try:
        resolved = harness_merge.require_destination(
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


def main():
    parser = argparse.ArgumentParser(prog="plan-merge.py")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_apply = sub.add_parser("apply", help="merge a proposal into a plan.yaml")
    p_apply.add_argument("--file", required=True, help="path to the plan.yaml")
    p_apply.add_argument(
        "--proposal", required=True, help="path to the proposed plan.yaml, or - for stdin"
    )
    p_apply.set_defaults(func=cmd_apply)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
