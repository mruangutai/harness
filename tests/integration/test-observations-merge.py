#!/usr/bin/env python3
"""Tests for observations-merge.py's `apply` subcommand (FEAT-32 T-04, D-05).

Every case runs the CLI as a SUBPROCESS against a fixture observations log inside a fresh
tempfile.mkdtemp(), nested under a .harness/harness/features/FEAT-99-fixture/observations/
path so harness_merge.require_destination accepts it. Resolves the binary the same way
test-plan-merge.py and test-expertise-merge.py resolve their own, so a mutated copy of the
source under test can be swapped in without editing this file:

    CLI = os.environ.get("OBSERVATIONS_MERGE_BIN") or os.path.join(HERE, "observations-merge.py")

Case 1 is deliberately never routed through the CLI: it reproduces #606's naive whole-file
write directly, so it stays red proof of the loss regardless of what this tool does.

D-05: an observations log has no entry ids to key on. There is no conflict exit (no exit 7) and
no cap (no exit 8) for this file class — case 5 exists precisely to catch a copy of
expertise-merge.py's conflict logic being pasted in here.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import os
import subprocess
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
HERE = BIN_DIR
CLI = os.environ.get("OBSERVATIONS_MERGE_BIN") or os.path.join(HERE, "observations-merge.py")

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------

BULLET_A = "- 2026-08-18: bullet A, the first record.\n"
BULLET_B = "- 2026-08-18: bullet B, the second record.\n"
BULLET_C = "- 2026-08-18: bullet C, the third record.\n"

TITLE = "# Observations — harness-pm — FEAT-99\n"


def fixture_root(prefix="observations-merge-test-"):
    """A fresh tempfile.mkdtemp(), with a nested
    .harness/harness/features/FEAT-99-fixture/observations/ directory so require_destination
    accepts a log written inside it."""
    root = tempfile.mkdtemp(prefix=prefix)
    d = os.path.join(root, ".harness", "harness", "features", "FEAT-99-fixture", "observations")
    os.makedirs(d, exist_ok=True)
    return root, os.path.join(d, "harness-pm.md")


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return text


def run_apply(file_path, entries_path):
    return subprocess.run(
        [sys.executable, CLI, "apply", "--file", file_path, "--entries", entries_path],
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------------------
# Cases
# ---------------------------------------------------------------------------


def case_naive_last_writer_wins():
    """Case 1 — THE RED CASE, permanent, never routed through the tool. Reproduces #606
    directly: a plain whole-file write holding A and B, then a plain whole-file write holding A
    and C. B is lost."""
    _root, path = fixture_root()
    write(path, TITLE + "\n" + BULLET_A + BULLET_B)
    write(path, TITLE + "\n" + BULLET_A + BULLET_C)
    content = open(path, encoding="utf-8").read()
    check("case1: naive whole-file write loses bullet B", BULLET_B not in content, content)


def case_green_union():
    """Case 2 — GREEN: the same two appends through the tool leave A, B and C all present, one
    assertion per bullet, with A first and base order of A and B unchanged."""
    _root, path = fixture_root()
    write(path, TITLE + "\n" + BULLET_A + BULLET_B)

    entries = os.path.join(_root, "entries.md")
    write(entries, BULLET_A + BULLET_C)

    r = run_apply(path, entries)
    check("case2: apply exits 0", r.returncode == 0, r.stdout + r.stderr)

    content = open(path, encoding="utf-8").read()
    check("case2: bullet A present", BULLET_A in content, content)
    check("case2: bullet B present", BULLET_B in content, content)
    check("case2: bullet C present", BULLET_C in content, content)
    idx_a = content.find(BULLET_A)
    idx_b = content.find(BULLET_B)
    check(
        "case2: A appears before B, and both remain in base order",
        idx_a != -1 and idx_b != -1 and idx_a < idx_b,
        content,
    )


def case_dedup():
    """Case 3 — DEDUP: applying an entries file whose only record is byte identical to a base
    record leaves the file with exactly one copy of it."""
    _root, path = fixture_root()
    write(path, TITLE + "\n" + BULLET_A + BULLET_B)

    entries = os.path.join(_root, "entries.md")
    write(entries, BULLET_A)

    r = run_apply(path, entries)
    check("case3: apply exits 0", r.returncode == 0, r.stdout + r.stderr)

    content = open(path, encoding="utf-8").read()
    first_line = BULLET_A.splitlines()[0]
    occurrences = content.count(first_line)
    check("case3: exactly one copy of the byte-identical record", occurrences == 1, content)


def case_dedup_normalised():
    """Case 4 — DEDUP IS ON NORMALISED TEXT: a record differing from a base record only in line
    wrapping and trailing spaces is treated as the same record and not duplicated. Also proves
    the real-file blank-line case (D-05): a record differing only in the number of trailing
    blank lines it carries dedups the same way."""
    _root, path = fixture_root()
    base_record = "- 2026-08-18: bullet with a   wrap and trailing spaces here.   \n  second line.\n"
    write(path, TITLE + "\n" + base_record)

    wrapped_record = "- 2026-08-18: bullet with a\nwrap and trailing spaces here.\n  second line.\n"
    entries = os.path.join(_root, "entries.md")
    write(entries, wrapped_record)

    r = run_apply(path, entries)
    check("case4: apply exits 0", r.returncode == 0, r.stdout + r.stderr)
    content = open(path, encoding="utf-8").read()
    first_line = "- 2026-08-18: bullet with a"
    check(
        "case4: normalised-identical record (wrapping/trailing-space) not duplicated",
        content.count(first_line) == 1,
        content,
    )

    # The real-file shape: same record text, differing only in trailing blank line count.
    _root2, path2 = fixture_root(prefix="observations-merge-test-c4b-")
    record_no_blank = "- 2026-08-18: a record with no trailing blank line.\n"
    write(path2, TITLE + "\n" + record_no_blank)
    record_with_blanks = "- 2026-08-18: a record with no trailing blank line.\n\n\n"
    entries2 = os.path.join(_root2, "entries.md")
    write(entries2, record_with_blanks)

    r2 = run_apply(path2, entries2)
    check("case4b: apply exits 0", r2.returncode == 0, r2.stdout + r2.stderr)
    content2 = open(path2, encoding="utf-8").read()
    check(
        "case4b: record differing only in trailing blank-line count dedups as one copy",
        content2.count("a record with no trailing blank line.") == 1,
        content2,
    )


def case_two_different_kept():
    """Case 5 — TWO DIFFERENT RECORDS ARE BOTH KEPT, no conflict, exit 0. This is the case that
    would break if expertise-merge.py's exit 7 conflict logic were copied here: D-05 defines
    no conflict exit for this file class."""
    _root, path = fixture_root()
    write(path, TITLE + "\n" + BULLET_A)

    entries = os.path.join(_root, "entries.md")
    write(entries, BULLET_B)

    r = run_apply(path, entries)
    check("case5: two different records both kept, exit 0 (no conflict exit exists)", r.returncode == 0, r.stdout + r.stderr)
    content = open(path, encoding="utf-8").read()
    check("case5: bullet A present", BULLET_A in content, content)
    check("case5: bullet B present", BULLET_B in content, content)


def case_multiline_records():
    """Case 6 — MULTI-LINE RECORDS: a base record with two indented continuation lines survives
    with those lines attached to it and in order, asserted on the exact text."""
    _root, path = fixture_root()
    multiline = (
        "- 2026-08-18: a record whose first line is short.\n"
        "  continuation line one, indented two spaces.\n"
        "  continuation line two, indented two spaces.\n"
    )
    write(path, TITLE + "\n" + multiline)

    entries = os.path.join(_root, "entries.md")
    write(entries, BULLET_B)

    r = run_apply(path, entries)
    check("case6: apply exits 0", r.returncode == 0, r.stdout + r.stderr)
    content = open(path, encoding="utf-8").read()
    check("case6: the exact multi-line record text survives", multiline in content, content)


def case_concurrency_real(trials=20):
    """Case 7 — CONCURRENCY FOR REAL, 20 trials, two subprocesses appending distinct records.
    Exactly two outcomes are admitted; a third is reported by trial, never absorbed into the
    assertion."""
    third_outcome_details = []
    locked_count = 0
    for i in range(trials):
        root, path = fixture_root(prefix=f"observations-merge-test-c7-{i}-")
        write(path, TITLE + "\n" + BULLET_A)

        record_x = f"- 2026-08-18: trial {i} record X.\n"
        record_y = f"- 2026-08-18: trial {i} record Y.\n"
        entries_x = os.path.join(root, "x.md")
        write(entries_x, record_x)
        entries_y = os.path.join(root, "y.md")
        write(entries_y, record_y)

        px = subprocess.Popen(
            [sys.executable, CLI, "apply", "--file", path, "--entries", entries_x],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        py = subprocess.Popen(
            [sys.executable, CLI, "apply", "--file", path, "--entries", entries_y],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        out_x, err_x = px.communicate(timeout=30)
        out_y, err_y = py.communicate(timeout=30)
        rc_x, rc_y = px.returncode, py.returncode

        content = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
        ok = False
        outcome = "other"

        if rc_x == 0 and rc_y == 0:
            outcome = "union"
            ok = (
                BULLET_A in content
                and record_x in content
                and record_y in content
            )
        elif sorted([rc_x, rc_y]) == [0, 6]:
            outcome = "locked"
            locked_count += 1
            if rc_x == 6:
                lock_out, lost, won = out_x + err_x, record_x, record_y
            else:
                lock_out, lost, won = out_y + err_y, record_y, record_x
            ok = (
                "LOCKED" in lock_out
                and lost not in content
                and won in content
                and BULLET_A in content
            )

        if not ok:
            third_outcome_details.append(
                f"trial {i}: outcome={outcome} rc_x={rc_x} rc_y={rc_y} "
                f"out_x={out_x!r} out_y={out_y!r} content={content!r}"
            )

    check(
        f"case7: {trials} concurrent trials admit only the union outcome or the lock outcome",
        not third_outcome_details,
        "\n".join(third_outcome_details),
    )
    check(
        f"case7: informational — the exit-6 lock branch was taken in {locked_count}/{trials} trials",
        True,
        "",
    )


def case_create_from_entries():
    """Case 8 — a log that does not exist yet is created from the entries alone, with a
    generated title, exit 0."""
    _root, path = fixture_root(prefix="observations-merge-test-c8-")
    check("case8: base file does not exist before apply", not os.path.exists(path), path)

    entries = os.path.join(_root, "entries.md")
    write(entries, BULLET_A)

    r = run_apply(path, entries)
    check("case8: create exits 0", r.returncode == 0, r.stdout + r.stderr)
    check("case8: the file now exists", os.path.exists(path), path)
    content = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
    check("case8: bullet A present", BULLET_A in content, content)
    check(
        "case8: a generated title line beginning with a hash is present",
        content.splitlines()[0].startswith("#") if content.splitlines() else False,
        content,
    )


def case_destination_refusal():
    """Case 9 — DESTINATION REFUSAL, both directions: a source path exits 9 untouched, a
    dot-dot escape wearing a legal tail exits 9, an Expertise file path exits 9, and a
    legitimate observations path exits 0.

    The dot-dot direction cannot be built from `..` alone: a pure `..` path ends in whatever
    follows the `..`, so it is merely a second non-matching path. A SYMLINK is what gives a
    literal argument that ENDS in the matching tail while RESOLVING somewhere the tail does
    not match.
    """
    root = tempfile.mkdtemp(prefix="observations-merge-test-c9-")
    entries = os.path.join(root, "entries.md")
    write(entries, BULLET_A)

    # REFUSE: a source path.
    src = os.path.join(root, "src", "main.py")
    os.makedirs(os.path.dirname(src), exist_ok=True)
    write(src, "real code\n")
    r = run_apply(src, entries)
    check("case9: a source path is REFUSED with exit 9", r.returncode == 9, r.stdout + r.stderr)
    check(
        "case9: ...and the refused file is untouched",
        open(src, encoding="utf-8").read() == "real code\n",
        "the tool wrote to a path it said it refused",
    )

    # REFUSE: a symlinked path segment wearing a legal tail. The literal argument must end in
    # the FULL matching tail — including the "observations" segment OBSERVATIONS_TAIL requires
    # — while the RESOLVED path does not, because FEAT-99-fixture is a symlink to somewhere
    # with no features/ ancestry at all. A symlink placed one segment short of "observations"
    # (as a naive port of plan-merge.py's fixture would do) never matches the tail under EITHER
    # interpretation, so it fails to discriminate the resolved-vs-argument mutant — the symlink
    # target itself must carry the observations/harness-pm.md structure beneath it.
    outside = os.path.join(root, "outside-real-target")
    os.makedirs(os.path.join(outside, "observations"), exist_ok=True)
    outside_log = os.path.join(outside, "observations", "harness-pm.md")
    outside_original = write(outside_log, TITLE + "\n" + BULLET_A)

    obs_dir = os.path.join(root, "escape", ".harness", "harness", "features")
    os.makedirs(obs_dir, exist_ok=True)
    symlink_path = os.path.join(obs_dir, "FEAT-99-fixture")
    os.symlink(outside, symlink_path)
    literal_path = os.path.join(symlink_path, "observations", "harness-pm.md")
    check(
        "case9: the escape's literal argument ends in the full legal-looking tail",
        literal_path.endswith(
            os.path.join("features", "FEAT-99-fixture", "observations", "harness-pm.md")
        ),
        literal_path,
    )

    r_escape = run_apply(literal_path, entries)
    check(
        "case9: a symlink escape whose LITERAL argument looks legal but RESOLVES elsewhere is "
        "REFUSED with exit 9",
        r_escape.returncode == 9,
        r_escape.stdout + r_escape.stderr,
    )
    check(
        "case9: ...and the file behind the symlink is untouched",
        open(outside_log, encoding="utf-8").read() == outside_original,
        "the tool wrote through the symlink it said it refused",
    )

    # REFUSE: an Expertise file path — it belongs to a different tool.
    expertise_dir = os.path.join(root, ".harness", "expertise")
    os.makedirs(expertise_dir, exist_ok=True)
    expertise_path = os.path.join(expertise_dir, "harness-pm.md")
    expertise_original = write(expertise_path, "# Expertise — harness-pm\n## Patterns (max 15)\n")
    r_expertise = run_apply(expertise_path, entries)
    check(
        "case9: an Expertise file path is REFUSED with exit 9 — it belongs to a different tool",
        r_expertise.returncode == 9,
        r_expertise.stdout + r_expertise.stderr,
    )
    check(
        "case9: ...and the Expertise file is untouched",
        open(expertise_path, encoding="utf-8").read() == expertise_original,
        "the tool wrote to an Expertise file it said it refused",
    )

    # ALLOW: a legitimate observations path.
    _legit_root, legit_path = fixture_root(prefix="observations-merge-test-c9-legit-")
    r_legit = run_apply(legit_path, entries)
    check(
        "case9: a legitimate observations path is ALLOWED — exit 0",
        r_legit.returncode == 0,
        r_legit.stdout + r_legit.stderr,
    )


def main():
    case_naive_last_writer_wins()
    case_green_union()
    case_dedup()
    case_dedup_normalised()
    case_two_different_kept()
    case_multiline_records()
    case_concurrency_real()
    case_create_from_entries()
    case_destination_refusal()

    fails = 0
    for name, ok, detail in RESULTS:
        if ok:
            print(f"PASS  {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n      | {detail}")

    summary = "FAIL test-observations-merge.py" if fails else "PASS test-observations-merge.py"
    print(summary)
    return fails


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
