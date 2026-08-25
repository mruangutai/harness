#!/usr/bin/env python3
"""Tests for branch-create-gate.sh (FEAT-18 T-05).

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
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "branch-create-gate.sh")
# HERE = <repo>/.agents/skills/harness/bin — four levels up is the repo root.
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))


def fire(cmd, root=REPO_ROOT, gh_bin=None):
    payload = json.dumps({"tool_input": {"command": cmd}})
    env = dict(os.environ, CLAUDE_PROJECT_DIR=root)
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


def main():
    run_assertion_1()
    run_assertion_2()
    run_assertion_3()
    run_assertion_4()
    run_assertion_5()

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
