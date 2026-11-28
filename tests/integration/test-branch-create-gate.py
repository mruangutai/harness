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
from integration_support import ROOT as _ROOT, BIN as _BIN
import ast  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402

from check_support import Checks  # noqa: E402
from git_support import checked_git, commit_all, init_repo  # noqa: E402
from harness_config_support import build_config, write_config  # noqa: E402

REPO_ROOT = str(_ROOT)
GATE = os.environ.get("BRANCH_CREATE_GATE_BIN") or str(_BIN / "branch-create-gate.py")
# A gh path that does not exist: the issue form denies "'gh' is not installed" offline.
NO_GH = "/no/such/gh/binary/anywhere"

C = Checks()
check = C.check


def fire_raw(payload, root, gh_bin=None, gate=GATE):
    # ONE NAME, ONE VALUE (FEAT-42 T-14). branch-create-gate.py resolves through
    # harness_boundary.resolve_root, which reads HARNESS_PROJECT_DIR and no other name; the
    # reverted sha-3952814 copy the parity proof diffs against reads HARNESS_PROJECT_DIR
    # first, so that one name points both copies at the same root, and three self-gate
    # cases read the real github block that way. gh_bin None removes GH_BIN from the env.
    env = dict(os.environ, HARNESS_PROJECT_DIR=root)
    if gh_bin is not None:
        env["GH_BIN"] = gh_bin
    else:
        env.pop("GH_BIN", None)
    return subprocess.run([gate], input=payload, capture_output=True,
                          text=True, env=env)


def fire(cmd, root=REPO_ROOT, gh_bin=None, gate=GATE):
    return fire_raw(json.dumps({"tool_input": {"command": cmd}}), root, gh_bin, gate)


def _hook(r):
    """(decision, reason, body) from the gate's hook JSON; (None, marker, None) when unparseable."""
    try:
        body = json.loads(r.stdout)
        out = body.get("hookSpecificOutput", {})
        return out.get("permissionDecision"), out.get("permissionDecisionReason", ""), body
    except Exception as e:
        return None, f"<unparseable stdout: {e}: {r.stdout!r}>", None


def _fire_corpus(run):
    """(command, should_match, result) per corpus row in corpus order; the rows run
    concurrently because each spawn is independent and reads its root and bin only."""
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(run, [cmd for cmd, _ in APPLICABILITY_CORPUS]))
    return [(cmd, match, r) for (cmd, match), r in zip(APPLICABILITY_CORPUS, results)]


# ============ THE APPLICABILITY CORPUS (FEAT-2274 SC-02) ============
# (command, should_match): whether the gate's own matcher reads a branch NAME being created out of
# the command. ONE pure literal, so another suite reads it with ast.literal_eval without running
# this file, and the Python gate and the extension's classifier are held to the same forms. Each
# branch-creating spelling is split by implicit string concatenation, for the reason the module
# docstring gives; the AST still holds one constant. Unrelated controls must never start matching.
APPLICABILITY_CORPUS = [
    ("git check" "out -b feat/FEAT-99-nope", True),
    ("git check" "out -B fix/123-typo", True),
    ("git -C repo check" "out -b feat/FEAT-99-nope", True),
    ("cd repo && git check" "out -b fix/123-typo", True),
    ("git check" "out --track -b fix/123-typo origin/main", True),
    ("git check" "out -b=fix/123-typo", True),
    ("git sw" "itch -c fix/123-typo", True),
    ("git sw" "itch --create fix/123-typo", True),
    ("git -c core.x=y sw" "itch -C fix/123-typo", True),
    ("git work" "tree add ../wt -b fix/123-typo", True),
    ("git work" "tree add -B fix/123-typo ../wt", True),
    ("git bra" "nch fix/123-typo", True),
    ("git -C repo bra" "nch fix/123-typo", True),
    ("git bra" "nch fix/123-typo main", True),
    ("git status", False),
    ("git branch -d x", False),
    ("git branch -D old", False),
    ("git branch", False),
    ("git branch --list", False),
    ("git branch --show-current", False),
    ("git checkout main", False),
    ("git checkout -- file.txt", False),
    ("git check" "out -b", False),
    ("git switch main", False),
    ("git worktree add ../wt main", False),
    ("git worktree list", False),
    ("git log --oneline", False),
    ("echo git branch", False),
    ("echo hi", False),
    ("gh pr close 5", False),
]


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
    decision, reason, _ = _hook(r)
    check("DENY: a branch naming a flow that does not exist on disk",
          decision == "deny" and "FEAT-99-nope" in reason,
          f"decision={decision!r} reason={reason!r} stdout={r.stdout!r} stderr={r.stderr!r}")


# ============ Assertion 3: ALLOW a flow that DOES exist ============
# A real positive case on a fixture root that holds one synthetic flow directory (FEAT-71:
# never a prior feature's folder). Without it, a gate that denies everything would pass
# assertion 2 alone; the same branch against the same root minus the directory must deny,
# so the allow is caused by the directory and nothing else.
FIXTURE_FLOW = "FEAT-90-fixture-flow"


def _flow_fixture(with_flow):
    root = _fixture({"sync": True, "repo": "acme/widgets"})
    if with_flow:
        os.makedirs(os.path.join(root, ".harness", "harness", "features", FIXTURE_FLOW))
    return root


def run_assertion_3():
    # The flow-id extraction is greedy over [a-z0-9-]*, so it captures the WHOLE
    # slug after FEAT-NN — the branch name has to match the fixture directory
    # exactly, a suffixed variant would extract a flow id the corpus can't find.
    cmd = "git check" + "out -b feat/" + FIXTURE_FLOW
    r = fire(cmd, root=_flow_fixture(True))
    # An allow for form 1 (flow branches) carries no permissionDecision key at
    # all — it prints a systemMessage and exits 0. Absence of a deny IS the
    # allow signal for this form; unparseable stdout matches nothing and fails.
    decision, reason, body = _hook(r)
    denied = decision == "deny"
    matched = body is not None and FIXTURE_FLOW in json.dumps(body)
    body = reason if body is None else body
    check("ALLOW: a branch naming a flow that DOES exist on disk",
          (not denied) and matched,
          f"body={body} stderr={r.stderr!r}")

    r = fire(cmd, root=_flow_fixture(False))
    decision, _, _ = _hook(r)
    check("DENY: the same branch once the fixture flow directory is absent",
          decision == "deny", f"decision={decision!r} stdout={r.stdout!r} stderr={r.stderr!r}")


# ============ Assertion 4: self-gating on github.sync / github.repo ============
def _marked_root():
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, ".harness"))
    # THE MARKER MAKES IT A ROOT (FEAT-42 T-14). branch-create-gate.py resolves through
    # harness_boundary.resolve_root, which honours the override only when
    # .harness/team-config.yaml is readable underneath it. A fixture holding only
    # harness.json is discarded and the gate falls back to the LIVE checkout, reading the
    # real github block instead of the one this fixture exists to set.
    with open(os.path.join(d, ".harness", "team-config.yaml"), "w") as f:
        f.write("agents: {}\n")
    return d


def _fixture(github_block):
    d = _marked_root()
    write_config(os.path.join(d, ".harness", "harness.json"),
                 {} if github_block is None else {"github": github_block})
    return d


def run_assertion_4():
    cmd = "git check" + "out -b feat/FEAT-99-nope"

    # no github block at all: the schema default is sync off -> exit 0, no output
    root = _fixture(None)
    r = fire(cmd, root=root)
    check("self-gate: no github block at all -> exit 0, no stdout",
          r.returncode == 0 and r.stdout.strip() == "",
          f"exit={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")

    # sync explicitly false -> exit 0, no output
    root = _fixture({"sync": False, "repo": "acme/widgets"})
    r = fire(cmd, root=root)
    check("self-gate: github.sync false -> exit 0, no stdout",
          r.returncode == 0 and r.stdout.strip() == "",
          f"exit={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")

    # sync true with the repo unpinned is an INVALID config (FEAT-2297): the matching branch
    # creation is refused with the loader's diagnosis, never self-gated through.
    root = _config_root(lambda c: json.dumps({**c, "github": {**c["github"], "sync": True}}))
    r = fire(cmd, root=root)
    check("github.sync true with repo unpinned: the branch creation is refused at exit 2 naming "
          "github.repo", _named_refusal(r, _CONFIG_READ) and "github.repo" in r.stderr,
          f"exit={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")


# ============ Assertion 5: both accepted branch-name forms parse ============
def run_assertion_5():
    # Form 1: the flow-id form. Reuses the allow from assertion 3's shape —
    # asserted independently here on parsing alone (a deny naming the RIGHT flow
    # id proves the flow-id extraction ran).
    cmd = "git check" + "out -b feat/FEAT-99-nope-parse-check"
    r = fire(cmd)
    _, reason, _ = _hook(r)
    check("form 1 (flow id) parses: deny names the exact flow id extracted",
          "FEAT-99-nope-parse-check" in reason,
          f"reason={reason!r}")

    # Form 2: the issue-number form. GH_BIN points at a path that does not
    # exist, so `command -v "$GH"` fails and the gate denies with "'gh' is not
    # installed" — proving the sed extraction pulled a number and the gate tried
    # to verify it, without touching the network or gh auth state.
    cmd = "git check" + "out -b fix/123-typo"
    r = fire(cmd, gh_bin=NO_GH)
    decision, reason, _ = _hook(r)
    check("form 2 (issue number) parses: 'gh' not installed deny names issue #123",
          decision == "deny" and "#123" in reason and "not installed" in reason,
          f"decision={decision!r} reason={reason!r}")


def run_assertion_6():
    cmd = "git check" + "out -b feat/FEAT-99-nope"

    config_root = _config_root(
        lambda c: json.dumps(c)[:-1] + ',"github":{"sync":true,"repo":"acme/widgets"}}')
    config_result = fire(cmd, root=config_root)
    check("duplicate harness.json keys refuse the branch creation at exit 2 rather than choosing "
          "one", _named_refusal(config_result, _CONFIG_READ) and "duplicate key" in config_result.stderr,
          f"stdout={config_result.stdout!r} stderr={config_result.stderr!r}")

    payload_root = _fixture({"sync": True, "repo": "acme/widgets"})
    payload = (
        '{"tool_input":{"command":"git status"},'
        '"tool_input":{"command":"git checkout -b feat/FEAT-99-nope"}}')
    payload_result = fire_raw(payload, payload_root)
    if payload_result.stdout.strip():
        check("duplicate hook-payload keys are rejected before branch policy evaluation",
              False, f"stdout={payload_result.stdout!r} stderr={payload_result.stderr!r}")


_REFUSAL_HEAD = "branch-create-gate: BLOCKED — the gate could not run ("
_REFUSAL_TAIL = "); the command it guards is refused rather than left unchecked."


def _faulted_bin(module=None, text=""):
    """A disposable copy of the bin, with `text` appended to `module` when one is named."""
    mbin = os.path.join(tempfile.mkdtemp(), "bin")
    shutil.copytree(os.path.dirname(GATE), mbin)
    if module:
        with open(os.path.join(mbin, module), "a", encoding="utf-8") as f:
            f.write(text)
    return mbin


def _run_in(mbin, command, root):
    return fire(command, root, NO_GH, os.path.join(mbin, "branch-create-gate.py"))


def _named_refusal(r, detail):
    return (r.returncode == 2 and not r.stdout.strip()
            and _REFUSAL_HEAD + detail in r.stderr and _REFUSAL_TAIL in r.stderr)


def _untouched(r):
    return r.returncode == 0 and not r.stdout.strip() and not r.stderr.strip()


def run_corpus_agreement():
    """A mislabelled corpus row would teach the failure-mode cases the wrong answer, so each row
    is held to the working gate first: a matched name always draws an answer (a deny or a
    systemMessage), an unrelated command draws nothing."""
    root = _fixture({"sync": True, "repo": "acme/widgets"})
    for cmd, match, r in _fire_corpus(lambda cmd: fire(cmd, root, NO_GH)):
        check(f"corpus row agrees with the healthy gate ({'match' if match else 'unrelated'}): "
              f"{cmd!r}", r.returncode == 0 and bool(r.stdout.strip()) == match,
              f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr[-200:]!r}")


def run_feat65():
    """FEAT-65's injected resolver defect, kept, under FEAT-2274's contract: matching precedes
    fail-closed execution. A branch-creating command is REFUSED at exit 2 with a named refusal
    when the gate cannot run; an unrelated command never reaches the resolver and passes."""
    mbin = _faulted_bin("harness_boundary.py",
                        "\n\ndef resolve_root(bin_dir, strict=True):\n"
                        "    raise RuntimeError('FEAT-65 injected')\n")
    r = _run_in(mbin, "git check" + "out -b x", REPO_ROOT)
    check("FEAT-65: an unexpected resolver defect REFUSES a matching branch creation at exit 2, "
          "named", _named_refusal(r, "RuntimeError: FEAT-65 injected"),
          f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr[-300:]!r}")
    for cmd, match, r in _fire_corpus(lambda cmd: _run_in(mbin, cmd, REPO_ROOT)):
        if match:
            check(f"resolver defect: a matching command is refused, named: {cmd!r}",
                  _named_refusal(r, "RuntimeError: FEAT-65 injected"),
                  f"rc={r.returncode} stderr={r.stderr[-300:]!r}")
        else:
            check(f"resolver defect: an unrelated command passes untouched: {cmd!r}",
                  _untouched(r),
                  f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr[-300:]!r}")


def run_no_root():
    """No marker under the override or the copied bin's derived root: a branch creation keeps
    today's exit 2, now named; an unrelated command — refused today too — passes."""
    mbin = _faulted_bin()
    noroot = tempfile.mkdtemp()
    r = _run_in(mbin, "git sw" + "itch -c fix/123-typo", noroot)
    check("no harness root: a matching branch creation is refused at exit 2, named",
          _named_refusal(r, "no harness root could be resolved from "),
          f"rc={r.returncode} stderr={r.stderr[-300:]!r}")
    r = _run_in(mbin, "git branch -d x", noroot)
    check("no harness root: an unrelated command exits 0 untouched", _untouched(r),
          f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr[-300:]!r}")


def run_body_failure():
    """The gate's own body fails after the root resolves: its config read raises."""
    mbin = _faulted_bin("artifact_accessors.py",
                        "\n\ndef load_harness_json(*args, **kwargs):\n"
                        "    raise RuntimeError('FEAT-2274 body injected')\n")
    root = _fixture({"sync": True, "repo": "acme/widgets"})
    r = _run_in(mbin, "git work" + "tree add ../wt -b fix/123-typo", root)
    check("body failure: a matching branch creation is refused at exit 2, named",
          _named_refusal(r, "RuntimeError: FEAT-2274 body injected"),
          f"rc={r.returncode} stderr={r.stderr[-300:]!r}")
    r = _run_in(mbin, "git status", root)
    check("body failure: an unrelated command exits 0 untouched", _untouched(r),
          f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr[-300:]!r}")


def run_issue_2107():
    """#2107: a LANDED feature.json whose github.parent is "²" — `"²".isdigit()` is true and
    int() refuses it — once crashed the corpus read at exit 1, which the extension read as "not
    blocking". A flow branch naming that feature is refused by name, never exit 1."""
    root = _flow_fixture(True)
    with open(os.path.join(root, ".harness", "harness", "features", FIXTURE_FLOW,
                           "feature.json"), "w", encoding="utf-8") as f:
        json.dump({"feature_id": FIXTURE_FLOW, "status": "planned",
                   "github": {"parent": "\u00b2"}}, f, ensure_ascii=False)
    init_repo(root, None, git=checked_git)
    commit_all(root, "landed", git=checked_git)
    r = fire("git check" + "out -b feat/" + FIXTURE_FLOW, root=root)
    decision, reason, _ = _hook(r)
    check("#2107: a flow branch over a landed feature.json with github.parent \"²\" is DENIED by "
          "name, never exit 1",
          r.returncode == 0 and decision == "deny"
          and FIXTURE_FLOW in reason and "feature.json" in reason and "parent" in reason,
          f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr[-300:]!r}")


# ============ A CONFIG THAT CANNOT BE READ IS NOT "SYNC OFF" (FEAT-2274 V1) ============
# MIGRATED from FEAT-65 c1 (CR-01)'s config-reader case. That case held a compatibility reader
# program to recovering from no file / not JSON / a non-object document as `false -` (sync off)
# and to exiting 1 with a traceback on a github block that is not a mapping, while the gate
# itself passed. Both encoded the contract V1 names as wrong: a failed config read let a branch
# creation through unchecked. Each shape now refuses a matching command by name at exit 2.
_CONFIG_READ = "harness.json could not be read: "
_CONFIG_FAULTS = (
    ("no harness.json", None),
    ("not JSON", lambda c: json.dumps(c)[:-1]),
    ("a top-level document that is not an object", lambda c: json.dumps([c])),
    ("duplicate keys", lambda c: json.dumps(c)[:-1] + ',"github":{"sync":true,"repo":"o/r"}}'),
    ("a github block that is a list", lambda c: json.dumps({**c, "github": [1, 2]})),
    ("a github block that is null", lambda c: json.dumps({**c, "github": None})),
)
_CONFIG_CONTROLS = (
    ("github.sync false", lambda c: json.dumps({**c, "github": {"sync": False, "repo": "acme/widgets"}})),
    ("no github block", lambda c: json.dumps({k: v for k, v in c.items() if k != "github"})),
)


def _config_root(derive):
    """A marked root whose harness.json is `derive(valid builder config)` as text, or none at
    all when `derive` is None — every invalid config is a visibly corrupted valid one."""
    root = _marked_root()
    if derive is not None:
        with open(os.path.join(root, ".harness", "harness.json"), "w", encoding="utf-8") as f:
            f.write(derive(build_config()))
    return root


def _config_fault_case(label, derive):
    root = _config_root(derive)
    r = fire("git check" + "out -b fix/123-typo", root, NO_GH)
    check(f"config fault ({label}): a matching branch creation is refused at exit 2, named",
          _named_refusal(r, _CONFIG_READ), f"rc={r.returncode} stderr={r.stderr[-300:]!r}")
    r = fire("git status", root, NO_GH)
    check(f"config fault ({label}): an unrelated command exits 0 untouched", _untouched(r),
          f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr[-300:]!r}")


def _config_control_case(label, derive):
    r = fire("git check" + "out -b fix/123-typo", _config_root(derive), NO_GH)
    check(f"valid config, {label}: a matching branch creation exits 0 untouched",
          _untouched(r), f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr[-300:]!r}")


def _broad_catches(path):
    tree = ast.parse(open(path, encoding="utf-8").read())
    return [node.lineno for node in ast.walk(tree) if isinstance(node, ast.ExceptHandler)
            and (node.type is None
                 or isinstance(node.type, ast.Name) and node.type.id == "Exception")]


def run_config_faults():
    for label, derive in _CONFIG_FAULTS:
        _config_fault_case(label, derive)
    for label, derive in _CONFIG_CONTROLS:
        _config_control_case(label, derive)
    hits = _broad_catches(GATE)
    check("the gate's config read carries no broad catch", hits == [], f"lines: {hits}")


def main():
    run_assertion_1()
    run_assertion_2()
    run_assertion_3()
    run_assertion_4()
    run_assertion_5()
    run_assertion_6()
    run_corpus_agreement()
    run_feat65()
    run_no_root()
    run_body_failure()
    run_issue_2107()
    run_config_faults()
    return C.report()


if __name__ == "__main__":
    sys.exit(main())
