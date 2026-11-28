#!/usr/bin/env python3
"""Tests for expertise-merge.py's `apply` subcommand (FEAT-30 T-06, D-05, DEC-95).

Every case runs the CLI as a SUBPROCESS against a fixture file in a fresh tempfile.mkdtemp() —
never a real `.harness/expertise/*.md` or `.harness/*/expertise/*.md` file. Resolves the binary
the same way test-feature-worktree.py resolves its own, so a copy of the source under test can be
swapped in without editing this file:

    CLI = os.environ.get("EXPERTISE_MERGE_BIN") or os.path.join(BIN_DIR, "expertise-merge.py")

Case 1 is deliberately never routed through the CLI: it reproduces today's naive whole-file
write directly, so it stays red proof of the DEC-95 loss regardless of what this tool does.
"""
from integration_support import ROOT, BIN
import ast  # noqa: E402
import functools  # noqa: E402
import hashlib  # noqa: E402
import importlib.util
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from check_support import Checks  # noqa: E402
from git_support import git, git_out  # noqa: E402

ROOT = str(ROOT)
BIN_DIR = str(BIN)
CLI = os.environ.get("EXPERTISE_MERGE_BIN") or os.path.join(BIN_DIR, "expertise-merge.py")
CHECK_EXPERTISE_BIN = os.path.join(BIN_DIR, "check-expertise.py")
sys.path.insert(0, os.path.dirname(os.path.abspath(CLI)))
import harness_merge  # noqa: E402  (local import, after sys.path fix-up)
_expertise_merge_spec = importlib.util.spec_from_file_location("expertise_merge_it_under_test", CLI)
expertise_merge = importlib.util.module_from_spec(_expertise_merge_spec)
_expertise_merge_spec.loader.exec_module(expertise_merge)

# Derived from Python's own `str.splitlines()` — the exact alphabet `parse_expertise` uses to
# count physical lines — rather than a hand-copied literal list, so this constant tracks the
# parser instead of a snapshot of it (SEC-01/F1, fix cycle 2).
LINE_BREAKING_CHARS = tuple(
    chr(c) for c in list(range(0x00, 0xA0)) + [0x2028, 0x2029]
    if len(("a" + chr(c) + "b").splitlines()) > 1
)

C = Checks()
_CHECK_LOCK = threading.Lock()


def check(name, ok, detail=""):
    """C.check under a lock: the pooled cases call this from four threads at once."""
    with _CHECK_LOCK:
        return C.check(name, ok, detail)


def render(sections, title=None):
    """Expertise text: an optional '# Expertise — <title>' line, then '## name' / '- id: text'.
    sections: [(heading, [(id, text), ...]), ...]."""
    lines = [] if title is None else [f"# Expertise — {title}"]
    for name, entries in sections:
        lines.append(f"## {name}")
        lines.extend(f"- {eid}: {text}" for eid, text in entries)
    return "\n".join(lines) + "\n"


def _write_text(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return content


def write_file(path, sections):
    """Write a starting Expertise file, titled with the path's basename less any .md."""
    base = os.path.basename(path)
    return _write_text(path, render(sections, base[:-3] if base.endswith(".md") else base))


def write_entries(path, sections):
    """Write a proposal entries file — no title line, same section/entry line format."""
    return _write_text(path, render(sections))


def file_sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def check_expertise(path):
    return subprocess.run([sys.executable, CHECK_EXPERTISE_BIN, path], capture_output=True, text=True)


def target(root, stem):
    """An Expertise-TIER path inside `root`, for any fixture handed to `--file`.

    The fixtures used to be flat — `<root>/case2.md` — and the tool now REFUSES a --file
    that is not an Expertise file (exit 9), because `bash-write-guard.py` is
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

    r3 = check_expertise(path)
    check(
        "case2: check-expertise.py still accepts the merged file",
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


def case_cap_drift_detector(_root):
    """Case 8 — the caps this tool enforces and check-expertise.py's own CAPS mapping must
    agree, read as TEXT from both files rather than restated as a third literal here."""
    tool_src = open(CLI, encoding="utf-8").read()
    checker_src = open(CHECK_EXPERTISE_BIN, encoding="utf-8").read()

    m_tool = re.search(r"CAPS\s*=\s*(\{[^}]*\})", tool_src)
    m_checker = re.search(r"CAPS\s*=\s*(\{[^}]*\})", checker_src)
    check("case8: CAPS mapping found in expertise-merge.py", m_tool is not None, tool_src[:200])
    check(
        "case8: CAPS mapping found in check-expertise.py",
        m_checker is not None,
        checker_src[:200],
    )
    if not (m_tool and m_checker):
        return

    caps_tool = ast.literal_eval(m_tool.group(1))
    caps_checker = ast.literal_eval(m_checker.group(1))
    for section in ("Patterns", "Gotchas", "Outcomes", "Open"):
        check(
            f"case8: {section} cap agrees between expertise-merge.py and check-expertise.py",
            caps_tool.get(section) == caps_checker.get(section),
            f"tool={caps_tool.get(section)!r} checker={caps_checker.get(section)!r}",
        )


def case_destination_refusal(root):
    """Case 9 — the tool REFUSES a --file that is not an Expertise file (exit 9).

    THE HOLE THIS CLOSES, reproduced 2026-08-21 before the fix: `bash-write-guard.py` is
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
                       ("repository tier", os.path.join(".harness", "sample-product", "expertise"))):
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

    r2 = check_expertise(path)
    check(
        "case11: check-expertise.py still accepts the written file",
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

    r2 = check_expertise(path)
    check(
        "case12: check-expertise.py still accepts the written file",
        r2.returncode == 0,
        r2.stdout + r2.stderr,
    )


def case_missing_target(root):
    """Case 13 — MISSING TARGET (D-04). A replace naming an id absent from its section exits
    10, writes nothing, and the file stays writable afterward."""
    path = target(root, "case13")
    original = write_file(path, [("Patterns", [("P-01", "one")])])
    before = file_sha(path)
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

    after = file_sha(path)
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
    before_b = file_sha(path_b)
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
    after_b = file_sha(path_b)
    check("case14: (b) file sha256 is unchanged", after_b == before_b, (before_b, after_b))

    # (c) — two ops in one proposal naming the same section and id.
    path_c = target(root, "case14c")
    write_file(path_c, [("Patterns", [("P-01", "one"), ("P-02", "two")])])
    before_c = file_sha(path_c)
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
    after_c = file_sha(path_c)
    check("case14: (c) file sha256 is unchanged", after_c == before_c, (before_c, after_c))


def case_atomic_failure(root):
    """Case 15 — ATOMIC FAILURE (D-08). A three-op proposal whose first two ops are valid and
    whose third names a missing target leaves the file untouched — nothing is applied until
    every op has resolved."""
    path = target(root, "case15")
    write_file(path, [("Patterns", [("P-01", "one"), ("P-02", "two"), ("P-03", "three")])])
    before = file_sha(path)
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
    after = file_sha(path)
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


@functools.lru_cache(maxsize=None)
def _harvest_help_verbs():
    """Memoised: the tool is the same on every contract_drift call (a raise is not cached).
    A SECOND, independent source of candidate verbs: the ops parser's own --ops help text,
    which is what makes ACCEPTED - CONTRACT able to fail at all."""
    r = subprocess.run([sys.executable, CLI, "ops", "--help"], capture_output=True, text=True)
    m = re.search(r"list of ([\w/]+) ops", r.stdout)
    if not m:
        raise _ContractHarvestError(
            f"the ops --help text did not name a slash-separated verb list: {r.stdout!r}"
        )
    return tuple(m.group(1).split("/"))


@functools.lru_cache(maxsize=None)
def _probe_verb_accepted(verb):
    """Probe one candidate verb with a well-formed single op against its own throwaway fixture.
    The probe op carries a target and section that EXIST in that fixture, so a refusal is
    attributable to the verb, never to a missing key. Memoised per verb; a raise is not cached."""
    tmp = tempfile.mkdtemp(prefix="expertise-merge-case17-probe-")
    try:
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
        if r.returncode != 12:
            return True
        if re.search(r"unknown op verb|op=merge", combined):
            return False
        raise _ContractHarvestError(
            f"broken probe for verb {verb!r} — exit 12 did not name the verb, it named "
            f"a key instead: {combined!r}"
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _probe_accepted_verbs(candidate_verbs):
    """ACCEPTED, collected by probing each candidate verb (see _probe_verb_accepted)."""
    return {verb for verb in candidate_verbs if _probe_verb_accepted(verb)}


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


def case_contract_drift(_root):
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

    r2 = check_expertise(path)
    check(
        "case19: check-expertise.py still accepts the written file",
        r2.returncode == 0,
        r2.stdout + r2.stderr,
    )


def _assert_case20_malformed(path, ops_path, label, what, extra_checks):
    """Run `ops_path` through the ops CLI and assert the shared MALFORMED OPS(12) shape: exit
    code, the token itself, byte-identity — then each of `extra_checks` (message, substring)
    pairs against the combined output. Returns the combined stdout+stderr."""
    before = file_sha(path)
    r = run_ops(path, ops_path)
    combined = r.stdout + r.stderr
    check(f"case20: ({label}) {what} exits 12", r.returncode == 12, combined)
    check(f"case20: ({label}) combined output carries MALFORMED OPS", "MALFORMED OPS" in combined, combined)
    for message, token in extra_checks:
        check(f"case20: ({label}) {message}", token in combined, combined)
    after = file_sha(path)
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


def _case21_full_alphabet(root, path, before, forged):
    """Every character `str.splitlines()` treats as a line boundary (LINE_BREAKING_CHARS,
    derived from `splitlines()` itself, not hardcoded) is refused the same way `\\n`/`\\r` are."""
    for sep in LINE_BREAKING_CHARS:
        label = f"U+{ord(sep):04X}"
        ops = write_ops(
            os.path.join(root, f"case21_{ord(sep):04x}_ops.json"),
            [{"op": "replace", "target": "G-08", "section": "Gotchas",
              "entry": f"harmless text{sep}{forged}"}],
        )
        r = run_ops(path, ops)
        combined = r.stdout + r.stderr
        check(f"case21: ({label}) an entry embedding it exits 12", r.returncode == 12, combined)
        check(f"case21: ({label}) combined output carries MALFORMED OPS", "MALFORMED OPS" in combined, combined)
        after = file_sha(path)
        check(f"case21: ({label}) file sha256 is unchanged", after == before, (before, after))


def _case21_cap_bypass(root):
    """SEC-01's P1 exploit: U+2028 embedded in a `replace` on an AT-CAP Gotchas section. Asserts
    the RE-PARSED file (the tool's own `parse_expertise`, not exit code alone) never grows past
    the cap — the exit-code-only gap that let this through cycle 1."""
    path = target(root, "case21-cap-bypass")
    write_file(path, [("Gotchas", [(f"G-{i:02d}", f"text {i}") for i in range(1, 16)])])
    ops = write_ops(
        os.path.join(root, "case21-cap-bypass-ops.json"),
        [{"op": "replace", "target": "G-08", "section": "Gotchas",
          "entry": "harmless text\u2028- G-16: forged additional entry"}],
    )
    r = run_ops(path, ops)
    check("case21: (cap bypass) U+2028 replace on at-cap Gotchas exits 12", r.returncode == 12, r.stdout + r.stderr)
    content = open(path, encoding="utf-8").read()
    _, sections, _, _ = expertise_merge.parse_expertise(content)
    check("case21: (cap bypass) re-parsed Gotchas count stays 15", len(sections["Gotchas"]) == 15, sections["Gotchas"])


def _case21_cross_section(root):
    """SEC-01's escalated exploit: a VT-embedded forged `## Gotchas (max 15)` header inside a
    `Patterns` entry, which pre-fix reclassified the rest of `Patterns` into `Gotchas`. Asserts
    BOTH re-parsed section counts stay at their base values."""
    path = target(root, "case21-cross-section")
    write_file(path, [
        ("Patterns", [(f"P-{i:02d}", f"ptext {i}") for i in range(1, 15)]),  # 14/15, room for one
        ("Gotchas", [(f"G-{i:02d}", f"gtext {i}") for i in range(1, 16)]),   # at cap
    ])
    ops = write_ops(
        os.path.join(root, "case21-cross-section-ops.json"),
        [{"op": "replace", "target": "P-08", "section": "Patterns",
          "entry": "real text\x0b## Gotchas (max 15)\x0b- G-16: forged..."}],
    )
    r = run_ops(path, ops)
    check("case21: (cross-section) VT-embedded forged header exits 12", r.returncode == 12, r.stdout + r.stderr)
    content = open(path, encoding="utf-8").read()
    _, sections, _, _ = expertise_merge.parse_expertise(content)
    check("case21: (cross-section) re-parsed Patterns count stays 14", len(sections["Patterns"]) == 14, sections["Patterns"])
    check("case21: (cross-section) re-parsed Gotchas count stays 15", len(sections["Gotchas"]) == 15, sections["Gotchas"])


def case_ops_entry_injection(root):
    """Case 21 — ENTRY INJECTION (VL-01/SEC-01). An `entry` carrying any `str.splitlines()`
    line-boundary character is a MALFORMED OPS(12) shape refusal, not a value `render` ever
    writes verbatim into the file. `replace` is the exact shape the exploit needs: it never
    changes a section's entry COUNT, so a validator narrower than `parse_expertise` would pass
    Step A while `_check_caps` still sees no overflow — SEC-01/F1's gap, pinned closed here for
    the full alphabet plus the panel's two escalated exploits (cap bypass, cross-section
    reclassification), each proven via a RE-PARSE, not the exit code alone."""
    path = target(root, "case21")
    write_file(path, [("Gotchas", [(f"G-{i:02d}", f"text {i}") for i in range(1, 16)])])  # at cap
    before = file_sha(path)
    forged = "- G-16: forged additional entry"
    _case21_full_alphabet(root, path, before, forged)

    content = open(path, encoding="utf-8").read()
    check(
        "case21: the forged entry never reaches the file",
        "G-16:" not in content,
        content,
    )

    _case21_cap_bypass(root)
    _case21_cross_section(root)


def _case22_full_alphabet(root, path, before):
    """Every character `str.splitlines()` treats as a line boundary (LINE_BREAKING_CHARS,
    derived from `splitlines()` itself, not hardcoded) is refused the same way `\\n`/`\\r` are."""
    for sep in LINE_BREAKING_CHARS:
        label = f"U+{ord(sep):04X}"
        forged_target = f"P-99{sep}- P-77: forged via target"
        ops = write_ops(
            os.path.join(root, f"case22_{ord(sep):04x}_ops.json"),
            [{"op": "add", "target": forged_target, "section": "Patterns", "entry": "harmless"}],
        )
        r = run_ops(path, ops)
        combined = r.stdout + r.stderr
        check(f"case22: ({label}) a target embedding it exits 12", r.returncode == 12, combined)
        check(f"case22: ({label}) combined output carries MALFORMED OPS", "MALFORMED OPS" in combined, combined)
        after = file_sha(path)
        check(f"case22: ({label}) file sha256 is unchanged", after == before, (before, after))


def case_ops_target_injection(root):
    """Case 22 — TARGET INJECTION (VL-01/SEC-01). A `target` carrying any `str.splitlines()`
    line-boundary character is the same MALFORMED OPS(12) shape refusal as an injected `entry`
    — `target` is written verbatim into a replace/drop refusal's stdout and, on `add`, into the
    rendered file itself, so it gets no weaker a check than `entry`. Separators are
    LINE_BREAKING_CHARS, derived from `splitlines()` itself, not hardcoded."""
    path = target(root, "case22")
    write_file(path, [("Patterns", [("P-01", "one")])])
    before = file_sha(path)
    _case22_full_alphabet(root, path, before)

    content = open(path, encoding="utf-8").read()
    check("case22: the forged line never reaches the file", "P-77" not in content, content)
    _, sections, _, _ = expertise_merge.parse_expertise(content)
    check("case22: re-parsed Patterns count stays 1", len(sections["Patterns"]) == 1, sections["Patterns"])


def case_ops_non_string_target(root):
    """Case 23 — NON-STRING TARGET (VL-02). A `target` that is a JSON array is a MALFORMED
    OPS(12) shape refusal, not an uncaught TypeError escaping the file's documented exit
    contract (0/6/7/8/9/10/11/12)."""
    path = target(root, "case23")
    write_file(path, [("Patterns", [("P-01", "one")])])
    before = file_sha(path)

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
    after = file_sha(path)
    check("case23: file sha256 is unchanged", after == before, (before, after))


def _assert_case24_ambiguous(root, stem, label, what, entry_text, extra_checks):
    """Write a base with `Patterns` carrying P-07 twice, propose an `add` of `entry_text`
    against it, and assert the shared AMBIGUOUS TARGET(11) shape: exit code, the token, byte
    identity — then each of `extra_checks` (message, substring) pairs against the output."""
    duplicated = [("P-01", "one"), ("P-07", "four-a"), ("P-07", "four-b")]
    path = target(root, stem)
    write_file(path, [("Patterns", duplicated)])
    before = file_sha(path)
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
    after = file_sha(path)
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


def _assert_case25_malformed(root, stem, base_sections_list, ops_list, label, extra_checks=()):
    """Shared MALFORMED OPS(12) shape assertion for case25: exit code, the token, byte
    identity — then each of `extra_checks` (message, substring) pairs against the output.
    Returns the fixture path so the caller can re-parse it."""
    path = target(root, stem)
    write_file(path, base_sections_list)
    before = file_sha(path)
    ops = write_ops(os.path.join(root, f"{stem}_ops.json"), ops_list)
    r = run_ops(path, ops)
    combined = r.stdout + r.stderr
    check(f"case25: ({label}) exits 12", r.returncode == 12, combined)
    check(f"case25: ({label}) combined output carries MALFORMED OPS", "MALFORMED OPS" in combined, combined)
    for message, token in extra_checks:
        check(f"case25: ({label}) {message}", token in combined, combined)
    after = file_sha(path)
    check(f"case25: ({label}) file sha256 is unchanged", after == before, (before, after))
    return path


def case_ops_target_grammar(root):
    """Case 25 — TARGET ID GRAMMAR (VL-06). An `add`'s `target` must be exactly the id
    `ENTRY_RE` would parse back out of the line `render` writes for it — never merely a
    non-empty, single-line string. Demonstrates both exploits the panel measured against the
    pre-fix tool: (a) a too-long id (`PPPP-1`) that `ENTRY_RE` cannot match at all, which the
    pre-fix code accepted, exit 0, then made invisible on the very next re-parse; (b) a target
    embedding a shorter valid id (`P-01: fake prefix`) that `ENTRY_RE` DOES match — capturing
    only `P-01`, not the full target — which the pre-fix code accepted, exit 0, forging a
    second `P-01` that permanently locked out any future legitimate replace/drop of it."""
    path_a = _assert_case25_malformed(
        root, "case25a",
        [("Gotchas", [("G-01", "one")])],
        [{"op": "add", "target": "PPPP-1", "section": "Gotchas", "entry": "invisible entry test"}],
        "too-long id vanishes on reparse",
        [("combined output carries the malformed target", "PPPP-1")],
    )
    _, sections_a, _, _ = expertise_merge.parse_expertise(open(path_a, encoding="utf-8").read())
    check("case25: (a) re-parsed Gotchas holds no new entry", len(sections_a["Gotchas"]) == 1, sections_a["Gotchas"])

    path_b = _assert_case25_malformed(
        root, "case25b",
        [("Patterns", [("P-01", "existing pattern one.")])],
        [{"op": "add", "target": "P-01: fake prefix", "section": "Patterns", "entry": "attacker text"}],
        "id-embedding target refused, not aliased",
        [("combined output carries the malformed target", "P-01: fake prefix")],
    )
    _, sections_b, _, _ = expertise_merge.parse_expertise(open(path_b, encoding="utf-8").read())
    p01_count = sum(1 for eid, _ in sections_b.get("Patterns", []) if eid == "P-01")
    check("case25: (b) re-parsed Patterns holds exactly one P-01", p01_count == 1, sections_b.get("Patterns"))

    # The lockout is gone: a legitimate replace of P-01 now succeeds, proving the refused add
    # never planted the ambiguous second occurrence the pre-fix tool used to leave behind.
    ops_replace = write_ops(
        os.path.join(root, "case25b_replace_ops.json"),
        [{"op": "replace", "target": "P-01", "section": "Patterns", "entry": "legitimate update"}],
    )
    r_replace = run_ops(path_b, ops_replace)
    check(
        "case25: (b) a following legitimate replace of P-01 exits 0, not 11",
        r_replace.returncode == 0,
        r_replace.stdout + r_replace.stderr,
    )


def case_ops_target_grammar_well_formed(root):
    """Case 26 — WELL-FORMED TARGET STILL SUCCEEDS (positive control). VL-06's grammar check
    cannot be passing by rejecting every add — a target that is exactly the id `ENTRY_RE`
    already recognizes must still be accepted."""
    path = target(root, "case26")
    write_file(path, [("Patterns", [("P-01", "one")])])
    ops = write_ops(
        os.path.join(root, "case26_ops.json"),
        [{"op": "add", "target": "P-02", "section": "Patterns", "entry": "well formed"}],
    )
    r = run_ops(path, ops)
    check("case26: well-formed add exits 0", r.returncode == 0, r.stdout + r.stderr)
    content = open(path, encoding="utf-8").read()
    check("case26: rendered file contains the new entry", "P-02: well formed" in content, content)


def _assert_case27_ambiguous(root, stem, exit_check_name, message_check_name, texts, base_sections=None):
    """Shared AMBIGUOUS TARGET(11) shape for case27: write `entries_a`/`entries_b` as a
    duplicated `P-02` under `Patterns`, run apply, and assert `exit_check_name` (exit 11).
    `base_sections` present (existing destination): write it first, hash before, assert
    `message_check_name` carries the full section/id/reason shape, then assert the sha256 is
    unchanged after. `base_sections=None` (absent destination): no base file, no before-hash;
    assert `message_check_name` carries AMBIGUOUS TARGET, then assert nothing was created."""
    path = target(root, stem)
    before = None
    if base_sections is not None:
        write_file(path, base_sections)
        before = file_sha(path)
    entries_path = os.path.join(root, f"{stem}_entries.md")
    write_entries(entries_path, [("Patterns", [("P-02", texts[0]), ("P-02", texts[1])])])
    r = run_apply(path, entries_path)
    combined = r.stdout + r.stderr
    check(exit_check_name, r.returncode == 11, combined)
    if base_sections is not None:
        check(message_check_name, (
            "AMBIGUOUS TARGET" in combined
            and "section=Patterns" in combined
            and "id=P-02" in combined
            and "reason=" in combined
        ), combined)
        after = file_sha(path)
        check(f"{stem}: destination bytes unchanged", after == before, (before, after))
    else:
        check(message_check_name, "AMBIGUOUS TARGET" in combined, combined)
        check(f"{stem}: nothing created at the absent destination", os.path.exists(path) is False)


def case_duplicate_proposal_ids(root):
    """Case 27 — DUPLICATE PROPOSAL IDS (BUG-276). A proposal naming the same section+id twice
    is refused at the CLI boundary, exit 11, AMBIGUOUS TARGET, before any transform runs —
    covering the existing-destination path (a, b) and the absent-destination path (c), where
    cmd_apply's transform runs with base_bytes None."""
    # (a) different texts for the duplicated id, against an existing destination.
    _assert_case27_ambiguous(
        root, "case27a",
        "case27a: duplicate ids exit 11",
        "case27a: message carries AMBIGUOUS TARGET, section, id and reason",
        ("ALPHA", "BRAVO"),
        base_sections=[("Patterns", [("P-01", "one")])],
    )

    # (b) identical texts for the duplicated id, against an existing destination — refusal is
    # keyed on the duplicated id, not on divergent text.
    _assert_case27_ambiguous(
        root, "case27b",
        "case27b: identical duplicate ids exit 11",
        "case27b: message carries AMBIGUOUS TARGET, section, id and reason",
        ("ALPHA", "ALPHA"),
        base_sections=[("Patterns", [("P-01", "one")])],
    )

    # (c) absent destination — cmd_apply's transform runs with base_bytes None.
    _assert_case27_ambiguous(
        root, "case27c",
        "case27c: absent destination exits 11",
        "case27c: message carries AMBIGUOUS TARGET",
        ("ALPHA", "BRAVO"),
    )


# ---------------------------------------------------------------------------------------------
# FEAT-2225 T-01: member-ops, read-only receipt verification and replay, run as subprocesses
# against fixture git repositories under the suite's temp root. Never a live Expertise file.
# Each case is RED against the pre-change tool (the subcommands do not exist) and carries
# named one-mechanism mutants in the T-01 receipt.
# ---------------------------------------------------------------------------------------------
PERSONA = "harness-backend-dev"
FEATURE = "FEAT-9001-fixture"
FEATURE_REL = ".harness/harness/features/" + FEATURE
NOTES_REL = FEATURE_REL + "/notes"
CRAFT_REL = ".harness/expertise/%s.md" % PERSONA
REPO_REL = ".harness/harness/expertise/%s.md" % PERSONA
SECTIONS4 = ("Patterns", "Gotchas", "Outcomes", "Open")
BASE_DOC = [("Patterns", [("P-01", "alpha rule"), ("P-03", "gamma rule")]),
            ("Gotchas", [("G-01", "watch one")]), ("Outcomes", []), ("Open", [])]


def sh(cwd, *args):
    """Isolated git (git_support ENV: fixed identity, no global config to turn on signing)."""
    return git_out(cwd, *args, timeout=30)


def head(co):
    return sh(co, "rev-parse", "HEAD")


def commit_all(co, message):
    sh(co, "add", "-A")
    sh(co, "commit", "-q", "-m", message)
    return head(co)


def new_checkout(parent, name, craft=None):
    co = os.path.join(parent, name)
    os.makedirs(os.path.join(co, FEATURE_REL))
    with open(os.path.join(co, FEATURE_REL, "BRIEF.md"), "w", encoding="utf-8") as fh:
        fh.write("fixture\n")
    with open(os.path.join(co, ".gitignore"), "w", encoding="utf-8") as fh:
        fh.write("*.lock\n")
    if craft is not None:
        os.makedirs(os.path.join(co, ".harness", "expertise"))
        write_file(os.path.join(co, CRAFT_REL), craft)
    sh(co, "init", "-q", "-b", "main")
    commit_all(co, "base")
    return co


def clone(src, parent, name):
    dst = os.path.join(parent, name)
    git(parent, "clone", "-q", src, dst, timeout=30)
    return dst


def fetch_head(co, src):
    sh(co, "fetch", "-q", src, "HEAD")
    return sh(co, "rev-parse", "FETCH_HEAD")


def run_cli(*args, stdin=None):
    return subprocess.run([sys.executable, CLI, *args], input=stdin, capture_output=True, text=True, timeout=60)


def mop(verb, section, target, entry=None):
    d = {"op": verb, "target": target, "section": section, "why": "fixture"}
    if entry is not None:
        d["entry"] = entry
    return d


def claim(op, persona=PERSONA):
    return dict(op, persona=persona)


def member(co, runtime, ops, tier="craft", repo=None, parent="parent-1", persona=PERSONA, supersedes=(),
           base=None, feature=FEATURE, raw=None):
    args = ["member-ops", "--root", co, "--feature", feature, "--persona", persona, "--runtime-id", runtime,
            "--parent-id", parent, "--tier", tier, "--ops", "-"]
    if repo:
        args += ["--repository", repo]
    for ref in supersedes:
        args += ["--supersedes", ref]
    if base:
        args += ["--base", base]
    return run_cli(*args, stdin=json.dumps(ops) if raw is None else raw)


def verify(co, runtime, claimed, tier="craft", repo=None, parent="parent-1", persona=PERSONA, base=None):
    args = ["verify-receipt", "--root", co, "--feature", FEATURE, "--persona", persona, "--runtime-id", runtime,
            "--parent-id", parent, "--tier", tier, "--claimed", "-"]
    if repo:
        args += ["--repository", repo]
    if base:
        args += ["--base", base]
    return run_cli(*args, stdin=json.dumps(claimed))


def replay(co, base, check_only=False):
    args = ["replay", "--root", co, "--feature", FEATURE, "--base", base]
    return run_cli(*args + (["--check"] if check_only else []))


def jout(proc):
    try:
        return json.loads(proc.stdout)
    except ValueError:
        return {}


def out_of(proc):
    return "rc=%s stdout=%s stderr=%s" % (proc.returncode, proc.stdout[-600:], proc.stderr[-600:])


def read_rel(co, rel):
    with open(os.path.join(co, rel), encoding="utf-8") as fh:
        return fh.read()


def receipt_path(co, runtime):
    return os.path.join(co, NOTES_REL, "expertise-receipt-%s.json" % hashlib.sha256(runtime.encode()).hexdigest())


def load_receipt(co, runtime):
    with open(receipt_path(co, runtime), encoding="utf-8") as fh:
        return json.load(fh)


def snapshot(co, locks=False):
    snap = {}
    for base, dirs, files in os.walk(co):
        dirs[:] = [d for d in dirs if d != ".git"]
        for name in files:
            if name.endswith(".lock") and not locks:
                continue  # flock files are never removed (harness_merge D-02); not evidence of a write
            path = os.path.join(base, name)
            with open(path, "rb") as fh:
                snap[os.path.relpath(path, co)] = hashlib.sha256(fh.read()).hexdigest()
    return snap


def doc(sections):
    return render(sections, PERSONA)


def sha_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def zero_counts():
    return {name: 0 for name in SECTIONS4}


def read_rel_if_exists(co, rel):
    return read_rel(co, rel) if os.path.exists(os.path.join(co, rel)) else ""


def load_receipt_or_stub(co, runtime):
    return load_receipt(co, runtime) if os.path.exists(receipt_path(co, runtime)) else {"batches": [{}]}


def read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def overwrite(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def overwrite_bytes(path, data):
    with open(path, "wb") as fh:
        fh.write(data)


def _check_absent_craft_result(co, p, text):
    out = jout(p)
    check("member absent craft: exits 0", p.returncode == 0, out_of(p))
    check("member absent craft: canonical title plus the four sections",
          text == "# Expertise — harness-backend-dev\n## Patterns\n- P-01: first rule\n## Gotchas\n## Outcomes\n## Open\n", text)
    after = dict(zero_counts(), Patterns=1)
    check("member absent craft: before/after per-section counts returned",
          out.get("counts") == {"before": zero_counts(), "after": after}, out.get("counts"))
    check("member absent craft: outcomes returned", out.get("outcomes") == [["ADDED", "P-01"]], out.get("outcomes"))
    r3 = check_expertise(os.path.join(co, CRAFT_REL))
    check("member absent craft: result passes check-expertise", r3.returncode == 0, r3.stdout)


def _check_absent_receipt_header(co):
    rc = load_receipt_or_stub(co, "run-a")
    check("member receipt: persona feature runtime parent recorded",
          (rc.get("persona"), rc.get("feature"), rc.get("runtime_id"), rc.get("parent_id")) == (PERSONA, FEATURE, "run-a", "parent-1"), rc)
    b = rc["batches"][0]
    check("member receipt: checkout-relative destination", b.get("destination") == CRAFT_REL, b.get("destination"))


def _check_absent_receipt_content(co, text):
    b = load_receipt_or_stub(co, "run-a")["batches"][0]
    check("member receipt: exact accepted ops", b.get("ops") == [mop("add", "Patterns", "P-01", "first rule")], b.get("ops"))
    check("member receipt: absent original recorded as null",
          b.get("originals") == [{"section": "Patterns", "target": "P-01", "original": None}], b.get("originals"))
    check("member receipt: before/after content hashes",
          b.get("before_sha256") is None and b.get("after_sha256") == sha_text(text), b)


def _check_absent_receipt_identity(root, co, p):
    b = load_receipt_or_stub(co, "run-a")["batches"][0]
    out = jout(p)
    ident = b.get("id") or ""
    check("member receipt: content-derived 64-hex batch identity returned too",
          len(ident) == 64 and out.get("batch") == ident, (ident, out.get("batch")))
    co2 = new_checkout(root, "absent-twin")
    twin = jout(member(co2, "run-a", [mop("add", "Patterns", "P-01", "first rule")]))
    check("member receipt: identity is stable across identical fixtures", twin.get("batch") == ident, twin.get("batch"))


def _check_absent_repository(co):
    p2 = member(co, "run-b", [mop("add", "Gotchas", "G-01", "repo gotcha")], tier="repository", repo="harness")
    check("member absent repository: exits 0", p2.returncode == 0, out_of(p2))
    rtext = read_rel_if_exists(co, REPO_REL)
    check("member absent repository: canonical file", rtext == doc([("Patterns", []), ("Gotchas", [("G-01", "repo gotcha")]),
                                                                  ("Outcomes", []), ("Open", [])]), rtext)
    rc2 = load_receipt_or_stub(co, "run-b")
    check("member absent repository: receipt destination", rc2["batches"][0].get("destination") == REPO_REL, rc2)


def case_member_absent_files(root):
    co = new_checkout(root, "absent")
    p = member(co, "run-a", [mop("add", "Patterns", "P-01", "first rule")])
    text = read_rel_if_exists(co, CRAFT_REL)
    _check_absent_craft_result(co, p, text)
    _check_absent_receipt_header(co)
    _check_absent_receipt_content(co, text)
    _check_absent_receipt_identity(root, co, p)
    _check_absent_repository(co)


def _check_boundary_refusals(co, ops, before):
    refused = {
        "undeclared repository": member(co, "r1", ops, tier="repository", repo="nosuch"),
        "dot-dot repository": member(co, "r2", ops, tier="repository", repo=".."),
        "path repository": member(co, "r3", ops, tier="repository", repo="harness/x"),
        "repository tier without segment": member(co, "r4", ops, tier="repository"),
        "craft tier with a segment": member(co, "r5", ops, tier="craft", repo="harness"),
        "non harness persona": member(co, "r6", ops, persona="reviewer"),
        "persona traversal": member(co, "r7", ops, persona="harness-../x"),
        "unknown feature": member(co, "r8", ops, feature="FEAT-0-nothing"),
        "feature traversal": member(co, "r9", ops, feature="../x"),
    }
    for name, proc in refused.items():
        check("member boundary: %s refused with 9" % name, proc.returncode == 9, out_of(proc))
    check("member boundary: refusals wrote nothing", snapshot(co) == before, "tree changed")


def _check_boundary_symlinked_segment(co, outside, ops):
    os.symlink(outside, os.path.join(co, ".harness", "linked"))
    p = member(co, "r10", ops, tier="repository", repo="linked")
    check("member boundary: symlinked repository segment refused with 9", p.returncode == 9, out_of(p))


def _check_boundary_symlinked_craft(root, outside, ops):
    sym = new_checkout(root, "bounds-sym")
    os.symlink(outside, os.path.join(sym, ".harness", "expertise"))
    p = member(sym, "r11", ops)
    check("member boundary: symlinked craft tier (global/control-plane stand-in) refused with 9", p.returncode == 9, out_of(p))
    return sym


def _check_boundary_symlink_onto_control(root, ops):
    ctl = os.path.join(root, "bounds-control", ".harness", "expertise")
    os.makedirs(ctl)
    inside = new_checkout(root, "bounds-ctl")
    os.symlink(ctl, os.path.join(inside, ".harness", "expertise"))
    p = member(inside, "r12", ops)
    check("member boundary: symlink onto another tree's legal-looking .harness/expertise refused with 9", p.returncode == 9, out_of(p))
    return inside, ctl


def _check_boundary_symlinked_legal_tail(root, inside, ops):
    ctl_seg = os.path.join(root, "bounds-control2", ".harness", "linked2", "expertise")
    os.makedirs(ctl_seg)
    os.symlink(os.path.join(root, "bounds-control2", ".harness", "linked2"), os.path.join(inside, ".harness", "linked2"))
    p = member(inside, "r13", ops, tier="repository", repo="linked2")
    check("member boundary: symlinked repository segment with a legal-looking tail refused with 9", p.returncode == 9, out_of(p))
    return ctl_seg


def _check_boundary_nothing_landed(outside, ctl, ctl_seg, sym):
    check("member boundary: nothing landed in the symlink targets", os.listdir(ctl) == [] and os.listdir(ctl_seg) == [], (os.listdir(ctl), os.listdir(ctl_seg)))
    check("member boundary: nothing landed outside the checkout", os.listdir(outside) == [], os.listdir(outside))
    check("member boundary: no receipt after refusals", not os.path.exists(receipt_path(sym, "r11")), None)


def case_member_destination_boundaries(root):
    co = new_checkout(root, "bounds", craft=BASE_DOC)
    outside = os.path.join(root, "bounds-outside")
    os.makedirs(outside)
    before = snapshot(co)
    ops = [mop("add", "Patterns", "P-09", "nine")]
    _check_boundary_refusals(co, ops, before)
    _check_boundary_symlinked_segment(co, outside, ops)
    sym = _check_boundary_symlinked_craft(root, outside, ops)
    inside, ctl = _check_boundary_symlink_onto_control(root, ops)
    ctl_seg = _check_boundary_symlinked_legal_tail(root, inside, ops)
    _check_boundary_nothing_landed(outside, ctl, ctl_seg, sym)


def _check_strict_op_keys(co, good, before):
    bad = {"persona key": dict(good, persona=PERSONA), "state key": dict(good, state="applied"),
           "unknown key": dict(good, extra=1)}
    for name, op_obj in bad.items():
        p = member(co, "run-x", [op_obj])
        check("member strict: %s rejected with 12" % name, p.returncode == 12, out_of(p))
    check("member strict: rejects left every byte alone", snapshot(co) == before, None)


def _check_strict_payloads(co, path, good):
    p = run_cli("ops", "--file", path, "--ops", "-", stdin=json.dumps([dict(good, persona=PERSONA)]))
    check("ops regression: persona is still not a low-level op key", p.returncode == 12, out_of(p))
    p = member(co, "run-x", [])
    check("member strict: empty list without supersedes refused with 12", p.returncode == 12, out_of(p))
    p = member(co, "run-x", None, raw="{not json")
    check("member strict: undecodable JSON refused with 12", p.returncode == 12, out_of(p))


def _check_plain_paths(root, co, path, good):
    p = run_cli("ops", "--file", path, "--ops", "-", stdin=json.dumps([good]))
    check("ops regression: plain ops still applies", p.returncode == 0 and "ADDED P-09" in p.stdout, out_of(p))
    check("ops regression: plain ops writes no receipt", not os.path.exists(os.path.join(co, NOTES_REL)), None)
    entries = os.path.join(root, "strict-entries.md")
    write_entries(entries, [("Patterns", [("P-10", "ten")])])
    p = run_apply(path, entries)
    check("apply regression: union apply still works", p.returncode == 0 and "ADDED P-10" in p.stdout, out_of(p))


def case_member_strict_ops(root):
    co = new_checkout(root, "strict", craft=BASE_DOC)
    path = os.path.join(co, CRAFT_REL)
    before = snapshot(co)
    good = mop("add", "Patterns", "P-09", "nine")
    _check_strict_op_keys(co, good, before)
    _check_strict_payloads(co, path, good)
    _check_plain_paths(root, co, path, good)


def _check_batches_receipt(co, p1, p2):
    check("batches: both calls succeed", p1.returncode == 0 and p2.returncode == 0, out_of(p1) + out_of(p2))
    rc = load_receipt(co, "run-q")
    b1, b2 = rc["batches"][0], rc["batches"][1]
    check("batches: ordered 1 then 2", (b1["seq"], b2["seq"]) == (1, 2) and len(rc["batches"]) == 2, rc)
    check("batches: distinct content-derived identities", b1["id"] != b2["id"], None)
    check("batches: second batch originals are the first batch's text and absence",
          b2["originals"] == [{"section": "Patterns", "target": "P-02", "original": "first take"},
                              {"section": "Gotchas", "target": "G-02", "original": None}], b2["originals"])
    check("batches: second batch starts from the first batch's result", b2["before_sha256"] == b1["after_sha256"], None)
    check("batches: ops recorded exactly in call order",
          b2["ops"] == [mop("replace", "Patterns", "P-02", "second take"), mop("add", "Gotchas", "G-02", "new gotcha")], b2["ops"])


def _check_batches_counts(p2):
    out2 = jout(p2)
    check("batches: counts reflect the second call only",
          out2.get("counts") == {"before": dict(zero_counts(), Patterns=3, Gotchas=1), "after": dict(zero_counts(), Patterns=3, Gotchas=2)},
          out2.get("counts"))


def _check_batches_identity_refusals(co):
    snap = snapshot(co)
    p3 = member(co, "run-q", [mop("add", "Patterns", "P-07", "seven")], parent="other-parent")
    check("batches: a different parent for the same runtime id is refused with 15", p3.returncode == 15, out_of(p3))
    other = member(co, "run-q", [mop("add", "Patterns", "P-07", "seven")], persona="harness-other")
    check("batches: a different persona for the same runtime id is refused with 15", other.returncode == 15, out_of(other))
    check("batches: those refusals changed nothing", snapshot(co) == snap, None)


def case_member_batches_append(root):
    co = new_checkout(root, "seq", craft=BASE_DOC)
    p1 = member(co, "run-q", [mop("add", "Patterns", "P-02", "first take")])
    p2 = member(co, "run-q", [mop("replace", "Patterns", "P-02", "second take"), mop("add", "Gotchas", "G-02", "new gotcha")])
    _check_batches_receipt(co, p1, p2)
    _check_batches_counts(p2)
    _check_batches_identity_refusals(co)


def _check_refusal_ops(co):
    p = member(co, "run-ok", [mop("replace", "Patterns", "P-99", "x")])
    check("refusal: missing target refused with 10", p.returncode == 10, out_of(p))
    p = member(co, "run-ok", [mop("add", "Patterns", "P-08", "fine"), mop("replace", "Patterns", "P-99", "x")])
    check("refusal: a multi-op batch with one bad op applies nothing", p.returncode == 10, out_of(p))
    p = member(co, "run-new", [mop("add", "Patterns", "P-08", "tracks FEAT-12 work")])
    check("refusal: candidate failing check-expertise refused with 14", p.returncode == 14, out_of(p))


def _check_refusal_untouched(co, snap):
    check("refusal: target bytes, receipts and notes unchanged, no applied batch", snapshot(co) == snap, None)
    check("refusal: the refused runtime has no receipt", not os.path.exists(receipt_path(co, "run-new")), None)


def _check_refusal_cap(root):
    capped = new_checkout(root, "refuse-cap", craft=[("Patterns", []), ("Gotchas", []), ("Outcomes", []),
                                                      ("Open", [("Q-%02d" % n, "open") for n in range(1, 6)])])
    snap = snapshot(capped)
    p = member(capped, "run-cap", [mop("add", "Open", "Q-06", "overflow")])
    check("refusal: cap overflow refused with 8", p.returncode == 8, out_of(p))
    check("refusal: cap overflow preserved every byte", snapshot(capped) == snap, None)


def case_member_refusal_preserves(root):
    co = new_checkout(root, "refuse", craft=BASE_DOC)
    member(co, "run-ok", [mop("add", "Patterns", "P-02", "two")])
    snap = snapshot(co)
    _check_refusal_ops(co)
    _check_refusal_untouched(co, snap)
    _check_refusal_cap(root)


def case_member_receipt_failure_fails_closed(root):
    co = new_checkout(root, "rfail", craft=BASE_DOC)
    with open(os.path.join(co, NOTES_REL), "w", encoding="utf-8") as fh:
        fh.write("a file where the notes directory must be\n")
    ops = [mop("add", "Patterns", "P-02", "two")]
    p = member(co, "run-f", ops)
    check("receipt failure: call fails with 15", p.returncode == 15 and "RECEIPT" in p.stdout, out_of(p))
    check("receipt failure: success was not published", jout(p) == {}, p.stdout)
    check("receipt failure: the target did persist", "- P-02: two" in read_rel(co, CRAFT_REL), None)
    os.remove(os.path.join(co, NOTES_REL))
    v = verify(co, "run-f", [claim(ops[0])])
    check("receipt failure: verification fails closed on the missing receipt", v.returncode == 15 and "MISSING RECEIPT" in v.stdout, out_of(v))
    r = replay(co, head(co))
    check("receipt failure: replay fails closed on the unreceipted change", r.returncode == 15 and "UNRECEIPTED" in r.stdout, out_of(r))


def _verify_fixture(root):
    co = new_checkout(root, "verify", craft=BASE_DOC)
    add2 = mop("add", "Patterns", "P-02", "v1 text")
    rep2 = mop("replace", "Patterns", "P-02", "v2 text")
    member(co, "run-v", [add2])
    member(co, "run-v", [rep2, mop("add", "Gotchas", "G-02", "kept gotcha")])
    return co, add2, rep2


def _check_verify_final_effect(co, add2, rep2):
    snap = snapshot(co, locks=True)
    v = verify(co, "run-v", [claim(add2), claim(rep2), claim(mop("add", "Gotchas", "G-02", "kept gotcha"))])
    vo = jout(v)
    check("verify: ordered active batches verify on their FINAL effect (superseded intermediate absent)",
          v.returncode == 0 and vo.get("verified") is True, out_of(v))
    check("verify: reports measured per-section counts", vo.get("counts", {}).get("Patterns") == 3, vo.get("counts"))
    check("verify: read-only (no file, lock or receipt changed or added)", snapshot(co, locks=True) == snap, None)


def _verify_refusal_cases(add2):
    return {
        "wrong runtime": dict(runtime="run-none", claimed=[claim(add2)]),
        "wrong persona": dict(runtime="run-v", claimed=[claim(add2, "harness-other")], persona="harness-other"),
        "wrong parent": dict(runtime="run-v", claimed=[claim(add2)], parent="elsewhere"),
        "wrong destination": dict(runtime="run-v", claimed=[claim(add2)], tier="repository", repo="harness"),
        "op not exactly recorded": dict(runtime="run-v", claimed=[claim(dict(add2, why="different why"))]),
        "fabricated op": dict(runtime="run-v", claimed=[claim(mop("add", "Patterns", "P-77", "never applied"))]),
        "persona missing from item": dict(runtime="run-v", claimed=[add2]),
    }


def _check_verify_refusals(co, add2):
    for label, args in _verify_refusal_cases(add2).items():
        runtime = args.pop("runtime")
        claimed = args.pop("claimed")
        v = verify(co, runtime, claimed, **args)
        check("verify: %s refused with 15" % label, v.returncode == 15, out_of(v))


def _check_verify_tampered_file(co, add2, rep2):
    path = os.path.join(co, CRAFT_REL)
    good = read_rel(co, CRAFT_REL)
    overwrite(path, good.replace("v2 text", "v1 text"))
    v = verify(co, "run-v", [claim(add2), claim(rep2)])
    check("verify: file reverted to the superseded intermediate is a mismatch", v.returncode == 15 and "MISMATCH" in v.stdout, out_of(v))
    overwrite(path, good.replace("- P-02: v2 text\n", ""))
    v = verify(co, "run-v", [claim(rep2)])
    check("verify: entry removed after the receipt is a mismatch", v.returncode == 15, out_of(v))
    overwrite(path, good)


def _check_verify_preserved_add(co):
    # preserved identical add versus invented application
    keep = mop("add", "Patterns", "P-01", "alpha rule")
    p = member(co, "run-keep", [keep])
    check("verify: identical existing add is PRESERVED", p.returncode == 0 and jout(p).get("outcomes") == [["PRESERVED", "P-01"]], out_of(p))
    v = verify(co, "run-keep", [claim(keep)])
    check("verify: preserved add verifies and is listed as preserved",
          v.returncode == 0 and jout(v).get("preserved") == [["Patterns", "P-01"]], out_of(v))


def _check_verify_invented_application(co):
    forged = load_receipt(co, "run-keep")
    forged["batches"][0]["ops"] = [mop("add", "Patterns", "P-55", "invented")]
    overwrite(receipt_path(co, "run-keep"), json.dumps(forged))
    v = verify(co, "run-keep", [claim(mop("add", "Patterns", "P-55", "invented"))])
    check("verify: an invented application (receipt edited, file never changed) is refused", v.returncode == 15, out_of(v))


def case_member_verify(root):
    co, add2, rep2 = _verify_fixture(root)
    _check_verify_final_effect(co, add2, rep2)
    _check_verify_refusals(co, add2)
    _check_verify_tampered_file(co, add2, rep2)
    _check_verify_preserved_add(co)
    _check_verify_invented_application(co)


# FEAT-2225 F2 — verify-receipt checks the COMPLETE destination, not only the recorded op keys.
GBASE_DOC = [("Patterns", []), ("Gotchas", [("G-01", "watch one"), ("G-02", "watch two")]),
             ("Outcomes", []), ("Open", [])]
FULL_ADD = mop("add", "Patterns", "P-01", "receipted rule")


def _complete_fixture(root, name, before=None):
    co = new_checkout(root, name, craft=GBASE_DOC)
    if before:
        overwrite(os.path.join(co, CRAFT_REL), read_rel(co, CRAFT_REL).replace(*before))
    member(co, "run-full", [FULL_ADD])
    return co


def _verify_full(co):
    return verify(co, "run-full", [claim(FULL_ADD)])


def _refuses_unreceipted(name, v):
    check(name, v.returncode == 15 and "UNRECEIPTED CONTENT" in v.stdout, out_of(v))


def _check_tamper_after(co, old, new, name):
    path = os.path.join(co, CRAFT_REL)
    good = read_rel(co, CRAFT_REL)
    overwrite(path, good.replace(old, new))
    _refuses_unreceipted(name, _verify_full(co))
    overwrite(path, good)


def _verifies(name, co):
    v = _verify_full(co)
    check(name, v.returncode == 0, out_of(v))


def case_verify_complete_destination(root):
    co = _complete_fixture(root, "vfull")
    _verifies("verify full: a clean receipted add verifies", co)
    _check_tamper_after(co, "- G-01: watch one\n", "",
                        "verify full: receipted P-01 add plus unreceipted deletion of pre-existing G-01 refuses")
    _check_tamper_after(co, "watch two", "edited by hand",
                        "verify full: receipted add plus unreceipted edit of another entry refuses")
    _verifies("verify full: restored file verifies again", co)
    early = _complete_fixture(root, "vfull-early", before=("- G-01: watch one\n", ""))
    _refuses_unreceipted("verify full: unreceipted G-01 deletion BEFORE the receipted add refuses", _verify_full(early))


# FEAT-2225 c2 — the write chain anchors on the authorized base (merge-base with the default
# branch, or with --base), never on the feature's own HEAD.
LINEAGES = (("member", PERSONA, "lead-run"), ("lead", "harness-product-lead", "orch-run"))


def _feature_branch_fixture(root, name, persona, tamper):
    """Baseline on main, then a feature branch; `tamper` deletes G-01 in a COMMIT before the
    first receipted application."""
    co = new_checkout(root, name)
    rel = ".harness/expertise/%s.md" % persona
    os.makedirs(os.path.join(co, ".harness", "expertise"), exist_ok=True)
    write_file(os.path.join(co, rel), GBASE_DOC)
    main = commit_all(co, "baseline")
    sh(co, "checkout", "-q", "-b", "feat/fixture")
    if tamper:
        overwrite(os.path.join(co, rel), read_rel(co, rel).replace("- G-01: watch one\n", ""))
        commit_all(co, "unreceipted edit")
    return co, main


def _check_committed_tamper(root, label, persona, parent):
    co, main = _feature_branch_fixture(root, "ctamper-" + label, persona, tamper=True)
    p = member(co, "run-" + label, [FULL_ADD], persona=persona, parent=parent)
    check("verify c2 %s: the receipted application itself lands" % label, p.returncode == 0, out_of(p))
    for base in (None, main):
        v = verify(co, "run-" + label, [claim(FULL_ADD, persona)], persona=persona, parent=parent, base=base)
        _refuses_unreceipted("verify c2 %s: unreceipted G-01 deletion COMMITTED before the first receipted "
                             "application refuses (base=%s)" % (label, "default" if base is None else "--base"), v)


def _check_feature_branch_clean(root, label, persona, parent):
    co, main = _feature_branch_fixture(root, "cclean-" + label, persona, tamper=False)
    member(co, "run-" + label, [FULL_ADD], persona=persona, parent=parent)
    commit_all(co, "receipted application committed")
    for base in (None, main):
        v = verify(co, "run-" + label, [claim(FULL_ADD, persona)], persona=persona, parent=parent, base=base)
        check("verify c2 %s: a committed receipted application on a feature branch verifies (base=%s)"
              % (label, "default" if base is None else "--base"), v.returncode == 0, out_of(v))


def _check_no_authorized_base(root):
    co, _ = _feature_branch_fixture(root, "cnobase", PERSONA, tamper=False)
    member(co, "run-nb", [FULL_ADD])
    sh(co, "branch", "-m", "main", "trunk")
    v = verify(co, "run-nb", [claim(FULL_ADD)])
    check("verify c2: no default branch and no --base refuses with 15, NO AUTHORIZED BASE",
          v.returncode == 15 and v.stdout.startswith("NO AUTHORIZED BASE"), out_of(v))


def _check_unchained_active_batch(root):
    """N2: run-f's add was undone by hand and run-a re-added the identical entry. The file and the
    final effect agree, the chain reaches the base through run-a, and run-f's batch is OFF it."""
    co = new_checkout(root, "cunchained", craft=GBASE_DOC)
    path = os.path.join(co, CRAFT_REL)
    baseline = read_bytes(path)
    member(co, "run-f", [FULL_ADD])
    overwrite_bytes(path, baseline)
    member(co, "run-a", [FULL_ADD])
    check("verify c2: the runtime whose write is on the chain verifies", verify(co, "run-a", [claim(FULL_ADD)]).returncode == 0, None)
    v = verify(co, "run-f", [claim(FULL_ADD)])
    check("verify c2: an active batch off the write chain refuses and is named (unchained-batch guard)",
          v.returncode == 15 and "active batches off the write chain" in v.stdout, out_of(v))


def case_verify_authorized_anchor(root):
    for label, persona, parent in LINEAGES:
        _check_committed_tamper(root, label, persona, parent)
        _check_feature_branch_clean(root, label, persona, parent)
    _check_no_authorized_base(root)
    _check_unchained_active_batch(root)


def _local_receipts_fixture(root):
    """FEAT-2641 D-04: receipts are local working files, ignored and never committed."""
    co = new_checkout(root, "sel", craft=BASE_DOC)
    with open(os.path.join(co, ".gitignore"), "w", encoding="utf-8") as fh:
        fh.write("*.lock\n.harness/*/features/*/notes/\n")
    base = commit_all(co, "ignore working files")
    member(co, "run-one", [mop("add", "Patterns", "P-05", "fresh rule")])
    member(co, "run-two", [mop("add", "Gotchas", "G-02", "watch two")], parent="parent-2")
    commit_all(co, "distill")
    return co, base


def case_replay_local_receipts(root):
    co, base = _local_receipts_fixture(root)
    tracked = sh(co, "ls-files", "--", NOTES_REL)
    check("local receipts: member-ops receipts are never committed", tracked == "", tracked)
    snap = snapshot(co, locks=True)
    r = replay(co, base, check_only=True)
    out = jout(r)
    check("local receipts: replay --check reports replayed true", r.returncode == 0 and out.get("replayed") is True,
          out_of(r))
    paths = sorted(x.get("path") for x in out.get("receipts", []))
    want = sorted(NOTES_REL + "/expertise-receipt-%s.json" % hashlib.sha256(rt).hexdigest()
                  for rt in (b"run-one", b"run-two"))
    check("local receipts: both uncommitted receipts are read", paths == want, paths)
    check("replay --check is read-only", snapshot(co, locks=True) == snap, None)
    check("replay --check reports the checkout file already equals the replay", out.get("files", [{}])[0].get("up_to_date") is True, out.get("files"))


def case_replay_base_tracked_receipt(root):
    """SC-10 (validate c0 must_fix 9): no base-tree exclusion. A receipt the base already tracks
    (a branch cut before DEC-262 untracked them) is read like any other local receipt; restoring
    the old base exclusion drops it and the replay no longer reproduces the checkout."""
    co = new_checkout(root, "sel-base", craft=BASE_DOC)
    base0 = head(co)
    member(co, "run-one", [mop("add", "Patterns", "P-05", "fresh rule")])
    sh(co, "add", "--", receipt_path(co, "run-one"))
    sh(co, "commit", "-q", "-m", "receipt tracked at base")
    base = head(co)
    member(co, "run-two", [mop("add", "Gotchas", "G-02", "watch two")], parent="parent-2")
    commit_all(co, "distill")
    tracked = sh(co, "ls-tree", "-r", "--name-only", base, "--", NOTES_REL)
    check("base-tracked receipt: the base tracks run-one's receipt and its Expertise file is unchanged",
          tracked.endswith(os.path.basename(receipt_path(co, "run-one")))
          and sh(co, "diff", "--name-only", base0, base, "--", CRAFT_REL) == "", tracked)
    r = replay(co, base, check_only=True)
    out = jout(r)
    paths = sorted(x.get("path") for x in out.get("receipts", []))
    want = sorted(NOTES_REL + "/expertise-receipt-%s.json" % hashlib.sha256(rt).hexdigest()
                  for rt in (b"run-one", b"run-two"))
    check("base-tracked receipt: replay --check reads the base-tracked receipt with the local one",
          r.returncode == 0 and out.get("replayed") is True and paths == want, out_of(r))
    check("base-tracked receipt: the replay reproduces the checkout's Expertise file",
          (out.get("files") or [{}])[0].get("up_to_date") is True, out.get("files"))


def _collision_fixture(root):
    origin = new_checkout(root, "o-col", craft=BASE_DOC)
    base0 = head(origin)
    a, b = clone(origin, root, "a-col"), clone(origin, root, "b-col")
    member(a, "run-a", [mop("add", "Patterns", "P-05", "from A"), mop("add", "Patterns", "P-06", "shared text")])
    member(b, "run-b", [mop("add", "Patterns", "P-05", "from B"), mop("add", "Patterns", "P-06", "shared text")])
    member(b, "run-b", [mop("replace", "Patterns", "P-05", "from B v2")])
    commit_all(a, "A merges")
    return base0, a, b


def _collision_first_replay(a, b, base0):
    ra = replay(a, base0)
    check("replay collision: the first worktree replays cleanly onto its own base", ra.returncode == 0, out_of(ra))
    return fetch_head(b, a)


def _check_collision_dry_run(b, base1):
    mine = read_rel(b, CRAFT_REL)
    r = replay(b, base1, check_only=True)
    out = jout(r)
    first_batch = load_receipt(b, "run-b")["batches"][0]["id"]
    check("replay collision: --check succeeds", r.returncode == 0, out_of(r))
    want_map = [{"persona": PERSONA, "runtime_id": "run-b", "destination": CRAFT_REL, "section": "Patterns",
                 "original_id": "P-05", "replayed_id": "P-02", "batch": first_batch}]
    check("replay collision: original-to-replayed id mapping (first free positive id)", out.get("mappings") == want_map, out.get("mappings"))
    check("replay collision: --check left the file alone and says it is stale",
          read_rel(b, CRAFT_REL) == mine and out["files"][0]["up_to_date"] is False, out.get("files"))
    return want_map


def _check_collision_write(b, base1):
    r = replay(b, base1)
    check("replay collision: write run succeeds", r.returncode == 0, out_of(r))
    expected = doc([("Patterns", [("P-01", "alpha rule"), ("P-03", "gamma rule"), ("P-05", "from A"),
                                  ("P-06", "shared text"), ("P-02", "from B v2")]),
                    ("Gotchas", [("G-01", "watch one")]), ("Outcomes", []), ("Open", [])])
    check("replay collision: both entries survive, identical add preserved, later reference remapped",
          read_rel(b, CRAFT_REL) == expected, read_rel(b, CRAFT_REL))
    blob = sh(b, "show", "%s:%s" % (base1, CRAFT_REL))
    f = jout(r)["files"][0]
    check("replay collision: base and result hash evidence",
          f.get("base_sha256") == sha_text(blob + "\n") and f.get("result_sha256") == sha_text(expected), f)
    return expected


def _check_collision_repeat(b, base1, want_map, expected):
    again = read_rel(b, CRAFT_REL)
    r2 = replay(b, base1)
    check("replay repeat: second replay rebuilds from the base, not from its own output",
          r2.returncode == 0 and read_rel(b, CRAFT_REL) == again == expected and jout(r2)["mappings"] == want_map, out_of(r2))
    check("replay repeat: second replay finds the file already up to date", jout(r2)["files"][0]["up_to_date"] is True, jout(r2))
    r3 = check_expertise(os.path.join(b, CRAFT_REL))
    check("replay collision: result passes check-expertise", r3.returncode == 0, r3.stdout)


def case_replay_collision_and_repeat(root):
    base0, a, b = _collision_fixture(root)
    base1 = _collision_first_replay(a, b, base0)
    want_map = _check_collision_dry_run(b, base1)
    expected = _check_collision_write(b, base1)
    _check_collision_repeat(b, base1, want_map, expected)


def _independent_fixture(root):
    origin = new_checkout(root, "o-ind", craft=BASE_DOC)
    base0 = head(origin)
    x, y = clone(origin, root, "x-ind"), clone(origin, root, "y-ind")
    member(x, "run-x", [mop("replace", "Patterns", "P-01", "new one")])
    member(y, "run-y", [mop("replace", "Patterns", "P-01", "new one")])
    shutil.copy(receipt_path(y, "run-y"), receipt_path(x, "run-y"))
    return origin, base0, x


def _check_independent_replace_pair(x, base0):
    snap = snapshot(x)
    r = replay(x, base0)
    out = jout(r)
    reasons = [q.get("reason", "") for q in out.get("refusals", [])]
    check("replay independent: two callers replacing one base entry refuse (identical text not hidden)",
          r.returncode == 13 and any(s.startswith("INDEPENDENT") for s in reasons), out_of(r))
    both = out.get("refusals", [{}])[0].get("runtimes")
    check("replay independent: refusal names both runs", both == ["run-x", "run-y"], both)
    check("replay independent: refused file stays byte-identical", snapshot(x) == snap, None)


def _check_independent_replace_drop(root, origin, x, base0):
    z = clone(origin, root, "z-ind")
    member(z, "run-z", [mop("drop", "Patterns", "P-01")])
    shutil.copy(receipt_path(z, "run-z"), receipt_path(x, "run-z"))
    os.remove(receipt_path(x, "run-y"))
    r = replay(x, base0)
    check("replay independent: replace versus drop of one entry refuses too",
          r.returncode == 13 and any(q["reason"].startswith("INDEPENDENT") for q in jout(r).get("refusals", [])), out_of(r))


def case_replay_independent_callers(root):
    origin, base0, x = _independent_fixture(root)
    _check_independent_replace_pair(x, base0)
    _check_independent_replace_drop(root, origin, x, base0)


def _changed_main_fixture(root):
    origin = new_checkout(root, "o-chg", craft=BASE_DOC)
    x = clone(origin, root, "x-chg")
    member(x, "run-c", [mop("replace", "Patterns", "P-03", "mine")])
    member(x, "run-d", [mop("drop", "Patterns", "P-01")])
    z = clone(origin, root, "z-chg")
    write_file(os.path.join(z, CRAFT_REL), [("Patterns", [("P-03", "changed upstream")]), ("Gotchas", [("G-01", "watch one")]),
                                            ("Outcomes", []), ("Open", [])])
    base_z = commit_all(z, "main moved")
    sh(x, "fetch", "-q", z, "HEAD")
    return x, base_z


def _check_changed_replace_refusal(x, ref):
    c_id = load_receipt(x, "run-c")["batches"][0]["id"]
    check("replay changed main: replace refusal names persona run destination section id batch",
          ref.get("P-03", {}).get("persona") == PERSONA and ref["P-03"].get("runtimes") == ["run-c"]
          and ref["P-03"].get("destination") == CRAFT_REL and ref["P-03"].get("section") == "Patterns"
          and ref["P-03"].get("batches") == [c_id] and ref["P-03"].get("reason", "").startswith("CHANGED"), ref.get("P-03"))


def _check_changed_main(x, base_z):
    snap = snapshot(x)
    r = replay(x, base_z)
    out = jout(r)
    check("replay changed main: replace/drop over a changed or vanished entry refuse with 13", r.returncode == 13, out_of(r))
    ref = {q.get("target"): q for q in out.get("refusals", [])}
    _check_changed_replace_refusal(x, ref)
    check("replay changed main: vanished drop target is DISAPPEARED",
          ref.get("P-01", {}).get("reason", "").startswith("DISAPPEARED"), ref.get("P-01"))
    check("replay changed main: refused file byte-identical", snapshot(x) == snap, None)


def _cap_fixture(root):
    base_open = [("Patterns", []), ("Gotchas", []), ("Outcomes", []), ("Open", [("Q-%02d" % n, "open") for n in range(1, 5)])]
    o2 = new_checkout(root, "o-cap", craft=base_open)
    base_o = head(o2)
    x2 = clone(o2, root, "x-cap")
    member(x2, "run-cap", [mop("add", "Open", "Q-05", "fifth")])
    r = replay(x2, base_o, check_only=True)
    check("replay cap: exactly at the cap succeeds", r.returncode == 0, out_of(r))
    return o2, x2


def _check_cap_overflow(root, o2, x2):
    z2 = clone(o2, root, "z-cap")
    write_file(os.path.join(z2, CRAFT_REL), [("Patterns", []), ("Gotchas", []), ("Outcomes", []),
                                             ("Open", [("Q-%02d" % n, "open") for n in range(1, 5)] + [("Q-06", "upstream")])])
    base_c = commit_all(z2, "main fills Open")
    sh(x2, "fetch", "-q", z2, "HEAD")
    snap = snapshot(x2)
    r = replay(x2, base_c)
    check("replay cap: overflow refuses rather than truncates",
          r.returncode == 13 and any("CAP EXCEEDED" in q.get("reason", "") for q in jout(r).get("refusals", [])), out_of(r))
    check("replay cap: refused file byte-identical", snapshot(x2) == snap, None)


def case_replay_changed_main_and_cap(root):
    x, base_z = _changed_main_fixture(root)
    _check_changed_main(x, base_z)
    o2, x2 = _cap_fixture(root)
    _check_cap_overflow(root, o2, x2)


def _supersession_fixture(root):
    origin = new_checkout(root, "o-sup", craft=BASE_DOC)
    x = clone(origin, root, "x-sup")
    member(x, "run-c", [mop("replace", "Patterns", "P-03", "mine")])
    old = load_receipt(x, "run-c")["batches"][0]["id"]
    z = clone(origin, root, "z-sup")
    write_file(os.path.join(z, CRAFT_REL), [("Patterns", [("P-01", "alpha rule"), ("P-03", "changed upstream")]),
                                            ("Gotchas", [("G-01", "watch one")]), ("Outcomes", []), ("Open", [])])
    base_z = commit_all(z, "main moved")
    sh(x, "fetch", "-q", z, "HEAD")
    return origin, x, old, z, base_z


def _check_supersession_original_refused(x, base_z, old):
    r = replay(x, base_z)
    check("supersession: the original judgment is refused first", r.returncode == 13 and jout(r)["refusals"][0]["batches"] == [old], out_of(r))


def _check_supersession_authority(x, base_z, old):
    other = member(x, "run-o", [mop("add", "Patterns", "P-01", "o")], persona="harness-other", supersedes=[old], base=base_z)
    check("supersession: another persona cannot retire the batch", other.returncode == 15 and "UNAUTHORIZED" in other.stdout, out_of(other))
    crossed = member(x, "run-r", [mop("add", "Patterns", "P-09", "n")], tier="repository", repo="harness", supersedes=[old], base=base_z)
    check("supersession: another destination cannot retire the batch", crossed.returncode == 15, out_of(crossed))


def _check_supersession_references(x, base_z, old, new_op):
    missing = member(x, "run-m", [new_op], supersedes=["a" * 64], base=base_z)
    check("supersession: unknown batch reference refused with 15", missing.returncode == 15 and "MISSING" in missing.stdout, out_of(missing))
    nobase = member(x, "run-n", [new_op], supersedes=[old])
    check("supersession: a reference needs the explicit main base (12)", nobase.returncode == 12, out_of(nobase))
    malformed = member(x, "run-n", [new_op], supersedes=["not-a-batch-id"], base=base_z)
    check("supersession: malformed reference refused with 12", malformed.returncode == 12, out_of(malformed))
    failed = member(x, "run-bad", [mop("replace", "Patterns", "P-77", "x")], supersedes=[old], base=base_z)
    check("supersession: failing replacement ops refuse with 10", failed.returncode == 10, out_of(failed))


def _check_supersession_nothing_retired(x, base_z, snap):
    check("supersession: all refusals wrote nothing and retired nothing", snapshot(x) == snap, None)
    check("supersession: failed replacement leaves the old batch active (replay still refuses)", replay(x, base_z).returncode == 13, None)


def _check_supersession_replacement(x, base_z, old, new_op, old_bytes):
    p = member(x, "run-c2", [new_op], parent="parent-2", supersedes=[old], base=base_z)
    check("supersession: same persona re-dispatched child replaces the refused batch", p.returncode == 0 and jout(p).get("supersedes") == [old], out_of(p))
    expected = doc([("Patterns", [("P-01", "alpha rule"), ("P-03", "mine revised")]), ("Gotchas", [("G-01", "watch one")]),
                    ("Outcomes", []), ("Open", [])])
    check("supersession: file is the main reconstruction plus the new ops", read_rel(x, CRAFT_REL) == expected, read_rel(x, CRAFT_REL))
    check("supersession: historical receipt is immutable", read_bytes(receipt_path(x, "run-c")) == old_bytes, None)
    check("supersession: replacement receipt records the exact reference",
          load_receipt(x, "run-c2")["batches"][0]["supersedes"] == [old], None)
    return expected


def _check_supersession_replay_idempotent(x, base_z, expected):
    r = replay(x, base_z)
    check("supersession: replay now succeeds and the file is already the replay", r.returncode == 0 and jout(r)["files"][0]["up_to_date"] is True, out_of(r))
    again = read_rel(x, CRAFT_REL)
    r2 = replay(x, base_z)
    check("supersession: replay is idempotent", r2.returncode == 0 and read_rel(x, CRAFT_REL) == again == expected, out_of(r2))


def _check_supersession_verification(x, base_z, new_op):
    v = verify(x, "run-c2", [claim(new_op)], parent="parent-2", base=base_z)
    check("supersession: replacement receipt verifies with its authorization reference", v.returncode == 0, out_of(v))
    v = verify(x, "run-c2", [claim(new_op)], parent="parent-2")
    check("supersession: replacement verifies its complete destination with no --base (superseded write honoured)",
          v.returncode == 0, out_of(v))
    v = verify(x, "run-c", [claim(mop("replace", "Patterns", "P-03", "mine"))], base=base_z)
    check("supersession: the retired batch no longer verifies as active", v.returncode == 15, out_of(v))


def _check_supersession_ambiguous(x, base_z, old, new_op):
    snap = snapshot(x)
    again3 = member(x, "run-c3", [new_op], parent="parent-3", supersedes=[old], base=base_z)
    check("supersession: a second replacement of the same batch is ambiguous (15)", again3.returncode == 15 and "AMBIGUOUS" in again3.stdout, out_of(again3))
    check("supersession: ambiguous attempt wrote nothing", snapshot(x) == snap, None)


def _supersession_withdraw(root, origin, z, base_z):
    x2 = clone(origin, root, "x2-sup")
    member(x2, "run-c", [mop("replace", "Patterns", "P-03", "mine")])
    old2 = load_receipt(x2, "run-c")["batches"][0]["id"]
    sh(x2, "fetch", "-q", z, "HEAD")
    w = member(x2, "run-c5", [], parent="parent-5", supersedes=[old2], base=base_z)
    check("supersession: empty replacement withdraws the judgment", w.returncode == 0, out_of(w))
    return x2, old2


def _check_supersession_withdrawal_result(x2, z, old2, base_z):
    check("supersession: withdrawal leaves exactly the main blob", read_rel(x2, CRAFT_REL) == sh(z, "show", "HEAD:" + CRAFT_REL) + "\n", read_rel(x2, CRAFT_REL))
    rc = load_receipt(x2, "run-c5")["batches"][0]
    check("supersession: withdrawal is an empty batch, not a fabricated op", rc["ops"] == [] and rc["supersedes"] == [old2], rc)
    r = replay(x2, base_z)
    check("supersession: replay after withdrawal succeeds", r.returncode == 0, out_of(r))
    v = verify(x2, "run-c5", [], parent="parent-5", base=base_z)
    check("supersession: withdrawal verifies with an empty claimed list", v.returncode == 0, out_of(v))


def case_supersession_flow(root):
    origin, x, old, z, base_z = _supersession_fixture(root)
    _check_supersession_original_refused(x, base_z, old)
    old_bytes = read_bytes(receipt_path(x, "run-c"))
    new_op = mop("replace", "Patterns", "P-03", "mine revised")
    snap = snapshot(x)
    _check_supersession_authority(x, base_z, old)
    _check_supersession_references(x, base_z, old, new_op)
    _check_supersession_nothing_retired(x, base_z, snap)
    expected = _check_supersession_replacement(x, base_z, old, new_op, old_bytes)
    _check_supersession_replay_idempotent(x, base_z, expected)
    _check_supersession_verification(x, base_z, new_op)
    _check_supersession_ambiguous(x, base_z, old, new_op)
    x2, old2 = _supersession_withdraw(root, origin, z, base_z)
    _check_supersession_withdrawal_result(x2, z, old2, base_z)


def forge_receipt(co, runtime, batch_id, supersedes):
    rc = {"schema": 1, "persona": PERSONA, "feature": FEATURE, "runtime_id": runtime, "parent_id": "p",
          "batches": [{"id": batch_id, "seq": 1, "destination": CRAFT_REL, "ops": [], "originals": [],
                       "before_sha256": None, "after_sha256": "0" * 64, "supersedes": supersedes, "recorded_at_ns": 1}]}
    with open(receipt_path(co, runtime), "w", encoding="utf-8") as fh:
        json.dump(rc, fh)


def _evidence_fixture(root):
    co = new_checkout(root, "evid", craft=BASE_DOC)
    base0 = head(co)
    member(co, "run-t", [mop("add", "Patterns", "P-02", "two")])
    path = receipt_path(co, "run-t")
    return co, base0, path, read_bytes(path)


def _check_evidence_identity(co, base0, path, good):
    forged = json.loads(good)
    forged["batches"][0]["after_sha256"] = "f" * 64
    overwrite(path, json.dumps(forged))
    r = replay(co, base0)
    check("evidence: a receipt whose content no longer matches its identity fails replay with 15", r.returncode == 15 and "IDENTITY" in r.stdout, out_of(r))
    v = verify(co, "run-t", [claim(mop("add", "Patterns", "P-02", "two"))])
    check("evidence: ... and fails verification with 15", v.returncode == 15, out_of(v))


def _check_evidence_undecodable_and_restored(co, base0, path, good):
    overwrite(path, "{")
    check("evidence: undecodable receipt fails replay with 15", replay(co, base0).returncode == 15, None)
    overwrite_bytes(path, good)
    check("evidence: restored receipt replays", replay(co, base0, check_only=True).returncode == 0, None)


def _check_evidence_missing_pieces(co, base0, path, good):
    with open(os.path.join(co, CRAFT_REL), "a", encoding="utf-8") as fh:
        fh.write("- P-40: hand edited\n")
    os.remove(path)
    r = replay(co, base0)
    check("evidence: an Expertise change with no receipt is refused with 15", r.returncode == 15 and "UNRECEIPTED" in r.stdout, out_of(r))
    overwrite_bytes(path, good)
    os.remove(os.path.join(co, CRAFT_REL))
    r = replay(co, base0)
    check("evidence: a receipt naming a file the checkout lacks is refused with 15", r.returncode == 15, out_of(r))


def _check_evidence_cycle(co, base0):
    forge_receipt(co, "run-t", "a" * 64, ["b" * 64])
    forge_receipt(co, "run-u", "b" * 64, ["a" * 64])
    write_file(os.path.join(co, CRAFT_REL), BASE_DOC)
    r = replay(co, base0)
    check("evidence: cyclic supersession is refused with 15 and named", r.returncode == 15 and "CYCLIC" in r.stdout, out_of(r))


def case_replay_evidence_fails_closed(root):
    co, base0, path, good = _evidence_fixture(root)
    _check_evidence_identity(co, base0, path, good)
    _check_evidence_undecodable_and_restored(co, base0, path, good)
    _check_evidence_missing_pieces(co, base0, path, good)
    _check_evidence_cycle(co, base0)


def run_guarded(case, root):
    try:
        case(root)
    except Exception as exc:  # a missing subcommand or a mutant reads as FAIL, never as a crashed suite
        check("%s: completed without raising" % case.__name__, False, repr(exc))


SERIAL_CASES = (
    case_naive_last_writer_wins, case_green_union, case_concurrency_real, case_divergent_text,
    case_cap_overflow, case_new_file, case_destination_refusal, case_cap_drift_detector,
    case_stale_lock_recovery, case_replace_at_capacity, case_removal, case_missing_target,
    case_ambiguous_target, case_atomic_failure, case_add_only_compatibility, case_contract_drift,
    case_concurrent_writers, case_multi_op_composition, case_malformed_ops_cli,
    case_ops_entry_injection, case_ops_target_injection, case_ops_non_string_target,
    case_ops_add_duplicated_base, case_ops_target_grammar, case_ops_target_grammar_well_formed,
    case_duplicate_proposal_ids)
# The FEAT-2225 cases each own a private subtree of `root` and spawn many git/python
# subprocesses; a bounded pool keeps the whole suite inside its 60 second budget.
POOLED_CASES = (
    case_member_absent_files, case_member_destination_boundaries, case_member_strict_ops,
    case_member_batches_append, case_member_refusal_preserves, case_member_receipt_failure_fails_closed,
    case_member_verify, case_replay_local_receipts, case_replay_base_tracked_receipt,
    case_replay_collision_and_repeat,
    case_replay_independent_callers, case_replay_changed_main_and_cap, case_supersession_flow,
    case_replay_evidence_fails_closed, case_verify_complete_destination, case_verify_authorized_anchor)


def _run_all_cases(root):
    for case in SERIAL_CASES:
        case(root)
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda case: run_guarded(case, root), POOLED_CASES))


def main():
    root = tempfile.mkdtemp(prefix="expertise-merge-test-")
    try:
        _run_all_cases(root)
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
    sys.exit(C.report())
