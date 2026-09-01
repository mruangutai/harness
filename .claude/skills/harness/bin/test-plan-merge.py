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

import yaml

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


def run_verb(*argv, env=None):
    """Any verb, argv passed through verbatim — so a case can assert on argument handling
    itself rather than only on a well-formed invocation. `env=None` inherits this process's own
    environment (os.environ default); a case that must control HARNESS_AGENT_TYPE passes an
    explicit mapping so the ambient test-runner environment can never leak a false pass."""
    return subprocess.run([sys.executable, CLI, *argv], capture_output=True, text=True, env=env)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# Cases
# ---------------------------------------------------------------------------


def case_proposal_indent_differs_from_base():
    """A proposal whose list items are indented differently from the base's still produces a
    PARSEABLE plan, and the splice is checked before it is written.

    THE LIVE FAILURE THIS PINS, on 2026-08-31: FEAT-41's own plan indents `decisions:` items
    two spaces (`  - id: D-11`). An operator-approved amendment was proposed as a standalone
    document with items at column 0 — valid YAML on its own, and the shape every example in
    this repository's prose uses. `apply` spliced that text VERBATIM, printed ADDED D-13 and
    APPLIED, exited 0, and left a signed 1541-line plan that PyYAML could not load. Nothing
    refused it, because the merge parsed the base and the proposal and never the RESULT.

    Two independent defects, and the test asserts both, because either alone leaves a hole:
      (a) the spliced item is re-indented to the base list's own indent;
      (b) the merged text is parsed before it is written, so ANY future splice bug is a
          refusal rather than a corrupted plan.
    """
    root, plan_path = fixture_root()

    # The base indents its decision items TWO SPACES, which is what the live corpus does.
    base = ("schema: plan/1\n"
            "feature: FEAT-99-fixture\n"
            "decisions:\n"
            "  - id: D-01\n"
            "    choice: the base decision\n"
            "    because: it was here first\n"
            "    dec: none\n"
            "tasks:\n" + task_block("T-01") +
            DEFAULT_APPROVAL)
    with open(plan_path, "w", encoding="utf-8") as stream:
        stream.write(base)

    # The proposal puts its item at COLUMN ZERO — the indentation a human writes by hand.
    proposal = os.path.join(root, "proposal.yaml")
    with open(proposal, "w", encoding="utf-8") as stream:
        stream.write("decisions:\n"
                     "- id: D-02\n"
                     "  choice: the amendment\n"
                     "  because: an operator approved it\n"
                     "  dec: DEC-199\n")

    result = run_apply(plan_path, proposal)
    merged = open(plan_path, encoding="utf-8").read()

    check("apply_indent_mismatch_exits_0", result.returncode == 0,
          f"exit {result.returncode}: {(result.stdout + result.stderr)[:300]!r}")

    parsed, error = None, None
    try:
        parsed = yaml.safe_load(merged)
    except yaml.YAMLError as exc:
        error = exc
    check("apply_indent_mismatch_leaves_a_PARSEABLE_plan", error is None,
          f"merged plan does not load: {error}")

    ids = [d.get("id") for d in (parsed or {}).get("decisions") or []]
    check("apply_indent_mismatch_added_the_decision", ids == ["D-01", "D-02"], f"ids={ids}")

    # The base's own item is untouched, byte for byte — re-indenting the ADDITION must never
    # reformat what was already signed.
    check("apply_indent_mismatch_preserves_the_base_item",
          "  - id: D-01\n    choice: the base decision\n" in merged,
          "the base's decision item was reformatted")


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


# ---------------------------------------------------------------------------
# FEAT-41 T-03: the four new verbs
# ---------------------------------------------------------------------------


def case_set_task_station_one_line():
    """The whole promise of a splice: ONE line changes and every other byte is identical.
    Asserting only that the task's status reads the new value would pass on a YAML round trip
    that silently renormalised quoting and dropped every comment in the file."""
    root, plan = fixture_root()
    try:
        before = write(plan, render_plan(ids(1, 3), preamble="# a leading comment\n"))
        r = run_verb("set-task-station", "--file", plan, "--task", "T-02", "--station", "building")
        after = read(plan)
        check("set-task-station exits 0", r.returncode == 0, f"rc={r.returncode} {r.stderr!r}")
        b_lines, a_lines = before.splitlines(True), after.splitlines(True)
        differing = [i for i, (x, y) in enumerate(zip(b_lines, a_lines)) if x != y]
        check("set-task-station changes EXACTLY one line",
              len(b_lines) == len(a_lines) and len(differing) == 1,
              f"differing={differing}")
        check("set-task-station changes T-02's status line and nothing else",
              differing and a_lines[differing[0]].strip() == "status: building"
              and "T-02" in "".join(a_lines[max(0, differing[0] - 2):differing[0]]),
              "".join(a_lines))
        check("set-task-station leaves the leading comment intact",
              after.startswith("# a leading comment\n"), after[:40])
        # COUNTED IN THE TASKS SECTION ONLY — the approval mapping also carries a
        # `status: pending`, so a whole-file count says 3 and proves nothing about the tasks.
        check("set-task-station leaves T-01 and T-03 pending",
              after.split("tasks:")[1].count("status: pending") == 2, after)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_set_task_station_unknown_id():
    root, plan = fixture_root()
    try:
        before = write(plan, render_plan(ids(1, 2)))
        r = run_verb("set-task-station", "--file", plan, "--task", "T-99", "--station", "done")
        check("set-task-station exits 3 on an unknown task id", r.returncode == 3,
              f"rc={r.returncode} {r.stderr!r}")
        check("set-task-station's exit-3 message NAMES the ids the plan does carry",
              "T-01" in r.stderr and "T-02" in r.stderr, r.stderr)
        check("set-task-station writes nothing on an unknown task id", read(plan) == before)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_set_feature_station_insert_and_replace():
    root, plan = fixture_root()
    try:
        write(plan, render_plan(ids(1, 2)))
        r = run_verb("set-feature-station", "--file", plan, "--station", "review")
        after = read(plan)
        check("set-feature-station exits 0 when the key is absent", r.returncode == 0,
              f"rc={r.returncode} {r.stderr!r}")
        check("set-feature-station INSERTS status immediately after feature:",
              "feature: FEAT-99-fixture\nstatus: review\n" in after, after[:200])
        r2 = run_verb("set-feature-station", "--file", plan, "--station", "done")
        after2 = read(plan)
        check("set-feature-station exits 0 when the key is present", r2.returncode == 0,
              f"rc={r2.returncode} {r2.stderr!r}")
        check("set-feature-station REPLACES rather than appending a second key",
              after2.count("status: done") == 1 and "status: review" not in after2
              and len(after2.splitlines()) == len(after.splitlines()), after2[:200])
        check("set-feature-station does not touch a task's status",
              after2.split("tasks:")[1].count("status: pending") == 2, after2)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_illegal_station_exit_4():
    """Exit 4 BEFORE the lock is taken, so a refused value never opens the file."""
    root, plan = fixture_root()
    try:
        before = write(plan, render_plan(ids(1, 2)))
        for verb, extra in (("set-task-station", ["--task", "T-01"]),
                            ("set-feature-station", [])):
            for bad in ("Done", "icebox", "", "abandonded"):
                r = run_verb(verb, "--file", plan, *extra, "--station", bad)
                check(f"{verb} exits 4 on the illegal station {bad!r}", r.returncode == 4,
                      f"rc={r.returncode} {r.stderr!r}")
                check(f"{verb}'s exit-4 line lists the legal stations for {bad!r}",
                      all(st in r.stderr for st in
                          ("backlog", "plan", "ready", "building", "review", "done")),
                      r.stderr)
                check(f"{verb} writes nothing when {bad!r} is refused", read(plan) == before)
        # TERMINAL_MARKER is legal for both verbs even though it is NOT a board station.
        r = run_verb("set-task-station", "--file", plan, "--task", "T-01",
                     "--station", "abandoned")
        check("set-task-station ACCEPTS abandoned, the terminal marker", r.returncode == 0,
              f"rc={r.returncode} {r.stderr!r}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_sign_approval():
    root, plan = fixture_root()
    try:
        write(plan, render_plan(ids(1, 2)))
        r = run_verb("sign-approval", "--file", plan, "--by", "Mike Ruangutai",
                     "--date", "2026-08-30")
        after = read(plan)
        check("sign-approval exits 0", r.returncode == 0, f"rc={r.returncode} {r.stderr!r}")
        check("sign-approval writes status: approved", "status: approved" in after, after[:400])
        check("sign-approval writes approved_by", "approved_by: Mike Ruangutai" in after,
              after[:400])
        # THE DATE IS ASSERTED BY VALUE, NOT BY SUBSTRING (FEAT-41 F-02). It used to grep for
        # the bare text `date: 2026-08-30`. Signing now emits every field through YAML, which
        # quotes this one -- bare, `2026-08-30` reloads as a datetime.date rather than as the
        # string the operator typed and the signature records. No consumer reads the field, so
        # the quoting is free; what matters is the value, and asking for the value is a stronger
        # question than asking for the spelling. `--date` is as free-form as `--by`, so it is
        # escaped by the same uniform rule rather than exempted -- an exemption would be a hole
        # in the check that closes F-02.
        check("sign-approval writes date, and it reloads as the string that was passed",
              (yaml.safe_load(after).get("approval") or {}).get("date") == "2026-08-30",
              after[:400])
        check("sign-approval leaves status: pending behind nowhere",
              "status: pending" not in after.split("tasks:")[0], after[:400])
        check("sign-approval does not disturb the tasks",
              after.split("tasks:")[1].count("status: pending") == 2, after)
    finally:
        shutil.rmtree(root, ignore_errors=True)

def case_f02_sign_approval_cannot_write_an_unparseable_signature():
    """FEAT-41 F-02, high, found by the validation panel.

    `sign-approval` is the ONLY verb that writes a free-form operator string. The station verbs
    validate their value against a closed vocabulary before the lock is taken (case
    `illegal_station_exit_4`), so they cannot emit arbitrary text; `--by` and `--date` were
    interpolated raw into `f"{indent}{key}: {value}"`. A signer name carrying a colon therefore
    wrote an UNPARSEABLE signed plan.yaml and exited 0 -- and T-09 has just closed the editor
    route that would have repaired it by hand, so the document was left unrecoverable through
    any sanctioned path.

    THE ASSERTION IS A ROUND TRIP, NOT A GREP. Checking for a quoted substring would bless one
    particular escaping style and miss the two failures that are not syntax errors at all:
    `#845 owner` is swallowed as a comment, and a bare `yes` reloads as the BOOLEAN True. What
    matters is that the value read back equals the value passed, whatever quoting achieves it.

    EITHER OUTCOME IS ACCEPTABLE, and the test says so deliberately: refuse and leave the file
    untouched, or write it correctly. What is forbidden is the third thing it did -- report
    success while leaving the document broken.
    """
    hostile = [
        ("colon and space breaks the mapping", "Dr: Bob"),
        ("a leading hash is swallowed as a comment", "#845 owner"),
        ("a YAML boolean word must stay a STRING", "yes"),
        ("a trailing colon", "Bob:"),
        ("a quote of its own", "O'Brien \"Bob\""),
        ("a bare newline", "Bob\nEvil: true"),
    ]
    for label, by in hostile:
        root, plan = fixture_root()
        try:
            before = write(plan, render_plan(ids(1, 2)))
            r = run_verb("sign-approval", "--file", plan, "--by", by, "--date", "2026-08-30")
            after = read(plan)
            if r.returncode != 0:
                check(f"F-02 ({label}): refused, and the plan is byte-identical",
                      after == before, f"rc={r.returncode} stderr={r.stderr[:200]!r}")
                continue
            try:
                doc = yaml.safe_load(after)
                loaded = True
            except yaml.YAMLError as exc:
                doc, loaded = None, False
                detail = str(exc)[:200]
            check(f"F-02 ({label}): it exited 0, so the plan it wrote MUST parse",
                  loaded, detail if not loaded else "")
            if not loaded:
                continue
            got = (doc.get("approval") or {}).get("approved_by")
            check(f"F-02 ({label}): approved_by round-trips as the exact string passed",
                  got == by, f"passed={by!r} reloaded={got!r}")
            check(f"F-02 ({label}): the tasks are undisturbed",
                  len(doc.get("tasks") or []) == 2, repr(doc.get("tasks")))
        finally:
            shutil.rmtree(root, ignore_errors=True)

    # NEGATIVE CONTROL. An ordinary name must still land in the BARE form. Without this, quoting
    # every value unconditionally would pass every case above while needlessly churning the
    # appearance of a document a human signs and reads.
    root, plan = fixture_root()
    try:
        write(plan, render_plan(ids(1, 2)))
        run_verb("sign-approval", "--file", plan, "--by", "Mike Ruangutai",
                 "--date", "2026-08-30")
        after = read(plan)
        check("F-02 NEGATIVE CONTROL: an ordinary signer name stays unquoted",
              "approved_by: Mike Ruangutai" in after, after[:400])
    finally:
        shutil.rmtree(root, ignore_errors=True)



def case_sign_approval_is_the_only_signer():
    """Every other verb still leaves the approval bytes byte-identical — the D-04 promise, now
    asserted against the THREE new writing verbs rather than only against apply."""
    root, plan = fixture_root()
    try:
        write(plan, render_plan(ids(1, 2)))
        head = read(plan).split("tasks:")[0]
        run_verb("set-task-station", "--file", plan, "--task", "T-01", "--station", "building")
        run_verb("set-feature-station", "--file", plan, "--station", "building")
        after_head = read(plan).split("tasks:")[0]
        check("neither station verb writes the approval mapping",
              "status: pending" in after_head and "approved_by" not in after_head,
              after_head)
        check("the approval block's own bytes are untouched by the station verbs",
              DEFAULT_APPROVAL in read(plan), after_head)
        check("only the feature status key was added to the head",
              after_head.count("status: building") == 1, after_head)
        _ = head
    finally:
        shutil.rmtree(root, ignore_errors=True)

def case_1103_sign_approval_refuses_a_governed_agent():
    """#1103: the structural identity check, checked INSIDE cmd_sign_approval itself rather
    than only by the calling hook's text-parsing denylist. HARNESS_AGENT_TYPE is what the OMP
    host injects onto a governed subagent's own Bash environment (never derivable from this
    command's own argv or text) — so this is the same signal plan-sign-gate.py's hook reads,
    checked from the other end of the same call."""
    root, plan = fixture_root()
    try:
        write(plan, render_plan(ids(1, 2)))
        before = read(plan)
        env = dict(os.environ, HARNESS_AGENT_TYPE="harness-pm")
        r = run_verb("sign-approval", "--file", plan, "--by", "harness-pm",
                     "--date", "2026-08-30", env=env)
        after = read(plan)
        check("a governed agent's sign-approval exits 10", r.returncode == 10,
              f"rc={r.returncode} {r.stderr!r}")
        check("the refusal names the agent and REQ-05/DEC-120",
              "harness-pm" in r.stderr and "REQ-05" in r.stderr, r.stderr)
        check("the plan is untouched — no partial write on refusal", after == before, after[:400])
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_1103_sign_approval_negative_control_absent_is_main_session():
    """NEGATIVE CONTROL for the case above: an ABSENT HARNESS_AGENT_TYPE is the main session,
    the same exemption plan-sign-gate.py's own hook already uses (`if not (payload.get
    ("agent_type") or ""): sys.exit(0)`), and one this whole codebase applies consistently
    (dispatch-guard.sh, bash-write-guard.sh, check-domain.sh, validate-digest.py). Refusing on
    absence here would refuse the main session's own legitimate signature — a stricter check
    that is provably wrong, not merely untested."""
    root, plan = fixture_root()
    try:
        write(plan, render_plan(ids(1, 2)))
        env = {k: v for k, v in os.environ.items() if k != "HARNESS_AGENT_TYPE"}
        r = run_verb("sign-approval", "--file", plan, "--by", "Mike Ruangutai",
                     "--date", "2026-08-30", env=env)
        after = read(plan)
        check("an absent HARNESS_AGENT_TYPE may still sign", r.returncode == 0,
              f"rc={r.returncode} {r.stderr!r}")
        check("the signature actually lands", "approved_by: Mike Ruangutai" in after, after[:400])
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_f02_verify_signature_is_not_dead_code():
    """FEAT-41, cycle 1 QA, med, and MUTATION-PROVEN by them: `_verify_signature`'s refusal was
    UNREACHABLE in this suite. Disabling the whole function with an early `return` broke nothing
    -- every F-02 hostile value is already stopped one layer earlier by `_field_lines`, so the
    "second independent layer" the F-02 commit claimed was, from the suite's point of view,
    indistinguishable from dead code. A later refactor could have reintroduced raw interpolation
    for one value class and shipped green.

    FORCED THROUGH THE FRONT DOOR, NOT BY PATCHING THE MODULE. This suite drives the real CLI in
    a subprocess, and a monkeypatched stand-in would prove something about a stand-in. A base
    plan carrying a DUPLICATE `approved_by` inside its approval block reaches the comparison with
    the escaping fully intact: the signature is spliced in correctly, and then YAML's last-wins
    duplicate resolution hands the LATER value back, so the reloaded name is not the one signed.
    That is the exact condition the comparison loop exists for, and nothing else in this suite
    reaches it.

    IT IS ALSO A REAL DOCUMENT, not a contrivance: a plan that already carried a stale signer
    line is how a duplicate key gets there.
    """
    root, plan = fixture_root()
    try:
        write(plan, "schema: plan/1\nfeature: FEAT-99-fixture\napproval:\n"
                    "  status: pending\n  approved_by: null\n  approved_by: stale-signer\n"
                    "tasks:\n  - id: T-01\n    title: t\n")
        before = read(plan)
        r = run_verb("sign-approval", "--file", plan, "--by", "Mike Ruangutai",
                     "--date", "2026-08-30")
        check("F-02 layer two: a signature that would reload as a DIFFERENT name is REFUSED at "
              "exit 5 — the comparison loop, which `_field_lines` cannot cover",
              r.returncode == 5, f"rc={r.returncode} stderr={r.stderr[:200]!r}")
        # ASSERTED ON stderr, WHERE REFUSALS GO. The first cut read stdout, which is empty on a
        # refusal, so it failed while the behaviour was correct.
        check("F-02 layer two: the refusal names both the value asked for and the value it "
              "would reload as — a reader cannot act on 'refused' alone",
              "Mike Ruangutai" in r.stderr and "stale-signer" in r.stderr,
              f"stderr={r.stderr[:300]!r}")
        check("F-02 layer two: and the plan is left BYTE-IDENTICAL — a refusal that had already "
              "written would be worse than the bug",
              read(plan) == before, "plan changed")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_add_tasks_alias():
    root, plan = fixture_root()
    try:
        write(plan, render_plan(ids(1, 2)))
        prop = os.path.join(os.path.dirname(plan), "proposal.yaml")
        write(prop, render_plan(ids(1, 3)))
        r = run_verb("add-tasks", "--file", plan, "--proposal", prop)
        check("add-tasks exits 0", r.returncode == 0, f"rc={r.returncode} {r.stderr!r}")
        check("add-tasks adds the new task", "T-03" in read(plan), read(plan))
        check("add-tasks reports through the same ADDED/APPLIED contract as apply",
              "ADDED T-03" in r.stdout and "APPLIED" in r.stdout, r.stdout)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_apply_still_refuses_a_changed_value():
    """apply's exit 7 must survive the arrival of four sibling verbs."""
    root, plan = fixture_root()
    try:
        write(plan, render_plan(ids(1, 2)))
        prop = os.path.join(os.path.dirname(plan), "proposal.yaml")
        write(prop, render_plan(ids(1, 2), titles={"T-02": "a DIFFERENT title"}))
        r = run_apply(plan, prop)
        check("apply still exits 7 on a changed task value after the new verbs exist",
              r.returncode == 7, f"rc={r.returncode} {r.stderr!r}")
    finally:
        shutil.rmtree(root, ignore_errors=True)



def case_high1_apply_cannot_mint_the_station_only_marker():
    """FEAT-41 HIGH-1, cycle 4. `apply` wrote the `station_only: true` credential onto a
    task-bearing SIGNED plan and exited 0, reporting APPLIED.

    `_verify_spliced` parses the merged result with `yaml.safe_load`, which answers "is this
    YAML" and not "is this a legal plan". So the schema rule the loader enforces was invisible to
    the writer, and the tool cheerfully persisted a document that no reader can load -- the same
    shape as the splice defect STEP 9 was added for.

    THE FIX GIVES THE PLAN SCHEMA ONE HOME. `validate_plan_doc` is extracted from `load_plan` and
    called by both, so the reader and the writer cannot disagree about what a legal plan is. A
    writer-side copy of the rule would be a second place for it to stop being true.
    """
    root, plan = fixture_root()
    try:
        # A SCHEMA-VALID BASE, deliberately, and `render_plan` cannot supply one: its tasks omit
        # REQUIRED_TASK_FIELDS, so the do-no-harm rule correctly SKIPS such a base and the case
        # would pass for the wrong reason. The scenario that matters is minting the marker onto a
        # LEGAL signed plan.
        write(plan, "schema: plan/1\nfeature: FEAT-99-fixture\nstatus: building\n"
                    "approval:\n  status: approved\n  approved_by: X\n  date: 2026-01-01\n"
                    "tasks:\n  - id: T-01\n    title: t\n    change_type: logic\n"
                    "    execution_mode: main-session-direct\n    status: done\n"
                    "    files: [a.py]\n    verify: run it\n    intent: do it\n")
        before = read(plan)
        prop = os.path.join(root, "prop.yaml")
        write(prop, "schema: plan/1\nfeature: FEAT-99-fixture\nstation_only: true\ntasks: []\n")
        r = run_verb("apply", "--file", plan, "--proposal", prop)
        check("HIGH-1: `apply` REFUSES to mint station_only onto a plan that has tasks",
              r.returncode != 0, f"rc={r.returncode} stdout={r.stdout[:200]!r}")
        check("HIGH-1: and the plan is left BYTE-IDENTICAL — a refusal that had already written "
              "would be the defect it is meant to prevent",
              read(plan) == before, "plan changed")
        check("HIGH-1: the refusal names the marker, so the operator can act on it",
              "station_only" in (r.stderr + r.stdout),
              f"stderr={r.stderr[:200]!r} stdout={r.stdout[:200]!r}")
    finally:
        shutil.rmtree(root, ignore_errors=True)



def main():
    case_proposal_indent_differs_from_base()
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

    case_set_task_station_one_line()
    case_set_task_station_unknown_id()
    case_set_feature_station_insert_and_replace()
    case_illegal_station_exit_4()
    case_sign_approval()
    case_f02_sign_approval_cannot_write_an_unparseable_signature()
    case_f02_verify_signature_is_not_dead_code()
    case_high1_apply_cannot_mint_the_station_only_marker()
    case_sign_approval_is_the_only_signer()
    case_1103_sign_approval_refuses_a_governed_agent()
    case_1103_sign_approval_negative_control_absent_is_main_session()
    case_add_tasks_alias()
    case_apply_still_refuses_a_changed_value()

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
