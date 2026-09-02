#!/usr/bin/env bash
# PreToolUse Bash hook — close the CASUAL Bash write bypass (DEC-151).
#
# Field incident: qa, denied a source edit by check-domain, made the same edit
# via `perl -pi` from Bash — the domain hook only sees Write/Edit. This guard
# does not make Bash-write extraction "winnable" in general (DEC-85 stands);
# it parses the COMMON in-place editors and redirections, which is what an
# agent under pressure actually reaches for. Unparseable commands pass — the
# guard converts casual bypass into deliberate obfuscation, which the post-run
# tree audit then catches.
#
# Policy:
#   - reviewers (code/security/ui) — READ-ONLY: any detected write pattern is
#     denied outright, no path analysis. Their job is findings, never fixes.
#   - dev-ops — exempt (trusted by design, owns builds/deploy; DEC-85).
#   - every other harness agent — a detected write whose target path is
#     extractable and OUTSIDE the agent's domain (per team-config.yaml,
#     shared paths included) is denied; in-domain and unparseable pass.
#   - main session and non-harness agents — ungoverned, exit 0.
set -uo pipefail

payload=$(cat)

# BASH_SOURCE is the one question only bash can answer, which is why any bash remains.
_self="${BASH_SOURCE[0]:-$0}"
_selfdir="$(cd "$(dirname "$_self")" && pwd)"
_derived="$(cd "$_selfdir/../../../.." && pwd)"

# T-15: ONE interpreter launch, not two. Same reasoning as T-13 on the sibling hook —
# this fires on every Bash tool call, and a Python start-up per launch is the bulk of
# it. Behaviour is unchanged: the dev-ops exemption, the harness-* prefix filter, the
# absent-manifest fail-open and every exit-2 message are identical, and the unchanged
# test suite is the equivalence proof (D-10, REQ-07).
# `-P` IS LOAD-BEARING, NOT TIDINESS (#556). Python puts the invoking directory at
# sys.path[0] AHEAD of PYTHONPATH, so the harness_boundary import below took a
# harness_boundary.py sitting in the GOVERNED AGENT's cwd in preference to ours. Measured
# 2026-08-27 at sha 7179095: a stub returning a bogus root turned this hook from exit 2
# (refused) into exit 0 ("enforcement OFF"). The bootstrap removes only sys.path[0]
# before the heredoc imports anything, preserving site-packages on Python 3.9.
# test-no-distribution.py case 7 is the invariant.
HOOK_PAYLOAD="$payload" PYTHONPATH="$_selfdir${PYTHONPATH:+:$PYTHONPATH}" \
  python3 -c 'import sys; sys.path.pop(0); exec(compile(sys.stdin.read(), "<stdin>", "exec"))' "$_derived" "$_selfdir" <<'PY'
import sys, os, re, json, shlex

# harness_yaml is imported LAZILY, after the manifest check — NOT here. Ordering is
# behaviour: the two-launch version reached the absent-manifest fail-open in BASH,
# before any interpreter needed the module, so a guard whose module is missing must
# still exit 0 there rather than crash. (T-13 shipped this bug on the sibling hook and
# a test caught it.)
_derived, _bin_dir = sys.argv[1:3]
sys.path.insert(0, _bin_dir)


def _root():
    """WHERE THIS HARNESS IS ROOTED — asked of harness_boundary, the one resolver (FEAT-42
    T-11). Both call sites below carried the two-name environment chain: one falling through
    to `_derived`, the other to `""`. The `""` is why an unset environment left every
    subsequent join relative to whatever directory the hook inherited.

    strict=False, and for the same reason as check-domain.sh's twin of this function: a tree
    with no manifest must fail OPEN at exit 0 (DEC-101), and a strict raise fires on exactly
    that tree. strict=False returns the derived root, which is what the deleted code returned
    there too. What is gone is the `""` and the cwd fall-through, and the override now has to
    carry the MARKER before it is honoured — a probe neither deleted site performed.

    THE except CLAUSE IS THE BOOTSTRAP, not a second resolver. `_derived` is the bash
    wrapper's own BASH_SOURCE walk, and it is the only root computable when
    harness_boundary.py is not on the path at all — the isolated-copy fixture, which exists
    to prove the fail-open still fires.
    """
    try:
        import harness_boundary as _hb_root
    except Exception:
        return _derived
    return _hb_root.resolve_root(_bin_dir, strict=False)

try:
    d = json.loads(os.environ.get("HOOK_PAYLOAD") or "")
except Exception:
    sys.exit(0)

# MOVED UP (FEAT-30 T-05), verbatim and unchanged. The HEAD-move rule below runs
# BEFORE the harness-dev-ops early return under ruling R-01, so both helpers must
# already exist at that point. Nothing about either function changed.
def mask_quoted(text):
    """Blank the CONTENTS of quoted spans, preserving length and the quotes.

    The redirect scan below is a regex over the raw command, so a `>` inside a
    quoted string was read as an operator. That blocked the MANDATED
    `Co-Authored-By: … <noreply@anthropic.com>` trailer on every agent commit, an
    arrow in a printed string, and an HTML comment in prose (Task #5).

    Masking rather than deleting keeps offsets and lengths intact, so a QUOTED
    redirect target still yields a capturable token: `> "src/x.py"` becomes
    `> "xxxxxxxxx"`, which still finds the redirect and still blocks. The guard
    fails safe — a masked span can only hide `>` characters that bash itself
    would treat as literal text, never an operator.
    """
    out, q = [], None
    for ch in text:
        if q:
            if ch == q:
                q = None; out.append(ch)
            else:
                out.append("x")
            continue
        if ch in "\"'":
            q = ch
        out.append(ch)
    return "".join(out)

def segments(text):
    """Split a compound command into its parts at UNQUOTED shell separators.

    `shlex.split` leaves `;` attached to the preceding token ('docs/a.md;'), so the
    guard's `if a in (";", "&&", ...)` break never fired and the NEXT command's name was
    collected as an operand — `rm -f docs/a.md; echo ok` was refused for "rm targets
    echo" (B-6). Splitting first makes each command's operand list actually end.
    """
    parts, cur, q, i = [], [], None, 0
    while i < len(text):
        ch = text[i]
        if q:
            cur.append(ch)
            if ch == q:
                q = None
            i += 1
            continue
        if ch in "\"'":
            q = ch; cur.append(ch); i += 1; continue
        two = text[i:i + 2]
        if two in ("&&", "||"):
            parts.append("".join(cur)); cur = []; i += 2; continue
        if ch in ";\n|&":
            parts.append("".join(cur)); cur = []; i += 1; continue
        cur.append(ch)
        i += 1
    parts.append("".join(cur))
    return [p for p in (s.strip() for s in parts) if p]


agent = d.get("agent_type") or ""
if not agent:
    sys.exit(0)

# =============================== THE HEAD-MOVE RULE ===============================
# REQ-04. HEAD is SHARED MUTABLE STATE for the duration of a run: one governed agent
# moving it re-points every file under every other agent standing in that checkout.
#
# PLACEMENT IS THE RULE, NOT A DETAIL. Operator ruling R-01 of 2026-08-20: this runs
# BEFORE the harness-dev-ops early return below, so it binds ALL SIXTEEN governed
# agents. Placed after that return it would provably never reach harness-dev-ops —
# the return precedes the `harness-` prefix test — and T-01, T-02 and T-08 are laned
# to exactly that persona. THE EARLY RETURN SURVIVES for every WRITE: it is not
# deleted, not narrowed, and no second exemption is added. Only the ordering changed.
#
# Why that does not contradict DEC-151: the authority at DECISIONS.md:3650 scopes the
# exemption to extractable TARGET PATHS, and moving HEAD is not one. The recovery path
# it exists to preserve — dev-ops writing when the guard itself is broken, including
# writing THIS FILE — is untouched. Accepted cost, recorded in the BRIEF beside REQ-04:
# when HEAD is wrong and the guard is working, dev-ops cannot fix it either, and the
# repair is the operator's from the main session, which carries no agent_type.
#
# THE MAIN SESSION IS NOT GOVERNED and is unaffected — it has no agent_type, so it
# returned at the check above. The case where IT moves a branch under a live run is
# answered by isolation instead: after T-01 each orchestrator commits inside its own
# worktree.
GIT_GLOBAL_FLAGS_WITH_VALUE = ("-C", "-c", "--git-dir", "--work-tree", "--namespace",
                               "--exec-path", "--super-prefix")

# THE REFUSE LIST IS THE CLOSED SET. Everything else DECIDABLE is allowed and only the
# UNDECIDABLE case is refused — this direction is load-bearing under R-01, not a
# nicety: T-01's and T-02's verify blocks run `git show` against the pinned sha and are
# executed by harness-dev-ops, which R-01 now binds. An implementation reading its list
# as exhaustive-by-default would refuse a task's own verification command.
HEAD_MOVERS = {"switch", "rebase", "merge", "cherry-pick", "revert"}


def _git_subcommand(tokens):
    """(subcommand, operands) for a git invocation, or (None, []) if undecidable.

    Walks the RAW args so flag/value coupling survives: filtering flags out first and
    then re-finding the subcommand by string would match a flag's VALUE. Same shape
    filtering the worktree parser below already applies, including a leading `-C`.
    """
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in GIT_GLOBAL_FLAGS_WITH_VALUE:
            i += 2
            continue
        if t.startswith("-"):
            i += 1
            continue
        return t, tokens[i + 1:]
    return None, []


def _moves_head(sub, operands, project_root):
    """True when this git invocation moves HEAD. See HEAD_MOVERS for the closed set."""
    if sub in HEAD_MOVERS:
        return True
    if sub == "checkout":
        # A pathspec checkout RESTORES FILES and moves nothing. `--` is the explicit
        # form; otherwise every non-flag operand naming an existing path is a pathspec.
        # `-B` is a forced branch re-point and moves HEAD whatever else is present.
        if any(o in ("-B", "-b") for o in operands):
            return True
        if "--" in operands:
            return False
        rest = [o for o in operands if not o.startswith("-")]
        if rest and all(os.path.exists(os.path.join(project_root, o)) or os.path.exists(o)
                        for o in rest):
            return False
        return True
    if sub == "reset":
        # A hard, keep or merge reset moves HEAD. `--soft` and a bare/pathspec reset do
        # not: they move the index, which is not shared checkout state.
        return any(o in ("--hard", "--keep", "--merge") for o in operands)
    return False


if agent.startswith("harness-"):
    _cmd_head = ((d.get("tool_input") or {}).get("command") or "")
    if _cmd_head:
        _proot = _root()

        def _refuse_head(what):
            print(f"bash-write-guard: BLOCKED — {what}", file=sys.stderr)
            print("  HEAD is SHARED MUTABLE STATE for the duration of a run: moving it "
                  "re-points every file under every other agent standing in this "
                  "checkout.", file=sys.stderr)
            print("  Work in the worktree cut for this feature and address it with git's "
                  "-C option rather than moving to it.", file=sys.stderr)
            sys.exit(2)

        for _seg in segments(_cmd_head):
            try:
                _tk = shlex.split(_seg, posix=True)
            except ValueError:
                _tk = _seg.split()
            if not _tk or os.path.basename(_tk[0]) != "git":
                continue
            _sub, _ops_head = _git_subcommand(_tk[1:])
            if _sub is None:
                # UNDECIDABLE, so refused — the direction DEC-151 already chose for the
                # unparsed worktree destination. A git call whose subcommand this guard
                # cannot find is not one it may judge safe.
                _refuse_head("a `git` command whose subcommand this guard cannot "
                             "determine, so it cannot say whether it moves HEAD")
            if _moves_head(_sub, _ops_head, _proot):
                _refuse_head(f"`git {_sub}` moves HEAD, and every harness agent is "
                             f"refused this for the duration of a run")

# harness-dev-ops is EXEMPT: it owns the tooling this guard is made of, and blocking
# it would remove the one recovery path when the guard itself is broken. THE HEAD-MOVE
# RULE ABOVE IS DELIBERATELY NOT SUBJECT TO IT (ruling R-01) — this exemption covers
# WRITES, which is the scope DEC-151 gives it.
if agent == "harness-dev-ops":
    sys.exit(0)
if not agent.startswith("harness-"):
    sys.exit(0)

root = _root()
manifest = os.path.join(root, ".harness", "team-config.yaml")

# not onboarded — fail open like check-domain
if not os.access(manifest, os.R_OK):
    sys.exit(0)

import harness_yaml

# LAZY, HERE, AND FAIL-CLOSED — the same shape T-01 put in the sibling guard, for the
# same reason. NOT at the top of the file: the isolated-copy case in this file's own
# T-14 block asserts that an absent manifest still fails OPEN, and a top-level import
# breaks it. Unhandled, an ImportError exits 1, which is NON-BLOCKING, so the write
# would land and BOTH routes would go unenforced at once (D-06). Exit 2 is safe at this
# point because harness-dev-ops and every non-harness agent already returned above, so
# the tier that repairs the file is never blocked by it.
try:
    import harness_boundary
except Exception as _be:
    print("bash-write-guard: BLOCKED — the boundary module harness_boundary.py could "
          "not be imported, so no domain can be checked.", file=sys.stderr)
    print(f"  {type(_be).__name__}: {_be}", file=sys.stderr)
    print("  Enforcement is CLOSED rather than partial. Restore "
          ".agents/skills/harness/bin/harness_boundary.py, then retry.", file=sys.stderr)
    sys.exit(2)

# The RETURN VALUE IS THE DECISION — see check-domain.sh's note. A bare call leaves
# REQ-04's fail-closed and SC-09's expiry inert: the function prints, and the write
# proceeds anyway because only exit 2 blocks (DEC-100).
if not harness_yaml.require_or_bootstrap(root):
    sys.exit(2)

# GRANTED, and there is no parser. Recorded, NOT acted on here — see below.
#
# This used to `sys.exit(0)` on the spot, which short-circuited the ENTIRE guard. But
# only the DOMAIN check needs the manifest: the reviewer read-only rule and the
# write-pattern detection need neither a manifest nor a parser. So a bootstrap-grant
# session let `harness-code-reviewer` run `rm -rf src/main.py` — reproduced live, exit 0
# where a PyYAML-present run exits 2. On `main` this guard had NO YAML dependency at
# all, so reviewer read-only was unconditional; the short-circuit was a regression
# introduced by this feature.
#
# It is also the exact defect the sibling hook was fixed for one commit earlier
# ("Skip only what actually needs the parser", check-domain.sh) — fixed there and not
# here, in a pair of files this same feature otherwise went to lengths to keep in step
# (D-03). Two guards, one rule, and I changed one of them.
_no_parser = harness_yaml.yaml is None

# ROOT-SIDE: THE SESSION IS STANDING IN AN OUT-OF-PLACE WORKTREE (issue #103). This
# guard has no domain_check function, so T-02's insertion point does not exist here.
#
# WHAT THIS PLACEMENT RESTS ON. It must sit ahead of BOTH early exits below — `if not
# cmd` and `if not findings` — because a session standing in such a tree must be refused
# even when the command extracts no write target at all. `git status --porcelain` from
# that root is what asserts this, and it is the only case pinning the position. It must
# also stay ahead of the per-finding DEC-153 continue, which is never reached when there
# are no findings.
#
# Its position relative to `if _no_parser: sys.exit(0)` below is NOT asserted and is not
# load-bearing. Sitting above it means this route still refuses in a bootstrap-grant
# session while the Write route does not — the chosen divergence T-02 records. Do not
# move this check below that exit to buy symmetry.
_root_wt = harness_boundary.worktree_owner(root)
if _root_wt is not None and _root_wt[1] is None:
    print(f"bash-write-guard: BLOCKED — {_root_wt[0]} holds a .git pointer file that "
          "does not parse, so this session's checkout cannot be placed.", file=sys.stderr)
    print("  Repair or remove it, then start the session again.", file=sys.stderr)
    sys.exit(2)
if _root_wt is not None and not _root_wt[2]:
    # THE ROOT-SIDE WORDING, not the target-side one. `git worktree remove` succeeds at
    # exit 0 from inside the tree it removes, so that guidance printed to a session
    # standing in that tree tells the agent to delete its own cwd.
    print(f"bash-write-guard: BLOCKED — {_root_wt[0]} is a git worktree that is not "
          f"under {harness_boundary.WORKTREES_SEGMENT}/, and this session is rooted "
          "in it.", file=sys.stderr)
    print(f"  Worktrees belong under {harness_boundary.worktree_refusal_location(_root_wt[1])}",
          file=sys.stderr)
    print("  Start the session from the main checkout, or from a checkout under that "
          "location, instead.", file=sys.stderr)
    sys.exit(2)

cmd = ((d.get("tool_input") or {}).get("command") or "")
if not cmd:
    sys.exit(0)

REVIEWERS = {"harness-code-reviewer", "harness-security-reviewer", "harness-ui-reviewer"}

# --- detect write patterns and extract candidate target paths where parseable ---
findings = []   # (pattern-name, [paths])

SHELL_FEEDERS = {"bash", "sh", "zsh", "dash", "ksh"}


def strip_heredoc_bodies(text):
    """Drop heredoc BODIES, keeping the command line that opens them.

    A heredoc body is DATA, not shell syntax: `python3 - <<PY ... if a > b: ... PY`
    feeds a script to an interpreter, and reading that `>` as a redirect refused every
    inline script this repo runs (B-6). The `<<TAG` line itself is kept, so a real
    redirect on it — `cat <<EOF > src/main.py` — is still scanned and still blocks.

    EXCEPTION, and it is the whole reason this is safe: when the heredoc feeds a SHELL
    (`bash <<EOF`), the body IS code and its redirects are real. Those bodies are kept.
    An unrecognised feeder is treated as a shell too — the guard fails toward scanning.
    """
    lines, out, i = text.splitlines(), [], 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        # Only an UNQUOTED << opens a heredoc; mask first so `echo "a <<b"` does not.
        m = re.search(r"<<-?\s*([\"']?)([A-Za-z_][A-Za-z0-9_]*)\1", mask_quoted(line))
        i += 1
        if not m:
            continue
        tag, dash = m.group(2), "<<-" in line
        try:
            words = [os.path.basename(w) for w in shlex.split(line)]
        except ValueError:
            # An unbalanced quote must not raise: this is a PreToolUse hook, and only
            # exit 2 blocks (DEC-100), so an uncaught exception fails OPEN. Keep the body.
            words = []
            keep_body = True
        else:
            # A shell ANYWHERE in the pipeline means the body is code, not data:
            # `cat <<EOF | bash` routes it to a shell just as surely as `bash <<EOF`,
            # and looking only at the first word let that shape through (a fail-open
            # this function introduced and this line closes).
            keep_body = (any(w in SHELL_FEEDERS for w in words)
                         or not words
                         or words[0] not in KNOWN_DATA_FEEDERS)
        while i < len(lines):
            body = lines[i]
            i += 1
            if (body.strip() if dash else body) == tag:
                out.append(body)
                break
            if keep_body:
                out.append(body)
    return "\n".join(out)


# Feeders whose heredoc body is inert DATA. Anything not listed keeps its body scanned,
# so a novel or obfuscated feeder cannot smuggle a redirect past the guard.
KNOWN_DATA_FEEDERS = {"cat", "python", "python3", "git", "tee", "jq", "sed", "awk",
                      "grep", "node", "ruby", "perl", "psql", "sqlite3", "mail", "ssh"}


scan_text = strip_heredoc_bodies(cmd)
SEGMENTS = segments(scan_text)

# redirections:  > path   >> path   (not 2>/dev/null, >&2, >(...) etc.)
# Scanned over the MASKED text so quoted text cannot pose as an operator.
for _seg in SEGMENTS:
    for m in re.finditer(r"(?<![0-9&<])>{1,2}\s*([^\s;&|)]+)", mask_quoted(_seg)):
        p = m.group(1)
        if p.startswith(("&", "(", "/dev/")):
            continue
        findings.append(("redirect", [p]))

# A redirection is not an operand. `shlex.split` hands back `2>/dev/null` as an ordinary
# token, so `cp docs/a.md docs/b.md 2>/dev/null` read its LAST token as the cp destination
# and denied a legal in-domain copy, naming "2>/dev/null" as the path (B-5, hit twice during
# FEAT-11). Two shapes exist and both must go: the operator glued to its target
# (`2>/dev/null`, `>out.md`) and the operator standing alone, whose target is the NEXT token
# (`> out.md`).
#
# THIS DOES NOT WEAKEN THE GUARD, and that is the whole reason it is safe to drop them: the
# redirect scan above (the `>{1,2}` finditer over the masked text) already reports every real
# redirect target as its own finding. `cp a b > src/evil.py` is still denied — by the finding
# that correctly calls it a redirect, instead of by one that mislabels it a cp destination.
REDIR = re.compile(r"^(?:[0-9]*(?:>{1,2}|<)|[0-9]*>&|&>{1,2})")


# WHICH COMMANDS ACTUALLY TAKE A SCRIPT ARGUMENT AFTER -f. This set is the whole fix for
# #241, and getting it wrong fails in one of two directions, so it is a set and not a
# blanket rule.
#
# `sed -f script.sed file`, `perl -f`, `awk -f prog.awk file` consume the token after -f,
# and skipping it is what keeps the SCRIPT out of the target list.
#
# `rm -f path` does NOT. There -f means force, and the token after it is the target. The
# skip was unconditional, so `rm -f <out-of-domain-path>` arrived with an EMPTY target
# list and no deny fired — measured at exit 0 while bare `rm <same path>` exited 2. The
# most common deletion idiom was the one that got through. `rm -rf dir` was never affected
# because -rf is a single token; `rm -r -f path` was.
#
# DO NOT "simplify" this by dropping -f from the flag list entirely: `sed -i -f script.sed
# <out-of-domain>` blocks correctly TODAY by skipping the script path and keeping the real
# target, and a blanket drop would report the script as the target instead.
SCRIPT_ARG_CMDS = ("sed", "perl", "awk")


def trailing_files(args, drop_first_script=False, script_flags=False):
    out, skip, saw_expr, skip_is_redir = [], False, False, False
    for a in args:
        if skip:
            # A skipped REDIRECT target is not an expression. Conflating the two would let
            # `sed -i 's/a/b/' f > out` look as if -e had been passed, and drop_first_script
            # would then keep the script `s/a/b/` in the file list.
            skip = False
            if not skip_is_redir:
                saw_expr = True
            skip_is_redir = False
            continue
        if script_flags and a in ("-e", "-E", "--expression", "-f", "--file"):
            skip = True; continue          # the next token is an expression/script, not a target
        m = REDIR.match(a) if a else None
        if m:
            # A bare operator takes the next token as its target; a glued one carries it.
            if m.end() == len(a):
                skip = True; skip_is_redir = True
            continue
        if not a or a.startswith("-") or a in (";", "&&", "||"):
            continue                       # empty covers BSD `sed -i ''`
        out.append(a)
    if drop_first_script and not saw_expr and out:
        out = out[1:]                      # bare `sed -i 's/a/b/' file`: first arg is the script
    return out

tokens = []
for _seg in SEGMENTS:
    try:
        tokens.append(shlex.split(_seg, posix=True))
    except ValueError:
        tokens.append(_seg.split())

# Each segment is one command, so its operand list ends at the segment boundary — no
# in-list separator hunting, which is what silently failed before (B-6).
for seg_tokens in tokens:
    for i, t in enumerate(seg_tokens):
        base = os.path.basename(t)
        args = seg_tokens[i + 1:]
        if base in ("sed", "perl") and any(a.startswith(("-i", "-pi", "-ni")) or a == "-p" and "-i" in args for a in args):
            findings.append((f"{base} in-place",
                             trailing_files(args, drop_first_script=(base == "sed"),
                                            script_flags=(base in SCRIPT_ARG_CMDS))))
        elif base == "tee":
            findings.append(("tee", [a for a in trailing_files(args) if a != "-"]))
        elif base in ("mv", "cp") and len(trailing_files(args)) >= 2:
            findings.append((base, trailing_files(args)[-1:]))
        elif base == "rm":
            findings.append(("rm", trailing_files(args)))
        elif base == "sponge":
            findings.append(("sponge", trailing_files(args)))
        elif base == "awk" and any(a == "-i" or a.startswith("inplace") for a in args):
            findings.append(("awk inplace", trailing_files(args, script_flags=True)))

# --- WORKTREE CREATION (issue #103, REQ-03) -------------------------------------
# THE CREATION DOOR, not the write door. Measured at a29ad06:
# `git worktree add --detach ~/GitHub/harness-SIBLING HEAD` exited 0 from BOTH hooks.
# Catching the mistake after the tree exists is worth less than preventing it.
#
# THIS SCAN MUST RUN BEFORE `if not findings: sys.exit(0)` BELOW. `git` produces no
# findings, so placed after that exit the whole check is dead code.
#
# NOT extended to `git clone` or `git init`. Those materialise a DIFFERENT repository,
# which carries no .harness/team-config.yaml and no agents, so no agent is misled into
# believing that tree is governed — which is the harm issue #103 records. Every other
# git subcommand is untouched.
_WT_FLAGS_WITH_VALUE = ("-b", "-B", "--reason")

def _worktree_destination(args, sub):
    """The destination operand of `git worktree add|move`, or None if unparsed.

    None means REFUSE, never permit. Failing loudly on a form this does not understand
    is the point; failing open reproduces the defect.
    """
    rest, i = [], 0
    while i < len(args):
        a = args[i]
        if a in _WT_FLAGS_WITH_VALUE:
            i += 2                       # these CONSUME the following token
            continue
        if a.startswith("-"):
            i += 1                       # --detach, --force, -f, --checkout, --lock, ...
            continue
        rest.append(a)
        i += 1
    if sub == "move":
        return rest[1] if len(rest) > 1 else None    # <worktree> <new-path>
    return rest[0] if rest else None

for seg_tokens in tokens:
    for i, t in enumerate(seg_tokens):
        if os.path.basename(t) != "git":
            continue
        # Walk the raw args so flag/value coupling survives: the first non-flag operand
        # must be `worktree` and the next `add` or `move`. Filtering flags out first and
        # then re-finding the subcommand by string would match a flag's VALUE.
        _args = seg_tokens[i + 1:]
        _j, _ops = 0, []
        while _j < len(_args) and len(_ops) < 2:
            _a = _args[_j]
            if _a in _WT_FLAGS_WITH_VALUE:
                _j += 2
                continue
            if _a.startswith("-"):
                _j += 1
                continue
            _ops.append(_a)
            _j += 1
        # `remove` and `prune` ADMITTED here (FEAT-30 T-05, SC-07's Bash-route half).
        # THE SAME PARSER, extended — not a second one, and its operand walk is not
        # duplicated. Measured at eeabc59: this test read `_ops[1]` against add and move
        # ONLY, so `remove` was never inspected and a FORCED removal passed at exit 0.
        # T-02's refusal lives inside feature-worktree.py, and a governed agent bypasses
        # a CLI by calling git directly — a gate an agent can route around is the shape
        # this feature exists to replace.
        if len(_ops) < 2 or _ops[0] != "worktree" or _ops[1] not in ("add", "move",
                                                                    "remove", "prune"):
            continue
        _sub = _ops[1]

        if _sub in ("remove", "prune"):
            # NO DIRTY-TREE DETECTOR HERE, deliberately, and that is why this rule is
            # small: WITHOUT a force flag git itself already refuses a dirty tree at
            # exit 128. Refusing the force flag IS the whole mechanism. This guard
            # cannot cheaply know whether a tree is dirty and does not need to.
            if any(a in ("-f", "--force") or a.startswith("--force=") for a in _args):
                print(f"bash-write-guard: BLOCKED — `git worktree {_sub}` carrying a "
                      f"force flag.", file=sys.stderr)
                print("  Use `.agents/skills/harness/bin/feature-worktree.py remove`: it "
                      "refuses on a dirty tree and reports every path it would discard.",
                      file=sys.stderr)
                print("  Without --force git refuses a dirty tree itself; forcing is how "
                      "unlanded work is destroyed silently.", file=sys.stderr)
                sys.exit(2)
            # Unforced: git decides. The destination logic below is for add and move
            # only — remove and prune carry no destination this guard must resolve, so
            # nothing about the existing add/move behaviour changes.
            continue

        _dest = _worktree_destination(_args[_j:], _sub)

        def _refuse_worktree(why):
            print(f"bash-write-guard: BLOCKED — {why}", file=sys.stderr)
            print(f"  Worktrees belong under "
                  f"{os.path.join(root, harness_boundary.WORKTREES_SEGMENT) + os.sep}",
                  file=sys.stderr)
            print("  A worktree elsewhere silently disables the harness machinery for "
                  "every session opened in it (issue #103).", file=sys.stderr)
            sys.exit(2)

        if _dest is None:
            _refuse_worktree(f"`git worktree {_sub}` with no destination this guard can "
                             "determine. Give an absolute path under "
                             f"{harness_boundary.WORKTREES_SEGMENT}/.")
        if not os.path.isabs(_dest):
            # A RELATIVE DESTINATION CANNOT BE RESOLVED. The Bash payload carries a
            # command and no working directory, so resolving against root would read
            # `git worktree add .claude/worktrees/FEAT-99` issued from an unrelated
            # directory as legitimate — a silent permit of the exact mistake.
            _refuse_worktree(f"`git worktree {_sub} {_dest}` gives a RELATIVE "
                             "destination, which this guard cannot resolve. Give an "
                             "absolute path under "
                             f"{harness_boundary.WORKTREES_SEGMENT}/.")

        # BOTH SIDES ARE realpath-RESOLVED, and it is one or the other rather than a
        # preference. root is derived above with os.access alone and never resolved, so
        # resolving only the destination compares two spellings of the same tree — on
        # darwin a mkdtemp fixture is /var/folders/... while realpath gives
        # /private/var/folders/..., commonpath returns "/" and the paired ALLOW goes red
        # against correct code. Resolving NEITHER also makes the fixture pass and is
        # rejected on substance: the comparison would be string-level, so
        # `<root>/.claude/worktrees/../../../tmp/sib` would be judged inside and
        # permitted. Resolving both closes that and its symlink form together.
        #
        # A LOCAL resolved copy only. Every other rule in this file compares against the
        # unresolved root, and changing that would alter behaviour no criterion covers.
        _wt_root = os.path.realpath(root)
        _legal = os.path.realpath(os.path.join(_wt_root, harness_boundary.WORKTREES_SEGMENT))
        _abs_dest = os.path.realpath(_dest)
        try:
            _inside = os.path.commonpath([_abs_dest, _legal]) == _legal
        except ValueError:      # different drives / unrelated roots
            _inside = False
        if not _inside:
            _refuse_worktree(f"`git worktree {_sub}` targets {_dest}, which is not "
                             f"under {harness_boundary.WORKTREES_SEGMENT}/.")

if not findings:
    sys.exit(0)

def deny(reason):
    print(f"bash-write-guard: BLOCKED — {reason}", file=sys.stderr)
    print("  File changes go through the Write tool, where your domain is enforced. "
          "A path the domain hook denied does not become writable by switching tools — "
          "that is guardrail evasion (DEC-151). If the file should be yours, raise it "
          "as an open_question.", file=sys.stderr)
    sys.exit(2)

if agent in REVIEWERS:
    pats = ", ".join(sorted({f[0] for f in findings}))
    deny(f"{agent} is READ-ONLY and this command writes files ({pats}). "
         f"Report the finding; never fix.")

# NO PARSER: everything above this line ran — the write-pattern detection and the
# reviewer read-only denial, neither of which needs the manifest. Only the domain walk
# below does, so only it is skipped. The grant exists to let a broken machine be fixed,
# not to suspend the rules that do not depend on the thing that is broken.
if _no_parser:
    sys.exit(0)

# --- non-reviewers: check extractable paths against the agent's domain ---
# T-14, and this is the SECURITY-RELEVANT half of D-03. This file used to carry its
# own copy of check-domain.sh's manifest skimmer — two hand-maintained walks over the
# same rulebook, which is one edit away from the two write surfaces disagreeing about
# what an agent may write. That is not a theoretical risk here: this hook exists
# BECAUSE an agent routed around check-domain.sh (DEC-151), so a divergence between
# them is a bypass by construction. Both now call one function; they cannot drift.
try:
    mine, shared = harness_yaml.manifest_domains(manifest, agent)
except harness_yaml.DuplicateKeyError as e:
    print(f"bash-write-guard: BLOCKED — the manifest has a duplicate key {e.key!r}.",
          file=sys.stderr)
    print(f"  {manifest}", file=sys.stderr)
    print("  The second occurrence silently shadows the first, so which domain "
          "applies is ambiguous. Enforcement cannot be trusted until it is fixed.",
          file=sys.stderr)
    sys.exit(2)
except harness_yaml.YamlParseError as e:
    # FAIL CLOSED, matching check-domain.sh. Distinct from the absent-manifest case
    # at :46, which still exits 0: an unconfigured project has nothing to enforce,
    # whereas here the project IS configured and exactly one action fixes it.
    print("bash-write-guard: BLOCKED — the manifest does not parse, so no domain can "
          "be checked.", file=sys.stderr)
    print(f"  {e.original}", file=sys.stderr)
    print("  Enforcement is CLOSED rather than partial: a rulebook that cannot be "
          "read cannot be half-applied. Fix the file (the main session owns it), "
          "then retry.", file=sys.stderr)
    sys.exit(2)

RE_FEATURE_ARTIFACT = re.compile(r"^\.harness/[^/]+/features/([^/]+)/")


def feature_checkout_guard(rel, absolute_path):
    """Refuse an allowed Bash write aimed at a feature's main-checkout artifact.

    The tool route now binds this checkout question, but the Bash route previously
    continued on the same allowed verdict and let the identical write land. This does
    not extend run-digest content preservation to Bash: shell commands carry no complete
    incoming file payload to compare with prior content.
    """
    match = RE_FEATURE_ARTIFACT.match(rel)
    if match is None:
        return
    feature_id = match.group(1)
    try:
        expected = harness_boundary.worktree_for_feature(root, feature_id)
        if expected is None:
            return
        checkout = harness_boundary.checkout_relative(absolute_path)
        if checkout is not None and harness_boundary.real(checkout[0]) == harness_boundary.real(expected):
            return
        deny(f"{absolute_path} is a feature artifact whose write belongs in worktree "
             f"{expected}. Write it there, not in the main checkout.")
    except harness_boundary.AmbiguousWorktree as exc:
        deny(f"{absolute_path} belongs to feature {feature_id}, but its worktree is "
             f"ambiguous: {exc}")
    except Exception:
        # Absorbing: preserve the already-computed allowance rather than crashing to an
        # exit code the host does not treat as a refusal.
        return


# THE DOMAIN DECISION IS harness_boundary.classify's, NOT THIS FILE'S (issue #261).
# This guard used to carry its own glob_to_re/matches pair and match raw globs with no
# notion of the two bases and no control-plane target-side test. Measured at a29ad06,
# with src/** granted to harness-backend-dev: a Write to <root>/src/main.py exited 2
# while `echo hi > <root>/src/main.py` exited 0. Two write surfaces, two answers, and
# this hook exists BECAUSE an agent routed around the other one (DEC-151) — so a
# divergence between them is a bypass by construction.
for name, paths in findings:
    for p in paths:
        ap = os.path.abspath(os.path.join(root, p)) if not os.path.isabs(p) else p
        rel = os.path.relpath(ap, os.path.abspath(root))

        # BOTH CONTINUES BELOW RUN AHEAD OF classify, AND THAT ORDERING IS BEHAVIOUR.
        # Worktree carve-out (DEC-153): disposable checkouts are where sanctioned
        # perturbation proofs live — qa mutates source there to prove a test
        # discriminates. Moving it after classify would change what qa may do in a
        # worktree. The MAIN checkout stays hard-protected. Reviewers never reach this
        # branch (denied on any write pattern above).
        if re.match(r"^\.claude/worktrees/", rel):
            continue
        # tmp/cache noise is not a domain question.
        if re.match(r"^(\.pytest_cache|node_modules|__pycache__|\.venv)", rel):
            continue

        verdict = harness_boundary.classify(ap, root, mine, shared, "bash-write-guard")

        if verdict["outcome"] == "out_of_place_worktree" and verdict.get("unparsed"):
            deny(f"{verdict['checkout']} holds a .git pointer file that does not parse, "
                 "so this code cannot say which repository owns it or whether it is in a "
                 "legal place. A checkout that cannot be placed is not one to write into.")

        if verdict["outcome"] == "out_of_place_worktree":
            # The TARGET-SIDE wording, and the removal guidance is correct here: the
            # tree being named is not the one this session is running in.
            deny(f"{ap} is inside a git worktree that is not under "
                 f"{harness_boundary.WORKTREES_SEGMENT}/. Worktrees belong under "
                 f"{verdict['expected']} — that tree ({verdict['checkout']}) should be "
                 "removed with `git worktree remove` rather than written into.")

        if verdict["outcome"] == "wrong_checkout":
            # Issue #895, same ground as out_of_place_worktree above: this must run
            # BEFORE the outside-repo `rel.startswith("..")` continue below, or the
            # fix is dead on this route exactly as issue #103 was before the
            # out_of_place_worktree block landed here — a target outside root always
            # produces a rel starting with "..", which is what let a worktree-rooted
            # Bash write reach the main checkout unrefused while the same target via
            # the Write tool was already denied (DEC-151: two surfaces disagreeing is
            # a bypass by construction).
            deny(f"{ap} is in {verdict['checkout']}, but this session is rooted in "
                 f"{verdict['root']}. Write it there instead: a domain grant is "
                 "matched by relative path shape, and the identical path in a "
                 "different checkout of this repository is not the same file.")

        # THE OUTSIDE-REPO CONTINUE, MOVED BELOW classify AND NARROWED TO A FILTER ON
        # THE OUTCOME (D-07). It has to run after classify or the issue #103 fix is dead
        # code on this route — that continue is precisely what made a sibling worktree
        # invisible here. But it must NOT be dropped in favour of classify's own
        # not_a_domain_question: `rel` is ROOT-relative, so every path under the product
        # workspace begins with `..`, and dropping it would start enforcing product-base
        # domains on the Bash route for the first time. That widening has no REQ, no
        # criterion and no test behind it, and the grilling fences it off as out of
        # scope. Product paths keep today's Bash-route behaviour.
        if rel.startswith(".."):
            continue

        if verdict["outcome"] in ("allow", "not_a_domain_question"):
            feature_checkout_guard(rel, ap)
            continue

        if verdict["outcome"] == "shared":
            feature_checkout_guard(rel, ap)
            # Shared paths are owned by nobody and always serialized (DEC-85). Same
            # notice check-domain.sh prints on its own route.
            print(f"bash-write-guard: {agent} is writing SHARED path "
                  f"{verdict['rel']} (owned by nobody, must be serialized).",
                  file=sys.stderr)
            continue

        # `rel` in this message comes from the VERDICT and is BASE-relative, where the
        # line above computes it ROOT-relative. In the product base the two differ, so
        # this guard's message text changed there. That is intended, not a regression.
        deny(f"{agent}: `{name}` targets {verdict['rel']}, outside your domain.")

sys.exit(0)
PY
