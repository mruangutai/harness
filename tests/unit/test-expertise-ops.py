#!/usr/bin/env python3
"""Unit tests for expertise-merge.py's resolve_ops (BUG-1308 T-01, D-01..D-10).

Loads .claude/skills/harness/bin/expertise-merge.py by file path — the filename is hyphenated,
so it cannot be imported as a normal module — and exercises resolve_ops(base_sections,
base_order, ops) directly: a PURE function, no IO, no sys.exit, no CLI subprocess. Writes
nothing under the bin directory.
"""
import copy
import importlib.util
import os
import sys

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
MODULE_PATH = os.environ.get("EXPERTISE_MERGE_BIN") or os.path.join(BIN_DIR, "expertise-merge.py")

_spec = importlib.util.spec_from_file_location("expertise_merge_ops_under_test", MODULE_PATH)
expertise_merge = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(expertise_merge)

resolve_ops = expertise_merge.resolve_ops
compute_union = expertise_merge.compute_union
MergeRefusal = expertise_merge.harness_merge.MergeRefusal


# Derived from Python's own `str.splitlines()` — the exact alphabet `parse_expertise` uses to
# count physical lines — rather than a hand-copied literal list, so this constant tracks the
# parser instead of a snapshot of it (SEC-01/F1, fix cycle 2). Probes the C0/C1 control range
# plus the two Unicode line/paragraph separators; anything Python treats as a line boundary
# lands here.
LINE_BREAKING_CHARS = tuple(
    chr(c) for c in list(range(0x00, 0xA0)) + [0x2028, 0x2029]
    if len(("a" + chr(c) + "b").splitlines()) > 1
)


RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))


def base_sections(sections):
    """sections: [(name, [(id, text), ...]), ...] -> (base_sections dict, base_order list)."""
    secs = {name: list(entries) for name, entries in sections}
    order = [name for name, _ in sections]
    return secs, order


def op(verb, section, target, entry=None, **extra):
    d = {"op": verb, "target": target, "section": section}
    if entry is not None:
        d["entry"] = entry
    d.update(extra)
    return d


def case_u1():
    entries = [(f"P-{n:02d}", f"text-{n:02d}") for n in range(1, 16)]
    secs, order = base_sections([("Patterns", entries)])
    merged, _, _ = resolve_ops(secs, order, [op("replace", "Patterns", "P-07", "NEW TEXT")])
    patterns = merged["Patterns"]
    check("u1: merged Patterns still has 15 entries", len(patterns) == 15, patterns)
    check("u1: index 6 carries new text", patterns[6] == ("P-07", "NEW TEXT"), patterns[6])
    others_ok = all(patterns[i] == entries[i] for i in range(15) if i != 6)
    check("u1: every other id untouched at its own index", others_ok, patterns)


def case_u2():
    g_entries = [(f"G-{n:02d}", f"gtext-{n}") for n in range(1, 6)]
    secs, order = base_sections([("Gotchas", g_entries)])
    merged, _, _ = resolve_ops(secs, order, [op("drop", "Gotchas", "G-03")])
    ids = [eid for eid, _ in merged["Gotchas"]]
    check("u2: G-03 absent", "G-03" not in ids, ids)
    others_present = all(g[0] in ids for g in g_entries if g[0] != "G-03")
    check("u2: every other id present", others_present, ids)
    check("u2: section length one smaller", len(merged["Gotchas"]) == len(g_entries) - 1, ids)


def case_u3():
    secs, order = base_sections([("Patterns", [("P-01", "one")])])
    try:
        resolve_ops(secs, order, [op("replace", "Patterns", "P-99", "x")])
        check("u3: MergeRefusal raised", False, "no exception raised")
    except MergeRefusal as e:
        check("u3: code is 10", e.code == 10, e.code)
        check("u3: line starts MISSING TARGET", e.lines[0].startswith("MISSING TARGET"), e.lines)


def case_u5():
    secs, order = base_sections([("Patterns", [("P-04", "a"), ("P-04", "b")])])
    try:
        resolve_ops(secs, order, [op("replace", "Patterns", "P-04", "c")])
        check("u5: MergeRefusal raised", False, "no exception raised")
    except MergeRefusal as e:
        check("u5: code is 11", e.code == 11, e.code)


def case_u6():
    secs, order = base_sections([("Patterns", [("P-01", "one"), ("P-02", "two")])])
    ops = [op("replace", "Patterns", "P-01", "x"), op("drop", "Patterns", "P-01")]
    try:
        resolve_ops(secs, order, ops)
        check("u6: MergeRefusal raised", False, "no exception raised")
    except MergeRefusal as e:
        check("u6: code is 11", e.code == 11, e.code)


def case_u7():
    secs, order = base_sections([("Patterns", [("P-01", "one"), ("P-02", "two")])])
    try:
        resolve_ops(secs, order, [op("merge", "Patterns", "P-01")])
        check("u7: MergeRefusal raised", False, "no exception raised")
    except MergeRefusal as e:
        check("u7: code is 12", e.code == 12, e.code)
        expected = "replace on the surviving id plus a drop of the absorbed id"
        check("u7: line names the replace plus drop rewrite", expected in e.lines[0], e.lines)


def case_u8():
    entries = [(f"P-{n:02d}", f"text-{n:02d}") for n in range(1, 16)]
    secs, order = base_sections([("Patterns", entries)])
    ops = [op("drop", "Patterns", "P-01"), op("add", "Patterns", "P-16", "sixteen")]
    merged, _, _ = resolve_ops(secs, order, ops)
    check("u8: succeeds with final length 15", len(merged["Patterns"]) == 15, merged["Patterns"])


def case_u9():
    entries = [(f"P-{n:02d}", f"text-{n:02d}") for n in range(1, 16)]
    secs, order = base_sections([("Patterns", entries)])
    try:
        resolve_ops(secs, order, [op("add", "Patterns", "P-16", "sixteen")])
        check("u9: MergeRefusal raised", False, "no exception raised")
    except MergeRefusal as e:
        check("u9: code is 8", e.code == 8, e.code)
        check("u9: line starts CAP EXCEEDED", e.lines[0].startswith("CAP EXCEEDED"), e.lines)


def case_u10():
    """THE PERMANENT RED CASE. Pins compute_union's inability to replace as a forever contract:
    feeding it u1's exact base and replacement text must still return a non-empty conflicts
    list and leave the old text in place. Reverting resolve_ops to the union path reddens this."""
    entries = [(f"P-{n:02d}", f"text-{n:02d}") for n in range(1, 16)]
    secs, order = base_sections([("Patterns", entries)])
    prop_secs = {"Patterns": [("P-07", "NEW TEXT")]}
    prop_order = ["Patterns"]
    merged, _, conflicts = compute_union(secs, order, prop_secs, prop_order)
    check("u10: compute_union returns non-empty conflicts", len(conflicts) > 0, conflicts)
    check(
        "u10: merged Patterns still carries OLD text at index 6",
        merged["Patterns"][6] == ("P-07", "text-07"),
        merged["Patterns"][6],
    )


def case_u11():
    """MULTI-OP SAME SECTION, low-index drop with a higher-index replace, run both orders.
    This is the ONLY place Step D's order-independence is asserted — never trimmed."""
    entries = [("P-01", "a"), ("P-02", "b"), ("P-03", "c"), ("P-04", "d"), ("P-05", "e")]
    marker = "MARKER TEXT"
    variants = (
        ("forward", [op("drop", "Patterns", "P-01"), op("replace", "Patterns", "P-05", marker)]),
        ("reversed", [op("replace", "Patterns", "P-05", marker), op("drop", "Patterns", "P-01")]),
    )
    results = {}
    for label, ops in variants:
        secs, order = base_sections([("Patterns", list(entries))])
        merged, _, _ = resolve_ops(secs, order, ops)
        results[label] = merged["Patterns"]
        ids = [eid for eid, _ in merged["Patterns"]]
        check(
            f"u11: {label} order id sequence is [P-02,P-03,P-04,P-05]",
            ids == ["P-02", "P-03", "P-04", "P-05"],
            ids,
        )
        p05_text = dict(merged["Patterns"])["P-05"]
        check(f"u11: {label} order P-05 carries marker text", p05_text == marker, p05_text)
        no_other_marker = all(t != marker for eid, t in merged["Patterns"] if eid != "P-05")
        check(f"u11: {label} order no other entry carries the marker", no_other_marker, merged["Patterns"])
    check(
        "u11: forward and reversed order produce identical merged Patterns",
        results["forward"] == results["reversed"],
        results,
    )


def case_u12():
    """TWO DROPS AT DISTINCT ORIGINAL INDICES IN ONE SECTION."""
    entries = [("P-01", "a"), ("P-02", "b"), ("P-03", "c"), ("P-04", "d"), ("P-05", "e")]
    secs, order = base_sections([("Patterns", list(entries))])
    ops = [op("drop", "Patterns", "P-01"), op("drop", "Patterns", "P-04")]
    merged, _, _ = resolve_ops(secs, order, ops)
    ids = [eid for eid, _ in merged["Patterns"]]
    check("u12: merged Patterns id sequence is [P-02,P-03,P-05]", ids == ["P-02", "P-03", "P-05"], ids)
    check("u12: length is 3", len(ids) == 3, ids)


def case_u13():
    """MISSING SECTION IS A SHAPE REFUSAL, on every verb, plus an empty-string section."""
    secs, order = base_sections(
        [("Patterns", [("P-01", "a"), ("P-02", "b"), ("P-03", "c")]), ("Gotchas", [("G-01", "g")])]
    )
    baseline = copy.deepcopy(secs)
    bad_ops = [
        ("add no section", {"op": "add", "target": "P-99", "entry": "x"}),
        ("replace no section", {"op": "replace", "target": "P-01", "entry": "x"}),
        ("drop no section", {"op": "drop", "target": "P-01"}),
        ("replace empty section", {"op": "replace", "target": "P-01", "section": "", "entry": "x"}),
    ]
    for label, bad_op in bad_ops:
        try:
            resolve_ops(secs, order, [bad_op])
            check(f"u13: {label} raises MergeRefusal", False, "no exception raised")
        except MergeRefusal as e:
            check(f"u13: {label} code is 12", e.code == 12, e.code)
            check(f"u13: {label} line starts MALFORMED OPS", e.lines[0].startswith("MALFORMED OPS"), e.lines)
            check(f"u13: {label} line names section", "section" in e.lines[0], e.lines)
            check(f"u13: {label} line names the op's index", "index=0" in e.lines[0], e.lines)
    check("u13: base mapping unchanged after shape refusals", secs == baseline, secs)


def case_u14():
    """A PAYLOAD THAT IS NOT A LIST — a DIGEST-shaped mapping, and a bare string."""
    secs, order = base_sections([("Patterns", [("P-01", "a")])])
    valid_replace = op("replace", "Patterns", "P-01", "b")
    payloads = [
        ("digest mapping", {"expertise_update": [valid_replace]}),
        ("bare string", "not a list"),
    ]
    for label, payload in payloads:
        try:
            resolve_ops(secs, order, payload)
            check(f"u14: {label} raises MergeRefusal", False, "no exception raised")
        except MergeRefusal as e:
            check(f"u14: {label} code is 12", e.code == 12, e.code)
            check(f"u14: {label} line starts MALFORMED OPS", e.lines[0].startswith("MALFORMED OPS"), e.lines)
            check(f"u14: {label} line names expertise_update", "expertise_update" in e.lines[0], e.lines)


def case_u15():
    """A SECTION REDUCED TO EMPTY BY DROPS survives as an empty section, still in order."""
    secs, order = base_sections(
        [("Gotchas", [("G-01", "g1"), ("G-02", "g2")]), ("Patterns", [("P-01", "p1")])]
    )
    ops = [op("drop", "Gotchas", "G-01"), op("drop", "Gotchas", "G-02")]
    merged, out_order, _ = resolve_ops(secs, order, ops)
    check("u15: merged mapping still carries the key Gotchas", "Gotchas" in merged, list(merged))
    check("u15: Gotchas has zero entries", len(merged["Gotchas"]) == 0, merged["Gotchas"])
    check(
        "u15: Gotchas still in order at its original position",
        out_order.index("Gotchas") == order.index("Gotchas"),
        out_order,
    )
    check("u15: Patterns untouched", merged["Patterns"] == [("P-01", "p1")], merged["Patterns"])


def case_u16():
    """AN OP NAMING THE ONLY ENTRY IN A SECTION — (a) replace, (b) drop."""
    marker = "MARKER"
    secs_a, order_a = base_sections([("Open", [("O-01", "orig")])])
    merged_a, _, _ = resolve_ops(secs_a, order_a, [op("replace", "Open", "O-01", marker)])
    check("u16: (a) replace leaves Open at length 1", len(merged_a["Open"]) == 1, merged_a["Open"])
    check("u16: (a) replace Open carries the marker", merged_a["Open"][0] == ("O-01", marker), merged_a["Open"])

    secs_b, order_b = base_sections([("Open", [("O-01", "orig")])])
    merged_b, _, _ = resolve_ops(secs_b, order_b, [op("drop", "Open", "O-01")])
    check("u16: (b) drop leaves Open at length 0", len(merged_b["Open"]) == 0, merged_b["Open"])
    check("u16: (b) drop leaves Open still present", "Open" in merged_b, list(merged_b))


def _assert_malformed(secs, order, ops_payload, label):
    """Shared MALFORMED OPS(12) shape assertion: raises, code 12, line starts MALFORMED OPS.
    Guards against a non-MergeRefusal exception (e.g. an uncaught TypeError, VL-02's pre-fix
    crash) escaping and silently aborting every later case in the suite."""
    try:
        resolve_ops(secs, order, ops_payload)
        check(f"{label}: raises MergeRefusal", False, "no exception raised")
    except MergeRefusal as e:
        check(f"{label}: code is 12", e.code == 12, e.code)
        check(f"{label}: line starts MALFORMED OPS", e.lines[0].startswith("MALFORMED OPS"), e.lines)
    except Exception as e:
        check(f"{label}: raises MergeRefusal, not {type(e).__name__}", False, repr(e))


def case_u17():
    """AN ENTRY EMBEDDING ANY splitlines() LINE-BOUNDARY CHARACTER IS A MALFORMED-OPS SHAPE
    REFUSAL (VL-01/SEC-01), not a value `render` ever writes verbatim into a rendered file.
    `replace` keeps the base's own entry count unchanged, matching the exact shape the exploit
    needs. Separators are LINE_BREAKING_CHARS, derived from `str.splitlines()` itself, not a
    hardcoded `\n`/`\r` pair — so this case cannot silently fall behind the parser it guards."""
    for sep in LINE_BREAKING_CHARS:
        secs, order = base_sections([("Patterns", [("P-01", "one")])])
        entry = f"harmless{sep}## Gotchas (max 15)"
        _assert_malformed(secs, order, [op("replace", "Patterns", "P-01", entry)], f"u17: U+{ord(sep):04X} entry")


def case_u18():
    """A TARGET EMBEDDING ANY splitlines() LINE-BOUNDARY CHARACTER IS THE SAME MALFORMED-OPS
    SHAPE REFUSAL (VL-01/SEC-01) an entry gets — target is written verbatim into a replace/drop
    refusal's stdout and, on add, into the rendered file. Separators are LINE_BREAKING_CHARS,
    derived from `str.splitlines()` itself."""
    for sep in LINE_BREAKING_CHARS:
        secs, order = base_sections([("Patterns", [("P-01", "one")])])
        forged_target = f"P-99{sep}- P-77: forged"
        _assert_malformed(secs, order, [op("add", "Patterns", forged_target, "harmless")], f"u18: U+{ord(sep):04X} target")


def case_u19():
    """A NON-STRING TARGET IS A MALFORMED-OPS SHAPE REFUSAL (VL-02), not an uncaught TypeError
    escaping the file's documented exit contract."""
    secs, order = base_sections([("Patterns", [("P-01", "one")])])
    _assert_malformed(secs, order, [op("add", "Patterns", ["P-50", "x"], "x")], "u19")


def case_u20():
    """ADD AGAINST A DUPLICATED BASE ID IS AMBIGUOUS (VL-03, D-03(a)), exactly like
    replace/drop on the identical base — never silently PRESERVED or wrongly CONFLICT."""
    duplicated = [("P-01", "one"), ("P-07", "four-a"), ("P-07", "four-b")]
    variants = (
        ("a", "third totally different text"),  # used to be CONFLICT, exit 7
        ("b", "four-b"),  # matches the surviving occurrence — used to be PRESERVED, exit 0
    )
    for label, entry in variants:
        secs, order = base_sections([("Patterns", list(duplicated))])
        try:
            resolve_ops(secs, order, [op("add", "Patterns", "P-07", entry)])
            check(f"u20: ({label}) MergeRefusal raised", False, "no exception raised")
        except MergeRefusal as e:
            check(f"u20: ({label}) code is 11", e.code == 11, e.code)


def case_u21():
    """A TARGET ENTRY_RE WOULD NOT PARSE BACK OUT UNCHANGED IS THE SAME MALFORMED-OPS SHAPE
    REFUSAL (VL-06). `_validate_target_grammar` round-trips `target` through `ENTRY_RE` via the
    exact synthetic line `render` would produce, catching two distinct exploits the panel
    measured: a too-long id `ENTRY_RE` cannot match at all (invisible on the very next
    re-parse), and a target embedding a shorter valid id that `ENTRY_RE` DOES match, capturing
    only the embedded id (forging a colliding, corrupted duplicate). Checked for every verb,
    not just `add` — the Step-A gate this lives in runs before verb-specific resolution."""
    secs, order = base_sections([("Patterns", [("P-01", "one")])])
    _assert_malformed(secs, order, [op("add", "Patterns", "PPPP-1", "x")], "u21: add too-long id")
    _assert_malformed(
        secs, order, [op("add", "Patterns", "P-01: fake prefix", "x")], "u21: add embeds valid id"
    )
    _assert_malformed(secs, order, [op("replace", "Patterns", "PPPP-1", "x")], "u21: replace too-long id")
    _assert_malformed(secs, order, [op("drop", "Patterns", "PPPP-1")], "u21: drop too-long id")


def case_u22():
    """A WELL-FORMED TARGET STILL SUCCEEDS (positive control) — VL-06's grammar check accepts
    every id ENTRY_RE actually recognizes, so it cannot be passing by rejecting everything."""
    secs, order = base_sections([("Patterns", [("P-01", "one")])])
    merged, _, outcomes = resolve_ops(secs, order, [op("add", "Patterns", "P-02", "two")])
    check("u22: well-formed add succeeds", ("ADDED", "P-02") in outcomes, outcomes)
    check("u22: entry present in merged", ("P-02", "two") in merged["Patterns"], merged["Patterns"])


def case_u23():
    """A PROPOSAL NAMING THE SAME id TWICE IN ONE SECTION IS AMBIGUOUS ON THE PROPOSAL ALONE
    (BUG-276): the first entry must not silently win over the second, regardless of base state.
    """
    # (a) different texts
    secs, order = base_sections([("Patterns", [("P-01", "one")])])
    prop_secs = {"Patterns": [("P-02", "ALPHA"), ("P-02", "BRAVO")]}
    prop_order = ["Patterns"]
    try:
        compute_union(secs, order, prop_secs, prop_order)
        check("u23a: MergeRefusal raised", False, "no exception raised")
    except MergeRefusal as e:
        check("u23a: different texts refuse with code 11", e.code == 11, e.code)
        check("u23a: line starts AMBIGUOUS TARGET", e.lines[0].startswith("AMBIGUOUS TARGET"), e.lines)
        check(
            "u23a: line carries section, id and reason tokens",
            "section=Patterns" in e.lines[0] and "id=P-02" in e.lines[0] and "reason=" in e.lines[0],
            e.lines,
        )

    # (b) identical texts
    secs, order = base_sections([("Patterns", [("P-01", "one")])])
    prop_secs = {"Patterns": [("P-02", "ALPHA"), ("P-02", "ALPHA")]}
    prop_order = ["Patterns"]
    try:
        compute_union(secs, order, prop_secs, prop_order)
        check("u23b: MergeRefusal raised", False, "no exception raised")
    except MergeRefusal as e:
        check("u23b: identical texts refuse with code 11", e.code == 11, e.code)
        check("u23b: line starts AMBIGUOUS TARGET", e.lines[0].startswith("AMBIGUOUS TARGET"), e.lines)
        check(
            "u23b: line carries section, id and reason tokens",
            "section=Patterns" in e.lines[0] and "id=P-02" in e.lines[0] and "reason=" in e.lines[0],
            e.lines,
        )

    # (c) no base
    secs, order = {}, []
    prop_secs = {"Patterns": [("P-02", "ALPHA"), ("P-02", "BRAVO")]}
    prop_order = ["Patterns"]
    try:
        compute_union(secs, order, prop_secs, prop_order)
        check("u23c: MergeRefusal raised", False, "no exception raised")
    except MergeRefusal as e:
        check("u23c: no base refuses with code 11", e.code == 11, e.code)
        check("u23c: line starts AMBIGUOUS TARGET", e.lines[0].startswith("AMBIGUOUS TARGET"), e.lines)
        check(
            "u23c: line carries section, id and reason tokens",
            "section=Patterns" in e.lines[0] and "id=P-02" in e.lines[0] and "reason=" in e.lines[0],
            e.lines,
        )


# ---------------------------------------------------------------------------------------------
# FEAT-2225 T-01: member-ops destination, receipts, supersession and replay engine. These cases
# are RED against the pre-change tool (every name below is new) and each one is paired with a
# one-mechanism mutant in the T-01 receipt.
# ---------------------------------------------------------------------------------------------
import contextlib
import json
import shutil
import tempfile

PERSONA = "harness-backend-dev"
CRAFT_REL = f".harness/expertise/{PERSONA}.md"
REPO_REL = f".harness/harness/expertise/{PERSONA}.md"


def replay_entry(runtime, ops, originals, seq=1, ident=None, persona=PERSONA, destination=CRAFT_REL,
                 supersedes=(), receipt=None, ts=0):
    """A plain-dict batch entry shaped like what load_active hands the replay engine."""
    return {
        "id": ident or f"{runtime}-{seq}", "seq": seq, "destination": destination, "ops": ops,
        "originals": [{"section": o["section"], "target": o["target"], "original": t}
                      for o, t in zip(ops, originals)],
        "persona": persona, "feature": "FEAT-1", "runtime_id": runtime, "parent_id": "p",
        "receipt": receipt or f"notes/{runtime}.json", "supersedes": list(supersedes),
        "recorded_at_ns": ts, "before_sha256": None, "after_sha256": "0" * 64,
    }


def replay_blob(sections):
    lines = [f"# Expertise — {PERSONA}"]
    for name, entries in sections:
        lines.append(f"## {name}")
        lines.extend(f"- {eid}: {text}" for eid, text in entries)
    return ("\n".join(lines) + "\n").encode("utf-8")


def case_u30_free_ids():
    free = expertise_merge._next_free_id
    check("u30: first gap is chosen", free("P", ["P-01", "P-03"]) == "P-02", free("P", ["P-01", "P-03"]))
    check("u30: past the end", free("P", ["P-01", "P-02"]) == "P-03", None)
    check("u30: empty section starts at 01", free("P", []) == "P-01", None)
    check("u30: other prefixes do not occupy ids", free("G", ["P-01"]) == "G-01", None)
    check("u30: numeric not textual comparison", free("P", ["P-1", "P-2"]) == "P-03", free("P", ["P-1", "P-2"]))
    wide = [f"P-{n:02d}" for n in range(1, 100)]
    check("u30: width grows past 99", free("P", wide) == "P-100", free("P", wide))


def case_u31_destination_rel():
    rel = expertise_merge.destination_rel
    check("u31: craft path", rel(PERSONA, "craft", None) == CRAFT_REL, rel(PERSONA, "craft", None))
    check("u31: repository path", rel(PERSONA, "repository", "harness") == REPO_REL, None)
    bad = [(PERSONA, "craft", "harness"), (PERSONA, "repository", None), (PERSONA, "repository", ".."),
           (PERSONA, "repository", "a/b"), (PERSONA, "repository", "expertise"), ("reviewer", "craft", None),
           ("harness-../x", "craft", None), (PERSONA, "global", None)]
    for args in bad:
        try:
            rel(*args)
            check(f"u31: {args} refused", False, "no refusal")
        except MergeRefusal as e:
            check(f"u31: {args} refused with 9", e.code == 9, e.code)


def apply_entries(blob, entries):
    replay = expertise_merge._DestinationReplay(CRAFT_REL, blob)
    for entry in entries:
        replay.apply_batch(entry)
    return replay


def case_u32_collision_remap():
    blob = replay_blob([("Patterns", [("P-01", "a"), ("P-03", "c")])])
    first = replay_entry("r1", [op("add", "Patterns", "P-03", "mine")], [None], seq=1)
    later = replay_entry("r1", [op("replace", "Patterns", "P-03", "mine two")], ["mine"], seq=2)
    replay = apply_entries(blob, [first, later])
    pats = dict(replay.sections["Patterns"])
    check("u32: refusals empty", replay.refusals == [], replay.refusals)
    check("u32: foreign P-03 kept", pats.get("P-03") == "c", pats)
    check("u32: first free id P-02 received the add, then the remapped replace", pats.get("P-02") == "mine two", pats)
    want = [{"runtime_id": "r1", "section": "Patterns", "original_id": "P-03", "replayed_id": "P-02", "batch": "r1-1",
             "persona": PERSONA, "destination": CRAFT_REL}]
    check("u32: mapping exact", replay.mappings == want, replay.mappings)
    # reserved ids: another add in the same batch already names P-02, so the remap must skip it
    both = replay_entry("r2", [op("add", "Patterns", "P-03", "x"), op("add", "Patterns", "P-02", "y")], [None, None])
    pats2 = dict(apply_entries(blob, [both]).sections["Patterns"])
    check("u32: reserved P-02 not reused, first free after it is P-04", pats2.get("P-04") == "x" and pats2.get("P-02") == "y", pats2)


def case_u33_identical_add_preserved():
    blob = replay_blob([("Patterns", [("P-01", "a")])])
    replay = apply_entries(blob, [replay_entry("r1", [op("add", "Patterns", "P-01", "a")], [None])])
    check("u33: identical add keeps one entry", replay.sections["Patterns"] == [("P-01", "a")], replay.sections["Patterns"])
    check("u33: no mapping for preserved add", replay.mappings == [] and replay.refusals == [], (replay.mappings, replay.refusals))


def refusal_reason(blob, entries):
    refusals = apply_entries(blob, entries).refusals
    return refusals[0]["reason"] if refusals else None


def u34_fixtures():
    changed = replay_blob([("Patterns", [("P-01", "changed upstream")])])
    gone = replay_blob([("Patterns", [("P-02", "other")])])
    ready = replay_blob([("Patterns", [("P-01", "orig")])])
    done = replay_blob([("Patterns", [("P-01", "new")])])
    rep = replay_entry("r1", [op("replace", "Patterns", "P-01", "new")], ["orig"])
    drp = replay_entry("r1", [op("drop", "Patterns", "P-01")], ["orig"])
    return changed, gone, ready, done, rep, drp


def case_u34_refusals():
    changed, gone, _, _, rep, drp = u34_fixtures()
    check("u34: replace over changed entry refuses CHANGED", (refusal_reason(changed, [rep]) or "").startswith("CHANGED"), refusal_reason(changed, [rep]))
    check("u34: replace of vanished entry refuses DISAPPEARED", (refusal_reason(gone, [rep]) or "").startswith("DISAPPEARED"), refusal_reason(gone, [rep]))
    check("u34: drop over changed entry refuses CHANGED", (refusal_reason(changed, [drp]) or "").startswith("CHANGED"), None)
    check("u34: drop of vanished entry refuses DISAPPEARED", (refusal_reason(gone, [drp]) or "").startswith("DISAPPEARED"), None)


def case_u34_applies():
    _, _, ready, done, rep, drp = u34_fixtures()
    check("u34: replace when original matches applies", apply_entries(ready, [rep]).sections["Patterns"] == [("P-01", "new")], None)
    idem = apply_entries(done, [rep])
    check("u34: already-applied replace is idempotent", idem.refusals == [] and idem.sections["Patterns"] == [("P-01", "new")], idem.refusals)
    check("u34: drop when original matches applies", apply_entries(ready, [drp]).sections["Patterns"] == [], None)


def case_u34_refused_batch_report():
    changed, _, _, _, rep, _ = u34_fixtures()
    refused = apply_entries(changed, [rep])
    check("u34: refused batch leaves state unchanged", refused.sections["Patterns"] == [("P-01", "changed upstream")], None)
    r = refused.refusals[0]
    for key, want in (("persona", PERSONA), ("runtimes", ["r1"]), ("destination", CRAFT_REL), ("section", "Patterns"),
                      ("target", "P-01"), ("batches", ["r1-1"])):
        check(f"u34: refusal names {key}", r.get(key) == want, r)


def case_u35_independent_callers():
    blob = replay_blob([("Patterns", [("P-01", "orig"), ("P-02", "two")])])
    a = replay_entry("r1", [op("replace", "Patterns", "P-01", "new")], ["orig"], ts=1)
    b = replay_entry("r2", [op("replace", "Patterns", "P-01", "new")], ["orig"], ts=2)
    reason = refusal_reason(blob, [a, b])
    check("u35: identical independent replace is refused, not hidden by idempotence",
          (reason or "").startswith("INDEPENDENT") and "r1" in reason and "r2" in reason, reason)
    c = replay_entry("r2", [op("drop", "Patterns", "P-01")], ["orig"], ts=2)
    check("u35: replace then drop by another caller refused", (refusal_reason(blob, [a, c]) or "").startswith("INDEPENDENT"), None)
    again = replay_entry("r1", [op("replace", "Patterns", "P-01", "newer")], ["new"], seq=2, ts=3)
    check("u35: the SAME caller may chain edits of one entry",
          apply_entries(blob, [a, again]).sections["Patterns"][0] == ("P-01", "newer"), None)


def case_u36_caps_deferred():
    secs, order = base_sections([("Open", [(f"Q-{n:02d}", "t") for n in range(1, 6)])])
    try:
        resolve_ops(secs, order, [op("add", "Open", "Q-06", "t")])
        check("u36: default still enforces the cap", False, "no refusal")
    except MergeRefusal as e:
        check("u36: default cap refusal is 8", e.code == 8, e.code)
    merged, _, _ = resolve_ops(secs, order, [op("add", "Open", "Q-06", "t")], enforce_caps=False)
    check("u36: enforce_caps=False defers the cap", len(merged["Open"]) == 6, len(merged["Open"]))


def graph_reason(entries):
    try:
        active = expertise_merge.active_entries(entries)
        return None, [e["id"] for e in active]
    except MergeRefusal as e:
        return e, None


def u38_chain():
    a = replay_entry("r1", [], [], ident="A", receipt="n/r1")
    b = replay_entry("r2", [], [], ident="B", supersedes=["A"], receipt="n/r2")
    return a, b


def u38_refused_graphs(a, b):
    return {
        "missing": [replay_entry("r2", [], [], ident="B", supersedes=["Z"])],
        "cross-persona": [a, replay_entry("r2", [], [], ident="B", supersedes=["A"], persona="harness-other")],
        "cross-destination": [a, replay_entry("r2", [], [], ident="B", supersedes=["A"], destination=REPO_REL)],
        "not-earlier": [replay_entry("r1", [], [], ident="A", seq=2, receipt="n/r1"),
                        replay_entry("r1", [], [], ident="B", seq=1, supersedes=["A"], receipt="n/r1")],
        "self": [replay_entry("r1", [], [], ident="A", supersedes=["A"])],
        "ambiguous": [a, b, replay_entry("r3", [], [], ident="C", supersedes=["A"], receipt="n/r3")],
        "cycle": [replay_entry("r1", [], [], ident="A", supersedes=["B"], receipt="n/r1"),
                  replay_entry("r2", [], [], ident="B", supersedes=["A"], receipt="n/r2")],
    }


def case_u38_retirement():
    a, b = u38_chain()
    err, active = graph_reason([a, b])
    check("u38: replacement retires the referenced batch", err is None and active == ["B"], (err, active))
    c = replay_entry("r3", [], [], ident="C", supersedes=["B"], receipt="n/r3")
    err, active = graph_reason([a, b, c])
    check("u38: chains retire step by step", err is None and active == ["C"], (err, active))


def case_u38_refused_graphs():
    cases = u38_refused_graphs(*u38_chain())
    for name, entries in cases.items():
        err, _ = graph_reason(entries)
        check(f"u38: {name} supersession refused with 15", err is not None and err.code == 15, err)
    err, _ = graph_reason(cases["cycle"])
    check("u38: cycle is named CYCLIC", err is not None and "CYCLIC" in err.lines[0], err)
    err, _ = graph_reason(cases["ambiguous"])
    check("u38: double supersession is named AMBIGUOUS", err is not None and "AMBIGUOUS" in err.lines[0], err)


def case_u39_batch_identity():
    header = {"persona": PERSONA, "feature": "FEAT-1", "runtime_id": "r1", "parent_id": "p"}
    batch = {"seq": 1, "destination": CRAFT_REL, "ops": [op("add", "Patterns", "P-01", "a")],
             "originals": [{"section": "Patterns", "target": "P-01", "original": None}],
             "before_sha256": None, "after_sha256": "1" * 64, "supersedes": []}
    ident = expertise_merge.batch_identity(header, batch)
    check("u39: identity is a sha256 hex digest", len(ident) == 64 and set(ident) <= set("0123456789abcdef"), ident)
    check("u39: identity ignores the timestamp", expertise_merge.batch_identity(header, dict(batch, recorded_at_ns=5)) == ident, None)
    mutations = {"seq": 2, "destination": "x", "ops": [], "after_sha256": "2" * 64, "supersedes": ["f" * 64],
                 "before_sha256": "3" * 64, "originals": []}
    for key, value in mutations.items():
        check(f"u39: identity covers {key}", expertise_merge.batch_identity(header, dict(batch, **{key: value})) != ident, None)
    for key in header:
        changed = dict(header, **{key: "other"})
        check(f"u39: identity covers {key}", expertise_merge.batch_identity(changed, batch) != ident, None)


@contextlib.contextmanager
def failed_receipt_tree():
    """A feature checkout where member_ops landed its target and then failed at the receipt write:
    yields (tmp, features, the refusal member_ops raised, or None when it raised nothing)."""
    tmp = tempfile.mkdtemp(prefix="member-ops-unit-")
    real = expertise_merge.harness_merge.locked_update

    def failing(path, transform, timeout=None):
        if path.endswith(".json"):
            raise OSError("disk full")
        return real(path, transform, timeout)

    try:
        features = os.path.join(tmp, ".harness", "harness", "features", "FEAT-1")
        os.makedirs(features)
        expertise_merge.harness_merge.locked_update = failing
        try:
            expertise_merge.member_ops(tmp, "FEAT-1", PERSONA, "r1", "p", "craft", None,
                                       json.dumps([op("add", "Patterns", "P-01", "text")]))
            refusal = None
        except MergeRefusal as e:
            refusal = e
        finally:
            expertise_merge.harness_merge.locked_update = real
        yield tmp, features, refusal
    finally:
        expertise_merge.harness_merge.locked_update = real
        shutil.rmtree(tmp, ignore_errors=True)


def case_u40_receipt_failure_fails_call():
    with failed_receipt_tree() as (tmp, features, refusal):
        if refusal is None:
            check("u40: receipt failure fails the call", False, "no refusal")
        else:
            check("u40: receipt failure is refusal 15", refusal.code == 15, refusal)
        target = os.path.join(tmp, CRAFT_REL)
        written = open(target, encoding="utf-8").read() if os.path.exists(target) else ""
        check("u40: target was persisted before the receipt step", "P-01: text" in written, written)
        notes = os.path.join(features, "notes")
        receipts = [n for n in os.listdir(notes) if n.endswith(".json")] if os.path.isdir(notes) else []
        check("u40: no receipt exists, so verification must fail closed", receipts == [], receipts)


def case_u40_verify_without_receipt():
    with failed_receipt_tree() as (tmp, _features, _refusal):
        try:
            expertise_merge.verify_receipt(tmp, "FEAT-1", PERSONA, "r1", "p", "craft", None,
                                           [dict(op("add", "Patterns", "P-01", "text"), persona=PERSONA)])
            check("u40: verify refuses without receipt", False, "verified")
        except MergeRefusal as e:
            check("u40: verify without receipt is 15", e.code == 15, e)


def case_u41_effect_mismatches():
    sections = {"Patterns": [("P-01", "v2")]}
    batches = [
        {"ops": [op("add", "Patterns", "P-01", "v1")]},
        {"ops": [op("replace", "Patterns", "P-01", "v2"), op("add", "Patterns", "P-02", "kept")]},
    ]
    miss = expertise_merge._effect_mismatches(batches, sections)
    check("u41: final effect of ordered batches, superseded intermediate not required",
          [m[0] for m in miss] == [("Patterns", "P-02")], miss)
    gone = expertise_merge._effect_mismatches([{"ops": [op("drop", "Patterns", "P-01")]}], sections)
    check("u41: drop expects absence", [m[0] for m in gone] == [("Patterns", "P-01")], gone)
    ok = expertise_merge._effect_mismatches([{"ops": [op("drop", "Patterns", "P-09")]}], sections)
    check("u41: drop of absent id is satisfied", ok == [], ok)


def case_u42_receipt_file_agreement():
    """Success is published only once receipt and file agree: a target that changes between its
    own persist and the receipt landing (a stand-in for any disagreement) fails the call."""
    tmp = tempfile.mkdtemp(prefix="member-ops-unit-")
    real = expertise_merge.harness_merge.locked_update
    target = os.path.join(tmp, CRAFT_REL)

    def disagreeing(path, transform, timeout=None):
        real(path, transform, timeout)
        if path.endswith(".json"):
            with open(target, "a", encoding="utf-8") as fh:
                fh.write("- P-99: written behind the receipt's back\n")

    try:
        os.makedirs(os.path.join(tmp, ".harness", "harness", "features", "FEAT-1"))
        expertise_merge.harness_merge.locked_update = disagreeing
        try:
            expertise_merge.member_ops(tmp, "FEAT-1", PERSONA, "r1", "p", "craft", None,
                                       json.dumps([op("add", "Patterns", "P-01", "text")]))
            check("u42: receipt/file disagreement refuses the call", False, "published success")
        except MergeRefusal as e:
            check("u42: disagreement is refusal 15 naming the mismatch", e.code == 15 and "MISMATCH" in e.lines[0], e)
    finally:
        expertise_merge.harness_merge.locked_update = real
        shutil.rmtree(tmp, ignore_errors=True)


def run_guarded(fn):
    try:
        fn()
    except Exception as exc:  # a mutant or the pre-change tool must read as FAIL, never crash the suite
        check(f"{fn.__name__}: completed without raising", False, repr(exc))


LEGACY_CASES = (case_u1, case_u2, case_u3, case_u5, case_u6, case_u7, case_u8, case_u9, case_u10,
                case_u11, case_u12, case_u13, case_u14, case_u15, case_u16, case_u17, case_u18,
                case_u19, case_u20, case_u21, case_u22, case_u23)
GUARDED_CASES = (case_u30_free_ids, case_u31_destination_rel, case_u32_collision_remap,
                 case_u33_identical_add_preserved, case_u34_refusals, case_u34_applies,
                 case_u34_refused_batch_report, case_u35_independent_callers, case_u36_caps_deferred,
                 case_u38_retirement, case_u38_refused_graphs, case_u39_batch_identity,
                 case_u40_receipt_failure_fails_call, case_u40_verify_without_receipt,
                 case_u41_effect_mismatches, case_u42_receipt_file_agreement)


def print_results():
    fails = 0
    for name, ok, detail in RESULTS:
        if ok:
            print(f"PASS  {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n      | {detail}")
    return fails


def main():
    for case in LEGACY_CASES:
        case()
    for case in GUARDED_CASES:
        run_guarded(case)

    fails = print_results()
    summary = "FAIL test-expertise-ops.py" if fails else "PASS test-expertise-ops.py"
    print(summary)
    return fails


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
