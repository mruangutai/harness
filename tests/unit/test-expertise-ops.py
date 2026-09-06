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


def main():
    case_u1()
    case_u2()
    case_u3()
    case_u5()
    case_u6()
    case_u7()
    case_u8()
    case_u9()
    case_u10()
    case_u11()
    case_u12()
    case_u13()
    case_u14()
    case_u15()
    case_u16()
    case_u17()
    case_u18()
    case_u19()
    case_u20()
    case_u21()
    case_u22()

    fails = 0
    for name, ok, detail in RESULTS:
        if ok:
            print(f"PASS  {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n      | {detail}")

    summary = "FAIL test-expertise-ops.py" if fails else "PASS test-expertise-ops.py"
    print(summary)
    return fails


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
