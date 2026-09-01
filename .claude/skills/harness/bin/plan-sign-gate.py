#!/usr/bin/env python3
"""Refuse an agent's `plan-merge.py sign-approval`, so only the main session can sign.

FEAT-41 T-08, REQ-05, making DEC-120 mechanical. An agent may ASK for a signature and be
refused; only the main session can write one. Until this gate that rule was prose:
`sign-approval` takes the lock and writes the approval block for whoever calls it.

MODELLED ON gh-close-gate.py, which DEC-203 section 8 records the reasoning for, and which
is the working precedent for this exact shape — tokenize, compare basenames, re-scan the
argument of `eval` and `bash -c`, and fall back to a raw-text scan for a line that will not
lex. Its own comment lists ten forms measured reaching a grep-based gate straight through.

WHAT SURVIVES THIS GATE, stated rather than implied: a binary produced only by shell
expansion — `P=plan-merge.py; python3 $P sign-approval` — is invisible here. Catching it
needs the shell's own expansion, which a PreToolUse hook is never given: it receives
`tool_input.command` as text. So this is a guardrail against a signature written out of
habit or over-eagerness, NOT a security boundary. What actually bounds the harness is that
`sign-approval` is the only verb that writes the block, and this gate makes reaching it from
an agent an explicit act of evasion rather than an ordinary tool call.

IT DENIES ONE VERB, NOT THE TOOL. `apply`, `add-tasks`, `set-task-station` and
`set-feature-station` are the orchestrator's legal routes and stay open — T-05's playbook
names them and T-09's shape gate leaves them as plan.yaml's only writer. A gate that refused
the whole tool would take the orchestrator's ability to record a task status with it.
"""
import json
import os
import re
import shlex
import sys

VERB = "sign-approval"
TOOL = "plan-merge.py"

ROOT = sys.argv[1] if len(sys.argv) > 1 else ""

# THE REFUSAL NAMES A COMMAND THE READER CAN RUN. The wrapper hands over the resolved harness
# root (matching gh-close-gate.sh), so when the tool is confirmed on disk underneath it the
# message carries the ABSOLUTE path and is copy-pasteable from any cwd; otherwise it falls back
# to the repo-relative form. It never asserts a path it could not confirm.
_rel = os.path.join(".claude", "skills", "harness", "bin", TOOL)
_abs = os.path.join(ROOT, _rel) if ROOT else ""
TOOL_PATH = _abs if _abs and os.path.isfile(_abs) else _rel

# ONE refusal text, used verbatim for EVERY denial. A second wording would drift and the
# operator would learn two different answers to one question.
#
# IT NAMES THE VERB LITERALLY rather than saying "the verb": a refusal logged without the
# command that triggered it must still say what was refused.
REASON = (
    f"Refused: {VERB} writes the approval signature, which is the USER'S and is relayed by\n"
    f"the main session alone (DEC-120). An agent may ask for a signature and be refused; it\n"
    f"cannot write one.\n"
    f"\n"
    f"Return awaiting_user with what you need signed. Do not call {VERB}, and do not edit the\n"
    f"approval block by hand — the main session runs {VERB} itself once the user has given\n"
    f"their word:\n"
    f"  python3 {TOOL_PATH} {VERB} --file <plan.yaml> ...\n"
    f"\n"
    f"Every other verb of this tool stays open to you: apply, add-tasks, set-task-station and\n"
    f"set-feature-station. This gate refuses one verb, not the tool."
)

try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)

# AN ABSENT OR EMPTY agent_type IS THE MAIN SESSION, and that exemption is the mechanism
# rather than a named branch — check-domain.sh's approval_guard records the same reasoning
# for the same reason, and issue #132 records what happened the last time that file grew a
# second carve-out to keep in sync.
if not (payload.get("agent_type") or ""):
    sys.exit(0)

cmd = (payload.get("tool_input") or {}).get("command") or ""

# Shell operators shlex hands back as their own tokens. They are separators, never words.
OPS = {";", "&", "&&", "|", "||", "(", ")", "<", ">", ">>", "\n"}
MAX_DEPTH = 3

# argparse's end-of-options marker. It is NOT a shell operator, so shlex hands it back as an
# ordinary token and it broke the tool/verb adjacency test (FEAT-41 F-03).
SEP = "--"

# The TEXT fallback, for a command line `shlex` cannot lex at all. It reads the raw string,
# so an unbalanced quote does not stop it. Weaker than tokenizing — it cannot see through
# quoting or a path — and only ever reached when tokenizing is impossible.
#
# IT SKIPS SEPARATORS TOO (FEAT-41 F-03). Fixing only the token scan above would have moved
# the evasion rather than closed it: an unlexable line carrying `plan-merge.py -- sign-approval`
# reaches exactly this regex, and the hole would have survived one unbalanced quote away.
RAW_SIGN = re.compile(r"plan-merge\.py[\"'\s]+(?:" + re.escape(SEP) + r"[\"'\s]+)*"
                      + re.escape(VERB) + r"(\s|$)")


def words(s):
    """Token list with quoting resolved, or None when the line will not lex."""
    try:
        lex = shlex.shlex(s, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        return [t for t in lex if t not in OPS]
    except ValueError:
        return None


def is_tool(tok):
    """`plan-merge.py`, `/abs/plan-merge.py`, `\\plan-merge.py`, `"plan-merge.py"` — one file."""
    return os.path.basename(tok.strip("\\'\"$()`")) == TOOL


def denies(line, depth=0):
    toks = words(line)
    if toks is None:
        # UNPARSEABLE FALLS BACK TO A TEXT SCAN, IT DOES NOT BLANKET-DENY. gh-close-gate.py
        # records what the blanket version cost when it was measured: shlex raises on ANY
        # unbalanced quote, and an English possessive is an unbalanced quote, so `echo it's
        # fine` was refused. It blocked ordinary work and caught nothing, because a real
        # evasion has no need of an unbalanced quote to hide behind.
        return bool(RAW_SIGN.search(line))
    for i, t in enumerate(toks):
        # THE VERB MUST FOLLOW THE TOOL, PAST ANY END-OF-OPTIONS SEPARATOR (FEAT-41 F-03).
        # A bare `sign-approval` anywhere in a command line is not a signing attempt — an agent
        # grepping for the verb, or writing a receipt that mentions it, is doing legitimate
        # work, and a substring match would refuse both. So position still matters; what was
        # wrong was testing STRICT adjacency.
        #
        # argparse treats a lone `--` as end-of-options and DROPS it, so `plan-merge.py --
        # sign-approval` is a line argparse executes while no token sits adjacent to the tool.
        # Measured against the real tool: one `--` signs, two `--` and an empty token are both
        # refused by argparse at exit 2 and cannot sign at all.
        #
        # A RUN IS SKIPPED, NOT ONE, and deliberately: the repeated form cannot sign today, so
        # skipping it costs nothing, and it means this gate does not silently reopen if
        # argparse's handling of a second separator ever changes. Only `--` is skipped —
        # widening to "the verb appears anywhere after the tool" would refuse the legitimate
        # `apply` call asserted as a negative control in test-plan-sign-gate.py.
        if not is_tool(t):
            continue
        j = i + 1
        while toks[j:j + 1] == [SEP]:
            j += 1
        if toks[j:j + 1] == [VERB]:
            return True
    if depth < MAX_DEPTH:
        # `eval "... sign-approval ..."` and `bash -c '...'` carry a whole command line
        # inside ONE token. Re-scan any token that still looks like a command line.
        for t in toks:
            if len(t.split()) >= 3 and denies(t, depth + 1):
                return True
    return False


if denies(cmd):
    sys.stderr.write(REASON + "\n")
    sys.exit(2)
sys.exit(0)
