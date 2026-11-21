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
    9  --file is not an Expertise file destination — nothing applied
    11 AMBIGUOUS TARGET — the same id appears more than once for one target — nothing applied

python3 stdlib only, no third-party imports, so this runs on any machine that runs the harness.

Locking and the atomic replace are FEAT-32 T-05's rewire onto harness_merge (D-02): this file no
longer carries its own lock or replace primitive — see harness_merge.py's module docstring for
the lock dialect this tool now shares with plan-merge.py and observations-merge.py.

FEAT-2225 T-01 adds three subcommands on the same engine and the same harness_merge core, no
second writer and no second lock lifetime:

    expertise-merge.py member-ops      --root R --feature F --persona P --runtime-id C --parent-id PP
                                       --tier craft|repository [--repository SEG] --ops <path or ->
                                       [--supersedes BATCH-ID ... --base MAIN-SHA]
    expertise-merge.py verify-receipt  --root R --feature F --persona P --runtime-id C --parent-id PP
                                       --tier ... [--repository SEG] --claimed <path or -> [--base SHA]
    expertise-merge.py replay          --root R --feature F --base MAIN-SHA [--check]

member-ops applies ordinary ops to the persona's own file beneath the feature checkout and persists
notes/expertise-receipt-<sha256(runtime id)>.json beside the feature (it travels in the PR).
verify-receipt is read-only. replay rebuilds each touched file from the main blob and replays the
PR's active receipt batches. Their stdout is one JSON object; extra exit codes:
    13 replay refused (changed/vanished original, independent callers, cap, candidate) — the JSON
       `refusals` list names persona, run, destination, section/id, batch identity and reason
    14 the computed candidate failed check-expertise — nothing applied
    15 receipt evidence missing, mismatched, unauthorized or ambiguous — fails closed
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness_merge  # noqa: E402  (local import, after sys.path fix-up)

# DEC-145's four canonical sections and their entry caps, verbatim. This is the one place this
# tool spells them; test-expertise-merge.py's case 8 reads check-expertise.py's own CAPS mapping
# as TEXT and asserts the two agree, rather than adding a third copy of these numbers anywhere.
CAPS = {"Patterns": 15, "Gotchas": 15, "Outcomes": 10, "Open": 5}

# The same two patterns check-expertise.py parses an Expertise file with, so a file this tool
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
        # A continuation line — check-expertise.py treats any indented, non-empty line right
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


def _check_proposal_duplicate_ids(prop_sections, prop_order):
    """A proposal naming the same id twice within one section is ambiguous on the proposal
    alone, before any base comparison: raises MergeRefusal(11) on the second occurrence,
    comparing no text at all. Mirrors _check_proposal_ambiguity, whose message differs only in
    saying ops where this one says entries."""
    for name in prop_order:
        seen = set()
        for eid, _ in prop_sections.get(name, []):
            if eid in seen:
                raise harness_merge.MergeRefusal(
                    11,
                    [f"AMBIGUOUS TARGET section={name} id={eid} "
                     "reason=two entries in one proposal name this target"],
                )
            seen.add(eid)


def compute_union(base_sections, base_order, prop_sections, prop_order):
    """The UNION, keyed by section and id, preserving existing order and appending new ids in
    the order the proposal gives them. Returns (merged, order, conflicts). A conflict is
    (section, id, base_text, proposed_text) for the same id carrying different text — nothing
    is dropped to produce this return; the caller decides whether it is safe to write. Refuses
    with MergeRefusal(11) before any base comparison if the proposal itself names the same
    (section, id) twice."""
    _check_proposal_duplicate_ids(prop_sections, prop_order)
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


def _validate_target_grammar(target, index):
    """VL-06: refuse a `target` that `ENTRY_RE` would not parse back out unchanged from the
    exact line `render` writes for it. Derived, not re-typed: this round-trips `target` through
    `ENTRY_RE` itself via the synthetic line `f"- {target}: x"` `render` would produce, then
    requires the anchored match's captured id equal `target` verbatim — never a second
    hand-copied `[A-Za-z]{1,3}-\\d+` literal (REQ-07 forbids editing `ENTRY_RE`, and duplicating
    its class is the VL-05 lesson this file already learned). `"PPPP-1"` fails to match at all;
    `"P-01: fake prefix"` matches but captures `"P-01" != target`, so the containment vector
    (a valid id embedded inside a longer target) is closed by the equality, not by a hand-rolled
    anchor."""
    match = ENTRY_RE.match(f"- {target}: x")
    if not match or match.group(1) != target:
        _malformed(index, f"target {target!r} does not match the entry id grammar")


def _validate_target_section(op, index):
    target = op.get("target")
    if not target:
        _malformed(index, "missing required key target")
    if not isinstance(target, str):
        _malformed(index, f"target must be a string, not {type(target).__name__}")
    _reject_multiline(target, index, "target")
    _validate_target_grammar(target, index)
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


def resolve_ops(base_sections, base_order, ops, enforce_caps=True):
    """PURE: no IO, no sys.exit, never mutates base_sections or base_order. Raises
    harness_merge.MergeRefusal(code, lines) for every refusal (D-01..D-10). Returns
    (merged, order, outcomes) where outcomes is the per-op verb in op order, paired with id.
    `enforce_caps=False` defers the Step E cap check to a caller that evaluates it once on a
    complete candidate (replay applies many batches in sequence; an intermediate state is not
    the candidate)."""
    if not isinstance(ops, list):
        raise harness_merge.MergeRefusal(
            12, ["MALFORMED OPS payload is not a list; pass the expertise_update list itself"]
        )
    parsed_ops = [_parse_op(op, i) for i, op in enumerate(ops)]
    resolved = _resolve_all(base_sections, parsed_ops)
    merged, order = _apply_resolved(base_sections, base_order, resolved)
    if enforce_caps:
        _check_caps(merged)
    return merged, order, _build_outcomes(resolved)


def default_title(file_path):
    base = os.path.basename(file_path)
    if base.endswith(".md"):
        base = base[:-3]
    return f"# Expertise — {base}"


_EXPERTISE_REL = r"\.harness/(?:[^/]+/)?expertise/(harness-[a-z0-9-]+)\.md"
EXPERTISE_TAIL = re.compile(r"(?:^|/)" + _EXPERTISE_REL + "$")


def require_expertise_destination(file_path):
    """REFUSE a --file that is not an Expertise file. Raises harness_merge.MergeRefusal(9).

    WHY THIS EXISTS, and it is not defence-in-depth for its own sake. `bash-write-guard.py`
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


def _add_identity_arguments(parser):
    parser.add_argument("--root", required=True, help="the feature checkout (host-bound)")
    parser.add_argument("--feature", required=True)
    parser.add_argument("--persona", required=True)
    parser.add_argument("--runtime-id", required=True)
    parser.add_argument("--parent-id", required=True)
    parser.add_argument("--tier", required=True, choices=("craft", "repository"))
    parser.add_argument("--repository", help="literal declared repository segment (tier=repository)")


def _read_stream(spec):
    if spec == "-":
        return sys.stdin.read()
    with open(spec, encoding="utf-8") as fh:
        return fh.read()


def _run_json(action, exit_code=lambda result: 0):
    """Run `action`, print its result as one JSON object. A MergeRefusal prints its lines and
    exits with its code, exactly as cmd_ops does."""
    try:
        result = action()
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line)
        sys.exit(refusal.code)
    print(json.dumps(result, sort_keys=True))
    sys.exit(exit_code(result))


def cmd_member_ops(args):
    _run_json(lambda: member_ops(
        args.root, args.feature, args.persona, args.runtime_id, args.parent_id, args.tier,
        args.repository, _read_stream(args.ops), args.supersedes or (), args.base))


def cmd_verify_receipt(args):
    _run_json(lambda: verify_receipt(
        args.root, args.feature, args.persona, args.runtime_id, args.parent_id, args.tier,
        args.repository, _decode_json(_read_stream(args.claimed), "claimed list"), args.base))


def cmd_replay(args):
    _run_json(lambda: replay_feature(args.root, args.feature, args.base, args.check),
              lambda result: 0 if result["replayed"] else EXIT_REPLAY)


# ---------------------------------------------------------------------------------------------
# FEAT-2225 T-01 — member-ops, receipts, read-only verification and replay.
#
# The host (T-04) owns caller authority: it binds root, feature, persona and runtime ids. This
# core checks WHERE the write lands and that the ordered evidence agrees; it delegates parsing,
# section/id resolution, caps, the flock and the atomic replace to resolve_ops and harness_merge.
# There is no journal, pending state or resume path: a target write that is not followed by its
# receipt fails the call, and the disagreement fails closed in verify-receipt and replay.
# ---------------------------------------------------------------------------------------------
RECEIPT_SCHEMA = 1
EXIT_REPLAY, EXIT_CANDIDATE, EXIT_EVIDENCE = 13, 14, 15
SUBPROCESS_TIMEOUT_SECONDS = 30
CHECK_EXPERTISE_BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "check-expertise.py")
PERSONA_RE = re.compile(r"^harness-[a-z0-9-]+$")
SEGMENT_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
FEATURE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
REV_RE = re.compile(r"^[0-9a-fA-F]{7,64}$")
RECEIPT_NAME_RE = re.compile(r"^expertise-receipt-([0-9a-f]{64})\.json$")
EXPERTISE_PATH_RE = re.compile("^" + _EXPERTISE_REL + "$")
HEADER_KEYS = ("persona", "feature", "runtime_id", "parent_id")
RECEIPT_KEYS = {"schema", "batches", *HEADER_KEYS}
IDENTITY_KEYS = ("seq", "destination", "ops", "originals", "before_sha256", "after_sha256", "supersedes")
BATCH_KEYS = {"id", "recorded_at_ns", *IDENTITY_KEYS}


def _refuse(code, *lines):
    raise harness_merge.MergeRefusal(code, lines)


def _sha256(data):
    return hashlib.sha256(data).hexdigest()


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _decode_json(text, what):
    try:
        return json.loads(text)
    except ValueError as exc:
        _refuse(12, f"MALFORMED {what} could not decode JSON: {exc}")


def section_counts(sections):
    return {name: len(sections.get(name, [])) for name in CAPS}


# ---- destination and location ----------------------------------------------------------------

def destination_rel(persona, tier, segment):
    """The checkout-relative path of the persona's own file. The persona is a host-bound name
    and the repository segment a literal token, never a free path."""
    if not _is_persona(persona):
        _refuse(9, f"REFUSED persona {persona!r} is not a harness-* persona name")
    if tier == "craft" and segment is None:
        return f".harness/expertise/{persona}.md"
    if tier == "repository" and _declared_segment(segment):
        return f".harness/{segment}/expertise/{persona}.md"
    _refuse(9, f"REFUSED destination tier={tier!r} repository={segment!r}: use craft with no "
               "repository segment, or repository with one literal declared segment")


def resolve_destination(root, rel):
    """Absolute path of `rel` beneath `root`, refusing any resolution that is not EXACTLY that
    path: a symlink anywhere in the chain (even one staying inside) fails, as does an undeclared
    repository segment. Creates nothing."""
    real_root = os.path.realpath(root)
    if not os.path.isdir(real_root):
        _refuse(9, f"REFUSED root {root!r} is not a directory")
    parts = rel.split("/")
    if len(parts) == 4 and parts[1] not in harness_segments(real_root):
        _refuse(9, f"REFUSED repository segment {parts[1]!r} is not declared under {real_root}/.harness")
    path = os.path.join(real_root, *parts)
    if os.path.realpath(path) != path:
        _refuse(9, f"REFUSED {rel} resolves to {os.path.realpath(path)}, outside the feature checkout {real_root}")
    return require_expertise_destination(path)


def harness_segments(real_root):
    """The segment directories of the checkout's `.harness`: a repository-tier destination and a
    feature directory may live only under one of these, never under a path the caller invents."""
    harness_dir = os.path.join(real_root, ".harness")
    try:
        names = sorted(os.listdir(harness_dir))
    except OSError:
        return []
    return [name for name in names if os.path.isdir(os.path.join(harness_dir, name))]


def feature_directory(root, feature):
    """The one `.harness/<segment>/features/<feature>` directory under `root`."""
    if not (isinstance(feature, str) and FEATURE_RE.match(feature)):
        _refuse(9, f"REFUSED feature {feature!r} is not a feature id")
    real_root = os.path.realpath(root)
    harness_dir = os.path.join(real_root, ".harness")
    found = [p for p in (os.path.join(harness_dir, s, "features", feature) for s in harness_segments(real_root))
             if os.path.isdir(p) and os.path.realpath(p) == p]
    if len(found) != 1:
        _refuse(9, f"REFUSED feature {feature} has {len(found)} feature directories under "
                   f"{harness_dir}; exactly one is required")
    return found[0]


def receipt_location(feature_dir, runtime_id):
    digest = _sha256(runtime_id.encode("utf-8"))
    return os.path.join(feature_dir, "notes", f"expertise-receipt-{digest}.json")


def parse_state(data, rel):
    """(title, sections, order, headers) of file bytes; an absent file gets the canonical title
    and the four empty sections."""
    if data is None:
        return default_title(rel), {name: [] for name in CAPS}, list(CAPS), {}
    title, sections, order, headers = parse_expertise(data.decode("utf-8"))
    return title or default_title(rel), sections, order, headers


def render_state(title, sections, order, headers):
    return render(title, sections, order, headers).encode("utf-8")


def check_candidate(rel, data):
    """Run check-expertise on the computed candidate, placed at its real relative path so the
    checker classifies the tier and title exactly as it would the landed file."""
    with tempfile.TemporaryDirectory(prefix="expertise-candidate-") as tmp:
        path = os.path.join(tmp, *rel.split("/"))
        os.makedirs(os.path.dirname(path))
        with open(path, "wb") as fh:
            fh.write(data)
        try:
            proc = subprocess.run([sys.executable, CHECK_EXPERTISE_BIN, path], capture_output=True,
                                  text=True, timeout=SUBPROCESS_TIMEOUT_SECONDS)
        except (OSError, subprocess.TimeoutExpired) as exc:
            _refuse(EXIT_CANDIDATE, f"CHECK-EXPERTISE could not run on {rel}: {exc}")
        report = [line.replace(path, rel) for line in proc.stdout.splitlines()]
    if proc.returncode != 0:
        _refuse(EXIT_CANDIDATE, f"CHECK-EXPERTISE FAILED {rel}", *report)


# ---- receipt model ---------------------------------------------------------------------------

def batch_identity(header, batch):
    """A batch's stable content-derived identity. The timestamp is deliberately outside it."""
    core = {key: batch[key] for key in IDENTITY_KEYS}
    core.update({key: header[key] for key in HEADER_KEYS})
    return _sha256(_canonical(core))


def _invalid(name, message):
    _refuse(EXIT_EVIDENCE, f"INVALID RECEIPT {name}: {message}")


def _require(condition, name, message):
    if not condition:
        _invalid(name, message)


def _is_persona(value):
    return isinstance(value, str) and bool(PERSONA_RE.match(value))


def _is_text(value):
    return isinstance(value, str) and bool(value)


def _declared_segment(segment):
    return isinstance(segment, str) and bool(SEGMENT_RE.match(segment)) and segment != "expertise"


def _destination_form_ok(persona, rel):
    if not isinstance(rel, str):
        return False
    if rel == f".harness/expertise/{persona}.md":
        return True
    match = re.fullmatch(r"\.harness/([^/]+)/expertise/(.+)\.md", rel)
    return bool(match and match.group(2) == persona and _declared_segment(match.group(1)))


def _check_original(name, index, verb, entry, original):
    possible = (original is None or original == entry) if verb == "add" else isinstance(original, str)
    _require(possible, name, f"originals[{index}] is impossible for op={verb}")


def _parse_recorded_op(name, op, index):
    try:
        return _parse_op(op, index)
    except harness_merge.MergeRefusal as exc:
        _invalid(name, "; ".join(exc.lines))


def _record_describes(record, section, target):
    return (isinstance(record, dict) and set(record) == {"section", "target", "original"}
            and record["section"] == section and record["target"] == target)


def _validate_op_record(name, index, op, record):
    verb, target, section, entry = _parse_recorded_op(name, op, index)
    _require(_record_describes(record, section, target), name, f"originals[{index}] does not describe op {index}")
    _check_original(name, index, verb, entry, record["original"])


def _validate_ops(name, batch):
    ops, originals = batch["ops"], batch["originals"]
    _require(isinstance(ops, list) and isinstance(originals, list) and len(ops) == len(originals),
             name, "ops and originals must be parallel lists")
    for index, (op, record) in enumerate(zip(ops, originals)):
        _validate_op_record(name, index, op, record)


def _validate_batch_fields(name, batch):
    _require(batch["before_sha256"] is None or HEX64_RE.match(str(batch["before_sha256"])), name, "bad before_sha256")
    _require(HEX64_RE.match(str(batch["after_sha256"])), name, "bad after_sha256")
    refs = batch["supersedes"]
    _require(isinstance(refs, list) and all(isinstance(r, str) and HEX64_RE.match(r) for r in refs),
             name, "supersedes must be a list of batch identities")
    _require(isinstance(batch["recorded_at_ns"], int) and not isinstance(batch["recorded_at_ns"], bool),
             name, "recorded_at_ns must be an integer")


def _validate_batch(name, header, index, batch):
    _require(isinstance(batch, dict) and set(batch) == BATCH_KEYS, name, f"batch {index + 1} has the wrong keys")
    _require(batch["seq"] == index + 1, name, f"batch {index + 1} is out of sequence")
    _require(_destination_form_ok(header["persona"], batch["destination"]), name,
             f"batch {index + 1} destination is not this persona's file")
    _validate_ops(name, batch)
    _validate_batch_fields(name, batch)


def _validate_receipt_header(name, raw, feature, digest):
    _require(isinstance(raw, dict) and set(raw) == RECEIPT_KEYS and raw["schema"] == RECEIPT_SCHEMA,
             name, "unexpected shape or schema")
    _require(_is_persona(raw["persona"]), name, "bad persona")
    _require(raw["feature"] == feature, name, f"receipt is for feature {raw['feature']!r}, not {feature!r}")
    _require(_is_text(raw["runtime_id"]) and _sha256(raw["runtime_id"].encode("utf-8")) == digest,
             name, "runtime_id does not match the file name")
    _require(_is_text(raw["parent_id"]), name, "bad parent_id")


def _validate_receipt(name, raw, feature, digest):
    _validate_receipt_header(name, raw, feature, digest)
    _require(isinstance(raw["batches"], list), name, "batches must be a list")
    for index, batch in enumerate(raw["batches"]):
        _validate_batch(name, raw, index, batch)


def parse_receipt(name, data, feature):
    match = RECEIPT_NAME_RE.match(name)
    _require(match is not None, name, "not a receipt file name")
    try:
        raw = json.loads(data.decode("utf-8"))
    except ValueError:
        _invalid(name, "not JSON")
    _validate_receipt(name, raw, feature, match.group(1))
    return raw


def read_receipt_file(path, feature):
    try:
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError as exc:
        _invalid(os.path.basename(path), f"unreadable: {exc}")
    return parse_receipt(os.path.basename(path), data, feature), _sha256(data)


def _flatten(raw, rel_path, file_sha):
    header = {key: raw[key] for key in HEADER_KEYS}
    return [dict(batch, receipt=rel_path, receipt_sha256=file_sha, **header) for batch in raw["batches"]]


def ordered(entries):
    return sorted(entries, key=lambda e: (e["recorded_at_ns"], e["runtime_id"], e["seq"]))


# ---- git (read-only) -------------------------------------------------------------------------

def _git(real_root, *args):
    try:
        return subprocess.run(["git", "-C", real_root, "-c", "core.quotepath=off", *args],
                              capture_output=True, timeout=SUBPROCESS_TIMEOUT_SECONDS)
    except (OSError, subprocess.TimeoutExpired) as exc:
        _refuse(EXIT_EVIDENCE, f"GIT FAILED {' '.join(args[:2])}: {exc}")


def _git_lines(real_root, *args):
    proc = _git(real_root, *args)
    if proc.returncode != 0:
        _refuse(EXIT_EVIDENCE, f"GIT FAILED {' '.join(args[:2])}: {proc.stderr.decode(errors='replace').strip()}")
    return proc.stdout.decode().splitlines()


def resolve_base(real_root, base):
    if not (isinstance(base, str) and REV_RE.match(base)):
        _refuse(EXIT_EVIDENCE, f"BASE UNRESOLVED {base!r} is not a main commit sha")
    proc = _git(real_root, "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}")
    sha = proc.stdout.decode().strip()
    if proc.returncode != 0 or not sha:
        _refuse(EXIT_EVIDENCE, f"BASE UNRESOLVED {base} is not a commit in {real_root}")
    return sha


def base_blob(real_root, base_sha, rel):
    """The exact bytes of `rel` at the main base, or None when main does not carry it."""
    proc = _git(real_root, "cat-file", "blob", f"{base_sha}:./{rel}")
    return proc.stdout if proc.returncode == 0 else None


def _changed_expertise_paths(real_root, base_sha):
    """Expertise files this checkout changed relative to where it forked from the base."""
    fork = _git_lines(real_root, "merge-base", base_sha, "HEAD")
    if not fork:
        _refuse(EXIT_EVIDENCE, f"BASE UNRELATED {base_sha} shares no history with this checkout")
    changed = _git_lines(real_root, "diff", "--relative", "--name-only", fork[0])
    changed += _git_lines(real_root, "ls-files", "--others", "--exclude-standard")
    return {path for path in changed if EXPERTISE_PATH_RE.match(path)}


def pr_receipt_paths(real_root, feature_dir, base_sha):
    """This PR's receipt files: every receipt in the feature's notes that the main base does not
    already carry. A receipt already on main belongs to an earlier distill and is never read."""
    notes = os.path.join(feature_dir, "notes")
    try:
        names = sorted(n for n in os.listdir(notes) if RECEIPT_NAME_RE.match(n))
    except OSError:
        return []
    paths = [os.path.join(notes, n) for n in names]
    if base_sha is None:
        return paths
    proc = _git(real_root, "ls-tree", "-r", "--name-only", base_sha, "--", os.path.relpath(notes, real_root))
    known = set(proc.stdout.decode().splitlines()) if proc.returncode == 0 else set()
    return [p for p in paths if os.path.relpath(p, real_root) not in known]


# ---- supersession graph ----------------------------------------------------------------------

def _check_references(entries):
    by_id = {}
    for entry in entries:
        if entry["id"] in by_id:
            _refuse(EXIT_EVIDENCE, f"DUPLICATE BATCH {entry['id']} appears in more than one receipt position")
        by_id[entry["id"]] = entry
    for entry in entries:
        for ref in entry["supersedes"]:
            _check_reference(entry, by_id.get(ref), ref)
    return by_id


def _check_reference(entry, target, ref):
    label = f"batch={entry['id']} references={ref}"
    if target is None:
        _refuse(EXIT_EVIDENCE, f"SUPERSEDES MISSING {label}: no such batch in this PR's receipts")
    same_scope = all(target[k] == entry[k] for k in ("persona", "feature", "destination"))
    if not same_scope:
        _refuse(EXIT_EVIDENCE, f"UNAUTHORIZED SUPERSESSION {label}: only the same persona, feature and destination may retire a batch")
    if target is entry or (target["receipt"] == entry["receipt"] and target["seq"] >= entry["seq"]):
        _refuse(EXIT_EVIDENCE, f"SUPERSEDES NOT EARLIER {label}")


def _check_acyclic(by_id):
    done = set()

    def visit(ident, path):
        if ident in path:
            _refuse(EXIT_EVIDENCE, f"CYCLIC SUPERSESSION through batch={ident}")
        if ident in done:
            return
        for ref in by_id[ident]["supersedes"]:
            visit(ref, path | {ident})
        done.add(ident)

    for ident in by_id:
        visit(ident, frozenset())


def _retired(entries):
    retired = {}
    for entry in entries:
        for ref in entry["supersedes"]:
            if retired.setdefault(ref, entry["id"]) != entry["id"]:
                _refuse(EXIT_EVIDENCE, f"AMBIGUOUS SUPERSESSION batch={ref} is superseded by both {retired[ref]} and {entry['id']}")
    return retired


def active_entries(entries):
    """The batches no validated successful replacement has retired, in input order."""
    _check_acyclic(_check_references(entries))
    retired = _retired(entries)
    return [e for e in entries if e["id"] not in retired]


def _check_identities(entries):
    for entry in entries:
        if batch_identity(entry, entry) != entry["id"]:
            _refuse(EXIT_EVIDENCE, f"IDENTITY MISMATCH batch={entry['id']} in {entry['receipt']}: content does not hash to its identity")


def load_active(root, feature, base_sha):
    """(all entries, active entries, receipt manifest) of the current PR's receipts. Missing,
    unreadable or tampered evidence refuses with 15; nothing here writes."""
    real_root = os.path.realpath(root)
    entries, manifest = [], []
    for path in pr_receipt_paths(real_root, feature_directory(real_root, feature), base_sha):
        raw, digest = read_receipt_file(path, feature)
        rel = os.path.relpath(path, real_root)
        entries.extend(_flatten(raw, rel, digest))
        manifest.append({"path": rel, "sha256": digest})
    active = active_entries(entries)
    _check_identities(entries)
    return entries, active, manifest


# ---- replay engine ---------------------------------------------------------------------------

def _next_free_id(prefix, taken_ids):
    """The first free positive numeric id for `prefix`, zero-padded to at least two digits."""
    used = set()
    for eid in taken_ids:
        head, _, number = eid.partition("-")
        if head == prefix and number.isdigit():
            used.add(int(number))
    n = 1
    while n in used:
        n += 1
    return f"{prefix}-{n:02d}"


class _DestinationReplay:
    """One destination file rebuilt from its main blob, then each active batch replayed in
    recorded order. A refused batch changes nothing and is reported; the caller decides to write
    only when no batch of any destination refused."""

    def __init__(self, rel, blob):
        self.rel = rel
        self.title, self.sections, self.order, self.headers = parse_state(blob, rel)
        self.remap, self.touched, self.mappings, self.refusals, self.entries = {}, {}, [], [], []

    def _record(self, entry, code, reason, section=None, target=None, runtimes=None):
        self.refusals.append({
            "persona": entry["persona"], "runtimes": runtimes or [entry["runtime_id"]],
            "destination": self.rel, "section": section, "target": target,
            "batches": [entry["id"]], "code": code, "reason": reason})

    def apply_batch(self, entry):
        self.entries.append(entry)
        reserved = {(op["section"], op["target"]) for op in entry["ops"]}
        effective = [self._effective_op(entry, op, rec["original"], reserved)
                     for op, rec in zip(entry["ops"], entry["originals"])]
        if any(op is None for op in effective):
            return
        try:
            merged, order, _ = resolve_ops(self.sections, self.order, effective, enforce_caps=False)
        except harness_merge.MergeRefusal as exc:
            self._record(entry, exc.code, "; ".join(exc.lines))
            return
        self.sections, self.order = merged, order

    def _effective_op(self, entry, op, original, reserved):
        """The op as it must be applied to the current state, or None after recording a refusal."""
        section = op["section"]
        target = self.remap.get((entry["runtime_id"], section, op["target"]), op["target"])
        if op["op"] == "add":
            return dict(op, target=self._add_target(entry, op, target, reserved))
        problem = self._edit_problem(entry["runtime_id"], op, target, original)
        if problem is None:
            return dict(op, target=target)
        self._record(entry, EXIT_REPLAY, problem[0], section, target, problem[1])
        return None

    def _add_target(self, entry, op, target, reserved):
        section = op["section"]
        existing = dict(self.sections.get(section, [])).get(target)
        if existing is None or existing == op["entry"]:
            return target
        taken = [eid for eid, _ in self.sections.get(section, [])] + [t for s, t in reserved if s == section]
        fresh = _next_free_id(target.split("-", 1)[0], taken)
        reserved.add((section, fresh))
        self.remap[(entry["runtime_id"], section, op["target"])] = fresh
        self.mappings.append({
            "persona": entry["persona"], "runtime_id": entry["runtime_id"], "destination": self.rel,
            "section": section, "original_id": op["target"], "replayed_id": fresh, "batch": entry["id"]})
        return fresh

    def _edit_problem(self, runtime, op, target, original):
        """(reason, runtimes) when a replace/drop cannot be replayed, else None. Independent
        callers are checked BEFORE the idempotence test so an identical edit cannot hide one."""
        section = op["section"]
        prior = self.touched.setdefault((section, target), runtime)
        if prior != runtime:
            return (f"INDEPENDENT callers {prior} and {runtime} both change {section} {target}; "
                    "the members must re-judge or curate", sorted([prior, runtime]))
        current = dict(self.sections.get(section, [])).get(target)
        if current == original or (op["op"] == "replace" and current == op["entry"]):
            return None
        if current is None:
            return (f"DISAPPEARED {section} {target}: recorded original {original!r} is gone from the base", [runtime])
        return (f"CHANGED {section} {target}: recorded original {original!r} but the base now holds {current!r}", [runtime])

    def _candidate_refusal(self, refusal):
        entries = self.entries
        match = re.search(r"section=(\w+)", refusal.lines[0])
        self.refusals.append({
            "persona": entries[0]["persona"] if entries else None,
            "runtimes": sorted({e["runtime_id"] for e in entries}), "destination": self.rel,
            "section": match.group(1) if match else None, "target": None,
            "batches": [e["id"] for e in entries], "code": refusal.code,
            "reason": "; ".join(refusal.lines)})

    def finish(self):
        """The complete candidate bytes after caps and check-expertise, or None when anything refused."""
        if self.refusals:
            return None
        try:
            _check_caps(self.sections)
            data = render_state(self.title, self.sections, self.order, self.headers)
            check_candidate(self.rel, data)
        except harness_merge.MergeRefusal as refusal:
            self._candidate_refusal(refusal)
            return None
        return data


def _by_destination(active):
    groups = {}
    for entry in ordered(active):
        groups.setdefault(entry["destination"], []).append(entry)
    return dict(sorted(groups.items()))


def _check_coverage(real_root, base_sha, entries):
    uncovered = _changed_expertise_paths(real_root, base_sha) - {e["destination"] for e in entries}
    if uncovered:
        _refuse(EXIT_EVIDENCE, f"UNRECEIPTED CHANGE {sorted(uncovered)}: Expertise changed with no receipt in this PR")


def _plan_destination(real_root, base_sha, rel, batches):
    path = resolve_destination(real_root, rel)
    if not os.path.isfile(path):
        _refuse(EXIT_EVIDENCE, f"MISSING FILE {rel}: receipts name it but the checkout has none")
    blob = base_blob(real_root, base_sha, rel)
    replay = _DestinationReplay(rel, blob)
    base_counts = section_counts(replay.sections)
    for entry in batches:
        replay.apply_batch(entry)
    with open(path, "rb") as fh:
        current = fh.read()
    return {"rel": rel, "path": path, "replay": replay, "data": replay.finish(), "current": current,
            "base_sha256": None if blob is None else _sha256(blob), "base_counts": base_counts}


def _file_report(plan, will_write):
    data = plan["data"]
    return {
        "destination": plan["rel"], "base_sha256": plan["base_sha256"],
        "result_sha256": None if data is None else _sha256(data),
        "current_sha256": _sha256(plan["current"]), "up_to_date": data == plan["current"],
        "written": will_write and data != plan["current"],
        "counts": {"base": plan["base_counts"], "result": section_counts(plan["replay"].sections)}}


def _plan_refusals(plans):
    return [r for plan in plans for r in plan["replay"].refusals]


def _plan_mappings(plans):
    return [m for plan in plans for m in plan["replay"].mappings]


def _write_plans(plans):
    for plan in plans:
        if plan["data"] != plan["current"]:
            harness_merge.locked_update(plan["path"], lambda _current, data=plan["data"]: data)


def replay_feature(root, feature, base, check_only):
    """Rebuild every touched file from the main blob and replay the PR's active batches.
    All-or-nothing: any refusal leaves every file byte-identical. `check_only` never writes."""
    real_root = os.path.realpath(root)
    base_sha = resolve_base(real_root, base)
    entries, active, manifest = load_active(real_root, feature, base_sha)
    _check_coverage(real_root, base_sha, entries)
    plans = [_plan_destination(real_root, base_sha, rel, batches)
             for rel, batches in _by_destination(active).items()]
    refusals = _plan_refusals(plans)
    will_write = not refusals and not check_only
    files = [_file_report(plan, will_write) for plan in plans]
    if will_write:
        _write_plans(plans)
    return {"replayed": not refusals, "check": check_only, "base": base_sha, "receipts": manifest,
            "batches": [e["id"] for e in ordered(active)], "files": files, "refusals": refusals,
            "mappings": _plan_mappings(plans)}


# ---- member-ops ------------------------------------------------------------------------------

def _require_text(value, what):
    if not (isinstance(value, str) and value and "\x00" not in value):
        _refuse(9, f"REFUSED {what} must be a non-empty string")


def _caller(feature, persona, runtime_id, parent_id):
    _require_text(runtime_id, "runtime id")
    _require_text(parent_id, "parent id")
    return {"persona": persona, "feature": feature, "runtime_id": runtime_id, "parent_id": parent_id}


def _supersedes_refs(supersedes, base):
    refs = sorted(set(supersedes))
    for ref in refs:
        if not (isinstance(ref, str) and HEX64_RE.match(ref)):
            _refuse(12, f"MALFORMED SUPERSEDES {ref!r} is not a batch identity")
    if refs and base is None:
        _refuse(12, "MALFORMED SUPERSEDES a replacement needs --base, the explicit main sha it reconstructs from")
    return refs


def _decode_ops(text, replacing):
    ops = _decode_json(text, "OPS")
    if not isinstance(ops, list):
        _refuse(12, "MALFORMED OPS payload is not a list; pass the expertise_update list itself")
    if not ops and not replacing:
        _refuse(12, "MALFORMED OPS member-ops needs at least one op unless it supersedes an earlier batch")
    for index, op in enumerate(ops):
        _parse_op(op, index)  # shape errors refuse before any lock is taken
    return ops


def _own_receipt(path, caller):
    """The caller's existing receipt, validated and bound to this exact identity, else None."""
    if not os.path.exists(path):
        return None
    raw, _ = read_receipt_file(path, caller["feature"])
    if any(raw[key] != caller[key] for key in HEADER_KEYS):
        _refuse(EXIT_EVIDENCE, f"IDENTITY MISMATCH runtime {caller['runtime_id']} already has a receipt "
                               "for a different persona or parent")
    return raw


def _supersession_context(real_root, caller, rel, refs, base, own, receipt):
    """(base sha, active entries with the referenced batches omitted) for a replacement; the
    references are validated against this PR's receipts BEFORE anything is written."""
    if not refs:
        return None, None
    base_sha = resolve_base(real_root, base)
    entries, _, _ = load_active(real_root, caller["feature"], base_sha)
    stub = dict(caller, id="pending", seq=len(own["batches"]) + 1 if own else 1, destination=rel, supersedes=refs,
                receipt=os.path.relpath(receipt, real_root), ops=[], originals=[], recorded_at_ns=0)
    validated = active_entries(entries + [stub])
    return base_sha, [e for e in validated if e is not stub]


def _reconstruct(real_root, base_sha, rel, active):
    """The destination as the main base plus every other active batch; refuses if that replay does."""
    replay = _DestinationReplay(rel, base_blob(real_root, base_sha, rel))
    for entry in [e for e in ordered(active) if e["destination"] == rel]:
        replay.apply_batch(entry)
    if replay.refusals:
        _refuse(EXIT_REPLAY, *[f"RECONSTRUCTION REFUSED {r['section']} {r['target']}: {r['reason']}" for r in replay.refusals])
    return replay.title, replay.sections, replay.order, replay.headers


def _original_entries(sections, ops):
    return [{"section": op["section"], "target": op["target"],
             "original": dict(sections.get(op["section"], [])).get(op["target"])} for op in ops]


def _land_target(dest, rel, ops, reconstruct):
    """Compute and persist the target under harness_merge's lock; returns what the receipt records."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    landed = {}

    def transform(current):
        title, sections, order, headers = reconstruct() if reconstruct else parse_state(current, rel)
        merged, new_order, outcomes = resolve_ops(sections, order, ops)
        data = render_state(title, merged, new_order, headers)
        check_candidate(rel, data)
        landed.update(
            outcomes=outcomes, originals=_original_entries(sections, ops),
            before_sha256=None if current is None else _sha256(current), after_sha256=_sha256(data),
            counts={"before": section_counts(sections), "after": section_counts(merged)})
        return data

    harness_merge.locked_update(dest, transform)
    return landed


def _build_batch(caller, seq, rel, ops, landed, refs):
    batch = {"seq": seq, "destination": rel, "ops": ops, "originals": landed["originals"],
             "before_sha256": landed["before_sha256"], "after_sha256": landed["after_sha256"],
             "supersedes": list(refs), "recorded_at_ns": time.time_ns()}
    batch["id"] = batch_identity(caller, batch)
    return batch


def _persist_batch(receipt, caller, rel, ops, landed, refs):
    """Append the batch to the caller's receipt through the same locked atomic replace."""
    appended = {}

    def transform(current):
        doc = ({"schema": RECEIPT_SCHEMA, "batches": [], **caller} if current is None
               else parse_receipt(os.path.basename(receipt), current, caller["feature"]))
        batch = _build_batch(caller, len(doc["batches"]) + 1, rel, ops, landed, refs)
        doc["batches"].append(batch)
        appended["batch"] = batch
        return (json.dumps(doc, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")

    try:
        os.makedirs(os.path.dirname(receipt), exist_ok=True)
        harness_merge.locked_update(receipt, transform)
    except OSError as exc:
        _refuse(EXIT_EVIDENCE, f"RECEIPT PERSISTENCE FAILED for {rel}: {exc}",
                "the target file was written; with no receipt, verification and replay fail closed")
    return appended["batch"]


def _confirm_agreement(dest, receipt, caller, batch):
    """Success is published only once the persisted receipt and the file agree."""
    doc, _ = read_receipt_file(receipt, caller["feature"])
    recorded = [b for b in doc["batches"] if b["id"] == batch["id"]]
    with open(dest, "rb") as fh:
        file_sha = _sha256(fh.read())
    if not recorded or recorded[0]["after_sha256"] != file_sha or batch_identity(doc, recorded[0]) != batch["id"]:
        _refuse(EXIT_EVIDENCE, f"RECEIPT/FILE MISMATCH batch={batch['id']}: the receipt and {batch['destination']} disagree")


def _locate(root, feature, persona, runtime_id, tier, segment):
    """(real root, destination rel, destination path, receipt path) for the host-bound caller."""
    real_root = os.path.realpath(root)
    rel = destination_rel(persona, tier, segment)
    dest = resolve_destination(real_root, rel)
    return real_root, rel, dest, receipt_location(feature_directory(real_root, feature), runtime_id)


def _reconstructor(refs, real_root, base_sha, rel, active):
    """None for an ordinary write; for a replacement, the callable that rebuilds the target."""
    return (lambda: _reconstruct(real_root, base_sha, rel, active)) if refs else None


def _member_report(real_root, caller, rel, receipt, refs, batch, landed):
    return {"applied": True, "persona": caller["persona"], "feature": caller["feature"],
            "runtime_id": caller["runtime_id"], "destination": rel, "batch": batch["id"],
            "supersedes": refs, "receipt": os.path.relpath(receipt, real_root),
            "outcomes": landed["outcomes"], "counts": landed["counts"],
            "before_sha256": landed["before_sha256"], "after_sha256": landed["after_sha256"]}


def member_ops(root, feature, persona, runtime_id, parent_id, tier, segment, ops_text, supersedes=(), base=None):
    """Apply the persona's ordinary ops to its own file beneath the feature checkout and record
    the batch. Returns the JSON-ready result; raises MergeRefusal for every refusal."""
    caller = _caller(feature, persona, runtime_id, parent_id)
    refs = _supersedes_refs(supersedes, base)
    ops = _decode_ops(ops_text, bool(refs))
    real_root, rel, dest, receipt = _locate(root, feature, persona, runtime_id, tier, segment)
    own = _own_receipt(receipt, caller)
    base_sha, active = _supersession_context(real_root, caller, rel, refs, base, own, receipt)
    reconstruct = _reconstructor(refs, real_root, base_sha, rel, active)
    landed = _land_target(dest, rel, ops, reconstruct)
    batch = _persist_batch(receipt, caller, rel, ops, landed, refs)
    _confirm_agreement(dest, receipt, caller, batch)
    return _member_report(real_root, caller, rel, receipt, refs, batch, landed)


# ---- read-only verification ------------------------------------------------------------------

def _effect_mismatches(batches, sections):
    """[((section, id), expected, actual)] where the file disagrees with the FINAL effect of the
    ordered batches: a superseded intermediate need not survive, only what the sequence leaves."""
    expected = {}
    for batch in batches:
        for op in batch["ops"]:
            expected[(op["section"], op["target"])] = None if op["op"] == "drop" else op["entry"]
    actual = {(name, eid): text for name, entries in sections.items() for eid, text in entries}
    return [(key, want, actual.get(key)) for key, want in expected.items() if actual.get(key) != want]


def _claimed_ops(claimed, persona):
    """Strip the item-level persona (kept outside the core op shape); every item must carry the caller's."""
    if not isinstance(claimed, list):
        _refuse(EXIT_EVIDENCE, "CLAIM is not a list of expertise_update items")
    for item in claimed:
        if not (isinstance(item, dict) and item.get("persona") == persona):
            _refuse(EXIT_EVIDENCE, f"CLAIM item {item!r} does not carry persona {persona}")
    return [{k: v for k, v in item.items() if k != "persona"} for item in claimed]


def _match_claimed(mine, claimed_ops):
    """The recorded ops the member did NOT report; refuses on any claimed op no active batch recorded."""
    remaining = [op for batch in mine for op in batch["ops"]]
    for claimed in claimed_ops:
        try:
            remaining.remove(claimed)
        except ValueError:
            _refuse(EXIT_EVIDENCE, f"NOT RECORDED claimed op {json.dumps(claimed, sort_keys=True)} "
                                   "is not an exact op of this runtime's active batches for this destination")
    return remaining


def _check_caller_identity(own, caller):
    if not own:
        _refuse(EXIT_EVIDENCE, f"MISSING RECEIPT no receipt batch for runtime {caller['runtime_id']} in this PR")
    for entry in own:
        if any(entry[key] != caller[key] for key in HEADER_KEYS):
            _refuse(EXIT_EVIDENCE, f"IDENTITY MISMATCH receipt belongs to persona {entry['persona']}, "
                                   f"parent {entry['parent_id']}, not the caller")


def _require_files(real_root, receipt, dest, rel):
    if not os.path.isfile(receipt):
        _refuse(EXIT_EVIDENCE, f"MISSING RECEIPT {os.path.relpath(receipt, real_root)}")
    if not os.path.isfile(dest):
        _refuse(EXIT_EVIDENCE, f"MISSING FILE {rel}")


def _recorded_batches(real_root, feature, caller, rel, base):
    """The caller's active batches for `rel`, in sequence, after the receipt identity is bound."""
    entries, active, _ = load_active(real_root, feature, resolve_base(real_root, base) if base else None)
    runtime_id = caller["runtime_id"]
    _check_caller_identity([e for e in entries if e["runtime_id"] == runtime_id], caller)
    return sorted((e for e in active if e["runtime_id"] == runtime_id and e["destination"] == rel),
                  key=lambda e: e["seq"])


def _read_destination(dest, rel):
    with open(dest, "rb") as fh:
        data = fh.read()
    _, sections, _, _ = parse_state(data, rel)
    return data, sections


def _refuse_mismatches(batches, sections):
    mismatches = _effect_mismatches(batches, sections)
    if mismatches:
        _refuse(EXIT_EVIDENCE, *[f"MISMATCH {s} {i}: receipt says {want!r}, file holds {got!r}"
                                 for (s, i), want, got in mismatches])


def _preserved_adds(batches):
    """[section, id] of every add whose identical entry already stood in the file."""
    return [[op["section"], op["target"]] for e in batches for op, rec in zip(e["ops"], e["originals"])
            if op["op"] == "add" and rec["original"] == op["entry"]]


def verify_receipt(root, feature, persona, runtime_id, parent_id, tier, segment, claimed, base=None):
    """READ-ONLY. Match persona, feature, runtime ids, exact ops and destination against the
    ordered active batches, then compare the file with their final effect. Never applies."""
    caller = _caller(feature, persona, runtime_id, parent_id)
    real_root, rel, dest, receipt = _locate(root, feature, persona, runtime_id, tier, segment)
    _require_files(real_root, receipt, dest, rel)
    mine = _recorded_batches(real_root, feature, caller, rel, base)
    unreported = _match_claimed(mine, _claimed_ops(claimed, persona))
    data, sections = _read_destination(dest, rel)
    _refuse_mismatches(mine, sections)
    return {"verified": True, "persona": persona, "feature": feature, "runtime_id": runtime_id,
            "destination": rel, "batches": [e["id"] for e in mine], "preserved": _preserved_adds(mine),
            "unreported": unreported, "counts": section_counts(sections), "file_sha256": _sha256(data)}


def _add_apply_parser(sub):
    p_apply = sub.add_parser("apply", help="union-merge a proposal into an Expertise file")
    p_apply.add_argument("--file", required=True, help="path to the Expertise markdown file")
    p_apply.add_argument(
        "--entries", required=True, help="path to the proposed entries, or - for stdin"
    )
    p_apply.set_defaults(func=cmd_apply)


def _add_ops_parser(sub):
    p_ops = sub.add_parser("ops", help="apply add/replace/drop ops to an Expertise file")
    p_ops.add_argument("--file", required=True, help="path to the Expertise markdown file")
    p_ops.add_argument(
        "--ops",
        required=True,
        help="path to a JSON list of add/replace/drop ops, or - for stdin",
    )
    p_ops.set_defaults(func=cmd_ops)


def _add_member_parser(sub):
    p_member = sub.add_parser("member-ops", help="apply ops to a persona's own file and record a receipt")
    _add_identity_arguments(p_member)
    p_member.add_argument("--ops", required=True, help="path to a JSON list of ordinary ops, or - for stdin")
    p_member.add_argument("--supersedes", action="append", help="batch identity this replacement retires")
    p_member.add_argument("--base", help="main commit sha; required with --supersedes")
    p_member.set_defaults(func=cmd_member_ops)


def _add_verify_parser(sub):
    p_verify = sub.add_parser("verify-receipt", help="read-only: check a member's claimed ops against its receipt")
    _add_identity_arguments(p_verify)
    p_verify.add_argument("--claimed", required=True, help="path to the expertise_update list, or - for stdin")
    p_verify.add_argument("--base", help="main commit sha; limits receipts to this PR's")
    p_verify.set_defaults(func=cmd_verify_receipt)


def _add_replay_parser(sub):
    p_replay = sub.add_parser("replay", help="replay this PR's receipts onto the main base")
    p_replay.add_argument("--root", required=True)
    p_replay.add_argument("--feature", required=True)
    p_replay.add_argument("--base", required=True, help="the main commit sha to rebuild from")
    p_replay.add_argument("--check", action="store_true", help="read-only: report, write nothing")
    p_replay.set_defaults(func=cmd_replay)


def main():
    parser = argparse.ArgumentParser(prog="expertise-merge.py")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for add_parser in (_add_apply_parser, _add_ops_parser, _add_member_parser,
                       _add_verify_parser, _add_replay_parser):
        add_parser(sub)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
