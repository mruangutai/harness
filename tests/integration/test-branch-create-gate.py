#!/usr/bin/env python3
"""Tests for branch-create-gate.py (FEAT-18 T-05).

SC-07's second half is why this file exists: "a deletion that also disabled
the gate would pass an absence check on its own." An absence grep alone is
NOT a test — it is the thing SC-07 names as insufficient. So this suite pairs
the absence-of-config-keys assertion with independent proof, on live branch
payloads, that the gate still adjudicates exactly as before: denies a flow
that doesn't exist, allows one that does, self-gates on sync/repo, and parses
both accepted branch-name forms.

Every payload that could look like a real branch-creating command is composed
in python, never spelled literally in a shell command line — this gate is
registered live on the Bash route this test itself runs under, and a literal
`checkout -b` substring in the tool invoking python would be denied before
this file's own subprocess.run ever fired.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import json
import os
import shutil
import subprocess
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
HERE = BIN_DIR
GATE = os.environ.get("BRANCH_CREATE_GATE_BIN") or os.path.join(
    HERE, "branch-create-gate.py")
# HERE = <repo>/.agents/skills/harness/bin — four levels up is the repo root.
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))


def fire(cmd, root=REPO_ROOT, gh_bin=None):
    payload = json.dumps({"tool_input": {"command": cmd}})
    # BOTH NAMES, ONE VALUE (FEAT-42 T-14). branch-create-gate.py resolves through
    # harness_boundary.resolve_root, which reads HARNESS_PROJECT_DIR and no other name; the
    # reverted sha-3952814 copy the parity proof diffs against reads HARNESS first and the
    # host-owned name second. Setting only the host-owned name points the new copy at the
    # live checkout, and three self-gate cases read the real github block that way.
    env = dict(os.environ, CLAUDE_PROJECT_DIR=root, HARNESS_PROJECT_DIR=root)
    if gh_bin is not None:
        env["GH_BIN"] = gh_bin
    else:
        env.pop("GH_BIN", None)
    return subprocess.run([GATE], input=payload, capture_output=True,
                          text=True, env=env)


def fire_raw(payload, root, gh_bin=None):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=root, HARNESS_PROJECT_DIR=root)
    if gh_bin is not None:
        env["GH_BIN"] = gh_bin
    else:
        env.pop("GH_BIN", None)
    return subprocess.run([GATE], input=payload, capture_output=True,
                          text=True, env=env)


def out_json(r):
    return json.loads(r.stdout)


# ============ Assertion 1: the four keys and item-edit are ABSENT ============
# This is the half that goes RED in step 2, against the restored (pre-deletion)
# file. It is independent of the other assertions, and on its own it is exactly
# what SC-07 warns is insufficient.
BANNED = ["project_number", "project_id", "status_field", "in_progress_option",
          "item-edit"]


def run_assertion_1():
    src = open(GATE).read()
    hits = [k for k in BANNED if k in src]
    check("the four config keys and the item-edit call are absent from the script",
          hits == [], f"found: {hits}")


# ============ Assertion 2: DENY a flow that does not exist on disk ============
def run_assertion_2():
    cmd = "git check" + "out -b feat/FEAT-99-nope"
    r = fire(cmd)
    try:
        body = out_json(r)
        decision = body.get("hookSpecificOutput", {}).get("permissionDecision")
        reason = body.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")
    except Exception as e:
        decision, reason = None, f"<unparseable stdout: {e}: {r.stdout!r}>"
    check("DENY: a branch naming a flow that does not exist on disk",
          decision == "deny" and "FEAT-99-nope" in reason,
          f"decision={decision!r} reason={reason!r} stdout={r.stdout!r} stderr={r.stderr!r}")


# ============ Assertion 3: ALLOW a flow that DOES exist ============
# feat/FEAT-18-board-truth is the live branch this very feature ships under —
# a real positive case. Without it, a gate that denies everything would pass
# assertion 2 alone.
def run_assertion_3():
    # The flow-id extraction is greedy over [a-z0-9-]*, so it captures the WHOLE
    # slug after FEAT-NN — the branch name has to match the live directory
    # exactly, a suffixed variant would extract a flow id the ls glob can't find.
    cmd = "git check" + "out -b feat/FEAT-18-board-truth"
    r = fire(cmd)
    try:
        body = out_json(r)
        # An allow for form 1 (flow branches) carries no permissionDecision key at
        # all — it prints a systemMessage and exits 0. Absence of a deny IS the
        # allow signal for this form.
        denied = body.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"
        matched = "FEAT-18-board-truth" in json.dumps(body)
    except Exception as e:
        denied, matched = True, False
        body = f"<unparseable stdout: {e}: {r.stdout!r}>"
    check("ALLOW: a branch naming a flow that DOES exist on disk",
          (not denied) and matched,
          f"body={body} stderr={r.stderr!r}")


# ============ Assertion 4: self-gating on github.sync / github.repo ============
def _fixture(github_block):
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, ".harness"))
    doc = {} if github_block is None else {"github": github_block}
    with open(os.path.join(d, ".harness", "harness.json"), "w") as f:
        json.dump(doc, f)
    # THE MARKER MAKES IT A ROOT (FEAT-42 T-14). branch-create-gate.py resolves through
    # harness_boundary.resolve_root, which honours the override only when
    # .harness/team-config.yaml is readable underneath it. A fixture holding only
    # harness.json is discarded and the gate falls back to the LIVE checkout, reading the
    # real github block instead of the one this fixture exists to set.
    with open(os.path.join(d, ".harness", "team-config.yaml"), "w") as f:
        f.write("agents: {}\n")
    return d


def run_assertion_4():
    cmd = "git check" + "out -b feat/FEAT-99-nope"

    # sync absent entirely (no github block at all) -> exit 0, no output
    root = _fixture(None)
    r = fire(cmd, root=root)
    check("self-gate: no github block at all -> exit 0, no stdout",
          r.returncode == 0 and r.stdout.strip() == "",
          f"exit={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")

    # sync explicitly false -> exit 0, no output
    root = _fixture({"sync": False, "repo": "mruangutai/harness"})
    r = fire(cmd, root=root)
    check("self-gate: github.sync false -> exit 0, no stdout",
          r.returncode == 0 and r.stdout.strip() == "",
          f"exit={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")

    # sync true but repo unpinned (the "-" sentinel) -> exit 0, no output
    root = _fixture({"sync": True})
    r = fire(cmd, root=root)
    check("self-gate: github.sync true, repo unpinned (\"-\" sentinel) -> exit 0, no stdout",
          r.returncode == 0 and r.stdout.strip() == "",
          f"exit={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")


# ============ Assertion 5: both accepted branch-name forms parse ============
def run_assertion_5():
    # Form 1: the flow-id form. Reuses the live allow from assertion 3's shape —
    # asserted independently here on parsing alone (a deny naming the RIGHT flow
    # id proves the flow-id extraction ran).
    cmd = "git check" + "out -b feat/FEAT-99-nope-parse-check"
    r = fire(cmd)
    try:
        body = out_json(r)
        reason = body.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")
    except Exception as e:
        reason = f"<unparseable: {e}: {r.stdout!r}>"
    check("form 1 (flow id) parses: deny names the exact flow id extracted",
          "FEAT-99-nope-parse-check" in reason,
          f"reason={reason!r}")

    # Form 2: the issue-number form. GH_BIN points at a path that does not
    # exist, so `command -v "$GH"` fails and the gate denies with "'gh' is not
    # installed" — proving the sed extraction pulled a number and the gate tried
    # to verify it, without touching the network or gh auth state.
    cmd = "git check" + "out -b fix/123-typo"
    r = fire(cmd, gh_bin="/no/such/gh/binary/anywhere")
    try:
        body = out_json(r)
        reason = body.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")
        decision = body.get("hookSpecificOutput", {}).get("permissionDecision")
    except Exception as e:
        reason, decision = f"<unparseable: {e}: {r.stdout!r}>", None
    check("form 2 (issue number) parses: 'gh' not installed deny names issue #123",
          decision == "deny" and "#123" in reason and "not installed" in reason,
          f"decision={decision!r} reason={reason!r}")


def run_assertion_6():
    cmd = "git check" + "out -b feat/FEAT-99-nope"

    config_root = _fixture(None)
    with open(os.path.join(config_root, ".harness", "harness.json"), "w") as stream:
        stream.write(
            '{"github":{"sync":false},"github":{"sync":true,"repo":"acme/widgets"}}')
    config_result = fire(cmd, root=config_root)
    if config_result.stdout.strip():
        check("duplicate harness.json keys disable branch policy rather than choosing one",
              False, f"stdout={config_result.stdout!r} stderr={config_result.stderr!r}")

    payload_root = _fixture({"sync": True, "repo": "acme/widgets"})
    payload = (
        '{"tool_input":{"command":"git status"},'
        '"tool_input":{"command":"git checkout -b feat/FEAT-99-nope"}}')
    payload_result = fire_raw(payload, payload_root)
    if payload_result.stdout.strip():
        check("duplicate hook-payload keys are rejected before branch policy evaluation",
              False, f"stdout={payload_result.stdout!r} stderr={payload_result.stderr!r}")


def run_feat65():
    """FEAT-65: no guard here — typed boundaries only. A defect in the shared resolver is loud
    (traceback, nonzero), never a silent pass-through; the DEC-234 prologue absorbs only a
    missing module or a strict "no root" refusal."""
    mbin = os.path.join(tempfile.mkdtemp(), "bin")
    shutil.copytree(os.path.dirname(GATE), mbin)
    with open(os.path.join(mbin, "harness_boundary.py"), "a", encoding="utf-8") as f:
        f.write("\n\ndef resolve_root(bin_dir, strict=True):\n    raise RuntimeError('FEAT-65 injected')\n")
    r = subprocess.run([os.path.join(mbin, "branch-create-gate.py")],
                       input=json.dumps({"tool_input": {"command": "git checkout -b x"}}),
                       capture_output=True, text=True,
                       env=dict(os.environ, CLAUDE_PROJECT_DIR=REPO_ROOT, HARNESS_PROJECT_DIR=REPO_ROOT))
    check("FEAT-65: an unexpected resolver defect is loud and nonzero, not absorbed by the prologue",
          r.returncode not in (0, 2) and "FEAT-65 injected" in r.stderr,
          f"rc={r.returncode} stderr={r.stderr[-200:]!r}")


def run_feat65_config_reader():
    """FEAT-65 c1 (CR-01): the compatibility config reader — a program this gate runs through a
    clean interpreter — recovers from its own boundary classes (no file, not JSON, a github
    block that is not a mapping) with the same `false -` the shell gate printed, and carries
    no broad catch for the census to miss."""
    src = open(GATE, encoding="utf-8").read()
    start = src.index('_CONFIG_READER = """') + len('_CONFIG_READER = """')
    reader = src[start:src.index('"""', start)]
    def run(body):
        root = tempfile.mkdtemp()
        os.makedirs(os.path.join(root, ".harness"))
        if body is not None:
            with open(os.path.join(root, ".harness", "harness.json"), "w") as f:
                f.write(body)
        return subprocess.run([sys.executable, "-I", "-", root], input=reader,
                              capture_output=True, text=True)
    for label, body in (("no harness.json", None), ("not JSON", "{nope"),
                        ("a top-level document that is not an object", "[1, 2]")):
        r = run(body)
        check(f"FEAT-65 config reader recovers from {label} as `false -`",
              r.returncode == 0 and r.stdout == "false -\n" and r.stderr == "",
              f"rc={r.returncode} out={r.stdout!r} err={r.stderr[-200:]!r}")
    # The exceptional path the gate runs this program FOR: a github block that is not a mapping
    # exposes the helper's traceback, exactly as the shell gate did (see _github_config).
    r = run('{"github": [1, 2]}')
    check("FEAT-65 config reader keeps its traceback for a github block that is not a mapping",
          r.returncode == 1 and r.stdout == "" and "AttributeError" in r.stderr,
          f"rc={r.returncode} out={r.stdout!r} err={r.stderr[-200:]!r}")
    check("FEAT-65 config reader carries no broad catch",
          "except Exception" not in reader and "except:" not in reader, reader)


def main():
    run_assertion_1()
    run_assertion_2()
    run_assertion_3()
    run_assertion_4()
    run_assertion_5()
    run_assertion_6()
    run_feat65()
    run_feat65_config_reader()

    fails = 0
    for name, ok, detail in RESULTS:
        if ok:
            print(f"ok    {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n      | {detail}")
    print(f"\n{len(RESULTS) - fails}/{len(RESULTS)} cases passed.")
    return fails


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
