#!/usr/bin/env python3
"""expertise-merge.py — union-merge apply for Expertise files (FEAT-30 T-06, D-05, DEC-95).

DEC-95 recorded the residue: two concurrent close-outs each doing a whole-file write to the
same `.harness/expertise/<agent>.md` lose whatever the other one added — plain last-writer-wins.
This CLI is the fix: it never overwrites blindly. It reads the file under an exclusive lock,
computes the UNION of what is already there and what is being proposed, and writes that union
back atomically. Anything the union cannot represent safely — the same entry id carrying two
different texts, or a section that would exceed its DEC-145 cap — is reported and applied
nothing, on the theory that a loud refusal beats a second silent loss.

    expertise-merge.py apply --file <path to an Expertise markdown file> --entries <path or ->

Exit codes are part of the interface (T-07 routes an agent's behaviour on them):
    0  applied — stdout lists every id ADDED, every id PRESERVED, then a final APPLIED line
    6  could not acquire the lock within the retry budget
    7  the same section+id exists on both sides with different text — nothing applied
    8  the union would exceed a DEC-145 section cap — nothing applied

python3 stdlib only, no third-party imports, so this runs on any machine that runs the harness.

Locking and the atomic replace are FEAT-32 T-05's rewire onto harness_merge (D-02): this file no
longer carries its own lock or replace primitive — see harness_merge.py's module docstring for
the lock dialect this tool now shares with plan-merge.py and observations-merge.py.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness_merge  # noqa: E402  (local import, after sys.path fix-up)

# DEC-145's four canonical sections and their entry caps, verbatim. This is the one place this
# tool spells them; test-expertise-merge.py's case 8 reads check-expertise.sh's own CAPS mapping
# as TEXT and asserts the two agree, rather than adding a third copy of these numbers anywhere.
CAPS = {"Patterns": 15, "Gotchas": 15, "Outcomes": 10, "Open": 5}

# The same two patterns check-expertise.sh parses an Expertise file with, so a file this tool
# writes is read back identically by the checker that governs the format.
SECTION_RE = re.compile(r"^## (\w+)(?: \(max (\d+)\))?\s*$")
ENTRY_RE = re.compile(r"^- ([A-Za-z]{1,3}-\d+): (.*)$")

# Guards step 3, the union computation, and nothing else. False reproduces today's naive
# behaviour exactly: the proposal replaces the file, whole, with no comparison against what was
# already there — no divergence check, no cap check, because neither question is being asked
# about a union that was never computed. Nothing outside this file's source text ever changes
# this: no environment variable, no flag. That is deliberate — a test proves its own assertions
# are load-bearing by mutating this literal, by name, in a COPY of this file.
UNION_APPLY = True


def parse_expertise(text):
    """Parse Expertise markdown into (title_line_or_None, sections, order, headers).

    sections: {section_name: [[id, text], ...]} in file order.
    order:    section names in the order first encountered.
    headers:  {section_name: the exact heading line encountered}, so a re-render can keep an
              existing "(max N)" annotation rather than silently dropping it.
    """
    lines = text.splitlines()
    title = None
    start = 0
    if lines and lines[0].startswith("# "):
        title = lines[0]
        start = 1

    sections = {}
    order = []
    headers = {}
    current = None
    for line in lines[start:]:
        m = SECTION_RE.match(line)
        if m:
            current = m.group(1)
            if current not in sections:
                sections[current] = []
                order.append(current)
                headers[current] = line
            continue
        em = ENTRY_RE.match(line)
        if em and current is not None:
            sections[current].append([em.group(1), em.group(2)])
            continue
        # A continuation line — check-expertise.sh treats any indented, non-empty line right
        # after an entry as wrapped text of that entry, so this parser must reconstruct the
        # same logical text or two files holding the "same" entry could compare unequal.
        if (
            line.startswith("  ")
            and line.strip()
            and current is not None
            and sections.get(current)
        ):
            sections[current][-1][1] += " " + line.strip()

    # Freeze to tuples: nothing downstream mutates an entry's text in place again.
    for name in sections:
        sections[name] = [(eid, text) for eid, text in sections[name]]
    return title, sections, order, headers


def render(title, sections, order, headers):
    out = []
    if title:
        out.append(title)
    for name in order:
        out.append(headers.get(name, f"## {name}"))
        for eid, text in sections.get(name, []):
            out.append(f"- {eid}: {text}")
    return "\n".join(out) + "\n"


def compute_union(base_sections, base_order, prop_sections, prop_order):
    """The UNION, keyed by section and id, preserving existing order and appending new ids in
    the order the proposal gives them. Returns (merged, order, conflicts). A conflict is
    (section, id, base_text, proposed_text) for the same id carrying different text — nothing
    is dropped to produce this return; the caller decides whether it is safe to write."""
    order = list(base_order)
    for name in prop_order:
        if name not in order:
            order.append(name)

    merged = {}
    conflicts = []
    for name in order:
        base_entries = base_sections.get(name, [])
        base_by_id = dict(base_entries)
        merged_list = list(base_entries)
        seen = set(base_by_id)
        for eid, text in prop_sections.get(name, []):
            if eid in base_by_id:
                if base_by_id[eid] != text:
                    conflicts.append((name, eid, base_by_id[eid], text))
                continue
            if eid not in seen:
                merged_list.append((eid, text))
                seen.add(eid)
        merged[name] = merged_list
    return merged, order, conflicts


# The distill contract's op verbs (BUG-1308, D-01, D-02). "merge" is deliberately absent: D-10
# keeps it an authoring concept the contract rewrites into a replace plus a drop, never a verb
# this tool applies.
_OP_KEYS = {
    "add": {"op", "target", "section", "entry", "why"},
    "replace": {"op", "target", "section", "entry", "why"},
    "drop": {"op", "target", "section", "why"},
}


def _malformed(index, message):
    raise harness_merge.MergeRefusal(12, [f"MALFORMED OPS op index={index}: {message}"])


def _validate_verb(op, index):
    verb = op.get("op")
    if verb == "merge":
        raise harness_merge.MergeRefusal(
            12,
            ["MALFORMED OPS op=merge is not a mechanism op; express it as a replace on the "
             "surviving id plus a drop of the absorbed id."],
        )
    if verb not in _OP_KEYS:
        _malformed(index, f"unknown op verb {verb!r}; expected add, replace or drop")
    return verb


def _reject_multiline(value, index, field):
    """VL-01: an entry/target carrying an embedded newline (`\\n`, `\\r`, or the `\\r\\n` pair
    — this catches all three, since every one of them contains one of the two characters) would
    become a real physical line once `render` writes it verbatim, forging fake section
    headers/entries that `_check_caps` (D-07) never sees because it only ever counts parsed list
    length. Refuse it here, at the single Step A shape gate, rather than at each of render's /
    `_rebuild_section`'s write sites — the apply path's `render` must not carry this policy
    SEC-01/F1 (fix cycle 2): the check below now refuses any value for which
    `len(value.splitlines()) > 1` — the same boundary set `parse_expertise`'s `str.splitlines()`
    call recognizes (as of this Python, `\\n \\r \\v \\f \\x1c \\x1d \\x1e \\x85 \\u2028 \\u2029`,
    a superset of `\\n`/`\\r`) — so the validator and the parser share one definition of "a line"
    and cannot diverge by construction, regardless of which characters a future Python release
    adds to or removes from that set. The narrower `\\n`/`\\r` check retained below is now a
    strict subset of this one and never fires on its own.
    (REQ-07)."""
    if "\n" in value or "\r" in value:
        _malformed(index, f"{field} must be a single line")
    if len(value.splitlines()) > 1:
        _malformed(index, f"{field} must be a single line")


def _validate_target_section(op, index):
    target = op.get("target")
    if not target:
        _malformed(index, "missing required key target")
    if not isinstance(target, str):
        _malformed(index, f"target must be a string, not {type(target).__name__}")
    _reject_multiline(target, index, "target")
    section = op.get("section")
    if not section:
        _malformed(index, "missing required key section")
    if section not in CAPS:
        _malformed(index, f"section {section!r} is not one of Patterns, Gotchas, Outcomes, Open")
    return section


def _validate_entry_shape(entry, index):
    """VL-02/VL-01 for the `entry` key: must be a string, and (VL-01) a single line."""
    if not isinstance(entry, str):
        _malformed(index, f"entry must be a string, not {type(entry).__name__}")
    _reject_multiline(entry, index, "entry")


def _validate_entry_and_keys(op, index, verb):
    has_entry = "entry" in op
    if verb in ("add", "replace") and not has_entry:
        _malformed(index, "missing required key entry")
    if verb == "drop" and has_entry:
        _malformed(index, "forbidden key entry for op=drop")
    if has_entry:
        _validate_entry_shape(op["entry"], index)
    extra = set(op.keys()) - _OP_KEYS[verb]
    if extra:
        _malformed(index, f"forbidden key {sorted(extra)[0]} for op={verb}")


def _parse_op(op, index):
    """Step A, shape. Returns (verb, target, section, entry_or_None). Raises
    harness_merge.MergeRefusal(12, ...) for every shape violation; never mutates `op`."""
    if not isinstance(op, dict):
        _malformed(index, "op is not an object")
    verb = _validate_verb(op, index)
    section = _validate_target_section(op, index)
    _validate_entry_and_keys(op, index, verb)
    return verb, op["target"], section, op.get("entry")


def _base_matches(base_sections, section, target):
    """The list of base entries in `section` whose id equals `target`, in file order."""
    return [eid for eid, _ in base_sections.get(section, []) if eid == target]


def _check_base_ambiguity(matches, section, target):
    """A target id appearing more than once in its own section is ambiguous regardless of verb
    (D-03(a)); raises MergeRefusal(11) with the same line shape every verb shares."""
    if len(matches) > 1:
        raise harness_merge.MergeRefusal(
            11,
            [f"AMBIGUOUS TARGET section={section} id={target} "
             f"reason=the id appears {len(matches)} times in section {section}"],
        )


def _resolve_replace_or_drop(base_sections, section, target):
    """Step B for replace/drop: exactly one candidate must exist in the op's own section."""
    matches = _base_matches(base_sections, section, target)
    if not matches:
        raise harness_merge.MergeRefusal(
            10,
            [f"MISSING TARGET section={section} id={target} "
             "reason=no entry with this id exists in this section"],
        )
    _check_base_ambiguity(matches, section, target)


def _resolve_add(base_sections, section, target, entry):
    """Step B for add. A duplicated base id is refused as AMBIGUOUS TARGET(11) before either
    outcome below is considered (D-03(a), VL-03) — matching replace/drop on the identical base
    shape rather than silently resolving against whichever occurrence `dict()` keeps last.
    Otherwise returns True when this add is a no-op PRESERVE (identical text already present);
    raises MergeRefusal(7) — the existing CONFLICT line shape — when the id already holds
    different text."""
    matches = _base_matches(base_sections, section, target)
    _check_base_ambiguity(matches, section, target)
    if not matches:
        return False
    existing = dict(base_sections.get(section, []))
    if existing[target] == entry:
        return True
    raise harness_merge.MergeRefusal(
        7,
        [
            f"CONFLICT section={section} id={target}",
            f"  existing text: {existing[target]}",
            f"  proposed text: {entry}",
        ],
    )


def _check_proposal_ambiguity(resolved):
    """Step C: two ops resolving to the same (section, id) key, of any verb combination."""
    seen = set()
    for verb, section, target, entry, preserved in resolved:
        key = (section, target)
        if key in seen:
            raise harness_merge.MergeRefusal(
                11,
                [f"AMBIGUOUS TARGET section={section} id={target} "
                 "reason=two ops in one proposal name this target"],
            )
        seen.add(key)


def _resolve_all(base_sections, parsed_ops):
    """Steps B and C: every op resolves against the ORIGINAL base_sections, never against an
    earlier op's result, before Step D applies anything."""
    resolved = []
    for verb, target, section, entry in parsed_ops:
        if verb in ("replace", "drop"):
            _resolve_replace_or_drop(base_sections, section, target)
            preserved = False
        else:
            preserved = _resolve_add(base_sections, section, target, entry)
        resolved.append((verb, section, target, entry, preserved))
    _check_proposal_ambiguity(resolved)
    return resolved


def _rebuild_section(base_entries, section_ops, adds):
    """The Step D invariant: walk the section's BASE entries in their original order, addressing
    each by its (section, id) key, never by a position resolved earlier — then append this
    section's adds, in proposal order. Never indexes into `base_entries` or `adds`."""
    rebuilt = []
    for eid, text in base_entries:
        if eid in section_ops:
            verb, new_text = section_ops[eid]
            if verb == "replace":
                rebuilt.append((eid, new_text))
            # verb == "drop" -> emit nothing
        else:
            rebuilt.append((eid, text))
    rebuilt.extend(adds)
    return rebuilt


def _apply_resolved(base_sections, base_order, resolved):
    """Step D. A section every one of whose entries is dropped survives, empty, at its original
    position in order; a section named only by an add is created and appended to order."""
    ops_by_section = {}
    adds_by_section = {}
    for verb, section, target, entry, preserved in resolved:
        if verb in ("replace", "drop"):
            ops_by_section.setdefault(section, {})[target] = (verb, entry)
        elif not preserved:
            adds_by_section.setdefault(section, []).append((target, entry))

    merged = {name: list(entries) for name, entries in base_sections.items()}
    order = list(base_order)
    for section in set(ops_by_section) | set(adds_by_section):
        merged[section] = _rebuild_section(
            base_sections.get(section, []),
            ops_by_section.get(section, {}),
            adds_by_section.get(section, []),
        )
        if section not in order:
            order.append(section)
    return merged, order


def _check_caps(merged):
    """Step E: caps evaluated once, on the final merged state (D-07)."""
    for name, cap in CAPS.items():
        size = len(merged.get(name, []))
        if size > cap:
            raise harness_merge.MergeRefusal(
                8, [f"CAP EXCEEDED section={name} cap={cap} union_size={size}"]
            )


def _build_outcomes(resolved):
    outcomes = []
    for verb, section, target, entry, preserved in resolved:
        if verb == "replace":
            outcomes.append(("REPLACED", target))
        elif verb == "drop":
            outcomes.append(("DROPPED", target))
        elif preserved:
            outcomes.append(("PRESERVED", target))
        else:
            outcomes.append(("ADDED", target))
    return outcomes


def resolve_ops(base_sections, base_order, ops):
    """PURE: no IO, no sys.exit, never mutates base_sections or base_order. Raises
    harness_merge.MergeRefusal(code, lines) for every refusal (D-01..D-10). Returns
    (merged, order, outcomes) where outcomes is the per-op verb in op order, paired with id."""
    if not isinstance(ops, list):
        raise harness_merge.MergeRefusal(
            12, ["MALFORMED OPS payload is not a list; pass the expertise_update list itself"]
        )
    parsed_ops = [_parse_op(op, i) for i, op in enumerate(ops)]
    resolved = _resolve_all(base_sections, parsed_ops)
    merged, order = _apply_resolved(base_sections, base_order, resolved)
    _check_caps(merged)
    return merged, order, _build_outcomes(resolved)


def default_title(file_path):
    base = os.path.basename(file_path)
    if base.endswith(".md"):
        base = base[:-3]
    return f"# Expertise — {base}"


EXPERTISE_TAIL = re.compile(
    r"(?:^|/)\.harness/(?:[^/]+/)?expertise/(harness-[a-z0-9-]+)\.md$")


def require_expertise_destination(file_path):
    """REFUSE a --file that is not an Expertise file. Raises harness_merge.MergeRefusal(9).

    WHY THIS EXISTS, and it is not defence-in-depth for its own sake. `bash-write-guard.sh`
    is ALLOW-BY-OMISSION: it scans a command for a write PATTERN it recognises — a
    redirect, `sed -i`, `rm`, `cp`, `tee` — and when it finds none it exits 0 at
    `:617`, BEFORE the reviewer read-only denial at `:628` and before the domain walk at
    `:676`. A `python3 … expertise-merge.py apply --file <anything>` command carries no
    such pattern, so it reaches neither check.

    REPRODUCED 2026-08-21, and this is the measurement that made the fix a ship gate:
    `harness-code-reviewer` — a READ-ONLY persona — invoking this tool against
    `src/main.py` exits 0, while `printf x >> src/main.py` from the same persona exits 2.
    FEAT-30's own T-07 then rewired `harness-distill/SKILL.md` to instruct every agent to
    use exactly this invocation shape, which turned a latent hole into the recommended
    path.

    WHAT THIS CANNOT DO, stated so nobody mistakes it for the whole fix: this tool has NO
    identity source. No `agent_type` reaches a Bash-invoked CLI and no environment
    variable carries one, so it cannot check WHO called it — only WHERE it writes. A
    documentor overwriting the pm's Expertise file is still not caught here. That half
    needs the guard's default inverted for known first-party write tools, which is
    enforcement-layer work and is filed separately.

    Both tiers are legal (FEAT-27): `.harness/expertise/<agent>.md` and
    `.harness/<repo>/expertise/<agent>.md`. Matched on the REALPATH, so `..` and a symlink
    cannot walk out of the tier and back in under a legal-looking tail.
    """
    return harness_merge.require_destination(
        file_path,
        EXPERTISE_TAIL,
        "an Expertise file",
        [
            "  --file must be .harness/expertise/<agent>.md or "
            ".harness/<repo>/expertise/<agent>.md, and <agent> must be a harness-* "
            "name.",
            "  This tool merges Expertise and writes nothing else. A path the domain "
            "hook would deny does not become writable by routing through a CLI.",
        ],
    )


def cmd_apply(args):
    file_path = args.file
    try:
        resolved = require_expertise_destination(file_path)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)

    if args.entries == "-":
        proposal_text = sys.stdin.read()
    else:
        with open(args.entries, encoding="utf-8") as f:
            proposal_text = f.read()
    _, prop_sections, prop_order, _ = parse_expertise(proposal_text)

    result = {}

    def transform(base_bytes):
        if base_bytes is not None:
            base_text = base_bytes.decode("utf-8")
            title, base_sections, base_order, headers = parse_expertise(base_text)
        else:
            title, base_sections, base_order, headers = None, {}, [], {}

        if UNION_APPLY:
            merged, order, conflicts = compute_union(
                base_sections, base_order, prop_sections, prop_order
            )
            if conflicts:
                lines = []
                for name, eid, base_txt, prop_txt in conflicts:
                    lines.append(f"CONFLICT section={name} id={eid}")
                    lines.append(f"  existing text: {base_txt}")
                    lines.append(f"  proposed text: {prop_txt}")
                raise harness_merge.MergeRefusal(7, lines)

            for name, cap in CAPS.items():
                size = len(merged.get(name, []))
                if size > cap:
                    raise harness_merge.MergeRefusal(
                        8,
                        [f"CAP EXCEEDED section={name} cap={cap} union_size={size}"],
                    )
        else:
            # UNION_APPLY off: reproduce today's whole-file overwrite exactly. No comparison
            # against the base at all — that absence of comparison IS the last-writer-wins bug.
            merged, order = prop_sections, prop_order

        out_title = title if title is not None else default_title(file_path)

        base_ids_by_section = {
            name: {eid for eid, _ in base_sections.get(name, [])} for name in order
        }
        added, preserved = [], []
        for name in order:
            for eid, _ in merged.get(name, []):
                if eid in base_ids_by_section.get(name, ()):
                    preserved.append(eid)
                else:
                    added.append(eid)

        result["added"] = added
        result["preserved"] = preserved

        return render(out_title, merged, order, headers).encode("utf-8")

    try:
        harness_merge.locked_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line)
        sys.exit(refusal.code)

    for eid in result.get("added", []):
        print(f"ADDED {eid}")
    for eid in result.get("preserved", []):
        print(f"PRESERVED {eid}")
    print(f"APPLIED {file_path}")
    sys.exit(0)


def cmd_ops(args):
    """add/replace/drop against an Expertise file (D-01). Compatible with cmd_apply: same
    destination refusal (exit 9, stderr), same lock file (D-09), refusal lines to stdout."""
    file_path = args.file
    try:
        resolved = require_expertise_destination(file_path)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)

    if args.ops == "-":
        ops_text = sys.stdin.read()
    else:
        with open(args.ops, encoding="utf-8") as f:
            ops_text = f.read()

    result = {}

    def transform(base_bytes):
        try:
            ops = json.loads(ops_text)
        except json.JSONDecodeError as exc:
            raise harness_merge.MergeRefusal(
                12, [f"MALFORMED OPS could not decode JSON: {exc}"]
            )

        if base_bytes is not None:
            title, base_sections, base_order, headers = parse_expertise(
                base_bytes.decode("utf-8")
            )
        else:
            title, base_sections, base_order, headers = None, {}, [], {}

        merged, order, outcomes = resolve_ops(base_sections, base_order, ops)
        result["outcomes"] = outcomes
        out_title = title if title is not None else default_title(file_path)
        return render(out_title, merged, order, headers).encode("utf-8")

    try:
        harness_merge.locked_update(resolved, transform)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line)
        sys.exit(refusal.code)

    for verb, target in result.get("outcomes", []):
        print(f"{verb} {target}")
    print(f"APPLIED {file_path}")
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(prog="expertise-merge.py")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_apply = sub.add_parser("apply", help="union-merge a proposal into an Expertise file")
    p_apply.add_argument("--file", required=True, help="path to the Expertise markdown file")
    p_apply.add_argument(
        "--entries", required=True, help="path to the proposed entries, or - for stdin"
    )
    p_apply.set_defaults(func=cmd_apply)

    p_ops = sub.add_parser("ops", help="apply add/replace/drop ops to an Expertise file")
    p_ops.add_argument("--file", required=True, help="path to the Expertise markdown file")
    p_ops.add_argument(
        "--ops",
        required=True,
        help="path to a JSON list of add/replace/drop ops, or - for stdin",
    )
    p_ops.set_defaults(func=cmd_ops)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
