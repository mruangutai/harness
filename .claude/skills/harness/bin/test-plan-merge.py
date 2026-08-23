#!/usr/bin/env python3
"""Tests for plan-merge.py's `apply` subcommand (FEAT-32 T-03, D-01..D-04).

Every case runs the CLI as a SUBPROCESS against a fixture plan.yaml inside a fresh
tempfile.mkdtemp(), nested under a .harness/harness/features/FEAT-99-fixture/ path so
harness_merge.require_destination accepts it — never a real feature directory. Resolves the
binary the same way test-expertise-merge.py resolves its own, so a mutated copy of the source
under test can be swapped in without editing this file:

    CLI = os.environ.get("PLAN_MERGE_BIN") or os.path.join(HERE, "plan-merge.py")

Case 1 is deliberately never routed through the CLI: it reproduces #628's naive whole-file
write directly, so it stays red proof of the loss regardless of what this tool does.
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.environ.get("PLAN_MERGE_BIN") or os.path.join(HERE, "plan-merge.py")
TEMPLATE_PLAN = os.path.join(HERE, "..", "templates", "plan.yaml")

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------

DEFAULT_APPROVAL = (
    "approval:\n"
    "  status: pending\n"
    "  signer: 'main-session'\n"
    "  rulings:\n"
    "    - allow budget increase\n"
    "    - deny scope change\n"
    "  # a trailing comment inside the approval block\n"
)

# Loads EQUAL to DEFAULT_APPROVAL's parsed value (status: pending, same signer, same rulings)
# but is TEXTUALLY different: reflowed whitespace, double-quoted scalar, comment absent.
REFLOWED_APPROVAL = (
    "approval:\n"
    "  status:    pending\n"
    '  signer: "main-session"\n'
    "  rulings:\n"
    "    - allow budget increase\n"
    "    - deny scope change\n"
)

# LOADS DIFFERENT from DEFAULT_APPROVAL — a real signature attempt.
APPROVED_APPROVAL = (
    "approval:\n"
    "  status: approved\n"
    "  signer: 'main-session'\n"
    "  rulings:\n"
    "    - allow budget increase\n"
    "    - deny scope change\n"
)


def ids(n_start, n_end):
    return [f"T-{i:02d}" for i in range(n_start, n_end + 1)]


def task_block(tid, title=None):
    title = title or f"Task {tid}"
    return f"  - id: {tid}\n    title: {title}\n    status: pending\n"


def decision_block(did, choice=None):
    choice = choice or f"Decision {did}"
    return f"  - id: {did}\n    choice: {choice}\n"


def render_plan(task_ids, titles=None, decision_ids=None, approval=DEFAULT_APPROVAL, preamble=""):
    titles = titles or {}
    out = []
    if preamble:
        out.append(preamble)
    out.append("schema: plan/1\n")
    out.append("feature: FEAT-99-fixture\n")
    out.append("\n")
    if approval is not None:
        out.append(approval)
        out.append("\n")
    out.append("tasks:\n")
    for tid in task_ids:
        out.append(task_block(tid, titles.get(tid)))
    if decision_ids:
        out.append("\n")
        out.append("decisions:\n")
        for did in decision_ids:
            out.append(decision_block(did))
    return "".join(out)


def fixture_root(prefix="plan-merge-test-"):
    """A fresh tempfile.mkdtemp(), with a nested .harness/harness/features/FEAT-99-fixture/
    directory so require_destination accepts a plan.yaml written inside it."""
    root = tempfile.mkdtemp(prefix=prefix)
    d = os.path.join(root, ".harness", "harness", "features", "FEAT-99-fixture")
    os.makedirs(d, exist_ok=True)
    return root, os.path.join(d, "plan.yaml")


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return text


def run_apply(file_path, proposal_path):
    return subprocess.run(
        [sys.executable, CLI, "apply", "--file", file_path, "--proposal", proposal_path],
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------------------
# Cases
# ---------------------------------------------------------------------------


def case_naive_last_writer_wins():
    """Case 1 — THE RED CASE, permanent, never routed through the tool. Reproduces #628
    directly: a plain whole-file write of T-01..T-14, then a plain whole-file write of T-01
    alone. Thirteen separate per-id assertions, never a count."""
    _root, path = fixture_root()
    full = ids(1, 14)
    write(path, render_plan(full))
    write(path, render_plan(["T-01"]))
    content = open(path, encoding="utf-8").read()
    for tid in full[1:]:
        check(f"case1: naive whole-file write loses {tid}", f"- id: {tid}\n" not in content, content[:400])


def case_green_union():
    """Case 2 — THE GREEN CASE. Same base, applied through the tool this time."""
    _root, path = fixture_root()
    full = ids(1, 14)
    write(path, render_plan(full))

    proposal1 = os.path.join(_root, "proposal1.yaml")
    write(proposal1, render_plan(["T-01"]))
    r1 = run_apply(path, proposal1)
    check("case2: first apply exits 0", r1.returncode == 0, r1.stdout + r1.stderr)

    content1 = open(path, encoding="utf-8").read()
    for tid in full:
        check(f"case2: {tid} present after first apply", f"- id: {tid}\n" in content1, content1)

    proposal2 = os.path.join(_root, "proposal2.yaml")
    write(proposal2, render_plan(["T-15"]))
    r2 = run_apply(path, proposal2)
    check("case2: second apply exits 0", r2.returncode == 0, r2.stdout + r2.stderr)

    content2 = open(path, encoding="utf-8").read()
    for tid in full + ["T-15"]:
        check(f"case2: {tid} present after second apply", f"- id: {tid}\n" in content2, content2)


def case_approval_byte_identity():
    """Case 3 — APPROVAL BYTE IDENTITY. The proposal's approval block LOADS EQUAL to the
    base's but is textually reflowed, requoted, and drops the comment. Key presence is NOT
    substituted for a byte-identity assertion."""
    _root, path = fixture_root()
    full = ids(1, 14)
    base_text = render_plan(full, approval=DEFAULT_APPROVAL)
    write(path, base_text)

    proposal = os.path.join(_root, "proposal.yaml")
    write(proposal, render_plan(full + ["T-15"], approval=REFLOWED_APPROVAL))

    r = run_apply(path, proposal)
    check("case3: exit 0", r.returncode == 0, r.stdout + r.stderr)

    result = open(path, encoding="utf-8").read()
    check(
        "case3: the exact byte slice of the base's approval block occurs verbatim in the result",
        DEFAULT_APPROVAL in result,
        repr(DEFAULT_APPROVAL) + " NOT IN " + repr(result),
    )

    def hash_line_count(text):
        return sum(1 for line in text.splitlines() if line.lstrip().startswith("#"))

    check(
        "case3: number of hash-comment lines in the whole file is unchanged",
        hash_line_count(result) == hash_line_count(base_text),
        f"before={hash_line_count(base_text)} after={hash_line_count(result)}",
    )
    check("case3: stdout carries IGNORED-APPROVAL", "IGNORED-APPROVAL" in r.stdout, r.stdout)


def case_concurrency_real(trials=20):
    """Case 4 — CONCURRENCY FOR REAL. Two subprocesses race overlapping proposals against the
    same base. Exactly two outcomes are admitted; a third is reported by trial, never
    absorbed into the assertion."""
    third_outcome_details = []
    locked_count = 0
    for i in range(trials):
        root, path = fixture_root(prefix=f"plan-merge-test-c4-{i}-")
        base_ids = ids(1, 3)
        write(path, render_plan(base_ids))
        proposal_a = os.path.join(root, "a.yaml")
        write(proposal_a, render_plan(base_ids + ["T-15"]))
        proposal_b = os.path.join(root, "b.yaml")
        write(proposal_b, render_plan(base_ids + ["T-16"]))

        pa = subprocess.Popen(
            [sys.executable, CLI, "apply", "--file", path, "--proposal", proposal_a],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        pb = subprocess.Popen(
            [sys.executable, CLI, "apply", "--file", path, "--proposal", proposal_b],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        out_a, err_a = pa.communicate(timeout=30)
        out_b, err_b = pb.communicate(timeout=30)
        rc_a, rc_b = pa.returncode, pb.returncode

        content = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
        ok = False
        outcome = "other"

        if rc_a == 0 and rc_b == 0:
            outcome = "union"
            ok = all(f"- id: {tid}\n" in content for tid in base_ids + ["T-15", "T-16"])
        elif sorted([rc_a, rc_b]) == [0, 6]:
            outcome = "locked"
            locked_count += 1
            if rc_a == 6:
                lock_stdout, lost_id, won_id = out_a + err_a, "T-15", "T-16"
            else:
                lock_stdout, lost_id, won_id = out_b + err_b, "T-16", "T-15"
            ok = (
                "LOCKED" in lock_stdout
                and f"- id: {lost_id}\n" not in content
                and f"- id: {won_id}\n" in content
                and all(f"- id: {tid}\n" in content for tid in base_ids)
            )

        if not ok:
            third_outcome_details.append(
                f"trial {i}: outcome={outcome} rc_a={rc_a} rc_b={rc_b} "
                f"out_a={out_a!r} out_b={out_b!r} content={content!r}"
            )

    check(
        f"case4: {trials} concurrent trials admit only the union outcome or the lock outcome",
        not third_outcome_details,
        "\n".join(third_outcome_details),
    )
    check(
        f"case4: informational — the exit-6 lock branch was taken in {locked_count}/{trials} trials",
        True,
        "",
    )


def case_conflict():
    """Case 5 — CONFLICT: a proposal carrying T-03 with a different title exits 7, prints the
    id and both values, and leaves the file byte identical to before."""
    _root, path = fixture_root()
    full = ids(1, 5)
    original = write(path, render_plan(full))

    proposal = os.path.join(_root, "proposal.yaml")
    write(proposal, render_plan(full, titles={"T-03": "A completely different title"}))

    r = run_apply(path, proposal)
    check("case5: conflict exits 7", r.returncode == 7, r.stdout + r.stderr)
    check("case5: stdout names the id", "T-03" in (r.stdout + r.stderr), r.stdout + r.stderr)
    check(
        "case5: stdout carries both values",
        "Task T-03" in (r.stdout + r.stderr) and "A completely different title" in (r.stdout + r.stderr),
        r.stdout + r.stderr,
    )
    after = open(path, encoding="utf-8").read()
    check("case5: file is byte identical to before", after == original, repr((original, after)))
    # harness_merge's flock lock (D-02) is DELIBERATELY never removed — unlike
    # expertise-merge.py's O_EXCL create-and-delete scheme — so its mere presence proves
    # nothing about a refusal's cleanup. What DOES matter: no stray mkstemp() tempfile is
    # left behind in plan.yaml's directory (locked_update removes its tmpfile on any
    # exception, MergeRefusal included).
    plan_dir = os.path.dirname(path)
    stray = [n for n in os.listdir(plan_dir) if n not in ("plan.yaml", "plan.yaml.lock")]
    check("case5: no stray tempfile left behind after the refusal", not stray, stray)


def case_idempotence():
    """Case 6 — IDEMPOTENCE: applying the same proposal twice leaves the second run at exit 0
    with the file byte identical to after the first run."""
    _root, path = fixture_root()
    full = ids(1, 5)
    write(path, render_plan(full))

    proposal = os.path.join(_root, "proposal.yaml")
    write(proposal, render_plan(full + ["T-15"]))

    r1 = run_apply(path, proposal)
    check("case6: first apply exits 0", r1.returncode == 0, r1.stdout + r1.stderr)
    after_first = open(path, encoding="utf-8").read()

    r2 = run_apply(path, proposal)
    check("case6: second apply exits 0", r2.returncode == 0, r2.stdout + r2.stderr)
    after_second = open(path, encoding="utf-8").read()

    check(
        "case6: file is byte identical after the second, idempotent apply",
        after_first == after_second,
        repr((after_first, after_second)),
    )


def case_destination_refusal():
    """Case 7 — DESTINATION REFUSAL, both directions.

    The dot-dot direction cannot be built from `..` alone: a pure `..` path ends in whatever
    follows the `..`, so it is merely a second non-matching path. A SYMLINK is what gives a
    literal argument that ENDS in the matching tail while RESOLVING somewhere the tail does
    not match: FEAT-99-fixture is a symlink pointing outside any features/ tree, and the
    literal argument still ends in .../features/FEAT-99-fixture/plan.yaml.
    """
    root = tempfile.mkdtemp(prefix="plan-merge-test-c7-")
    proposal = os.path.join(root, "proposal.yaml")
    write(proposal, render_plan(["T-01"]))

    # REFUSE: a source path.
    src = os.path.join(root, "src", "main.py")
    os.makedirs(os.path.dirname(src), exist_ok=True)
    write(src, "real code\n")
    r = run_apply(src, proposal)
    check("case7: a source path is REFUSED with exit 9", r.returncode == 9, r.stdout + r.stderr)
    check(
        "case7: ...and the refused file is untouched",
        open(src, encoding="utf-8").read() == "real code\n",
        "the tool wrote to a path it said it refused",
    )

    # REFUSE: a symlinked path segment. The literal argument ends in the matching tail; the
    # RESOLVED path does not, because FEAT-99-fixture is a symlink to somewhere else entirely.
    outside = os.path.join(root, "outside-real-target")
    os.makedirs(outside, exist_ok=True)
    outside_plan = os.path.join(outside, "plan.yaml")
    outside_original = write(outside_plan, render_plan(["T-01"]))

    harness_dir = os.path.join(root, "escape", ".harness", "harness", "features")
    os.makedirs(harness_dir, exist_ok=True)
    symlink_path = os.path.join(harness_dir, "FEAT-99-fixture")
    os.symlink(outside, symlink_path)
    literal_path = os.path.join(symlink_path, "plan.yaml")
    check(
        "case7: the escape's literal argument ends in the matching tail",
        literal_path.endswith(os.path.join("features", "FEAT-99-fixture", "plan.yaml")),
        literal_path,
    )

    r_escape = run_apply(literal_path, proposal)
    check(
        "case7: a symlink escape whose LITERAL argument matches but RESOLVES elsewhere is "
        "REFUSED with exit 9",
        r_escape.returncode == 9,
        r_escape.stdout + r_escape.stderr,
    )
    check(
        "case7: ...and the file behind the symlink is untouched",
        open(outside_plan, encoding="utf-8").read() == outside_original,
        "the tool wrote through the symlink it said it refused",
    )

    # ALLOW: a legitimate fixture plan.yaml.
    _legit_root, legit_path = fixture_root(prefix="plan-merge-test-c7-legit-")
    write(legit_path, render_plan(["T-01"]))
    r_legit = run_apply(legit_path, proposal)
    check(
        "case7: a legitimate fixture plan.yaml is ALLOWED — exit 0",
        r_legit.returncode == 0,
        r_legit.stdout + r_legit.stderr,
    )


def case_unparseable():
    """Case 8 — UNPARSEABLE: a proposal that is not valid YAML exits 5, names the proposal
    side, and leaves the base byte identical."""
    _root, path = fixture_root()
    original = write(path, render_plan(ids(1, 3)))

    proposal = os.path.join(_root, "proposal.yaml")
    write(proposal, "tasks: [unterminated flow seq\n  - broken: :\n")

    r = run_apply(path, proposal)
    check("case8: unparseable proposal exits 5", r.returncode == 5, r.stdout + r.stderr)
    check(
        "case8: stdout/stderr names the proposal side",
        "proposal" in (r.stdout + r.stderr).lower(),
        r.stdout + r.stderr,
    )
    after = open(path, encoding="utf-8").read()
    check("case8: base file is byte identical to before", after == original, repr((original, after)))


def case_comments_survive():
    """Case 9 — COMMENTS SURVIVE: a base carrying the plan.yaml template's own leading
    comment block still carries every one of those lines, byte identical, after a merge that
    adds a task."""
    with open(TEMPLATE_PLAN, encoding="utf-8") as f:
        template_lines = f.readlines()
    comment_block = "".join(template_lines[:19])
    check(
        "case9: the template's leading block is all comment lines",
        all(line.startswith("#") for line in template_lines[:19]),
        comment_block,
    )

    _root, path = fixture_root()
    full = ids(1, 5)
    write(path, render_plan(full, preamble=comment_block + "\n"))

    proposal = os.path.join(_root, "proposal.yaml")
    write(proposal, render_plan(full + ["T-15"]))

    r = run_apply(path, proposal)
    check("case9: exit 0", r.returncode == 0, r.stdout + r.stderr)

    result = open(path, encoding="utf-8").read()
    for i, line in enumerate(template_lines[:19]):
        check(f"case9: template comment line {i + 1} survives byte identical", line in result, repr(line))
    check("case9: T-15 was added", "- id: T-15\n" in result, result)


def case_structural_refusal():
    """Case 10 — THE STRUCTURAL REFUSAL, both directions. Base approval loads status: pending."""
    # 10a: proposal adds T-15 AND carries an approval that LOADS DIFFERENT -> exit 8, applies
    # NOTHING. Byte-identity, not a key check, and T-15 absent by id.
    _root, path = fixture_root(prefix="plan-merge-test-c10a-")
    full = ids(1, 5)
    original = write(path, render_plan(full, approval=DEFAULT_APPROVAL))
    proposal_a = os.path.join(_root, "proposal.yaml")
    write(proposal_a, render_plan(full + ["T-15"], approval=APPROVED_APPROVAL))

    r_a = run_apply(path, proposal_a)
    check("case10a: differing approval exits 8", r_a.returncode == 8, r_a.stdout + r_a.stderr)
    check(
        "case10a: stdout/stderr names the approval mapping and both loaded values",
        "approval" in (r_a.stdout + r_a.stderr).lower()
        and "pending" in (r_a.stdout + r_a.stderr)
        and "approved" in (r_a.stdout + r_a.stderr),
        r_a.stdout + r_a.stderr,
    )
    after_a = open(path, encoding="utf-8").read()
    check("case10a: file is byte identical to before (nothing applied)", after_a == original, repr((original, after_a)))
    check("case10a: T-15 is absent, asserted by id", "- id: T-15\n" not in after_a, after_a)

    # 10b: proposal adds T-15 and carries NO approval key at all -> exit 0, T-15 present.
    _root_b, path_b = fixture_root(prefix="plan-merge-test-c10b-")
    write(path_b, render_plan(full, approval=DEFAULT_APPROVAL))
    proposal_b = os.path.join(_root_b, "proposal.yaml")
    write(proposal_b, render_plan(full + ["T-15"], approval=None))

    r_b = run_apply(path_b, proposal_b)
    check("case10b: proposal with no approval key exits 0", r_b.returncode == 0, r_b.stdout + r_b.stderr)
    after_b = open(path_b, encoding="utf-8").read()
    check("case10b: T-15 is present", "- id: T-15\n" in after_b, after_b)

    # 10c: proposal's approval differs only in whitespace/comments (loads equal) -> exit 0,
    # the same parsed-not-textual property case 3 grades, here on the refusal path.
    _root_c, path_c = fixture_root(prefix="plan-merge-test-c10c-")
    write(path_c, render_plan(full, approval=DEFAULT_APPROVAL))
    proposal_c = os.path.join(_root_c, "proposal.yaml")
    write(proposal_c, render_plan(full + ["T-15"], approval=REFLOWED_APPROVAL))

    r_c = run_apply(path_c, proposal_c)
    check("case10c: loaded-equal-but-reflowed approval exits 0", r_c.returncode == 0, r_c.stdout + r_c.stderr)
    after_c = open(path_c, encoding="utf-8").read()
    check("case10c: T-15 is present", "- id: T-15\n" in after_c, after_c)


def case_create_path_approval():
    """Case 11 — THE CREATE PATH MUST NOT CARRY THE PROPOSAL'S APPROVAL. Base does not exist
    (step 3 treats it as an empty mapping, D-04 read together with step 7b): a proposal carrying
    an approval key differs from the base's absent one, so it must refuse exit 8 rather than
    write the proposal's signature to a brand-new file.
    """
    # 11a: base does not exist, proposal carries NO approval key -> exit 0, file created, whole.
    _root_a, path_a = fixture_root(prefix="plan-merge-test-c11a-")
    check("case11a: base file does not exist before apply", not os.path.exists(path_a), path_a)
    full = ids(1, 3)
    proposal_a = os.path.join(_root_a, "proposal.yaml")
    write(proposal_a, render_plan(full, approval=None))

    r_a = run_apply(path_a, proposal_a)
    check("case11a: create with no approval key exits 0", r_a.returncode == 0, r_a.stdout + r_a.stderr)
    check("case11a: the file now exists", os.path.exists(path_a), path_a)
    if os.path.exists(path_a):
        content_a = open(path_a, encoding="utf-8").read()
        for tid in full:
            check(f"case11a: {tid} present in the created file", f"- id: {tid}\n" in content_a, content_a)

    # 11b: base does not exist, proposal DOES carry an approval key -> exit 8, nothing written,
    # no file left behind (the create-path analogue of case10a's byte-identity check).
    _root_b, path_b = fixture_root(prefix="plan-merge-test-c11b-")
    check("case11b: base file does not exist before apply", not os.path.exists(path_b), path_b)
    proposal_b = os.path.join(_root_b, "proposal.yaml")
    write(proposal_b, render_plan(full, approval=APPROVED_APPROVAL))

    r_b = run_apply(path_b, proposal_b)
    check("case11b: create with an approval key exits 8", r_b.returncode == 8, r_b.stdout + r_b.stderr)
    check(
        "case11b: no file was created by the refused apply",
        not os.path.exists(path_b),
        "the tool wrote a file it said it refused",
    )
    check(
        "case11b: stdout/stderr names the approval mapping",
        "approval" in (r_b.stdout + r_b.stderr).lower(),
        r_b.stdout + r_b.stderr,
    )
    check(
        "case11b: stdout/stderr names the main session as the signer",
        "main session" in (r_b.stdout + r_b.stderr).lower(),
        r_b.stdout + r_b.stderr,
    )
    # As in case5, harness_merge's flock lock (D-02) is deliberately never removed, so its mere
    # presence proves nothing about a refusal's cleanup; what matters is no stray mkstemp()
    # tempfile and, per this assertion's own name, no plan.yaml itself.
    plan_dir = os.path.dirname(path_b)
    stray = [
        n for n in (os.listdir(plan_dir) if os.path.isdir(plan_dir) else [])
        if n not in ("plan.yaml.lock",)
    ]
    check("case11b: no stray tempfile/plan.yaml left behind after the refusal", not stray, stray)


def main():
    case_naive_last_writer_wins()
    case_green_union()
    case_approval_byte_identity()
    case_concurrency_real()
    case_conflict()
    case_idempotence()
    case_destination_refusal()
    case_unparseable()
    case_comments_survive()
    case_structural_refusal()
    case_create_path_approval()

    fails = 0
    for name, ok, detail in RESULTS:
        if ok:
            print(f"PASS  {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n      | {detail}")

    summary = "FAIL test-plan-merge.py" if fails else "PASS test-plan-merge.py"
    print(summary)
    return fails


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
