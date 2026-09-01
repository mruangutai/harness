#!/usr/bin/env python3
"""Tests for quarantine.py, the explicit adopt/discard CLI (FEAT-51 T-04).

Every case builds its own tempfile.mkdtemp() root, nested under a
.harness/harness/features/FEAT-99-fixture/ directory so plan-merge.py's
require_destination (reached through `quarantine.py adopt` for plan.yaml) accepts the
canonical target — never a real feature directory. Resolves the binary the same way
test-plan-merge.py resolves its own, so a mutated copy of the source under test can be
swapped in without editing this file:

    CLI = os.environ.get("QUARANTINE_BIN") or os.path.join(HERE, "quarantine.py")
"""
import hashlib
import os
import subprocess
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.environ.get("QUARANTINE_BIN") or os.path.join(HERE, "quarantine.py")

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))


def run(*argv):
    return subprocess.run([sys.executable, CLI, *argv], capture_output=True, text=True)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return text


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# LOADS FINE ON ITS OWN, TEXTUALLY DISTINCTIVE (a comment and single-quoted scalars) so a
# byte-identity assertion after adoption cannot be satisfied by mere parsed-value equality.
DEFAULT_APPROVAL = (
    "approval:\n"
    "  status: pending\n"
    "  signer: 'main-session'\n"
    "  rulings:\n"
    "    - allow budget increase\n"
    "    - deny scope change\n"
    "  # a trailing comment inside the approval block\n"
)


def task_block(tid):
    # Every REQUIRED_TASK_FIELDS entry (harness_yaml.py), or plan-merge.py's post-merge
    # schema check refuses the merge for a reason that has nothing to do with adoption.
    return (
        f"  - id: {tid}\n"
        f"    title: Task {tid}\n"
        "    change_type: config\n"
        "    execution_mode: main-session-direct\n"
        "    files: [a.py]\n"
        "    verify: run it\n"
        "    intent: do it\n"
    )


def render_plan(task_ids, approval=DEFAULT_APPROVAL):
    out = ["schema: plan/1\n", "feature: FEAT-99-fixture\n", "\n"]
    if approval:
        out.append(approval)
        out.append("\n")
    out.append("tasks:\n")
    for tid in task_ids:
        out.append(task_block(tid))
    return "".join(out)


def ids(n_start, n_end):
    return [f"T-{i:02d}" for i in range(n_start, n_end + 1)]


def fixture_root():
    """A fresh tempfile.mkdtemp() with a nested .harness/harness/features/FEAT-99-fixture/
    directory, so plan-merge.py's require_destination accepts a plan.yaml canonical target
    adopted through it."""
    root = tempfile.mkdtemp(prefix="quarantine-test-")
    feature_dir = os.path.join(root, ".harness", "harness", "features", "FEAT-99-fixture")
    os.makedirs(feature_dir, exist_ok=True)
    return root, feature_dir


def quarantine_dir(feature_dir, agent="harness-backend-dev", session="12345678"):
    d = os.path.join(feature_dir, "quarantine", f"{agent}-{session}")
    os.makedirs(d, exist_ok=True)
    return d


# ---------------------------------------------------------------------------
# Case 1 + 2 — adopting plan.yaml unions task ids and preserves approval bytes
# ---------------------------------------------------------------------------

def case_1_2_adopt_plan_unions_tasks_and_preserves_approval():
    root, feature_dir = fixture_root()
    canonical = os.path.join(feature_dir, "plan.yaml")
    write(canonical, render_plan(ids(1, 14)))

    qdir = quarantine_dir(feature_dir)
    quarantined = os.path.join(qdir, "plan.yaml")
    write(quarantined, render_plan(["T-15"], approval=None))
    quarantined_before = open(quarantined, encoding="utf-8").read()

    result = run("adopt", "--file", quarantined, "--root", root)
    check("case1: adopt plan.yaml exits 0", result.returncode == 0, result.stdout + result.stderr)
    check(
        "case1: stdout carries ADOPTED naming both paths",
        f"ADOPTED {canonical} FROM {quarantined}" in result.stdout,
        result.stdout,
    )

    merged_text = open(canonical, encoding="utf-8").read()
    merged_doc = yaml.safe_load(merged_text)
    merged_ids = {t["id"] for t in merged_doc["tasks"]}
    check(
        "case1: canonical carries all fifteen task ids",
        merged_ids == set(ids(1, 14) + ["T-15"]),
        sorted(merged_ids),
    )
    check(
        "case1: the canonical plan is never the one-task quarantined file",
        merged_text != quarantined_before,
        "canonical equals the quarantined one-task proposal",
    )
    check(
        "case2: the canonical approval block survives adoption byte-identical",
        DEFAULT_APPROVAL in merged_text,
        repr(DEFAULT_APPROVAL) + " NOT IN " + repr(merged_text),
    )
    check(
        "case1: adopt leaves the quarantine file in place",
        os.path.exists(quarantined),
        "quarantine file was removed by adopt",
    )


# ---------------------------------------------------------------------------
# Case 3 — adopting BRIEF.md replaces it
# ---------------------------------------------------------------------------

def case_3_adopt_brief_replaces_canonical():
    root, feature_dir = fixture_root()
    canonical = os.path.join(feature_dir, "BRIEF.md")
    write(canonical, "# Old brief\nstale content\n")

    qdir = quarantine_dir(feature_dir, agent="harness-pm", session="abcdef12")
    quarantined = os.path.join(qdir, "BRIEF.md")
    write(quarantined, "# New brief\nfresh content\n")

    result = run("adopt", "--file", quarantined, "--root", root)
    check("case3: adopt BRIEF.md exits 0", result.returncode == 0, result.stdout + result.stderr)
    check(
        "case3: stdout carries ADOPTED naming both paths",
        f"ADOPTED {canonical} FROM {quarantined}" in result.stdout,
        result.stdout,
    )
    check(
        "case3: canonical BRIEF.md now holds the quarantined content",
        open(canonical, encoding="utf-8").read() == "# New brief\nfresh content\n",
        open(canonical, encoding="utf-8").read(),
    )
    check(
        "case3: adopt leaves the quarantine file in place",
        os.path.exists(quarantined),
        "quarantine file was removed by adopt",
    )


# ---------------------------------------------------------------------------
# Case 4 — adopt on an illegal basename exits 2
# ---------------------------------------------------------------------------

def case_4_adopt_illegal_basename_exits_2():
    root, feature_dir = fixture_root()
    qdir = quarantine_dir(feature_dir, agent="harness-qa", session="deadbeef")
    quarantined = os.path.join(qdir, "notes.txt")
    write(quarantined, "irrelevant\n")

    result = run("adopt", "--file", quarantined, "--root", root)
    check(
        "case4: illegal basename exits 2", result.returncode == 2, result.stdout + result.stderr
    )
    for legal in ("plan.yaml", "BRIEF.md", "feature.json", "STATE.md"):
        check(f"case4: refusal message names {legal}", legal in result.stderr, result.stderr)


# ---------------------------------------------------------------------------
# Case 5 — discard removes only the named directory
# ---------------------------------------------------------------------------

def case_5_discard_removes_only_named_directory():
    root, feature_dir = fixture_root()
    qdir_a = quarantine_dir(feature_dir, agent="harness-backend-dev", session="11111111")
    qdir_b = quarantine_dir(feature_dir, agent="harness-frontend-dev", session="22222222")
    write(os.path.join(qdir_a, "plan.yaml"), "irrelevant a\n")
    write(os.path.join(qdir_b, "plan.yaml"), "irrelevant b\n")

    result = run("discard", "--dir", qdir_a, "--root", root)
    check("case5: discard exits 0", result.returncode == 0, result.stdout + result.stderr)
    check(
        "case5: stdout carries DISCARDED naming the directory",
        f"DISCARDED {qdir_a}" in result.stdout,
        result.stdout,
    )
    check("case5: the named directory is gone", not os.path.exists(qdir_a))
    check("case5: the sibling quarantine directory survives", os.path.isdir(qdir_b))


# ---------------------------------------------------------------------------
# Case 6 — discard refuses a path outside a features/*/quarantine/ segment
# ---------------------------------------------------------------------------

def case_6_discard_refuses_path_outside_quarantine_segment():
    root, feature_dir = fixture_root()
    outside = os.path.join(feature_dir, "notes")
    os.makedirs(outside, exist_ok=True)
    write(os.path.join(outside, "keepme.txt"), "still here\n")

    result = run("discard", "--dir", outside, "--root", root)
    check(
        "case6: discard outside a quarantine segment exits 2",
        result.returncode == 2,
        result.stdout + result.stderr,
    )
    check(
        "case6: the refused directory and its contents are untouched",
        os.path.isdir(outside) and os.path.exists(os.path.join(outside, "keepme.txt")),
    )


# ---------------------------------------------------------------------------
# Case 7 — list changes no file
# ---------------------------------------------------------------------------

def case_7_list_changes_no_file():
    root, feature_dir = fixture_root()
    canonical = os.path.join(feature_dir, "plan.yaml")
    write(canonical, render_plan(ids(1, 14)))
    qdir = quarantine_dir(feature_dir, agent="harness-backend-dev", session="33333333")
    quarantined = os.path.join(qdir, "plan.yaml")
    write(quarantined, render_plan(["T-15"], approval=None))

    before = {canonical: sha256(canonical), quarantined: sha256(quarantined)}

    result = run("list", "--feature", "FEAT-99-fixture", "--root", root)
    check("case7: list exits 0", result.returncode == 0, result.stdout + result.stderr)
    check(
        "case7: list prints the quarantined file's path",
        quarantined in result.stdout,
        result.stdout,
    )

    after = {canonical: sha256(canonical), quarantined: sha256(quarantined)}
    check(
        "case7: list modifies neither the canonical nor the quarantined file",
        before == after,
        (before, after),
    )


# ---------------------------------------------------------------------------
# Bonus — list is silent and exits 0 when nothing is quarantined
# ---------------------------------------------------------------------------

def case_8_list_empty_prints_nothing_exits_0():
    root, feature_dir = fixture_root()
    result = run("list", "--feature", "FEAT-99-fixture", "--root", root)
    check("case8: empty list exits 0", result.returncode == 0, result.stdout + result.stderr)
    check("case8: empty list prints nothing on stdout", result.stdout == "", result.stdout)


def main():
    case_1_2_adopt_plan_unions_tasks_and_preserves_approval()
    case_3_adopt_brief_replaces_canonical()
    case_4_adopt_illegal_basename_exits_2()
    case_5_discard_removes_only_named_directory()
    case_6_discard_refuses_path_outside_quarantine_segment()
    case_7_list_changes_no_file()
    case_8_list_empty_prints_nothing_exits_0()

    fails = 0
    for name, ok, detail in RESULTS:
        if ok:
            print(f"PASS  {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n      | {detail}")

    summary = "FAIL test-quarantine.py" if fails else "PASS test-quarantine.py"
    print(summary)
    return fails


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
