#!/usr/bin/env python3
"""Tests for expertise-merge.py's `apply` subcommand (FEAT-30 T-06, D-05, DEC-95).

Every case runs the CLI as a SUBPROCESS against a fixture file in a fresh tempfile.mkdtemp() —
never a real `.harness/expertise/*.md` or `.harness/*/expertise/*.md` file. Resolves the binary
the same way test-feature-worktree.py resolves its own, so a copy of the source under test can be
swapped in without editing this file:

    CLI = os.environ.get("EXPERTISE_MERGE_BIN") or os.path.join(HERE, "expertise-merge.py")

Case 1 is deliberately never routed through the CLI: it reproduces today's naive whole-file
write directly, so it stays red proof of the DEC-95 loss regardless of what this tool does.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import ast
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
HERE = BIN_DIR
CLI = os.environ.get("EXPERTISE_MERGE_BIN") or os.path.join(HERE, "expertise-merge.py")
CHECK_EXPERTISE_BIN = os.path.join(HERE, "check-expertise.sh")
sys.path.insert(0, os.path.dirname(os.path.abspath(CLI)))
import harness_merge  # noqa: E402  (local import, after sys.path fix-up)

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))


def write_file(path, sections):
    """Write a starting Expertise file. sections: [(heading, [(id, text), ...]), ...]."""
    base = os.path.basename(path)
    if base.endswith(".md"):
        base = base[:-3]
    lines = [f"# Expertise — {base}"]
    for name, entries in sections:
        lines.append(f"## {name}")
        for eid, text in entries:
            lines.append(f"- {eid}: {text}")
    content = "\n".join(lines) + "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return content


def write_entries(path, sections):
    """Write a proposal entries file — no title line, same section/entry line format."""
    lines = []
    for name, entries in sections:
        lines.append(f"## {name}")
        for eid, text in entries:
            lines.append(f"- {eid}: {text}")
    content = "\n".join(lines) + "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return content


def target(root, stem):
    """An Expertise-TIER path inside `root`, for any fixture handed to `--file`.

    The fixtures used to be flat — `<root>/case2.md` — and the tool now REFUSES a --file
    that is not an Expertise file (exit 9), because `bash-write-guard.sh` is
    allow-by-omission and reached neither its reviewer check nor its domain walk for a
    CLI invocation. The fixture shape was wrong for the rule, not the other way round:
    every assertion below is unchanged.
    """
    d = os.path.join(root, ".harness", "expertise")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "harness-%s.md" % stem)


def run_apply(file_path, entries_path):
    return subprocess.run(
        [sys.executable, CLI, "apply", "--file", file_path, "--entries", entries_path],
        capture_output=True,
        text=True,
    )


def case_naive_last_writer_wins(root):
    """Case 1 — THE RED CASE, permanent. Never through the tool: two plain whole-file writes,
    same shape as today's close-out, prove the DEC-95 loss directly."""
    path = os.path.join(root, "case1.md")
    write_file(path, [("Patterns", [("P-01", "one"), ("P-02", "two")])])
    write_file(path, [("Patterns", [("P-01", "one"), ("P-03", "three")])])
    write_file(path, [("Patterns", [("P-01", "one"), ("P-04", "four")])])
    content = open(path, encoding="utf-8").read()
    check("case1: naive last-writer-wins loses P-02", "P-02" not in content, content)
    check("case1: naive last-writer-wins loses P-03", "P-03" not in content, content)


def case_green_union(root):
    """Case 2 — THE GREEN CASE. Same two close-outs, through the tool this time."""
    path = target(root, "case2")
    write_file(path, [("Patterns", [("P-01", "one"), ("P-02", "two")])])
    entries_a = os.path.join(root, "case2_a.md")
    write_entries(entries_a, [("Patterns", [("P-01", "one"), ("P-03", "three")])])
    entries_b = os.path.join(root, "case2_b.md")
    write_entries(entries_b, [("Patterns", [("P-01", "one"), ("P-04", "four")])])

    r1 = run_apply(path, entries_a)
    check("case2: apply A exits 0", r1.returncode == 0, r1.stdout + r1.stderr)
    r2 = run_apply(path, entries_b)
    check("case2: apply B exits 0", r2.returncode == 0, r2.stdout + r2.stderr)

    content = open(path, encoding="utf-8").read()
    for eid in ("P-01", "P-02", "P-03", "P-04"):
        check(f"case2: {eid} present after both applies", f"- {eid}:" in content, content)

    r3 = subprocess.run([CHECK_EXPERTISE_BIN, path], capture_output=True, text=True)
    check(
        "case2: check-expertise.sh still accepts the merged file",
        r3.returncode == 0,
        r3.stdout + r3.stderr,
    )


def case_concurrency_real(root, trials=20):
    """Case 3 — CONCURRENCY FOR REAL. Two subprocesses race to apply overlapping proposals to
    the same file. Exactly two outcomes are admitted: the union of both proposals survives, or
    one process exited 6 with the lock message and applied nothing. A third outcome in any trial
    is a finding, reported by name — never widened into the assertion."""
    third_outcome_details = []
    for i in range(trials):
        path = target(root, f"case3-{i}")
        write_file(path, [("Patterns", [("P-01", "one")])])
        entries_a = os.path.join(root, f"case3_{i}_a.md")
        write_entries(entries_a, [("Patterns", [("P-01", "one"), ("P-05", "five")])])
        entries_b = os.path.join(root, f"case3_{i}_b.md")
        write_entries(entries_b, [("Patterns", [("P-01", "one"), ("P-06", "six")])])

        pa = subprocess.Popen(
            [sys.executable, CLI, "apply", "--file", path, "--entries", entries_a],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        pb = subprocess.Popen(
            [sys.executable, CLI, "apply", "--file", path, "--entries", entries_b],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        out_a, err_a = pa.communicate(timeout=30)
        out_b, err_b = pb.communicate(timeout=30)
        rc_a, rc_b = pa.returncode, pb.returncode

        content = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
        ok = False
        outcome = "other"

        if rc_a == 0 and rc_b == 0:
            outcome = "union"
            ok = (
                "- P-01:" in content
                and "- P-05:" in content
                and "- P-06:" in content
            )
        elif sorted([rc_a, rc_b]) == [0, 6]:
            outcome = "locked"
            if rc_a == 6:
                lock_stdout, lost_id, won_id = out_a, "P-05", "P-06"
            else:
                lock_stdout, lost_id, won_id = out_b, "P-06", "P-05"
            ok = (
                "LOCKED" in lock_stdout
                and f"- {lost_id}:" not in content
                and f"- {won_id}:" in content
                and "- P-01:" in content
            )

        if not ok:
            third_outcome_details.append(
                f"trial {i}: outcome={outcome} rc_a={rc_a} rc_b={rc_b} "
                f"out_a={out_a!r} out_b={out_b!r} content={content!r}"
            )

    check(
        f"case3: {trials} concurrent trials admit only the union outcome or the lock outcome",
        not third_outcome_details,
        "\n".join(third_outcome_details),
    )


def case_divergent_text(root):
    """Case 4 — DIVERGENT TEXT exits 7, applies nothing, both texts on stdout."""
    path = target(root, "case4")
    original = write_file(path, [("Patterns", [("P-01", "one"), ("P-02", "two")])])
    entries = os.path.join(root, "case4_entries.md")
    write_entries(entries, [("Patterns", [("P-02", "TWO DIFFERENT TEXT")])])

    r = run_apply(path, entries)
    check("case4: divergent text exits 7", r.returncode == 7, r.stdout + r.stderr)
    check("case4: existing text appears in stdout", "two" in r.stdout, r.stdout)
    check("case4: proposed text appears in stdout", "TWO DIFFERENT TEXT" in r.stdout, r.stdout)

    after = open(path, encoding="utf-8").read()
    check("case4: file is byte identical to before", after == original, repr((original, after)))
    entries_noop = os.path.join(root, "case4_entries_noop.md")
    write_entries(entries_noop, [("Patterns", [("P-01", "one")])])
    r2 = run_apply(path, entries_noop)
    check("case4: a following apply still exits 0", r2.returncode == 0, r2.stdout + r2.stderr)


def case_cap_overflow(root):
    """Case 5 — CAP OVERFLOW exits 8, applies nothing, names the section and the cap."""
    path = target(root, "case5")
    fifteen = [(f"P-{i:02d}", f"text {i}") for i in range(1, 16)]
    original = write_file(path, [("Patterns", fifteen)])
    entries = os.path.join(root, "case5_entries.md")
    write_entries(entries, [("Patterns", [("P-16", "text 16")])])

    r = run_apply(path, entries)
    check("case5: cap overflow exits 8", r.returncode == 8, r.stdout + r.stderr)
    check("case5: stdout names the section", "Patterns" in r.stdout, r.stdout)
    check("case5: stdout names the cap", "15" in r.stdout, r.stdout)

    after = open(path, encoding="utf-8").read()
    check("case5: file is byte identical to before", after == original, repr((original, after)))
    entries_noop = os.path.join(root, "case5_entries_noop.md")
    write_entries(entries_noop, [("Patterns", [("P-01", "text 1")])])
    r2 = run_apply(path, entries_noop)
    check("case5: a following apply still exits 0", r2.returncode == 0, r2.stdout + r2.stderr)


def case_new_file(root):
    """Case 6 — a file that does not exist yet is created from the proposal alone, exit 0."""
    path = target(root, "case6")
    entries = os.path.join(root, "case6_entries.md")
    write_entries(entries, [("Patterns", [("P-01", "one")])])

    check("case6: target file absent before apply", not os.path.exists(path))
    r = run_apply(path, entries)
    check("case6: exits 0", r.returncode == 0, r.stdout + r.stderr)
    check("case6: file created", os.path.exists(path))

    content = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
    check("case6: proposed entry present", "- P-01:" in content, content)
    r2 = run_apply(path, entries)
    check("case6: a following apply still exits 0", r2.returncode == 0, r2.stdout + r2.stderr)


def case_cap_drift_detector():
    """Case 8 — the caps this tool enforces and check-expertise.sh's own CAPS mapping must
    agree, read as TEXT from both files rather than restated as a third literal here."""
    tool_src = open(CLI, encoding="utf-8").read()
    checker_src = open(CHECK_EXPERTISE_BIN, encoding="utf-8").read()

    m_tool = re.search(r"CAPS\s*=\s*(\{[^}]*\})", tool_src)
    m_checker = re.search(r"CAPS\s*=\s*(\{[^}]*\})", checker_src)
    check("case8: CAPS mapping found in expertise-merge.py", m_tool is not None, tool_src[:200])
    check(
        "case8: CAPS mapping found in check-expertise.sh",
        m_checker is not None,
        checker_src[:200],
    )
    if not (m_tool and m_checker):
        return

    caps_tool = ast.literal_eval(m_tool.group(1))
    caps_checker = ast.literal_eval(m_checker.group(1))
    for section in ("Patterns", "Gotchas", "Outcomes", "Open"):
        check(
            f"case8: {section} cap agrees between expertise-merge.py and check-expertise.sh",
            caps_tool.get(section) == caps_checker.get(section),
            f"tool={caps_tool.get(section)!r} checker={caps_checker.get(section)!r}",
        )


def case_destination_refusal(root):
    """Case 9 — the tool REFUSES a --file that is not an Expertise file (exit 9).

    THE HOLE THIS CLOSES, reproduced 2026-08-21 before the fix: `bash-write-guard.sh` is
    ALLOW-BY-OMISSION. It scans a command for a write pattern it recognises and, finding
    none, exits 0 at `:617` — BEFORE the reviewer read-only denial at `:628` and before
    the domain walk at `:676`. A `python3 … expertise-merge.py apply --file <anything>`
    command carries no such pattern. Measured: `harness-code-reviewer`, a READ-ONLY
    persona, got exit 0 against `src/main.py` through this tool while `printf x >>
    src/main.py` from the same persona got exit 2. FEAT-30's T-07 then made this
    invocation the INSTRUCTED path for every agent.

    BOTH DIRECTIONS, and the allow half is what makes the refuse half mean something: a
    tool that refused everything would pass the refusals and break every other case here.
    """
    entries = os.path.join(root, "case9_entries.md")
    write_entries(entries, [("Patterns", [("P-01", "one")])])

    # REFUSE: a source path, the shape that motivated the fix.
    src = os.path.join(root, "src", "main.py")
    os.makedirs(os.path.dirname(src), exist_ok=True)
    open(src, "w").write("real code\n")
    r = run_apply(src, entries)
    check("case9: a non-Expertise --file is REFUSED with exit 9",
          r.returncode == 9, f"exit {r.returncode}: {r.stderr.strip()[:200]}")
    check("case9: ...and the refused file is UNTOUCHED",
          open(src, encoding="utf-8").read() == "real code\n",
          "the tool wrote to a path it said it refused")

    # REFUSE: a `..` escape wearing a legal-looking tail. Matched on the REALPATH, so a
    # string check on the given path would pass this and write outside the tier.
    esc = os.path.join(root, ".harness", "expertise", "..", "..", "harness-pm.md")
    r = run_apply(esc, entries)
    check("case9: a `..` escape carrying a legal tail is REFUSED — the match is on the "
          "realpath, not the argument",
          r.returncode == 9, f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # ALLOW: both legal tiers (FEAT-27).
    for label, rel in (("project tier", os.path.join(".harness", "expertise")),
                       ("repository tier", os.path.join(".harness", "kaya", "expertise"))):
        d = os.path.join(root, rel)
        os.makedirs(d, exist_ok=True)
        f = os.path.join(d, "harness-pm.md")
        write_file(f, [("Patterns", [("P-00", "zero")])])
        r = run_apply(f, entries)
        check(f"case9: the {label} is ALLOWED — exit 0",
              r.returncode == 0, f"exit {r.returncode}: {r.stderr.strip()[:200]}")


def case_stale_lock_recovery(root):
    """Case 10 — THE STALE-LOCK RECOVERY, the reason D-02 exists.

    A child holds the lock through harness_merge.acquire and is SIGKILLed while holding it —
    no finally block of its own ever runs. A following apply in the PARENT must still succeed:
    under real flock (D-02) the kernel releases the lock on process death, so this is fast and
    exits 0 with the entry on disk. Under the O_EXCL create-and-delete branch (USE_FLOCK
    mutated to False) the lock FILE outlives the SIGKILLed holder, the apply exits 6 instead,
    and this case is the one that goes red — proving the flock branch is load-bearing, not
    merely present.
    """
    path = target(root, "case10")
    write_file(path, [("Patterns", [("P-01", "one")])])
    entries = os.path.join(root, "case10_entries.md")
    write_entries(entries, [("Patterns", [("P-02", "two")])])

    lock_path = path + ".lock"
    r_fd, w_fd = os.pipe()
    pid = os.fork()
    if pid == 0:
        # Child: acquire the lock through the SAME core the CLI under test uses, signal the
        # parent it holds it, then block forever. No finally block of ours ever runs — we are
        # about to be SIGKILLed, which is the whole point of this case.
        os.close(r_fd)
        try:
            with harness_merge.acquire(lock_path):
                os.write(w_fd, b"x")
                os.close(w_fd)
                while True:
                    time.sleep(3600)
        finally:
            os._exit(0)

    os.close(w_fd)
    os.read(r_fd, 1)  # blocks until the child confirms it holds the lock
    os.close(r_fd)
    os.kill(pid, signal.SIGKILL)
    os.waitpid(pid, 0)

    r = run_apply(path, entries)
    check(
        "case10: a following apply exits 0 after the lock holder is SIGKILLed",
        r.returncode == 0,
        f"exit {r.returncode}: {(r.stdout + r.stderr)!r}",
    )
    content = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
    check(
        "case10: the proposed entry is on disk after recovery",
        "- P-02:" in content,
        content,
    )


def write_ops(path, ops):
    """Write an ops payload — ALWAYS a bare JSON list; the tool accepts no mapping wrapper
    (T-01's settled payload shape). case20(c) is the one exception and writes its own
    digest-shaped mapping directly, never through this helper."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(ops, f)
    return path


def run_ops(file_path, ops_path):
    return subprocess.run(
        [sys.executable, CLI, "ops", "--file", file_path, "--ops", ops_path],
        capture_output=True,
        text=True,
    )


_ENTRY_LINE_RE = re.compile(r"^- ([A-Za-z]{1,3}-\d+): (.*)$")


def parse_section_entries(content, section):
    """A minimal, independent re-implementation of the entry-line shape, section-scoped, so
    assertions about section order and content never depend on the tool's own parser."""
    in_section = False
    out = []
    for line in content.splitlines():
        if line.startswith("## "):
            in_section = line[3:].split(" ")[0] == section
            continue
        if in_section:
            m = _ENTRY_LINE_RE.match(line)
            if m:
                out.append((m.group(1), m.group(2)))
    return out


def case_replace_at_capacity(root):
    """Case 11 — REPLACE AT CAPACITY (D-06, D-07). A replace never changes section length, so
    a section already at its cap accepts a replace."""
    path = target(root, "case11")
    fifteen = [(f"P-{i:02d}", f"text {i}") for i in range(1, 16)]
    write_file(path, [("Patterns", fifteen)])
    ops_path = write_ops(
        os.path.join(root, "case11_ops.json"),
        [{"op": "replace", "target": "P-07", "section": "Patterns", "entry": "REPLACED TEXT SEVEN"}],
    )

    r = run_ops(path, ops_path)
    check("case11: replace at capacity exits 0", r.returncode == 0, r.stdout + r.stderr)
    check("case11: stdout carries REPLACED P-07", "REPLACED P-07" in r.stdout, r.stdout)

    content = open(path, encoding="utf-8").read()
    entries = parse_section_entries(content, "Patterns")
    check("case11: Patterns still holds 15 entries", len(entries) == 15, content)
    ids = [eid for eid, _ in entries]
    check(
        "case11: the 7th entry line is P-07",
        len(ids) >= 7 and ids[6] == "P-07",
        ids,
    )
    texts = dict(entries)
    check(
        "case11: the 7th entry line carries the new text",
        texts.get("P-07") == "REPLACED TEXT SEVEN",
        content,
    )

    r2 = subprocess.run([CHECK_EXPERTISE_BIN, path], capture_output=True, text=True)
    check(
        "case11: check-expertise.sh still accepts the written file",
        r2.returncode == 0,
        r2.stdout + r2.stderr,
    )


def case_removal(root):
    """Case 12 — REMOVAL. A drop deletes the entry outright and leaves its neighbours in
    place."""
    path = target(root, "case12")
    five = [(f"G-{i:02d}", f"text {i}") for i in range(1, 6)]
    write_file(path, [("Gotchas", five)])
    ops_path = write_ops(
        os.path.join(root, "case12_ops.json"),
        [{"op": "drop", "target": "G-03", "section": "Gotchas"}],
    )

    r = run_ops(path, ops_path)
    check("case12: drop exits 0", r.returncode == 0, r.stdout + r.stderr)
    check("case12: stdout carries DROPPED G-03", "DROPPED G-03" in r.stdout, r.stdout)

    content = open(path, encoding="utf-8").read()
    check("case12: the string - G-03: is absent from the file", "- G-03:" not in content, content)
    for eid in ("G-01", "G-02", "G-04", "G-05"):
        check(f"case12: {eid} is still present", f"- {eid}:" in content, content)

    r2 = subprocess.run([CHECK_EXPERTISE_BIN, path], capture_output=True, text=True)
    check(
        "case12: check-expertise.sh still accepts the written file",
        r2.returncode == 0,
        r2.stdout + r2.stderr,
    )


def case_missing_target(root):
    """Case 13 — MISSING TARGET (D-04). A replace naming an id absent from its section exits
    10, writes nothing, and the file stays writable afterward."""
    path = target(root, "case13")
    original = write_file(path, [("Patterns", [("P-01", "one")])])
    before = hashlib.sha256(open(path, "rb").read()).hexdigest()
    ops_path = write_ops(
        os.path.join(root, "case13_ops.json"),
        [{"op": "replace", "target": "P-99", "section": "Patterns", "entry": "does not exist"}],
    )

    r = run_ops(path, ops_path)
    combined = r.stdout + r.stderr
    check("case13: missing target exits 10", r.returncode == 10, combined)
    check("case13: combined output carries MISSING TARGET", "MISSING TARGET" in combined, combined)
    check("case13: combined output carries the id P-99", "P-99" in combined, combined)
    check("case13: combined output carries the section Patterns", "Patterns" in combined, combined)

    after = hashlib.sha256(open(path, "rb").read()).hexdigest()
    check("case13: file sha256 is unchanged", after == before, (before, after))
    check(
        "case13: file content is byte identical to before",
        open(path, encoding="utf-8").read() == original,
        None,
    )

    entries_noop = os.path.join(root, "case13_entries_noop.md")
    write_entries(entries_noop, [("Patterns", [("P-01", "one")])])
    r2 = run_apply(path, entries_noop)
    check("case13: a following add-only apply still exits 0", r2.returncode == 0, r2.stdout + r2.stderr)


def case_ambiguous_target(root):
    """Case 14 — AMBIGUOUS TARGET, D-03's whole set, TWO sub-cases: (b) a duplicate id inside
    one section of the base file, (c) two ops in one proposal naming the same target. The
    former sub-case (a) — one id in two sections with the op omitting section — is DELETED, not
    renamed: D-02 makes section required on every op, so that input is refused at exit 12 by
    shape before any resolution runs (exercised through the CLI by case20 instead)."""
    # (b) — a base file whose Patterns section carries P-04 twice.
    path_b = target(root, "case14b")
    write_file(path_b, [("Patterns", [("P-01", "one"), ("P-04", "four-a"), ("P-04", "four-b")])])
    before_b = hashlib.sha256(open(path_b, "rb").read()).hexdigest()
    ops_b = write_ops(
        os.path.join(root, "case14b_ops.json"),
        [{"op": "replace", "target": "P-04", "section": "Patterns", "entry": "new text"}],
    )
    r_b = run_ops(path_b, ops_b)
    combined_b = r_b.stdout + r_b.stderr
    check("case14: (b) a duplicate id in one section exits 11", r_b.returncode == 11, combined_b)
    check("case14: (b) combined output carries AMBIGUOUS TARGET", "AMBIGUOUS TARGET" in combined_b, combined_b)
    check("case14: (b) combined output carries the id P-04", "P-04" in combined_b, combined_b)
    check("case14: (b) combined output carries the section Patterns", "Patterns" in combined_b, combined_b)
    check("case14: (b) combined output carries a reason", "reason=" in combined_b, combined_b)
    after_b = hashlib.sha256(open(path_b, "rb").read()).hexdigest()
    check("case14: (b) file sha256 is unchanged", after_b == before_b, (before_b, after_b))

    # (c) — two ops in one proposal naming the same section and id.
    path_c = target(root, "case14c")
    write_file(path_c, [("Patterns", [("P-01", "one"), ("P-02", "two")])])
    before_c = hashlib.sha256(open(path_c, "rb").read()).hexdigest()
    ops_c = write_ops(
        os.path.join(root, "case14c_ops.json"),
        [
            {"op": "replace", "target": "P-01", "section": "Patterns", "entry": "first replace"},
            {"op": "replace", "target": "P-01", "section": "Patterns", "entry": "second replace"},
        ],
    )
    r_c = run_ops(path_c, ops_c)
    combined_c = r_c.stdout + r_c.stderr
    check("case14: (c) two ops naming the same target exits 11", r_c.returncode == 11, combined_c)
    check("case14: (c) combined output carries AMBIGUOUS TARGET", "AMBIGUOUS TARGET" in combined_c, combined_c)
    check("case14: (c) combined output carries the id P-01", "P-01" in combined_c, combined_c)
    check("case14: (c) combined output carries the section Patterns", "Patterns" in combined_c, combined_c)
    check("case14: (c) combined output carries a reason", "reason=" in combined_c, combined_c)
    after_c = hashlib.sha256(open(path_c, "rb").read()).hexdigest()
    check("case14: (c) file sha256 is unchanged", after_c == before_c, (before_c, after_c))


def case_atomic_failure(root):
    """Case 15 — ATOMIC FAILURE (D-08). A three-op proposal whose first two ops are valid and
    whose third names a missing target leaves the file untouched — nothing is applied until
    every op has resolved."""
    path = target(root, "case15")
    write_file(path, [("Patterns", [("P-01", "one"), ("P-02", "two"), ("P-03", "three")])])
    before = hashlib.sha256(open(path, "rb").read()).hexdigest()
    ops_path = write_ops(
        os.path.join(root, "case15_ops.json"),
        [
            {"op": "replace", "target": "P-01", "section": "Patterns", "entry": "one replaced"},
            {"op": "drop", "target": "P-02", "section": "Patterns"},
            {"op": "replace", "target": "P-99", "section": "Patterns", "entry": "missing"},
        ],
    )

    r = run_ops(path, ops_path)
    check("case15: atomic failure exits non-zero", r.returncode != 0, r.stdout + r.stderr)
    after = hashlib.sha256(open(path, "rb").read()).hexdigest()
    check(
        "case15: file sha256 equals the sha256 taken before the invocation",
        after == before,
        (before, after),
    )

    entries_noop = os.path.join(root, "case15_entries_noop.md")
    write_entries(entries_noop, [("Patterns", [("P-01", "one")])])
    r2 = run_apply(path, entries_noop)
    check("case15: a following add-only apply still exits 0", r2.returncode == 0, r2.stdout + r2.stderr)


def case_add_only_compatibility(root):
    """Case 16 — ADD-ONLY COMPATIBILITY (D-09). Through apply --entries only, unmodified: the
    ADDED/PRESERVED/APPLIED tokens, exit 7 on divergent text, exit 8 over cap."""
    path = target(root, "case16")
    write_file(path, [("Patterns", [(f"P-{i:02d}", f"text {i}") for i in range(1, 15)])])  # P-01..P-14
    entries_add = os.path.join(root, "case16_entries_add.md")
    write_entries(entries_add, [("Patterns", [("P-01", "text 1"), ("P-15", "text 15")])])
    r = run_apply(path, entries_add)
    check("case16: add-only proposal exits 0", r.returncode == 0, r.stdout + r.stderr)
    check("case16: stdout carries the ADDED token", "ADDED P-15" in r.stdout, r.stdout)
    check("case16: stdout carries the PRESERVED token", "PRESERVED P-01" in r.stdout, r.stdout)
    check("case16: stdout carries the APPLIED token", "APPLIED" in r.stdout, r.stdout)

    entries_conflict = os.path.join(root, "case16_entries_conflict.md")
    write_entries(entries_conflict, [("Patterns", [("P-01", "DIFFERENT TEXT")])])
    r2 = run_apply(path, entries_conflict)
    check("case16: same-id-different-text proposal still exits 7", r2.returncode == 7, r2.stdout + r2.stderr)

    entries_overcap = os.path.join(root, "case16_entries_overcap.md")
    write_entries(entries_overcap, [("Patterns", [("P-16", "text 16")])])
    r3 = run_apply(path, entries_overcap)
    check("case16: over-cap proposal still exits 8", r3.returncode == 8, r3.stdout + r3.stderr)


class _ContractHarvestError(Exception):
    """Raised when contract_drift cannot mechanically locate the ops vocabulary line, the
    parser's own --ops help text, or runs a broken probe. Caught only inside contract_drift,
    which turns it into a failure string rather than crashing the case."""


def _normalise(text):
    """Collapse whitespace runs to one space and strip backtick/asterisk/underscore, so a
    reflow, a rewrap or an emphasis change cannot redden contract_drift."""
    text = re.sub(r"[`*_]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _harvest_contract_verbs(normalised):
    """CONTRACT, harvested MECHANICALLY: the ONE pipe-separated verb list carried on the ops
    example's `op:` key. Never restated as a literal set — a restated copy is exactly what
    would make this blind to the drift it exists to catch."""
    matches = re.findall(r"op: \w+ # (\w+(?: \| \w+)+)", normalised)
    if len(matches) != 1:
        raise _ContractHarvestError(
            "the ops vocabulary line could not be located: pattern 'op: <verb> # <a | b | ...>' "
            f"matched {len(matches)} times in the normalised SKILL.md text, expected exactly 1"
        )
    return [tok.strip() for tok in matches[0].split("|")]


def _harvest_help_verbs():
    """A SECOND, independent source of candidate verbs: the ops parser's own --ops help text,
    which is what makes ACCEPTED - CONTRACT able to fail at all."""
    r = subprocess.run([sys.executable, CLI, "ops", "--help"], capture_output=True, text=True)
    m = re.search(r"list of ([\w/]+) ops", r.stdout)
    if not m:
        raise _ContractHarvestError(
            f"the ops --help text did not name a slash-separated verb list: {r.stdout!r}"
        )
    return m.group(1).split("/")


def _probe_accepted_verbs(candidate_verbs):
    """ACCEPTED, collected by probing each candidate verb with a well-formed single op against
    its own throwaway fixture. Every probe op carries a target and section that EXIST in that
    fixture, so a refusal is attributable to the verb, never to a missing key."""
    tmp = tempfile.mkdtemp(prefix="expertise-merge-case17-probe-")
    try:
        accepted = set()
        for verb in candidate_verbs:
            fixture = target(tmp, f"probe-{verb}")
            write_file(fixture, [("Patterns", [("X-01", "known text")])])
            op = {"op": verb, "target": "X-01", "section": "Patterns"}
            if verb == "add":
                op["entry"] = "known text"
            elif verb == "replace":
                op["entry"] = "probe replaced text"
            ops_path = write_ops(os.path.join(tmp, f"{verb}_ops.json"), [op])
            r = run_ops(fixture, ops_path)
            combined = r.stdout + r.stderr
            if r.returncode == 12:
                if re.search(r"unknown op verb|op=merge", combined):
                    continue
                raise _ContractHarvestError(
                    f"broken probe for verb {verb!r} — exit 12 did not name the verb, it named "
                    f"a key instead: {combined!r}"
                )
            accepted.add(verb)
        return accepted
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def contract_drift(skill_text):
    """Mechanised contract-drift detector (BUG-1308, D-10, SC-09, T-02 case17). Returns a list
    of failure strings — empty means the ops subcommand and the distillation contract agree.
    Runnable against a drifted COPY of the skill text: CONTRACT and REWRITTEN are re-harvested
    from `skill_text` every call; ACCEPTED is probed against the real tool, unaffected by the
    copy, because it names what the TOOL accepts, not what the text claims."""
    normalised = _normalise(skill_text)
    try:
        contract = set(_harvest_contract_verbs(normalised))
        help_verbs = set(_harvest_help_verbs())
        accepted = _probe_accepted_verbs(sorted(contract | help_verbs))
    except _ContractHarvestError as exc:
        return [str(exc)]

    rewritten = (
        {"merge"}
        if "replace on the surviving id" in normalised and "drop of the absorbed id" in normalised
        else set()
    )

    failures = []
    left = contract - accepted
    if left != rewritten:
        failures.append(
            f"CONTRACT - ACCEPTED == {sorted(left)!r} but REWRITTEN == {sorted(rewritten)!r}"
        )
    right = accepted - contract
    if right:
        failures.append(f"ACCEPTED - CONTRACT == {sorted(right)!r}, expected empty set()")
    return failures


def case_contract_drift():
    """Case 17 — CONTRACT DRIFT DETECTOR (D-10, SC-09, T-03), the same idiom as case 8. The one
    statement this case exists to hold: every op verb the distillation contract names is either
    accepted by the ops subcommand or is merge, the verb the contract itself rewrites into a
    replace on the surviving id plus a drop of the absorbed id — and the tool accepts no verb
    the contract omits."""
    skill_path = os.path.join(ROOT, ".claude", "skills", "harness-distill", "SKILL.md")
    skill_text = open(skill_path, encoding="utf-8").read()

    anchor_pattern = r"op: \w+ # (\w+(?: \| \w+)+)"
    anchor_matches = re.findall(anchor_pattern, _normalise(skill_text))
    check(
        "case17: the op: vocabulary anchor matches the real SKILL.md exactly once",
        len(anchor_matches) == 1,
        f"pattern={anchor_pattern!r} matches={anchor_matches!r}",
    )

    real_failures = contract_drift(skill_text)
    check("case17: contract_drift(real SKILL.md) returns no failures", real_failures == [], real_failures)

    # MUTATION DEMONSTRATION — three drifted COPIES built in this case's own tmp dir. The real
    # SKILL.md is never written.
    copy_a = skill_text.replace("drop of the absorbed id", "handling of the absorbed id")
    check(
        "case17: copy (a) actually removed the phrase 'drop of the absorbed id'",
        "drop of the absorbed id" not in copy_a and "replace on the surviving id" in copy_a,
        None,
    )
    failures_a = contract_drift(copy_a)
    check(
        "case17: copy (a) — rewrite phrase removed — reddens the FIRST direction "
        "(CONTRACT - ACCEPTED)",
        any(f.startswith("CONTRACT - ACCEPTED") for f in failures_a),
        failures_a,
    )
    check(
        "case17: copy (a) does not redden the SECOND direction (ACCEPTED - CONTRACT)",
        not any(f.startswith("ACCEPTED - CONTRACT") for f in failures_a),
        failures_a,
    )

    copy_b = skill_text.replace(
        "# add | replace | merge | drop", "# add | replace | merge | drop | prune"
    )
    check(
        "case17: copy (b) actually inserted the extra verb prune",
        "| drop | prune" in copy_b,
        None,
    )
    failures_b = contract_drift(copy_b)
    check(
        "case17: copy (b) — extra verb prune inserted — reddens the FIRST direction "
        "(CONTRACT - ACCEPTED)",
        any(f.startswith("CONTRACT - ACCEPTED") for f in failures_b),
        failures_b,
    )
    check(
        "case17: copy (b) does not redden the SECOND direction (ACCEPTED - CONTRACT)",
        not any(f.startswith("ACCEPTED - CONTRACT") for f in failures_b),
        failures_b,
    )

    copy_c = skill_text.replace("# add | replace | merge | drop", "# add | replace | merge")
    check(
        "case17: copy (c) actually removed the verb drop from the vocabulary line",
        "# add | replace | merge" in copy_c
        and "# add | replace | merge | drop" not in copy_c,
        None,
    )
    failures_c = contract_drift(copy_c)
    check(
        "case17: copy (c) — drop removed from the vocabulary line — reddens the SECOND "
        "direction (ACCEPTED - CONTRACT)",
        any(f.startswith("ACCEPTED - CONTRACT") for f in failures_c),
        failures_c,
    )
    check(
        "case17: copy (c) does not redden the FIRST direction (CONTRACT - ACCEPTED)",
        not any(f.startswith("CONTRACT - ACCEPTED") for f in failures_c),
        failures_c,
    )


def _launch_case18_children(path, entries_a, ops_b):
    """Launch child A (apply) and child B (ops) against the same file, both PIPE-captured."""
    child_a = subprocess.Popen(
        [sys.executable, CLI, "apply", "--file", path, "--entries", entries_a],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    child_b = subprocess.Popen(
        [sys.executable, CLI, "ops", "--file", path, "--ops", ops_b],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    return child_a, child_b


def _poll_case18_children(child_a, child_b, hold_window):
    """Poll both children every 0.05s for `hold_window` seconds. Returns (premature, elapsed):
    premature names whichever child exited early, or None if neither did."""
    started = time.monotonic()
    deadline = started + hold_window
    while time.monotonic() < deadline:
        if child_a.poll() is not None:
            return "child A (apply)", time.monotonic() - started
        if child_b.poll() is not None:
            return "child B (ops)", time.monotonic() - started
        time.sleep(0.05)
    return None, time.monotonic() - started


def _hold_lock_and_race_case18(lock_path, path, entries_a, ops_b, hold_window):
    """Take the production lock ourselves, launch both children under it, and check neither
    exits during the hold window — the D-09 regression this case exists to catch. NO
    production test bypass anywhere in this call chain: no environment variable, no injected
    sleep, no test-only flag, no edit of expertise-merge.py or harness_merge.py."""
    with harness_merge.acquire(lock_path):
        child_a, child_b = _launch_case18_children(path, entries_a, ops_b)
        premature, held_wall_clock = _poll_case18_children(child_a, child_b, hold_window)
    check(
        f"case18: neither child exits during the {hold_window}s hold window while the "
        f"test holds the production lock ({held_wall_clock:.2f}s observed)",
        premature is None,
        (
            f"{premature} exited while the test held the lock — it did not take the "
            "lock the core defines; this is the D-09 regression"
        ) if premature else "",
    )
    return child_a, child_b


def _await_case18_child(child, label):
    """Wait up to 20s for `child` to exit once the lock is released, and check it exits 0."""
    try:
        out, err = child.communicate(timeout=20)
        check(
            f"case18: child {label} exits 0 once the lock is released",
            child.returncode == 0,
            f"exit {child.returncode}: {out + err}",
        )
    except subprocess.TimeoutExpired:
        child.kill()
        check(f"case18: child {label} completes within 20s of the lock being released", False, "")


def _check_case18_final_state(path, marker):
    content = open(path, encoding="utf-8").read()
    entries = parse_section_entries(content, "Patterns")
    ids = sorted(eid for eid, _ in entries)
    expected_ids = sorted([f"P-{i:02d}" for i in range(1, 9)] + ["P-09", "P-10"])
    check(
        "case18: the Patterns id census is exactly the original eight plus P-09 and P-10",
        ids == expected_ids,
        ids,
    )
    texts = dict(entries)
    check(
        "case18: the P-07 entry carries child B's marker text",
        texts.get("P-07") == marker,
        content,
    )


def case_concurrent_writers(root):
    """Case 18 — CONCURRENT WRITERS (SC-11, D-09). Contention forced DETERMINISTICALLY by the
    test itself holding the production lock, with NO production test bypass: no environment
    variable, no injected sleep, no test-only flag, no edit of expertise-merge.py or
    harness_merge.py."""
    path = target(root, "case18")
    eight = [(f"P-{i:02d}", f"text {i}") for i in range(1, 9)]
    write_file(path, [("Patterns", eight)])

    entries_a = os.path.join(root, "case18_entries.md")
    write_entries(entries_a, [("Patterns", [("P-09", "text 9"), ("P-10", "text 10")])])
    marker = "CHILD B MARKER TEXT"
    ops_b = write_ops(
        os.path.join(root, "case18_ops.json"),
        [{"op": "replace", "target": "P-07", "section": "Patterns", "entry": marker}],
    )

    child_a, child_b = _hold_lock_and_race_case18(path + ".lock", path, entries_a, ops_b, 2.0)
    _await_case18_child(child_a, "A (apply)")
    _await_case18_child(child_b, "B (ops)")
    _check_case18_final_state(path, marker)


def case_multi_op_composition(root):
    """Case 19 — MULTI-OP COMPOSITION IN ONE SECTION, through the CLI (cycle-1 panel finding).
    Two ops on distinct original indices of one section, low index first: drop P-01 (index 0),
    then replace P-05 (index 4). u11 is the unit half; the reversed-order run is deliberately
    not repeated here — u11 asserts order-independence directly against resolve_ops."""
    path = target(root, "case19")
    five = [(f"P-{i:02d}", f"text {i}") for i in range(1, 6)]
    write_file(path, [("Patterns", five)])
    marker = "CASE19 MARKER TEXT"
    ops_path = write_ops(
        os.path.join(root, "case19_ops.json"),
        [
            {"op": "drop", "target": "P-01", "section": "Patterns"},
            {"op": "replace", "target": "P-05", "section": "Patterns", "entry": marker},
        ],
    )

    r = run_ops(path, ops_path)
    check("case19: multi-op composition exits 0", r.returncode == 0, r.stdout + r.stderr)
    check("case19: stdout carries DROPPED P-01", "DROPPED P-01" in r.stdout, r.stdout)
    check("case19: stdout carries REPLACED P-05", "REPLACED P-05" in r.stdout, r.stdout)

    content = open(path, encoding="utf-8").read()
    entries = parse_section_entries(content, "Patterns")
    ids = [eid for eid, _ in entries]
    check(
        "case19: the id sequence is exactly P-02, P-03, P-04, P-05 in file order",
        ids == ["P-02", "P-03", "P-04", "P-05"],
        ids,
    )
    texts = dict(entries)
    check("case19: the P-05 entry carries the marker text", texts.get("P-05") == marker, content)
    other_marked = [eid for eid, text in entries if eid != "P-05" and text == marker]
    check("case19: no other entry carries the marker text", other_marked == [], other_marked)

    r2 = subprocess.run([CHECK_EXPERTISE_BIN, path], capture_output=True, text=True)
    check(
        "case19: check-expertise.sh still accepts the written file",
        r2.returncode == 0,
        r2.stdout + r2.stderr,
    )


def _assert_case20_malformed(path, ops_path, label, what, extra_checks):
    """Run `ops_path` through the ops CLI and assert the shared MALFORMED OPS(12) shape: exit
    code, the token itself, byte-identity — then each of `extra_checks` (message, substring)
    pairs against the combined output. Returns the combined stdout+stderr."""
    before = hashlib.sha256(open(path, "rb").read()).hexdigest()
    r = run_ops(path, ops_path)
    combined = r.stdout + r.stderr
    check(f"case20: ({label}) {what} exits 12", r.returncode == 12, combined)
    check(f"case20: ({label}) combined output carries MALFORMED OPS", "MALFORMED OPS" in combined, combined)
    for message, token in extra_checks:
        check(f"case20: ({label}) {message}", token in combined, combined)
    after = hashlib.sha256(open(path, "rb").read()).hexdigest()
    check(f"case20: ({label}) file sha256 is unchanged", after == before, (before, after))
    return combined


def _case20_missing_section_key(root, path):
    """(a) — a well-formed replace op with the section key ABSENT."""
    ops = write_ops(
        os.path.join(root, "case20a_ops.json"),
        [{"op": "replace", "target": "P-01", "entry": "new text"}],
    )
    _assert_case20_malformed(path, ops, "a", "missing section key", [
        ("combined output names the offending key section", "section"),
        ("combined output names the op's index", "index=0"),
    ])
    entries_noop = os.path.join(root, "case20a_entries_noop.md")
    write_entries(entries_noop, [("Patterns", [("P-01", "text 1")])])
    r2 = run_apply(path, entries_noop)
    check(
        "case20: (a) a following add-only apply still exits 0, so the file is still writable",
        r2.returncode == 0,
        r2.stdout + r2.stderr,
    )


def _case20_empty_section_key(root, path):
    """(b) — the same op with section present but the empty string."""
    ops = write_ops(
        os.path.join(root, "case20b_ops.json"),
        [{"op": "replace", "target": "P-01", "section": "", "entry": "new text"}],
    )
    _assert_case20_malformed(path, ops, "b", "empty section key", [
        ("combined output names the offending key section", "section"),
        ("combined output names the op's index", "index=0"),
    ])


def _case20_digest_mapping_payload(root, path):
    """(c) — a DIGEST-shaped mapping rather than a bare list; the settled payload shape has no
    mapping wrapper (T-01), so this is written directly, never through write_ops."""
    ops = os.path.join(root, "case20c_ops.json")
    with open(ops, "w", encoding="utf-8") as f:
        json.dump(
            {
                "expertise_update": [
                    {"op": "replace", "target": "P-01", "section": "Patterns", "entry": "new text"}
                ]
            },
            f,
        )
    _assert_case20_malformed(path, ops, "c", "digest-shaped mapping", [
        ("combined output carries the literal token expertise_update", "expertise_update"),
    ])


def case_malformed_ops_cli(root):
    """Case 20 — MALFORMED OPS THROUGH THE CLI, WITH BYTE IDENTITY (D-02, D-05, SC-04). The
    exit-12 shape branch's CLI half. (a)/(b) are the required-section ruling; u13 is their unit
    half. (c) is the payload-shape refusal; u14 is its unit half."""
    path = target(root, "case20")
    three = [(f"P-{i:02d}", f"text {i}") for i in range(1, 4)]
    write_file(path, [("Patterns", three)])

    _case20_missing_section_key(root, path)
    _case20_empty_section_key(root, path)
    _case20_digest_mapping_payload(root, path)


def case_ops_entry_injection(root):
    """Case 21 — ENTRY INJECTION (VL-01). An `entry` carrying an embedded newline (`\\n` or
    `\\r`) is a MALFORMED OPS(12) shape refusal, not a value `render` ever writes verbatim into
    the file. `replace` is the exact shape the exploit needs: it never changes a section's
    entry COUNT, so `_check_caps` (D-07) — which only ever counts parsed list length — sees no
    overflow, while the embedded newline still becomes real physical lines once `render` writes
    it, forging a fake section header/entry inside an already-at-cap section."""
    path = target(root, "case21")
    write_file(path, [("Gotchas", [(f"G-{i:02d}", f"text {i}") for i in range(1, 16)])])  # at cap
    before = hashlib.sha256(open(path, "rb").read()).hexdigest()
    forged = "## Gotchas (max 15)\n- G-16: forged additional entry"

    for label, newline in (("a", "\\n"), ("b", "\\r")):
        real_newline = "\n" if newline == "\\n" else "\r"
        ops = write_ops(
            os.path.join(root, f"case21{label}_ops.json"),
            [{"op": "replace", "target": "G-08", "section": "Gotchas",
              "entry": f"harmless text{real_newline}{forged}"}],
        )
        r = run_ops(path, ops)
        combined = r.stdout + r.stderr
        check(f"case21: ({label}) an entry embedding {newline} exits 12", r.returncode == 12, combined)
        check(f"case21: ({label}) combined output carries MALFORMED OPS", "MALFORMED OPS" in combined, combined)
        after = hashlib.sha256(open(path, "rb").read()).hexdigest()
        check(f"case21: ({label}) file sha256 is unchanged", after == before, (before, after))

    content = open(path, encoding="utf-8").read()
    check(
        "case21: the forged header never reaches the file",
        "## Gotchas (max 15)\n- G-16:" not in content,
        content,
    )


def case_ops_target_injection(root):
    """Case 22 — TARGET INJECTION (VL-01). A `target` carrying an embedded newline (`\\n` or
    `\\r`) is the same MALFORMED OPS(12) shape refusal as an injected `entry` — `target` is
    written verbatim into a replace/drop refusal's stdout and, on `add`, into the rendered file
    itself, so it gets no weaker a check than `entry`."""
    path = target(root, "case22")
    write_file(path, [("Patterns", [("P-01", "one")])])
    before = hashlib.sha256(open(path, "rb").read()).hexdigest()

    for label, newline in (("a", "\\n"), ("b", "\\r")):
        real_newline = "\n" if newline == "\\n" else "\r"
        forged_target = f"P-99{real_newline}- P-77: forged via target"
        ops = write_ops(
            os.path.join(root, f"case22{label}_ops.json"),
            [{"op": "add", "target": forged_target, "section": "Patterns", "entry": "harmless"}],
        )
        r = run_ops(path, ops)
        combined = r.stdout + r.stderr
        check(f"case22: ({label}) a target embedding {newline} exits 12", r.returncode == 12, combined)
        check(f"case22: ({label}) combined output carries MALFORMED OPS", "MALFORMED OPS" in combined, combined)
        after = hashlib.sha256(open(path, "rb").read()).hexdigest()
        check(f"case22: ({label}) file sha256 is unchanged", after == before, (before, after))

    content = open(path, encoding="utf-8").read()
    check("case22: the forged line never reaches the file", "P-77" not in content, content)


def case_ops_non_string_target(root):
    """Case 23 — NON-STRING TARGET (VL-02). A `target` that is a JSON array is a MALFORMED
    OPS(12) shape refusal, not an uncaught TypeError escaping the file's documented exit
    contract (0/6/7/8/9/10/11/12)."""
    path = target(root, "case23")
    write_file(path, [("Patterns", [("P-01", "one")])])
    before = hashlib.sha256(open(path, "rb").read()).hexdigest()

    ops = write_ops(
        os.path.join(root, "case23_ops.json"),
        [{"op": "add", "target": ["P-50", "x"], "section": "Patterns", "entry": "x"}],
    )
    r = run_ops(path, ops)
    combined = r.stdout + r.stderr
    check("case23: a non-string target exits 12, not 1", r.returncode == 12, combined)
    check("case23: combined output carries MALFORMED OPS", "MALFORMED OPS" in combined, combined)
    check(
        "case23: combined output carries no Python traceback",
        "Traceback (most recent call last)" not in combined,
        combined,
    )
    after = hashlib.sha256(open(path, "rb").read()).hexdigest()
    check("case23: file sha256 is unchanged", after == before, (before, after))


def _assert_case24_ambiguous(root, stem, label, what, entry_text, extra_checks):
    """Write a base with `Patterns` carrying P-07 twice, propose an `add` of `entry_text`
    against it, and assert the shared AMBIGUOUS TARGET(11) shape: exit code, the token, byte
    identity — then each of `extra_checks` (message, substring) pairs against the output."""
    duplicated = [("P-01", "one"), ("P-07", "four-a"), ("P-07", "four-b")]
    path = target(root, stem)
    write_file(path, [("Patterns", duplicated)])
    before = hashlib.sha256(open(path, "rb").read()).hexdigest()
    ops = write_ops(
        os.path.join(root, f"{stem}_ops.json"),
        [{"op": "add", "target": "P-07", "section": "Patterns", "entry": entry_text}],
    )
    r = run_ops(path, ops)
    combined = r.stdout + r.stderr
    check(f"case24: ({label}) {what}, not the pre-fix outcome", r.returncode == 11, combined)
    check(f"case24: ({label}) combined output carries AMBIGUOUS TARGET", "AMBIGUOUS TARGET" in combined, combined)
    for message, token in extra_checks:
        check(f"case24: ({label}) {message}", token in combined, combined)
    after = hashlib.sha256(open(path, "rb").read()).hexdigest()
    check(f"case24: ({label}) file sha256 is unchanged", after == before, (before, after))


def case_ops_add_duplicated_base(root):
    """Case 24 — ADD AGAINST A DUPLICATED BASE (VL-03, D-03(a)). A base id appearing twice in
    its own section is ambiguous for `add` exactly as it already is for `replace`/`drop` — the
    (a) CONFLICT-today shape (proposed text matching neither occurrence) and the (b)
    PRESERVED-today shape (proposed text matching the surviving, last-in-file occurrence) both
    refuse AMBIGUOUS TARGET(11), never silently resolving against whichever occurrence `dict()`
    happens to keep."""
    _assert_case24_ambiguous(
        root, "case24a", "a", "add matching neither occurrence exits 11",
        "third totally different text",
        [("combined output carries the id P-07", "P-07")],
    )
    _assert_case24_ambiguous(
        root, "case24b", "b", "add matching the surviving occurrence exits 11",
        "four-b",
        [],
    )


def _run_all_cases(root):
    case_naive_last_writer_wins(root)
    case_green_union(root)
    case_concurrency_real(root)
    case_divergent_text(root)
    case_cap_overflow(root)
    case_new_file(root)
    case_destination_refusal(root)
    case_cap_drift_detector()
    case_stale_lock_recovery(root)
    case_replace_at_capacity(root)
    case_removal(root)
    case_missing_target(root)
    case_ambiguous_target(root)
    case_atomic_failure(root)
    case_add_only_compatibility(root)
    case_contract_drift()
    case_concurrent_writers(root)
    case_multi_op_composition(root)
    case_malformed_ops_cli(root)
    case_ops_entry_injection(root)
    case_ops_target_injection(root)
    case_ops_non_string_target(root)
    case_ops_add_duplicated_base(root)


def _report_results():
    fails = 0
    for name, ok, detail in RESULTS:
        if ok:
            print(f"PASS  {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n      | {detail}")
    return fails


def main():
    root = tempfile.mkdtemp(prefix="expertise-merge-test-")
    try:
        _run_all_cases(root)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    fails = _report_results()

    summary = "FAIL test-expertise-merge.py" if fails else "PASS test-expertise-merge.py"
    print(summary)
    return fails


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
