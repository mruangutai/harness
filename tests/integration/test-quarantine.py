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
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import hashlib
import os
import subprocess
import sys
import tempfile

import yaml

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
HERE = BIN_DIR
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
# Case 9 — adopt refuses a --file whose realpath is outside any quarantine directory
# ---------------------------------------------------------------------------

def case_9_adopt_refuses_file_outside_quarantine():
    root, feature_dir = fixture_root()
    # feature.json, not plan.yaml: feature.json takes the harness_merge.locked_update arm,
    # which has no downstream guard of its own, so a nonzero exit here can only have come
    # from quarantine.py's own containment — never from a sibling tool refusing first.
    canonical = os.path.join(feature_dir, "feature.json")
    write(canonical, '{"feature": "FEAT-99-fixture", "real": true}\n')
    canonical_before = sha256(canonical)

    # A legally-named file that sits in a sibling `notes/` directory rather than under any
    # `quarantine/<writer>/` segment — the shape adopt must still refuse.
    decoy = os.path.join(feature_dir, "notes", "feature.json")
    write(decoy, '{"feature": "FEAT-99-fixture", "decoy": true}\n')

    result = run("adopt", "--file", decoy, "--root", root)
    check(
        "case9: file outside any quarantine directory exits 2",
        result.returncode == 2,
        result.stdout + result.stderr,
    )
    check(
        "case9: the canonical feature.json is byte-unchanged",
        sha256(canonical) == canonical_before,
        "canonical feature.json was overwritten",
    )


# ---------------------------------------------------------------------------
# Case 10 — a --file inside feature A's quarantine cannot land on feature B's canonical
# ---------------------------------------------------------------------------

def case_10_adopt_cannot_cross_from_feature_a_onto_feature_b():
    root, feature_a = fixture_root()
    feature_b = os.path.join(root, ".harness", "harness", "features", "FEAT-98-victim")
    os.makedirs(feature_b, exist_ok=True)
    victim = os.path.join(feature_b, "feature.json")
    write(victim, '{"feature": "FEAT-98-victim", "real": true}\n')
    victim_before = sha256(victim)

    # A's own `quarantine/` segment is a SYMLINK onto feature B's directory. The OLD
    # arithmetic (two dirname() hops up from the given file, oblivious to symlinks and to
    # segment names) computes "A/quarantine/feature.json" as the write target — a string
    # that, followed through the symlink at open() time, physically lands inside B.
    quarantine_link = os.path.join(feature_a, "quarantine")
    os.symlink(feature_b, quarantine_link)
    writer_dir = os.path.join(quarantine_link, "writer")
    subdir = os.path.join(writer_dir, "subdir")
    os.makedirs(subdir, exist_ok=True)
    quarantined = os.path.join(subdir, "feature.json")
    write(quarantined, '{"feature": "FEAT-98-victim", "adopted": "wrongly"}\n')

    result = run("adopt", "--file", quarantined, "--root", root)
    check(
        "case10: cross-feature adopt via symlinked quarantine exits 2",
        result.returncode == 2,
        result.stdout + result.stderr,
    )
    check(
        "case10: feature B's canonical feature.json is byte-unchanged",
        sha256(victim) == victim_before,
        "feature B's canonical feature.json was overwritten by an adopt scoped to feature A",
    )


# ---------------------------------------------------------------------------
# Case 11 — adopt refuses a --file nested deeper than one dir under quarantine/
# ---------------------------------------------------------------------------

def case_11_adopt_refuses_deeper_nesting_under_quarantine():
    root, feature_dir = fixture_root()
    # feature.json for the same reason as case 9: no downstream guard to mask a missing
    # containment check, so "exits 2" can only be quarantine.py's own refusal.
    canonical = os.path.join(feature_dir, "feature.json")
    write(canonical, '{"feature": "FEAT-99-fixture", "real": true}\n')
    canonical_before = sha256(canonical)

    qdir = quarantine_dir(feature_dir)
    subdir = os.path.join(qdir, "sub")
    os.makedirs(subdir, exist_ok=True)
    quarantined = os.path.join(subdir, "feature.json")
    write(quarantined, '{"feature": "FEAT-99-fixture", "nested": true}\n')

    result = run("adopt", "--file", quarantined, "--root", root)
    check(
        "case11: nesting deeper than one dir under quarantine/ exits 2",
        result.returncode == 2,
        result.stdout + result.stderr,
    )
    check(
        "case11: the canonical feature.json is byte-unchanged",
        sha256(canonical) == canonical_before,
        "canonical feature.json was overwritten",
    )


# ---------------------------------------------------------------------------
# Case 13 — adopt refuses a --file that is quarantine-shaped only under a DIFFERENT root
# than the one it was invoked against (the wider hole root-anchoring closed in cycle 2)
# ---------------------------------------------------------------------------

def case_13_adopt_refuses_file_shaped_correctly_under_a_foreign_root():
    root_attacker, feature_dir_attacker = fixture_root()
    decoy = os.path.join(feature_dir_attacker, "quarantine", "w", "feature.json")
    write(decoy, '{"feature": "FEAT-99-fixture", "attacker": true}\n')

    root_victim, feature_dir_victim = fixture_root()
    victim = os.path.join(feature_dir_victim, "feature.json")
    write(victim, '{"feature": "FEAT-99-fixture", "real": true}\n')
    victim_before = sha256(victim)

    result = run("adopt", "--file", decoy, "--root", root_victim)
    check(
        "case13: a quarantine-shaped file under a foreign root exits 2",
        result.returncode == 2,
        result.stdout + result.stderr,
    )
    check(
        "case13: the invoked root's canonical feature.json is byte-unchanged",
        sha256(victim) == victim_before,
        "a file merely shaped like a quarantine path under a different root overwrote "
        "this root's canonical artifact",
    )


# ---------------------------------------------------------------------------
# Case 12 — adopt refuses a symlink inside a legal quarantine dir whose realpath escapes it
# ---------------------------------------------------------------------------

def case_12_adopt_refuses_symlink_escaping_quarantine_dir():
    root, feature_dir = fixture_root()
    canonical = os.path.join(feature_dir, "plan.yaml")
    write(canonical, render_plan(ids(1, 14)))
    canonical_before = sha256(canonical)

    escape_target = os.path.join(root, "escape.yaml")
    write(escape_target, "not a quarantine proposal at all\n")
    escape_before = sha256(escape_target)

    qdir = quarantine_dir(feature_dir)
    quarantined = os.path.join(qdir, "plan.yaml")
    os.symlink(escape_target, quarantined)

    result = run("adopt", "--file", quarantined, "--root", root)
    check(
        "case12: a symlink whose realpath escapes the quarantine dir exits 2",
        result.returncode == 2,
        result.stdout + result.stderr,
    )
    # The two byte-unchanged assertions this case carried in cycle 1 are DELETED, not
    # strengthened: the cycle-1 receipt recorded both passing even on the pre-fix baseline
    # (plan-merge's own schema refusal on the escape file's non-plan content left both
    # targets untouched before quarantine.py's own containment ever mattered), so neither
    # one discriminates this tool's containment from a downstream guard. "exits 2" above is
    # the sole discriminator for this case, per the cycle-2 dispatch's instruction to delete
    # a vacuous assertion rather than leave it standing.



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
    case_9_adopt_refuses_file_outside_quarantine()
    case_10_adopt_cannot_cross_from_feature_a_onto_feature_b()
    case_11_adopt_refuses_deeper_nesting_under_quarantine()
    case_12_adopt_refuses_symlink_escaping_quarantine_dir()
    case_13_adopt_refuses_file_shaped_correctly_under_a_foreign_root()

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
