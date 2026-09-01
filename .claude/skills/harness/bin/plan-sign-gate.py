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


# Bash's line continuation. Bash REMOVES `\<newline>` before the shell ever sees words, so the
# tokens either side of it are adjacent at execution time. Neither scanner below removes it on
# its own: shlex(posix=True) yields the literal token `'\nsign-approval'`, and the raw-text
# class `["'\s]` has no backslash in it (FEAT-41 H-02).
CONTINUATION = re.compile(r"\\\r?\n")

# A BRACED PARAMETER EXPANSION, which bash may expand to WHITESPACE (FEAT-41 C2-03).
#
# `plan-merge.py${IFS}sign-approval` reaches this gate as eleven literal characters inside ONE
# shlex token, so neither the tool nor the verb appears as a token, the adjacency loop never
# fires, and RAW_SIGN's `["'\s]` class matches nothing either. Bash expands and word-splits, and
# argparse receives the verb. `${IFS}` needs no prearranged variable -- it is always set.
#
# BRACED ONLY, AND MEASURED. Bare `$IFS` immediately followed by letters is NOT an evasion: bash
# consumes the longest valid name, so `$IFSsign-approval` expands `$IFSsign` to nothing and the
# line becomes `plan-merge.py-approval`, which cannot sign. Denying that would be a guess, and
# there is a precision control asserting it stays allowed. A bare `$IFS` FOLLOWED BY A SPACE
# needs nothing here -- the space is already a separator.
BRACED_EXPANSION = re.compile(r'"?\$\{[^{}]*\}"?')


def _strip_substitutions(line):
    """Replace every `$(...)` and backtick substitution with a space.

    SCANNED, NOT REGEXED, and the nested case is why (FEAT-41 MF-1). `\\$\\([^)]*\\)` stops at the
    FIRST `)`, so `$(echo "$(printf " ")")` would leave the outer `)` behind and the token would
    still not split where bash splits it -- a one-line fix that looks right and leaks. There is a
    case for exactly that shape.
    """
    out, i, n = [], 0, len(line)
    while i < n:
        if line[i] == "$" and i + 1 < n and line[i + 1] == "(":
            depth, j = 0, i + 1
            while j < n:
                if line[j] == "(":
                    depth += 1
                elif line[j] == ")":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            # An UNCLOSED substitution consumes the rest of the line. That is deliberate: bash
            # cannot run it either, and leaving the text behind would let a truncated `$(` hide
            # the verb from the scan while a later heredoc or continuation completed it.
            out.append(" ")
            i = j + 1
            continue
        if line[i] == "`":
            j = line.find("`", i + 1)
            out.append(" ")
            i = (j + 1) if j != -1 else n
            continue
        out.append(line[i])
        i += 1
    return "".join(out)


def as_bash_reads_it(line):
    """Rejoin continued lines and neutralise expansions and substitutions, so both scanners see
    the words bash will actually execute.

    ONE MECHANISM, APPLIED BEFORE EITHER PATH -- for the FOURTH time in this file's history. F-03
    needed its separator fix in the token scan AND the text fallback; H-02 needed it for the
    continuation; C2-03 for `${IFS}`; this is `$(...)` and backticks, the next member of C2-03's
    own class. The repetition is the point: teaching two scanners separately leaves the same
    asymmetry one escape away every time.

    THE HONEST RULE IS NOT "EVALUATE THE SHELL", which no PreToolUse hook can do. It is that an
    expansion or substitution COULD be whitespace, so a gate deciding ADJACENCY must assume it is.
    That is bounded: ordinary WORDS between the tool and the verb are not expansions and still
    break the adjacency, which is what this file's `apply`-mentions-the-verb controls assert.

    AND IT IS STILL A DENYLIST. Cycle 3's panel said so plainly and it is recorded here rather
    than argued with: closing two members of a class does not close the class, and no reviewer can
    enumerate the shell. The structural answer is an identity check inside `cmd_sign_approval`,
    which cannot be written today -- no runtime identity signal reaches a subprocess, since
    `HARNESS_AGENT_ID` is a marker inside agent definition FILES rather than an environment
    variable. That design question is routed up, not silently left implied by a passing suite.
    """
    return BRACED_EXPANSION.sub(" ", _strip_substitutions(CONTINUATION.sub("", line)))


# Wrappers that build a command's argv from somewhere the gate cannot read: standard input, a
# file, or a filename walk. `bash`/`sh` are deliberately ABSENT -- `denies` recurses into a nested
# command line, so its verb IS determinable (FEAT-41 HIGH-2).
INDIRECT = {"xargs", "parallel"}
INTERPRETERS = {"python", "python3", "python2", "env", "nice", "time", "nohup", "stdbuf"}


def _invokes_tool_indirectly(toks):
    """True when a wrapper will run the tool with argv the gate cannot see.

    FAIL CLOSED ON INDIRECTION, WHICH IS NOT ANOTHER SEPARATOR PATCH. Measured: three xargs
    variants all deliver the verb, and the third reads it FROM A FILE --
    `xargs plan-merge.py < verb.txt` -- so the verb's text never appears in the command line and
    no text scanner can ever see it. Closing "the xargs form" would have been a fifth patch
    leaving the class open. A gate that cannot determine the verb must refuse rather than guess,
    exactly as an unresolvable path refuses in check-domain.sh.

    THE COMMAND WORD IS RESOLVED, NOT MERELY SEARCHED FOR, and that is what keeps this narrow:
    `xargs -I{} grep plan-merge.py dir` mentions the tool as grep's PATTERN and must stay allowed.
    So we skip the wrapper's own flags, then read the next token as the COMMAND, allowing one
    interpreter prefix (`python3 tool`). Only if THAT resolves to the tool is it an invocation.
    """
    for i, t in enumerate(toks):
        base = os.path.basename(t.strip("\\'\"$()`"))
        if base == "find":
            # find's command begins after `-exec`/`-execdir`, not after its own flags.
            for j in range(i + 1, len(toks)):
                if toks[j] in ("-exec", "-execdir"):
                    if any(is_tool(x) for x in toks[j + 1:j + 3]):
                        return True
            continue
        if base not in INDIRECT:
            continue
        j = i + 1
        while j < len(toks) and toks[j].startswith("-"):
            j += 1
        # One interpreter prefix is allowed, so `xargs python3 <tool>` is seen as invoking it.
        for cand in (j, j + 1):
            if cand < len(toks) and is_tool(toks[cand]):
                return True
            if not (cand < len(toks)
                    and os.path.basename(toks[cand].strip("\\'\"$()`")) in INTERPRETERS):
                break
    return False


def denies(line, depth=0):
    line = as_bash_reads_it(line)
    toks = words(line)
    if toks is None:
        # UNPARSEABLE FALLS BACK TO A TEXT SCAN, IT DOES NOT BLANKET-DENY. gh-close-gate.py
        # records what the blanket version cost when it was measured: shlex raises on ANY
        # unbalanced quote, and an English possessive is an unbalanced quote, so `echo it's
        # fine` was refused. It blocked ordinary work and caught nothing, because a real
        # evasion has no need of an unbalanced quote to hide behind.
        return bool(RAW_SIGN.search(line))
    if _invokes_tool_indirectly(toks):
        # THE VERB IS UNDETERMINABLE HERE, so this refuses without looking for it (FEAT-41
        # HIGH-2). Every other branch in this function asks "is the verb in the right position";
        # this one asks "can the position be read at all", and when it cannot the answer is no.
        return True
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
