#!/usr/bin/env python3
"""plan-sign-gate.sh — the PreToolUse Bash hook that refuses an agent's `sign-approval`.

FEAT-41 T-08, closing REQ-05. DEC-120 says the approval signature is the user's and is
relayed by the main session alone. Until this gate that was prose: `plan-merge.py
sign-approval` would take the lock and write the block for whoever called it, so an agent
that decided the plan looked finished could sign it and nothing would notice.

EVERY DENY CASE ASSERTS THE REFUSAL TEXT, NOT ONLY THE EXIT CODE. An exit-2-only assertion
passes against a gate that denies EVERYTHING, which is the failure mode a write gate on a
shared tool actually has — see `case: set-task-station` and `case: an ordinary command`,
which exist to catch exactly that. The text assertion is on the literal string
`sign-approval`, because a refusal logged without the command that triggered it must still
say which verb was refused.
"""
import json
import os
import subprocess
import tempfile

BIN = os.path.dirname(os.path.abspath(__file__))
GATE = os.environ.get("PLAN_SIGN_GATE_BIN") or os.path.join(BIN, "plan-sign-gate.sh")

fails = 0


def check(name, cond, detail=""):
    global fails
    if cond:
        print(f"ok    {name}")
    else:
        fails += 1
        print(f"FAIL  {name}\n      {detail}")


def _root():
    """A throwaway harness root.

    THE team-config.yaml MARKER IS NOT OPTIONAL (FEAT-42 T-15). plan-sign-gate.sh resolves
    through harness_boundary.resolve_root, which honours HARNESS_PROJECT_DIR only when
    .harness/team-config.yaml is readable underneath it. A fixture holding only harness.json
    silently falls back to the derived root — the LIVE checkout — and the case would then be
    measuring this repository rather than its own fixture.
    """
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, ".harness"))
    with open(os.path.join(d, ".harness", "harness.json"), "w") as f:
        json.dump({"schema_version": 1}, f)
    with open(os.path.join(d, ".harness", "team-config.yaml"), "w") as f:
        f.write("agents: {}\n")
    return d


ROOT = _root()


def gate(command, agent_type=None):
    """(returncode, stderr). A deny is exit 2 with the refusal on stderr; an allow is 0."""
    payload = {"tool_input": {"command": command}}
    if agent_type is not None:
        payload["agent_type"] = agent_type
    env = dict(os.environ)
    env["HARNESS_PROJECT_DIR"] = ROOT
    r = subprocess.run(["bash", GATE], input=json.dumps(payload),
                       capture_output=True, text=True, env=env)
    return r.returncode, (r.stderr or "")


SIGN = "python3 .claude/skills/harness/bin/plan-merge.py sign-approval --file p.yaml"

# ---------------------------------------------------------------------------------------
# THE MAIN SESSION IS EXEMPT BY THE MECHANISM, NOT BY A NAMED CARVE-OUT.
# An absent `agent_type` IS the main session — check-domain.sh's approval_guard records the
# same reasoning for the same reason, and a named branch would be a second carve-out to keep
# in sync. This case is what makes the gate usable at all: the main session is the ONE
# author that must be able to sign.
# ---------------------------------------------------------------------------------------
rc, err = gate(SIGN)
check("a payload with NO agent_type may sign — an absent agent_type is the main session",
      rc == 0, f"rc={rc} stderr={err[:400]!r}")

rc, err = gate(SIGN, agent_type="")
check("an EMPTY agent_type may sign too — empty and absent are the same author",
      rc == 0, f"rc={rc} stderr={err[:400]!r}")

# ---------------------------------------------------------------------------------------
# THE DENIAL, AND ITS TEXT.
# ---------------------------------------------------------------------------------------
rc, err = gate(SIGN, agent_type="harness-orchestrator")
check("an agent invoking sign-approval is DENIED at exit 2",
      rc == 2, f"rc={rc} stderr={err[:400]!r}")
check("the refusal names sign-approval LITERALLY, so a log line read without the command "
      "still says what was refused",
      "sign-approval" in err, f"stderr={err[:400]!r}")
check("the refusal states the RULE — the signature is the user's, relayed by the main session",
      "main session" in err, f"stderr={err[:400]!r}")
check("the refusal names awaiting_user, which is what the agent should return instead",
      "awaiting_user" in err, f"stderr={err[:400]!r}")

# ---------------------------------------------------------------------------------------
# THE FOUR EVASIONS THE PRECEDENT ALREADY MEASURED (gh-close-gate.sh's own comment lists
# ten reaching a grep-based gate straight through). basename strips the path, shlex strips
# the quoting and the backslash, and each token is re-scanned so eval and bash -c are READ.
# ---------------------------------------------------------------------------------------
rc, err = gate("/opt/homebrew/bin/python3 /abs/path/to/plan-merge.py sign-approval --file p",
               agent_type="harness-pm")
check("an ABSOLUTE path to plan-merge.py is denied — basename, not the literal string",
      rc == 2 and "sign-approval" in err, f"rc={rc} stderr={err[:300]!r}")

rc, err = gate('eval "python3 plan-merge.py sign-approval --file p.yaml"',
               agent_type="harness-pm")
check("eval carrying the command in ONE token is denied — the token is re-scanned",
      rc == 2 and "sign-approval" in err, f"rc={rc} stderr={err[:300]!r}")

rc, err = gate("bash -c 'python3 plan-merge.py sign-approval --file p.yaml'",
               agent_type="harness-pm")
check("bash -c carrying the command in ONE token is denied",
      rc == 2 and "sign-approval" in err, f"rc={rc} stderr={err[:300]!r}")

rc, err = gate('python3 "plan-merge.py" sign-approval --file p.yaml', agent_type="harness-pm")
check("a QUOTED script name is denied — shlex resolves the quoting before basename",
      rc == 2 and "sign-approval" in err, f"rc={rc} stderr={err[:300]!r}")

# ---------------------------------------------------------------------------------------
# THE UNLEXABLE LINE FALLS BACK TO A TEXT SCAN, IT DOES NOT BLANKET-DENY, and it does not
# blanket-ALLOW either. gh-close-gate.py's own comment records what a blanket deny cost:
# shlex raises on ANY unbalanced quote, so an English possessive refused ordinary work all
# day. The fallback is weaker — it cannot see through a path or quoting — and is reached
# only when tokenizing is impossible.
# ---------------------------------------------------------------------------------------
rc, err = gate("python3 plan-merge.py sign-approval --name \"O'Brien", agent_type="harness-pm")
check("an UNLEXABLE command line still denies, through the raw-text fallback",
      rc == 2 and "sign-approval" in err, f"rc={rc} stderr={err[:300]!r}")

rc, err = gate("echo it's fine", agent_type="harness-pm")
check("NEGATIVE CONTROL: an unlexable line that is NOT a signing attempt is allowed — the "
      "fallback is a text scan, never a blanket deny",
      rc == 0, f"rc={rc} stderr={err[:300]!r}")

# ---------------------------------------------------------------------------------------
# THE NEGATIVE CONTROLS THAT MAKE EVERY DENY ABOVE MEAN SOMETHING. Without these the whole
# file passes against `sys.exit(2)`.
# ---------------------------------------------------------------------------------------
rc, err = gate("python3 .claude/skills/harness/bin/plan-merge.py set-task-station --file p "
               "--task T-01 --station done", agent_type="harness-orchestrator")
check("NEGATIVE CONTROL: set-task-station is ALLOWED for an agent — this gate refuses ONE "
      "verb, not the tool",
      rc == 0, f"rc={rc} stderr={err[:300]!r}")

rc, err = gate("python3 .claude/skills/harness/bin/plan-merge.py apply --file p --proposal x",
               agent_type="harness-orchestrator")
check("NEGATIVE CONTROL: apply is ALLOWED for an agent",
      rc == 0, f"rc={rc} stderr={err[:300]!r}")

rc, err = gate("git status --porcelain", agent_type="harness-orchestrator")
check("NEGATIVE CONTROL: an ordinary command is ALLOWED for an agent",
      rc == 0, f"rc={rc} stderr={err[:300]!r}")

# THE VERB MUST FOLLOW THE TOOL, and this is the case that kills a bare substring match.
# `sign-approval` appearing anywhere in a command line is not a signing attempt: an agent
# writing a receipt that mentions the verb, or grepping for it, is doing legitimate work.
rc, err = gate("grep -rn sign-approval .claude/skills/harness/bin/",
               agent_type="harness-orchestrator")
check("NEGATIVE CONTROL: the bare word sign-approval WITHOUT plan-merge.py before it is "
      "allowed — a grep or a receipt is not a signing attempt",
      rc == 0, f"rc={rc} stderr={err[:300]!r}")

# ---------------------------------------------------------------------------------------
# FEAT-41 F-03, high, found by the validation panel. THE ADJACENCY TEST WAS TOO STRICT.
#
# `denies()` required the verb to be the token IMMEDIATELY after the tool. argparse treats a
# lone `--` as end-of-options and DROPS it, so `plan-merge.py -- sign-approval` broke the
# adjacency the gate tested while remaining a command argparse actually executes. A habitual
# `--`, not an attack, forged the user's signature.
#
# MEASURED, NOT ASSUMED, and the class is bounded. Driving the real plan-merge.py against a
# throwaway plan:
#     sign-approval          rc=0  SIGNS
#     -- sign-approval       rc=0  SIGNS      <- the hole
#     -- -- sign-approval    rc=2  argparse refuses, cannot sign
#     '' sign-approval       rc=2  argparse refuses, cannot sign
# So exactly one separator evades. The gate now skips a RUN of `--` rather than one: the
# repeated form cannot sign today, and skipping it costs nothing, but it means the gate does
# not silently reopen if argparse's handling of a second `--` ever changes.
# ---------------------------------------------------------------------------------------
for _sep in ("--", "-- --"):
    rc, err = gate(f"python3 .claude/skills/harness/bin/plan-merge.py {_sep} sign-approval "
                   f"--file p.yaml --by Someone --date 2026-01-01",
                   agent_type="harness-orchestrator")
    check(f"F-03: `plan-merge.py {_sep} sign-approval` is DENIED — argparse drops the "
          f"separator, so adjacency is not what makes a line a signing attempt",
          rc == 2, f"rc={rc} stderr={err[:300]!r}")

# NEGATIVE CONTROL FOR THE WIDENING. Skipping separators must not turn the scan into "the verb
# appears somewhere after the tool" — that would refuse a legitimate `apply` whose own argument
# or a trailing comment happens to name the verb.
rc, err = gate("python3 .claude/skills/harness/bin/plan-merge.py apply --file p.yaml "
               "--proposal q.yaml  # not a sign-approval call",
               agent_type="harness-orchestrator")
check("F-03 NEGATIVE CONTROL: an `apply` call that merely MENTIONS sign-approval later on the "
      "line is still allowed — separators are skipped, arbitrary tokens are not",
      rc == 0, f"rc={rc} stderr={err[:300]!r}")

# AND THE SAME HOLE IN THE TEXT FALLBACK. The three cases above all lex, so none of them
# reaches `RAW_SIGN` — fixing only the token scan would have moved the evasion one unbalanced
# quote away instead of closing it. `it's` is the cheapest real unlexable line there is, and it
# is the exact shape gh-close-gate.py's blanket-deny measurement was about.
rc, err = gate("echo it's fine; python3 .claude/skills/harness/bin/plan-merge.py -- "
               "sign-approval --file p.yaml --by Someone --date 2026-01-01",
               agent_type="harness-orchestrator")
check("F-03: the TEXT fallback also skips the separator — an unlexable line carrying "
      "`plan-merge.py -- sign-approval` is DENIED",
      rc == 2, f"rc={rc} stderr={err[:300]!r}")

# NEGATIVE CONTROL for the fallback: an unlexable line that is NOT a signing attempt still
# passes, so the fallback did not quietly become the blanket deny it was written to avoid.
rc, err = gate("echo it's fine && git status", agent_type="harness-orchestrator")
check("F-03 NEGATIVE CONTROL: an unlexable line that is not a signing attempt is still "
      "allowed — the fallback is a scan, never a blanket deny",
      rc == 0, f"rc={rc} stderr={err[:300]!r}")

# ---------------------------------------------------------------------------------------
# FEAT-41 H-02, high, found by cycle 1's panel. A SHELL LINE CONTINUATION EVADED BOTH PATHS.
#
# `\<newline>` is bash's line continuation: bash REMOVES it, so the verb lands adjacent to the
# tool and the command signs. shlex does not remove it — with posix=True it yields the literal
# token `'\nsign-approval'`, which is not equal to `sign-approval`, so the adjacency test saw
# no verb at all. MEASURED both halves before fixing:
#     tokens  -> ['python3', '...plan-merge.py', '\nsign-approval', '--file', 'p.yaml']
#     bash    -> ARG1=sign-approval        <- executes as adjacent
# The text fallback missed it for a different reason: backslash is absent from its `["'\s]`
# separator class, so the scan stopped at the `\`.
#
# THE FIX IS TO ADOPT BASH'S OWN VIEW ONCE, before either path runs, rather than to teach two
# scanners about backslashes separately. That is why F-03's lesson repeats here: its fix had to
# land in both the token scan and the fallback, and a second per-path patch would have left the
# same asymmetry one escape away.
# ---------------------------------------------------------------------------------------
rc, err = gate("python3 .claude/skills/harness/bin/plan-merge.py \\\nsign-approval "
               "--file p.yaml --by Someone --date 2026-01-01",
               agent_type="harness-orchestrator")
check("H-02: `plan-merge.py \\<newline>sign-approval` is DENIED — bash removes the "
      "continuation and signs, so the gate must read the line the way bash does",
      rc == 2, f"rc={rc} stderr={err[:300]!r}")

# AND IN THE TEXT FALLBACK, for the same reason F-03 needed both: an unlexable line carrying
# the continuation must not survive one unbalanced quote away from the token scan.
rc, err = gate("echo it's fine; python3 .claude/skills/harness/bin/plan-merge.py \\\n"
               "sign-approval --file p.yaml --by Someone --date 2026-01-01",
               agent_type="harness-orchestrator")
check("H-02: the TEXT fallback also removes the continuation — an unlexable line carrying "
      "`plan-merge.py \\<newline>sign-approval` is DENIED",
      rc == 2, f"rc={rc} stderr={err[:300]!r}")

# NEGATIVE CONTROL. Removing continuations must not make a genuine multi-line command that
# merely MENTIONS the verb into a signing attempt — the join happens at the backslash only,
# never at an ordinary newline, so a separate command on its own line stays separate.
rc, err = gate("python3 .claude/skills/harness/bin/plan-merge.py apply --file p.yaml \\\n"
               "--proposal q.yaml  # not a sign-approval call",
               agent_type="harness-orchestrator")
check("H-02 NEGATIVE CONTROL: a continuation inside an ordinary `apply` call is still "
      "allowed — the line is rejoined, not blanket-denied",
      rc == 0, f"rc={rc} stderr={err[:300]!r}")

# ---------------------------------------------------------------------------------------
# FEAT-41 C2-03, high, found by cycle 2's panel and reproduced END TO END: a forged approval
# block landed at exit 0 with no stderr from either gate.
#
# A PARAMETER EXPANSION IS NOT WHITESPACE UNTIL BASH MAKES IT WHITESPACE. H-02 taught the gate
# to rejoin continued lines, which is a purely textual transform. `${IFS}` is not: the gate sees
# eleven literal characters INSIDE one token, so neither the tool nor the verb appears as a token
# at all, the adjacency loop never fires, and RAW_SIGN's `["'\s]+` separator class matches
# nothing either. Bash expands it, word-splits, and argparse receives `sign-approval`. MEASURED:
#     tokens -> ['python3', '...plan-merge.py${IFS}sign-approval', '--file', 'p.yaml']
#     bash   -> ARG1=sign-approval
#
# THE GATE CANNOT EXPAND VARIABLES, so the honest rule is not "evaluate the shell" -- it is that
# an expansion COULD be whitespace, therefore a gate deciding adjacency must assume it is. That
# is a bounded widening, not "the verb appears somewhere after the tool": the negative controls
# below and above still pass, because ordinary WORDS between the tool and the verb are not
# expansions and still break the adjacency.
#
# WHAT THIS DOES NOT CLOSE, stated rather than implied: `$P` where P holds the whole command is
# out of reach of any PreToolUse hook, and plan-sign-gate.py's own module docstring already says
# so. This closes the form that needs no prearranged variable -- `${IFS}` is always set.
# ---------------------------------------------------------------------------------------
# WHICH FORMS ACTUALLY SPLIT WAS MEASURED, NOT GUESSED, and the first draft of this test was
# wrong: it asserted that bare `$IFSsign-approval` must be denied. Bash reads the LONGEST valid
# name, so that is `$IFSsign` -- unset, empty -- and the line becomes `plan-merge.py-approval`,
# which cannot sign anything. Denying it would have been a false positive baked into a test.
for _exp in ("${IFS}", '"${IFS}"', "${IFS}${IFS}"):
    rc, err = gate(f"python3 .claude/skills/harness/bin/plan-merge.py{_exp}sign-approval "
                   f"--file p.yaml --by Someone --date 2026-01-01",
                   agent_type="harness-orchestrator")
    check(f"C2-03: `plan-merge.py{_exp}sign-approval` is DENIED — bash word-splits the "
          f"expansion, so the gate must treat it as the whitespace it may become",
          rc == 2, f"rc={rc} stderr={err[:300]!r}")

# PRECISION CONTROL, from the mistake above. `$IFSsign-approval` is NOT a signing attempt --
# bash consumes `IFSsign` as the name -- so the gate must not deny it. This is the assertion that
# stops the expansion rule from being widened into "any `$` near the verb".
rc, err = gate("python3 .claude/skills/harness/bin/plan-merge.py$IFSsign-approval "
               "--file p.yaml", agent_type="harness-orchestrator")
check("C2-03 PRECISION CONTROL: `$IFSsign-approval` is ALLOWED — bash reads the longest name, "
      "so this line cannot sign, and a gate that denied it would be guessing",
      rc == 0, f"rc={rc} stderr={err[:300]!r}")

# AND IN THE TEXT FALLBACK, for the third time in this file: F-03 and H-02 both had to land in
# both scanners, and an evasion that survives in only one of them has merely moved.
rc, err = gate("echo it's fine; python3 .claude/skills/harness/bin/plan-merge.py${IFS}"
               "sign-approval --file p.yaml --by Someone --date 2026-01-01",
               agent_type="harness-orchestrator")
check("C2-03: the TEXT fallback also neutralises the expansion — an unlexable line carrying "
      "`plan-merge.py${IFS}sign-approval` is DENIED",
      rc == 2, f"rc={rc} stderr={err[:300]!r}")

# NEGATIVE CONTROL FOR THE WIDENING, and it is the one that matters: neutralising expansions must
# not make every mention of the verb a signing attempt. An expansion used as an ordinary ARGUMENT
# on a legitimate `apply` line, with real words between tool and verb, stays allowed.
rc, err = gate("python3 $HARNESS_BIN/plan-merge.py apply --file $PLAN --proposal q.yaml "
               "  # not a sign-approval call",
               agent_type="harness-orchestrator")
check("C2-03 NEGATIVE CONTROL: expansions used as ordinary arguments on an `apply` line are "
      "still allowed — words between the tool and the verb still break adjacency",
      rc == 0, f"rc={rc} stderr={err[:300]!r}")


# ---------------------------------------------------------------------------------------
# FEAT-41 MF-1, high, found INDEPENDENTLY by cycle 3's code reviewer and security reviewer, both
# running the exact string through the real gate: exit 0, a real approval signature forged.
#
# THE SAME CLASS AS C2-03, ONE MEMBER LATER, and that is the finding about me rather than about
# the code: C2-03 closed `${IFS}` and I wrote a regex for BRACED expansion only. An unquoted
# `$(...)` word-splits identically -- `set --` proof gives argc=2 -- and backticks do the same.
# MEASURED at source before fixing:
#     bash  -> argc=3, so `sign-approval` arrives as its own argument
#     gate  -> tokens ['plan-merge.py$', '(', 'printf', ...]; `(` and `)` are OPS and drop out,
#              so the token after the tool is `printf`, the adjacency never fires, and RAW_SIGN's
#              `["'\s]` class sees `)` rather than whitespace
#
# THE PANEL'S STANDING OBJECTION IS RECORDED RATHER THAN ANSWERED: this file is a DENYLIST of
# evasion forms and closing two members does not make it complete. `cmd_sign_approval` has no
# identity check of its own, so this gate is the sole enforcement REQ-05 rests on, and no runtime
# identity signal reaches a subprocess today (`HARNESS_AGENT_ID` is a marker inside agent
# definition files, not an env var) -- so the structural fix is not available from here. Routed up.
# ---------------------------------------------------------------------------------------
for _sub in ('$(printf " ")', "$(echo)", "$(:)", "`printf ' '`", '$(printf "%s" " ")'):
    rc, err = gate(f"python3 .claude/skills/harness/bin/plan-merge.py{_sub}sign-approval "
                   f"--file p.yaml --by Someone --date 2026-01-01",
                   agent_type="harness-orchestrator")
    check(f"MF-1: `plan-merge.py{_sub}sign-approval` is DENIED — a command substitution "
          f"word-splits exactly as ${{IFS}} does",
          rc == 2, f"rc={rc} stderr={err[:300]!r}")

# NESTED SUBSTITUTION, because a naive `\$\([^)]*\)` stops at the FIRST `)` and would leave the
# outer one behind -- which is how a one-line regex fix would have looked correct and leaked.
rc, err = gate('python3 .claude/skills/harness/bin/plan-merge.py$(echo "$(printf " ")")'
               'sign-approval --file p.yaml --by Someone --date 2026-01-01',
               agent_type="harness-orchestrator")
check("MF-1: a NESTED command substitution is DENIED — the scan must balance parens, not stop at "
      "the first one",
      rc == 2, f"rc={rc} stderr={err[:300]!r}")

# NEGATIVE CONTROL, and the one that bounds the widening: a substitution used as an ordinary
# ARGUMENT on a legitimate `apply` line stays allowed. Real words still sit between tool and verb.
rc, err = gate("python3 .claude/skills/harness/bin/plan-merge.py apply --file $(ls p.yaml) "
               "--proposal q.yaml  # not a sign-approval call",
               agent_type="harness-orchestrator")
check("MF-1 NEGATIVE CONTROL: a substitution as an ordinary argument on an `apply` line is still "
      "allowed — neutralising it does not make every mention of the verb a signing attempt",
      rc == 0, f"rc={rc} stderr={err[:300]!r}")

# AND A DATE SUBSTITUTION ON A REAL SIGNING CALL IS STILL DENIED, which it already was -- asserted
# so the neutralisation cannot accidentally turn a legitimate deny into an allow.
rc, err = gate("python3 .claude/skills/harness/bin/plan-merge.py sign-approval --file p.yaml "
               "--by Someone --date $(date +%F)",
               agent_type="harness-orchestrator")
check("MF-1: a normal signing call carrying a substitution in --date is still DENIED",
      rc == 2, f"rc={rc} stderr={err[:300]!r}")


# ---------------------------------------------------------------------------------------
# FEAT-41 HIGH-2, high, cycle 4: `xargs` forged a real signature end to end, at exit 0.
#
# THIS IS WHERE FORM-CHASING STOPS BEING HONEST, and the measurement is why. Three variants all
# deliver the verb:
#     echo sign-approval | xargs -I{} ... plan-merge.py {} ...   -> ARG1=sign-approval
#     echo sign-approval | xargs        ... plan-merge.py        -> ARG1=sign-approval (appended)
#     xargs ... plan-merge.py < verb.txt                         -> ARG1=sign-approval
# The third takes the verb FROM A FILE. Its text never appears in the command line, so NO
# text-scanning gate can ever see it. Closing "the xargs form" would be a fifth patch that leaves
# the class open, which is the pattern four review cycles have now demonstrated.
#
# SO THE RULE IS FAIL-CLOSED ON INDIRECTION, not another separator. When the tool's argv is
# supplied by a wrapper that reads it from somewhere the gate cannot see, the verb is
# UNDETERMINABLE -- and a gate that cannot determine the verb must refuse rather than guess. That
# is the same posture MF-5 established for an unresolvable path, and for the same reason.
#
# `bash -c` is deliberately NOT in that class: `denies` already RECURSES into a nested command
# line, so its verb is determinable and its own cases below still pass.
#
# WHAT THIS STILL DOES NOT MAKE COMPLETE is recorded in #1103: the structural answer is an
# identity check inside cmd_sign_approval, which needs a runtime identity signal that does not
# exist yet. This closes the reachable instances and the class of indirection; it does not turn a
# text scanner into a boundary.
# ---------------------------------------------------------------------------------------
_TOOLPATH = "python3 .claude/skills/harness/bin/plan-merge.py"
for _label, _cmd in (
    ("xargs -I{} placeholder",
     f"echo sign-approval | xargs -I{{}} {_TOOLPATH} {{}} --file p.yaml --by A --date 2026-01-01"),
    ("xargs appending",
     f"echo sign-approval | xargs {_TOOLPATH}"),
    ("xargs reading a FILE, verb absent from the line",
     f"xargs {_TOOLPATH} < /tmp/verb.txt"),
    ("find -exec",
     f"find . -name p.yaml -exec {_TOOLPATH} sign-approval --file {{}} \\;"),
):
    rc, err = gate(_cmd, agent_type="harness-orchestrator")
    check(f"HIGH-2: the tool invoked through {_label} is DENIED — the gate cannot see which verb "
          f"it will receive, so it must refuse rather than guess",
          rc == 2, f"rc={rc} stderr={err[:300]!r}")

# NEGATIVE CONTROL: an xargs line that does NOT invoke the tool is untouched. The rule is about
# the tool being invoked indirectly, never about xargs being present.
rc, err = gate("echo sign-approval | xargs -I{} grep {} .claude/skills/harness/bin/",
               agent_type="harness-orchestrator")
check("HIGH-2 NEGATIVE CONTROL: an xargs line that does not invoke plan-merge.py is still "
      "allowed — grepping for the verb is legitimate work",
      rc == 0, f"rc={rc} stderr={err[:300]!r}")

# NEGATIVE CONTROL: `bash -c` stays allowed for a non-signing nested line, proving the
# indirection rule did not swallow the recursion path that already works.
rc, err = gate(f"bash -c '{_TOOLPATH} apply --file p.yaml --proposal q.yaml'",
               agent_type="harness-orchestrator")
check("HIGH-2 NEGATIVE CONTROL: `bash -c` with a non-signing nested line is still allowed — "
      "recursion determines its verb, so it is not indirection",
      rc == 0, f"rc={rc} stderr={err[:300]!r}")

# AND `bash -c` CARRYING THE VERB IS STILL DENIED, by the recursion rather than by this rule.
rc, err = gate(f"bash -c '{_TOOLPATH} sign-approval --file p.yaml --by A --date 2026-01-01'",
               agent_type="harness-orchestrator")
check("HIGH-2: `bash -c` carrying a real signing call is still DENIED, via recursion",
      rc == 2, f"rc={rc} stderr={err[:300]!r}")


print(f"\n{fails} failing." if fails else "\nall checks passed.")
raise SystemExit(1 if fails else 0)
