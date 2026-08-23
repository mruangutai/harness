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
import ast
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
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


def main():
    root = tempfile.mkdtemp(prefix="expertise-merge-test-")
    try:
        case_naive_last_writer_wins(root)
        case_green_union(root)
        case_concurrency_real(root)
        case_divergent_text(root)
        case_cap_overflow(root)
        case_new_file(root)
        case_destination_refusal(root)
        case_cap_drift_detector()
        case_stale_lock_recovery(root)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    fails = 0
    for name, ok, detail in RESULTS:
        if ok:
            print(f"PASS  {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n      | {detail}")

    summary = "FAIL test-expertise-merge.py" if fails else "PASS test-expertise-merge.py"
    print(summary)
    return fails


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
