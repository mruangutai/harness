#!/usr/bin/env python3
"""gh-close-gate.py — the PreToolUse Bash hook that refuses a hand-typed issue close.

Every case feeds hook JSON on stdin and asserts the process's STDOUT, because that is the
whole contract: a deny is exit 0 plus a structured permissionDecision, and an allow is exit 0
plus NOTHING. Asserting the exit code alone would pass for both.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_os.path.dirname(_anchor_tests))
import json
import os
import shutil
import subprocess
import sys
import tempfile

from harness_config_support import build_config, write_config  # noqa: E402

BIN = _anchor_bin
GATE = os.environ.get("GH_CLOSE_GATE_BIN") or os.path.join(BIN, "gh-close-gate.py")

fails = 0


def check(name, cond, detail=""):
    global fails
    if cond:
        print(f"ok    {name}")
    else:
        fails += 1
        print(f"FAIL  {name}\n      {detail}")


def _root(sync=True):
    """A throwaway harness root. The gate self-gates on github.sync, so every case needs one."""
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, ".harness"))
    write_config(os.path.join(d, ".harness", "harness.json"), {"github": {"sync": sync, "repo": "o/r"}})
    # THE MARKER, WITHOUT WHICH THE OVERRIDE IS DISCARDED (FEAT-42 T-15). gh-close-gate.py
    # resolves through harness_boundary.resolve_root, which honours HARNESS_PROJECT_DIR only
    # when .harness/team-config.yaml is readable underneath it. A fixture holding only
    # harness.json falls back to the derived root — the LIVE checkout — so every case would
    # read the real github.sync instead of the one it just wrote.
    with open(os.path.join(d, ".harness", "team-config.yaml"), "w") as f:
        f.write("agents: {}\n")
    return d


def _config_root(derive):
    """A marked root whose harness.json is `derive(valid builder config)` as text, or none at
    all when `derive` is None — every invalid config is a visibly corrupted valid one."""
    root = _root()
    path = os.path.join(root, ".harness", "harness.json")
    os.remove(path)
    if derive is not None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(derive(build_config()))
    return root


def gate(command, root=None):
    """(returncode, decision_or_None, reason_or_None)."""
    env = dict(os.environ)
    env["HARNESS_PROJECT_DIR"] = root or _root()
    r = subprocess.run([GATE], input=json.dumps({"tool_input": {"command": command}}),
                       capture_output=True, text=True, env=env)
    if not r.stdout.strip():
        return (r.returncode, None, None)
    doc = json.loads(r.stdout)["hookSpecificOutput"]
    return (r.returncode, doc.get("permissionDecision"), doc.get("permissionDecisionReason"))


# ---------------- THE APPLICABILITY CORPUS (FEAT-2274 SC-02) ---------------------------------
# (command, should_match): whether the gate's own matcher treats the command as an issue close
# it guards. ONE pure literal, so another suite reads it with ast.literal_eval without running
# this file, and the Python gate and the extension's classifier are held to the same spellings.
# Every entry mirrors a case asserted below; the unrelated controls must never start matching.
APPLICABILITY_CORPUS = [
    ("gh issue close 728 --repo x/y", True),
    ("gh api -X PATCH repos/o/r/issues/9 -f state=closed", True),
    ("cd /tmp && gh issue close 728", True),
    ("FOO=1 gh issue close 728", True),
    ("echo hi | gh issue close 728", True),
    ("true; gh issue close 728", True),
    ("gh api -f state=closed -X PATCH repos/o/r/issues/9", True),
    ("gh api repos/o/r/issues/9 -X PATCH -f state=closed", True),
    ("gh issue close 1 && python3 .claude/skills/harness/bin/gh-sync.py ship d", True),
    ('gh "issue" close 5', True),
    ("gh 'issue' 'close' 5", True),
    ("/opt/homebrew/bin/gh issue close 5", True),
    ("/usr/bin/env gh issue close 5", True),
    ("\\gh issue close 5", True),
    ('eval "gh issue close 5"', True),
    ("bash -c 'gh issue close 5'", True),
    ('sh -c "gh issue close 5"', True),
    ("x=$(gh issue close 5)", True),
    ("$(echo gh) issue close 5", True),
    ('gh api -X PATCH repos/o/r/issues/5 -f state="closed"', True),
    ("gh api --method PATCH repos/o/r/issues/5 --input -", True),
    ('gh api graphql -f query="mutation{closeIssue(input:{issueId:\"x\"}){clientMutationId}}"',
     True),
    ('gh issue close "5', True),
    ("echo it's here; gh issue close 5", True),
    ("echo 'gh issue close is refused here'", True),
    ("echo gh issue close", True),
    ("gh issue view 728", False),
    ("gh issue list --repo o/r --state closed", False),
    ("git status", False),
    ("python3 .claude/skills/harness/bin/gh-sync.py abandon d --reason-file r --yes", False),
    ("python3 .claude/skills/harness/bin/gh-sync.py ship d", False),
    ("gh api repos/o/r/issues/9", False),
    ("echo it's fine", False),
    ("git commit -m \"don't close the loop\"", False),
    ("cat > /tmp/x.md <<'MD'\nthe module's contract\nMD\n"
     "gh issue comment 8 --repo o/r --body-file /tmp/x.md", False),
    ("G=gh; $G issue close 5", False),
    ("gh pr close 5", False),
    ("gh issue close-milestone 5", False),
    ("gh api repos/o/r/issues/5 --jq .state", False),
    ("gh api -X GET repos/o/r/issues/5", False),
    ("git commit -m 'closes the loop'", False),
    ("gh issue edit 5 --add-label wontfix", False),
    ("echo hi", False),
    ("git branch -d x", False),
]


# ---------------- the plain deny, and its three clauses ------------------------------------
rc, decision, reason = gate("gh issue close 728 --repo x/y")
check("gh issue close is DENIED, as a structured permissionDecision at exit 0",
      rc == 0 and decision == "deny", f"rc={rc} decision={decision!r}")

# THE THREE CLAUSES, each its own assertion. They route by the operator's INTENT, and the
# order matters: the likeliest reason for a hand-typed close is that the work is FINISHED, and
# an operator told only "run abandon" would mark shipped work not_planned.
check("clause 1 — the FINISHED route comes first, and its answer is to type nothing",
      reason is not None and "If the work is finished, do nothing here" in reason
      and "gh-sync.py ship" in reason, repr(reason))
check("clause 2 — the DROPPED route is a RUNNABLE command, not a bare name: interpreter, "
      "path, feature dir, the mandatory --reason-file, and --yes",
      reason is not None and "gh-sync.py abandon" in reason
      and "--reason-file" in reason and "--yes" in reason and "python3" in reason,
      repr(reason))
check("clause 3 — the UNTRACKED escape, because this gate cannot resolve an issue number and "
      "a false deny is only acceptable if the refusal says how to recover",
      reason is not None and "not tracked by the harness" in reason
      and "web UI" in reason, repr(reason))

# ---------------- ONE refusal text, asserted by EQUALITY ------------------------------------
rc2, decision2, reason2 = gate("gh api -X PATCH repos/o/r/issues/9 -f state=closed")
check("gh api state=closed is DENIED", rc2 == 0 and decision2 == "deny",
      f"rc={rc2} decision={decision2!r}")
check("the two denials return the IDENTICAL reason string — asserted by equality, so a second "
      "wording cannot drift into existence",
      reason2 == reason, f"{reason2!r} != {reason!r}")

# ---------------- the gh invocation is found in any position ---------------------------------
for cmd in ("cd /tmp && gh issue close 728",
            "FOO=1 gh issue close 728",
            "echo hi | gh issue close 728",
            "true; gh issue close 728"):
    _rc, _d, _ = gate(cmd)
    check(f"denied in position: {cmd!r}", _d == "deny", f"decision={_d!r}")

# Argument order must not matter for the api form.
for cmd in ("gh api -f state=closed -X PATCH repos/o/r/issues/9",
            "gh api repos/o/r/issues/9 -X PATCH -f state=closed"):
    _rc, _d, _ = gate(cmd)
    check(f"denied whatever the argument order: {cmd!r}", _d == "deny", f"decision={_d!r}")

# ---------------- what it must NOT refuse -----------------------------------------------------
for cmd in ("gh issue view 728",
            "gh issue list --repo o/r --state closed",
            "git status",
            "python3 .claude/skills/harness/bin/gh-sync.py abandon d --reason-file r --yes",
            "python3 .claude/skills/harness/bin/gh-sync.py ship d",
            "gh api repos/o/r/issues/9"):
    _rc, _d, _ = gate(cmd)
    check(f"allowed, with NO output at all: {cmd!r}", _rc == 0 and _d is None,
          f"rc={_rc} decision={_d!r}")

# A COMPOUND command carrying both a close and a gh-sync.py call is still DENIED. An earlier
# cut exited 0 early on any line mentioning gh-sync.py, which waved exactly this through.
_rc, _d, _ = gate("gh issue close 1 && python3 .claude/skills/harness/bin/gh-sync.py ship d")
check("a compound command carrying BOTH a close and a gh-sync.py call is still denied",
      _d == "deny", f"decision={_d!r}")

# ---------------- THE EVASIONS A CHARACTER CLASS LET THROUGH ----------------------------------
# Every line below was MEASURED reaching `gh issue close` straight through the gate's first
# cut, which matched the raw command string with `grep -E`. A character class is not a shell
# lexer: it cannot strip a quote, resolve a path, or read inside `eval`. The gate tokenizes
# with `shlex` now, and each of these is a distinct escape route, so each gets its own
# assertion rather than a loop over a blob.
for _cmd, _why in (
    ('gh "issue" close 5',                       "a quote inside the subcommand"),
    ("gh 'issue' 'close' 5",                     "single quotes on every word"),
    ("/opt/homebrew/bin/gh issue close 5",       "an absolute path to the same binary"),
    ("/usr/bin/env gh issue close 5",            "reached through env"),
    ("\\gh issue close 5",                         "a backslash, which defeats an alias not a gate"),
    ('eval "gh issue close 5"',                  "a whole command line inside one eval token"),
    ("bash -c 'gh issue close 5'",               "a whole command line inside one bash -c token"),
    ("sh -c \"gh issue close 5\"",                 "the same through sh"),
    ("x=$(gh issue close 5)",                    "command substitution in an assignment"),
    ("$(echo gh) issue close 5",                 "the binary produced by a substitution"),
    ('gh api -X PATCH repos/o/r/issues/5 -f state="closed"', "a quoted state value"),
    ("gh api --method PATCH repos/o/r/issues/5 --input -",
     "the state hidden in a JSON body on stdin, invisible to the command string"),
    ('gh api graphql -f query="mutation{closeIssue(input:{issueId:\"x\"}){clientMutationId}}"',
     "the GraphQL mutation, which never spells state=closed"),
):
    _rc, _d, _ = gate(_cmd)
    check(f"evasion denied — {_why}: {_cmd!r}", _d == "deny", f"decision={_d!r}")

# AN UNLEXABLE LINE FALLS BACK TO A TEXT SCAN. It is not indistinguishable from an evasive
# one -- it can still be READ -- so it gets the weaker raw-string check rather than a blanket
# refusal. A line that will not lex AND is genuinely closing is still denied.
_rc, _d, _ = gate('gh issue close "5')
check("an unbalanced quote still DENIES when the line is genuinely a close",
      _d == "deny", f"decision={_d!r}")

_rc, _d, _ = gate("echo it's here; gh issue close 5")
check("an unlexable line carrying a real close is caught by the text fallback",
      _d == "deny", f"decision={_d!r}")

# THE REGRESSION THIS FALLBACK EXISTS FOR, pinned so it cannot come back. `shlex` raises on
# ANY unbalanced quote, so an English possessive inside a heredoc made the gate refuse an
# ordinary comment. Blanket-denying the unlexable blocked real work and caught nothing: a
# genuine evasion has no need of an unbalanced quote.
for _cmd, _why in (
    ("echo it's fine", "an English contraction"),
    ("git commit -m \"don't close the loop\"", "a possessive in a commit message"),
    ("cat > /tmp/x.md <<'MD'\nthe module's contract\nMD\n"
     "gh issue comment 8 --repo o/r --body-file /tmp/x.md",
     "a possessive inside a heredoc, ahead of a legitimate gh issue comment"),
):
    _rc, _d, _ = gate(_cmd)
    check(f"an unlexable line that closes NOTHING is allowed — {_why}",
          _rc == 0 and _d is None, f"decision={_d!r}")

# THE KNOWN BLIND SPOT, asserted so it cannot be quietly lost or quietly fixed without notice.
# Catching this needs the shell's own expansion, which a PreToolUse hook does not have. The
# gate's header states it; this pins it. What bounds the harness is structural instead: no
# harness command closes an issue except `abandon`.
# A close that appears only inside a quoted string DENIES, and that is the DESIGN rather than
# an accident of the tokenizer: the gate cannot tell `echo 'gh issue close 5'` from
# `eval 'gh issue close 5'` without running the shell, and the header commits to denying where
# the two cannot be distinguished. The cost is a false deny on a benign echo, which is
# recoverable; the alternative is a false allow on an eval, which is not.
_rc, _d, _ = gate("echo 'gh issue close is refused here'")
check("a close inside a quoted string DENIES, as the header commits to — the gate cannot "
      "distinguish echo from eval without running the shell",
      _d == "deny", f"decision={_d!r}")

_rc, _d, _ = gate("G=gh; $G issue close 5")
check("KNOWN BLIND SPOT — a binary that exists only after shell expansion is NOT caught, and "
      "the gate is a guardrail against habit rather than a security boundary",
      _d is None, f"decision={_d!r}")

# Denials all carry the ONE reason string, whatever route reached them.
_reasons = set()
for _cmd in ('gh "issue" close 5', "eval \"gh issue close 5\"",
             "gh api --method PATCH repos/o/r/issues/5 --input -"):
    _reasons.add(gate(_cmd)[2])
check("every evasion route returns the IDENTICAL reason string, so the operator learns one "
      "answer to one question",
      len(_reasons) == 1, sorted(_reasons))

# ---------------- what tokenizing must NOT start refusing --------------------------------------
for cmd in ("gh pr close 5",
            "gh issue close-milestone 5",
            "gh api repos/o/r/issues/5 --jq .state",
            "gh api -X GET repos/o/r/issues/5",
            "git commit -m 'closes the loop'",
            "gh issue edit 5 --add-label wontfix"):
    _rc, _d, _ = gate(cmd)
    check(f"tokenizing does not widen the refusal to: {cmd!r}", _rc == 0 and _d is None,
          f"rc={_rc} decision={_d!r}")

# ---------------- self-gating ------------------------------------------------------------------
_rc, _d, _ = gate("gh issue close 728", root=_root(sync=False))
check("github.sync false: the gate exits 0 with no output, even for gh issue close — it costs "
      "nothing where the mirror is off",
      _rc == 0 and _d is None, f"rc={_rc} decision={_d!r}")

# MIGRATED (FEAT-2274 V1): this case once asserted only "no deny", which a gate exiting 0 on the
# unreadable config also satisfied. A strict reader refusing duplicate keys is a config READ
# failure, so a matching close is now refused at exit 2 rather than either copy being chosen.
_duplicate_config_root = _config_root(
    lambda c: json.dumps(c)[:-1] + ', "github": {"sync": true, "repo": "o/r"}}')
_rc, _d, _ = gate("gh issue close 728", root=_duplicate_config_root)
check("duplicate harness.json keys refuse a matching close at exit 2 rather than choosing one",
      _rc == 2 and _d is None, f"rc={_rc} decision={_d!r}")

_duplicate_payload_root = _root()
_duplicate_payload_env = dict(os.environ, HARNESS_PROJECT_DIR=_duplicate_payload_root)
_duplicate_payload = (
    '{"tool_input":{"command":"gh issue list"},'
    '"tool_input":{"command":"gh issue close 728"}}')
_duplicate_payload_result = subprocess.run(
    [GATE], input=_duplicate_payload, capture_output=True, text=True,
    env=_duplicate_payload_env)
if _duplicate_payload_result.stdout.strip():
    check("duplicate hook-payload keys are rejected before close policy evaluation",
          False, f"stdout={_duplicate_payload_result.stdout!r}")

# A HARNESS ROOT WITH NO CONFIG — which is what "no harness.json" now means (FEAT-42 T-15).
# A bare tmpdir stood here, and under the MARKER rule a directory with no
# .harness/team-config.yaml is not a root at all: resolve_root discards it and the gate falls
# back to the LIVE checkout, reading the real github block and denying. The case is about a
# MISSING harness.json, so the fixture carries the marker and omits only harness.json.
_noroot = tempfile.mkdtemp()
os.makedirs(os.path.join(_noroot, ".harness"))
with open(os.path.join(_noroot, ".harness", "team-config.yaml"), "w") as _f:
    _f.write("agents: {}\n")
# MIGRATED (FEAT-2274 V1): a missing harness.json at a resolved root is a config read failure,
# not "sync off" — a matching close is refused at exit 2 instead of passing unchecked.
_rc, _d, _ = gate("gh issue close 728", root=_noroot)
check("no harness.json at all: a matching close is refused at exit 2",
      _rc == 2 and _d is None, f"rc={_rc} decision={_d!r}")

# ---------------- THE CORPUS AGREES WITH THE HEALTHY GATE ------------------------------------
# A mislabelled corpus row would teach the failure-mode cases below the wrong answer, so each
# row is first held to what the working gate actually decides on it.
for _cmd, _match in APPLICABILITY_CORPUS:
    _rc, _d, _ = gate(_cmd)
    check(f"corpus row agrees with the healthy gate ({'match' if _match else 'unrelated'}): "
          f"{_cmd!r}", _rc == 0 and _d == ("deny" if _match else None),
          f"rc={_rc} decision={_d!r}")

# ---------------- MATCHING PRECEDES FAIL-CLOSED EXECUTION (FEAT-2274 SC-02) -----------------
# The gate decides applicability from the payload command alone, before root resolution and
# before any library or config load. A command it guards is REFUSED when the gate itself cannot
# run, with a named refusal; an unrelated command passes untouched under the identical fault.
_REFUSAL_HEAD = "gh-close-gate: BLOCKED — the gate could not run ("
_REFUSAL_TAIL = "); the command it guards is refused rather than left unchecked."


def _faulted_bin(module=None, text=""):
    """A disposable copy of the bin, with `text` appended to `module` when one is named."""
    mbin = os.path.join(tempfile.mkdtemp(), "bin")
    shutil.copytree(BIN, mbin)
    if module:
        with open(os.path.join(mbin, module), "a", encoding="utf-8") as f:
            f.write(text)
    return mbin


def _run_in(mbin, command, project_dir):
    return subprocess.run([os.path.join(mbin, "gh-close-gate.py")],
                          input=json.dumps({"tool_input": {"command": command}}),
                          capture_output=True, text=True,
                          env=dict(os.environ, HARNESS_PROJECT_DIR=project_dir))


def _named_refusal(r, detail):
    return (r.returncode == 2 and not r.stdout.strip()
            and _REFUSAL_HEAD + detail in r.stderr and _REFUSAL_TAIL in r.stderr)


# FEAT-65's injected resolver defect, kept: it is no longer a loud exit 1 that the extension
# reads as "not blocking", but a named refusal for a guarded command — and nothing at all for
# an unrelated one, which never reaches the resolver.
_mbin = _faulted_bin("harness_boundary.py",
                     "\n\ndef resolve_root(bin_dir, strict=True):\n"
                     "    raise RuntimeError('FEAT-65 injected')\n")
_r = _run_in(_mbin, "gh issue close 728", _root())
check("FEAT-65: an unexpected resolver defect REFUSES a matching close at exit 2, named",
      _named_refusal(_r, "RuntimeError: FEAT-65 injected"),
      f"rc={_r.returncode} stdout={_r.stdout!r} stderr={_r.stderr[-300:]!r}")
for _cmd, _match in APPLICABILITY_CORPUS:
    _r = _run_in(_mbin, _cmd, _root())
    if _match:
        check(f"resolver defect: a matching command is refused, named: {_cmd!r}",
              _named_refusal(_r, "RuntimeError: FEAT-65 injected"),
              f"rc={_r.returncode} stderr={_r.stderr[-300:]!r}")
    else:
        check(f"resolver defect: an unrelated command passes untouched: {_cmd!r}",
              _r.returncode == 0 and not _r.stdout.strip() and not _r.stderr.strip(),
              f"rc={_r.returncode} stdout={_r.stdout!r} stderr={_r.stderr[-300:]!r}")

# NO ROOT AT ALL. The override names a directory without the marker and the copied bin derives
# none either: today's "refusing to run" exit 2 stays for a close, and an unrelated command,
# which the gate never had any business with, passes.
_mbin = _faulted_bin()
_noroot_dir = tempfile.mkdtemp()
_r = _run_in(_mbin, "gh issue close 728", _noroot_dir)
check("no harness root: a matching close is refused at exit 2, named",
      _named_refusal(_r, "no harness root could be resolved from "),
      f"rc={_r.returncode} stderr={_r.stderr[-300:]!r}")
_r = _run_in(_mbin, "git status", _noroot_dir)
check("no harness root: an unrelated command exits 0 untouched",
      _r.returncode == 0 and not _r.stdout.strip() and not _r.stderr.strip(),
      f"rc={_r.returncode} stdout={_r.stdout!r} stderr={_r.stderr[-300:]!r}")

# THE GATE'S OWN BODY FAILS after the root resolves: its config read raises.
_mbin = _faulted_bin("artifact_accessors.py",
                     "\n\ndef load_harness_json(*args, **kwargs):\n"
                     "    raise RuntimeError('FEAT-2274 body injected')\n")
_r = _run_in(_mbin, "gh api -X PATCH repos/o/r/issues/9 -f state=closed", _root())
check("body failure: a matching close is refused at exit 2, named",
      _named_refusal(_r, "RuntimeError: FEAT-2274 body injected"),
      f"rc={_r.returncode} stderr={_r.stderr[-300:]!r}")
_r = _run_in(_mbin, "gh pr close 5", _root())
check("body failure: an unrelated command exits 0 untouched",
      _r.returncode == 0 and not _r.stdout.strip() and not _r.stderr.strip(),
      f"rc={_r.returncode} stdout={_r.stdout!r} stderr={_r.stderr[-300:]!r}")

# ---------------- A CONFIG THAT CANNOT BE READ IS NOT "SYNC OFF" (FEAT-2274 V1) ---------------
# Once a command matches, a missing or invalid harness.json refuses it with the loader's
# diagnosis: only a VALID config with sync off exempts. An unrelated command never reaches the
# config read (FEAT-2297: the gate recognises the close before loading anything).
_CONFIG_READ = "harness.json could not be read: "
_CONFIG_FAULTS = (
    ("no harness.json", None),
    ("not JSON", lambda c: json.dumps(c)[:-1]),
    ("a document that is not a mapping", lambda c: json.dumps([c])),
    ("a github block that is a list", lambda c: json.dumps({**c, "github": [1, 2]})),
    ("a github block that is null", lambda c: json.dumps({**c, "github": None})),
)


def _untouched(r):
    return r.returncode == 0 and not r.stdout.strip() and not r.stderr.strip()


def _config_fault_case(label, derive):
    root = _config_root(derive)
    r = _run_in(os.path.dirname(GATE), "gh issue close 728", root)
    check(f"config fault ({label}): a matching close is refused at exit 2, named",
          _named_refusal(r, _CONFIG_READ), f"rc={r.returncode} stderr={r.stderr[-300:]!r}")
    r = _run_in(os.path.dirname(GATE), "gh pr close 5", root)
    check(f"config fault ({label}): an unrelated command exits 0 untouched", _untouched(r),
          f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr[-300:]!r}")


for _label, _derive in _CONFIG_FAULTS:
    _config_fault_case(_label, _derive)

# The control: a VALID config with sync off is still the legitimate exemption — explicitly, or
# by the schema default when the github block is absent.
for _label, _root_dir in (
        ("github.sync false", _root(sync=False)),
        ("no github block", _config_root(lambda c: json.dumps({k: v for k, v in c.items() if k != "github"})))):
    _r = _run_in(os.path.dirname(GATE), "gh issue close 728", _root_dir)
    check(f"valid config, {_label}: a matching close exits 0 untouched", _untouched(_r),
          f"rc={_r.returncode} stdout={_r.stdout!r} stderr={_r.stderr[-300:]!r}")

print(f"\n{'ALL PASSED' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
